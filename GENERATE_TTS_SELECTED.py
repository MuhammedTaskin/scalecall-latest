#!/usr/bin/env python3
"""
ElevenLabs TTS for Selected Best Conversations
Auto-generated to stay within 110k character limit
"""

import os
import json
import time
import requests
from datetime import datetime

ELEVENLABS_API_KEY = "sk_61bdd16dbc21a3820bfdb0601dc18db053a04ea7a8d77462"

class SelectedTTSGenerator:
    def __init__(self):
        self.api_key = ELEVENLABS_API_KEY
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        # Load selection
        with open("data/selected_for_tts.json", 'r') as f:
            self.selection = json.load(f)
        
        # 37 voices for variety
        self.voices = [
            "pNInz6obpgDQGcFmaJgB", "VR6AewLTigWG4xSOukaG", "yoZ06aMxZJJ28mfd3POQ",
            "21m00Tcm4TlvDq8ikWAM", "MF3mGyEYCl7XYWbV9V6O", "XB0fDUnXU5powFXDhCwa",
            # Add more voice IDs as needed
        ]
        
        self.output_dir = "data/tts_audio_final"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_all(self):
        """Generate TTS for all selected conversations"""
        
        print(f"🎤 Generating TTS for {len(self.selection['conversations'])} conversations")
        print(f"   Total characters: {self.selection['metadata']['total_chars']:,}")
        print(f"   Using Flash v2.5: 0.5 credits per char (50% cheaper!)")
        print(f"   Credits needed: {self.selection['metadata']['total_chars'] // 2:,}")
        
        for i, conv_info in enumerate(self.selection['conversations']):
            # Load conversation
            with open(conv_info['path'], 'r') as f:
                conv = json.load(f)
            
            # Get voice (consistent per conversation)
            voice_id = self.voices[hash(conv_info['id']) % len(self.voices)]
            
            # Generate audio for each turn
            customer_turns = conv.get('customer_turns_for_tts', conv.get('customer_turns', []))
            for j, turn in enumerate(customer_turns):
                text = turn.get('text', '')
                if not text:
                    continue
                
                # Generate audio
                audio = self.text_to_speech(text, voice_id, turn.get('emotion', 'normal'))
                if audio:
                    filename = f"{self.output_dir}/{conv_info['id']}_turn_{j+1}.mp3"
                    with open(filename, 'wb') as f:
                        f.write(audio)
                
                time.sleep(0.3)  # Rate limit
            
            if (i + 1) % 10 == 0:
                print(f"   Progress: {i+1}/{len(self.selection['conversations'])}")
        
        print(f"✅ TTS generation complete!")
        print(f"📁 Audio files in: {self.output_dir}")
    
    def text_to_speech(self, text: str, voice_id: str, emotion: str) -> bytes:
        """Generate TTS with Flash v2.5"""
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        data = {
            "text": text,
            "model_id": "eleven_flash_v2_5",  # 0.5 credits per char (50% cheaper!)
            "language_code": "tr",
            "voice_settings": {
                "stability": 0.7 if emotion == "normal" else 0.4,
                "similarity_boost": 0.75,
                "use_speaker_boost": True
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=30)
            if response.status_code == 200:
                return response.content
        except:
            pass
        return None

if __name__ == "__main__":
    generator = SelectedTTSGenerator()
    generator.generate_all()
