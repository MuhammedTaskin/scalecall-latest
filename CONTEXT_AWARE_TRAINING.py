#!/usr/bin/env python3
"""
CONTEXT-AWARE TRAINING WITH TOOL RESULTS
The model needs to handle tool execution results!
"""

import json
from pathlib import Path

# THE REAL CONVERSATION FLOW:
# 1. Customer speaks
# 2. Model requests tool execution
# 3. System executes and returns results
# 4. Model uses results to generate response
# 5. Response is synthesized to speech

def create_context_aware_examples():
    """
    Training examples that show the model how to handle tool results
    """
    
    examples = []
    
    # TURN 1: Customer speaks about eSIM issue
    examples.append({
        "input": {
            "audio": "data/tts_audio_final/flash_heavy_0174_turn_1.mp3",
            "context": {
                "previous_tools": [],
                "conversation_state": "initial"
            }
        },
        "output": {
            "stage": "request_tool",
            "agent": "RouterAgent",
            "tool_request": {
                "tool": "verify_user",
                "wait_for_result": True
            },
            "preliminary_response": "Merhaba, eSIM sorununuz için üzgünüm. Güvenliğiniz için kimlik doğrulaması yapmam gerekiyor."
        }
    })
    
    # TURN 1.5: After tool execution
    examples.append({
        "input": {
            "audio": "data/tts_audio_final/flash_heavy_0174_turn_1.mp3",
            "context": {
                "tool_result": {
                    "tool": "verify_user",
                    "result": {"verified": True, "customer_id": "CUS789456", "name": "Can Yılmaz"}
                },
                "conversation_state": "verified"
            }
        },
        "output": {
            "stage": "process_result",
            "agent": "RouterAgent",
            "final_response": "Teşekkürler Can Bey, kimliğinizi doğruladım. eSIM aktivasyon sorununuz için sizi hemen teknik ekibe yönlendiriyorum.",
            "next_action": {
                "tool": "route_to_agent",
                "params": {"to_agent": "TechAgent", "reason": "eSIM activation issue"}
            }
        }
    })
    
    # TURN 2: Technical agent takes over with context
    examples.append({
        "input": {
            "audio": "data/tts_audio_final/flash_heavy_0174_turn_3.mp3",
            "context": {
                "customer_id": "CUS789456",
                "current_agent": "TechAgent",
                "issue": "eSIM activation",
                "previous_tools": ["verify_user", "route_to_agent"]
            }
        },
        "output": {
            "stage": "request_multiple_tools",
            "agent": "TechAgent",
            "tool_requests": [
                {"tool": "check_esim_status", "params": {"phone_number": "from_customer_account"}},
                {"tool": "check_device_imei", "params": {"imei": "from_customer_statement"}}
            ],
            "preliminary_response": "iPhone 14 Pro kullandığınızı anlıyorum. Hemen eSIM durumunuzu kontrol ediyorum."
        }
    })
    
    # TURN 2.5: After multiple tool executions
    examples.append({
        "input": {
            "context": {
                "tool_results": [
                    {
                        "tool": "check_esim_status",
                        "result": {"esim_active": False, "issue": "activation_pending", "attempts": 3}
                    },
                    {
                        "tool": "check_device_imei",
                        "result": {"device_compatible": True, "model": "iPhone 14 Pro", "esim_capable": True}
                    }
                ]
            }
        },
        "output": {
            "stage": "analyze_and_resolve",
            "agent": "TechAgent",
            "decision": "reissue_activation",
            "tool_request": {
                "tool": "reissue_activation_code",
                "params": {"phone_number": "customer_phone", "force_new": True}
            },
            "response": "Cihazınız eSIM uyumlu ve aktivasyon beklemede görünüyor. 3 başarısız deneme var. Yeni bir aktivasyon kodu oluşturuyorum."
        }
    })
    
    # TURN 2.6: Final resolution
    examples.append({
        "input": {
            "context": {
                "tool_result": {
                    "tool": "reissue_activation_code",
                    "result": {"qr_code": "QR789456ABC", "sms_sent": True, "expires_in": "24h", "activation_link": "https://..."}
                }
            }
        },
        "output": {
            "stage": "resolution",
            "agent": "TechAgent",
            "final_response": "Yeni QR kodunuz QR789456ABC olarak oluşturuldu ve SMS ile gönderildi. 24 saat içinde taratarak aktive edebilirsiniz. 5 dakika içinde aktif olacaktır.",
            "success": True,
            "follow_up": "activation_confirmation"
        }
    })
    
    return examples

def create_training_format_with_context():
    """
    Create training data that teaches the model to handle the full cycle
    """
    
    training_data = []
    
    # Format 1: Simple linear flow (for basic training)
    linear_examples = [
        {
            "audio": "data/tts_audio_final/flash_heavy_0174_turn_1.mp3",
            "text": "STAGE:REQUEST|AGENT:RouterAgent|TOOL:verify_user|RESPONSE:Kimlik doğrulaması yapalım"
        },
        {
            "context": "TOOL_RESULT:verify_user:success:CUS789456",
            "text": "STAGE:PROCESS|AGENT:RouterAgent|ACTION:route_to_TechAgent|RESPONSE:Kimliğiniz doğrulandı Can Bey, teknik ekibe aktarıyorum"
        },
        {
            "audio": "data/tts_audio_final/flash_heavy_0174_turn_3.mp3",
            "text": "STAGE:REQUEST|AGENT:TechAgent|TOOLS:check_esim_status,check_device_imei|RESPONSE:eSIM durumunuzu kontrol ediyorum"
        },
        {
            "context": "TOOL_RESULTS:esim_inactive,device_compatible",
            "text": "STAGE:RESOLVE|AGENT:TechAgent|TOOL:reissue_activation_code|RESPONSE:Yeni aktivasyon kodu oluşturuyorum"
        },
        {
            "context": "TOOL_RESULT:qr_code_generated:QR789456",
            "text": "STAGE:COMPLETE|AGENT:TechAgent|RESPONSE:QR kodunuz QR789456, SMS ile gönderildi, 5 dakikada aktif olacak"
        }
    ]
    
    # Add examples with context
    for ex in linear_examples:
        if 'audio' in ex and Path(ex['audio']).exists():
            training_data.append(ex)
        elif 'context' in ex:
            # Context-based responses (after tool execution)
            training_data.append(ex)
    
    # Format 2: Structured JSON format (for advanced training)
    context_examples = create_context_aware_examples()
    
    for ex in context_examples:
        if 'input' in ex and 'output' in ex:
            # Convert to training format
            if 'audio' in ex['input'] and Path(ex['input']['audio']).exists():
                training_item = {
                    "audio": ex['input']['audio'],
                    "context": json.dumps(ex['input'].get('context', {}), ensure_ascii=False),
                    "text": json.dumps(ex['output'], ensure_ascii=False)
                }
                training_data.append(training_item)
            elif 'context' in ex['input']:
                # Pure context-based (after tool execution)
                training_item = {
                    "context": json.dumps(ex['input']['context'], ensure_ascii=False),
                    "text": json.dumps(ex['output'], ensure_ascii=False)
                }
                training_data.append(training_item)
    
    return training_data

def main():
    """Create the complete context-aware training dataset"""
    
    print("🎯 CREATING CONTEXT-AWARE TRAINING WITH TOOL RESULTS")
    print("=" * 60)
    
    # Create training data
    training_data = create_training_format_with_context()
    
    # Add more examples from actual conversations
    with open('data/selected_for_tts.json', 'r') as f:
        selected = json.load(f)
    
    # Process conversations to add context flow
    for conv_info in selected['conversations'][:20]:
        conv_path = Path(conv_info['path'])
        if not conv_path.exists():
            continue
            
        with open(conv_path, 'r') as f:
            conv = json.load(f)
        
        conv_id = conv_info['id']
        agent_responses = conv.get('agent_responses', [])
        
        for i, agent_resp in enumerate(agent_responses):
            audio_file = f"data/tts_audio_final/{conv_id}_turn_{i+1}.mp3"
            
            if Path(audio_file).exists():
                agent = agent_resp.get('agent_persona', 'RouterAgent')
                if agent == "TechnicalSupportAgent":
                    agent = "TechAgent"
                
                tools = agent_resp.get('tools_triggered', [])
                text = agent_resp.get('text', '')
                
                # Add request stage
                training_data.append({
                    "audio": audio_file,
                    "text": f"STAGE:REQUEST|AGENT:{agent}|TOOLS:{','.join(tools)}|RESPONSE:{text[:100]}..."
                })
                
                # Add result processing stage (simulated)
                if tools:
                    training_data.append({
                        "context": f"TOOL_RESULTS:{tools[0]}:success",
                        "text": f"STAGE:PROCESS|AGENT:{agent}|RESPONSE:{text}"
                    })
    
    # Save training dataset
    with open('CONTEXT_AWARE_TRAINING.json', 'w', encoding='utf-8') as f:
        json.dump(training_data, f, ensure_ascii=False, indent=2)
    
    with open('gemma3n_context_training.jsonl', 'w', encoding='utf-8') as f:
        for item in training_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"\n✅ Created {len(training_data)} training examples")
    print(f"   - Audio-based: {len([x for x in training_data if 'audio' in x])}")
    print(f"   - Context-based: {len([x for x in training_data if 'context' in x and 'audio' not in x])}")
    
    # Show the flow
    print("\n" + "=" * 60)
    print("🔄 THE COMPLETE CONVERSATION FLOW:")
    print("\n1️⃣ Customer speaks (audio)")
    print("   ↓")
    print("2️⃣ Model: STAGE:REQUEST|TOOL:verify_user")
    print("   ↓")
    print("3️⃣ System executes tool → {verified:true, customer_id:CUS123}")
    print("   ↓")
    print("4️⃣ Model: STAGE:PROCESS|RESPONSE:Kimliğiniz doğrulandı Can Bey")
    print("   ↓")
    print("5️⃣ System synthesizes response to speech")
    
    print("\n" + "=" * 60)
    print("✅ THIS HANDLES TOOL RESULTS PROPERLY!")
    print("\nThe model learns:")
    print("  • REQUEST stage: Ask for tool execution")
    print("  • PROCESS stage: Use tool results in response")
    print("  • RESOLVE stage: Take action based on results")
    print("  • COMPLETE stage: Finalize with success/failure")

if __name__ == "__main__":
    main()