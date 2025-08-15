#!/usr/bin/env python3
"""
Simple enhancer - uses existing agent responses and adds proper tool calls
"""

import json
from pathlib import Path
from datetime import datetime

def enhance_conversation(conv_path):
    """Enhance a single conversation with proper tools"""
    
    with open(conv_path, 'r', encoding='utf-8') as f:
        conv = json.load(f)
    
    conv_id = conv.get('id', 'unknown')
    
    result = {
        "conversation_id": conv_id,
        "has_audio": True,
        "turns": [],
        "agents_involved": set(),
        "tools_used": set()
    }
    
    # Process customer turns and agent responses
    customer_turns = conv.get('customer_turns_for_tts', [])
    agent_responses = conv.get('agent_responses', [])
    
    for i, customer_turn in enumerate(customer_turns):
        # Handle nested structure
        if isinstance(customer_turn, dict):
            if len(customer_turn) == 1 and list(customer_turn.keys())[0].startswith('turn_'):
                turn_key = list(customer_turn.keys())[0]
                customer_turn = customer_turn[turn_key]
        
        if not isinstance(customer_turn, dict):
            continue
        
        # Add customer turn
        result["turns"].append({
            "turn": i * 2 + 1,
            "role": "user",
            "text": customer_turn.get('text', ''),
            "emotion": customer_turn.get('emotion', 'normal'),
            "audio_file": f"data/tts_audio_final/{conv_id}_turn_{i+1}.mp3"
        })
        
        # Add agent response if available
        if i < len(agent_responses):
            agent_resp = agent_responses[i]
            agent_name = agent_resp.get('agent_persona', 'RouterAgent')
            
            # Map invalid agent names to valid ones
            agent_map = {
                'TechnicalSupportAgent': 'TechAgent',
                'SalesAgent': 'PlanAgent',
                'SupportAgent': 'FAQAgent'
            }
            agent_name = agent_map.get(agent_name, agent_name)
            
            # Get tools from response
            tools = agent_resp.get('tools_triggered', [])
            
            # Ensure tools are valid
            valid_tools = {
                "verify_user", "get_customer_status", "route_to_agent",
                "check_esim_status", "check_device_imei", "reissue_activation_code", 
                "create_tech_ticket", "get_customer_plan", "list_all_plans", 
                "change_customer_plan", "check_plan_compatibility",
                "get_last_bill", "get_unpaid_amount", "apply_campaign_discount", 
                "create_payment_note", "search_faq", "get_common_solutions", 
                "send_help_sms", "create_info_ticket",
                "escalate_to_human", "end_conversation"
            }
            
            # Filter valid tools
            tools = [t for t in tools if t in valid_tools]
            
            # Add default tools if none exist
            if not tools:
                if i == 0 and agent_name == "RouterAgent":
                    tools = ["verify_user"]
                elif agent_name == "TechAgent":
                    tools = ["check_esim_status"]
                elif agent_name == "BillingAgent":
                    tools = ["get_last_bill"]
                elif agent_name == "PlanAgent":
                    tools = ["get_customer_plan"]
                elif agent_name == "FAQAgent":
                    tools = ["search_faq"]
            
            result["turns"].append({
                "turn": i * 2 + 2,
                "role": "assistant",
                "agent": agent_name,
                "text": agent_resp.get('text', ''),
                "tools": tools
            })
            
            result["agents_involved"].add(agent_name)
            result["tools_used"].update(tools)
    
    # Convert sets to lists
    result["agents_involved"] = list(result["agents_involved"])
    result["tools_used"] = list(result["tools_used"])
    
    return result

def main():
    """Process all selected conversations"""
    
    print("🚀 SIMPLE DATASET ENHANCER")
    print("=" * 60)
    
    # Load selected conversations
    with open('data/selected_for_tts.json', 'r', encoding='utf-8') as f:
        selected = json.load(f)
    
    dataset = []
    
    for i, conv_info in enumerate(selected['conversations']):
        conv_path = Path(conv_info['path'])
        
        if not conv_path.exists():
            print(f"[{i+1}/76] Skipping {conv_info['id']} - file not found")
            continue
        
        print(f"[{i+1}/76] Processing {conv_info['id']}...", end='')
        
        try:
            result = enhance_conversation(conv_path)
            result['metadata'] = {
                'primary_issue': conv_info.get('primary_issue'),
                'score': conv_info['score'],
                'dataset': conv_info['dataset']
            }
            dataset.append(result)
            print(f" ✅ {len(result['agents_involved'])} agents, {len(result['tools_used'])} tools")
        except Exception as e:
            print(f" ❌ Error: {e}")
    
    # Save dataset
    with open('ENHANCED_DATASET.json', 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    # Create training JSONL
    with open('enhanced_training.jsonl', 'w', encoding='utf-8') as f:
        for conv in dataset:
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
    print("📈 ENHANCEMENT COMPLETE!")
    print(f"  Total conversations: {len(dataset)}")
    print(f"  Total turns: {sum(len(c['turns']) for c in dataset)}")
    
    all_agents = set()
    all_tools = set()
    for conv in dataset:
        all_agents.update(conv['agents_involved'])
        all_tools.update(conv['tools_used'])
    
    print(f"  Unique agents: {all_agents}")
    print(f"  Unique tools ({len(all_tools)}): {list(all_tools)[:10]}...")
    print(f"\n✅ Files created:")
    print(f"  - ENHANCED_DATASET.json")
    print(f"  - enhanced_training.jsonl")

if __name__ == "__main__":
    main()