#!/usr/bin/env python3
"""
ElevenLabs MINI TEST - Verify API and voice quality
Tests with just 2-3 conversations (~500 chars) before full generation
"""

import os
import json
import time
import requests
from datetime import datetime

# Your API key
ELEVENLABS_API_KEY = "sk_61bdd16dbc21a3820bfdb0601dc18db053a04ea7a8d77462"

class MiniTester:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        # Test with 2 voices only
        self.test_voices = {
            "male": "VR6AewLTigWG4xSOukaG",  # Arnold
            "female": "MF3mGyEYCl7XYWbV9V6O",  # Elli
        }
        
        self.output_dir = "data/tts_test"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def test_api_connection(self):
        """Test API key validity"""
        print("🔌 Testing API connection...")
        
        url = "https://api.elevenlabs.io/v1/user"
        
        try:
            response = requests.get(url, headers={"xi-api-key": self.api_key})
            if response.status_code == 200:
                user_info = response.json()
                print(f"✅ API Connected!")
                print(f"   Subscription: {user_info.get('subscription', {}).get('tier', 'Unknown')}")
                print(f"   Character limit: {user_info.get('subscription', {}).get('character_limit', 'Unknown')}")
                print(f"   Characters used: {user_info.get('subscription', {}).get('character_count', 0)}")
                return True
            else:
                print(f"❌ API Error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def generate_test_audio(self, text: str, voice_id: str, filename: str):
        """Generate single test audio"""
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        data = {
            "text": text,
            "model_id": "eleven_flash_v2_5",
            "language_code": "tr",
            "voice_settings": {
                "stability": 0.7,
                "similarity_boost": 0.75,
                "use_speaker_boost": True
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                audio_path = f"{self.output_dir}/{filename}.mp3"
                with open(audio_path, 'wb') as f:
                    f.write(response.content)
                print(f"   ✅ Generated: {filename}.mp3 ({len(text)} chars)")
                return True
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text[:100]}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def run_mini_test(self):
        """Run minimal test with 2-3 samples"""
        
        print("\n" + "="*60)
        print("🧪 ELEVENLABS MINI TEST")
        print("="*60)
        
        # First check API
        if not self.test_api_connection():
            return False
        
        # Select 2-3 test conversations
        test_samples = [
            {
                "id": "test_001",
                "text": "Merhaba, eSIM'im çalışmıyor. Yardımcı olabilir misiniz?",
                "voice": "male",
                "emotion": "frustrated"
            },
            {
                "id": "test_002", 
                "text": "Faturamda anlamadığım bir ücret var.",
                "voice": "female",
                "emotion": "confused"
            },
            {
                "id": "test_003",
                "text": "Teşekkür ederim, çok yardımcı oldunuz!",
                "voice": "female",
                "emotion": "polite"
            }
        ]
        
        print(f"\n🎤 Testing voice generation...")
        print(f"   Total characters: {sum(len(s['text']) for s in test_samples)}")
        
        success = 0
        for sample in test_samples:
            voice_id = self.test_voices[sample['voice']]
            if self.generate_test_audio(sample['text'], voice_id, sample['id']):
                success += 1
            time.sleep(0.5)  # Rate limit
        
        print(f"\n📊 Test Results:")
        print(f"   Success: {success}/{len(test_samples)}")
        print(f"   Output: {self.output_dir}/")
        
        if success == len(test_samples):
            print(f"\n✅ ALL TESTS PASSED!")
            print(f"   API working correctly")
            print(f"   Flash v2.5 generating Turkish audio")
            print(f"   Ready for full generation!")
            return True
        else:
            print(f"\n⚠️ Some tests failed")
            return False

def test_real_conversation():
    """Test with actual conversation from dataset"""
    
    print("\n🔄 Testing with real conversation...")
    
    # Load a short conversation
    test_file = "data/smart_flash_dataset/smart_0001.json"
    
    if os.path.exists(test_file):
        with open(test_file, 'r') as f:
            conv = json.load(f)
        
        print(f"   Loaded: {conv.get('id', 'unknown')}")
        
        # Get customer turns
        turns = conv.get('customer_turns', [])
        total_chars = sum(len(t.get('text', '')) for t in turns)
        print(f"   Customer turns: {len(turns)}")
        print(f"   Total characters: {total_chars}")
        
        return conv
    else:
        print("   No test file found")
        return None

def main():
    print("🚀 ElevenLabs Mini Test Starting...")
    
    # Run mini test
    tester = MiniTester(ELEVENLABS_API_KEY)
    
    if tester.run_mini_test():
        # Test with real conversation
        real_conv = test_real_conversation()
        
        if real_conv:
            print("\n💡 Next Steps:")
            print("1. Listen to generated test audio")
            print("2. If quality is good, run FREE tier sampler")
            print("3. Then proceed with full generation")
        
        print("\n📝 Character Usage:")
        print("   This test: ~150 characters")
        print("   FREE tier remaining: ~9,850 characters")
        print("   Full dataset needs: 64,000 characters")
    else:
        print("\n❌ Tests failed - check API key and connection")

if __name__ == "__main__":
    main()