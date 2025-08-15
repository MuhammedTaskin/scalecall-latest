#!/usr/bin/env python3
"""
EMOTION-AWARE TRAINING DATASET CREATOR FOR TEKNOFEST 2025
=========================================================

Maps emotional metadata from original conversation JSONs to training data,
creating an enhanced dataset that teaches Gemma 3N to understand emotional
context from text annotations instead of audio processing.

Key Innovation:
- Injects voice characteristics (emotion, pace, dialect) into text input
- Model learns to detect emotional cues and respond appropriately
- No fake audio processing needed - real emotional context training
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict

class EmotionAwareDatasetCreator:
    """Creates emotion-aware training dataset for Turkish telco AI"""
    
    def __init__(self):
        self.emotion_mapping = {}  # Maps audio file to emotional metadata
        self.enhanced_examples = []
        self.stats = {
            'total_examples': 0,
            'emotions_found': defaultdict(int),
            'pace_distribution': defaultdict(int),
            'dialect_markers': set(),
            'missing_metadata': 0
        }
    
    def extract_conversation_id_from_audio(self, audio_path: str) -> tuple:
        """Extract conversation ID and turn from audio path
        Example: data/tts_audio_final/flash_heavy_0174_turn_001.mp3
        Returns: ('flash_heavy_0174', 'turn_001')
        """
        filename = Path(audio_path).stem
        match = re.match(r'(.+?)_(turn_\d+)', filename)
        if match:
            return match.group(1), match.group(2)
        return None, None
    
    def load_conversation_metadata(self, conv_file: str) -> Dict[str, Any]:
        """Load emotional metadata from original conversation JSON"""
        with open(conv_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        metadata = {}
        
        # Extract customer turns with emotional data
        for turn in data.get('customer_turns_for_tts', []):
            turn_id = turn.get('turn_id')
            if turn_id:
                metadata[turn_id] = {
                    'emotion': turn.get('emotion', 'neutral'),
                    'pace': turn.get('pace', 'medium'),
                    'dialect_markers': turn.get('dialect_markers', []),
                    'background_context': turn.get('background_context', ''),
                    'text': turn.get('text', '')
                }
        
        # Add conversation-level metadata
        metadata['conversation'] = {
            'customer_profile': data.get('customer_profile', 'unknown'),
            'region': data.get('region', 'unknown'),
            'complexity': data.get('complexity', 'medium'),
            'emotional_journey': data.get('metadata', {}).get('emotional_journey', []),
            'traits': data.get('metadata', {}).get('traits', [])
        }
        
        return metadata
    
    def build_emotion_mapping(self, selected_conversations: str):
        """Build mapping of audio files to emotional metadata"""
        print("🔍 Building emotion mapping from conversation files...")
        
        with open(selected_conversations, 'r') as f:
            selection_data = json.load(f)
        
        for conv_info in selection_data['conversations']:
            conv_path = conv_info['path']
            conv_id = conv_info['id']
            
            if not os.path.exists(conv_path):
                print(f"⚠️ Missing file: {conv_path}")
                continue
            
            # Load emotional metadata
            metadata = self.load_conversation_metadata(conv_path)
            
            # Map each turn's audio to its emotional data
            for turn_id, turn_data in metadata.items():
                if turn_id != 'conversation':
                    # Create audio filename pattern
                    audio_pattern = f"{conv_id}_{turn_id}"
                    self.emotion_mapping[audio_pattern] = {
                        **turn_data,
                        'conversation_metadata': metadata['conversation']
                    }
        
        print(f"✅ Mapped {len(self.emotion_mapping)} audio files to emotional metadata")
    
    def create_emotion_context_string(self, emotion_data: Dict) -> str:
        """Create a text representation of emotional context"""
        parts = []
        
        # Add primary emotion
        emotion = emotion_data.get('emotion', 'neutral')
        parts.append(f"Duygu: {emotion}")
        
        # Add speaking pace
        pace = emotion_data.get('pace', 'medium')
        pace_map = {'fast': 'hızlı', 'medium': 'normal', 'slow': 'yavaş'}
        parts.append(f"Konuşma hızı: {pace_map.get(pace, pace)}")
        
        # Add customer profile if available
        if 'conversation_metadata' in emotion_data:
            conv_meta = emotion_data['conversation_metadata']
            if isinstance(conv_meta, dict):
                profile = conv_meta.get('customer_profile', '')
                if profile and isinstance(profile, str):
                    profile_map = {
                        'student_abroad': 'yurtdışında öğrenci',
                        'elderly': 'yaşlı',
                        'business': 'iş insanı',
                        'tech_savvy': 'teknoloji meraklısı',
                        'frustrated_regular': 'sık arayan müşteri'
                    }
                    parts.append(f"Profil: {profile_map.get(profile, profile)}")
                
                # Add customer traits
                traits = conv_meta.get('traits', [])
                if traits and isinstance(traits, list):
                    trait_map = {
                        'anxious': 'endişeli',
                        'budget_conscious': 'fiyat duyarlı',
                        'tech_savvy': 'teknoloji bilen',
                        'patient': 'sabırlı',
                        'impatient': 'sabırsız',
                        'confused': 'kafası karışık'
                    }
                    mapped_traits = [trait_map.get(t, t) for t in traits[:2] if isinstance(t, str)]
                    if mapped_traits:
                        parts.append(f"Özellikler: {', '.join(mapped_traits)}")
        
        # Add dialect markers if present
        dialect_markers = emotion_data.get('dialect_markers', [])
        if dialect_markers and isinstance(dialect_markers, list) and len(dialect_markers) > 0:
            if dialect_markers[0] != 'neutral':
                parts.append(f"Aksent: {dialect_markers[0]}")
        
        return f"[{' | '.join(parts)}]"
    
    def enhance_training_example(self, example: Dict) -> Dict:
        """Enhance a training example with emotional context"""
        audio_path = example.get('audio', '')
        
        # Extract conversation and turn IDs
        conv_id, turn_id = self.extract_conversation_id_from_audio(audio_path)
        
        if not conv_id or not turn_id:
            self.stats['missing_metadata'] += 1
            return example  # Return unchanged if can't extract IDs
        
        # Look up emotional metadata
        audio_key = f"{conv_id}_{turn_id}"
        emotion_data = None
        
        # Try exact match first
        if audio_key in self.emotion_mapping:
            emotion_data = self.emotion_mapping[audio_key]
        else:
            # Try partial matches (handle variations)
            for key, data in self.emotion_mapping.items():
                if conv_id in key and turn_id in key:
                    emotion_data = data
                    break
        
        if not emotion_data:
            self.stats['missing_metadata'] += 1
            return example  # Return unchanged if no metadata found
        
        # Create emotion context string
        emotion_context = self.create_emotion_context_string(emotion_data)
        
        # Update statistics
        self.stats['emotions_found'][emotion_data.get('emotion', 'neutral')] += 1
        self.stats['pace_distribution'][emotion_data.get('pace', 'medium')] += 1
        
        # Enhance the context with emotional information
        enhanced_context = example.get('context', '')
        
        # Find where customer text starts and inject emotion context
        if 'Müşteri:' in enhanced_context:
            # Split and inject emotion context before customer text
            parts = enhanced_context.split('Müşteri:', 1)
            if len(parts) == 2:
                enhanced_context = f"{parts[0]}Müşteri {emotion_context}: {parts[1]}"
        elif enhanced_context == "":
            # First turn - add emotion context at the beginning
            enhanced_context = f"Müşteri {emotion_context} ile konuşmaya başlıyor."
        
        # Create enhanced example - KEEP OUTPUT EXACTLY THE SAME
        enhanced_example = {
            'audio': audio_path,
            'context': enhanced_context,
            'output': example['output']  # DO NOT MODIFY OUTPUT AT ALL
        }
        
        return enhanced_example
    
    def process_training_data(self, input_file: str, output_file: str):
        """Process existing training data and add emotional context"""
        print(f"\n📝 Processing training data: {input_file}")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                
                try:
                    example = json.loads(line)
                    enhanced = self.enhance_training_example(example)
                    self.enhanced_examples.append(enhanced)
                    self.stats['total_examples'] += 1
                    
                    if line_num % 100 == 0:
                        print(f"   Processed {line_num} examples...")
                        
                except json.JSONDecodeError as e:
                    print(f"⚠️ Error parsing line {line_num}: {e}")
        
        # Write enhanced dataset
        print(f"\n💾 Writing enhanced dataset to: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            for example in self.enhanced_examples:
                # Write exactly as is - audio, context (enhanced), output (unchanged)
                f.write(json.dumps(example, ensure_ascii=False) + '\n')
        
        print(f"✅ Created {len(self.enhanced_examples)} emotion-aware training examples")
    
    def print_statistics(self):
        """Print dataset statistics"""
        print("\n" + "="*60)
        print("📊 EMOTION-AWARE DATASET STATISTICS")
        print("="*60)
        print(f"Total examples: {self.stats['total_examples']}")
        print(f"Examples with emotions: {self.stats['total_examples'] - self.stats['missing_metadata']}")
        print(f"Missing metadata: {self.stats['missing_metadata']}")
        
        print("\n🎭 Emotion Distribution:")
        for emotion, count in sorted(self.stats['emotions_found'].items(), key=lambda x: x[1], reverse=True):
            print(f"   {emotion}: {count}")
        
        print("\n⚡ Pace Distribution:")
        for pace, count in sorted(self.stats['pace_distribution'].items(), key=lambda x: x[1], reverse=True):
            print(f"   {pace}: {count}")
        
        print("\n✨ Sample Enhanced Context:")
        if self.enhanced_examples:
            sample = self.enhanced_examples[0]
            print(f"   Original: {sample['audio']}")
            print(f"   Context: {sample['context'][:200]}...")

def main():
    """Main execution"""
    creator = EmotionAwareDatasetCreator()
    
    # Build emotion mapping from selected conversations
    selected_file = 'data/selected_for_tts.json'
    creator.build_emotion_mapping(selected_file)
    
    # Process training data
    input_file = '/Users/ozai/Downloads/gemma3n_autonomous_training.jsonl'
    output_file = 'data/gemma3n_emotion_aware_training.jsonl'
    
    creator.process_training_data(input_file, output_file)
    creator.print_statistics()
    
    print("\n🏆 Ready for TEKNOFEST 2025!")
    print("   Model will learn emotional context from text annotations")
    print("   No fake audio processing needed!")

if __name__ == "__main__":
    main()