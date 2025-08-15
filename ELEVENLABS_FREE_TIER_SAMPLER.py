#!/usr/bin/env python3
"""
ElevenLabs FREE TIER Sampler
Generates ~10,000 chars (within free tier) for testing
Smartly selects diverse conversations
"""

import os
import json
import time
import requests
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# ⚠️ ADD YOUR API KEY HERE ⚠️
ELEVENLABS_API_KEY = "YOUR_API_KEY_HERE"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class FreeTierSampler:
    def __init__(self, api_key: str, char_limit: int = 9500):
        self.api_key = api_key
        self.char_limit = char_limit  # Stay under 10k
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        # Best Turkish voices
        self.voices = {
            "male": "VR6AewLTigWG4xSOukaG",  # Arnold
            "female": "MF3mGyEYCl7XYWbV9V6O",  # Elli
        }
        
        self.emotion_settings = {
            "angry": {"stability": 0.3, "similarity_boost": 0.7},
            "normal": {"stability": 0.7, "similarity_boost": 0.75},
            "polite": {"stability": 0.8, "similarity_boost": 0.8}
        }
        
        self.audio_dir = "data/tts_audio_free"
        os.makedirs(self.audio_dir, exist_ok=True)
    
    def select_diverse_sample(self) -> List[Dict]:
        """Select diverse conversations within char limit"""
        
        selected = []
        total_chars = 0
        
        # Priority: Get variety of scenarios
        datasets = [
            ("data/varied_dataset/conversations", "detailed", 3),  # 3 detailed
            ("data/correct_flash_dataset", "short", 10),  # 10 short
            ("data/smart_flash_dataset", "smart", 10)  # 10 smart
        ]
        
        for dataset_dir, dataset_type, max_count in datasets:
            if not os.path.exists(dataset_dir):
                continue
            
            files = [f for f in os.listdir(dataset_dir) if f.endswith('.json')]
            random.shuffle(files)  # Random selection
            
            count = 0
            for file in files:
                if count >= max_count:
                    break
                
                with open(os.path.join(dataset_dir, file), 'r') as f:
                    conv = json.load(f)
                
                # Calculate characters
                turns = conv.get('customer_turns_for_tts', conv.get('customer_turns', []))
                conv_chars = sum(len(t.get('text', '')) for t in turns)
                
                if total_chars + conv_chars > self.char_limit:
                    continue
                
                selected.append({
                    "file": os.path.join(dataset_dir, file),
                    "type": dataset_type,
                    "id": conv.get('conversation_id', conv.get('id', file)),
                    "chars": conv_chars,
                    "turns": len(turns)
                })
                
                total_chars += conv_chars
                count += 1
        
        return selected, total_chars
    
    def text_to_speech(self, text: str, voice_id: str, emotion: str = "normal") -> Optional[bytes]:
        """Generate TTS with Flash v2.5"""
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        settings = self.emotion_settings.get(emotion, self.emotion_settings["normal"])
        
        data = {
            "text": text,
            "model_id": "eleven_flash_v2_5",
            "language_code": "tr",
            "voice_settings": {
                "stability": settings["stability"],
                "similarity_boost": settings["similarity_boost"],
                "use_speaker_boost": True
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=30)
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"API Error {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return None
    
    def process_sample(self, sample: Dict) -> Tuple[int, int]:
        """Process a single sample conversation"""
        
        with open(sample['file'], 'r') as f:
            conv = json.load(f)
        
        # Get customer turns
        turns = conv.get('customer_turns_for_tts', conv.get('customer_turns', []))
        
        # Select voice based on hash
        voice_key = "female" if hash(sample['id']) % 2 == 0 else "male"
        voice_id = self.voices[voice_key]
        
        success = 0
        failed = 0
        
        for i, turn in enumerate(turns):
            text = turn.get('text', '')
            if not text:
                continue
            
            emotion = turn.get('emotion', 'normal')
            
            audio = self.text_to_speech(text, voice_id, emotion)
            if audio:
                turn_id = turn.get('turn_id', turn.get('turn', f'turn_{i+1}'))
                filename = f"{self.audio_dir}/{sample['id']}_{turn_id}.mp3"
                with open(filename, 'wb') as f:
                    f.write(audio)
                success += 1
                time.sleep(0.3)  # Rate limit
            else:
                failed += 1
        
        return success, failed
    
    def generate_free_sample(self):
        """Generate FREE tier sample"""
        
        print("\n" + "="*80)
        print("🆓 ELEVENLABS FREE TIER SAMPLER")
        print("🎯 Target: <10,000 characters (FREE)")
        print("="*80)
        
        # Select diverse sample
        print("\n📊 Selecting diverse sample...")
        samples, total_chars = self.select_diverse_sample()
        
        print(f"✅ Selected {len(samples)} conversations")
        print(f"📝 Total characters: {total_chars:,} / 10,000")
        print(f"💰 Cost: FREE!")
        
        # Show sample distribution
        by_type = {}
        for s in samples:
            by_type[s['type']] = by_type.get(s['type'], 0) + 1
        
        print(f"\n📈 Sample distribution:")
        for type_name, count in by_type.items():
            print(f"   {type_name}: {count} conversations")
        
        # Process samples
        print(f"\n🎙️ Generating audio...")
        total_success = 0
        total_failed = 0
        
        for i, sample in enumerate(samples, 1):
            print(f"   [{i}/{len(samples)}] {sample['id'][:30]}... ({sample['chars']} chars)")
            success, failed = self.process_sample(sample)
            total_success += success
            total_failed += failed
        
        # Summary
        print("\n" + "="*80)
        print("✅ GENERATION COMPLETE!")
        print(f"🔊 Generated {total_success} audio files")
        if total_failed > 0:
            print(f"⚠️ Failed: {total_failed} turns")
        print(f"📁 Output: {self.audio_dir}")
        print(f"💾 Total size: ~{total_success * 10}KB")
        
        # Save manifest
        manifest = {
            "generated_at": datetime.now().isoformat(),
            "model": "eleven_flash_v2_5",
            "samples": samples,
            "statistics": {
                "conversations": len(samples),
                "characters": total_chars,
                "audio_files": total_success,
                "failed": total_failed
            }
        }
        
        with open(f"{self.audio_dir}/manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)
        
        print(f"\n📄 Manifest saved: {self.audio_dir}/manifest.json")
        
        return manifest

def main():
    # Check API key
    if ELEVENLABS_API_KEY == "YOUR_API_KEY_HERE":
        print("\n❌ SETUP REQUIRED:")
        print("1. Get FREE API key from: https://elevenlabs.io/sign-up")
        print("2. Edit line 15 with your key")
        print("3. Run again!")
        print("\n✅ FREE tier includes 10,000 characters/month!")
        return
    
    sampler = FreeTierSampler(ELEVENLABS_API_KEY)
    sampler.generate_free_sample()
    
    print("\n🚀 NEXT STEPS:")
    print("1. Test audio quality")
    print("2. If satisfied, upgrade to Creator plan ($22) for full dataset")
    print("3. Run ELEVENLABS_UNIVERSAL_TTS.py for complete generation")

if __name__ == "__main__":
    main()