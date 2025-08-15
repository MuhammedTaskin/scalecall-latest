#!/usr/bin/env python3
"""
TEKNOFEST 2025 - TURKISH TTS ENGINE
Production-Ready Turkish Text-to-Speech using Piper
"""

import subprocess
import tempfile
import os
import json
import asyncio
import logging
import hashlib
import threading
import queue
import time
from typing import Dict, Optional, List, Callable
from pathlib import Path
import re

logger = logging.getLogger(__name__)

class TurkishTTSEngine:
    """High-performance Turkish TTS using Piper with professional Turkish model"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or "TURKISH_TTS_MODEL.onnx"
        self.config_path = f"{self.model_path}.json"
        self.audio_cache = {}
        self.temp_files = []
        self.processing_queue = queue.Queue()
        self.worker_thread = None
        self.is_running = False
        self.setup_engine()
        
    def setup_engine(self):
        """Initialize TTS engine"""
        try:
            # Check if piper is available
            result = subprocess.run(['which', 'piper'], capture_output=True, text=True)
            if result.returncode != 0:
                # Try direct piper command
                result = subprocess.run(['piper', '--help'], capture_output=True, text=True)
                if result.returncode != 0:
                    raise Exception("Piper not found. Install with: pip install piper-tts")
            
            # Check if model exists
            if not os.path.exists(self.model_path):
                logger.error(f"Model not found: {self.model_path}")
                logger.info("Place your TURKISH_TTS_MODEL.onnx model in the current directory")
                return False
                
            # Check config file
            if not os.path.exists(self.config_path):
                logger.warning(f"Config not found: {self.config_path}")
                logger.info("TTS will work without config but may have reduced quality")
            
            logger.info(f"✅ Turkish TTS ready with model: {self.model_path}")
            
            # Start background worker for async processing
            self.start_worker()
            return True
            
        except Exception as e:
            logger.error(f"TTS setup failed: {e}")
            return False
    
    def start_worker(self):
        """Start background worker thread for TTS processing"""
        if self.worker_thread and self.worker_thread.is_alive():
            return
            
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        logger.info("TTS worker thread started")
    
    def _worker_loop(self):
        """Background worker for processing TTS requests"""
        while self.is_running:
            try:
                # Get task from queue with timeout
                task = self.processing_queue.get(timeout=1.0)
                if task is None:  # Shutdown signal
                    break
                    
                text, emotion, callback, error_callback = task
                
                try:
                    audio_file = self._generate_speech_sync(text, emotion)
                    if callback:
                        callback(audio_file)
                except Exception as e:
                    if error_callback:
                        error_callback(e)
                finally:
                    self.processing_queue.task_done()
                    
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Worker error: {e}")
    
    def clean_turkish_text(self, text: str) -> str:
        """Clean and optimize text for Turkish TTS"""
        
        # Remove tool calls and special formatting
        text = re.sub(r'\[([^\]]+)\]', '', text)
        
        # Turkish-specific replacements for better pronunciation
        replacements = {
            # Currency and units
            'TL': 'Türk Lirası',
            '₺': 'Türk Lirası',
            'GB': 'gigabay',
            'MB': 'megabay',
            'KB': 'kilobay',
            
            # Tech terms
            'SMS': 'es em es',
            'eSIM': 'e sim',
            'SIM': 'sim',
            'WiFi': 'vay fay',
            'Wi-Fi': 'vay fay',
            'QR': 'kıy ar',
            'URL': 'yu ar el',
            'ID': 'ay di',
            'API': 'a pi ay',
            'HTTP': 'ha te te pi',
            'HTTPS': 'ha te te pi es',
            
            # Symbols
            '%': ' yüzde ',
            '&': ' ve ',
            '@': ' at işareti ',
            '#': ' hashtag ',
            '+': ' artı ',
            '=': ' eşittir ',
            '€': ' avro ',
            '$': ' dolar ',
            
            # Numbers with units (basic)
            ' 1 ': ' bir ',
            ' 2 ': ' iki ',
            ' 3 ': ' üç ',
            ' 4 ': ' dört ',
            ' 5 ': ' beş ',
            ' 10 ': ' on ',
            ' 15 ': ' on beş ',
            ' 20 ': ' yirmi ',
            ' 25 ': ' yirmi beş ',
            ' 30 ': ' otuz ',
            ' 50 ': ' elli ',
            ' 100 ': ' yüz ',
        }
        
        # Apply replacements
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove problematic characters
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\'\"]', ' ', text)
        
        # Ensure proper sentence ending
        text = text.strip()
        if text and text[-1] not in '.!?':
            text += '.'
        
        return text
    
    def _generate_speech_sync(self, text: str, emotion: str = "neutral") -> Optional[str]:
        """Synchronous speech generation"""
        
        if not os.path.exists(self.model_path):
            logger.error("Model not available")
            return None
        
        # Clean text
        clean_text = self.clean_turkish_text(text)
        if not clean_text or len(clean_text.strip()) < 2:
            return None
        
        # Check cache
        cache_key = hashlib.md5(f"{clean_text}_{emotion}".encode()).hexdigest()
        if cache_key in self.audio_cache:
            cache_file = self.audio_cache[cache_key]
            if os.path.exists(cache_file):
                return cache_file
        
        try:
            # Create output file
            output_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            output_path = output_file.name
            output_file.close()
            
            # Build command
            cmd = ["piper", "--model", self.model_path, "--output_file", output_path]
            
            # Add config if available
            if os.path.exists(self.config_path):
                cmd.extend(["--config", self.config_path])
            
            # Execute piper
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = process.communicate(input=clean_text.encode("utf-8"))
            
            if process.returncode == 0 and os.path.exists(output_path):
                # Cache the result
                self.audio_cache[cache_key] = output_path
                self.temp_files.append(output_path)
                
                # Log success
                file_size = os.path.getsize(output_path)
                logger.info(f"TTS: {len(clean_text)} chars -> {file_size} bytes")
                
                return output_path
            else:
                error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                logger.error(f"Piper failed: {error_msg}")
                
                # Cleanup failed file
                if os.path.exists(output_path):
                    os.unlink(output_path)
                return None
                
        except Exception as e:
            logger.error(f"TTS generation error: {e}")
            return None
    
    def generate_speech(self, text: str, emotion: str = "neutral") -> Optional[str]:
        """Synchronous TTS generation"""
        return self._generate_speech_sync(text, emotion)
    
    async def generate_speech_async(self, text: str, emotion: str = "neutral") -> Optional[str]:
        """Asynchronous TTS generation"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._generate_speech_sync, text, emotion)
    
    def generate_speech_background(self, 
                                 text: str, 
                                 emotion: str = "neutral",
                                 callback: Optional[Callable] = None,
                                 error_callback: Optional[Callable] = None):
        """Queue TTS generation for background processing"""
        if not self.is_running:
            self.start_worker()
        
        task = (text, emotion, callback, error_callback)
        self.processing_queue.put(task)
    
    def play_audio(self, audio_file: str) -> bool:
        """Play audio file on macOS"""
        if not audio_file or not os.path.exists(audio_file):
            return False
        
        try:
            # Use afplay on macOS
            result = subprocess.run(['afplay', audio_file], 
                                  capture_output=True, 
                                  timeout=30)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Audio playback failed: {e}")
            return False
    
    async def speak_text(self, text: str, emotion: str = "neutral", play: bool = True) -> Optional[str]:
        """Generate and optionally play speech"""
        audio_file = await self.generate_speech_async(text, emotion)
        
        if audio_file and play:
            # Play in background
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.play_audio, audio_file)
        
        return audio_file
    
    def get_cache_stats(self) -> Dict:
        """Get TTS cache statistics"""
        total_size = 0
        valid_files = 0
        
        for file_path in self.audio_cache.values():
            if os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
                valid_files += 1
        
        return {
            'cached_files': len(self.audio_cache),
            'valid_files': valid_files,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'temp_files': len(self.temp_files)
        }
    
    def cleanup_cache(self, max_files: int = 50):
        """Clean up old cache files"""
        if len(self.audio_cache) <= max_files:
            return
        
        # Sort by file modification time
        cache_items = list(self.audio_cache.items())
        cache_items.sort(key=lambda x: os.path.getmtime(x[1]) if os.path.exists(x[1]) else 0)
        
        # Remove oldest files
        files_to_remove = len(cache_items) - max_files
        for i in range(files_to_remove):
            cache_key, file_path = cache_items[i]
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
                if file_path in self.temp_files:
                    self.temp_files.remove(file_path)
                del self.audio_cache[cache_key]
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
    
    def shutdown(self):
        """Shutdown TTS engine and cleanup"""
        self.is_running = False
        
        # Signal worker to stop
        if self.worker_thread and self.worker_thread.is_alive():
            self.processing_queue.put(None)
            self.worker_thread.join(timeout=2.0)
        
        # Cleanup temp files
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
        
        self.temp_files.clear()
        self.audio_cache.clear()
        
        logger.info("TTS engine shutdown complete")

# Test and demo functions
async def test_turkish_tts():
    """Test Turkish TTS with various examples"""
    
    print("🗣️ Turkish TTS Test")
    
    # Initialize TTS
    tts = TurkishTTSEngine()
    
    if not os.path.exists(tts.model_path):
        print(f"❌ Model not found: {tts.model_path}")
        print("Please ensure TURKISH_TTS_MODEL.onnx is in the current directory")
        return
    
    # Test cases
    test_cases = [
        ("Merhaba, Türk Telekom müşteri hizmetlerine hoş geldiniz.", "happy"),
        ("Bakiyeniz 250 Türk Lirası, hesabınız aktif durumda.", "neutral"),
        ("Yaşadığınız sorun için çok özür dileriz, hemen çözüyoruz.", "sad"),
        ("eSIM aktivasyonunuz başarıyla tamamlandı!", "happy"),
        ("Teknik ekibimiz sorununuzu inceliyor, lütfen bekleyin.", "neutral")
    ]
    
    print(f"Using model: {tts.model_path}")
    
    for i, (text, emotion) in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {emotion}")
        print(f"Text: {text}")
        
        # Generate speech
        start_time = time.time()
        audio_file = await tts.speak_text(text, emotion, play=False)
        generation_time = time.time() - start_time
        
        if audio_file:
            file_size = os.path.getsize(audio_file)
            print(f"✅ Generated: {audio_file}")
            print(f"📊 Size: {file_size} bytes, Time: {generation_time:.2f}s")
            
            # Play audio
            print("🔊 Playing audio...")
            tts.play_audio(audio_file)
        else:
            print("❌ Generation failed")
        
        # Small delay between tests
        await asyncio.sleep(1)
    
    # Show cache stats
    stats = tts.get_cache_stats()
    print(f"\n📈 Cache Stats: {stats}")
    
    # Cleanup
    tts.shutdown()

def install_requirements():
    """Install required packages"""
    try:
        import subprocess
        
        print("📦 Installing requirements...")
        subprocess.run(['pip', 'install', 'piper-tts'], check=True)
        print("✅ Installed piper-tts")
        
        return True
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if "--install" in sys.argv:
        install_requirements()
    elif "--test" in sys.argv:
        asyncio.run(test_turkish_tts())
    else:
        print("Turkish TTS Engine - TEKNOFEST 2025")
        print("Usage:")
        print("  python TURKISH_TTS_ENGINE.py --install")
        print("  python TURKISH_TTS_ENGINE.py --test")
        print("\nMake sure TURKISH_TTS_MODEL.onnx is in the current directory")