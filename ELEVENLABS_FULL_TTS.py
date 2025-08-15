#!/usr/bin/env python3
"""
Complete ElevenLabs TTS for ALL conversations
Processes both detailed (20) and short (100) conversations
"""

import os
import json
import time
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ⚠️ ADD YOUR API KEY HERE ⚠️
ELEVENLABS_API_KEY = "YOUR_API_KEY_HERE"

class CompleteTTSGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        # Best Turkish voices (tested)
        self.voices = {
            "male_1": "21m00Tcm4TlvDq8ikWAM",  # Josh
            "male_2": "VR6AewLTigWG4xSOukaG",  # Arnold  
            "female_1": "EXAVITQu4vr4xnSDxMaL",  # Bella
            "female_2": "MF3mGyEYCl7XYWbV9V6O",  # Elli
        }
        
        self.emotion_settings = {
            "angry": {"stability": 0.3, "similarity_boost": 0.7},
            "confused": {"stability": 0.5, "similarity_boost": 0.6},
            "normal": {"stability": 0.7, "similarity_boost": 0.75},
            "impatient": {"stability": 0.35, "similarity_boost": 0.7},
            "polite": {"stability": 0.75, "similarity_boost": 0.8}
        }
        
        self.audio_dir = "data/tts_audio"
        os.makedirs(self.audio_dir, exist_ok=True)
    
    def text_to_speech(self, text: str, voice_id: str, emotion: str = "normal") -> bytes:
        """Generate TTS with ElevenLabs Flash v2.5"""
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        settings = self.emotion_settings.get(emotion, self.emotion_settings["normal"])
        
        data = {
            "text": text,
            "model_id": "eleven_flash_v2_5",
            "voice_settings": {
                "stability": settings["stability"],
                "similarity_boost": settings["similarity_boost"],
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        response = requests.post(url, json=data, headers=self.headers)
        
        if response.status_code == 200:
            return response.content
        else:
            print(f"  Error: {response.status_code}")
            return None
    
    def process_detailed_conversation(self, conv_file: str):
        """Process detailed conversation (20 conversations)"""
        
        conv_id = os.path.basename(conv_file).replace('.json', '')
        
        with open(conv_file, 'r', encoding='utf-8') as f:
            conv = json.load(f)
        
        audio_files = []
        voice_id = self.voices[f"{'female' if hash(conv_id) % 2 else 'male'}_{(hash(conv_id) % 2) + 1}"]
        
        for turn in conv.get('customer_turns_for_tts', []):
            text = turn['text']
            emotion = turn.get('emotion', 'normal')
            
            audio = self.text_to_speech(text, voice_id, emotion)
            if audio:
                filename = f"{self.audio_dir}/{conv_id}_{turn['turn_id']}.mp3"
                with open(filename, 'wb') as f:
                    f.write(audio)
                audio_files.append(filename)
                time.sleep(0.3)  # Rate limit
        
        return conv_id, len(audio_files)
    
    def process_short_conversation(self, conv_file: str):
        """Process short conversation (100 conversations)"""
        
        conv_id = os.path.basename(conv_file).replace('.json', '')
        
        with open(conv_file, 'r', encoding='utf-8') as f:
            conv = json.load(f)
        
        audio_files = []
        voice_id = self.voices[f"{'female' if hash(conv_id) % 2 else 'male'}_{(hash(conv_id) % 2) + 1}"]
        
        for turn in conv.get('customer_turns', []):
            text = turn['text']
            emotion = turn.get('emotion', 'normal')
            
            audio = self.text_to_speech(text, voice_id, emotion)
            if audio:
                filename = f"{self.audio_dir}/{conv_id}_turn{turn['turn']}.mp3"
                with open(filename, 'wb') as f:
                    f.write(audio)
                audio_files.append(filename)
                time.sleep(0.3)  # Rate limit
        
        return conv_id, len(audio_files)
    
    def process_all(self):
        """Process ALL conversations"""
        
        print("🎙️ ELEVENLABS TTS GENERATOR")
        print("=" * 60)
        
        # Get conversation files
        detailed_files = [
            f"data/varied_dataset/conversations/{f}" 
            for f in os.listdir("data/varied_dataset/conversations") 
            if f.endswith('.json')
        ][:20]  # First 20
        
        short_files = [
            f"data/flash_lite_dataset/{f}"
            for f in os.listdir("data/flash_lite_dataset")
            if f.endswith('.json')
        ][:100]  # First 100
        
        print(f"📁 Found {len(detailed_files)} detailed + {len(short_files)} short conversations")
        print(f"🔊 Generating ~300 audio files...")
        
        total_audio = 0
        
        # Process with 3 workers
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Process detailed
            print("\n📝 Processing detailed conversations...")
            futures = {executor.submit(self.process_detailed_conversation, f): f for f in detailed_files}
            for future in as_completed(futures):
                conv_id, num_audio = future.result()
                total_audio += num_audio
                print(f"  ✅ {conv_id}: {num_audio} audio files")
            
            # Process short
            print("\n⚡ Processing short conversations...")
            futures = {executor.submit(self.process_short_conversation, f): f for f in short_files}
            for i, future in enumerate(as_completed(futures)):
                conv_id, num_audio = future.result()
                total_audio += num_audio
                if (i+1) % 20 == 0:
                    print(f"  ✅ Progress: {i+1}/100")
        
        print("\n" + "=" * 60)
        print(f"✅ TTS COMPLETE!")
        print(f"🔊 Generated {total_audio} audio files")
        print(f"📁 Audio directory: {self.audio_dir}")
        print(f"💾 Ready for training!")
        
        return total_audio

def main():
    # Check API key
    if ELEVENLABS_API_KEY == "YOUR_API_KEY_HERE":
        print("❌ SETUP REQUIRED:")
        print("1. Get API key from https://elevenlabs.io")
        print("2. Edit this file and add your key on line 14")
        print("3. Run again!")
        return
    
    tts = CompleteTTSGenerator(ELEVENLABS_API_KEY)
    tts.process_all()

if __name__ == "__main__":
    main()