#!/usr/bin/env python3
"""
TEKNOFEST 2025 - SIMPLE BACKEND
Clean, fast backend for AI conversations
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Optional
from aiohttp import web
import aiohttp_cors
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import optional components
try:
    from TURKISH_TTS_ENGINE import TurkishTTSEngine
    TTS_AVAILABLE = True
except:
    TTS_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except:
    REQUESTS_AVAILABLE = False

class SimpleBackend:
    """Simple backend for AI conversations"""
    
    def __init__(self, model_url: Optional[str] = None):
        self.model_url = model_url
        self.conversation_history = []
        
        # Initialize TTS if available
        if TTS_AVAILABLE and os.path.exists("tr_TR-fahrettin-medium.onnx"):
            self.tts = TurkishTTSEngine()
            logger.info("Turkish TTS enabled")
        else:
            self.tts = None
            logger.info("TTS disabled")
    
    async def process_message(self, user_message: str, emotion: str = "neutral") -> Dict:
        """Process user message and return response"""
        
        # Call AI model if available
        if self.model_url and REQUESTS_AVAILABLE:
            try:
                response = requests.post(
                    f"{self.model_url}/predict",
                    json={"text": user_message, "emotion": emotion},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get("generated_text", "")
                    
                    # Clean up response
                    if "assistant" in ai_response:
                        ai_response = ai_response.split("assistant")[-1].strip()
                    
                    model_used = "gemma3n-finetuned"
                else:
                    raise Exception(f"Model returned {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"Model error: {e}, using fallback")
                ai_response = self._fallback_response(user_message, emotion)
                model_used = "fallback"
        else:
            ai_response = self._fallback_response(user_message, emotion)
            model_used = "fallback"
        
        # Generate TTS if available
        audio_file = None
        if self.tts:
            try:
                audio_file = await self.tts.generate_speech_async(ai_response, emotion)
            except Exception as e:
                logger.error(f"TTS error: {e}")
        
        # Save conversation
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "emotion": emotion,
            "ai_response": ai_response,
            "model_used": model_used,
            "audio_file": audio_file
        }
        self.conversation_history.append(conversation)
        
        return {
            "response": ai_response,
            "emotion": emotion,
            "model_used": model_used,
            "audio_file": os.path.basename(audio_file) if audio_file else None,
            "audio_url": f"/audio/{os.path.basename(audio_file)}" if audio_file else None,
            "tts_available": self.tts is not None
        }
    
    def _fallback_response(self, message: str, emotion: str) -> str:
        """Simple fallback responses"""
        
        # Emotion-based greetings
        greetings = {
            "angry": "Yaşadığınız sorun için özür dileriz. Hemen yardımcı oluyorum.",
            "sad": "Size yardımcı olmak için buradayım.",
            "confused": "Sorununuzu anlıyorum, açıklayayım.",
            "happy": "Merhaba! Size nasıl yardımcı olabilirim?",
            "neutral": "Hoş geldiniz, size yardımcı oluyorum."
        }
        
        greeting = greetings.get(emotion, greetings["neutral"])
        
        # Simple keyword matching
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["fatura", "bakiye", "balance"]):
            return f"{greeting} Bakiyeniz 250 TL. Hesabınız aktif durumda."
        
        elif any(word in message_lower for word in ["esim", "sim"]):
            return f"{greeting} eSIM aktivasyonu için cihazınızın uyumlu olması gerekiyor. Hangi cihazınız var?"
        
        elif any(word in message_lower for word in ["internet", "bağlantı", "yavaş"]):
            return f"{greeting} İnternet bağlantı sorununuzu kontrol ediyorum. Modemin ışıkları yanıyor mu?"
        
        elif any(word in message_lower for word in ["paket", "plan"]):
            return f"{greeting} Mevcut paketiniz: Premium 100GB. Aylık ücreti 150 TL."
        
        elif any(word in message_lower for word in ["yardım", "destek"]):
            return f"{greeting} Size şu konularda yardımcı olabilirim: Fatura, eSIM, internet, paket bilgileri."
        
        else:
            return f"{greeting} Size nasıl yardımcı olabilirim? Fatura, eSIM, internet veya paket konularında destek verebilirim."

# Create backend instance
backend = None

async def handle_chat(request):
    """Handle chat requests"""
    try:
        data = await request.json()
        message = data.get("message", "")
        emotion = data.get("emotion", "neutral")
        
        if not message:
            return web.json_response({"error": "Message required"}, status=400)
        
        result = await backend.process_message(message, emotion)
        return web.json_response(result)
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def handle_health(request):
    """Health check"""
    return web.json_response({
        "status": "healthy",
        "model_connected": backend.model_url is not None,
        "tts_available": backend.tts is not None,
        "conversations": len(backend.conversation_history)
    })

async def serve_audio(request):
    """Serve audio files"""
    filename = request.match_info.get('filename')
    
    # Find audio file in temp directory
    import tempfile
    temp_dir = tempfile.gettempdir()
    audio_path = os.path.join(temp_dir, filename)
    
    if os.path.exists(audio_path) and filename.endswith('.wav'):
        return web.FileResponse(audio_path, headers={'Content-Type': 'audio/wav'})
    else:
        return web.Response(status=404, text="Audio not found")

async def get_history(request):
    """Get conversation history"""
    limit = int(request.query.get('limit', 10))
    history = backend.conversation_history[-limit:]
    return web.json_response({"history": history})

async def clear_history(request):
    """Clear conversation history"""
    backend.conversation_history.clear()
    return web.json_response({"message": "History cleared"})

async def run_server(model_url: Optional[str] = None, port: int = 8000):
    """Run the simple backend server"""
    global backend
    
    # Initialize backend
    backend = SimpleBackend(model_url)
    
    # Create app
    app = web.Application()
    
    # Setup CORS
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })
    
    # Add routes
    routes = [
        web.post('/chat', handle_chat),
        web.get('/health', handle_health),
        web.get('/audio/{filename}', serve_audio),
        web.get('/history', get_history),
        web.delete('/history', clear_history)
    ]
    
    for route in routes:
        cors.add(app.router.add_route(route.method, route.path, route.handler))
    
    # Start server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', port)
    await site.start()
    
    print(f"""
    ╔════════════════════════════════════════╗
    ║  TEKNOFEST 2025 - SIMPLE BACKEND      ║
    ╠════════════════════════════════════════╣
    ║  Running: http://localhost:{port}         ║
    ║  Model: {'Connected' if model_url else 'Fallback'}            ║
    ║  TTS: {'Enabled' if backend.tts else 'Disabled'}              ║
    ╚════════════════════════════════════════╝
    
    API Endpoints:
    POST /chat        - Send message, get AI response
    GET  /health      - System status
    GET  /history     - Conversation history
    GET  /audio/{file} - Serve TTS audio
    
    Test:
    curl -X POST http://localhost:{port}/chat \\
      -H "Content-Type: application/json" \\
      -d '{{"message": "Merhaba", "emotion": "happy"}}'
    """)
    
    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    import sys
    
    # Get model URL from command line
    model_url = sys.argv[1] if len(sys.argv) > 1 else None
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    
    if model_url:
        print(f"Connecting to model: {model_url}")
    else:
        print("Running in fallback mode (no AI model)")
    
    # Run server
    asyncio.run(run_server(model_url, port))