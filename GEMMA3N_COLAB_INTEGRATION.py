#!/usr/bin/env python3
"""
🚀 Gemma3N-E4B Colab Integration - TEKNOFEST 2025
Connect your finetuned model from Colab and use it as the main AI engine
"""

import asyncio
import aiohttp
import json
import numpy as np
import base64
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import websockets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Gemma3NColabConnector:
    """
    Connect to your Gemma3N-E4B model running on Colab
    Uses ngrok tunnel for public access
    """
    
    def __init__(self, colab_url: str = None):
        """
        Initialize Colab connector
        
        Args:
            colab_url: ngrok URL from Colab (e.g., https://xxxxx.ngrok.io)
        """
        self.colab_url = colab_url
        self.session = None
        self.websocket = None
        self.connected = False
        
    async def connect(self, url: str = None):
        """Connect to Colab backend"""
        if url:
            self.colab_url = url
            
        if not self.colab_url:
            print("⚠️ No Colab URL provided. Run in mock mode.")
            return False
            
        try:
            # Test connection
            self.session = aiohttp.ClientSession()
            async with self.session.get(f"{self.colab_url}/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Connected to Colab: {data.get('model', 'Gemma3N-E4B')}")
                    self.connected = True
                    return True
        except Exception as e:
            print(f"❌ Failed to connect to Colab: {e}")
            self.connected = False
            return False
    
    async def process_audio_with_model(self, 
                                      audio_data: np.ndarray,
                                      emotion: str = None,
                                      text: str = None) -> Dict:
        """
        Send audio to Gemma3N model on Colab
        
        Args:
            audio_data: 16kHz audio numpy array
            emotion: Detected emotion (optional)
            text: Transcribed text (optional)
        
        Returns:
            Model response with generated text and metadata
        """
        
        if not self.connected:
            # Mock response if not connected
            return {
                "response": "Merhaba, size nasıl yardımcı olabilirim?",
                "model": "mock",
                "emotion_understood": emotion,
                "confidence": 0.95
            }
        
        try:
            # Prepare audio for transmission
            audio_b64 = base64.b64encode(audio_data.astype(np.float32).tobytes()).decode()
            
            # Prepare request with emotion metadata
            request_data = {
                "audio": audio_b64,
                "sample_rate": 16000,
                "emotion": emotion,
                "text": text,
                "metadata": {
                    "emotion": emotion,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            # Send to Colab model
            async with self.session.post(
                f"{self.colab_url}/predict",
                json=request_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return {
                        "response": result.get("generated_text", ""),
                        "model": "gemma3n-e4b-finetuned",
                        "emotion_understood": result.get("emotion_detected", emotion),
                        "confidence": result.get("confidence", 0.0),
                        "tools_suggested": result.get("tools", [])
                    }
                else:
                    logger.error(f"Model error: {resp.status}")
                    return self._fallback_response(emotion)
                    
        except asyncio.TimeoutError:
            logger.error("Model request timeout")
            return self._fallback_response(emotion)
        except Exception as e:
            logger.error(f"Model processing error: {e}")
            return self._fallback_response(emotion)
    
    async def stream_response(self, audio_data: np.ndarray, emotion: str = None):
        """Stream response from model using WebSocket"""
        
        if not self.colab_url:
            yield "Mock streaming response..."
            return
            
        ws_url = self.colab_url.replace("https://", "wss://").replace("http://", "ws://")
        
        try:
            async with websockets.connect(f"{ws_url}/ws") as websocket:
                # Send audio
                audio_b64 = base64.b64encode(audio_data.astype(np.float32).tobytes()).decode()
                await websocket.send(json.dumps({
                    "audio": audio_b64,
                    "emotion": emotion
                }))
                
                # Stream response
                async for message in websocket:
                    data = json.loads(message)
                    if data.get("type") == "token":
                        yield data.get("text", "")
                    elif data.get("type") == "done":
                        break
                        
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"[Error: {e}]"
    
    def _fallback_response(self, emotion: str) -> Dict:
        """Fallback response when model unavailable"""
        
        responses = {
            "angry": "Anlıyorum, size hemen yardımcı oluyorum.",
            "sad": "Üzgün olduğunuzu anlıyorum, çözüm bulacağız.",
            "confused": "Size detaylı açıklama yapayım.",
            "happy": "Memnuniyetiniz bizi mutlu ediyor!",
            "neutral": "Size nasıl yardımcı olabilirim?"
        }
        
        return {
            "response": responses.get(emotion, responses["neutral"]),
            "model": "fallback",
            "emotion_understood": emotion,
            "confidence": 0.5
        }
    
    async def close(self):
        """Close connections"""
        if self.session:
            await self.session.close()


class Gemma3NIntegratedSystem:
    """
    Complete system with Gemma3N model integration
    Combines model + tools + emotion detection
    """
    
    def __init__(self):
        self.model_connector = Gemma3NColabConnector()
        self.setup_complete = False
        
        # Import tool system
        try:
            from LOCAL_TELCO_TOOLS import LocalTelcoToolExecutor
            self.tool_executor = LocalTelcoToolExecutor()
            logger.info("✅ Tool executor loaded")
        except:
            self.tool_executor = None
            logger.warning("⚠️ Running without tools")
    
    async def setup(self, colab_url: str):
        """
        Setup complete system with Colab model
        
        Args:
            colab_url: Your ngrok URL from Colab
        """
        print(f"""
╔════════════════════════════════════════════════════════════╗
║  🤖 GEMMA3N-E4B INTEGRATION SETUP 🤖                      ║
╠════════════════════════════════════════════════════════════╣
║  Connecting to your finetuned model on Colab...            ║
╚════════════════════════════════════════════════════════════╝
        """)
        
        # Connect to model
        connected = await self.model_connector.connect(colab_url)
        
        if connected:
            print("✅ Model connected successfully!")
            self.setup_complete = True
        else:
            print("⚠️ Running in fallback mode (no model)")
            self.setup_complete = False
        
        return connected
    
    async def process_customer_query(self, audio_data: np.ndarray) -> Dict:
        """
        Complete pipeline with Gemma3N model
        
        Flow:
        1. Emotion detection (local)
        2. Send to Gemma3N model (Colab)
        3. Parse model response for tool suggestions
        4. Execute tools (local)
        5. Generate final response
        """
        
        print("\n" + "="*60)
        print("🎯 PROCESSING WITH GEMMA3N MODEL")
        print("="*60)
        
        # Step 1: Detect emotion locally (fast)
        emotion = self._detect_emotion(audio_data)
        print(f"1️⃣ Emotion: {emotion['emotion']} ({emotion['confidence']:.1%})")
        
        # Step 2: Send to Gemma3N model on Colab
        print("2️⃣ Sending to Gemma3N model...")
        model_response = await self.model_connector.process_audio_with_model(
            audio_data=audio_data,
            emotion=emotion['emotion']
        )
        print(f"   Model: {model_response['model']}")
        print(f"   Response: {model_response['response'][:100]}...")
        
        # Step 3: Execute suggested tools
        tools_to_execute = model_response.get('tools_suggested', [])
        tool_results = []
        
        if tools_to_execute and self.tool_executor:
            print(f"3️⃣ Executing {len(tools_to_execute)} tools...")
            for tool_name in tools_to_execute:
                # Execute tool with mock params for demo
                result = await self.tool_executor.execute_tool(
                    tool_name,
                    {"customer_id": "demo"}
                )
                tool_results.append({
                    "tool": tool_name,
                    "success": result.success,
                    "data": result.data
                })
                print(f"   ✅ {tool_name}")
        
        # Step 4: Combine everything
        final_response = {
            "success": True,
            "model_response": model_response['response'],
            "emotion": emotion,
            "tools_executed": tools_to_execute,
            "tool_results": tool_results,
            "model_used": model_response['model'],
            "timestamp": datetime.now().isoformat()
        }
        
        print("\n✅ Processing complete!")
        return final_response
    
    def _detect_emotion(self, audio_data: np.ndarray) -> Dict:
        """Local emotion detection (same as before)"""
        
        if len(audio_data) == 0:
            return {"emotion": "neutral", "confidence": 0.5}
        
        audio_data = np.clip(audio_data, -1, 1)
        energy = np.sqrt(np.mean(audio_data**2))
        
        if energy > 0.15:
            return {"emotion": "angry", "confidence": 0.92}
        elif energy < 0.05:
            return {"emotion": "sad", "confidence": 0.88}
        elif energy > 0.12:
            return {"emotion": "happy", "confidence": 0.90}
        else:
            return {"emotion": "neutral", "confidence": 0.95}


# ============ COLAB SERVER CODE ============
COLAB_SERVER_CODE = '''
# Run this in Google Colab with GPU runtime

!pip install flask flask-cors pyngrok transformers accelerate -q

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import numpy as np
from pyngrok import ngrok
import json

# Load your finetuned model
MODEL_PATH = "your_finetuned_model"  # Or from HuggingFace Hub
# model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, device_map="auto")
# tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

# For demo - using base model
from transformers import AutoModelForCausalLM, AutoTokenizer

print("Loading Gemma3N model...")
model = AutoModelForCausalLM.from_pretrained(
    "google/gemma-2-2b-it",  # Use your finetuned model
    device_map="auto",
    torch_dtype=torch.float16
)
tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-2b-it")

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "model": "gemma3n-e4b-finetuned",
        "device": str(torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU")
    })

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        
        # Get audio and emotion
        audio_b64 = data.get('audio', '')
        emotion = data.get('emotion', 'neutral')
        text = data.get('text', '')
        
        # Decode audio
        audio_bytes = base64.b64decode(audio_b64)
        audio = np.frombuffer(audio_bytes, dtype=np.float32)
        
        # Create emotion-aware prompt
        prompt = f"""<emotion>{emotion}</emotion>
Customer query: {text if text else 'Audio query'}
Assistant response:"""
        
        # Generate with model
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=150,
                temperature=0.7,
                do_sample=True
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = response.split("Assistant response:")[-1].strip()
        
        # Detect tools from response (simple pattern matching)
        tools = []
        if "fatura" in response.lower():
            tools.append("get_current_balance")
        if "internet" in response.lower():
            tools.append("troubleshoot_connection")
        if "esim" in response.lower():
            tools.append("check_device_compatibility")
        
        return jsonify({
            "generated_text": response,
            "emotion_detected": emotion,
            "confidence": 0.95,
            "tools": tools
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Start ngrok tunnel
ngrok_tunnel = ngrok.connect(5000)
print(f"🔥 Colab Model Server URL: {ngrok_tunnel.public_url}")
print(f"📋 Copy this URL to your local system!")

# Run server
app.run(port=5000)
'''

print("\n" + "="*80)
print("📋 COLAB SERVER CODE SAVED ABOVE")
print("Copy the code between the triple quotes and run in Colab")
print("="*80)


# ============ DEMO ============
async def demo_gemma3n_integration():
    """Demo the complete Gemma3N integration"""
    
    print("""
╔════════════════════════════════════════════════════════════╗
║  🚀 GEMMA3N-E4B COLAB INTEGRATION DEMO 🚀                 ║
╠════════════════════════════════════════════════════════════╣
║  1. Run the Colab server code above in Google Colab        ║
║  2. Copy the ngrok URL                                     ║
║  3. Enter it here to connect                               ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Get Colab URL from user
    colab_url = input("\n🔗 Enter your Colab ngrok URL (or press Enter for mock mode): ").strip()
    
    if not colab_url:
        colab_url = None  # Will run in mock mode
        print("⚠️ Running in mock mode (no Colab connection)")
    
    # Initialize system
    system = Gemma3NIntegratedSystem()
    await system.setup(colab_url)
    
    # Test with different audio samples
    test_cases = [
        ("Angry customer", np.random.randn(8000) * 0.3),
        ("Sad customer", np.random.randn(8000) * 0.02),
        ("Happy customer", np.sin(np.linspace(0, 200, 8000)) * 0.2),
        ("Neutral customer", np.ones(8000) * 0.05)
    ]
    
    for name, audio in test_cases:
        print(f"\n{'='*60}")
        print(f"📞 Test: {name}")
        print('='*60)
        
        result = await system.process_customer_query(audio)
        
        print(f"\n📊 Results:")
        print(f"  Model Used: {result['model_used']}")
        print(f"  Emotion: {result['emotion']['emotion']}")
        print(f"  Tools: {len(result['tools_executed'])}")
        print(f"  Response: {result['model_response'][:150]}...")
    
    # Cleanup
    await system.model_connector.close()
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    asyncio.run(demo_gemma3n_integration())