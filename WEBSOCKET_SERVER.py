#!/usr/bin/env python3
"""
🚀 WebSocket Server for Real-time Emotion-Aware AI
Simple yet powerful WebSocket server for TEKNOFEST 2025
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
from typing import Dict, Optional
import uvicorn
from datetime import datetime

# Import our pipeline
from PRODUCTION_PIPELINE import (
    EmotionAwarePipeline,
    AudioProcessor,
    EmotionAnalyzer,
    CustomerProfiler,
    GemmaInference,
    AgentRouter,
    TTSEngine
)

# ============= FASTAPI APP =============
app = FastAPI(title="TEKNOFEST 2025 Telco AI")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= CONNECTION MANAGER =============
class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.pipeline = None
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept new connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
        # Initialize pipeline if needed
        if not self.pipeline:
            self.pipeline = EmotionAwarePipeline()
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection",
            "status": "connected",
            "message": "TEKNOFEST 2025 AI Pipeline Ready!",
            "timestamp": datetime.now().isoformat()
        }, client_id)
    
    def disconnect(self, client_id: str):
        """Remove connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def send_personal_message(self, message: dict, client_id: str):
        """Send message to specific client"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_json(message)
    
    async def broadcast(self, message: dict):
        """Broadcast to all connections"""
        for connection in self.active_connections.values():
            await connection.send_json(message)

# Initialize manager
manager = ConnectionManager()

# ============= WEBSOCKET ENDPOINT =============
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Main WebSocket endpoint"""
    
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            # Process based on message type
            if data["type"] == "audio":
                await process_audio_message(data, client_id)
            
            elif data["type"] == "text":
                await process_text_message(data, client_id)
            
            elif data["type"] == "command":
                await process_command(data, client_id)
            
            else:
                await manager.send_personal_message({
                    "type": "error",
                    "message": f"Unknown message type: {data['type']}"
                }, client_id)
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        print(f"Client {client_id} disconnected")
    
    except Exception as e:
        print(f"Error: {e}")
        manager.disconnect(client_id)

# ============= MESSAGE PROCESSORS =============
async def process_audio_message(data: dict, client_id: str):
    """Process audio input"""
    
    # Send processing status
    await manager.send_personal_message({
        "type": "status",
        "stage": "processing_audio",
        "message": "Processing your voice..."
    }, client_id)
    
    # Get audio data
    audio_data = data.get("audio")  # Base64 or file path
    
    # Process through pipeline
    pipeline = manager.pipeline
    
    # Step 1: Transcribe
    audio_processor = pipeline.audio_processor
    transcription = audio_processor.process_audio(audio_data)
    
    await manager.send_personal_message({
        "type": "transcription",
        "text": transcription["text"],
        "emotion_detected": transcription.get("emotion")
    }, client_id)
    
    # Step 2: Analyze emotion
    emotion_analyzer = pipeline.emotion_analyzer
    emotion_data = emotion_analyzer.detect_emotion(
        transcription["text"],
        transcription
    )
    
    await manager.send_personal_message({
        "type": "emotion_analysis",
        "emotion": emotion_data["emotion"],
        "confidence": emotion_data["confidence"],
        "pace": emotion_data.get("pace")
    }, client_id)
    
    # Step 3: Build profile
    profiler = pipeline.customer_profiler
    profile_data = profiler.build_profile(transcription["text"])
    
    await manager.send_personal_message({
        "type": "profile",
        "profile_type": profile_data["type"],
        "priority": profile_data["priority"],
        "traits": profile_data.get("traits", [])
    }, client_id)
    
    # Step 4: Generate response
    model = pipeline.model
    response = model.generate_response(
        transcription["text"],
        emotion_data,
        profile_data
    )
    
    # Step 5: Send response
    await stream_response(response, emotion_data["emotion"], client_id)

async def process_text_message(data: dict, client_id: str):
    """Process text input"""
    
    text = data.get("text", "")
    
    # Send processing status
    await manager.send_personal_message({
        "type": "status",
        "stage": "processing_text",
        "message": "Analyzing your message..."
    }, client_id)
    
    pipeline = manager.pipeline
    
    # Analyze emotion from text
    emotion_analyzer = pipeline.emotion_analyzer
    emotion_data = emotion_analyzer.detect_emotion(text, {})
    
    await manager.send_personal_message({
        "type": "emotion_analysis",
        "emotion": emotion_data["emotion"],
        "confidence": emotion_data["confidence"]
    }, client_id)
    
    # Build profile
    profiler = pipeline.customer_profiler
    profile_data = profiler.build_profile(text)
    
    # Generate response
    model = pipeline.model
    response = model.generate_response(text, emotion_data, profile_data)
    
    # Stream response
    await stream_response(response, emotion_data["emotion"], client_id)

async def stream_response(response: dict, emotion: str, client_id: str):
    """Stream response to client"""
    
    # Send agent info
    await manager.send_personal_message({
        "type": "agent",
        "name": response.get("agent", "RouterAgent"),
        "action": "responding"
    }, client_id)
    
    # Stream text response
    text = response.get("response", "")
    words = text.split()
    
    # Stream word by word for effect
    for i in range(0, len(words), 3):
        chunk = " ".join(words[i:i+3])
        await manager.send_personal_message({
            "type": "response_chunk",
            "text": chunk,
            "is_final": i + 3 >= len(words)
        }, client_id)
        await asyncio.sleep(0.1)  # Small delay for streaming effect
    
    # Send tools used
    if response.get("tools"):
        await manager.send_personal_message({
            "type": "tools_used",
            "tools": response["tools"]
        }, client_id)
    
    # Generate TTS
    tts_engine = manager.pipeline.tts
    audio_output = tts_engine.synthesize(text, emotion)
    
    await manager.send_personal_message({
        "type": "audio_response",
        "audio_url": audio_output,
        "emotion_tone": emotion
    }, client_id)

async def process_command(data: dict, client_id: str):
    """Process command messages"""
    
    command = data.get("command")
    
    if command == "reset":
        # Reset conversation
        await manager.send_personal_message({
            "type": "reset",
            "status": "success",
            "message": "Conversation reset"
        }, client_id)
    
    elif command == "get_stats":
        # Send statistics
        stats = {
            "total_connections": len(manager.active_connections),
            "model_status": "active" if manager.pipeline else "inactive",
            "supported_emotions": ["angry", "confused", "worried", "happy", "neutral"],
            "available_agents": ["RouterAgent", "TechAgent", "BillingAgent", "PlanAgent", "FAQAgent"]
        }
        
        await manager.send_personal_message({
            "type": "stats",
            "data": stats
        }, client_id)
    
    else:
        await manager.send_personal_message({
            "type": "error",
            "message": f"Unknown command: {command}"
        }, client_id)

# ============= REST ENDPOINTS =============
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "TEKNOFEST 2025 Emotion-Aware Telco AI",
        "status": "running",
        "websocket": "/ws/{client_id}",
        "features": [
            "Emotion-aware responses",
            "Customer profiling",
            "5 specialized agents",
            "21 telco tools",
            "Real-time streaming"
        ]
    }

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "connections": len(manager.active_connections)
    }

@app.get("/agents")
async def get_agents():
    """Get available agents"""
    return {
        "agents": [
            {
                "name": "RouterAgent",
                "role": "Initial routing and emotion detection",
                "priority": "high"
            },
            {
                "name": "TechAgent",
                "role": "Technical support and troubleshooting",
                "priority": "high"
            },
            {
                "name": "BillingAgent",
                "role": "Billing and payment queries",
                "priority": "medium"
            },
            {
                "name": "PlanAgent",
                "role": "Package and plan recommendations",
                "priority": "medium"
            },
            {
                "name": "FAQAgent",
                "role": "General questions and information",
                "priority": "low"
            }
        ]
    }

@app.get("/emotions")
async def get_emotions():
    """Get supported emotions"""
    return {
        "emotions": {
            "angry": {
                "indicators": ["kızgın", "sinirli", "öfkeli"],
                "response_tone": "understanding and calm",
                "priority": "high"
            },
            "confused": {
                "indicators": ["anlamadım", "nasıl", "karışık"],
                "response_tone": "clear and patient",
                "priority": "medium"
            },
            "worried": {
                "indicators": ["endişeli", "korkuyorum"],
                "response_tone": "reassuring",
                "priority": "high"
            },
            "happy": {
                "indicators": ["teşekkür", "harika", "memnun"],
                "response_tone": "cheerful",
                "priority": "low"
            },
            "neutral": {
                "indicators": [],
                "response_tone": "professional",
                "priority": "normal"
            }
        }
    }

# ============= MAIN =============
if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════╗
    ║  🚀 TEKNOFEST 2025 WEBSOCKET SERVER 🚀    ║
    ╠════════════════════════════════════════════╣
    ║  Emotion-Aware Turkish Telco AI           ║
    ║  WebSocket: ws://localhost:8000/ws/{id}   ║
    ║  REST API: http://localhost:8000          ║
    ╚════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )