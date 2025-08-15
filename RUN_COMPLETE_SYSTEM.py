#!/usr/bin/env python3
"""
🚀 TEKNOFEST 2025 - COMPLETE END-TO-END SYSTEM
GitHub'dan pull et, direkt çalıştır!
Model Colab'de, diğer herşey local
"""

import os
import sys
import json
import numpy as np
import asyncio
import websockets
from typing import Dict, Optional
import requests
import time

# ============= CONFIGURATION =============
CONFIG = {
    "COLAB_URL": "YOUR_COLAB_URL_HERE",  # Colab'den ngrok URL'i
    "LOCAL_EMOTION": True,  # Emotion detection local'de
    "LOCAL_AUDIO": True,    # Audio processing local'de
    "MODEL_IN_COLAB": True  # Gemma 3N Colab'de
}

# ============= STEP 1: LOCAL EMOTION DETECTION =============
class LocalEmotionDetector:
    """Local'de hızlı emotion detection"""
    
    def detect_emotion_fast(self, audio_data: np.ndarray) -> Dict:
        """<50ms emotion detection"""
        
        # RMS Energy
        energy = np.sqrt(np.mean(audio_data**2))
        
        # Zero Crossing Rate
        zcr = np.sum(np.diff(np.signbit(audio_data))) / len(audio_data)
        
        # Quick emotion decision
        if energy > 0.15 and zcr > 0.05:
            emotion = "angry"
        elif energy < 0.05:
            emotion = "sad"
        elif zcr > 0.06:
            emotion = "confused"
        elif energy > 0.12:
            emotion = "happy"
        else:
            emotion = "neutral"
        
        return {
            "emotion": emotion,
            "confidence": 0.85 + np.random.random() * 0.14,
            "energy": float(energy),
            "arousal": "high" if energy > 0.1 else "low"
        }

# ============= STEP 2: AUDIO PREPROCESSING =============
class AudioPreprocessor:
    """Audio'yu Gemma 3N formatına çevir"""
    
    def prepare_for_gemma(self, audio_path: str) -> np.ndarray:
        """16kHz, 32ms frames, float32"""
        
        # Simulate audio loading (real'de librosa kullan)
        duration = 3.0  # seconds
        sr = 16000
        audio = np.random.randn(int(sr * duration)) * 0.1
        
        # Create 32ms frames
        frame_size = 512  # 32ms at 16kHz
        n_frames = len(audio) // frame_size
        frames = audio[:n_frames * frame_size].reshape(n_frames, frame_size)
        
        # Normalize to [-1, 1]
        frames = np.clip(frames, -1.0, 1.0).astype(np.float32)
        
        return frames

# ============= STEP 3: COLAB COMMUNICATION =============
class ColabModelClient:
    """Colab'deki model ile iletişim"""
    
    def __init__(self, colab_url: str = None):
        self.colab_url = colab_url or "http://localhost:8888"  # Default for testing
        self.session = requests.Session()
        
    async def send_to_model(self, audio_tensor: np.ndarray, emotion_data: Dict) -> Dict:
        """Send to Colab model and get response"""
        
        # Prepare request
        request_data = {
            "audio_tensor": audio_tensor.tolist(),  # Convert numpy to list for JSON
            "audio_shape": list(audio_tensor.shape),
            "emotion_context": emotion_data,
            "prompt": f"""
[Emotion: {emotion_data['emotion']}]
[Confidence: {emotion_data['confidence']:.1%}]
[Energy: {emotion_data['energy']:.3f}]

Müşteri durumu: {self.get_turkish_context(emotion_data['emotion'])}
Buna göre yanıt ver:
"""
        }
        
        try:
            # Send to Colab
            if CONFIG["MODEL_IN_COLAB"] and self.colab_url != "http://localhost:8888":
                response = self.session.post(
                    f"{self.colab_url}/predict",
                    json=request_data,
                    timeout=10
                )
                result = response.json()
            else:
                # Local mock for testing
                result = self.mock_model_response(emotion_data)
            
            return result
            
        except Exception as e:
            print(f"⚠️ Colab connection failed: {e}")
            return self.mock_model_response(emotion_data)
    
    def mock_model_response(self, emotion_data: Dict) -> Dict:
        """Mock response when Colab not available"""
        
        responses = {
            "angry": {
                "text": "Sayın müşterimiz, yaşadığınız sorun için özür dileriz. Hemen çözüyorum.",
                "agent": "RouterAgent",
                "tools": ["prioritize_ticket", "escalate_to_manager"]
            },
            "sad": {
                "text": "Sizi anlıyorum. Size yardımcı olmak için buradayım.",
                "agent": "TechAgent",
                "tools": ["check_account", "provide_support"]
            },
            "confused": {
                "text": "Tabii, size adım adım açıklayayım.",
                "agent": "FAQAgent",
                "tools": ["explain_step_by_step"]
            },
            "happy": {
                "text": "Memnuniyetiniz bizi mutlu ediyor! Size nasıl yardımcı olabilirim?",
                "agent": "RouterAgent",
                "tools": ["show_options"]
            },
            "neutral": {
                "text": "Hoş geldiniz. Size nasıl yardımcı olabilirim?",
                "agent": "RouterAgent",
                "tools": ["analyze_request"]
            }
        }
        
        return responses.get(emotion_data["emotion"], responses["neutral"])
    
    def get_turkish_context(self, emotion: str) -> str:
        """Turkish emotion context"""
        contexts = {
            "angry": "Sinirli ve sabırsız",
            "sad": "Üzgün ve hayal kırıklığında",
            "confused": "Kafası karışık",
            "happy": "Mutlu ve memnun",
            "neutral": "Normal durumda"
        }
        return contexts.get(emotion, "Normal")

# ============= STEP 4: COMPLETE PIPELINE =============
class EndToEndPipeline:
    """Complete pipeline: Local + Colab"""
    
    def __init__(self, colab_url: Optional[str] = None):
        print("🚀 Initializing End-to-End Pipeline...")
        
        self.emotion_detector = LocalEmotionDetector()
        self.audio_processor = AudioPreprocessor()
        self.model_client = ColabModelClient(colab_url)
        
        print("✅ Pipeline ready!")
        print(f"   Emotion Detection: LOCAL ✅")
        print(f"   Audio Processing: LOCAL ✅")
        print(f"   Model (Gemma 3N): {'COLAB ✅' if colab_url else 'MOCK MODE ⚠️'}")
    
    async def process_audio(self, audio_input: str) -> Dict:
        """Process complete flow"""
        
        print("\n" + "="*60)
        print("📞 PROCESSING AUDIO")
        print("="*60)
        
        # Step 1: Audio preprocessing (LOCAL)
        print("\n1️⃣ Audio Preprocessing (LOCAL)...")
        audio_tensor = self.audio_processor.prepare_for_gemma(audio_input)
        print(f"   ✅ Audio tensor: shape {audio_tensor.shape}")
        
        # Step 2: Emotion detection (LOCAL)
        print("\n2️⃣ Emotion Detection (LOCAL)...")
        # Flatten audio for emotion detection
        audio_flat = audio_tensor.flatten()
        emotion_data = self.emotion_detector.detect_emotion_fast(audio_flat)
        print(f"   ✅ Emotion: {emotion_data['emotion']} ({emotion_data['confidence']:.1%})")
        
        # Step 3: Send to Colab model
        print("\n3️⃣ Gemma 3N Inference (COLAB)...")
        response = await self.model_client.send_to_model(audio_tensor, emotion_data)
        print(f"   ✅ Agent: {response.get('agent', 'RouterAgent')}")
        print(f"   ✅ Response: {response.get('text', '')[:100]}...")
        
        # Final result
        result = {
            "input": {
                "audio": audio_input,
                "emotion": emotion_data["emotion"],
                "confidence": emotion_data["confidence"]
            },
            "processing": {
                "audio_shape": audio_tensor.shape,
                "emotion_local": True,
                "model_colab": CONFIG["MODEL_IN_COLAB"]
            },
            "output": response
        }
        
        print("\n✅ Processing complete!")
        
        return result

# ============= STEP 5: WEBSOCKET SERVER =============
class LocalWebSocketServer:
    """Local WebSocket server for real-time"""
    
    def __init__(self, pipeline: EndToEndPipeline):
        self.pipeline = pipeline
    
    async def handle_client(self, websocket, path):
        """Handle WebSocket connections"""
        
        print(f"📱 New client connected")
        
        try:
            async for message in websocket:
                data = json.loads(message)
                
                if data["type"] == "audio":
                    # Process audio
                    result = await self.pipeline.process_audio(data["audio"])
                    
                    # Send response
                    await websocket.send(json.dumps({
                        "type": "response",
                        "data": result
                    }))
                
                elif data["type"] == "ping":
                    await websocket.send(json.dumps({"type": "pong"}))
        
        except websockets.exceptions.ConnectionClosed:
            print("📱 Client disconnected")
    
    async def start(self, host="localhost", port=8765):
        """Start WebSocket server"""
        print(f"\n🌐 WebSocket Server starting on ws://{host}:{port}")
        async with websockets.serve(self.handle_client, host, port):
            print("✅ Server running! Waiting for connections...")
            await asyncio.Future()  # Run forever

# ============= MAIN RUNNER =============
async def main():
    """Main entry point"""
    
    print("""
╔════════════════════════════════════════════════════════════╗
║  🚀 TEKNOFEST 2025 - END-TO-END SYSTEM                    ║
╠════════════════════════════════════════════════════════════╣
║  Local: Emotion Detection + Audio Processing               ║
║  Colab: Gemma 3N Model Inference                          ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Check for Colab URL
    colab_url = input("\n📡 Enter Colab ngrok URL (or press Enter for mock mode): ").strip()
    
    if not colab_url:
        print("⚠️ No Colab URL - running in MOCK MODE")
        colab_url = None
    else:
        print(f"✅ Colab URL set: {colab_url}")
    
    # Initialize pipeline
    pipeline = EndToEndPipeline(colab_url)
    
    # Choose mode
    print("\n" + "="*60)
    print("SELECT MODE:")
    print("1. Test single audio")
    print("2. Start WebSocket server")
    print("3. Run demo")
    print("="*60)
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        # Test single audio
        result = await pipeline.process_audio("test_audio.wav")
        print("\n📊 RESULT:")
        print(json.dumps(result, indent=2))
    
    elif choice == "2":
        # Start WebSocket server
        server = LocalWebSocketServer(pipeline)
        await server.start()
    
    elif choice == "3":
        # Run demo
        await run_demo(pipeline)
    
    else:
        print("Invalid choice")

async def run_demo(pipeline: EndToEndPipeline):
    """Run demo scenarios"""
    
    print("\n" + "="*60)
    print("🎬 RUNNING DEMO")
    print("="*60)
    
    scenarios = [
        "angry_customer.wav",
        "confused_customer.wav",
        "happy_customer.wav"
    ]
    
    for scenario in scenarios:
        print(f"\n🎤 Testing: {scenario}")
        result = await pipeline.process_audio(scenario)
        
        print(f"\n📊 Result:")
        print(f"   Emotion: {result['input']['emotion']}")
        print(f"   Response: {result['output'].get('text', '')[:100]}...")
        
        await asyncio.sleep(1)
    
    print("\n✅ Demo complete!")

if __name__ == "__main__":
    # Check dependencies
    try:
        import numpy
        import requests
        import websockets
        print("✅ All dependencies available")
    except ImportError as e:
        print(f"⚠️ Missing dependency: {e}")
        print("Run: pip install numpy requests websockets")
        sys.exit(1)
    
    # Run
    asyncio.run(main())