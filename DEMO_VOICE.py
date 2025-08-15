#!/usr/bin/env python3
"""
TEKNOFEST 2025 - VOICE DEMO
Simple terminal interface: Press ENTER → Talk → Get AI + Tools response
"""

import sounddevice as sd
import numpy as np
import requests
import json
from datetime import datetime

def record_audio(duration=5):
    """Record audio from microphone"""
    print("🎤 Recording for 5 seconds... SPEAK NOW!")
    sample_rate = 16000
    audio_data = sd.rec(
        int(duration * sample_rate), 
        samplerate=sample_rate, 
        channels=1,
        dtype=np.float32
    )
    sd.wait()
    print("✅ Recording complete!")
    return audio_data.flatten()

def detect_emotion(audio_data):
    """Detect emotion from audio"""
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

def send_to_gemma(audio_data, emotion, server_url):
    """Send to Gemma 3N with full pipeline"""
    print(f"🤖 Sending to Gemma 3N (emotion: {emotion})...")
    
    try:
        # Send to your Colab model
        response = requests.post(
            f"{server_url}/predict",
            json={
                "text": "",  # Pure audio
                "emotion": emotion,
                "audio_data": audio_data.tolist()
            },
            timeout=15
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Server error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    server_url = "https://7983b23bdd57.ngrok-free.app"
    
    print("""
╔════════════════════════════════════════════════════════════╗
║          TEKNOFEST 2025 - VOICE AI DEMO                   ║
║    🎤 Voice → 😊 Emotion → 🤖 Gemma 3N → 🔧 Tools         ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Test connection
    try:
        test = requests.get(f"{server_url}/health", timeout=3)
        if test.status_code == 200:
            print("✅ Connected to your trained Gemma 3N model!")
        else:
            print("❌ Cannot connect to model")
            return
    except:
        print("❌ Cannot reach server")
        return
    
    while True:
        try:
            # Wait for user
            input("\n🎤 Press ENTER to record and talk to AI (or Ctrl+C to quit): ")
            
            # Record audio
            audio_data = record_audio()
            
            # Detect emotion
            emotion = detect_emotion(audio_data)
            print(f"😊 Detected emotion: {emotion}")
            
            # Send to AI
            result = send_to_gemma(audio_data, emotion, server_url)
            
            if result:
                print("\n" + "="*60)
                print(f"🤖 AI Response: {result.get('generated_text', 'No response')}")
                print(f"🎭 Emotion: {result.get('emotion_detected', emotion)}")
                print(f"🔧 Tools Found: {result.get('tools_extracted', [])}")
                print(f"⚙️  Model: {result.get('model_type', 'unknown')}")
                print(f"📊 Status: {result.get('model_status', 'unknown')}")
                print("="*60)
            else:
                print("❌ Failed to get response")
                
        except KeyboardInterrupt:
            print("\n👋 Demo ended!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()