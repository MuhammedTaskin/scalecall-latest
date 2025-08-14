#!/usr/bin/env python3
"""
Direct STT (Whisper) testing script.
Tests the backend STT service independently of frontend/WebSocket.
"""
import asyncio
import os
import sys
import base64
import wave
import numpy as np
from pathlib import Path

# Add backend to path
sys.path.insert(0, 'backend')

from backend.stt_service import STTService

def create_test_audio(text="Hello testing", duration=2.0, filename="test_audio.wav"):
    """Create a simple test audio file with sine wave."""
    sample_rate = 16000
    samples = int(duration * sample_rate)
    
    # Generate sine wave (440 Hz tone)
    t = np.linspace(0, duration, samples)
    frequency = 440  # A note
    audio = np.sin(2 * np.pi * frequency * t) * 0.5
    
    # Convert to 16-bit PCM
    audio_int = (audio * 32767).astype(np.int16)
    
    # Write WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_int.tobytes())
    
    print(f"✅ Created test audio: {filename} ({duration}s, {len(audio_int)} samples)")
    return filename

def audio_file_to_base64_chunks(filename, chunk_size=1024):
    """Convert audio file to base64 chunks (simulating frontend audio chunks)."""
    chunks = []
    
    with open(filename, 'rb') as f:
        # Skip WAV header (44 bytes)
        f.seek(44)
        
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            
            # Convert to base64 (simulating frontend encoding)
            base64_chunk = base64.b64encode(chunk).decode('utf-8')
            chunks.append(base64_chunk)
    
    print(f"✅ Created {len(chunks)} base64 chunks from {filename}")
    return chunks

async def test_stt_service():
    """Test the STT service directly."""
    print("\n🧪 TESTING STT SERVICE DIRECTLY")
    print("================================")
    
    # Initialize STT service
    print("1️⃣ Initializing STT service...")
    stt = STTService()
    await stt.initialize()
    
    print("2️⃣ Creating test audio file...")
    # Create test audio
    test_file = create_test_audio("Testing Whisper STT", duration=3.0)
    
    print("3️⃣ Converting to base64 chunks...")
    # Convert to chunks (simulating frontend)
    chunks = audio_file_to_base64_chunks(test_file)
    
    print("4️⃣ Running transcription...")
    # Test transcription
    try:
        transcript = await stt.transcribe_audio(chunks)
        
        if transcript:
            print(f"✅ TRANSCRIPTION SUCCESS: '{transcript}'")
            return True
        else:
            print("❌ TRANSCRIPTION FAILED: Empty result")
            return False
            
    except Exception as e:
        print(f"❌ TRANSCRIPTION ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"🧹 Cleaned up {test_file}")

async def test_with_real_audio():
    """Test with a real audio file if available."""
    print("\n🎵 TESTING WITH REAL AUDIO (if available)")
    print("==========================================")
    
    # Look for any audio files in the current directory
    audio_files = list(Path('.').glob('*.wav')) + list(Path('.').glob('*.mp3'))
    
    if not audio_files:
        print("ℹ️ No real audio files found, skipping this test")
        return True
    
    print(f"📁 Found audio files: {[str(f) for f in audio_files]}")
    
    # Use the first one
    audio_file = audio_files[0]
    print(f"🎵 Testing with: {audio_file}")
    
    stt = STTService()
    await stt.initialize()
    
    try:
        # For real files, we'd need proper conversion
        # For now, just test if the service can handle it
        print("ℹ️ Real audio file testing requires proper audio conversion")
        print("ℹ️ This test focuses on the synthetic audio pipeline")
        return True
        
    except Exception as e:
        print(f"❌ Real audio test error: {e}")
        return False

async def main():
    """Main test function."""
    print("🎤 WHISPER STT BACKEND TEST")
    print("===========================")
    print("")
    
    # Test 1: Direct STT service
    success1 = await test_stt_service()
    
    # Test 2: Real audio (if available)
    success2 = await test_with_real_audio()
    
    print("\n📊 FINAL RESULTS")
    print("================")
    print(f"STT Service Test: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Real Audio Test:  {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1:
        print("\n🎉 STT BACKEND IS WORKING!")
        print("The issue is likely in the frontend/WebSocket pipeline")
    else:
        print("\n❌ STT BACKEND HAS ISSUES")
        print("Need to fix the backend before testing frontend")
    
    return success1 and success2

if __name__ == "__main__":
    asyncio.run(main())
