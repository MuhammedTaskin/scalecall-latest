#!/usr/bin/env python3
"""
Convert JSONL training data to CSV for Excel
"""

import json
import csv
from pathlib import Path

def jsonl_to_csv(jsonl_path, csv_path):
    """Convert JSONL file to CSV that can be opened in Excel"""
    
    print(f"📖 Reading JSONL file: {jsonl_path}")
    
    # Read all records
    records = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                
                # Flatten the record for CSV
                flat_record = {
                    'line_number': line_num,
                    'has_metadata': 'input' in record and isinstance(record['input'], dict),
                    'has_audio': 'audio' in record
                }
                
                # Handle metadata format (first 418 examples)
                if 'input' in record and isinstance(record['input'], dict):
                    metadata = record['input']
                    flat_record.update({
                        'text': metadata.get('text', '')[:200],  # Truncate for readability
                        'emotion': metadata.get('emotion', ''),
                        'pace': metadata.get('pace', ''),
                        'customer_profile': str(metadata.get('customer_profile', '')),
                        'region': metadata.get('region', ''),
                        'primary_issue': metadata.get('primary_issue', ''),
                        'secondary_issue': metadata.get('secondary_issue', ''),
                        'traits': ', '.join(metadata.get('traits', []) if isinstance(metadata.get('traits'), list) else []),
                        'background_context': metadata.get('background_context', ''),
                        'complexity': metadata.get('complexity', ''),
                        'audio_path': ''
                    })
                
                # Handle audio format (last 186 examples)
                elif 'audio' in record:
                    flat_record.update({
                        'text': record.get('context', '')[:200],  # Truncate
                        'emotion': '',
                        'pace': '',
                        'customer_profile': '',
                        'region': '',
                        'primary_issue': '',
                        'secondary_issue': '',
                        'traits': '',
                        'background_context': '',
                        'complexity': '',
                        'audio_path': record.get('audio', '')
                    })
                else:
                    # Fallback
                    flat_record.update({
                        'text': record.get('context', '')[:200],
                        'emotion': '',
                        'pace': '',
                        'customer_profile': '',
                        'region': '',
                        'primary_issue': '',
                        'secondary_issue': '',
                        'traits': '',
                        'background_context': '',
                        'complexity': '',
                        'audio_path': ''
                    })
                
                # Add output information
                output = record.get('output', {})
                flat_record.update({
                    'agent': output.get('agent', ''),
                    'tools': ', '.join(output.get('tools', output.get('tools_called', []))),
                    'response': output.get('response', '')[:200]  # Truncate
                })
                
                # Add conversation context
                flat_record['context'] = record.get('context', '')[:200]  # Truncate
                
                records.append(flat_record)
                
            except Exception as e:
                print(f"⚠️ Error on line {line_num}: {e}")
                continue
    
    print(f"✅ Processed {len(records)} records")
    
    # Define column order
    fieldnames = [
        'line_number',
        'has_metadata',
        'has_audio',
        'emotion',
        'pace',
        'customer_profile',
        'traits',
        'text',
        'agent',
        'tools',
        'response',
        'primary_issue',
        'secondary_issue',
        'region',
        'background_context',
        'complexity',
        'audio_path',
        'context'
    ]
    
    # Write to CSV
    print(f"💾 Writing to CSV: {csv_path}")
    
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as csvfile:  # utf-8-sig for Excel compatibility
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    
    print(f"✅ CSV file created successfully!")
    print(f"   Path: {csv_path}")
    print(f"   Rows: {len(records)}")
    print(f"   Can be opened in Excel")
    
    # Print statistics
    print("\n📊 Statistics:")
    metadata_count = sum(1 for r in records if r['has_metadata'])
    audio_count = sum(1 for r in records if r['has_audio'])
    print(f"   With metadata: {metadata_count}")
    print(f"   With audio: {audio_count}")
    
    # Count unique emotions
    emotions = set()
    for r in records:
        if r['emotion']:
            emotions.add(r['emotion'])
    print(f"   Unique emotions: {len(emotions)}")
    
    # Count unique profiles
    profiles = set()
    for r in records:
        if r['customer_profile']:
            profiles.add(r['customer_profile'])
    print(f"   Unique profiles: {len(profiles)}")
    
    # Show emotion distribution
    emotion_counts = {}
    for r in records:
        emotion = r['emotion']
        if emotion:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    print("\n🎭 Top 10 Emotions:")
    sorted_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for emotion, count in sorted_emotions:
        print(f"   {emotion}: {count}")
    
    return records

def main():
    # File paths
    jsonl_path = '/Users/ozai/ozai-space/scalecall/scalecall-latest/data/gemma3n_rich_metadata_training.jsonl'
    csv_path = '/Users/ozai/ozai-space/scalecall/scalecall-latest/data/gemma3n_training_data.csv'
    
    # Convert
    records = jsonl_to_csv(jsonl_path, csv_path)

if __name__ == "__main__":
    main()