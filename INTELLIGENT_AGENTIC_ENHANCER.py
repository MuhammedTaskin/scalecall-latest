#!/usr/bin/env python3
"""
INTELLIGENT AGENTIC ENHANCER
Enhances dataset with full agentic capabilities using pattern matching and domain knowledge
"""

import json
from pathlib import Path
from datetime import datetime
import random

# Agent system prompts
AGENT_PROMPTS = {
    "RouterAgent": "Sen bir Türk telekom müşteri yönlendirme uzmanısın. Müşterileri doğru departmana yönlendirirsin.",
    "TechAgent": "Sen bir Türk telekom teknik destek uzmanısın. eSIM, internet, modem ve cihaz sorunlarını çözersin.",
    "BillingAgent": "Sen bir Türk telekom fatura ve ödeme uzmanısın. Fatura, borç ve kampanya konularında yardım edersin.",
    "PlanAgent": "Sen bir Türk telekom tarife ve paket uzmanısın. En uygun tarifeleri önerir ve paket değişiklikleri yaparsın.",
    "FAQAgent": "Sen bir Türk telekom genel bilgi uzmanısın. Sık sorulan soruları cevaplar ve genel yardım sağlarsın."
}

# Tool execution patterns
TOOL_PATTERNS = {
    "verify_user": {
        "params": lambda: {"tc_no": f"{random.randint(10000000000, 99999999999)}", "mother_maiden_name": "AY"},
        "result": lambda: {"verified": True, "customer_id": f"CUS{random.randint(100000, 999999)}", "name": "Müşteri"},
        "duration_ms": 500
    },
    "get_customer_status": {
        "params": lambda: {"customer_id": f"CUS{random.randint(100000, 999999)}"},
        "result": lambda: {"status": "active", "plan": "Genç Tarife 10GB", "balance": 0},
        "duration_ms": 300
    },
    "route_to_agent": {
        "params": lambda: {"from_agent": "RouterAgent", "to_agent": "TechAgent", "reason": "technical_issue"},
        "result": lambda: {"transferred": True, "queue_position": 0},
        "duration_ms": 200
    },
    "check_esim_status": {
        "params": lambda: {"phone_number": f"5{random.randint(100000000, 999999999)}"},
        "result": lambda: {"esim_active": False, "issue": "activation_pending", "last_attempt": datetime.now().isoformat()},
        "duration_ms": 800
    },
    "check_device_imei": {
        "params": lambda: {"imei": f"{random.randint(100000000000000, 999999999999999)}"},
        "result": lambda: {"device_compatible": True, "model": "iPhone 14 Pro", "esim_capable": True},
        "duration_ms": 400
    },
    "reissue_activation_code": {
        "params": lambda: {"phone_number": f"5{random.randint(100000000, 999999999)}"},
        "result": lambda: {"qr_code": f"QR{random.randint(100000, 999999)}", "sms_sent": True, "expires_in": "24h"},
        "duration_ms": 1200
    },
    "get_last_bill": {
        "params": lambda: {"customer_id": f"CUS{random.randint(100000, 999999)}"},
        "result": lambda: {"amount": round(random.uniform(100, 500), 2), "period": "2024-12", "paid": False},
        "duration_ms": 600
    },
    "get_unpaid_amount": {
        "params": lambda: {"customer_id": f"CUS{random.randint(100000, 999999)}"},
        "result": lambda: {"total_debt": round(random.uniform(100, 1000), 2), "overdue": round(random.uniform(0, 500), 2)},
        "duration_ms": 500
    },
    "get_customer_plan": {
        "params": lambda: {"customer_id": f"CUS{random.randint(100000, 999999)}"},
        "result": lambda: {"plan_name": "Genç Tarife 10GB", "monthly_fee": 199.90, "data_limit": "10GB"},
        "duration_ms": 400
    },
    "list_all_plans": {
        "params": lambda: {},
        "result": lambda: {"plans": [{"name": "200GB Mega", "price": 399}, {"name": "Sınırsız Pro", "price": 599}]},
        "duration_ms": 700
    },
    "change_customer_plan": {
        "params": lambda: {"customer_id": f"CUS{random.randint(100000, 999999)}", "new_plan_id": "PLAN_MEGA"},
        "result": lambda: {"success": True, "effective_date": "next_billing_cycle"},
        "duration_ms": 1000
    },
    "apply_campaign_discount": {
        "params": lambda: {"customer_id": f"CUS{random.randint(100000, 999999)}", "campaign_code": "OGRENCI2024"},
        "result": lambda: {"applied": True, "discount_amount": 50, "valid_for_months": 3},
        "duration_ms": 800
    },
    "create_tech_ticket": {
        "params": lambda: {"customer_id": f"CUS{random.randint(100000, 999999)}", "issue": "esim_activation"},
        "result": lambda: {"ticket_id": f"TT{random.randint(100000, 999999)}", "priority": "high"},
        "duration_ms": 600
    },
    "create_payment_note": {
        "params": lambda: {"customer_id": f"CUS{random.randint(100000, 999999)}", "note": "Ödeme taahhüdü"},
        "result": lambda: {"note_id": f"PAY{random.randint(100000, 999999)}", "created": True},
        "duration_ms": 300
    },
    "search_faq": {
        "params": lambda: {"query": "esim aktivasyon"},
        "result": lambda: {"results": [{"title": "eSIM Aktivasyon", "content": "QR kod taratın..."}], "found": 3},
        "duration_ms": 300
    },
    "end_conversation": {
        "params": lambda: {"resolution_status": "resolved"},
        "result": lambda: {"ended": True, "satisfaction_survey_sent": True},
        "duration_ms": 100
    }
}

def determine_handoff(current_agent, customer_text, turn_index):
    """Intelligently determine if handoff is needed based on context"""
    
    text_lower = customer_text.lower()
    
    # RouterAgent hands off after verification
    if current_agent == "RouterAgent" and turn_index > 0:
        if "esim" in text_lower or "internet" in text_lower or "modem" in text_lower:
            return {"needed": True, "to_agent": "TechAgent", "reason": "Teknik sorun tespit edildi"}
        elif "fatura" in text_lower or "borç" in text_lower or "ödeme" in text_lower:
            return {"needed": True, "to_agent": "BillingAgent", "reason": "Fatura sorunu tespit edildi"}
        elif "paket" in text_lower or "tarife" in text_lower or "kampanya" in text_lower:
            return {"needed": True, "to_agent": "PlanAgent", "reason": "Tarife değişikliği talebi"}
        else:
            return {"needed": True, "to_agent": "FAQAgent", "reason": "Genel bilgi talebi"}
    
    # TechAgent hands off for billing after resolving tech issue
    if current_agent == "TechAgent" and ("fatura" in text_lower or "ücret" in text_lower or "paket" in text_lower):
        if "fatura" in text_lower or "borç" in text_lower:
            return {"needed": True, "to_agent": "BillingAgent", "reason": "Müşteri fatura sorunu belirtti"}
        elif "paket" in text_lower or "tarife" in text_lower:
            return {"needed": True, "to_agent": "PlanAgent", "reason": "Müşteri tarife değişikliği istiyor"}
    
    return {"needed": False, "to_agent": None, "reason": None}

def generate_tool_calls(agent, customer_text, turn_index):
    """Generate appropriate tool calls based on agent and context"""
    
    tool_calls = []
    text_lower = customer_text.lower()
    
    if agent == "RouterAgent":
        if turn_index == 0:
            # First turn: always verify user
            tool = "verify_user"
            tool_calls.append({
                "tool": tool,
                "params": TOOL_PATTERNS[tool]["params"](),
                "result": TOOL_PATTERNS[tool]["result"](),
                "duration_ms": TOOL_PATTERNS[tool]["duration_ms"]
            })
        else:
            # Get customer status and route
            for tool in ["get_customer_status", "route_to_agent"]:
                if tool in TOOL_PATTERNS:
                    tool_calls.append({
                        "tool": tool,
                        "params": TOOL_PATTERNS[tool]["params"](),
                        "result": TOOL_PATTERNS[tool]["result"](),
                        "duration_ms": TOOL_PATTERNS[tool]["duration_ms"]
                    })
    
    elif agent == "TechAgent":
        if "esim" in text_lower:
            tools = ["check_esim_status", "check_device_imei", "reissue_activation_code"]
        elif "internet" in text_lower or "bağlan" in text_lower:
            tools = ["check_device_imei", "create_tech_ticket"]
        else:
            tools = ["check_esim_status"]
        
        for tool in tools[:2]:  # Use 1-2 tools
            if tool in TOOL_PATTERNS:
                tool_calls.append({
                    "tool": tool,
                    "params": TOOL_PATTERNS[tool]["params"](),
                    "result": TOOL_PATTERNS[tool]["result"](),
                    "duration_ms": TOOL_PATTERNS[tool]["duration_ms"]
                })
    
    elif agent == "BillingAgent":
        if "borç" in text_lower or "öde" in text_lower:
            tools = ["get_unpaid_amount", "get_last_bill"]
        elif "kampanya" in text_lower or "indirim" in text_lower:
            tools = ["apply_campaign_discount", "create_payment_note"]
        else:
            tools = ["get_last_bill"]
        
        for tool in tools[:2]:
            if tool in TOOL_PATTERNS:
                tool_calls.append({
                    "tool": tool,
                    "params": TOOL_PATTERNS[tool]["params"](),
                    "result": TOOL_PATTERNS[tool]["result"](),
                    "duration_ms": TOOL_PATTERNS[tool]["duration_ms"]
                })
    
    elif agent == "PlanAgent":
        if "değiş" in text_lower or "geç" in text_lower:
            tools = ["get_customer_plan", "list_all_plans", "change_customer_plan"]
        else:
            tools = ["get_customer_plan", "list_all_plans"]
        
        for tool in tools[:2]:
            if tool in TOOL_PATTERNS:
                tool_calls.append({
                    "tool": tool,
                    "params": TOOL_PATTERNS[tool]["params"](),
                    "result": TOOL_PATTERNS[tool]["result"](),
                    "duration_ms": TOOL_PATTERNS[tool]["duration_ms"]
                })
    
    elif agent == "FAQAgent":
        tool = "search_faq"
        if tool in TOOL_PATTERNS:
            tool_calls.append({
                "tool": tool,
                "params": TOOL_PATTERNS[tool]["params"](),
                "result": TOOL_PATTERNS[tool]["result"](),
                "duration_ms": TOOL_PATTERNS[tool]["duration_ms"]
            })
    
    # Add end_conversation for final turns
    if "teşekkür" in text_lower or "sağ ol" in text_lower or turn_index > 5:
        tool = "end_conversation"
        if tool in TOOL_PATTERNS:
            tool_calls.append({
                "tool": tool,
                "params": TOOL_PATTERNS[tool]["params"](),
                "result": TOOL_PATTERNS[tool]["result"](),
                "duration_ms": TOOL_PATTERNS[tool]["duration_ms"]
            })
    
    return tool_calls

def predict_sentiment(current_emotion, agent_action):
    """Predict next customer sentiment based on current emotion and agent action"""
    
    sentiment_flow = {
        "worried": ["concerned", "relieved", "thankful"],
        "angry": ["frustrated", "concerned", "satisfied"],
        "confused": ["concerned", "understanding", "satisfied"],
        "frustrated": ["angry", "concerned", "relieved"],
        "concerned": ["worried", "relieved", "satisfied"],
        "normal": ["satisfied", "thankful", "happy"],
        "anxious": ["worried", "relieved", "thankful"],
        "relieved": ["thankful", "satisfied", "happy"],
        "thankful": ["satisfied", "happy", "normal"],
        "satisfied": ["happy", "thankful", "normal"]
    }
    
    if current_emotion in sentiment_flow:
        # If agent provides solution, move towards positive
        if any(tool in str(agent_action) for tool in ["reissue", "apply", "change", "create"]):
            return sentiment_flow[current_emotion][-1]  # Most positive
        else:
            return sentiment_flow[current_emotion][1]  # Middle state
    
    return "normal"

def enhance_conversation(conv_path):
    """Enhance a single conversation with FULL agentic capabilities"""
    
    with open(conv_path, 'r', encoding='utf-8') as f:
        conv = json.load(f)
    
    conv_id = conv.get('id', 'unknown')
    
    result = {
        "conversation_id": conv_id,
        "has_audio": True,
        "audio_files": [],
        "turns": [],
        "agents_involved": set(),
        "tools_used": set(),
        "handoffs": [],
        "sentiment_journey": []
    }
    
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
        
        customer_text = customer_turn.get('text', '')
        customer_emotion = customer_turn.get('emotion', 'normal')
        
        # Add customer turn
        audio_file = f"data/tts_audio_final/{conv_id}_turn_{i+1}.mp3"
        result["turns"].append({
            "turn": i * 2 + 1,
            "role": "user",
            "text": customer_text,
            "emotion": customer_emotion,
            "audio_file": audio_file if Path(audio_file).exists() else None
        })
        
        if Path(audio_file).exists():
            result["audio_files"].append(audio_file)
        
        # Get existing agent response or use current agent
        if i < len(agent_responses):
            existing = agent_responses[i]
            agent_text = existing.get('text', '')
            # Map invalid agent names
            agent_name = existing.get('agent_persona', current_agent)
            if agent_name == "TechnicalSupportAgent":
                agent_name = "TechAgent"
            elif agent_name == "SalesAgent":
                agent_name = "PlanAgent"
            current_agent = agent_name
        else:
            agent_text = "Anlıyorum, size yardımcı olacağım."
        
        # Generate intelligent tool calls
        tool_calls = generate_tool_calls(current_agent, customer_text, i)
        
        # Determine handoff
        handoff = determine_handoff(current_agent, customer_text, i)
        
        # Predict sentiment
        predicted_sentiment = predict_sentiment(customer_emotion, tool_calls)
        
        # Create rich agent response
        agent_turn = {
            "turn": i * 2 + 2,
            "role": "assistant",
            "agent": current_agent,
            "system_prompt": AGENT_PROMPTS[current_agent],
            "text": agent_text,
            "tool_calls": tool_calls,
            "handoff": handoff,
            "customer_sentiment": {
                "current": customer_emotion,
                "predicted_next": predicted_sentiment
            },
            "next_action": "wait_for_customer_response" if not handoff["needed"] else "transfer_to_agent"
        }
        
        result["turns"].append(agent_turn)
        result["agents_involved"].add(current_agent)
        
        # Track tools
        for tc in tool_calls:
            result["tools_used"].add(tc["tool"])
        
        # Track handoffs
        if handoff["needed"]:
            result["handoffs"].append({
                "at_turn": i * 2 + 2,
                "from": current_agent,
                "to": handoff["to_agent"],
                "reason": handoff["reason"]
            })
            current_agent = handoff["to_agent"]
        
        # Track sentiment journey
        result["sentiment_journey"].append({
            "turn": i + 1,
            "emotion": customer_emotion,
            "predicted": predicted_sentiment
        })
    
    # Convert sets to lists
    result["agents_involved"] = list(result["agents_involved"])
    result["tools_used"] = list(result["tools_used"])
    
    return result

def main():
    """Process all selected conversations with intelligence"""
    
    print("🧠 INTELLIGENT AGENTIC DATASET ENHANCER")
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
                'complexity': 'high',
                'region': 'turkey',
                'generated_at': datetime.now().isoformat(),
                'model': 'intelligent_enhancer_v2',
                'audio_count': len(result['audio_files']),
                'tool_count': len(result['tools_used']),
                'agent_count': len(result['agents_involved'])
            }
            dataset.append(result)
            print(f" ✅ {len(result['agents_involved'])} agents, {len(result['tools_used'])} tools, {len(result['handoffs'])} handoffs")
        except Exception as e:
            print(f" ❌ Error: {e}")
    
    # Save complete dataset
    with open('INTELLIGENT_AGENTIC_DATASET.json', 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    # Create training JSONL with full structure
    with open('intelligent_training.jsonl', 'w', encoding='utf-8') as f:
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
                        "system_prompt": agent['system_prompt'],
                        "agent_response": agent['text'],
                        "tool_calls": agent['tool_calls'],
                        "handoff": agent['handoff'],
                        "customer_sentiment": agent['customer_sentiment'],
                        "next_action": agent['next_action']
                    }
                    f.write(json.dumps(training_item, ensure_ascii=False) + '\n')
    
    # Statistics
    print("\n" + "=" * 60)
    print("🎯 INTELLIGENT ENHANCEMENT COMPLETE!")
    print(f"  Total conversations: {len(dataset)}")
    print(f"  Total turns: {sum(len(c['turns']) for c in dataset)}")
    print(f"  Total handoffs: {sum(len(c['handoffs']) for c in dataset)}")
    
    all_agents = set()
    all_tools = set()
    for conv in dataset:
        all_agents.update(conv['agents_involved'])
        all_tools.update(conv['tools_used'])
    
    print(f"  Unique agents: {all_agents}")
    print(f"  Unique tools ({len(all_tools)}): {all_tools}")
    print(f"\n✅ Files created:")
    print(f"  - INTELLIGENT_AGENTIC_DATASET.json (complete dataset)")
    print(f"  - intelligent_training.jsonl (training pairs)")
    print(f"\n🏆 READY FOR TEKNOFEST 2025!")
    print("  ✓ Tool execution with params & results")
    print("  ✓ System prompts for each agent")
    print("  ✓ Intelligent handoff decisions")
    print("  ✓ Customer sentiment tracking")
    print("  ✓ Next action planning")

if __name__ == "__main__":
    main()