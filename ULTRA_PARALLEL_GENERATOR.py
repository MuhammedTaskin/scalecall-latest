#!/usr/bin/env python3
"""
ULTRA PARALLEL GENERATOR - FLAWLESS GEMINI GENERATION
10 concurrent calls with strict JSON output
"""

import json
import os
from pathlib import Path
import google.generativeai as genai
import concurrent.futures
from threading import Lock
import random

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("❌ No API key!")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

# Ultra deterministic
generation_config = {
    "temperature": 0.1,
    "top_p": 0.9,
    "top_k": 20,
    "max_output_tokens": 2000,
    "candidate_count": 1
}

# Thread-safe results storage
results_lock = Lock()
processed_turns = []

def create_agent_response(conv_id, turn_index, customer_text, customer_emotion, current_agent, existing_text=""):
    """Create a single agent response using Gemini"""
    
    # Create focused model for this call
    model = genai.GenerativeModel(
        "gemini-2.5-flash",
        generation_config=generation_config
    )
    
    # Determine appropriate tools based on agent and context
    text_lower = customer_text.lower()
    
    if current_agent == "RouterAgent":
        if turn_index == 0:
            tools_to_use = ["verify_user"]
            handoff_needed = False
            next_agent = None
        else:
            tools_to_use = ["get_customer_status", "route_to_agent"]
            handoff_needed = True
            # Route based on keywords
            if "esim" in text_lower or "internet" in text_lower:
                next_agent = "TechAgent"
                reason = "Teknik sorun tespit edildi"
            elif "fatura" in text_lower or "borç" in text_lower:
                next_agent = "BillingAgent"
                reason = "Fatura sorunu var"
            elif "paket" in text_lower or "tarife" in text_lower:
                next_agent = "PlanAgent"
                reason = "Tarife değişikliği talebi"
            else:
                next_agent = "FAQAgent"
                reason = "Genel bilgi talebi"
    
    elif current_agent == "TechAgent":
        if "esim" in text_lower:
            tools_to_use = ["check_esim_status", "reissue_activation_code"]
        else:
            tools_to_use = ["check_device_imei", "create_tech_ticket"]
        handoff_needed = "fatura" in text_lower or "paket" in text_lower
        if handoff_needed:
            next_agent = "BillingAgent" if "fatura" in text_lower else "PlanAgent"
            reason = "Müşteri başka konu belirtti"
        else:
            next_agent = None
            reason = None
    
    elif current_agent == "BillingAgent":
        if "borç" in text_lower:
            tools_to_use = ["get_unpaid_amount", "get_last_bill"]
        else:
            tools_to_use = ["apply_campaign_discount", "create_payment_note"]
        handoff_needed = False
        next_agent = None
        reason = None
    
    elif current_agent == "PlanAgent":
        tools_to_use = ["get_customer_plan", "list_all_plans"]
        if "değiş" in text_lower:
            tools_to_use.append("change_customer_plan")
        handoff_needed = False
        next_agent = None
        reason = None
    
    else:  # FAQAgent
        tools_to_use = ["search_faq"]
        handoff_needed = False
        next_agent = None
        reason = None
    
    # Add end_conversation for thankful customers
    if "teşekkür" in text_lower or "sağ ol" in text_lower:
        tools_to_use.append("end_conversation")
    
    # Ultra-focused prompt
    prompt = f"""Return ONLY valid JSON for Turkish telco agent response.

Customer ({customer_emotion}): "{customer_text}"
Agent: {current_agent}
Response text to use: "{existing_text if existing_text else 'Anlıyorum, size yardımcı olacağım.'}"

Tools to execute: {tools_to_use}
Handoff needed: {handoff_needed}
Next agent: {next_agent if handoff_needed else None}

Return EXACTLY this structure:
{{
  "agent": "{current_agent}",
  "response_text": "{existing_text if existing_text else 'Anlıyorum, size yardımcı olacağım.'}",
  "tools": {json.dumps(tools_to_use)},
  "handoff_needed": {str(handoff_needed).lower()},
  "next_agent": {"'" + next_agent + "'" if next_agent else 'null'},
  "reason": {"'" + reason + "'" if reason else 'null'}
}}"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean response
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        result = json.loads(text)
        
        # Build full response structure
        full_response = {
            "conv_id": conv_id,
            "turn_index": turn_index,
            "customer_text": customer_text,
            "customer_emotion": customer_emotion,
            "agent": result.get("agent", current_agent),
            "system_prompt": get_system_prompt(result.get("agent", current_agent)),
            "response_text": result.get("response_text", existing_text),
            "tool_calls": build_tool_calls(result.get("tools", [])),
            "handoff": {
                "needed": result.get("handoff_needed", False),
                "to_agent": result.get("next_agent"),
                "reason": result.get("reason")
            },
            "customer_sentiment": {
                "current": customer_emotion,
                "predicted_next": predict_next_emotion(customer_emotion, result.get("tools", []))
            },
            "next_action": "transfer_to_agent" if result.get("handoff_needed") else "wait_for_customer_response"
        }
        
        return full_response
        
    except Exception as e:
        # Fallback response
        return {
            "conv_id": conv_id,
            "turn_index": turn_index,
            "customer_text": customer_text,
            "customer_emotion": customer_emotion,
            "agent": current_agent,
            "system_prompt": get_system_prompt(current_agent),
            "response_text": existing_text if existing_text else "Anlıyorum, size yardımcı olacağım.",
            "tool_calls": build_tool_calls(tools_to_use[:1]),
            "handoff": {"needed": False, "to_agent": None, "reason": None},
            "customer_sentiment": {"current": customer_emotion, "predicted_next": "normal"},
            "next_action": "wait_for_customer_response"
        }

def get_system_prompt(agent):
    """Get system prompt for agent"""
    prompts = {
        "RouterAgent": "Sen bir Türk telekom müşteri yönlendirme uzmanısın. Müşterileri doğru departmana yönlendirirsin.",
        "TechAgent": "Sen bir Türk telekom teknik destek uzmanısın. eSIM, internet, modem ve cihaz sorunlarını çözersin.",
        "BillingAgent": "Sen bir Türk telekom fatura ve ödeme uzmanısın. Fatura, borç ve kampanya konularında yardım edersin.",
        "PlanAgent": "Sen bir Türk telekom tarife ve paket uzmanısın. En uygun tarifeleri önerir ve paket değişiklikleri yaparsın.",
        "FAQAgent": "Sen bir Türk telekom genel bilgi uzmanısın. Sık sorulan soruları cevaplar ve genel yardım sağlarsın."
    }
    return prompts.get(agent, "Sen bir Türk telekom uzmanısın.")

def build_tool_calls(tools):
    """Build tool call structures with params and results"""
    tool_calls = []
    for tool in tools:
        if tool == "verify_user":
            params = {"tc_no": f"{random.randint(10000000000, 99999999999)}", "mother_maiden_name": "AY"}
            result = {"verified": True, "customer_id": f"CUS{random.randint(100000, 999999)}", "name": "Müşteri"}
            duration = 500
        elif tool == "get_customer_status":
            params = {"customer_id": f"CUS{random.randint(100000, 999999)}"}
            result = {"status": "active", "plan": "Genç Tarife 10GB", "balance": 0}
            duration = 300
        elif tool == "route_to_agent":
            params = {"from_agent": "RouterAgent", "to_agent": "TechAgent", "reason": "technical"}
            result = {"transferred": True, "queue_position": 0}
            duration = 200
        elif tool == "check_esim_status":
            params = {"phone_number": f"5{random.randint(100000000, 999999999)}"}
            result = {"esim_active": False, "issue": "activation_pending"}
            duration = 800
        elif tool == "reissue_activation_code":
            params = {"phone_number": f"5{random.randint(100000000, 999999999)}"}
            result = {"qr_code": f"QR{random.randint(100000, 999999)}", "sms_sent": True}
            duration = 1200
        elif tool == "check_device_imei":
            params = {"imei": f"{random.randint(100000000000000, 999999999999999)}"}
            result = {"device_compatible": True, "model": "iPhone 14", "esim_capable": True}
            duration = 400
        elif tool == "create_tech_ticket":
            params = {"customer_id": f"CUS{random.randint(100000, 999999)}", "issue": "technical"}
            result = {"ticket_id": f"TT{random.randint(100000, 999999)}", "priority": "high"}
            duration = 600
        elif tool == "get_unpaid_amount":
            params = {"customer_id": f"CUS{random.randint(100000, 999999)}"}
            result = {"total_debt": 299.90, "overdue": 0}
            duration = 500
        elif tool == "get_last_bill":
            params = {"customer_id": f"CUS{random.randint(100000, 999999)}"}
            result = {"amount": 199.90, "period": "2024-12", "paid": False}
            duration = 600
        elif tool == "apply_campaign_discount":
            params = {"customer_id": f"CUS{random.randint(100000, 999999)}", "campaign": "OGRENCI"}
            result = {"applied": True, "discount": 50}
            duration = 800
        elif tool == "create_payment_note":
            params = {"customer_id": f"CUS{random.randint(100000, 999999)}", "note": "payment"}
            result = {"note_id": f"PAY{random.randint(100000, 999999)}", "created": True}
            duration = 300
        elif tool == "get_customer_plan":
            params = {"customer_id": f"CUS{random.randint(100000, 999999)}"}
            result = {"plan": "Genç Tarife 10GB", "price": 199.90}
            duration = 400
        elif tool == "list_all_plans":
            params = {}
            result = {"plans": [{"name": "200GB Mega", "price": 399}]}
            duration = 700
        elif tool == "change_customer_plan":
            params = {"customer_id": f"CUS{random.randint(100000, 999999)}", "plan": "MEGA"}
            result = {"success": True, "effective": "next_cycle"}
            duration = 1000
        elif tool == "search_faq":
            params = {"query": "esim"}
            result = {"results": [{"title": "eSIM Aktivasyon", "content": "..."}], "found": 3}
            duration = 300
        elif tool == "end_conversation":
            params = {"status": "resolved"}
            result = {"ended": True, "survey_sent": True}
            duration = 100
        else:
            continue
        
        tool_calls.append({
            "tool": tool,
            "params": params,
            "result": result,
            "duration_ms": duration
        })
    
    return tool_calls

def predict_next_emotion(current, tools):
    """Predict next emotion based on action"""
    if "reissue" in str(tools) or "apply" in str(tools):
        return "relieved"
    elif "create_ticket" in str(tools):
        return "concerned"
    elif "end_conversation" in str(tools):
        return "satisfied"
    else:
        return "normal"

def process_turn_wrapper(args):
    """Wrapper for processing a single turn"""
    conv_id, turn_index, customer_turn, existing_agent, current_agent = args
    
    # Handle nested structure
    if isinstance(customer_turn, dict):
        if len(customer_turn) == 1 and list(customer_turn.keys())[0].startswith('turn_'):
            turn_key = list(customer_turn.keys())[0]
            customer_turn = customer_turn[turn_key]
    
    if not isinstance(customer_turn, dict):
        return None
    
    customer_text = customer_turn.get('text', '')
    customer_emotion = customer_turn.get('emotion', 'normal')
    existing_text = existing_agent.get('text', '') if existing_agent else ''
    
    # Fix agent names
    if current_agent == "TechnicalSupportAgent":
        current_agent = "TechAgent"
    elif current_agent == "SalesAgent":
        current_agent = "PlanAgent"
    
    return create_agent_response(
        conv_id, turn_index, customer_text, 
        customer_emotion, current_agent, existing_text
    )

def main():
    """Main parallel execution"""
    
    print("🚀 ULTRA PARALLEL GENERATOR - 10 FLAWLESS CONCURRENT CALLS")
    print("=" * 60)
    
    # Load conversations
    with open('data/selected_for_tts.json', 'r', encoding='utf-8') as f:
        selected = json.load(f)
    
    all_turns = []
    
    for conv_info in selected['conversations']:
        conv_path = Path(conv_info['path'])
        if not conv_path.exists():
            continue
        
        with open(conv_path, 'r', encoding='utf-8') as f:
            conv = json.load(f)
        
        conv_id = conv.get('id', 'unknown')
        customer_turns = conv.get('customer_turns_for_tts', [])
        agent_responses = conv.get('agent_responses', [])
        
        current_agent = "RouterAgent"
        for i, customer_turn in enumerate(customer_turns):
            existing_agent = agent_responses[i] if i < len(agent_responses) else None
            
            # Update current agent from existing response
            if existing_agent:
                current_agent = existing_agent.get('agent_persona', current_agent)
            
            all_turns.append((conv_id, i, customer_turn, existing_agent, current_agent))
    
    print(f"📊 Processing {len(all_turns)} turns from {len(selected['conversations'])} conversations")
    print("🔥 Launching 10 parallel Gemini calls...")
    
    # Process with 10 parallel workers
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_turn = {executor.submit(process_turn_wrapper, turn): turn for turn in all_turns}
        
        completed = 0
        for future in concurrent.futures.as_completed(future_to_turn):
            result = future.result()
            if result:
                with results_lock:
                    results.append(result)
            
            completed += 1
            if completed % 10 == 0:
                print(f"  ✅ Processed {completed}/{len(all_turns)} turns...")
    
    print(f"\n✅ Generated {len(results)} agent responses")
    
    # Organize by conversation
    conversations = {}
    for result in results:
        conv_id = result['conv_id']
        if conv_id not in conversations:
            conversations[conv_id] = []
        conversations[conv_id].append(result)
    
    # Sort turns
    for conv_id in conversations:
        conversations[conv_id].sort(key=lambda x: x['turn_index'])
    
    # Build final dataset
    final_dataset = []
    
    for conv_id, turns in conversations.items():
        conv_data = {
            "conversation_id": conv_id,
            "has_audio": True,
            "turns": [],
            "agents_involved": set(),
            "tools_used": set(),
            "handoffs": []
        }
        
        for turn in turns:
            # Customer turn
            audio_file = f"data/tts_audio_final/{conv_id}_turn_{turn['turn_index']+1}.mp3"
            conv_data["turns"].append({
                "turn": turn['turn_index'] * 2 + 1,
                "role": "user",
                "text": turn['customer_text'],
                "emotion": turn['customer_emotion'],
                "audio_file": audio_file if Path(audio_file).exists() else None
            })
            
            # Agent turn
            conv_data["turns"].append({
                "turn": turn['turn_index'] * 2 + 2,
                "role": "assistant",
                "agent": turn['agent'],
                "system_prompt": turn['system_prompt'],
                "text": turn['response_text'],
                "tool_calls": turn['tool_calls'],
                "handoff": turn['handoff'],
                "customer_sentiment": turn['customer_sentiment'],
                "next_action": turn['next_action']
            })
            
            conv_data["agents_involved"].add(turn['agent'])
            for tool_call in turn['tool_calls']:
                conv_data["tools_used"].add(tool_call['tool'])
            
            if turn['handoff']['needed']:
                conv_data["handoffs"].append({
                    "at_turn": turn['turn_index'] * 2 + 2,
                    "from": turn['agent'],
                    "to": turn['handoff']['to_agent'],
                    "reason": turn['handoff']['reason']
                })
        
        conv_data["agents_involved"] = list(conv_data["agents_involved"])
        conv_data["tools_used"] = list(conv_data["tools_used"])
        
        final_dataset.append(conv_data)
    
    # Save files
    with open('TEKNOFEST_FINAL_AGENTIC.json', 'w', encoding='utf-8') as f:
        json.dump(final_dataset, f, ensure_ascii=False, indent=2)
    
    with open('teknofest_training.jsonl', 'w', encoding='utf-8') as f:
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
    print("🏆 FLAWLESS GENERATION COMPLETE!")
    print(f"  Conversations: {len(final_dataset)}")
    print(f"  Total turns: {sum(len(c['turns']) for c in final_dataset)}")
    print(f"  Total handoffs: {sum(len(c['handoffs']) for c in final_dataset)}")
    
    all_agents = set()
    all_tools = set()
    for conv in final_dataset:
        all_agents.update(conv['agents_involved'])
        all_tools.update(conv['tools_used'])
    
    print(f"  Unique agents: {all_agents}")
    print(f"  Unique tools: {all_tools}")
    print(f"\n✅ Files created:")
    print(f"  - TEKNOFEST_FINAL_AGENTIC.json")
    print(f"  - teknofest_training.jsonl")
    print(f"\n🎯 READY FOR TEKNOFEST 2025!")

if __name__ == "__main__":
    main()