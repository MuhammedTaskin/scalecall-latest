#!/usr/bin/env python3
"""
FAST ElevenLabs TTS Generator
Voices customer turns from conversations
"""

import os
import json
import time
from typing import Dict, List
from datetime import datetime
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# ElevenLabs Configuration
ELEVENLABS_API_KEY = "YOUR_API_KEY_HERE"  # REPLACE THIS!
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1"

class FastElevenLabsTTS:
    def __init__(self):
        self.api_key = ELEVENLABS_API_KEY
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        # Turkish voices available in ElevenLabs
        self.turkish_voices = {
            "male_young": "21m00Tcm4TlvDq8ikWAM",  # Josh - works for Turkish
            "male_middle": "VR6AewLTigWG4xSOukaG",  # Arnold
            "female_young": "EXAVITQu4vr4xnSDxMaL",  # Bella  
            "female_middle": "MF3mGyEYCl7XYWbV9V6O",  # Elli
            "female_elderly": "XrExE9yKIg1WjnnlVkGX",  # Lily
            "male_elderly": "N2lVS1w4EtoT3dr4eOWO"   # Callum
        }
        
        # Map personas to voices
        self.persona_voice_map = {
            "angry_young": "male_young",
            "confused_elderly": "female_elderly",
            "business_professional": "male_middle",
            "frustrated_parent": "female_middle",
            "tech_savvy_impatient": "male_young",
            "polite_but_firm": "female_middle",
            "passive_aggressive": "male_middle",
            "overly_chatty": "female_young",
            "suspicious_paranoid": "male_elderly",
            "cheerful_optimistic": "female_young"
        }
        
        # Emotion to voice settings mapping
        self.emotion_settings = {
            "angry": {"stability": 0.3, "similarity_boost": 0.7, "style": 0.8},
            "frustrated": {"stability": 0.4, "similarity_boost": 0.7, "style": 0.7},
            "confused": {"stability": 0.5, "similarity_boost": 0.6, "style": 0.5},
            "happy": {"stability": 0.6, "similarity_boost": 0.8, "style": 0.3},
            "neutral": {"stability": 0.7, "similarity_boost": 0.75, "style": 0.2},
            "worried": {"stability": 0.45, "similarity_boost": 0.65, "style": 0.6},
            "impatient": {"stability": 0.35, "similarity_boost": 0.7, "style": 0.75}
        }
        
        # Directories
        self.conversations_dir = "data/varied_dataset/conversations"
        self.audio_dir = "data/varied_dataset/audio"
        self.tracking_dir = "data/varied_dataset/tts_tracking"
        
        for dir_path in [self.audio_dir, self.tracking_dir]:
            os.makedirs(dir_path, exist_ok=True)
    
    def text_to_speech(self, text: str, voice_id: str, settings: Dict) -> bytes:
        """Convert text to speech using ElevenLabs API"""
        
        url = f"{ELEVENLABS_API_URL}/text-to-speech/{voice_id}"
        
        data = {
            "text": text,
            "model_id": "eleven_flash_v2_5",  # BEST for conversational AI - 75ms latency! (v3 not suitable - high latency)
            "voice_settings": {
                "stability": settings.get("stability", 0.5),
                "similarity_boost": settings.get("similarity_boost", 0.75),
                "style": settings.get("style", 0.0),
                "use_speaker_boost": True
            }
        }
        
        response = requests.post(url, json=data, headers=self.headers)
        
        if response.status_code == 200:
            return response.content
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    
    def process_conversation(self, conv_file: str) -> Dict:
        """Process a single conversation file"""
        
        conv_id = os.path.basename(conv_file).replace('.json', '')
        print(f"  Processing: {conv_id}")
        
        with open(conv_file, 'r', encoding='utf-8') as f:
            conversation = json.load(f)
        
        # Get customer persona
        persona = conversation['customer_profile']['persona']
        voice_type = self.persona_voice_map.get(persona, "female_young")
        voice_id = self.turkish_voices[voice_type]
        
        # Create conversation audio directory
        conv_audio_dir = os.path.join(self.audio_dir, conv_id)
        os.makedirs(conv_audio_dir, exist_ok=True)
        
        audio_files = []
        
        # Process each customer turn
        for turn in conversation.get('customer_turns_for_tts', []):
            turn_id = turn['turn_id']
            text = turn['text']
            emotion = turn.get('emotion', 'neutral')
            
            # Get emotion settings
            settings = self.emotion_settings.get(emotion, self.emotion_settings['neutral'])
            
            print(f"    {turn_id}: {emotion} - {text[:50]}...")
            
            # Generate audio
            audio_data = self.text_to_speech(text, voice_id, settings)
            
            if audio_data:
                # Save audio file
                audio_file = os.path.join(conv_audio_dir, f"{turn_id}.mp3")
                with open(audio_file, 'wb') as f:
                    f.write(audio_data)
                
                audio_files.append({
                    "turn_id": turn_id,
                    "file": audio_file,
                    "emotion": emotion,
                    "text": text
                })
                
                # Rate limiting (ElevenLabs has limits)
                time.sleep(0.5)
        
        return {
            "conversation_id": conv_id,
            "audio_files": audio_files,
            "total_turns": len(audio_files)
        }
    
    def process_all_conversations(self, max_workers: int = 3):
        """Process all conversations with parallel TTS generation"""
        
        # Get all conversation files
        conv_files = [
            os.path.join(self.conversations_dir, f)
            for f in os.listdir(self.conversations_dir)
            if f.endswith('.json')
        ]
        
        print(f"🎙️ FAST ELEVENLABS TTS GENERATOR")
        print(f"📁 Found {len(conv_files)} conversations")
        print(f"🔊 Generating audio with {max_workers} parallel workers")
        print("=" * 60)
        
        results = []
        failed = []
        
        # Process with thread pool for speed
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_conv = {
                executor.submit(self.process_conversation, conv_file): conv_file
                for conv_file in conv_files
            }
            
            for future in as_completed(future_to_conv):
                conv_file = future_to_conv[future]
                try:
                    result = future.result()
                    results.append(result)
                    print(f"  ✅ Completed: {result['conversation_id']} ({result['total_turns']} turns)")
                except Exception as e:
                    failed.append(conv_file)
                    print(f"  ❌ Failed: {conv_file} - {str(e)}")
        
        # Save tracking
        tracking = {
            "generated_at": datetime.now().isoformat(),
            "total_conversations": len(conv_files),
            "successful": len(results),
            "failed": len(failed),
            "audio_generated": sum(r['total_turns'] for r in results),
            "results": results
        }
        
        tracking_file = os.path.join(self.tracking_dir, "tts_generation.json")
        with open(tracking_file, 'w') as f:
            json.dump(tracking, f, indent=2)
        
        print("\n" + "=" * 60)
        print(f"✅ TTS GENERATION COMPLETE!")
        print(f"📊 Successful: {len(results)}/{len(conv_files)}")
        print(f"🔊 Total audio files: {tracking['audio_generated']}")
        print(f"📁 Audio directory: {self.audio_dir}")
        print("=" * 60)
        
        return tracking

def main():
    """Main execution"""
    
    # Check API key
    if ELEVENLABS_API_KEY == "YOUR_API_KEY_HERE":
        print("❌ ERROR: Set your ElevenLabs API key first!")
        print("Get it from: https://elevenlabs.io/api")
        return
    
    tts = FastElevenLabsTTS()
    
    # Process all conversations FAST
    tts.process_all_conversations(max_workers=3)  # Parallel processing
    
    print("\n🎯 Next step: Create training pairs with audio + agent responses")

if __name__ == "__main__":
    main()