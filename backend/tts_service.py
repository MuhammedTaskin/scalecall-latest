"""
Text-to-Speech service using XTTS-v2 for sentence-level chunking.
"""
import asyncio
import logging
import os
import re
import uuid
from pathlib import Path
from typing import AsyncIterator, Dict, Set
import tempfile

try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class TTSService:
    """Text-to-Speech service with XTTS-v2 and sentence chunking."""
    
    def __init__(self):
        self.tts = None
        self._initialized = False
        self.audio_cache_dir = Path("audio_cache")
        self.audio_cache_dir.mkdir(exist_ok=True)
        self.active_sessions: Dict[str, bool] = {}  # Track active playback sessions
        
    async def initialize(self):
        """Initialize XTTS-v2 model."""
        if self._initialized:
            return
            
        if not TTS_AVAILABLE:
            logger.warning("XTTS not available, using mock TTS")
            self._initialized = True
            return
            
        try:
            logger.info("Loading XTTS-v2 model...")
            loop = asyncio.get_event_loop()
            
            # Initialize TTS model
            self.tts = await loop.run_in_executor(
                None,
                lambda: TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
            )
            
            self._initialized = True
            logger.info("XTTS-v2 model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load XTTS model: {e}")
            self._initialized = True  # Continue with mock
    
    async def generate_speech(self, text: str, session_id: str, language: str = "tr") -> AsyncIterator[str]:
        """
        Generate speech for text in sentence/phrase chunks.
        
        Args:
            text: Text to synthesize
            session_id: Client session ID for playback control
            language: Language code (default: Turkish)
            
        Yields:
            Audio file URLs for each sentence chunk
        """
        await self.initialize()
        
        if not text.strip():
            return
        
        # Mark session as active
        self.active_sessions[session_id] = True
        
        try:
            # Split text into sentences/phrases
            chunks = self._split_into_chunks(text)
            
            for i, chunk in enumerate(chunks):
                # Check if session was interrupted
                if not self.active_sessions.get(session_id, False):
                    logger.info(f"TTS interrupted for session {session_id}")
                    break
                
                if chunk.strip():
                    audio_url = await self._synthesize_chunk(chunk, session_id, i)
                    if audio_url:
                        yield audio_url
                        
        except Exception as e:
            logger.error(f"TTS generation error: {e}")
        finally:
            # Clean up session
            self.active_sessions.pop(session_id, None)
    
    def _split_into_chunks(self, text: str) -> list[str]:
        """Split text into speakable chunks (sentences/phrases)."""
        # Clean text
        text = text.strip()
        
        # Split by sentence endings, questions, and pauses
        sentences = re.split(r'[.!?]+\s+', text)
        
        chunks = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # If sentence is too long, split by commas or conjunctions
            if len(sentence) > 100:
                sub_chunks = re.split(r'[,;]\s+|(?:\s+(?:ve|ama|fakat|ancak|çünkü|için)\s+)', sentence)
                for sub_chunk in sub_chunks:
                    sub_chunk = sub_chunk.strip()
                    if sub_chunk:
                        chunks.append(sub_chunk)
            else:
                chunks.append(sentence)
        
        return chunks
    
    async def _synthesize_chunk(self, text: str, session_id: str, chunk_idx: int) -> str:
        """Synthesize a single text chunk."""
        try:
            # Generate unique filename
            chunk_id = f"{session_id}_{chunk_idx}_{uuid.uuid4().hex[:8]}"
            audio_file = self.audio_cache_dir / f"{chunk_id}.wav"
            
            if TTS_AVAILABLE and self.tts:
                # Real TTS synthesis
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    lambda: self.tts.tts_to_file(
                        text=text,
                        language="tr",
                        file_path=str(audio_file)
                    )
                )
            else:
                # Mock TTS - create empty audio file for development
                await self._create_mock_audio(str(audio_file), text)
            
            # Return relative URL for serving
            return f"/audio/{audio_file.name}"
            
        except Exception as e:
            logger.error(f"Error synthesizing chunk '{text}': {e}")
            return None
    
    async def _create_mock_audio(self, file_path: str, text: str):
        """Create mock audio file for development."""
        # Simulate synthesis time based on text length
        synthesis_time = min(len(text) * 0.05, 2.0)  # Max 2 seconds
        await asyncio.sleep(synthesis_time)
        
        # Create empty WAV file (or simple tone for testing)
        import wave
        import numpy as np
        
        duration = len(text) * 0.1  # ~100ms per character
        sample_rate = 22050
        samples = int(duration * sample_rate)
        
        # Generate simple tone (optional - can be silence)
        t = np.linspace(0, duration, samples)
        frequency = 440  # A note
        audio = np.sin(2 * np.pi * frequency * t) * 0.1  # Low volume
        
        # Convert to 16-bit PCM
        audio_int = (audio * 32767).astype(np.int16)
        
        with wave.open(file_path, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_int.tobytes())
    
    async def stop_playback(self, session_id: str):
        """Stop TTS playback for a session."""
        self.active_sessions[session_id] = False
        logger.info(f"TTS playback stopped for session {session_id}")
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Clean up old audio cache files."""
        try:
            import time
            current_time = time.time()
            
            for file_path in self.audio_cache_dir.glob("*.wav"):
                file_age = current_time - file_path.stat().st_mtime
                if file_age > (max_age_hours * 3600):
                    file_path.unlink()
                    logger.debug(f"Cleaned up old audio file: {file_path.name}")
                    
        except Exception as e:
            logger.error(f"Error cleaning up audio files: {e}")
