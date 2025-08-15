#!/usr/bin/env python3
"""
VOICE MORE CONVERSATIONS FAST!
Get more training data for TEKNOFEST judges
"""

import os
import json
import time
import requests
from typing import List, Dict
import random
from datetime import datetime

ELEVENLABS_API_KEY = "sk_61bdd16dbc21a3820bfdb0601dc18db053a04ea7a8d77462"

class FastTTSExpander:
    def __init__(self):
        self.api_key = ELEVENLABS_API_KEY
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        # Check ACTUAL audio files that exist
        self.already_voiced = set()
        self.output_dir = "data/tts_audio_final"
        
        # Extract conversation IDs from existing audio files
        if os.path.exists(self.output_dir):
            for file in os.listdir(self.output_dir):
                if file.endswith('.mp3'):
                    # Extract conv_id from filename pattern: {conv_id}_turn_{X}.mp3
                    parts = file.replace('.mp3', '').rsplit('_turn_', 1)
                    if len(parts) == 2:
                        conv_id = parts[0]
                        self.already_voiced.add(conv_id)
        
        print(f"📊 Found {len(self.already_voiced)} conversations already voiced")
        
        # Turkish voices for variety
        self.voices = [
            "pNInz6obpgDQGcFmaJgB",  # Adam
            "VR6AewLTigWG4xSOukaG",  # Elli  
            "yoZ06aMxZJJ28mfd3POQ",  # Josh
            "21m00Tcm4TlvDq8ikWAM",  # Rachel
            "MF3mGyEYCl7XYWbV9V6O",  # Emily
            "XB0fDUnXU5powFXDhCwa",  # Charlotte
            "pqHfZKP75CvOlQylNhV4",  # Bill
            "N2lVS1w4EtoT3dr4eOWO",  # Callum
            "IKne3meq5aSn9XLyUdCD",  # Charlie
            "JBFqnCBsd6RMkjVDRZzb",  # George
        ]
        
        # Output dir already set in __init__
        os.makedirs(self.output_dir, exist_ok=True)
    
    def find_new_conversations(self, target_count: int = 50) -> List[Dict]:
        """Find new conversations to voice"""
        
        new_convs = []
        datasets = [
            "data/flash_heavy_dataset",
            "data/varied_dataset/conversations",
            "data/smart_flash_dataset",
            "data/correct_flash_dataset"
        ]
        
        for dataset_dir in datasets:
            if not os.path.exists(dataset_dir):
                continue
                
            for file in os.listdir(dataset_dir):
                if not file.endswith('.json'):
                    continue
                    
                file_path = os.path.join(dataset_dir, file)
                
                try:
                    with open(file_path, 'r') as f:
                        conv = json.load(f)
                    
                    # Skip if already voiced
                    conv_id = conv.get('id', conv.get('conversation_id', file.replace('.json', '')))
                    if conv_id in self.already_voiced:
                        continue
                    
                    # Double-check by looking for any existing audio files
                    test_audio_path = f"{self.output_dir}/{conv_id}_turn_1.mp3"
                    if os.path.exists(test_audio_path):
                        print(f"   ⚠️ Skipping {conv_id} - audio already exists")
                        self.already_voiced.add(conv_id)  # Add to set for future checks
                        continue
                    
                    # Check if has customer turns
                    customer_turns = conv.get('customer_turns_for_tts', conv.get('customer_turns', []))
                    if not customer_turns:
                        continue
                    
                    # Calculate char count
                    char_count = sum(len(turn.get('text', '')) for turn in customer_turns)
                    
                    if char_count > 0:
                        new_convs.append({
                            'path': file_path,
                            'id': conv_id,
                            'chars': char_count,
                            'turns': len(customer_turns),
                            'data': conv
                        })
                        
                        if len(new_convs) >= target_count:
                            break
                except:
                    continue
            
            if len(new_convs) >= target_count:
                break
        
        # Sort by diversity (different char counts = different scenarios)
        new_convs.sort(key=lambda x: x['chars'])
        
        return new_convs[:target_count]
    
    def text_to_speech(self, text: str, voice_id: str) -> bytes:
        """Generate TTS with Flash v2.5 (cheapest and fastest)"""
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        data = {
            "text": text,
            "model_id": "eleven_flash_v2_5",  # 0.5 credits per char
            "language_code": "tr",
            "voice_settings": {
                "stability": 0.6,
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
    
    def generate_batch(self, conversations: List[Dict]):
        """Generate TTS for a batch of conversations"""
        
        total_chars = sum(c['chars'] for c in conversations)
        print(f"\n🎯 FAST TTS GENERATION")
        print(f"   Conversations: {len(conversations)}")
        print(f"   Total characters: {total_chars:,}")
        print(f"   Credits needed: {total_chars // 2:,}")
        print(f"   Estimated time: {len(conversations) * 10} seconds")
        
        generated = []
        
        for i, conv_info in enumerate(conversations):
            conv = conv_info['data']
            conv_id = conv_info['id']
            
            # Get consistent voice per conversation
            voice_id = self.voices[hash(conv_id) % len(self.voices)]
            
            # Generate audio for customer turns
            customer_turns = conv.get('customer_turns_for_tts', conv.get('customer_turns', []))
            audio_files = []
            
            for j, turn in enumerate(customer_turns):
                text = turn.get('text', '')
                
                if not text:
                    continue
                
                # Generate audio using EXACT same pattern as original
                audio = self.text_to_speech(text, voice_id)
                if audio:
                    # Use j+1 for turn number, exactly like the working script
                    filename = f"{self.output_dir}/{conv_id}_turn_{j+1}.mp3"
                    with open(filename, 'wb') as f:
                        f.write(audio)
                    audio_files.append(filename)
                
                time.sleep(0.2)  # Rate limit (faster than before)
            
            generated.append({
                'id': conv_id,
                'path': conv_info['path'],
                'audio_files': audio_files,
                'chars': conv_info['chars']
            })
            
            print(f"   [{i+1}/{len(conversations)}] {conv_id}: {len(audio_files)} audio files")
        
        return generated
    
    def save_expanded_selection(self, new_conversations: List[Dict]):
        """Save the expanded selection with full tracking"""
        
        # Load original selection
        with open("data/selected_for_tts.json", 'r') as f:
            original_selection = json.load(f)
        
        # Create new expanded selection
        expanded = {
            "metadata": {
                "total_selected": len(original_selection['conversations']) + len(new_conversations),
                "original_count": len(original_selection['conversations']),
                "new_count": len(new_conversations),
                "total_chars": original_selection['metadata'].get('total_chars', 0)
            },
            "conversations": original_selection['conversations'].copy()
        }
        
        # Add new conversations with full tracking
        for conv in new_conversations:
            # Extract dataset name from path
            dataset = 'unknown'
            if 'flash_heavy' in conv['path']:
                dataset = 'flash_heavy_dataset'
            elif 'varied_dataset' in conv['path']:
                dataset = 'varied_dataset'
            elif 'smart_flash' in conv['path']:
                dataset = 'smart_flash_dataset'
            elif 'correct_flash' in conv['path']:
                dataset = 'correct_flash_dataset'
            
            expanded['conversations'].append({
                'path': conv['path'],
                'id': conv['id'],
                'chars': conv['chars'],
                'score': 200,  # Default score
                'dataset': dataset,
                'audio_files': conv.get('audio_files', []),
                'generated_at': time.strftime('%Y-%m-%d %H:%M:%S')
            })
            expanded['metadata']['total_chars'] += conv['chars']
        
        # Save expanded selection
        with open("data/expanded_selection.json", 'w') as f:
            json.dump(expanded, f, indent=2, ensure_ascii=False)
        
        # Also save a backup of just the new ones
        new_only = {
            "metadata": {
                "count": len(new_conversations),
                "chars": sum(c['chars'] for c in new_conversations),
                "generated_at": time.strftime('%Y-%m-%d %H:%M:%S')
            },
            "conversations": new_conversations
        }
        
        with open("data/new_voiced_batch.json", 'w') as f:
            json.dump(new_only, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ EXPANDED SELECTION SAVED")
        print(f"   Total conversations: {expanded['metadata']['total_selected']}")
        print(f"   Original: {expanded['metadata']['original_count']}")
        print(f"   New: {expanded['metadata']['new_count']}")
        print(f"   Total characters: {expanded['metadata']['total_chars']:,}")
        print(f"   Files saved:")
        print(f"     - data/expanded_selection.json (all conversations)")
        print(f"     - data/new_voiced_batch.json (just new ones)")

def main(auto_confirm=False):
    """Main function to expand dataset FAST"""
    
    generator = FastTTSExpander()
    
    # Find new conversations to voice
    print("🔍 Finding new conversations to voice...")
    new_convs = generator.find_new_conversations(target_count=50)
    
    if not new_convs:
        print("❌ No new conversations found!")
        return
    
    print(f"📊 Found {len(new_convs)} new conversations")
    
    # Show sample of what will be voiced
    print("\n📝 Sample conversations to voice:")
    for conv in new_convs[:5]:
        print(f"   - {conv['id']} ({conv['chars']} chars)")
    
    # Ask for confirmation
    total_chars = sum(c['chars'] for c in new_convs)
    print(f"\n💰 This will use approximately {total_chars // 2:,} credits")
    
    if not auto_confirm:
        print(f"   Continue? (y/n): ", end='')
        try:
            if input().lower() != 'y':
                print("❌ Cancelled")
                return
        except EOFError:
            print("\n⚠️ Running in non-interactive mode, proceeding...")
            auto_confirm = True
    
    # Generate TTS
    generated = generator.generate_batch(new_convs)
    
    # Save expanded selection
    generator.save_expanded_selection(generated)
    
    print(f"\n🎉 DONE! Generated {len(generated)} new conversations")
    print(f"   Total audio files: {sum(len(g['audio_files']) for g in generated)}")
    print(f"   Ready to update training dataset!")

if __name__ == "__main__":
    main()