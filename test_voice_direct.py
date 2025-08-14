#!/usr/bin/env python3
"""
DIRECT VOICE INPUT TEST - No menus, just speak!
Press ENTER to start recording, speak, press ENTER again to stop and test STT
"""
import asyncio
import pyaudio
import base64
import sys
import threading
import time

# Add backend to path
sys.path.insert(0, 'backend')

from backend.stt_service import STTService

class DirectVoiceRecorder:
    def __init__(self, sample_rate=16000, chunk_size=1024):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.frames = []
        self.is_recording = False
        self.stream = None
        self.p = None
        
    def start_recording(self):
        """Start recording audio."""
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        self.frames = []
        self.is_recording = True
        
        print("🔴 RECORDING... (Press ENTER to stop)")
        
        # Start recording in background thread
        self.record_thread = threading.Thread(target=self._record_loop)
        self.record_thread.start()
    
    def _record_loop(self):
        """Background recording loop."""
        while self.is_recording:
            try:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                self.frames.append(data)
            except Exception as e:
                print(f"Recording error: {e}")
                break
    
    def stop_recording(self):
        """Stop recording and return audio data."""
        self.is_recording = False
        
        if self.record_thread:
            self.record_thread.join()
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.p:
            self.p.terminate()
        
        print("⏹️ Recording stopped!")
        
        return b''.join(self.frames) if self.frames else b''

def audio_to_base64_chunks(audio_data, chunk_size=1600):
    """Convert audio data to base64 chunks."""
    chunks = []
    for i in range(0, len(audio_data), chunk_size):
        chunk = audio_data[i:i + chunk_size]
        base64_chunk = base64.b64encode(chunk).decode('utf-8')
        chunks.append(base64_chunk)
    return chunks

async def main():
    """Direct voice testing - no menus!"""
    print("🎤 DIRECT VOICE INPUT TEST")
    print("=========================")
    print("This will record your voice and test STT immediately")
    print("")
    
    # Initialize STT once
    print("🧠 Initializing Whisper STT...")
    stt = STTService()
    await stt.initialize()
    print("✅ STT ready!")
    print("")
    
    recorder = DirectVoiceRecorder()
    
    print("Ready for voice input!")
    print("💡 Instructions:")
    print("   1. Press ENTER to start recording")
    print("   2. Speak clearly")
    print("   3. Press ENTER again to stop and transcribe")
    print("   4. Type 'quit' to exit")
    print("")
    
    while True:
        # Wait for user to press ENTER
        user_input = input("Press ENTER to start recording (or 'quit' to exit): ").strip().lower()
        
        if user_input == 'quit':
            print("👋 Goodbye!")
            break
            
        # Start recording
        recorder.start_recording()
        
        # Wait for user to press ENTER again
        input()  # This blocks until ENTER is pressed
        
        # Stop recording
        audio_data = recorder.stop_recording()
        
        if len(audio_data) < 1000:  # Too short
            print("❌ Recording too short, try again")
            continue
        
        print("🔄 Processing audio...")
        
        # Convert to chunks
        chunks = audio_to_base64_chunks(audio_data)
        print(f"📦 Created {len(chunks)} audio chunks")
        
        # Transcribe
        try:
            transcript = await stt.transcribe_audio(chunks)
            
            print(f"\n📝 TRANSCRIPTION:")
            print(f"➤ '{transcript}'")
            
            if not transcript:
                print("❌ No speech detected - try speaking louder/clearer")
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
        
        print("-" * 50)
        print()

if __name__ == "__main__":
    asyncio.run(main())
