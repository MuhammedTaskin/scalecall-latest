#!/usr/bin/env python3
"""
Test STT via WebSocket to isolate the issue.
This tests the full pipeline: WebSocket -> STT -> Response
"""
import asyncio
import websockets
import json
import base64
import wave
import numpy as np
import tempfile
import os

def create_speech_audio(text="Merhaba", duration=2.0):
    """Create a more realistic speech-like audio pattern."""
    sample_rate = 16000
    samples = int(duration * sample_rate)
    
    # Create speech-like pattern with multiple frequencies
    t = np.linspace(0, duration, samples)
    
    # Simulate formants (speech frequencies)
    f1 = 300 + 200 * np.sin(2 * np.pi * 2 * t)  # Varying fundamental
    f2 = 800 + 400 * np.sin(2 * np.pi * 1.5 * t)  # Second formant
    f3 = 2000 + 300 * np.sin(2 * np.pi * 0.8 * t)  # Third formant
    
    # Combine frequencies with envelope
    envelope = np.exp(-t * 0.5) * (1 - np.exp(-t * 10))  # Attack-decay envelope
    audio = (np.sin(2 * np.pi * f1 * t) * 0.4 + 
             np.sin(2 * np.pi * f2 * t) * 0.3 + 
             np.sin(2 * np.pi * f3 * t) * 0.2) * envelope
    
    # Add some noise for realism
    noise = np.random.normal(0, 0.05, samples)
    audio = audio + noise
    
    # Normalize
    audio = audio / np.max(np.abs(audio)) * 0.8
    
    # Convert to 16-bit PCM
    audio_int = (audio * 32767).astype(np.int16)
    
    # Create temporary WAV file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        with wave.open(tmp.name, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_int.tobytes())
        
        print(f"✅ Created speech-like audio: {tmp.name} ({duration}s)")
        return tmp.name, audio_int

def audio_to_base64_chunks(audio_data, chunk_size=1600):  # ~100ms chunks at 16kHz
    """Convert audio data to base64 chunks."""
    chunks = []
    
    # Convert numpy array to bytes
    audio_bytes = audio_data.tobytes()
    
    # Split into chunks
    for i in range(0, len(audio_bytes), chunk_size):
        chunk = audio_bytes[i:i + chunk_size]
        base64_chunk = base64.b64encode(chunk).decode('utf-8')
        chunks.append(base64_chunk)
    
    print(f"✅ Created {len(chunks)} audio chunks")
    return chunks

async def test_websocket_stt():
    """Test STT via WebSocket connection."""
    print("\n🔌 TESTING STT VIA WEBSOCKET")
    print("============================")
    
    uri = "ws://localhost:8000/ws/test_client_stt"
    
    try:
        print("1️⃣ Connecting to WebSocket...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")
            
            print("2️⃣ Creating speech-like audio...")
            audio_file, audio_data = create_speech_audio("Merhaba eSIM", duration=3.0)
            
            print("3️⃣ Converting to chunks...")
            chunks = audio_to_base64_chunks(audio_data)
            
            print("4️⃣ Sending audio start message...")
            start_msg = {"type": "user_audio_start"}
            await websocket.send(json.dumps(start_msg))
            
            print("5️⃣ Sending audio chunks...")
            for i, chunk in enumerate(chunks):
                chunk_msg = {"type": "user_audio_chunk", "pcm": chunk}
                await websocket.send(json.dumps(chunk_msg))
                
                # Small delay between chunks (simulate real-time)
                await asyncio.sleep(0.1)
                
                if i % 10 == 0:
                    print(f"   Sent chunk {i+1}/{len(chunks)}")
            
            print("6️⃣ Sending audio end message...")
            end_msg = {"type": "user_audio_end"}
            await websocket.send(json.dumps(end_msg))
            
            print("7️⃣ Waiting for transcription response...")
            
            # Listen for responses
            timeout_count = 0
            max_timeout = 10  # 10 seconds
            
            while timeout_count < max_timeout:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    msg = json.loads(response)
                    
                    print(f"📨 Received: {msg['type']}")
                    
                    if msg['type'] == 'stt_transcript':
                        transcript = msg['text']
                        print(f"✅ TRANSCRIPTION: '{transcript}'")
                        
                        # Cleanup
                        os.unlink(audio_file)
                        return True
                        
                    elif msg['type'] == 'error':
                        print(f"❌ ERROR: {msg['message']}")
                        os.unlink(audio_file)
                        return False
                        
                    elif msg['type'] == 'model_delta':
                        print(f"🤖 AI Response: {msg['text']}")
                        
                except asyncio.TimeoutError:
                    timeout_count += 1
                    print(f"⏳ Waiting... ({timeout_count}/{max_timeout})")
                    continue
            
            print("❌ TIMEOUT: No transcription received")
            os.unlink(audio_file)
            return False
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_backend_direct():
    """Test backend STT service directly (bypass WebSocket)."""
    print("\n🔬 TESTING BACKEND STT DIRECTLY")
    print("==============================")
    
    import sys
    sys.path.insert(0, 'backend')
    
    try:
        from backend.stt_service import STTService
        
        print("1️⃣ Initializing STT service...")
        stt = STTService()
        await stt.initialize()
        
        print("2️⃣ Creating realistic speech audio...")
        audio_file, audio_data = create_speech_audio("Merhaba eSIM almak istiyorum", duration=4.0)
        
        print("3️⃣ Converting to base64 chunks...")
        chunks = audio_to_base64_chunks(audio_data)
        
        print("4️⃣ Running transcription...")
        transcript = await stt.transcribe_audio(chunks)
        
        print(f"✅ DIRECT TRANSCRIPTION: '{transcript}'")
        
        # Cleanup
        os.unlink(audio_file)
        
        return bool(transcript)
        
    except Exception as e:
        print(f"❌ Direct backend test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all STT tests."""
    print("🎤 COMPREHENSIVE STT TESTING")
    print("============================")
    print("Testing STT without any frontend interference")
    print("")
    
    # Test 1: Direct backend
    print("TEST 1: Direct Backend STT")
    success1 = await test_backend_direct()
    
    # Test 2: WebSocket pipeline  
    print("\nTEST 2: WebSocket STT Pipeline")
    success2 = await test_websocket_stt()
    
    print("\n📊 FINAL RESULTS")
    print("================")
    print(f"Direct Backend:   {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"WebSocket Pipeline: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print("\n🎉 STT IS FULLY WORKING!")
        print("The issue must be in the frontend audio capture/sending")
    elif success1 and not success2:
        print("\n⚠️ STT BACKEND WORKS, WEBSOCKET ISSUE")
        print("Problem is in the WebSocket message handling")
    elif not success1:
        print("\n❌ STT BACKEND HAS ISSUES")
        print("Need to fix the core STT service")
    
    return success1 and success2

if __name__ == "__main__":
    asyncio.run(main())
