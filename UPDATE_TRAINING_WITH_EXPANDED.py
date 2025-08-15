#!/usr/bin/env python3
"""
UPDATE TRAINING DATASET WITH EXPANDED CONVERSATIONS
After voicing more files, this updates the training dataset
"""

import json
import os
from pathlib import Path

def update_training_dataset():
    """Update training dataset with newly voiced conversations"""
    
    # Check which selection file to use
    if os.path.exists("data/expanded_selection.json"):
        print("📊 Using expanded selection with new conversations")
        selection_file = "data/expanded_selection.json"
    else:
        print("📊 Using original selection")
        selection_file = "data/selected_for_tts.json"
    
    with open(selection_file, 'r') as f:
        selection = json.load(f)
    
    print(f"   Conversations: {selection['metadata'].get('total_selected', len(selection['conversations']))}")
    if 'original_count' in selection['metadata']:
        print(f"   Original: {selection['metadata']['original_count']}")
        print(f"   New: {selection['metadata']['new_count']}")
    
    # Now run the autonomous dataset creator with the expanded selection
    print("\n🔄 Regenerating training dataset...")
    
    # Import and run the creator
    import CREATE_AUTONOMOUS_TRAINING_DATASET
    
    # Update the creator to use the expanded selection
    generator = CREATE_AUTONOMOUS_TRAINING_DATASET.AutonomousDatasetGenerator()
    
    # Override the selection
    generator.selection = selection
    
    # Process all conversations
    generator.process_all_conversations()
    
    # Get stats
    print(f"\n📊 FINAL STATISTICS:")
    print(f"   Training examples: {len(generator.training_examples)}")
    print(f"   From conversations: {selection['metadata'].get('total_selected', len(selection['conversations']))}")
    print(f"   Average examples per conversation: {len(generator.training_examples) / len(selection['conversations']):.1f}")
    
    # Save an enhanced version with metadata
    enhanced_output = {
        "metadata": {
            "total_examples": len(generator.training_examples),
            "total_conversations": len(selection['conversations']),
            "original_conversations": selection['metadata'].get('original_count', 76),
            "new_conversations": selection['metadata'].get('new_count', 0),
            "generated_at": generator.generated_at,
            "for_competition": "TEKNOFEST 2025"
        },
        "examples": generator.training_examples
    }
    
    # Save as both JSONL (for training) and JSON (for inspection)
    with open("data/gemma3n_expanded_training.jsonl", 'w') as f:
        for example in generator.training_examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    
    with open("data/training_metadata.json", 'w') as f:
        json.dump(enhanced_output['metadata'], f, indent=2)
    
    print(f"\n✅ TRAINING DATASET UPDATED!")
    print(f"   Files created:")
    print(f"     - data/gemma3n_expanded_training.jsonl (training data)")
    print(f"     - data/training_metadata.json (statistics)")
    
    # Show impressive stats for competition
    print(f"\n🏆 COMPETITION READY:")
    print(f"   • {len(generator.training_examples)} multimodal training examples")
    print(f"   • {len(selection['conversations'])} unique conversations")
    print(f"   • {selection['metadata'].get('total_chars', 0):,} characters of Turkish speech")
    print(f"   • 5 agent types with 21 tool orchestrations")
    print(f"   • Context-aware conversation flows with handoffs")

if __name__ == "__main__":
    update_training_dataset()