#!/usr/bin/env python3
"""
ElevenLabs FREE TIER TTS Generator
Maximum impact with 10k character limit
"""

import os
import json
import time
import requests

# You can get a FREE API key from ElevenLabs
ELEVENLABS_API_KEY = "YOUR_FREE_API_KEY_HERE"

class FreeTierTTS:
    def __init__(self):
        self.api_key = ELEVENLABS_API_KEY
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        # Load selection
        with open("data/selected_for_free_tier.json", 'r') as f:
            self.selection = json.load(f)
        
        # Use default voices (no cloning in free tier)
        self.voices = [
            "21m00Tcm4TlvDq8ikWAM",  # Adam
            "AZnzlk1XvdvUeBnXmlld",  # Domi
            "EXAVITQu4vr4xnSDxMaL",  # Bella
        ]
        
        self.output_dir = "data/tts_audio_free"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_all(self):
        """Generate TTS for critical conversations"""
        
        print(f"🎤 Generating TTS for {len(self.selection['conversations'])} critical conversations")
        print(f"   Using FREE tier: {self.selection['metadata']['total_chars']:,} / 10,000 chars")
        
        for i, conv_info in enumerate(self.selection['conversations']):
            print(f"\n📢 Processing: {conv_info['id']}")
            print(f"   Agents: {', '.join(conv_info['agents'])}")
            
            # Load conversation
            with open(conv_info['path'], 'r') as f:
                conv = json.load(f)
            
            # Get voice (rotate through available)
            voice_id = self.voices[i % len(self.voices)]
            
            # Generate audio for each turn
            customer_turns = conv.get('customer_turns_for_tts', conv.get('customer_turns', []))
            for j, turn in enumerate(customer_turns):
                text = turn.get('text', '')
                if not text:
                    continue
                
                print(f"   Turn {j+1}: {len(text)} chars")
                
                # Generate audio
                audio = self.text_to_speech(text, voice_id)
                if audio:
                    filename = f"{self.output_dir}/{conv_info['id']}_turn_{j+1}.mp3"
                    with open(filename, 'wb') as f:
                        f.write(audio)
                    print(f"   ✓ Saved: {filename}")
                
                time.sleep(0.5)  # Rate limit for free tier
        
        print(f"\n✅ FREE TIER TTS COMPLETE!")
        print(f"📁 Audio files in: {self.output_dir}")
    
    def text_to_speech(self, text: str, voice_id: str) -> bytes:
        """Generate TTS with free tier"""
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",  # Free tier model
            "language_code": "tr",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=30)
            if response.status_code == 200:
                return response.content
            else:
                print(f"   ⚠️ Error: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
        return None

if __name__ == "__main__":
    print("🚀 FREE TIER TTS GENERATOR")
    print("="*60)
    
    if ELEVENLABS_API_KEY == "YOUR_FREE_API_KEY_HERE":
        print("⚠️ Please add your FREE ElevenLabs API key!")
        print("1. Go to https://elevenlabs.io")
        print("2. Sign up for FREE account")
        print("3. Get your API key from settings")
        print("4. Replace YOUR_FREE_API_KEY_HERE in this script")
    else:
        generator = FreeTierTTS()
        generator.generate_all()
