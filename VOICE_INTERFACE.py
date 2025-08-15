#!/usr/bin/env python3
"""
TEKNOFEST 2025 - SIMPLE VOICE INTERFACE
Talk to AI with microphone - emotion detection + response
"""

import asyncio
import numpy as np
import sounddevice as sd
import requests
import json
from datetime import datetime
import tempfile
import wave
import os

class SimpleVoiceInterface:
    """Simple mic input -> emotion -> AI -> response"""
    
    def __init__(self, server_url="http://localhost:8000"):
        self.server_url = server_url
        self.sample_rate = 16000
        self.duration = 5  # 5 seconds recording
        self.recording = False
        
    def record_audio(self):
        """Record audio from microphone"""
        print("🎤 Recording... (5 seconds)")
        audio_data = sd.rec(
            int(self.duration * self.sample_rate), 
            samplerate=self.sample_rate, 
            channels=1,
            dtype=np.float32
        )
        sd.wait()  # Wait for recording to complete
        print("✅ Recording complete")
        return audio_data.flatten()
    
    def detect_emotion_from_audio(self, audio_data):
        """Use existing emotion detection from ENTERPRISE_TELCO_PLATFORM"""
        try:
            from ENTERPRISE_TELCO_PLATFORM import EmotionAnalysisEngine
            detector = EmotionAnalysisEngine()
            return detector.detect_emotion(audio_data)
        except:
            # Fallback emotion detection
            if len(audio_data) == 0:
                return "neutral"
            
            energy = np.mean(np.abs(audio_data))
            variance = np.var(audio_data)
            
            if energy > 0.05 and variance > 0.01:
                return "angry"
            elif energy < 0.01:
                return "sad"
            elif variance > 0.02:
                return "confused"
            elif energy > 0.02 and variance < 0.005:
                return "happy"
            else:
                return "neutral"
    
    def audio_to_text(self, audio_data):
        """No text conversion - Gemma 3N processes audio directly"""
        print("🎵 Sending audio directly to Gemma 3N (no text conversion needed)")
        return ""  # Empty text - pure audio input
    
    async def send_to_ai(self, text, emotion, audio_data=None):
        """Send audio directly to Gemma 3N model"""
        try:
            print(f"🤖 Sending audio + text to Gemma 3N: '{text}' (emotion: {emotion})")
            
            # Prepare request with native audio
            payload = {
                "text": text,
                "emotion": emotion
            }
            
            # Send full audio to Gemma 3N (30s max, 16kHz)
            if audio_data is not None:
                # Ensure 16kHz, max 30 seconds (480k samples)
                max_samples = 16000 * 30  # 30 seconds at 16kHz
                if len(audio_data) > max_samples:
                    audio_data = audio_data[:max_samples]
                
                payload["audio_data"] = audio_data.tolist()
                print(f"🎵 Sending {len(audio_data)} audio samples to model")
            
            response = requests.post(
                f"{self.server_url}/process",
                json=payload,
                timeout=15  # Longer timeout for audio processing
            )
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                print(f"❌ Server error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def play_response(self, result):
        """Display and optionally play audio response"""
        if not result:
            print("❌ No response from AI")
            return
        
        # Display response
        print("\n" + "="*60)
        print(f"🤖 AI Response: {result.get('response', 'No response')}")
        print(f"😊 Emotion: {result.get('emotion', 'unknown')}")
        print(f"🔧 Tools used: {result.get('tools_executed', [])}")
        print(f"🎵 Audio: {'Available' if result.get('audio_file') else 'Not available'}")
        print("="*60)
        
        # Try to play audio if available
        audio_file = result.get('audio_file')
        if audio_file:
            try:
                audio_url = f"{self.server_url}/audio/{os.path.basename(audio_file)}"
                print(f"🔊 Audio available at: {audio_url}")
                # Note: Could add audio playback here
            except Exception as e:
                print(f"⚠️ Audio playback error: {e}")
    
    async def voice_chat_loop(self):
        """Main voice chat loop"""
        print("""
╔════════════════════════════════════════════════════════════╗
║  TEKNOFEST 2025 - VOICE INTERFACE                         ║
║  Talk to AI with microphone input                         ║
╚════════════════════════════════════════════════════════════╝

Commands:
- Press ENTER to start recording
- Type 'quit' to exit
- Type 'test' for connection test

""")
        
        while True:
            try:
                # Get user command
                command = input("\n🎤 Press ENTER to record (or 'quit'/'test'): ").strip().lower()
                
                if command == 'quit':
                    print("👋 Goodbye!")
                    break
                
                elif command == 'test':
                    # Test connection
                    try:
                        response = requests.get(f"{self.server_url}/health", timeout=5)
                        if response.status_code == 200:
                            health = response.json()
                            print(f"✅ Server healthy: {health}")
                        else:
                            print(f"❌ Server unhealthy: {response.status_code}")
                    except Exception as e:
                        print(f"❌ Connection failed: {e}")
                    continue
                
                elif command == '' or command == 'record':
                    # Record audio
                    try:
                        audio_data = self.record_audio()
                        
                        # Detect emotion
                        emotion = self.detect_emotion_from_audio(audio_data)
                        print(f"😊 Detected emotion: {emotion}")
                        
                        # No text conversion - pure audio to Gemma 3N
                        text = self.audio_to_text(audio_data)
                        
                        # Send audio directly to AI (text can be empty)
                        result = await self.send_to_ai(text, emotion, audio_data)
                        
                        # Play response
                        self.play_response(result)
                            
                    except Exception as e:
                        print(f"❌ Recording error: {e}")
                        print("💡 Make sure your microphone is connected")
                
                else:
                    print("❓ Unknown command. Press ENTER to record, 'test' to check connection, or 'quit' to exit.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

async def main():
    """Main function"""
    import sys
    
    # Get server URL from command line
    server_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print(f"🔗 Connecting to: {server_url}")
    
    # Create voice interface
    voice = SimpleVoiceInterface(server_url)
    
    # Start voice chat
    await voice.voice_chat_loop()

if __name__ == "__main__":
    # Check dependencies
    try:
        import sounddevice
        import numpy
        import requests
        print("✅ All dependencies available")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Install with: pip install sounddevice numpy requests")
        exit(1)
    
    # Run voice interface
    asyncio.run(main())