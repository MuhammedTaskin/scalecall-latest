#!/usr/bin/env python3
"""
REAL AUDIO INPUT TEST for backend STT
Record from your microphone and test Whisper directly
"""
import asyncio
import pyaudio
import wave
import base64
import sys
import os
import threading
import time

# Add backend to path
sys.path.insert(0, 'backend')

from backend.stt_service import STTService

class AudioRecorder:
    def __init__(self, duration=5, sample_rate=16000, chunk_size=1024):
        self.duration = duration
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.frames = []
        self.is_recording = False
        
    def record_audio(self):
        """Record audio from microphone."""
        print(f"🎤 Recording for {self.duration} seconds...")
        print("📢 SPEAK NOW!")
        
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        
        # Open stream
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        self.frames = []
        self.is_recording = True
        
        # Record for specified duration
        for i in range(int(self.sample_rate / self.chunk_size * self.duration)):
            if not self.is_recording:
                break
                
            data = stream.read(self.chunk_size)
            self.frames.append(data)
            
            # Progress indicator
            if i % 10 == 0:
                progress = (i * self.chunk_size) / (self.sample_rate * self.duration) * 100
                print(f"Recording... {progress:.0f}%")
        
        print("✅ Recording finished!")
        
        # Stop and close stream
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        return b''.join(self.frames)
    
    def save_wav(self, audio_data, filename):
        """Save audio data as WAV file."""
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data)
        
        print(f"💾 Saved audio to: {filename}")
        return filename

def audio_to_base64_chunks(audio_data, chunk_size=1600):
    """Convert raw audio to base64 chunks like frontend does."""
    chunks = []
    
    for i in range(0, len(audio_data), chunk_size):
        chunk = audio_data[i:i + chunk_size]
        base64_chunk = base64.b64encode(chunk).decode('utf-8')
        chunks.append(base64_chunk)
    
    return chunks

async def test_recorded_audio():
    """Test with real recorded audio."""
    print("\n🎙️ REAL MICROPHONE TEST")
    print("=======================")
    
    try:
        # Check if pyaudio is available
        import pyaudio
    except ImportError:
        print("❌ PyAudio not installed!")
        print("Install with: pip install pyaudio")
        return False
    
    # Get recording duration from user
    duration = input("🕐 Recording duration (seconds, default 5): ").strip()
    duration = float(duration) if duration else 5.0
    
    # Record audio
    recorder = AudioRecorder(duration=duration)
    audio_data = recorder.record_audio()
    
    # Save for inspection
    wav_file = recorder.save_wav(audio_data, "test_recording.wav")
    
    # Convert to chunks
    print("🔄 Converting to base64 chunks...")
    chunks = audio_to_base64_chunks(audio_data)
    print(f"✅ Created {len(chunks)} chunks")
    
    # Test STT
    print("🧠 Testing Whisper STT...")
    stt = STTService()
    await stt.initialize()
    
    transcript = await stt.transcribe_audio(chunks)
    
    print(f"\n📝 TRANSCRIPTION RESULT:")
    print(f"'{transcript}'")
    
    if transcript:
        print("✅ SUCCESS: STT backend works with real audio!")
        return True
    else:
        print("❌ FAILED: No transcription produced")
        return False

async def test_file_audio():
    """Test with an existing audio file."""
    print("\n📁 AUDIO FILE TEST")
    print("==================")
    
    # Look for audio files
    audio_files = []
    for ext in ['.wav', '.mp3', '.m4a', '.flac']:
        audio_files.extend([f for f in os.listdir('.') if f.lower().endswith(ext)])
    
    if not audio_files:
        print("ℹ️ No audio files found in current directory")
        return True
    
    print(f"📂 Found audio files: {audio_files}")
    
    # Let user choose
    filename = input("Enter filename to test (or press Enter to skip): ").strip()
    
    if not filename or filename not in audio_files:
        print("⏭️ Skipping file test")
        return True
    
    print(f"🎵 Testing with: {filename}")
    
    
    # For WAV files, we can test directly
    if filename.lower().endswith('.wav'):
        try:
            with wave.open(filename, 'rb') as wf:
                # Check format
                print(f"📊 Format: {wf.getnchannels()} channels, {wf.getframerate()}Hz, {wf.getsampwidth()*8}bit")
                
                # Read audio data
                audio_data = wf.readframes(wf.getnframes())
                
                # Convert to chunks
                chunks = audio_to_base64_chunks(audio_data)
                print(f"✅ Created {len(chunks)} chunks from file")
                
                # Test STT
                stt = STTService()
                await stt.initialize()
                
                transcript = await stt.transcribe_audio(chunks)
                
                print(f"\n📝 FILE TRANSCRIPTION:")
                print(f"'{transcript}'")
                
                return bool(transcript)
                
        except Exception as e:
            print(f"❌ Error processing file: {e}")
            return False
    else:
        print("ℹ️ Non-WAV files need conversion (skipping for now)")
        return True

async def interactive_test():
    """Interactive testing session."""
    print("\n🎮 INTERACTIVE STT TEST")
    print("=======================")
    
    stt = STTService()
    await stt.initialize()
    
    try:
        import pyaudio
    except ImportError:
        print("❌ PyAudio required for interactive test")
        return False
    
    while True:
        print("\nOptions:")
        print("1. Record and test (5 seconds)")
        print("2. Record and test (custom duration)")
        print("3. Quit")
        
        choice = input("Choose (1-3): ").strip()
        
        if choice == '3':
            break
        elif choice in ['1', '2']:
            duration = 5.0 if choice == '1' else float(input("Duration (seconds): "))
            
            recorder = AudioRecorder(duration=duration)
            audio_data = recorder.record_audio()
            
            chunks = audio_to_base64_chunks(audio_data)
            transcript = await stt.transcribe_audio(chunks)
            
            print(f"\n📝 RESULT: '{transcript}'")
            
            # Save this recording
            filename = f"recording_{int(time.time())}.wav"
            recorder.save_wav(audio_data, filename)
            print(f"💾 Saved as: {filename}")
        else:
            print("Invalid choice!")
    
    return True

async def main():
    """Main test menu."""
    print("🎤 REAL AUDIO STT BACKEND TEST")
    print("==============================")
    print("This tests the backend STT with YOUR actual voice")
    print("")
    
    # Check dependencies
    try:
        import pyaudio
        print("✅ PyAudio available")
    except ImportError:
        print("❌ PyAudio not found")
        print("Install with: pip install pyaudio")
        print("On macOS: brew install portaudio && pip install pyaudio")
        return
    
    while True:
        print("\n🎯 TEST OPTIONS:")
        print("1. Record from microphone and test STT")
        print("2. Test with existing audio file")
        print("3. Interactive testing session")
        print("4. Exit")
        
        choice = input("\nChoose test (1-4): ").strip()
        
        if choice == '1':
            await test_recorded_audio()
        elif choice == '2':
            await test_file_audio()
        elif choice == '3':
            await interactive_test()
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice!")

if __name__ == "__main__":
    asyncio.run(main())
