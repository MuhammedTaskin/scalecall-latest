#!/usr/bin/env python3
"""
SIMPLE E-SIM AGENT TEST
Quick test for Turkish conversation with e-SIM agent
"""
import asyncio
import pyaudio
import base64
import sys
import threading

# Add backend to path
sys.path.insert(0, 'backend')

from backend.stt_service import STTService
from backend.esim_tool_agent import ESIMToolAgent

class SimpleESIMTest:
    def __init__(self):
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.frames = []
        self.is_recording = False
        self.stream = None
        self.p = None
        
        # Initialize services
        self.stt = None
        self.agent = None
        
    async def initialize(self):
        """Initialize services."""
        print("🤖 Starting e-SIM Agent...")
        
        # Initialize STT
        self.stt = STTService()
        await self.stt.initialize()
        print("✅ Speech Recognition ready")
        
        # Initialize agent
        self.agent = ESIMToolAgent()
        print("✅ e-SIM Agent ready")
        
    def start_recording(self):
        """Start recording."""
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
        
        print("🔴 Recording...")
        self.record_thread = threading.Thread(target=self._record_loop)
        self.record_thread.start()
    
    def _record_loop(self):
        """Record audio."""
        while self.is_recording:
            try:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                self.frames.append(data)
            except Exception:
                break
    
    def stop_recording(self):
        """Stop recording."""
        self.is_recording = False
        
        if hasattr(self, 'record_thread'):
            self.record_thread.join()
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.p:
            self.p.terminate()
        
        print("⏹️ Stopped")
        return b''.join(self.frames)

    def audio_to_base64_chunks(self, audio_data):
        """Convert audio to chunks."""
        chunks = []
        chunk_size = 1600
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i + chunk_size]
            base64_chunk = base64.b64encode(chunk).decode('utf-8')
            chunks.append(base64_chunk)
        return chunks

    async def get_voice_input(self):
        """Get voice input."""
        print("\nPress ENTER to speak...")
        input()
        
        self.start_recording()
        input("Press ENTER to stop...")
        
        audio_data = self.stop_recording()
        
        if len(audio_data) < 1000:
            print("❌ Too short")
            return None
        
        print("🔄 Converting speech...")
        chunks = self.audio_to_base64_chunks(audio_data)
        transcript = await self.stt.transcribe_audio(chunks)
        
        if transcript:
            print(f"📝 You said: '{transcript}'")
            return transcript
        else:
            print("❌ Couldn't understand")
            return None

    def respond_in_turkish(self, text):
        """Generate Turkish response."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["merhaba", "selam", "nasılsın"]):
            return "Merhaba! Ben e-SIM call center otomatik asistanıyım. Size nasıl yardımcı olabilirim?"
        
        elif any(word in text_lower for word in ["kimsin", "adın", "ne yapıyorsun"]):
            return "Ben e-SIM call center otomatik sistemiyim. e-SIM işlemlerinizde size yardımcı oluyorum."
        
        elif any(word in text_lower for word in ["yardım", "nasıl", "ne yapabilirim"]):
            return "Size şu konularda yardımcı olabilirim: Bakiye kontrol, e-SIM durumu, aktifleştirme, kapatma, bakiye yükleme. Müşteri numaranızı söylerseniz işlem yapabilirim."
        
        elif any(word in text_lower for word in ["müşteri", "123456"]):
            return "Müşteri 123456 - Ahmet Yılmaz bulundu. Ne yapmak istiyorsunuz?"
        
        elif any(word in text_lower for word in ["bakiye", "para"]):
            return "Bakiyeniz: 150.75 TL"
        
        elif any(word in text_lower for word in ["esim", "durum", "kontrol"]):
            return "2 adet e-SIM'iniz var. 1 tanesi aktif, 1 tanesi askıda."
        
        else:
            return "Anlayamadım. Lütfen açıklayıcı bir şekilde söyleyiniz. Örneğin: 'Müşteri 123456 bakiye kontrol et'"

    async def chat_loop(self):
        """Main chat loop."""
        print("\n" + "="*50)
        print("🎙️ TÜRKÇE E-SIM ASISTAN")
        print("="*50)
        print("Türkçe konuşun, size Türkçe yanıt vereceğim!")
        print("Örnek komutlar:")
        print("• 'Merhaba'")
        print("• 'Sen kimsin?'")
        print("• 'Müşteri 123456 bakiye kontrol et'")
        print("• 'e-SIM durumu'")
        print("="*50)
        
        while True:
            choice = input("\nPress ENTER to speak, or type 'quit': ").strip().lower()
            
            if choice == 'quit':
                print("👋 Görüşürüz!")
                break
            
            # Get voice input
            text = await self.get_voice_input()
            
            if text:
                # Generate Turkish response
                response = self.respond_in_turkish(text)
                print(f"\n🤖 ASISTAN:")
                print(f"💬 {response}")
            
            print("-" * 50)

async def main():
    """Main function."""
    print("🎙️ TÜRKÇE E-SIM ASISTAN TESTI")
    print("Ses ile Türkçe konuşma testi")
    print("")
    
    # Initialize
    chat = SimpleESIMTest()
    await chat.initialize()
    
    # Start chat
    await chat.chat_loop()

if __name__ == "__main__":
    asyncio.run(main())
