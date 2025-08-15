#!/usr/bin/env python3
"""
TEKNOFEST 2025 - PIPER TTS INTEGRATION
High-Quality Turkish Text-to-Speech with Piper
"""

import subprocess
import tempfile
import os
import json
import asyncio
import logging
from typing import Dict, Optional, List
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

class PiperTTS:
    """Professional Turkish TTS using Piper"""
    
    def __init__(self):
        self.piper_executable = None
        self.models_dir = "./piper_models"
        self.voice_models = {}
        self.audio_cache = {}
        self.setup_piper()
        
    def setup_piper(self):
        """Setup Piper TTS system"""
        try:
            # Create models directory
            os.makedirs(self.models_dir, exist_ok=True)
            
            # Check if piper is installed
            result = subprocess.run(['which', 'piper'], capture_output=True, text=True)
            if result.returncode == 0:
                self.piper_executable = result.stdout.strip()
                logger.info(f"Found Piper at: {self.piper_executable}")
            else:
                logger.warning("Piper not found. Install with: pip install piper-tts")
                return
                
            # Download Turkish voice models
            self.download_turkish_models()
            
        except Exception as e:
            logger.error(f"Failed to setup Piper: {e}")
    
    def download_turkish_models(self):
        """Download high-quality Turkish voice models"""
        
        # Best Turkish voices for Piper
        turkish_models = {
            "female_natural": {
                "url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/tr/tr_TR/fgl/medium/tr_TR-fgl-medium.onnx",
                "config_url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/tr/tr_TR/fgl/medium/tr_TR-fgl-medium.onnx.json",
                "name": "Turkish Female (Fgül) - Natural",
                "quality": "high"
            },
            "male_professional": {
                "url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/tr/tr_TR/dfki/medium/tr_TR-dfki-medium.onnx", 
                "config_url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/tr/tr_TR/dfki/medium/tr_TR-dfki-medium.onnx.json",
                "name": "Turkish Male (DFKI) - Professional",
                "quality": "high"
            },
            "female_customer_service": {
                "url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/tr/tr_TR/fgl/low/tr_TR-fgl-low.onnx",
                "config_url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/tr/tr_TR/fgl/low/tr_TR-fgl-low.onnx.json", 
                "name": "Turkish Female - Customer Service",
                "quality": "medium"
            }
        }
        
        for voice_id, model_info in turkish_models.items():
            model_path = os.path.join(self.models_dir, f"{voice_id}.onnx")
            config_path = os.path.join(self.models_dir, f"{voice_id}.onnx.json")
            
            # Download model if not exists
            if not os.path.exists(model_path):
                logger.info(f"Downloading {model_info['name']}...")
                try:
                    # Download model
                    subprocess.run([
                        'wget', '-q', '-O', model_path, model_info['url']
                    ], check=True)
                    
                    # Download config
                    subprocess.run([
                        'wget', '-q', '-O', config_path, model_info['config_url']
                    ], check=True)
                    
                    self.voice_models[voice_id] = {
                        'model_path': model_path,
                        'config_path': config_path,
                        'name': model_info['name'],
                        'quality': model_info['quality']
                    }
                    
                    logger.info(f"✅ Downloaded {model_info['name']}")
                    
                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to download {voice_id}: {e}")
            else:
                self.voice_models[voice_id] = {
                    'model_path': model_path,
                    'config_path': config_path,
                    'name': model_info['name'],
                    'quality': model_info['quality']
                }
                logger.info(f"✅ Found existing {model_info['name']}")
    
    def select_voice_by_emotion(self, emotion: str) -> str:
        """Select appropriate voice based on detected emotion"""
        voice_mapping = {
            'happy': 'female_natural',
            'neutral': 'female_customer_service', 
            'sad': 'female_natural',
            'angry': 'male_professional',  # More authoritative
            'confused': 'female_customer_service',
            'default': 'female_customer_service'
        }
        
        return voice_mapping.get(emotion, voice_mapping['default'])
    
    def clean_text_for_tts(self, text: str) -> str:
        """Clean text for better TTS pronunciation"""
        # Remove tool calls
        import re
        text = re.sub(r'\[([^\]]+)\]', '', text)
        
        # Turkish-specific cleanup
        replacements = {
            'TL': 'Türk Lirası',
            'GB': 'gigabay',
            'SMS': 'es-em-es',
            'eSIM': 'i-sim',
            'WiFi': 'vay-fay',
            'QR': 'kıy-ar',
            'URL': 'yu-ar-el',
            'ID': 'ay-di',
            'API': 'a-pi-ay',
            '%': 'yüzde',
            '&': 've',
            '@': 'at işareti'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Remove special characters that cause issues
        text = re.sub(r'[^\w\s\.\,\!\?]', '', text)
        
        # Ensure proper spacing
        text = ' '.join(text.split())
        
        return text.strip()
    
    def generate_speech(self, 
                       text: str, 
                       emotion: str = "neutral", 
                       voice_id: Optional[str] = None,
                       speed: float = 1.0,
                       cache: bool = True) -> Optional[str]:
        """Generate speech audio file"""
        
        if not self.piper_executable:
            logger.error("Piper not available")
            return None
        
        # Clean text
        clean_text = self.clean_text_for_tts(text)
        if not clean_text:
            return None
        
        # Select voice
        if not voice_id:
            voice_id = self.select_voice_by_emotion(emotion)
        
        if voice_id not in self.voice_models:
            logger.error(f"Voice {voice_id} not available")
            return None
        
        # Check cache
        cache_key = hashlib.md5(f"{clean_text}_{voice_id}_{speed}".encode()).hexdigest()
        if cache and cache_key in self.audio_cache:
            cache_file = self.audio_cache[cache_key]
            if os.path.exists(cache_file):
                return cache_file
        
        # Generate audio
        try:
            # Create temporary output file
            output_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            output_path = output_file.name
            output_file.close()
            
            model_info = self.voice_models[voice_id]
            
            # Prepare piper command
            cmd = [
                self.piper_executable,
                '--model', model_info['model_path'],
                '--config', model_info['config_path'],
                '--output_file', output_path
            ]
            
            # Add speed control if supported
            if speed != 1.0:
                cmd.extend(['--length_scale', str(1.0/speed)])
            
            # Run piper
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=clean_text)
            
            if process.returncode == 0 and os.path.exists(output_path):
                if cache:
                    self.audio_cache[cache_key] = output_path
                
                logger.info(f"Generated TTS: {len(clean_text)} chars -> {output_path}")
                return output_path
            else:
                logger.error(f"Piper failed: {stderr}")
                if os.path.exists(output_path):
                    os.unlink(output_path)
                return None
                
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return None
    
    async def generate_speech_async(self, text: str, emotion: str = "neutral") -> Optional[str]:
        """Async wrapper for speech generation"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate_speech, text, emotion)
    
    def get_available_voices(self) -> Dict:
        """Get list of available voices"""
        return {
            voice_id: {
                'name': info['name'],
                'quality': info['quality']
            }
            for voice_id, info in self.voice_models.items()
        }
    
    def cleanup_cache(self, max_files: int = 100):
        """Clean up old audio cache files"""
        if len(self.audio_cache) > max_files:
            # Remove oldest files
            sorted_cache = sorted(
                self.audio_cache.items(),
                key=lambda x: os.path.getctime(x[1]) if os.path.exists(x[1]) else 0
            )
            
            for cache_key, file_path in sorted_cache[:len(self.audio_cache) - max_files]:
                try:
                    if os.path.exists(file_path):
                        os.unlink(file_path)
                    del self.audio_cache[cache_key]
                except Exception as e:
                    logger.error(f"Failed to cleanup {file_path}: {e}")

class TelcoTTSIntegration:
    """Integration of TTS with Telco AI System"""
    
    def __init__(self):
        self.tts = PiperTTS()
        self.enabled = self.tts.piper_executable is not None
        
    async def process_response_with_speech(self, 
                                          response_text: str, 
                                          emotion: str = "neutral") -> Dict:
        """Process AI response and generate speech"""
        
        result = {
            'text': response_text,
            'emotion': emotion,
            'audio_file': None,
            'audio_available': self.enabled
        }
        
        if not self.enabled:
            return result
        
        try:
            # Generate speech
            audio_file = await self.tts.generate_speech_async(response_text, emotion)
            result['audio_file'] = audio_file
            
            if audio_file:
                # Get file size for client
                file_size = os.path.getsize(audio_file)
                result['audio_size_bytes'] = file_size
                result['audio_duration_estimate'] = len(response_text) * 0.1  # ~0.1s per char
                
        except Exception as e:
            logger.error(f"TTS processing failed: {e}")
        
        return result
    
    def get_system_status(self) -> Dict:
        """Get TTS system status"""
        return {
            'tts_enabled': self.enabled,
            'piper_path': self.tts.piper_executable,
            'available_voices': self.tts.get_available_voices() if self.enabled else {},
            'cache_size': len(self.tts.audio_cache) if self.enabled else 0
        }

# Installation script
def install_piper_tts():
    """Install Piper TTS system"""
    
    print("🎤 Installing Piper TTS for Turkish...")
    
    try:
        # Install piper-tts
        subprocess.run(['pip', 'install', 'piper-tts'], check=True)
        print("✅ Installed piper-tts")
        
        # Install additional dependencies
        subprocess.run(['pip', 'install', 'onnxruntime'], check=True)
        print("✅ Installed onnxruntime")
        
        # Test installation
        result = subprocess.run(['piper', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Piper installed successfully: {result.stdout.strip()}")
            return True
        else:
            print("❌ Piper installation verification failed")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False

# Demo function
async def demo_turkish_tts():
    """Demonstrate Turkish TTS capabilities"""
    
    print("🗣️ Turkish TTS Demo")
    
    tts_integration = TelcoTTSIntegration()
    
    if not tts_integration.enabled:
        print("❌ TTS not available. Run install_piper_tts() first")
        return
    
    # Test phrases with different emotions
    test_cases = [
        ("Merhaba, size nasıl yardımcı olabilirim?", "happy"),
        ("Bakiyeniz 250 Türk Lirası, mevcut durumda ödemeli.", "neutral"),
        ("Yaşadığınız sorun için çok özür dileriz.", "sad"),
        ("Teknik ekibimiz sorununuzu hemen inceliyor.", "neutral"),
        ("eSIM aktivasyonunuz başarıyla tamamlandı!", "happy")
    ]
    
    print(f"Available voices: {list(tts_integration.tts.get_available_voices().keys())}")
    
    for text, emotion in test_cases:
        print(f"\n🎯 Testing: {emotion.upper()}")
        print(f"Text: {text}")
        
        result = await tts_integration.process_response_with_speech(text, emotion)
        
        if result['audio_file']:
            print(f"✅ Audio generated: {result['audio_file']}")
            print(f"📊 Size: {result.get('audio_size_bytes', 0)} bytes")
            print(f"⏱️ Duration: ~{result.get('audio_duration_estimate', 0):.1f}s")
        else:
            print("❌ Audio generation failed")

if __name__ == "__main__":
    # Install if needed
    import sys
    if "--install" in sys.argv:
        success = install_piper_tts()
        if success:
            print("\n🎉 Installation complete!")
            print("Now you can use Turkish TTS in your telco system!")
        sys.exit(0 if success else 1)
    
    # Run demo
    if "--demo" in sys.argv:
        asyncio.run(demo_turkish_tts())
    else:
        print("Usage:")
        print("  python PIPER_TTS_INTEGRATION.py --install")
        print("  python PIPER_TTS_INTEGRATION.py --demo")