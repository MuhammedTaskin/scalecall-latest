#!/usr/bin/env python3
"""
Convert JSONL training data to Excel for review
"""

import json
import pandas as pd
from pathlib import Path

def jsonl_to_excel(jsonl_path, excel_path):
    """Convert JSONL file to Excel with proper formatting"""
    
    print(f"📖 Reading JSONL file: {jsonl_path}")
    
    # Read all records
    records = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                
                # Flatten the record for Excel
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
    
    # Create DataFrame
    df = pd.DataFrame(records)
    
    # Reorder columns for better readability
    column_order = [
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
    
    # Only include columns that exist
    df = df[[col for col in column_order if col in df.columns]]
    
    # Write to Excel with formatting
    print(f"💾 Writing to Excel: {excel_path}")
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # Main data sheet
        df.to_excel(writer, sheet_name='Training Data', index=False)
        
        # Statistics sheet
        stats_data = {
            'Metric': [
                'Total Examples',
                'With Metadata',
                'With Audio Path',
                'Unique Emotions',
                'Unique Profiles',
                'Unique Agents',
                'Most Common Emotion',
                'Most Common Profile',
                'Most Common Agent'
            ],
            'Value': [
                len(df),
                df['has_metadata'].sum(),
                df['has_audio'].sum(),
                df['emotion'].nunique(),
                df['customer_profile'].nunique(),
                df['agent'].nunique(),
                df['emotion'].mode()[0] if not df['emotion'].empty else 'N/A',
                df['customer_profile'].mode()[0] if not df['customer_profile'].empty else 'N/A',
                df['agent'].mode()[0] if not df['agent'].empty else 'N/A'
            ]
        }
        
        stats_df = pd.DataFrame(stats_data)
        stats_df.to_excel(writer, sheet_name='Statistics', index=False)
        
        # Format the Excel file
        workbook = writer.book
        
        # Format main sheet
        worksheet = writer.sheets['Training Data']
        
        # Set column widths
        worksheet.column_dimensions['A'].width = 12  # line_number
        worksheet.column_dimensions['B'].width = 12  # has_metadata
        worksheet.column_dimensions['C'].width = 12  # has_audio
        worksheet.column_dimensions['D'].width = 15  # emotion
        worksheet.column_dimensions['E'].width = 10  # pace
        worksheet.column_dimensions['F'].width = 20  # customer_profile
        worksheet.column_dimensions['G'].width = 30  # traits
        worksheet.column_dimensions['H'].width = 50  # text
        worksheet.column_dimensions['I'].width = 15  # agent
        worksheet.column_dimensions['J'].width = 30  # tools
        worksheet.column_dimensions['K'].width = 50  # response
        
        # Add filters
        worksheet.auto_filter.ref = worksheet.dimensions
        
        # Freeze top row
        worksheet.freeze_panes = 'A2'
    
    print(f"✅ Excel file created successfully!")
    print(f"   Path: {excel_path}")
    print(f"   Sheets: Training Data, Statistics")
    
    return df

def main():
    # File paths
    jsonl_path = '/Users/ozai/ozai-space/scalecall/scalecall-latest/data/gemma3n_rich_metadata_training.jsonl'
    excel_path = '/Users/ozai/ozai-space/scalecall/scalecall-latest/data/gemma3n_training_data.xlsx'
    
    # Convert
    df = jsonl_to_excel(jsonl_path, excel_path)
    
    # Print summary
    print("\n📊 Summary:")
    print(f"   Total rows: {len(df)}")
    print(f"   Columns: {', '.join(df.columns)}")
    
    # Show emotion distribution
    print("\n🎭 Emotion Distribution:")
    emotion_counts = df['emotion'].value_counts().head(10)
    for emotion, count in emotion_counts.items():
        if emotion:  # Skip empty strings
            print(f"   {emotion}: {count}")

if __name__ == "__main__":
    main()