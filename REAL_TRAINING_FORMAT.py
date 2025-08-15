#!/usr/bin/env python3
"""
THE ACTUAL TRAINING FORMAT FOR GEMMA 3N
No bullshit, just what works
"""

import json
from pathlib import Path
from typing import Dict, List

def create_training_format():
    """
    Create the REAL training format that Gemma 3N expects
    """
    
    # Load our standardized conversations
    with open('data/selected_for_tts.json', 'r') as f:
        selected = json.load(f)
    
    training_examples = []
    
    for conv_info in selected['conversations']:
        conv_path = Path(conv_info['path'])
        if not conv_path.exists():
            continue
            
        with open(conv_path, 'r') as f:
            conv = json.load(f)
        
        # Build examples from conversation turns
        context = []
        
        customer_turns = conv.get('customer_turns_for_tts', [])
        agent_responses = conv.get('agent_responses', [])
        
        # Map turn numbers to content
        turn_map = {}
        
        # Add customer turns
        for customer_turn in customer_turns:
            turn_id = customer_turn.get('turn_id')
            if turn_id:
                turn_num = int(turn_id.split('_')[-1])
                turn_map[turn_num] = {
                    'type': 'customer',
                    'text': customer_turn.get('text', ''),
                    'audio': f"data/tts_audio_final/{conv['id']}_turn_{turn_num}.mp3"
                }
        
        # Add agent turns
        for agent_turn in agent_responses:
            turn_id = agent_turn.get('turn_id')
            if turn_id:
                try:
                    turn_num = int(turn_id.split('_')[-1])
                    turn_map[turn_num] = {
                        'type': 'agent',
                        'agent': agent_turn.get('agent_persona'),
                        'text': agent_turn.get('text', ''),
                        'tools': agent_turn.get('tools_triggered', [])
                    }
                except ValueError:
                    # Skip malformed turn IDs
                    continue
        
        # Create training examples from turn sequences
        sorted_turns = sorted(turn_map.keys())
        
        for i, turn_num in enumerate(sorted_turns):
            current_turn = turn_map[turn_num]
            
            # Only create examples for customer turns (they have audio)
            if current_turn['type'] == 'customer':
                # Find the next agent response
                next_agent_turn = None
                for j in range(i+1, len(sorted_turns)):
                    if turn_map[sorted_turns[j]]['type'] == 'agent':
                        next_agent_turn = turn_map[sorted_turns[j]]
                        break
                
                if next_agent_turn:
                    # Create the training example
                    example = {
                        # INPUT
                        "audio": current_turn['audio'],
                        "context": format_context(context),
                        
                        # OUTPUT (what model should generate)
                        "agent": next_agent_turn['agent'],
                        "tools": next_agent_turn['tools'],
                        "response": next_agent_turn['text']
                    }
                    
                    training_examples.append(example)
            
            # Add to context for next turn
            context.append(current_turn)
    
    return training_examples

def format_context(context: List[Dict]) -> str:
    """
    Format conversation context as a simple string
    """
    if not context:
        return ""
    
    formatted = []
    for turn in context[-4:]:  # Last 4 turns only (memory limit)
        if turn['type'] == 'customer':
            formatted.append(f"Müşteri: {turn['text']}")
        elif turn['type'] == 'agent':
            agent = turn.get('agent', 'Agent')
            text = turn.get('text', '')
            tools = turn.get('tools', [])
            
            formatted.append(f"{agent}: {text}")
            if tools:
                formatted.append(f"[Araçlar: {', '.join(tools)}]")
    
    return "\n".join(formatted)

def create_gemma_training_file():
    """
    Create the actual JSONL file for Gemma 3N training
    """
    
    training_examples = create_training_format()
    
    # Convert to Gemma's expected format
    gemma_format = []
    
    for ex in training_examples:
        # The format Gemma 3N expects for fine-tuning
        training_item = {
            "instruction": f"Sen bir Türk telekom çağrı merkezi temsilcisisin. Müşteri ses kaydını dinle ve uygun yanıtı ver.\n\nGeçmiş konuşma:\n{ex['context']}",
            "input": ex['audio'],  # Audio file path
            "output": json.dumps({
                "agent": ex['agent'],
                "tools": ex['tools'],
                "response": ex['response']
            }, ensure_ascii=False)
        }
        
        gemma_format.append(training_item)
    
    # Save as JSONL
    output_path = Path('data/gemma3n_real_training.jsonl')
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in gemma_format:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"✅ Created {len(gemma_format)} training examples")
    print(f"📁 Saved to: {output_path}")
    
    # Show sample
    if gemma_format:
        print("\n📝 Sample training item:")
        sample = gemma_format[0]
        print(f"Instruction: {sample['instruction'][:100]}...")
        print(f"Input (audio): {sample['input']}")
        print(f"Output: {sample['output'][:100]}...")
    
    return output_path

def verify_training_data():
    """
    Verify the training data is valid
    """
    
    with open('data/gemma3n_real_training.jsonl', 'r') as f:
        lines = f.readlines()
    
    valid = 0
    invalid = 0
    
    for line in lines:
        try:
            item = json.loads(line)
            
            # Check required fields
            if 'instruction' in item and 'input' in item and 'output' in item:
                # Check audio file exists
                audio_path = Path(item['input'])
                if audio_path.exists():
                    valid += 1
                else:
                    invalid += 1
                    print(f"❌ Missing audio: {audio_path}")
            else:
                invalid += 1
                
        except:
            invalid += 1
    
    print(f"\n📊 Validation Results:")
    print(f"  Valid: {valid}")
    print(f"  Invalid: {invalid}")
    
    return valid > 0 and invalid == 0

if __name__ == "__main__":
    print("🎯 CREATING REAL TRAINING FORMAT")
    print("=" * 60)
    
    # Create the training file
    training_file = create_gemma_training_file()
    
    # Verify it's valid
    is_valid = verify_training_data()
    
    if is_valid:
        print("\n✅ TRAINING DATA READY!")
        print("Next: Upload to Colab and train with Unsloth")
    else:
        print("\n⚠️ Some issues found, check the data")