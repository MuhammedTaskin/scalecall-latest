#!/usr/bin/env python3
"""
PARALLEL GEMINI GENERATOR - 10 CONCURRENT API CALLS
Uses everything learned as context for perfect generation
"""

import json
import os
from pathlib import Path
import google.generativeai as genai
from datetime import datetime
import time
import concurrent.futures
from threading import Lock

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("⚠️ Set GEMINI_API_KEY environment variable!")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

# DETERMINISTIC configuration
generation_config = {
    "temperature": 0.1,
    "top_p": 0.9,
    "top_k": 30,
    "max_output_tokens": 3000,
    "candidate_count": 1
}

# Create model instance
model = genai.GenerativeModel(
    "gemini-2.5-flash",
    generation_config=generation_config
)

# Lock for thread-safe operations
write_lock = Lock()
results = []

# CONTEXT FROM EVERYTHING WE'VE LEARNED
SYSTEM_CONTEXT = """You are generating PERFECT Turkish telco call center training data.

AGENTS (ONLY THESE 5):
- RouterAgent: Verifies users, gets status, routes to specialists
- TechAgent: Handles eSIM, internet, modem, device issues  
- BillingAgent: Handles bills, payments, debts, discounts
- PlanAgent: Handles plan changes, package recommendations
- FAQAgent: Handles general questions, FAQs

TOOLS (ONLY THESE 21):
verify_user, get_customer_status, route_to_agent,
check_esim_status, check_device_imei, reissue_activation_code, create_tech_ticket,
get_customer_plan, list_all_plans, change_customer_plan, check_plan_compatibility,
get_last_bill, get_unpaid_amount, apply_campaign_discount, create_payment_note,
search_faq, get_common_solutions, send_help_sms, create_info_ticket,
escalate_to_human, end_conversation

SYSTEM PROMPTS:
- RouterAgent: "Sen bir Türk telekom müşteri yönlendirme uzmanısın. Müşterileri doğru departmana yönlendirirsin."
- TechAgent: "Sen bir Türk telekom teknik destek uzmanısın. eSIM, internet, modem ve cihaz sorunlarını çözersin."
- BillingAgent: "Sen bir Türk telekom fatura ve ödeme uzmanısın. Fatura, borç ve kampanya konularında yardım edersin."
- PlanAgent: "Sen bir Türk telekom tarife ve paket uzmanısın. En uygun tarifeleri önerir ve paket değişiklikleri yaparsın."
- FAQAgent: "Sen bir Türk telekom genel bilgi uzmanısın. Sık sorulan soruları cevaplar ve genel yardım sağlarsın."

FLOW RULES:
1. RouterAgent ALWAYS starts and verifies user first
2. RouterAgent determines issue type and routes to appropriate agent
3. Agents execute 1-3 relevant tools with realistic params/results
4. Handoffs happen when customer mentions different issue type
5. Track sentiment: worried→concerned→relieved→thankful
6. End with end_conversation when resolved

RESPONSE FORMAT:
{
    "agent": "AgentName",
    "system_prompt": "Full Turkish prompt",
    "response_text": "Natural Turkish response",
    "tool_calls": [
        {
            "tool": "tool_name",
            "params": {"param": "value"},
            "result": {"key": "value"},
            "duration_ms": 500
        }
    ],
    "handoff": {
        "needed": boolean,
        "to_agent": "AgentName or null",
        "reason": "Turkish reason or null"
    },
    "customer_sentiment": {
        "current": "emotion",
        "predicted_next": "emotion"
    },
    "next_action": "wait_for_customer_response or transfer_to_agent"
}
"""

def process_single_turn(args):
    """Process a single turn with Gemini"""
    conv_id, turn_index, customer_turn, existing_agent, prev_agent = args
    
    # Handle nested structure
    if isinstance(customer_turn, dict):
        if len(customer_turn) == 1 and list(customer_turn.keys())[0].startswith('turn_'):
            turn_key = list(customer_turn.keys())[0]
            customer_turn = customer_turn[turn_key]
    
    if not isinstance(customer_turn, dict):
        return None
    
    customer_text = customer_turn.get('text', '')
    customer_emotion = customer_turn.get('emotion', 'normal')
    
    # Determine current agent
    if turn_index == 0:
        current_agent = "RouterAgent"
    elif existing_agent:
        current_agent = existing_agent.get('agent_persona', prev_agent)
        # Fix invalid names
        if current_agent == "TechnicalSupportAgent":
            current_agent = "TechAgent"
        elif current_agent == "SalesAgent":
            current_agent = "PlanAgent"
    else:
        current_agent = prev_agent
    
    prompt = f"""{SYSTEM_CONTEXT}

CURRENT SITUATION:
- Conversation: {conv_id}
- Turn: {turn_index + 1}
- Current Agent: {current_agent}
- Customer Emotion: {customer_emotion}
- Customer Says: "{customer_text}"
- Previous Agent Text: "{existing_agent.get('text', '') if existing_agent else ''}"

Generate a PERFECT agent response following ALL rules above.
Return ONLY valid JSON."""

    try:
        response = model.generate_content(prompt)
        result = json.loads(response.text.strip().replace("```json", "").replace("```", ""))
        
        # Validate agent names
        valid_agents = {'RouterAgent', 'TechAgent', 'BillingAgent', 'PlanAgent', 'FAQAgent'}
        if result.get('agent') not in valid_agents:
            result['agent'] = current_agent
        
        if result.get('handoff', {}).get('to_agent') and result['handoff']['to_agent'] not in valid_agents:
            result['handoff']['to_agent'] = None
            result['handoff']['needed'] = False
        
        # Add turn info
        result['turn_index'] = turn_index
        result['conv_id'] = conv_id
        result['customer_text'] = customer_text
        result['customer_emotion'] = customer_emotion
        
        return result
        
    except Exception as e:
        print(f"\n  ❌ Error for {conv_id} turn {turn_index}: {e}")
        # Fallback response
        return {
            'turn_index': turn_index,
            'conv_id': conv_id,
            'customer_text': customer_text,
            'customer_emotion': customer_emotion,
            'agent': current_agent,
            'system_prompt': f"Sen bir Türk telekom uzmanısın.",
            'response_text': existing_agent.get('text', 'Anlıyorum, size yardımcı olacağım.') if existing_agent else 'Merhaba, size nasıl yardımcı olabilirim?',
            'tool_calls': [],
            'handoff': {'needed': False, 'to_agent': None, 'reason': None},
            'customer_sentiment': {'current': customer_emotion, 'predicted_next': 'normal'},
            'next_action': 'wait_for_customer_response'
        }

def process_conversation_batch(conversations_batch):
    """Process a batch of conversations"""
    all_turns = []
    
    for conv in conversations_batch:
        conv_id = conv.get('id', 'unknown')
        customer_turns = conv.get('customer_turns_for_tts', [])
        agent_responses = conv.get('agent_responses', [])
        
        prev_agent = "RouterAgent"
        for i, customer_turn in enumerate(customer_turns):
            existing_agent = agent_responses[i] if i < len(agent_responses) else None
            all_turns.append((conv_id, i, customer_turn, existing_agent, prev_agent))
            
            if existing_agent:
                prev_agent = existing_agent.get('agent_persona', prev_agent)
    
    return all_turns

def main():
    """Main parallel processing"""
    
    print("🚀 PARALLEL GEMINI GENERATOR - 10 CONCURRENT CALLS")
    print("=" * 60)
    
    # Load conversations
    with open('data/selected_for_tts.json', 'r', encoding='utf-8') as f:
        selected = json.load(f)
    
    conversations = []
    for conv_info in selected['conversations']:
        conv_path = Path(conv_info['path'])
        if conv_path.exists():
            with open(conv_path, 'r', encoding='utf-8') as f:
                conv_data = json.load(f)
                conversations.append(conv_data)
    
    print(f"📊 Loaded {len(conversations)} conversations")
    
    # Prepare all turns for processing
    all_turns = process_conversation_batch(conversations)
    print(f"📝 Total turns to process: {len(all_turns)}")
    
    # Process in parallel with 10 workers
    print("\n🔥 LAUNCHING 10 PARALLEL GEMINI CALLS...")
    
    processed_results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Submit all tasks
        future_to_turn = {executor.submit(process_single_turn, turn): turn for turn in all_turns}
        
        # Process results as they complete
        for i, future in enumerate(concurrent.futures.as_completed(future_to_turn)):
            result = future.result()
            if result:
                processed_results.append(result)
                
                # Progress update
                if (i + 1) % 10 == 0:
                    print(f"  ✅ Processed {i + 1}/{len(all_turns)} turns...")
    
    print(f"\n✅ Generated {len(processed_results)} agent responses")
    
    # Organize results by conversation
    conversations_dict = {}
    for result in processed_results:
        conv_id = result['conv_id']
        if conv_id not in conversations_dict:
            conversations_dict[conv_id] = []
        conversations_dict[conv_id].append(result)
    
    # Sort turns within each conversation
    for conv_id in conversations_dict:
        conversations_dict[conv_id].sort(key=lambda x: x['turn_index'])
    
    # Build final dataset
    final_dataset = []
    
    for conv_id, turns in conversations_dict.items():
        conv_data = {
            "conversation_id": conv_id,
            "has_audio": True,
            "turns": [],
            "agents_involved": set(),
            "tools_used": set(),
            "handoffs": []
        }
        
        for turn_data in turns:
            # Add customer turn
            audio_file = f"data/tts_audio_final/{conv_id}_turn_{turn_data['turn_index']+1}.mp3"
            conv_data["turns"].append({
                "turn": turn_data['turn_index'] * 2 + 1,
                "role": "user",
                "text": turn_data['customer_text'],
                "emotion": turn_data['customer_emotion'],
                "audio_file": audio_file if Path(audio_file).exists() else None
            })
            
            # Add agent turn
            conv_data["turns"].append({
                "turn": turn_data['turn_index'] * 2 + 2,
                "role": "assistant",
                "agent": turn_data['agent'],
                "system_prompt": turn_data['system_prompt'],
                "text": turn_data['response_text'],
                "tool_calls": turn_data['tool_calls'],
                "handoff": turn_data['handoff'],
                "customer_sentiment": turn_data['customer_sentiment'],
                "next_action": turn_data['next_action']
            })
            
            # Track data
            conv_data["agents_involved"].add(turn_data['agent'])
            for tool in turn_data.get('tool_calls', []):
                conv_data["tools_used"].add(tool['tool'])
            
            if turn_data['handoff']['needed']:
                conv_data["handoffs"].append({
                    "at_turn": turn_data['turn_index'] * 2 + 2,
                    "from": turn_data['agent'],
                    "to": turn_data['handoff']['to_agent'],
                    "reason": turn_data['handoff']['reason']
                })
        
        # Convert sets to lists
        conv_data["agents_involved"] = list(conv_data["agents_involved"])
        conv_data["tools_used"] = list(conv_data["tools_used"])
        
        final_dataset.append(conv_data)
    
    # Save dataset
    with open('PARALLEL_GEMINI_DATASET.json', 'w', encoding='utf-8') as f:
        json.dump(final_dataset, f, ensure_ascii=False, indent=2)
    
    # Create training JSONL
    with open('parallel_training.jsonl', 'w', encoding='utf-8') as f:
        for conv in final_dataset:
            for i in range(0, len(conv['turns']), 2):
                if i + 1 < len(conv['turns']):
                    customer = conv['turns'][i]
                    agent = conv['turns'][i + 1]
                    
                    training_item = {
                        "conversation_id": conv['conversation_id'],
                        "audio_file": customer.get('audio_file'),
                        "customer_text": customer['text'],
                        "customer_emotion": customer['emotion'],
                        "agent": agent['agent'],
                        "system_prompt": agent['system_prompt'],
                        "agent_response": agent['text'],
                        "tool_calls": agent['tool_calls'],
                        "handoff": agent['handoff'],
                        "customer_sentiment": agent['customer_sentiment'],
                        "next_action": agent['next_action']
                    }
                    f.write(json.dumps(training_item, ensure_ascii=False) + '\n')
    
    print("\n" + "=" * 60)
    print("🏆 PARALLEL GENERATION COMPLETE!")
    print(f"  Conversations: {len(final_dataset)}")
    print(f"  Total turns: {sum(len(c['turns']) for c in final_dataset)}")
    print(f"  Files created:")
    print(f"    - PARALLEL_GEMINI_DATASET.json")
    print(f"    - parallel_training.jsonl")

if __name__ == "__main__":
    main()