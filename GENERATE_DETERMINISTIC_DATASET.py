#!/usr/bin/env python3
"""
TEKNOFEST 2025 - DETERMINISTIC DATASET GENERATOR
Uses Gemini 2.5 Flash with LOW temperature for consistent output
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
import google.generativeai as genai
from datetime import datetime
import time

# Configure Gemini with API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("⚠️ Set GEMINI_API_KEY environment variable!")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

# ULTRA DETERMINISTIC configuration
generation_config = {
    "temperature": 0.05,  # ULTRA LOW for maximum determinism
    "top_p": 0.9,        # Tighter nucleus sampling
    "top_k": 20,         # Fewer top tokens considered
    "max_output_tokens": 4096,
    "candidate_count": 1
}

# System instruction for CONSISTENT Turkish telco responses
system_instruction = """You are generating CONSISTENT, DETERMINISTIC training data for a Turkish telco call center AI.

CRITICAL REQUIREMENTS:
1. Generate ONLY formal, professional Turkish responses
2. Use EXACTLY the same tone and structure for similar situations
3. ALWAYS use formal Turkish (siz/sizin) 
4. Tool calls must use ONLY the 21 defined valid tools
5. Be CONSISTENT - similar problems get similar solutions
6. NO creativity - follow patterns exactly

VALID AGENTS (ONLY THESE 5):
- RouterAgent
- TechAgent  
- BillingAgent
- PlanAgent
- FAQAgent

VALID TOOLS (ONLY THESE 21):
verify_user, get_customer_status, route_to_agent,
check_esim_status, check_device_imei, reissue_activation_code, create_tech_ticket,
get_customer_plan, list_all_plans, change_customer_plan, check_plan_compatibility,
get_last_bill, get_unpaid_amount, apply_campaign_discount, create_payment_note,
search_faq, get_common_solutions, send_help_sms, create_info_ticket,
escalate_to_human, end_conversation
"""

# Initialize Gemini 2.5 Flash with deterministic settings
model = genai.GenerativeModel(
    "gemini-2.5-flash",
    generation_config=generation_config,
    system_instruction=system_instruction
)

# Agent personas with FIXED system prompts
AGENT_PERSONAS = {
    "RouterAgent": {
        "system_prompt": "Sen bir Türk telekom yönlendirme uzmanısın. Müşterileri doğru departmana yönlendir.",
        "capabilities": ["verify_user", "get_customer_status", "route_to_agent"],
        "personality": "professional, efficient"
    },
    "TechAgent": {
        "system_prompt": "Sen bir Türk telekom teknik destek uzmanısın. eSIM, internet, modem sorunlarını çöz.",
        "capabilities": ["check_esim_status", "check_device_imei", "reissue_activation_code", "create_tech_ticket"],
        "personality": "technical, patient"
    },
    "BillingAgent": {
        "system_prompt": "Sen bir Türk telekom fatura uzmanısın. Fatura, ödeme, borç konularında yardım et.",
        "capabilities": ["get_last_bill", "get_unpaid_amount", "apply_campaign_discount", "create_payment_note"],
        "personality": "precise, understanding"
    },
    "PlanAgent": {
        "system_prompt": "Sen bir Türk telekom tarife uzmanısın. En uygun paketleri öner.",
        "capabilities": ["get_customer_plan", "list_all_plans", "change_customer_plan", "check_plan_compatibility"],
        "personality": "consultative, value-focused"
    },
    "FAQAgent": {
        "system_prompt": "Sen bir Türk telekom genel bilgi uzmanısın. Sık sorulan soruları cevapla.",
        "capabilities": ["search_faq", "get_common_solutions", "send_help_sms", "create_info_ticket"],
        "personality": "informative, clear"
    }
}

def load_selected_conversations(limit=5):
    """Load first N selected conversations for testing"""
    
    with open('data/selected_for_tts.json', 'r', encoding='utf-8') as f:
        selected = json.load(f)
    
    conversations = []
    for conv_info in selected['conversations'][:limit]:
        conv_path = Path(conv_info['path'])
        if conv_path.exists():
            with open(conv_path, 'r', encoding='utf-8') as f:
                conv_data = json.load(f)
                conv_data['audio_generated'] = True
                conv_data['selection_score'] = conv_info['score']
                conversations.append(conv_data)
    
    return conversations

def generate_deterministic_response(conversation: Dict, turn_index: int) -> Dict:
    """Generate DETERMINISTIC agent response"""
    
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
    
    # Determine agent based on context
    existing_agent = conversation.get('agent_responses', [])[turn_index] if turn_index < len(conversation.get('agent_responses', [])) else None
    
    if turn_index == 0:
        current_agent = "RouterAgent"
    elif existing_agent:
        current_agent = existing_agent.get('agent_persona', 'RouterAgent')
    else:
        current_agent = "RouterAgent"
    
    customer_text = customer_turn.get('text', '')
    customer_emotion = customer_turn.get('emotion', 'normal')
    
    # DETERMINISTIC prompt
    prompt = f"""Generate a DETERMINISTIC, CONSISTENT Turkish response for this telco scenario.

Customer emotion: {customer_emotion}
Customer says: "{customer_text}"
Current agent: {current_agent}
Available tools: {AGENT_PERSONAS[current_agent]['capabilities']}

Generate EXACTLY this JSON structure with CONSISTENT patterns:
{{
    "agent": "{current_agent}",
    "system_prompt": "{AGENT_PERSONAS[current_agent]['system_prompt']}",
    "response_text": "Professional Turkish response",
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
        "current": "{customer_emotion}",
        "predicted_next": "normal"
    }},
    "next_action": "wait_for_customer_response"
}}

RULES:
- Use ONLY these agents: RouterAgent, TechAgent, BillingAgent, PlanAgent, FAQAgent
- Use ONLY the 21 valid tools listed
- Keep responses CONSISTENT and PROFESSIONAL
- NO creativity - follow patterns"""

    try:
        response = model.generate_content(prompt)
        result = json.loads(response.text.strip().replace("```json", "").replace("```", ""))
        
        # Validate and fix agent names
        valid_agents = {'RouterAgent', 'TechAgent', 'BillingAgent', 'PlanAgent', 'FAQAgent'}
        
        if result.get('agent') not in valid_agents:
            result['agent'] = 'RouterAgent'
        
        if result.get('handoff', {}).get('to_agent') and result['handoff']['to_agent'] not in valid_agents:
            result['handoff']['to_agent'] = 'TechAgent'
        
        # Validate tools
        valid_tools = {
            "verify_user", "get_customer_status", "route_to_agent",
            "check_esim_status", "check_device_imei", "reissue_activation_code", "create_tech_ticket",
            "get_customer_plan", "list_all_plans", "change_customer_plan", "check_plan_compatibility",
            "get_last_bill", "get_unpaid_amount", "apply_campaign_discount", "create_payment_note",
            "search_faq", "get_common_solutions", "send_help_sms", "create_info_ticket",
            "escalate_to_human", "end_conversation"
        }
        
        if 'tool_calls' in result:
            result['tool_calls'] = [
                tc for tc in result['tool_calls']
                if tc.get('tool') in valid_tools
            ]
        
        return result
        
    except Exception as e:
        print(f"❌ Generation error: {e}")
        return None

def create_training_example(conversation: Dict) -> Dict:
    """Create a complete training example"""
    
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
        # Handle nested turn structure
        if isinstance(customer_turn, dict):
            if len(customer_turn) == 1 and list(customer_turn.keys())[0].startswith('turn_'):
                turn_key = list(customer_turn.keys())[0]
                customer_turn = customer_turn[turn_key]
            
            text = customer_turn.get('text', '')
            emotion = customer_turn.get('emotion', 'normal')
        else:
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
        
        # Generate deterministic agent response
        agent_response = generate_deterministic_response(conversation, i)
        
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
            
            for tool in agent_response['tool_calls']:
                training_example["tools_used"].add(tool['tool'])
            
            if agent_response.get('handoff', {}).get('needed'):
                training_example["handoffs"].append({
                    "at_turn": i * 2 + 2,
                    "from": agent_response['agent'],
                    "to": agent_response['handoff']['to_agent'],
                    "reason": agent_response['handoff']['reason']
                })
            
            if 'customer_sentiment' in agent_response:
                training_example["sentiment_journey"].append(agent_response['customer_sentiment'])
    
    # Convert sets to lists
    training_example["agents_involved"] = list(training_example["agents_involved"])
    training_example["tools_used"] = list(training_example["tools_used"])
    
    return training_example

def main():
    """Generate deterministic dataset"""
    
    print("🚀 TEKNOFEST 2025 - DETERMINISTIC DATASET GENERATION")
    print("=" * 60)
    print("Temperature: 0.05 (ULTRA LOW)")
    print("Top-p: 0.9 (TIGHT)")
    print("Top-k: 20 (RESTRICTED)")
    print("=" * 60)
    
    # Test with first 5 conversations
    conversations = load_selected_conversations(limit=5)
    print(f"📊 Testing with {len(conversations)} conversations")
    
    dataset = []
    
    for i, conv in enumerate(conversations):
        conv_id = conv.get('id', f'conversation_{i}')
        print(f"\n[{i+1}/{len(conversations)}] Processing {conv_id}...")
        
        training_example = create_training_example(conv)
        
        # Add metadata
        training_example["metadata"] = {
            "primary_issue": conv.get('primary_issue'),
            "complexity": conv.get('complexity', 'medium'),
            "region": conv.get('region'),
            "generated_at": datetime.now().isoformat(),
            "temperature": 0.05,
            "model": "gemini-2.5-flash"
        }
        
        dataset.append(training_example)
        
        print(f"  ✅ Agents: {training_example['agents_involved']}")
        print(f"  ✅ Tools: {len(training_example['tools_used'])} used")
        print(f"  ✅ Turns: {len(training_example['turns'])}")
        
        # Rate limiting
        time.sleep(1)
    
    # Save test dataset
    with open('DETERMINISTIC_TEST_DATASET.json', 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ DETERMINISTIC TEST COMPLETE!")
    print(f"Generated {len(dataset)} conversations")
    print("File: DETERMINISTIC_TEST_DATASET.json")
    print("\nNow check consistency across similar scenarios!")

if __name__ == "__main__":
    main()