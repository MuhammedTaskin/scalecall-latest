#!/usr/bin/env python3
"""
UNIVERSAL ElevenLabs TTS Generator
Handles ALL dataset structures (detailed, short, smart) with robust error handling
Uses Flash v2.5 for ultra-low latency (75ms)
"""

import os
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import logging

# ⚠️ ADD YOUR API KEY HERE ⚠️
ELEVENLABS_API_KEY = "YOUR_API_KEY_HERE"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UniversalTTSGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        # Turkish voices (best performers for Turkish)
        self.voices = {
            "male_1": "pNInz6obpgDQGcFmaJgB",  # Adam - Deep
            "male_2": "VR6AewLTigWG4xSOukaG",  # Arnold - Professional
            "male_3": "yoZ06aMxZJJ28mfd3POQ",  # Sam - Young
            "female_1": "21m00Tcm4TlvDq8ikWAM",  # Rachel - Warm
            "female_2": "MF3mGyEYCl7XYWbV9V6O",  # Elli - Professional
            "female_3": "XB0fDUnXU5powFXDhCwa",  # Charlotte - Young
        }
        
        # Emotion-specific voice settings
        self.emotion_settings = {
            "angry": {
                "stability": 0.25,
                "similarity_boost": 0.65,
                "style": 0.3,
                "use_speaker_boost": True
            },
            "confused": {
                "stability": 0.45,
                "similarity_boost": 0.6,
                "style": 0.2,
                "use_speaker_boost": True
            },
            "normal": {
                "stability": 0.7,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            },
            "impatient": {
                "stability": 0.35,
                "similarity_boost": 0.7,
                "style": 0.25,
                "use_speaker_boost": True
            },
            "polite": {
                "stability": 0.8,
                "similarity_boost": 0.8,
                "style": 0.0,
                "use_speaker_boost": True
            },
            "frustrated": {
                "stability": 0.3,
                "similarity_boost": 0.65,
                "style": 0.35,
                "use_speaker_boost": True
            },
            "cheerful": {
                "stability": 0.6,
                "similarity_boost": 0.7,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        # Output directories
        self.audio_base = "data/tts_audio"
        self.audio_dirs = {
            "detailed": f"{self.audio_base}/detailed",
            "short": f"{self.audio_base}/short",
            "smart": f"{self.audio_base}/smart"
        }
        
        for dir_path in self.audio_dirs.values():
            os.makedirs(dir_path, exist_ok=True)
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "successful": 0,
            "failed": 0,
            "retries": 0
        }
    
    def get_consistent_voice(self, conv_id: str, gender_preference: Optional[str] = None) -> str:
        """Get consistent voice for a conversation based on ID"""
        # Use hash to consistently select voice
        hash_val = int(hashlib.md5(conv_id.encode()).hexdigest(), 16)
        
        if gender_preference:
            voice_pool = [k for k in self.voices.keys() if k.startswith(gender_preference)]
        else:
            # Random but consistent gender based on hash
            gender = "female" if hash_val % 2 == 0 else "male"
            voice_pool = [k for k in self.voices.keys() if k.startswith(gender)]
        
        # Select voice from pool
        voice_key = voice_pool[hash_val % len(voice_pool)]
        return self.voices[voice_key]
    
    def text_to_speech_with_retry(
        self, 
        text: str, 
        voice_id: str, 
        emotion: str = "normal",
        language_code: str = "tr",
        max_retries: int = 3
    ) -> Optional[bytes]:
        """Generate TTS with Flash v2.5 and retry logic"""
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        settings = self.emotion_settings.get(emotion, self.emotion_settings["normal"])
        
        data = {
            "text": text,
            "model_id": "eleven_flash_v2_5",
            "language_code": language_code,  # Enforce Turkish
            "voice_settings": settings
        }
        
        for attempt in range(max_retries):
            try:
                self.stats["total_requests"] += 1
                
                response = requests.post(
                    url, 
                    json=data, 
                    headers=self.headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    self.stats["successful"] += 1
                    return response.content
                elif response.status_code == 429:  # Rate limit
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    self.stats["retries"] += 1
                else:
                    logger.error(f"API Error {response.status_code}: {response.text[:200]}")
                    self.stats["failed"] += 1
                    return None
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    self.stats["retries"] += 1
                else:
                    self.stats["failed"] += 1
                    return None
        
        return None
    
    def detect_conversation_format(self, conv: Dict) -> str:
        """Detect which format the conversation uses"""
        if "customer_turns_for_tts" in conv:
            return "detailed"
        elif "customer_turns" in conv and isinstance(conv["customer_turns"][0], dict):
            if "turn" in conv["customer_turns"][0]:
                return "smart"
        elif "customer_turns_for_tts" in conv:
            return "short"
        else:
            # Try to detect from structure
            if "agent_handoffs" in conv and len(conv.get("agent_handoffs", [])) > 0:
                return "short"
            else:
                return "smart"
    
    def extract_customer_turns(self, conv: Dict, format_type: str) -> List[Dict]:
        """Extract customer turns based on format"""
        turns = []
        
        if format_type == "detailed":
            for turn in conv.get("customer_turns_for_tts", []):
                turns.append({
                    "id": turn.get("turn_id", f"turn_{len(turns)+1}"),
                    "text": turn.get("text", ""),
                    "emotion": turn.get("emotion", "normal")
                })
        
        elif format_type == "short":
            for turn in conv.get("customer_turns_for_tts", []):
                turns.append({
                    "id": turn.get("turn_id", f"turn_{len(turns)+1}"),
                    "text": turn.get("text", ""),
                    "emotion": turn.get("emotion", "normal")
                })
        
        elif format_type == "smart":
            for turn in conv.get("customer_turns", []):
                turns.append({
                    "id": f"turn_{turn.get('turn', len(turns)+1):03d}",
                    "text": turn.get("text", ""),
                    "emotion": turn.get("emotion", "normal")
                })
        
        return turns
    
    def process_conversation(self, conv_file: str, dataset_type: str) -> Tuple[str, int, int]:
        """Process any conversation format"""
        
        conv_id = os.path.basename(conv_file).replace('.json', '')
        
        try:
            with open(conv_file, 'r', encoding='utf-8') as f:
                conv = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load {conv_file}: {e}")
            return conv_id, 0, 1
        
        # Detect format
        format_type = self.detect_conversation_format(conv)
        
        # Extract customer turns
        customer_turns = self.extract_customer_turns(conv, format_type)
        
        if not customer_turns:
            logger.warning(f"No customer turns found in {conv_id}")
            return conv_id, 0, 0
        
        # Get consistent voice for this conversation
        voice_id = self.get_consistent_voice(conv_id)
        
        # Generate audio for each turn
        audio_dir = self.audio_dirs[dataset_type]
        audio_files = []
        failed = 0
        
        for turn in customer_turns:
            if not turn["text"]:
                continue
            
            audio = self.text_to_speech_with_retry(
                text=turn["text"],
                voice_id=voice_id,
                emotion=turn["emotion"]
            )
            
            if audio:
                filename = f"{audio_dir}/{conv_id}_{turn['id']}.mp3"
                with open(filename, 'wb') as f:
                    f.write(audio)
                audio_files.append(filename)
                
                # Rate limiting
                time.sleep(0.25)
            else:
                failed += 1
                logger.error(f"Failed to generate audio for {conv_id}_{turn['id']}")
        
        return conv_id, len(audio_files), failed
    
    def process_dataset(self, dataset_dir: str, dataset_type: str, max_files: Optional[int] = None):
        """Process an entire dataset"""
        
        # Get all JSON files
        files = [
            os.path.join(dataset_dir, f)
            for f in os.listdir(dataset_dir)
            if f.endswith('.json')
        ]
        
        if max_files:
            files = files[:max_files]
        
        logger.info(f"Processing {len(files)} files from {dataset_type} dataset")
        
        results = {
            "successful": 0,
            "failed": 0,
            "total_audio": 0
        }
        
        # Process with thread pool
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self.process_conversation, f, dataset_type): f
                for f in files
            }
            
            for i, future in enumerate(as_completed(futures), 1):
                conv_id, audio_count, failed_count = future.result()
                
                results["total_audio"] += audio_count
                if audio_count > 0:
                    results["successful"] += 1
                if failed_count > 0:
                    results["failed"] += failed_count
                
                if i % 10 == 0:
                    logger.info(f"  Progress: {i}/{len(files)} - Generated {results['total_audio']} audio files")
        
        return results
    
    def generate_all(self):
        """Generate TTS for ALL datasets"""
        
        print("\n" + "="*80)
        print("🎙️ UNIVERSAL ELEVENLABS TTS GENERATOR")
        print("🚀 Using Flash v2.5 for 75ms latency")
        print("="*80)
        
        datasets = [
            ("data/varied_dataset/conversations", "detailed", None),
            ("data/correct_flash_dataset", "short", None),
            ("data/smart_flash_dataset", "smart", None)
        ]
        
        total_results = {
            "conversations": 0,
            "audio_files": 0,
            "failed": 0
        }
        
        for dataset_dir, dataset_type, max_files in datasets:
            if not os.path.exists(dataset_dir):
                logger.warning(f"Dataset not found: {dataset_dir}")
                continue
            
            print(f"\n📁 Processing {dataset_type.upper()} dataset...")
            print(f"   Directory: {dataset_dir}")
            
            results = self.process_dataset(dataset_dir, dataset_type, max_files)
            
            total_results["conversations"] += results["successful"]
            total_results["audio_files"] += results["total_audio"]
            total_results["failed"] += results["failed"]
            
            print(f"   ✅ Generated {results['total_audio']} audio files from {results['successful']} conversations")
            
            if results["failed"] > 0:
                print(f"   ⚠️ Failed: {results['failed']} turns")
        
        # Final statistics
        print("\n" + "="*80)
        print("📊 FINAL STATISTICS")
        print("="*80)
        print(f"✅ Total conversations processed: {total_results['conversations']}")
        print(f"🔊 Total audio files generated: {total_results['audio_files']}")
        print(f"📁 Audio directory: {self.audio_base}")
        
        if total_results["failed"] > 0:
            print(f"⚠️ Total failed turns: {total_results['failed']}")
        
        print(f"\n📈 API Statistics:")
        print(f"   Total requests: {self.stats['total_requests']}")
        print(f"   Successful: {self.stats['successful']}")
        print(f"   Failed: {self.stats['failed']}")
        print(f"   Retries: {self.stats['retries']}")
        
        if self.stats['successful'] > 0:
            success_rate = (self.stats['successful'] / self.stats['total_requests']) * 100
            print(f"   Success rate: {success_rate:.1f}%")
        
        print("\n🎉 READY FOR TRAINING!")
        print("   Next steps:")
        print("   1. Create training pairs with audio + text")
        print("   2. Fine-tune Gemma 3N with multimodal data")
        print("   3. Implement persona switching mechanism")
        
        return total_results

def check_api_key():
    """Check if API key is configured"""
    if ELEVENLABS_API_KEY == "YOUR_API_KEY_HERE":
        print("\n❌ SETUP REQUIRED:")
        print("="*60)
        print("1. Get your API key from: https://elevenlabs.io/sign-up")
        print("2. Edit this file and replace 'YOUR_API_KEY_HERE' on line 17")
        print("3. Run again!")
        print("\n💡 TIP: ElevenLabs offers free tier with 10,000 characters/month")
        print("   Our dataset needs ~50,000 characters total")
        return False
    return True

def main():
    if not check_api_key():
        return
    
    # Initialize generator
    tts = UniversalTTSGenerator(ELEVENLABS_API_KEY)
    
    # Generate all audio
    results = tts.generate_all()
    
    # Save metadata
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "model": "eleven_flash_v2_5",
        "language": "tr",
        "statistics": results,
        "voices_used": list(tts.voices.keys())
    }
    
    with open("data/tts_audio/metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n💾 Metadata saved to: data/tts_audio/metadata.json")

if __name__ == "__main__":
    main()