#!/usr/bin/env python3
"""
TEKNOFEST 2025 - FINAL DETERMINISTIC GENERATOR
Efficient batch processing with progress saving
"""

import json
import os
from pathlib import Path
import google.generativeai as genai
from datetime import datetime
import time

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("⚠️ Set GEMINI_API_KEY environment variable!")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

# DETERMINISTIC configuration
generation_config = {
    "temperature": 0.1,  # LOW for deterministic output
    "top_p": 0.9,
    "top_k": 30,
    "max_output_tokens": 2000,
    "candidate_count": 1
}

# Initialize model
model = genai.GenerativeModel(
    "gemini-2.5-flash",
    generation_config=generation_config
)

# Valid agents and tools
VALID_AGENTS = ["RouterAgent", "TechAgent", "BillingAgent", "PlanAgent", "FAQAgent"]
VALID_TOOLS = [
    "verify_user", "get_customer_status", "route_to_agent",
    "check_esim_status", "check_device_imei", "reissue_activation_code", "create_tech_ticket",
    "get_customer_plan", "list_all_plans", "change_customer_plan", "check_plan_compatibility",
    "get_last_bill", "get_unpaid_amount", "apply_campaign_discount", "create_payment_note",
    "search_faq", "get_common_solutions", "send_help_sms", "create_info_ticket",
    "escalate_to_human", "end_conversation"
]

def load_conversations():
    """Load all 76 selected conversations"""
    with open('data/selected_for_tts.json', 'r', encoding='utf-8') as f:
        selected = json.load(f)
    
    conversations = []
    for conv_info in selected['conversations']:
        conv_path = Path(conv_info['path'])
        if conv_path.exists():
            with open(conv_path, 'r', encoding='utf-8') as f:
                conv_data = json.load(f)
                conv_data['selection_info'] = conv_info
                conversations.append(conv_data)
    
    return conversations

def generate_agent_response(customer_text, emotion, agent, turn_num):
    """Generate a single agent response"""
    
    # Determine appropriate tools based on agent and context
    if agent == "RouterAgent":
        if turn_num == 1:
            tools = ["verify_user"]
        else:
            tools = ["get_customer_status", "route_to_agent"]
    elif agent == "TechAgent":
        if "esim" in customer_text.lower():
            tools = ["check_esim_status", "reissue_activation_code"]
        else:
            tools = ["check_device_imei", "create_tech_ticket"]
    elif agent == "BillingAgent":
        if "borç" in customer_text.lower() or "öde" in customer_text.lower():
            tools = ["get_unpaid_amount", "get_last_bill"]
        else:
            tools = ["apply_campaign_discount", "create_payment_note"]
    elif agent == "PlanAgent":
        tools = ["get_customer_plan", "list_all_plans"]
    else:  # FAQAgent
        tools = ["search_faq", "send_help_sms"]
    
    # Simple prompt for consistent output
    prompt = f"""Generate Turkish telco agent response.

Customer ({emotion}): "{customer_text}"
Agent: {agent}
Turn: {turn_num}

Return JSON:
{{
    "text": "Professional Turkish response",
    "tools": {json.dumps(tools[:2])},
    "handoff": {{"needed": false, "to": null}}
}}"""

    try:
        response = model.generate_content(prompt)
        result = json.loads(response.text.strip().replace("```json", "").replace("```", ""))
        
        # Validate tools
        if "tools" in result:
            result["tools"] = [t for t in result["tools"] if t in VALID_TOOLS]
        
        return result
    except Exception as e:
        # Fallback response
        return {
            "text": "Anlıyorum. Size yardımcı olacağım.",
            "tools": tools[:1],
            "handoff": {"needed": False, "to": None}
        }

def process_conversation(conv):
    """Process a single conversation"""
    
    conv_id = conv.get('id', conv.get('conversation_id', 'unknown'))
    
    result = {
        "conversation_id": conv_id,
        "turns": [],
        "agents": [],
        "tools": []
    }
    
    # Get customer turns
    customer_turns = conv.get('customer_turns_for_tts', [])
    agent_responses = conv.get('agent_responses', [])
    
    current_agent = "RouterAgent"
    
    for i, customer_turn in enumerate(customer_turns):
        # Handle nested structure
        if isinstance(customer_turn, dict):
            if len(customer_turn) == 1 and list(customer_turn.keys())[0].startswith('turn_'):
                turn_key = list(customer_turn.keys())[0]
                customer_turn = customer_turn[turn_key]
        
        if not isinstance(customer_turn, dict):
            continue
            
        text = customer_turn.get('text', '')
        emotion = customer_turn.get('emotion', 'normal')
        
        # Add customer turn
        result["turns"].append({
            "role": "user",
            "text": text,
            "emotion": emotion,
            "audio_file": f"data/tts_audio_final/{conv_id}_turn_{i+1}.mp3"
        })
        
        # Determine agent from existing data if available
        if i < len(agent_responses):
            existing = agent_responses[i]
            current_agent = existing.get('agent_persona', current_agent)
        
        # Generate agent response
        agent_resp = generate_agent_response(text, emotion, current_agent, i+1)
        
        # Add agent turn
        result["turns"].append({
            "role": "assistant",
            "agent": current_agent,
            "text": agent_resp["text"],
            "tools": agent_resp["tools"]
        })
        
        result["agents"].append(current_agent)
        result["tools"].extend(agent_resp["tools"])
        
        # Handle handoff
        if agent_resp.get("handoff", {}).get("needed"):
            next_agent = agent_resp["handoff"].get("to")
            if next_agent and next_agent in VALID_AGENTS:
                current_agent = next_agent
    
    # Remove duplicates
    result["agents"] = list(set(result["agents"]))
    result["tools"] = list(set(result["tools"]))
    
    return result

def main():
    """Main processing loop"""
    
    print("🚀 FINAL DETERMINISTIC DATASET GENERATION")
    print("=" * 60)
    
    # Load conversations
    conversations = load_conversations()
    print(f"📊 Loaded {len(conversations)} conversations")
    
    # Check for existing progress
    progress_file = "FINAL_DATASET_PROGRESS.json"
    if os.path.exists(progress_file):
        with open(progress_file, 'r', encoding='utf-8') as f:
            processed = json.load(f)
        print(f"📂 Resuming from {len(processed)} processed")
    else:
        processed = []
    
    # Process remaining conversations
    for i, conv in enumerate(conversations[len(processed):], start=len(processed)):
        conv_id = conv.get('id', f'conv_{i}')
        print(f"\n[{i+1}/{len(conversations)}] Processing {conv_id}...")
        
        try:
            result = process_conversation(conv)
            processed.append(result)
            
            print(f"  ✅ Turns: {len(result['turns'])}")
            print(f"  ✅ Agents: {result['agents']}")
            print(f"  ✅ Tools: {len(result['tools'])} used")
            
            # Save progress every 5 conversations
            if (i + 1) % 5 == 0:
                with open(progress_file, 'w', encoding='utf-8') as f:
                    json.dump(processed, f, ensure_ascii=False, indent=2)
                print(f"  💾 Progress saved: {i+1}/{len(conversations)}")
            
            # Rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            continue
    
    # Save final dataset
    output_file = "TEKNOFEST_FINAL_DATASET.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)
    
    # Create training JSONL
    with open("teknofest_training.jsonl", 'w', encoding='utf-8') as f:
        for conv in processed:
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
                        "agent_response": agent['text'],
                        "tools": agent['tools']
                    }
                    f.write(json.dumps(training_item, ensure_ascii=False) + '\n')
    
    # Statistics
    print("\n" + "=" * 60)
    print("📈 GENERATION COMPLETE!")
    print(f"  Total conversations: {len(processed)}")
    print(f"  Total turns: {sum(len(c['turns']) for c in processed)}")
    print(f"  Unique agents: {set(sum([c['agents'] for c in processed], []))}")
    print(f"  Unique tools: {set(sum([c['tools'] for c in processed], []))}")
    print(f"\n✅ Files created:")
    print(f"  - {output_file}")
    print(f"  - teknofest_training.jsonl")
    print("\n🏆 Ready for TEKNOFEST 2025!")

if __name__ == "__main__":
    main()