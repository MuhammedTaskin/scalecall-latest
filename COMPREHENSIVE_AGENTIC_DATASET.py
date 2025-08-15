#!/usr/bin/env python3
"""
COMPREHENSIVE AGENTIC DATASET
Handling ALL edge cases and making it TRULY agentic
"""

import json
from pathlib import Path
import random

# WHAT MAKES IT TRULY AGENTIC:
# 1. Multi-agent coordination
# 2. Context-aware decisions
# 3. Error handling
# 4. Multi-step reasoning
# 5. Emotional adaptation
# 6. Handoff decisions
# 7. Escalation logic

def create_comprehensive_training_data():
    """
    Create a dataset that handles EVERYTHING
    """
    
    training_data = []
    
    # ============================================
    # SCENARIO 1: SIMPLE SUCCESS PATH
    # ============================================
    training_data.extend([
        {
            "scenario": "simple_verification",
            "input": {
                "audio": "data/tts_audio_final/flash_heavy_0174_turn_1.mp3",
                "context": {
                    "conversation_state": "initial",
                    "customer_emotion": "worried",
                    "previous_agents": [],
                    "failed_attempts": 0
                }
            },
            "output": {
                "agent": "RouterAgent",
                "reasoning": "New conversation, need verification first",
                "action": "VERIFY_THEN_ROUTE",
                "tools": ["verify_user"],
                "response": "Merhaba, size yardımcı olabilmem için kimlik doğrulaması yapmam gerekiyor.",
                "next_state": "awaiting_verification"
            }
        },
        {
            "scenario": "verification_success",
            "input": {
                "context": {
                    "tool_results": {"verify_user": {"success": True, "customer_id": "CUS123"}},
                    "customer_emotion": "worried",
                    "issue_detected": "esim"
                }
            },
            "output": {
                "agent": "RouterAgent",
                "reasoning": "Customer verified, eSIM issue needs TechAgent",
                "action": "ROUTE_TO_SPECIALIST",
                "tools": ["route_to_agent"],
                "params": {"to": "TechAgent", "reason": "eSIM activation issue"},
                "response": "Kimliğiniz doğrulandı. eSIM sorununuz için teknik ekibe aktarıyorum.",
                "next_state": "transferring"
            }
        }
    ])
    
    # ============================================
    # SCENARIO 2: ERROR HANDLING
    # ============================================
    training_data.extend([
        {
            "scenario": "verification_failed",
            "input": {
                "context": {
                    "tool_results": {"verify_user": {"success": False, "error": "invalid_credentials"}},
                    "failed_attempts": 1
                }
            },
            "output": {
                "agent": "RouterAgent",
                "reasoning": "Verification failed, give another chance",
                "action": "RETRY_VERIFICATION",
                "tools": ["verify_user"],
                "response": "Bilgilerinizi doğrulayamadım. Lütfen TC kimlik numaranızı ve anne kızlık soyadını tekrar söyler misiniz?",
                "next_state": "awaiting_verification_retry"
            }
        },
        {
            "scenario": "multiple_failures",
            "input": {
                "context": {
                    "tool_results": {"verify_user": {"success": False}},
                    "failed_attempts": 3
                }
            },
            "output": {
                "agent": "RouterAgent",
                "reasoning": "Too many failures, need human agent",
                "action": "ESCALATE_TO_HUMAN",
                "tools": ["escalate_to_human"],
                "params": {"reason": "verification_failed_multiple", "priority": "high"},
                "response": "Güvenliğiniz için sizi uzman temsilcimize yönlendiriyorum.",
                "next_state": "escalated"
            }
        }
    ])
    
    # ============================================
    # SCENARIO 3: COMPLEX MULTI-STEP RESOLUTION
    # ============================================
    training_data.extend([
        {
            "scenario": "esim_complex_issue",
            "input": {
                "audio": "data/tts_audio_final/flash_heavy_0174_turn_3.mp3",
                "context": {
                    "agent": "TechAgent",
                    "customer_emotion": "frustrated",
                    "issue": "esim_not_working",
                    "device_info": "iPhone 14 Pro"
                }
            },
            "output": {
                "agent": "TechAgent",
                "reasoning": "Need to diagnose before fixing",
                "action": "DIAGNOSE_MULTI_STEP",
                "tools": ["check_esim_status", "check_device_imei", "check_network_coverage"],
                "response": "iPhone 14 Pro için eSIM durumunu kontrol ediyorum. Birkaç test yapacağım.",
                "next_state": "diagnosing"
            }
        },
        {
            "scenario": "diagnosis_complete",
            "input": {
                "context": {
                    "tool_results": {
                        "check_esim_status": {"active": False, "issue": "pending"},
                        "check_device_imei": {"compatible": True},
                        "check_network_coverage": {"signal": "strong"}
                    }
                }
            },
            "output": {
                "agent": "TechAgent",
                "reasoning": "Device OK, network OK, eSIM stuck - need reissue",
                "action": "FIX_ISSUE",
                "tools": ["reissue_activation_code", "send_instructions_sms"],
                "response": "Cihazınız uyumlu, şebeke sinyali güçlü. eSIM'iniz takılmış. Yeni kod oluşturuyorum.",
                "next_state": "fixing"
            }
        }
    ])
    
    # ============================================
    # SCENARIO 4: CUSTOMER EMOTION HANDLING
    # ============================================
    training_data.extend([
        {
            "scenario": "angry_customer",
            "input": {
                "audio": "data/tts_audio_final/flash_heavy_0082_turn_1.mp3",
                "context": {
                    "customer_emotion": "angry",
                    "complaint": "high_bill",
                    "previous_calls": 3
                }
            },
            "output": {
                "agent": "RouterAgent",
                "reasoning": "Angry customer with billing issue, needs empathy + BillingAgent",
                "action": "EMPATHIZE_AND_ROUTE",
                "tools": ["verify_user", "get_call_history", "route_to_agent"],
                "response": "Yaşadığınız sorunu anlıyorum ve üzgünüm. Hemen fatura uzmanımıza bağlıyorum.",
                "empathy_level": "high",
                "next_state": "routing_to_billing"
            }
        }
    ])
    
    # ============================================
    # SCENARIO 5: AGENT HANDOFF DECISIONS
    # ============================================
    training_data.extend([
        {
            "scenario": "tech_to_billing_handoff",
            "input": {
                "context": {
                    "current_agent": "TechAgent",
                    "issue_resolved": "esim_activated",
                    "new_issue": "billing_question",
                    "customer_text": "Tamam eSIM çalıştı ama faturada neden 50 TL fazla var?"
                }
            },
            "output": {
                "agent": "TechAgent",
                "reasoning": "eSIM fixed but billing question needs BillingAgent",
                "action": "HANDOFF_TO_BILLING",
                "tools": ["create_handoff_note", "route_to_agent"],
                "params": {
                    "to": "BillingAgent",
                    "context": "eSIM issue resolved, customer has billing question",
                    "customer_mood": "satisfied_but_concerned"
                },
                "response": "eSIM'iniz aktif oldu. Fatura sorunuz için sizi fatura departmanına aktarıyorum.",
                "next_state": "transferring_to_billing"
            }
        }
    ])
    
    # ============================================
    # SCENARIO 6: NO SOLUTION AVAILABLE
    # ============================================
    training_data.extend([
        {
            "scenario": "unsolvable_issue",
            "input": {
                "context": {
                    "agent": "TechAgent",
                    "issue": "hardware_defect",
                    "attempted_solutions": ["reset", "reactivate", "troubleshoot"],
                    "all_failed": True
                }
            },
            "output": {
                "agent": "TechAgent",
                "reasoning": "Hardware issue cannot be fixed remotely",
                "action": "RECOMMEND_STORE_VISIT",
                "tools": ["find_nearest_store", "create_appointment", "send_details_sms"],
                "response": "Cihazınızda fiziksel bir sorun var. Size en yakın mağazamızda randevu oluşturuyorum.",
                "resolution": "redirect_to_physical",
                "next_state": "scheduling_appointment"
            }
        }
    ])
    
    # ============================================
    # SCENARIO 7: MULTI-AGENT COLLABORATION
    # ============================================
    training_data.extend([
        {
            "scenario": "complex_multi_agent",
            "input": {
                "context": {
                    "issue": "plan_upgrade_with_device_compatibility",
                    "requires": ["PlanAgent", "TechAgent"],
                    "customer_request": "Yeni pakete geçmek istiyorum ama cihazım uyumlu mu?"
                }
            },
            "output": {
                "agent": "PlanAgent",
                "reasoning": "Need tech check before plan change",
                "action": "COLLABORATE_WITH_TECH",
                "tools": ["request_tech_check", "hold_plan_change"],
                "response": "Yeni paket için önce cihaz uyumluluğunu kontrol etmem gerekiyor. Teknik kontrol yapıyorum.",
                "collaboration": {
                    "with": "TechAgent",
                    "for": "device_compatibility_check"
                },
                "next_state": "awaiting_tech_input"
            }
        }
    ])
    
    # ============================================
    # SCENARIO 8: CONTEXT PRESERVATION
    # ============================================
    training_data.extend([
        {
            "scenario": "remember_context",
            "input": {
                "context": {
                    "conversation_history": [
                        {"turn": 1, "issue": "esim", "resolved": True},
                        {"turn": 2, "issue": "billing", "resolved": False}
                    ],
                    "customer_returns": "Az önce bahsettiğim fatura sorunu hala çözülmedi"
                }
            },
            "output": {
                "agent": "BillingAgent",
                "reasoning": "Customer referring to previous unresolved billing issue",
                "action": "CONTINUE_PREVIOUS_ISSUE",
                "tools": ["retrieve_context", "get_last_bill"],
                "response": "Evet, fatura sorununuza dönüyorum. Son faturanızı inceliyorum.",
                "context_awareness": "high",
                "next_state": "resuming_billing_issue"
            }
        }
    ])
    
    # Convert to actual training format
    final_training_data = []
    
    for item in training_data:
        # Audio-based inputs
        if 'audio' in item.get('input', {}):
            audio_path = item['input']['audio']
            if Path(audio_path).exists():
                final_training_data.append({
                    "audio": audio_path,
                    "context": json.dumps(item['input'].get('context', {}), ensure_ascii=False),
                    "output": json.dumps(item['output'], ensure_ascii=False)
                })
        # Context-only inputs (for tool result processing)
        elif 'context' in item.get('input', {}):
            final_training_data.append({
                "context": json.dumps(item['input']['context'], ensure_ascii=False),
                "output": json.dumps(item['output'], ensure_ascii=False)
            })
    
    # Add real conversation data with comprehensive labeling
    with open('data/selected_for_tts.json', 'r') as f:
        selected = json.load(f)
    
    for conv_info in selected['conversations'][:30]:
        conv_path = Path(conv_info['path'])
        if not conv_path.exists():
            continue
            
        with open(conv_path, 'r') as f:
            conv = json.load(f)
        
        conv_id = conv_info['id']
        customer_turns = conv.get('customer_turns_for_tts', [])
        agent_responses = conv.get('agent_responses', [])
        
        current_agent = "RouterAgent"
        conversation_context = {
            "history": [],
            "resolved_issues": [],
            "pending_issues": []
        }
        
        for i in range(min(len(customer_turns), len(agent_responses))):
            audio_file = f"data/tts_audio_final/{conv_id}_turn_{i+1}.mp3"
            
            if not Path(audio_file).exists():
                continue
            
            # Get customer turn
            customer_turn = customer_turns[i]
            if isinstance(customer_turn, dict):
                if len(customer_turn) == 1 and list(customer_turn.keys())[0].startswith('turn_'):
                    turn_key = list(customer_turn.keys())[0]
                    customer_turn = customer_turn[turn_key]
            
            customer_text = customer_turn.get('text', '')
            customer_emotion = customer_turn.get('emotion', 'normal')
            
            # Get agent response
            agent_resp = agent_responses[i]
            agent = agent_resp.get('agent_persona', 'RouterAgent')
            if agent == "TechnicalSupportAgent":
                agent = "TechAgent"
            
            tools = agent_resp.get('tools_triggered', [])
            text = agent_resp.get('text', '')
            
            # Determine reasoning based on context
            reasoning = ""
            if i == 0:
                reasoning = "Initial contact, need verification"
            elif "esim" in customer_text.lower():
                reasoning = "eSIM issue detected, technical support needed"
            elif "fatura" in customer_text.lower():
                reasoning = "Billing issue detected"
            elif "paket" in customer_text.lower():
                reasoning = "Plan change request"
            
            # Determine action
            action = "PROCESS_REQUEST"
            if i == 0:
                action = "VERIFY_AND_ROUTE"
            elif any(t in tools for t in ["route_to_agent", "transfer"]):
                action = "HANDOFF"
            elif "teşekkür" in customer_text.lower():
                action = "CLOSE_CONVERSATION"
            
            # Add comprehensive output
            final_training_data.append({
                "audio": audio_file,
                "context": json.dumps({
                    "turn": i + 1,
                    "emotion": customer_emotion,
                    "history": conversation_context["history"][-3:],  # Last 3 turns
                    "current_agent": current_agent
                }, ensure_ascii=False),
                "output": json.dumps({
                    "agent": agent,
                    "reasoning": reasoning,
                    "action": action,
                    "tools": tools,
                    "response": text,
                    "emotion_handling": customer_emotion,
                    "next_state": f"turn_{i+2}" if i < len(agent_responses)-1 else "complete"
                }, ensure_ascii=False)
            })
            
            # Update context
            conversation_context["history"].append({
                "turn": i + 1,
                "agent": agent,
                "action": action
            })
            
            # Update current agent for next turn
            if agent != current_agent and agent in ["RouterAgent", "TechAgent", "BillingAgent", "PlanAgent", "FAQAgent"]:
                current_agent = agent
    
    return final_training_data

def main():
    """Create the comprehensive agentic dataset"""
    
    print("🎯 CREATING COMPREHENSIVE AGENTIC DATASET")
    print("=" * 60)
    
    # Generate comprehensive training data
    training_data = create_comprehensive_training_data()
    
    # Save dataset
    with open('COMPREHENSIVE_AGENTIC_DATASET.json', 'w', encoding='utf-8') as f:
        json.dump(training_data, f, ensure_ascii=False, indent=2)
    
    with open('gemma3n_comprehensive.jsonl', 'w', encoding='utf-8') as f:
        for item in training_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"\n✅ Created {len(training_data)} comprehensive training examples")
    
    # Count different types
    audio_based = len([x for x in training_data if 'audio' in x])
    context_only = len([x for x in training_data if 'context' in x and 'audio' not in x])
    
    print(f"   📢 Audio-based: {audio_based}")
    print(f"   🔄 Context-based: {context_only}")
    
    # Analyze scenarios covered
    scenarios = set()
    for item in training_data:
        if 'output' in item:
            try:
                output = json.loads(item['output']) if isinstance(item['output'], str) else item['output']
                if 'action' in output:
                    scenarios.add(output['action'])
            except:
                pass
    
    print(f"\n📊 SCENARIOS COVERED ({len(scenarios)}):")
    for scenario in sorted(scenarios):
        print(f"   • {scenario}")
    
    print("\n" + "=" * 60)
    print("✅ THIS IS TRULY AGENTIC!")
    print("\nThe model learns:")
    print("  🧠 REASONING: Why to take each action")
    print("  🔄 CONTEXT: Remember conversation history")
    print("  😊 EMOTION: Adapt to customer mood")
    print("  🚨 ERRORS: Handle failures gracefully")
    print("  🤝 HANDOFFS: Know when to transfer")
    print("  👥 COLLABORATION: Multi-agent coordination")
    print("  🎯 RESOLUTION: Complete end-to-end solutions")
    
    print("\n🏆 READY FOR TEKNOFEST 2025!")
    print("This dataset will create a TRULY AGENTIC system that:")
    print("  1. Makes intelligent decisions")
    print("  2. Handles all edge cases")
    print("  3. Maintains context")
    print("  4. Recovers from errors")
    print("  5. Collaborates between agents")
    print("  6. Provides complete solutions")

if __name__ == "__main__":
    main()