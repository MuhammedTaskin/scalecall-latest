"""
Fix Dataset Issues - Clean up the generated data
"""
import json
import re
import random
from typing import Dict, List

def fix_tool_call_formatting(dialog: Dict) -> Dict:
    """Fix malformed tool calls in dialogs."""
    fixed_conversations = []
    
    for turn in dialog["conversations"]:
        if turn["role"] == "assistant":
            new_content = []
            for content in turn["content"]:
                text = content.get("text", "")
                
                # Check if this is supposed to be a tool call but is malformed
                if "tool_call" in text and text.strip() == "":
                    # Skip empty tool calls
                    continue
                elif "tool_call" in text:
                    try:
                        # Validate JSON
                        json.loads(text)
                        new_content.append(content)
                    except json.JSONDecodeError:
                        # Try to fix common issues
                        fixed_text = text.strip()
                        if not fixed_text:
                            continue
                        
                        # Add missing quotes around tool names
                        fixed_text = re.sub(r'"name":(\w+),', r'"name":"\1",', fixed_text)
                        
                        try:
                            json.loads(fixed_text)
                            new_content.append({"type": "text", "text": fixed_text})
                        except json.JSONDecodeError:
                            # If still broken, skip this tool call
                            print(f"Skipping malformed tool call: {text[:50]}...")
                            continue
                else:
                    new_content.append(content)
            
            if new_content:  # Only add turn if it has content
                fixed_conversations.append({
                    "role": turn["role"],
                    "content": new_content
                })
        else:
            fixed_conversations.append(turn)
    
    dialog["conversations"] = fixed_conversations
    return dialog

def add_more_turkish_noise(dialog: Dict) -> Dict:
    """Add more realistic Turkish ASR noise to user inputs."""
    noise_patterns = {
        "eSIM": ["esim", "e sim", "mevsim", "eşim"],
        "paket": ["paketi", "paketim"],
        "değiştirmek": ["degistirmek", "değiştirmek"],
        "çekmiyor": ["cekmiyor", "çekmiyo"],
        "yükseltmek": ["yukseltmek"],
        "düşürmek": ["dusurtmek"]
    }
    
    # Only apply noise to some dialogs (don't over-corrupt)
    if random.random() > 0.3:  # 30% get additional noise
        return dialog
    
    for turn in dialog["conversations"]:
        if turn["role"] == "user":
            for content in turn["content"]:
                text = content.get("text", "")
                if len(text) > 5 and not text.startswith("<tool_result>"):
                    # Apply noise patterns
                    for clean, noisy_options in noise_patterns.items():
                        if clean in text:
                            noisy_version = random.choice(noisy_options)
                            text = text.replace(clean, noisy_version)
                    
                    content["text"] = text
    
    dialog["has_noise"] = True
    return dialog

def clean_dataset_file(input_file: str, output_file: str):
    """Clean a dataset file and save the fixed version."""
    print(f"🧹 Cleaning dataset: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        if input_file.endswith('.jsonl'):
            dialogs = [json.loads(line) for line in f]
        else:
            dialogs = json.load(f)
    
    print(f"📊 Original dialogs: {len(dialogs)}")
    
    fixed_dialogs = []
    skipped_count = 0
    
    for i, dialog in enumerate(dialogs):
        try:
            # Fix tool call formatting
            fixed_dialog = fix_tool_call_formatting(dialog)
            
            # Add Turkish noise (occasionally)
            if random.random() < 0.2:  # 20% get extra noise
                fixed_dialog = add_more_turkish_noise(fixed_dialog)
            
            # Skip dialogs with no conversations
            if not fixed_dialog.get("conversations"):
                skipped_count += 1
                continue
            
            fixed_dialogs.append(fixed_dialog)
            
        except Exception as e:
            print(f"❌ Error fixing dialog {i}: {e}")
            skipped_count += 1
    
    print(f"✅ Fixed dialogs: {len(fixed_dialogs)}")
    print(f"⚠️  Skipped dialogs: {skipped_count}")
    
    # Save fixed dataset
    with open(output_file, 'w', encoding='utf-8') as f:
        if output_file.endswith('.jsonl'):
            for dialog in fixed_dialogs:
                f.write(json.dumps(dialog, ensure_ascii=False) + '\n')
        else:
            json.dump(fixed_dialogs, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Saved cleaned dataset: {output_file}")
    return len(fixed_dialogs)

if __name__ == "__main__":
    import os
    
    data_dir = "data/generated"
    cleaned_dir = "data/cleaned"
    os.makedirs(cleaned_dir, exist_ok=True)
    
    # Clean the main datasets
    datasets_to_clean = [
        "turkish_telco_1000k_train.json",
        "turkish_telco_5000k_train.json", 
        "turkish_telco_20000k_train.json"
    ]
    
    for dataset in datasets_to_clean:
        input_path = f"{data_dir}/{dataset}"
        output_path = f"{cleaned_dir}/{dataset.replace('.json', '_cleaned.json')}"
        
        if os.path.exists(input_path):
            clean_dataset_file(input_path, output_path)
            print("="*60)
        else:
            print(f"❌ File not found: {input_path}")
    
    print("🎯 Dataset cleaning complete! Use files in data/cleaned/ for training.")
