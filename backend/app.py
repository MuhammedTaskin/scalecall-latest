"""
FastAPI app with WebSocket streaming for telco agent.
"""
import asyncio
import json
import uuid
import os
from typing import Dict, Any, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
from dotenv import load_dotenv

from backend.orchestrator import Orchestrator
from backend.db import init_db, SessionLocal
from backend.stt_service import STTService
from backend.tts_service import TTSService
from backend.api.llm import router as llm_router

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Telco Agent", version="1.0.0")

# Include API routers
app.include_router(llm_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
orchestrator = Orchestrator()
stt_service = STTService()
tts_service = TTSService()

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected")

    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)


manager = ConnectionManager()


@app.on_event("startup")
async def startup_event():
    """Initialize database and services."""
    await init_db()
    await stt_service.initialize()
    await tts_service.initialize()
    logger.info("Telco Agent started successfully")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Main WebSocket endpoint for real-time communication."""
    await manager.connect(websocket, client_id)
    
    # Session state
    session_state = {
        "messages": [],
        "current_persona": "RouterAgent",
        "audio_buffer": [],
        "is_recording": False
    }
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            await handle_message(client_id, message, session_state)
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)


async def handle_message(client_id: str, message: dict, session_state: dict):
    """Handle incoming WebSocket messages."""
    msg_type = message.get("type")
    
    try:
        if msg_type == "user_text":
            await handle_user_text(client_id, message["text"], session_state)
            
        elif msg_type == "user_audio_start":
            session_state["is_recording"] = True
            session_state["audio_buffer"] = []
            
        elif msg_type == "user_audio_chunk":
            if session_state["is_recording"]:
                session_state["audio_buffer"].append(message["pcm"])
                
        elif msg_type == "user_audio_end":
            session_state["is_recording"] = False
            if session_state["audio_buffer"]:
                await handle_audio_input(client_id, session_state["audio_buffer"], session_state)
                
        elif msg_type == "interrupt":
            await handle_interrupt(client_id)
            
        else:
            logger.warning(f"Unknown message type: {msg_type}")
            
    except Exception as e:
        logger.error(f"Error handling message {msg_type}: {e}")
        await manager.send_message(client_id, {
            "type": "error",
            "message": "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin."
        })


async def handle_user_text(client_id: str, text: str, session_state: dict):
    """Process user text input."""
    # Add user message to session
    user_msg = {"role": "user", "content": text}
    session_state["messages"].append(user_msg)
    
    # Stream LLM response
    async for chunk in orchestrator.stream(session_state["messages"], session_state["current_persona"]):
        if "delta" in chunk:
            await manager.send_message(client_id, {
                "type": "model_delta",
                "text": chunk["delta"]
            })
            
        elif "tool_call" in chunk:
            await manager.send_message(client_id, {
                "type": "tool_call",
                **chunk["tool_call"]
            })
            
            # Execute tool and feed result back
            tool_result = await orchestrator.execute_tool(chunk["tool_call"])
            await manager.send_message(client_id, {
                "type": "tool_result",
                "id": chunk["tool_call"]["id"],
                "name": chunk["tool_call"]["name"],
                "result": tool_result
            })
            
        elif "handoff" in chunk:
            session_state["current_persona"] = chunk["handoff"]["persona"]
            await manager.send_message(client_id, {
                "type": "handoff",
                "persona": chunk["handoff"]["persona"]
            })
            
        elif "complete" in chunk:
            # Generate TTS for the complete response
            if chunk["complete"]:
                await generate_tts(client_id, chunk["complete"])


async def handle_audio_input(client_id: str, audio_chunks: List[str], session_state: dict):
    """Process audio input via STT."""
    try:
        # Convert audio chunks and transcribe
        transcript = await stt_service.transcribe_audio(audio_chunks)
        
        if transcript:
            # Send transcript to client
            await manager.send_message(client_id, {
                "type": "stt_transcript",
                "text": transcript
            })
            
            # Process as text input
            await handle_user_text(client_id, transcript, session_state)
            
    except Exception as e:
        logger.error(f"STT error: {e}")
        await manager.send_message(client_id, {
            "type": "error",
            "message": "Ses tanıma başarısız oldu. Lütfen tekrar deneyin."
        })


async def handle_interrupt(client_id: str):
    """Handle TTS interrupt request."""
    await tts_service.stop_playback(client_id)
    await manager.send_message(client_id, {
        "type": "tts_stopped"
    })


async def generate_tts(client_id: str, text: str):
    """Generate TTS chunks for the given text."""
    try:
        async for chunk_url in tts_service.generate_speech(text, client_id):
            await manager.send_message(client_id, {
                "type": "tts_chunk",
                "url": chunk_url
            })
    except Exception as e:
        logger.error(f"TTS error: {e}")


# Static file serving for TTS audio files
app.mount("/audio", StaticFiles(directory="backend/audio_cache"), name="audio")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
