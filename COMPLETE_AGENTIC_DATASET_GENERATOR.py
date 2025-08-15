#!/usr/bin/env python3
"""
TEKNOFEST 2025 - COMPLETE AGENTIC DATASET GENERATOR
Uses Gemini 2.5 Flash to generate missing agent responses with full agentic capabilities
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
import google.generativeai as genai
from datetime import datetime
import time

# Configure Gemini 2.0 Flash with optimal settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("⚠️ Set GEMINI_API_KEY environment variable!")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

# Optimal configuration for Turkish telco conversations
generation_config = {
    "temperature": 0.1,  # DETERMINISTIC output for consistent responses
    "top_p": 0.95,      # Nucleus sampling for coherent responses
    "top_k": 40,        # Consider top 40 tokens (default: 20)
    "max_output_tokens": 4096,  # Enough for complex conversations
    "candidate_count": 1
}

# System instruction for Turkish telco domain
system_instruction = """You are generating high-quality training data for a Turkish telco call center AI.

CRITICAL REQUIREMENTS:
1. Generate ONLY natural, fluent Turkish responses
2. Use proper Turkish telco terminology and conventions
3. Maintain professional yet empathetic tone
4. Follow Turkish conversation patterns and cultural norms
5. Include realistic tool execution with proper parameters
6. Show emotional intelligence and adapt to customer emotions
7. Use formal Turkish (siz/sizin) for professional interactions

QUALITY STANDARDS:
- Responses must be grammatically perfect Turkish
- Tool calls must use ONLY the 21 defined valid tools
- Each response should demonstrate multiple capabilities
- Maintain context across conversation turns
- Show realistic problem-solving progression
"""

# Initialize Gemini 2.5 Flash (Latest Stable)
# - 1M token context window
# - Native Turkish support
# - Built-in thinking capabilities
# - 30 HD voices in 24 languages
# - 20-30% more efficient token usage
# - #2 on LMarena leaderboard
# - Cost: $0.10/1M input, $0.40/1M output
model = genai.GenerativeModel(
    "gemini-2.5-flash",  # Stable version with thinking capabilities
    generation_config=generation_config,
    system_instruction=system_instruction
)

# Agent personas with system prompts (USING ONLY VALID TOOLS)
AGENT_PERSONAS = {
    "RouterAgent": {
        "system_prompt": "Sen bir Türk telekom yönlendirme uzmanısın. Müşterileri doğru departmana yönlendir.",
        "capabilities": ["verify_user", "get_customer_status", "route_to_agent"],
        "personality": "professional, efficient, empathetic"
    },
    "TechAgent": {
        "system_prompt": "Sen bir Türk telekom teknik destek uzmanısın. eSIM, internet, modem sorunlarını çöz.",
        "capabilities": ["check_esim_status", "check_device_imei", "reissue_activation_code", "create_tech_ticket"],
        "personality": "technical, patient, solution-oriented"
    },
    "BillingAgent": {
        "system_prompt": "Sen bir Türk telekom fatura uzmanısın. Fatura, ödeme, borç konularında yardım et.",
        "capabilities": ["get_last_bill", "get_unpaid_amount", "apply_campaign_discount", "create_payment_note"],
        "personality": "precise, understanding, helpful"
    },
    "PlanAgent": {
        "system_prompt": "Sen bir Türk telekom tarife uzmanısın. En uygun paketleri öner.",
        "capabilities": ["get_customer_plan", "list_all_plans", "change_customer_plan", "check_plan_compatibility"],
        "personality": "consultative, friendly, value-focused"
    },
    "FAQAgent": {
        "system_prompt": "Sen bir Türk telekom genel bilgi uzmanısın. Sık sorulan soruları cevapla.",
        "capabilities": ["search_faq", "get_common_solutions", "send_help_sms", "create_info_ticket"],
        "personality": "informative, clear, accessible"
    }
}

# ONLY these tools are valid (21 total)
VALID_TOOLS = {
    "verify_user", "get_customer_status", "route_to_agent",
    "check_esim_status", "check_device_imei", "reissue_activation_code", "create_tech_ticket",
    "get_customer_plan", "list_all_plans", "change_customer_plan", "check_plan_compatibility",
    "get_last_bill", "get_unpaid_amount", "apply_campaign_discount", "create_payment_note",
    "search_faq", "get_common_solutions", "send_help_sms", "create_info_ticket",
    "escalate_to_human", "end_conversation"
}

# Tool definitions with realistic execution patterns
TOOL_DEFINITIONS = {
    # Authentication & Customer
    "verify_user": {
        "params": ["tc_no", "mother_maiden_name"],
        "returns": {"verified": True, "customer_id": "CUS{random}", "name": "{name}"},
        "duration_ms": 500
    },
    "get_customer_status": {
        "params": ["customer_id"],
        "returns": {"status": "active", "plan": "{plan_name}", "balance": "{balance}"},
        "duration_ms": 300
    },
    
    # eSIM & Device
    "check_esim_status": {
        "params": ["phone_number"],
        "returns": {"esim_active": False, "issue": "activation_pending", "last_attempt": "{timestamp}"},
        "duration_ms": 800
    },
    "check_device_imei": {
        "params": ["imei"],
        "returns": {"device_compatible": True, "model": "iPhone 14 Pro", "esim_capable": True},
        "duration_ms": 400
    },
    "reissue_activation_code": {
        "params": ["phone_number"],
        "returns": {"qr_code": "QR{random}", "sms_sent": True, "expires_in": "24h"},
        "duration_ms": 1200
    },
    
    # Billing
    "get_last_bill": {
        "params": ["customer_id"],
        "returns": {"amount": 299.90, "period": "2024-12", "paid": False},
        "duration_ms": 600
    },
    "get_unpaid_amount": {
        "params": ["customer_id"],
        "returns": {"total_debt": 599.80, "overdue": 299.90, "current": 299.90},
        "duration_ms": 500
    },
    "create_payment_note": {
        "params": ["customer_id", "note"],
        "returns": {"note_id": "PAY{random}", "created": True},
        "duration_ms": 300
    },
    
    # Plans & Packages
    "get_customer_plan": {
        "params": ["customer_id"],
        "returns": {"plan_name": "Genç Tarife 10GB", "monthly_fee": 199.90, "data_limit": "10GB"},
        "duration_ms": 400
    },
    "list_all_plans": {
        "params": [],
        "returns": {"plans": [{"name": "200GB Mega", "price": 399}, {"name": "Sınırsız Pro", "price": 599}]},
        "duration_ms": 700
    },
    "change_customer_plan": {
        "params": ["customer_id", "new_plan_id"],
        "returns": {"success": True, "effective_date": "next_billing_cycle"},
        "duration_ms": 1000
    },
    "check_plan_compatibility": {
        "params": ["customer_id", "plan_id"],
        "returns": {"compatible": True, "requirements_met": True},
        "duration_ms": 500
    },
    "apply_campaign_discount": {
        "params": ["customer_id", "campaign_code"],
        "returns": {"applied": True, "discount_amount": 50, "valid_for_months": 3},
        "duration_ms": 800
    },
    
    # Technical Support
    "create_tech_ticket": {
        "params": ["customer_id", "issue_description"],
        "returns": {"ticket_id": "TT{random}", "priority": "high", "estimated_resolution": "2h"},
        "duration_ms": 600
    },
    
    # Support & FAQ
    "search_faq": {
        "params": ["query"],
        "returns": {"results": [{"title": "eSIM Aktivasyon", "content": "..."}], "found": 3},
        "duration_ms": 300
    },
    "get_common_solutions": {
        "params": ["issue_type"],
        "returns": {"solutions": ["Cihazı yeniden başlatın", "QR kodu tekrar tarayın"]},
        "duration_ms": 200
    },
    "send_help_sms": {
        "params": ["phone_number", "content"],
        "returns": {"sent": True, "delivery_status": "delivered"},
        "duration_ms": 400
    },
    "create_info_ticket": {
        "params": ["customer_id", "request"],
        "returns": {"ticket_id": "INFO{random}", "status": "created"},
        "duration_ms": 500
    },
    
    # Agent Management
    "route_to_agent": {
        "params": ["from_agent", "to_agent", "reason"],
        "returns": {"transferred": True, "queue_position": 0, "estimated_wait": "immediate"},
        "duration_ms": 200
    },
    "escalate_to_human": {
        "params": ["reason", "priority"],
        "returns": {"escalated": True, "human_agent_id": "H{random}", "wait_time": "30s"},
        "duration_ms": 300
    },
    "end_conversation": {
        "params": ["resolution_status"],
        "returns": {"ended": True, "satisfaction_survey_sent": True},
        "duration_ms": 100
    }
}

def load_selected_conversations():
    """Load the 76 selected conversations that have audio"""
    
    with open('data/selected_for_tts.json', 'r', encoding='utf-8') as f:
        selected = json.load(f)
    
    conversations = []
    for conv_info in selected['conversations']:
        conv_path = Path(conv_info['path'])
        if conv_path.exists():
            with open(conv_path, 'r', encoding='utf-8') as f:
                conv_data = json.load(f)
                conv_data['audio_generated'] = True
                conv_data['selection_score'] = conv_info['score']
                conversations.append(conv_data)
    
    return conversations

def generate_complete_agent_response(conversation: Dict, turn_index: int) -> Dict:
    """Use Gemini to generate complete agent response with tools and handoffs"""
    
    # Build context
    customer_turns = conversation.get('customer_turns_for_tts', [])
    if turn_index >= len(customer_turns):
        return None
        
    customer_turn = customer_turns[turn_index]
    
    # Handle nested turn structure
    if isinstance(customer_turn, dict):
        if len(customer_turn) == 1 and list(customer_turn.keys())[0].startswith('turn_'):
            turn_key = list(customer_turn.keys())[0]
            customer_turn = customer_turn[turn_key]
    
    if not customer_turn or not isinstance(customer_turn, dict):
        return None
    
    existing_agent = conversation.get('agent_responses', [])[turn_index] if turn_index < len(conversation.get('agent_responses', [])) else None
    
    # Determine which agent should respond
    if turn_index == 0:
        current_agent = "RouterAgent"
    elif existing_agent:
        current_agent = existing_agent.get('agent_persona', 'RouterAgent')
    else:
        current_agent = "RouterAgent"
    
    # Extract text and emotion from customer turn
    customer_text = customer_turn.get('text', '')
    customer_emotion = customer_turn.get('emotion', 'normal')
    
    # Build prompt for Gemini
    prompt = f"""You are generating training data for a Turkish telco call center AI system.
    
Current conversation context:
- Customer emotion: {customer_emotion}
- Customer says: "{customer_text}"
- Current agent: {current_agent}
- Agent system prompt: {AGENT_PERSONAS[current_agent]['system_prompt']}

Previous conversation turns: {turn_index} turns completed

Generate a COMPLETE agent response with:
1. Natural Turkish response text (professional, empathetic)
2. Tool calls that would be made (with parameters and results)
3. If needed, handoff decision to another agent
4. Sentiment analysis of customer
5. Next action planning

Available tools for {current_agent}: {AGENT_PERSONAS[current_agent]['capabilities']}

CRITICAL: You MUST ONLY use these 5 agent names for handoffs:
- RouterAgent
- TechAgent  
- BillingAgent
- PlanAgent
- FAQAgent

NEVER use: SalesAgent, TechnicalSupportAgent, Teknik Destek Uzmanı, or any other names!

Tool definitions:
{json.dumps(TOOL_DEFINITIONS, indent=2)}

Output format (JSON):
{{
    "agent": "{current_agent}",
    "system_prompt": "...",
    "response_text": "Natural Turkish response",
    "tool_calls": [
        {{
            "tool": "tool_name",
            "params": {{}},
            "result": {{}},
            "duration_ms": 500
        }}
    ],
    "handoff": {{
        "needed": false,
        "to_agent": null,
        "reason": null
    }},
    "customer_sentiment": {{
        "current": "worried",
        "predicted_next": "relieved"
    }},
    "next_action": "wait_for_customer_response"
}}

Generate a realistic, helpful response that demonstrates the agent's capabilities."""

    try:
        response = model.generate_content(prompt)
        result = json.loads(response.text.strip().replace("```json", "").replace("```", ""))
        
        # VALIDATION: Fix invalid agent names
        valid_agents = {'RouterAgent', 'TechAgent', 'BillingAgent', 'PlanAgent', 'FAQAgent'}
        
        # Fix agent name
        if result.get('agent') not in valid_agents:
            # Map common mistakes
            agent_map = {
                'TechnicalSupportAgent': 'TechAgent',
                'Teknik Destek Uzmanı': 'TechAgent',
                'SalesAgent': 'PlanAgent',
                'SupportAgent': 'FAQAgent'
            }
            result['agent'] = agent_map.get(result['agent'], 'RouterAgent')
        
        # Fix handoff agent
        if result.get('handoff', {}).get('to_agent'):
            to_agent = result['handoff']['to_agent']
            if to_agent not in valid_agents:
                agent_map = {
                    'TechnicalSupportAgent': 'TechAgent',
                    'Teknik Destek Uzmanı': 'TechAgent',
                    'SalesAgent': 'PlanAgent',
                    'SupportAgent': 'FAQAgent'
                }
                result['handoff']['to_agent'] = agent_map.get(to_agent, 'TechAgent')
        
        # Validate tools
        valid_tools = VALID_TOOLS
        if 'tool_calls' in result:
            result['tool_calls'] = [
                tc for tc in result['tool_calls']
                if tc.get('tool') in valid_tools
            ]
        
        return result
    except Exception as e:
        print(f"❌ Gemini error: {e}")
        # Fallback to existing response if available
        if existing_agent:
            return {
                "agent": existing_agent['agent_persona'],
                "system_prompt": AGENT_PERSONAS[existing_agent['agent_persona']]['system_prompt'],
                "response_text": existing_agent['text'],
                "tool_calls": [{"tool": t, "params": {}, "result": {}} for t in existing_agent.get('tools_triggered', [])],
                "handoff": {"needed": False, "to_agent": None, "reason": None}
            }
        return None

def create_complete_training_example(conversation: Dict) -> Dict:
    """Create a complete training example with all agentic capabilities"""
    
    # Get conversation ID (handle both 'id' and 'conversation_id' keys)
    conv_id = conversation.get('id', conversation.get('conversation_id', 'unknown'))
    
    training_example = {
        "conversation_id": conv_id,
        "has_audio": True,
        "audio_files": [],
        "turns": [],
        "agents_involved": set(),
        "tools_used": set(),
        "handoffs": [],
        "sentiment_journey": []
    }
    
    # Process each turn
    for i, customer_turn in enumerate(conversation.get('customer_turns_for_tts', [])):
        # Handle nested turn structure (some have turn_id as key with nested object)
        if isinstance(customer_turn, dict):
            # Check if this is a nested structure like {"turn_010": {...}}
            if len(customer_turn) == 1 and list(customer_turn.keys())[0].startswith('turn_'):
                # Extract the nested turn data
                turn_key = list(customer_turn.keys())[0]
                customer_turn = customer_turn[turn_key]
            
            # Now extract the text and emotion
            text = customer_turn.get('text', '')
            emotion = customer_turn.get('emotion', 'normal')
        else:
            # Skip if not a dict
            continue
        
        # Customer turn with audio reference
        audio_file = f"data/tts_audio_final/{conv_id}_turn_{i+1}.mp3"
        
        customer_data = {
            "turn": i * 2 + 1,
            "role": "user",
            "audio_file": audio_file if Path(audio_file).exists() else None,
            "text": text,
            "emotion": emotion
        }
        training_example["turns"].append(customer_data)
        if customer_data["audio_file"]:
            training_example["audio_files"].append(audio_file)
        
        # Generate complete agent response
        agent_response = generate_complete_agent_response(conversation, i)
        
        if agent_response:
            agent_data = {
                "turn": i * 2 + 2,
                "role": "assistant",
                "agent": agent_response['agent'],
                "system_prompt": agent_response['system_prompt'],
                "text": agent_response['response_text'],
                "tool_calls": agent_response['tool_calls'],
                "handoff": agent_response.get('handoff')
            }
            training_example["turns"].append(agent_data)
            training_example["agents_involved"].add(agent_response['agent'])
            
            # Track tools
            for tool in agent_response['tool_calls']:
                training_example["tools_used"].add(tool['tool'])
            
            # Track handoffs
            if agent_response.get('handoff', {}).get('needed'):
                training_example["handoffs"].append({
                    "at_turn": i * 2 + 2,
                    "from": agent_response['agent'],
                    "to": agent_response['handoff']['to_agent'],
                    "reason": agent_response['handoff']['reason']
                })
            
            # Track sentiment
            if 'customer_sentiment' in agent_response:
                training_example["sentiment_journey"].append(agent_response['customer_sentiment'])
    
    # Convert sets to lists for JSON serialization
    training_example["agents_involved"] = list(training_example["agents_involved"])
    training_example["tools_used"] = list(training_example["tools_used"])
    
    return training_example

def generate_complete_dataset(start_from=0):
    """Generate the complete agentic dataset"""
    
    print("🚀 TEKNOFEST 2025 - COMPLETING AGENTIC DATASET")
    print("="*60)
    
    # Load selected conversations with audio
    conversations = load_selected_conversations()
    print(f"📊 Loaded {len(conversations)} conversations with audio")
    
    # Skip already processed
    conversations = conversations[start_from:]
    print(f"📝 Processing from index {start_from}")
    
    complete_dataset = []
    
    for i, conv in enumerate(conversations):
        actual_index = i + start_from
        conv_id = conv.get('id', f'conversation_{actual_index}')
        print(f"\n[{actual_index+1}/76] Processing {conv_id}...")
        
        # Create complete training example
        training_example = create_complete_training_example(conv)
        
        # Add metadata
        training_example["metadata"] = {
            "primary_issue": conv.get('primary_issue'),
            "complexity": conv.get('complexity', 'medium'),
            "region": conv.get('region'),
            "generated_at": datetime.now().isoformat(),
            "audio_count": len(training_example["audio_files"]),
            "tool_count": len(training_example["tools_used"]),
            "agent_count": len(training_example["agents_involved"])
        }
        
        complete_dataset.append(training_example)
        
        # Show progress
        print(f"  ✅ Agents: {training_example['agents_involved']}")
        print(f"  ✅ Tools: {len(training_example['tools_used'])} used")
        print(f"  ✅ Audio: {len(training_example['audio_files'])} files")
        print(f"  ✅ Handoffs: {len(training_example['handoffs'])}")
        
        # Rate limiting for Gemini
        time.sleep(1)
        
        # Save progress every 10 conversations
        if (i + 1) % 10 == 0:
            with open('complete_agentic_dataset_progress.json', 'w', encoding='utf-8') as f:
                json.dump(complete_dataset, f, ensure_ascii=False, indent=2)
            print(f"\n💾 Progress saved: {i+1} conversations")
    
    # Save final dataset
    with open('COMPLETE_AGENTIC_DATASET.json', 'w', encoding='utf-8') as f:
        json.dump(complete_dataset, f, ensure_ascii=False, indent=2)
    
    # Generate training JSONL
    with open('teknofest_final_training.jsonl', 'w', encoding='utf-8') as f:
        for example in complete_dataset:
            # Format for Gemma 3N training
            for i in range(0, len(example['turns']), 2):
                if i + 1 < len(example['turns']):
                    customer_turn = example['turns'][i]
                    agent_turn = example['turns'][i + 1]
                    
                    training_item = {
                        "conversation_id": example['conversation_id'],
                        "audio_file": customer_turn.get('audio_file'),
                        "customer_text": customer_turn['text'],
                        "customer_emotion": customer_turn['emotion'],
                        "agent": agent_turn['agent'],
                        "system_prompt": agent_turn['system_prompt'],
                        "agent_response": agent_turn['text'],
                        "tool_calls": agent_turn['tool_calls'],
                        "handoff": agent_turn.get('handoff')
                    }
                    f.write(json.dumps(training_item, ensure_ascii=False) + '\n')
    
    # Statistics
    print("\n" + "="*60)
    print("📈 DATASET COMPLETE!")
    print(f"  Total conversations: {len(complete_dataset)}")
    print(f"  Total audio files: {sum(len(e['audio_files']) for e in complete_dataset)}")
    print(f"  Unique agents: {set(sum([e['agents_involved'] for e in complete_dataset], []))}")
    print(f"  Unique tools: {set(sum([list(e['tools_used']) for e in complete_dataset], []))}")
    print(f"  Total handoffs: {sum(len(e['handoffs']) for e in complete_dataset)}")
    print("\n✅ Files created:")
    print("  - COMPLETE_AGENTIC_DATASET.json")
    print("  - teknofest_final_training.jsonl")
    print("\n🏆 Ready for TEKNOFEST 2025!")

if __name__ == "__main__":
    import sys
    start_from = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    generate_complete_dataset(start_from)