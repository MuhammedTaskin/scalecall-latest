#!/usr/bin/env python3
"""
SYSTEM-INTEGRATED TRAINING FORMAT
Training Gemma 3N to output in a way that ACTUALLY WORKS with the system
"""

import json
from pathlib import Path

# THINK ABOUT THE ACTUAL SYSTEM FLOW:
# 1. Customer speaks (audio)
# 2. Model outputs tool calls to make
# 3. System executes tools
# 4. System provides results back to model
# 5. Model generates final response using those results

# So we need TWO-STEP training OR a format that makes sense

# OPTION 1: Model outputs everything but in LOGICAL order
def create_logical_format_examples():
    """
    Model outputs:
    1. Agent identity
    2. Tools to call (without results)
    3. Expected response template
    4. System fills in the response with actual results
    """
    
    examples = [
        {
            "audio": "data/tts_audio_final/flash_heavy_0174_turn_1.mp3",
            "text": json.dumps({
                "agent": "RouterAgent",
                "action": "verify_user",
                "params": {
                    "tc_no": "${customer_provided_tc}",
                    "mother_maiden_name": "${customer_provided_maiden}"
                },
                "response_template": "Kimliğinizi doğruladım ${customer_name}. Size nasıl yardımcı olabilirim?",
                "on_failure": "Kimlik bilgilerinizi doğrulayamadım. Lütfen tekrar deneyin."
            }, ensure_ascii=False)
        }
    ]
    return examples

# OPTION 2: Model outputs step-by-step instructions
def create_step_by_step_examples():
    """
    Model outputs a sequence of steps for the system to execute
    """
    
    examples = [
        {
            "audio": "data/tts_audio_final/flash_heavy_0174_turn_1.mp3",
            "text": "<plan>\n1. SET agent=RouterAgent\n2. CALL verify_user WITH extracted_tc, extracted_maiden\n3. IF verified THEN SAY 'Kimliğinizi doğruladım, size nasıl yardımcı olabilirim?'\n4. ELSE SAY 'Kimlik doğrulama başarısız, lütfen bilgilerinizi kontrol edin'\n</plan>"
        }
    ]
    return examples

# OPTION 3: REALISTIC - Model outputs intent and system handles execution
def create_realistic_system_format():
    """
    THIS IS WHAT ACTUALLY MAKES SENSE!
    Model outputs intent, system executes and responds
    """
    
    examples = []
    
    # Example 1: Initial verification
    examples.append({
        "audio": "data/tts_audio_final/flash_heavy_0174_turn_1.mp3",
        "model_output": {
            "intent": "verify_and_assist",
            "agent": "RouterAgent", 
            "actions": [
                {
                    "tool": "verify_user",
                    "reason": "Customer needs help, must verify first",
                    "extract_from_audio": ["tc_no", "mother_maiden_name"]
                }
            ],
            "response_strategy": "empathetic_verification",
            "response": "Merhaba, eSIM sorununuz için üzgünüz. Güvenliğiniz için kimlik doğrulaması yapmam gerekiyor."
        }
    })
    
    # Example 2: After verification, route to appropriate agent
    examples.append({
        "audio": "data/tts_audio_final/flash_heavy_0174_turn_2.mp3",
        "model_output": {
            "intent": "route_to_specialist",
            "agent": "RouterAgent",
            "actions": [
                {
                    "tool": "get_customer_status",
                    "reason": "Check customer account status",
                    "use_from_context": ["customer_id"]
                },
                {
                    "tool": "route_to_agent", 
                    "reason": "eSIM issue requires technical support",
                    "params": {
                        "to_agent": "TechAgent",
                        "reason": "eSIM activation problem"
                    }
                }
            ],
            "response": "Kimliğinizi doğruladım. eSIM sorununuz için sizi teknik ekibe yönlendiriyorum."
        }
    })
    
    # Example 3: Technical support handles the issue
    examples.append({
        "audio": "data/tts_audio_final/flash_heavy_0174_turn_3.mp3",
        "model_output": {
            "intent": "resolve_esim_issue",
            "agent": "TechAgent",
            "actions": [
                {
                    "tool": "check_esim_status",
                    "reason": "Diagnose current eSIM state"
                },
                {
                    "tool": "check_device_imei",
                    "reason": "Verify device compatibility"
                },
                {
                    "tool": "reissue_activation_code",
                    "reason": "Generate new activation code",
                    "condition": "if_not_active"
                }
            ],
            "response": "iPhone 14 Pro'nuz eSIM uyumlu. Yeni aktivasyon kodu oluşturup SMS ile gönderdim."
        }
    })
    
    # Convert to training format
    training_data = []
    for ex in examples:
        if Path(ex["audio"]).exists():
            training_data.append({
                "audio": ex["audio"],
                "text": json.dumps(ex["model_output"], ensure_ascii=False)
            })
    
    return training_data

# OPTION 4: SIMPLE BUT EFFECTIVE - Just output next action
def create_simple_action_format():
    """
    Simplest format that actually works:
    Model just says what to do next
    """
    
    examples = [
        {
            "audio": "data/tts_audio_final/flash_heavy_0174_turn_1.mp3",
            "text": "ACTION: verify_user\nAGENT: RouterAgent\nRESPONSE: Merhaba, eSIM sorununuz için kimlik doğrulaması yapalım."
        },
        {
            "audio": "data/tts_audio_final/flash_heavy_0174_turn_2.mp3", 
            "text": "ACTION: route_to_agent:TechAgent\nAGENT: RouterAgent\nRESPONSE: Kimliğiniz doğrulandı, teknik ekibe aktarıyorum."
        },
        {
            "audio": "data/tts_audio_final/flash_heavy_0174_turn_3.mp3",
            "text": "ACTION: check_esim_status,reissue_activation_code\nAGENT: TechAgent\nRESPONSE: eSIM'inizi kontrol edip yeni kod gönderiyorum."
        }
    ]
    
    return examples

def main():
    """Create the training dataset with SYSTEM-INTEGRATED format"""
    
    print("🎯 CREATING SYSTEM-INTEGRATED TRAINING DATA")
    print("=" * 60)
    
    # Use the REALISTIC format
    print("\n📝 Creating REALISTIC system-integrated examples...")
    realistic_examples = create_realistic_system_format()
    
    # Add simple examples for clarity
    print("📝 Adding SIMPLE action examples...")
    simple_examples = create_simple_action_format()
    
    # Combine all examples
    all_training_data = []
    
    # Add realistic examples
    for ex in realistic_examples:
        all_training_data.append(ex)
    
    # Add simple examples
    for ex in simple_examples:
        if Path(ex["audio"]).exists():
            all_training_data.append(ex)
    
    # Now process remaining audio files with simple format
    print("\n📝 Processing all audio files with simple format...")
    
    with open('data/selected_for_tts.json', 'r') as f:
        selected = json.load(f)
    
    for conv_info in selected['conversations'][:30]:  # First 30
        conv_path = Path(conv_info['path'])
        if not conv_path.exists():
            continue
            
        with open(conv_path, 'r') as f:
            conv = json.load(f)
        
        conv_id = conv_info['id']
        agent_responses = conv.get('agent_responses', [])
        
        for i, agent_resp in enumerate(agent_responses):
            audio_file = f"data/tts_audio_final/{conv_id}_turn_{i+1}.mp3"
            
            if not Path(audio_file).exists():
                continue
            
            agent = agent_resp.get('agent_persona', 'RouterAgent')
            if agent == "TechnicalSupportAgent":
                agent = "TechAgent"
            
            tools = agent_resp.get('tools_triggered', [])
            text = agent_resp.get('text', '')
            
            # Create simple actionable format
            action = ','.join(tools) if tools else 'respond'
            
            simple_output = f"ACTION: {action}\nAGENT: {agent}\nRESPONSE: {text}"
            
            all_training_data.append({
                "audio": audio_file,
                "text": simple_output
            })
    
    # Save training data
    with open('SYSTEM_INTEGRATED_TRAINING.json', 'w', encoding='utf-8') as f:
        json.dump(all_training_data, f, ensure_ascii=False, indent=2)
    
    with open('gemma3n_system_training.jsonl', 'w', encoding='utf-8') as f:
        for item in all_training_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"\n✅ Created {len(all_training_data)} training examples")
    
    # Show examples
    print("\n" + "=" * 60)
    print("🎯 EXAMPLE OUTPUTS THAT ACTUALLY WORK WITH THE SYSTEM:")
    
    for i, ex in enumerate(all_training_data[:3]):
        print(f"\n📢 Example {i+1}:")
        print(f"Audio: {ex['audio']}")
        print(f"Output:\n{ex['text'][:200]}...")
    
    print("\n" + "=" * 60)
    print("✅ THIS FORMAT MAKES SENSE FOR SYSTEM INTEGRATION!")
    print("\nThe model outputs:")
    print("  1. ACTION: What tool(s) to call")
    print("  2. AGENT: Which agent is handling")  
    print("  3. RESPONSE: What to say to customer")
    print("\nThe SYSTEM then:")
    print("  1. Executes the tools")
    print("  2. Gets results")
    print("  3. Uses the response template")
    print("  4. Synthesizes to speech")

if __name__ == "__main__":
    main()