#!/usr/bin/env python3
"""
RICH METADATA TRAINING DATASET CREATOR FOR TEKNOFEST 2025
=========================================================

Replaces audio paths with complete emotional/voice metadata from original
conversation JSONs. The model learns from rich metadata instead of audio files.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any

class RichMetadataDatasetCreator:
    """Creates training dataset with full metadata instead of audio paths"""
    
    def __init__(self):
        self.conversation_cache = {}  # Cache loaded conversations
        self.enhanced_examples = []
        self.stats = {
            'total_examples': 0,
            'metadata_found': 0,
            'metadata_missing': 0,
            'unique_emotions': set(),
            'unique_profiles': set()
        }
    
    def extract_ids_from_audio_path(self, audio_path: str) -> tuple:
        """Extract conversation ID and turn ID from audio path
        Example: data/tts_audio_final/flash_heavy_0174_turn_001.mp3
        Returns: ('flash_heavy_0174', 'turn_001')
        """
        filename = Path(audio_path).stem
        match = re.match(r'(.+?)_(turn_\d+)', filename)
        if match:
            return match.group(1), match.group(2)
        return None, None
    
    def load_conversation(self, conv_id: str, selected_data: Dict) -> Optional[Dict]:
        """Load conversation JSON file based on conversation ID"""
        # Check cache first
        if conv_id in self.conversation_cache:
            return self.conversation_cache[conv_id]
        
        # Find the conversation file path
        for conv_info in selected_data['conversations']:
            if conv_info['id'] == conv_id:
                conv_path = conv_info['path']
                if os.path.exists(conv_path):
                    with open(conv_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.conversation_cache[conv_id] = data
                        return data
        return None
    
    def extract_turn_metadata(self, conv_data: Dict, turn_id: str) -> Optional[Dict]:
        """Extract complete metadata for a specific turn"""
        # Look for the turn in customer_turns_for_tts
        for turn in conv_data.get('customer_turns_for_tts', []):
            if turn.get('turn_id') == turn_id:
                # Extract all metadata for this turn
                metadata = {
                    'text': turn.get('text', ''),
                    'emotion': turn.get('emotion', 'neutral'),
                    'pace': turn.get('pace', 'medium'),
                    'dialect_markers': turn.get('dialect_markers', []),
                    'background_context': turn.get('background_context', ''),
                    # Add conversation-level metadata
                    'customer_profile': conv_data.get('customer_profile', ''),
                    'region': conv_data.get('region', ''),
                    'complexity': conv_data.get('complexity', 'medium'),
                    'conversation_dynamic': conv_data.get('conversation_dynamic', ''),
                    'primary_issue': conv_data.get('primary_issue', ''),
                    'secondary_issue': conv_data.get('secondary_issue', ''),
                    'traits': conv_data.get('metadata', {}).get('traits', []),
                    'emotional_journey': conv_data.get('metadata', {}).get('emotional_journey', [])
                }
                
                # Add dialect info if available
                if 'dialect_info' in conv_data:
                    metadata['dialect_info'] = conv_data['dialect_info']
                
                return metadata
        
        return None
    
    def transform_example(self, example: Dict, selected_data: Dict) -> Dict:
        """Transform a training example by replacing audio path with metadata"""
        audio_path = example.get('audio', '')
        
        # Extract conversation and turn IDs
        conv_id, turn_id = self.extract_ids_from_audio_path(audio_path)
        
        if not conv_id or not turn_id:
            # Keep original example if we can't extract IDs (agent responses without audio)
            self.stats['metadata_missing'] += 1
            return example
        
        # Load conversation data
        conv_data = self.load_conversation(conv_id, selected_data)
        if not conv_data:
            # Keep original example if conversation not found
            self.stats['metadata_missing'] += 1
            return example
        
        # Extract turn metadata
        turn_metadata = self.extract_turn_metadata(conv_data, turn_id)
        if not turn_metadata:
            # Keep original example if turn metadata not found
            self.stats['metadata_missing'] += 1
            return example
        
        # Update statistics
        self.stats['metadata_found'] += 1
        emotion = turn_metadata.get('emotion', 'neutral')
        profile = turn_metadata.get('customer_profile', '')
        if isinstance(emotion, str):
            self.stats['unique_emotions'].add(emotion)
        if isinstance(profile, str):
            self.stats['unique_profiles'].add(profile)
        
        # Create new example with metadata as input
        new_example = {
            'input': turn_metadata,  # Full metadata instead of audio path
            'context': example['context'],  # Keep original context
            'output': example['output']  # Keep output EXACTLY the same
        }
        
        return new_example
    
    def process_dataset(self, input_file: str, output_file: str, selected_file: str):
        """Process the dataset and replace audio paths with metadata"""
        print(f"📝 Processing: {input_file}")
        
        # Load selected conversations metadata
        with open(selected_file, 'r') as f:
            selected_data = json.load(f)
        
        # Process each training example
        with open(input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                
                try:
                    example = json.loads(line)
                    transformed = self.transform_example(example, selected_data)
                    
                    # Always append (either transformed or original)
                    self.enhanced_examples.append(transformed)
                    self.stats['total_examples'] += 1
                    
                    if line_num % 100 == 0:
                        print(f"   Processed {line_num} examples...")
                        
                except json.JSONDecodeError as e:
                    print(f"⚠️ Error parsing line {line_num}: {e}")
        
        # Write enhanced dataset
        print(f"\n💾 Writing to: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            for example in self.enhanced_examples:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')
        
        print(f"✅ Created {len(self.enhanced_examples)} examples with rich metadata")
    
    def print_statistics(self):
        """Print processing statistics"""
        print("\n" + "="*60)
        print("📊 RICH METADATA DATASET STATISTICS")
        print("="*60)
        print(f"Total examples: {self.stats['total_examples']}")
        print(f"With metadata: {self.stats['metadata_found']}")
        print(f"Missing metadata: {self.stats['metadata_missing']}")
        print(f"Unique emotions: {len(self.stats['unique_emotions'])}")
        print(f"Unique profiles: {len(self.stats['unique_profiles'])}")
        
        if self.enhanced_examples:
            print("\n✨ Sample transformed example:")
            sample = self.enhanced_examples[0]
            print(f"Input metadata keys: {list(sample['input'].keys())}")
            print(f"Emotion: {sample['input'].get('emotion')}")
            print(f"Profile: {sample['input'].get('customer_profile')}")
            print(f"Text preview: {sample['input'].get('text', '')[:100]}...")

def main():
    """Main execution"""
    creator = RichMetadataDatasetCreator()
    
    # Process the dataset
    input_file = '/Users/ozai/Downloads/gemma3n_autonomous_training.jsonl'
    output_file = 'data/gemma3n_rich_metadata_training.jsonl'
    selected_file = 'data/selected_for_tts.json'
    
    creator.process_dataset(input_file, output_file, selected_file)
    creator.print_statistics()
    
    print("\n🏆 Dataset ready for TEKNOFEST 2025!")
    print("   Input: Rich emotional/voice metadata")
    print("   Output: Unchanged agent responses")
    print("   No audio files needed for training!")

if __name__ == "__main__":
    main()