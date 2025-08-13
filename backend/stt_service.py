"""
Speech-to-Text service using Whisper for PTT (Press-to-Talk) mode.
"""
import asyncio
import logging
import base64
import tempfile
import os
from typing import List
from pathlib import Path

try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

logger = logging.getLogger(__name__)


class STTService:
    """Speech-to-Text service with Whisper support."""
    
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self.model = None
        self._initialized = False
        
    async def initialize(self):
        """Initialize the Whisper model."""
        if self._initialized:
            return
            
        if not WHISPER_AVAILABLE:
            logger.warning("Faster-whisper not available, using mock transcription")
            self._initialized = True
            return
            
        try:
            logger.info(f"Loading Whisper model: {self.model_size}")
            # Load model in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                None, 
                lambda: WhisperModel(self.model_size, device="cpu", compute_type="int8")
            )
            self._initialized = True
            logger.info("Whisper model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            self._initialized = True  # Continue with mock
    
    async def transcribe_audio(self, audio_chunks: List[str]) -> str:
        """
        Transcribe audio chunks from base64 PCM data.
        
        Args:
            audio_chunks: List of base64-encoded PCM audio chunks
            
        Returns:
            Transcribed text or empty string if failed
        """
        await self.initialize()
        
        if not audio_chunks:
            return ""
        
        try:
            # Combine audio chunks
            audio_data = b""
            for chunk in audio_chunks:
                audio_data += base64.b64decode(chunk)
            
            if len(audio_data) < 1000:  # Too short
                return ""
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
                
                # Convert PCM to WAV format (simplified)
                # In production, you'd use proper audio libraries
                self._write_wav_file(temp_path, audio_data)
                
                # Transcribe
                if WHISPER_AVAILABLE and self.model:
                    transcript = await self._transcribe_file(temp_path)
                else:
                    # Mock transcription for development
                    transcript = await self._mock_transcribe(audio_data)
                
                # Clean up
                os.unlink(temp_path)
                
                return transcript.strip()
                
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
    
    def _write_wav_file(self, path: str, pcm_data: bytes):
        """Write PCM data as WAV file (simplified)."""
        import wave
        import struct
        
        # Basic WAV parameters
        sample_rate = 16000
        channels = 1
        sample_width = 2  # 16-bit
        
        with wave.open(path, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_data)
    
    async def _transcribe_file(self, file_path: str) -> str:
        """Transcribe audio file using Whisper."""
        try:
            loop = asyncio.get_event_loop()
            
            def transcribe():
                segments, info = self.model.transcribe(
                    file_path, 
                    language="tr",  # Turkish
                    beam_size=5,
                    best_of=5,
                    temperature=0.0
                )
                
                # Combine segments
                text = ""
                for segment in segments:
                    text += segment.text + " "
                
                return text.strip()
            
            result = await loop.run_in_executor(None, transcribe)
            return result
            
        except Exception as e:
            logger.error(f"Whisper transcription error: {e}")
            return ""
    
    async def _mock_transcribe(self, audio_data: bytes) -> str:
        """Mock transcription for development."""
        # Simulate processing time
        await asyncio.sleep(0.5)
        
        # Return common Turkish phrases based on audio length
        length = len(audio_data)
        
        if length < 5000:
            return "Merhaba"
        elif length < 10000:
            return "eSIM almak istiyorum"
        elif length < 20000:
            return "Cihazımı kontrol edebilir misiniz"
        else:
            return "Aktivasyon kodumu yeniden gönderebilir misiniz"
