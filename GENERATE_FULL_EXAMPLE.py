#!/usr/bin/env python3
"""
Generate a complete conversation example with Gemini
"""

import json
import os
import google.generativeai as genai

# Configure
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("❌ No API key!")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

# Deterministic config
generation_config = {
    "temperature": 0.1,
    "top_p": 0.9,
    "top_k": 20,
    "max_output_tokens": 2000,
    "candidate_count": 1
}

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    generation_config=generation_config
)

# Load an actual conversation
from pathlib import Path

# Get the first conversation with audio
conv_path = Path("data/flash_heavy_dataset/flash_heavy_0174.json")
with open(conv_path, 'r', encoding='utf-8') as f:
    conv = json.load(f)

conv_id = conv['id']
customer_turns = conv.get('customer_turns_for_tts', [])
agent_responses = conv.get('agent_responses', [])

print(f"🎯 GENERATING FULL EXAMPLE FOR: {conv_id}")
print("=" * 60)

# Process first 3 turns as example
full_conversation = {
    "conversation_id": conv_id,
    "has_audio": True,
    "turns": [],
    "agents_involved": [],
    "tools_used": [],
    "handoffs": []
}

current_agent = "RouterAgent"

for i in range(min(3, len(customer_turns))):
    # Get customer turn
    customer_turn = customer_turns[i]
    
    # Handle nested structure
    if isinstance(customer_turn, dict):
        if len(customer_turn) == 1 and list(customer_turn.keys())[0].startswith('turn_'):
            turn_key = list(customer_turn.keys())[0]
            customer_turn = customer_turn[turn_key]
    
    customer_text = customer_turn.get('text', '')
    customer_emotion = customer_turn.get('emotion', 'normal')
    
    # Add customer turn
    audio_file = f"data/tts_audio_final/{conv_id}_turn_{i+1}.mp3"
    full_conversation["turns"].append({
        "turn": i * 2 + 1,
        "role": "user",
        "text": customer_text,
        "emotion": customer_emotion,
        "audio_file": audio_file if Path(audio_file).exists() else None
    })
    
    print(f"\n📢 Turn {i+1} - Customer ({customer_emotion}):")
    print(f"   \"{customer_text[:100]}...\"")
    
    # Get existing agent response for reference
    existing_agent = agent_responses[i] if i < len(agent_responses) else None
    existing_text = existing_agent.get('text', '') if existing_agent else ''
    
    # Update current agent from existing response
    if existing_agent:
        existing_agent_name = existing_agent.get('agent_persona', current_agent)
        if existing_agent_name == "TechnicalSupportAgent":
            existing_agent_name = "TechAgent"
        elif existing_agent_name == "SalesAgent":
            existing_agent_name = "PlanAgent"
        current_agent = existing_agent_name
    
    # Generate with Gemini
    text_lower = customer_text.lower()
    
    # Determine tools and handoff based on turn
    if i == 0:
        tools_str = '["verify_user"]'
        handoff_needed = "false"
        next_agent = "null"
        reason = "null"
    elif i == 1 and current_agent == "RouterAgent":
        tools_str = '["get_customer_status", "route_to_agent"]'
        handoff_needed = "true"
        next_agent = '"TechAgent"' if "esim" in text_lower else '"FAQAgent"'
        reason = '"Teknik sorun tespit edildi"' if "esim" in text_lower else '"Genel bilgi talebi"'
    else:
        if current_agent == "TechAgent":
            tools_str = '["check_esim_status", "reissue_activation_code"]' if "esim" in text_lower else '["check_device_imei"]'
        elif current_agent == "BillingAgent":
            tools_str = '["get_last_bill", "get_unpaid_amount"]'
        elif current_agent == "PlanAgent":
            tools_str = '["get_customer_plan", "list_all_plans"]'
        else:
            tools_str = '["search_faq"]'
        
        handoff_needed = "true" if ("fatura" in text_lower or "paket" in text_lower) and current_agent == "TechAgent" else "false"
        next_agent = '"BillingAgent"' if "fatura" in text_lower and handoff_needed == "true" else '"PlanAgent"' if "paket" in text_lower and handoff_needed == "true" else "null"
        reason = '"Müşteri fatura sorunu belirtti"' if "fatura" in text_lower and handoff_needed == "true" else '"Müşteri paket değişikliği istiyor"' if "paket" in text_lower and handoff_needed == "true" else "null"
    
    # Get system prompt
    system_prompts = {
        'RouterAgent': 'Sen bir Türk telekom müşteri yönlendirme uzmanısın.',
        'TechAgent': 'Sen bir Türk telekom teknik destek uzmanısın.',
        'BillingAgent': 'Sen bir Türk telekom fatura uzmanısın.',
        'PlanAgent': 'Sen bir Türk telekom tarife uzmanısın.',
        'FAQAgent': 'Sen bir Türk telekom bilgi uzmanısın.'
    }
    system_prompt = system_prompts.get(current_agent, 'Sen bir Türk telekom uzmanısın.')
    
    # Get predicted sentiment
    sentiment_map = {
        'worried': 'concerned',
        'anxious': 'relieved',
        'concerned': 'relieved',
        'relieved': 'thankful',
        'budget-conscious': 'satisfied',
        'thankful': 'satisfied'
    }
    predicted_sentiment = sentiment_map.get(customer_emotion, 'normal')
    
    next_action = 'transfer_to_agent' if handoff_needed == 'true' else 'wait_for_customer_response'
    
    prompt = f"""Generate Turkish telco agent response with EXACT structure.

Customer ({customer_emotion}): "{customer_text}"
Agent: {current_agent}
Use this response text: "{existing_text}"

Return ONLY this JSON:
{{
    "agent": "{current_agent}",
    "system_prompt": "{system_prompt}",
    "response_text": "{existing_text if existing_text else 'Anlıyorum, size yardımcı olacağım.'}",
    "tool_calls": {tools_str},
    "handoff": {{
        "needed": {handoff_needed},
        "to_agent": {next_agent},
        "reason": {reason}
    }},
    "customer_sentiment": {{
        "current": "{customer_emotion}",
        "predicted_next": "{predicted_sentiment}"
    }},
    "next_action": "{next_action}"
}}

Add realistic params and results for each tool."""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean JSON
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        result = json.loads(text)
        
        # Add full tool execution details
        tool_calls_with_details = []
        for tool in result.get('tool_calls', []):
            if isinstance(tool, str):
                # Add params and results
                if tool == "verify_user":
                    tool_call = {
                        "tool": tool,
                        "params": {"tc_no": "12345678910", "mother_maiden_name": "YI"},
                        "result": {"verified": True, "customer_id": "CUS174890", "name": "Can Yılmaz"},
                        "duration_ms": 500
                    }
                elif tool == "get_customer_status":
                    tool_call = {
                        "tool": tool,
                        "params": {"customer_id": "CUS174890"},
                        "result": {"status": "active", "plan": "Genç Tarife 10GB", "balance": 0},
                        "duration_ms": 300
                    }
                elif tool == "route_to_agent":
                    tool_call = {
                        "tool": tool,
                        "params": {"from_agent": current_agent, "to_agent": result['handoff']['to_agent'], "reason": "technical_issue"},
                        "result": {"transferred": True, "queue_position": 0},
                        "duration_ms": 200
                    }
                elif tool == "check_esim_status":
                    tool_call = {
                        "tool": tool,
                        "params": {"phone_number": "5551234567"},
                        "result": {"esim_active": False, "issue": "activation_pending", "last_attempt": "2024-12-14T10:30:00"},
                        "duration_ms": 800
                    }
                elif tool == "reissue_activation_code":
                    tool_call = {
                        "tool": tool,
                        "params": {"phone_number": "5551234567"},
                        "result": {"qr_code": "QR789456", "sms_sent": True, "expires_in": "24h"},
                        "duration_ms": 1200
                    }
                elif tool == "check_device_imei":
                    tool_call = {
                        "tool": tool,
                        "params": {"imei": "356789123456789"},
                        "result": {"device_compatible": True, "model": "iPhone 14 Pro", "esim_capable": True},
                        "duration_ms": 400
                    }
                else:
                    tool_call = {
                        "tool": tool,
                        "params": {},
                        "result": {},
                        "duration_ms": 500
                    }
                tool_calls_with_details.append(tool_call)
            else:
                tool_calls_with_details.append(tool)
        
        result['tool_calls'] = tool_calls_with_details
        
        # Add agent turn
        agent_turn = {
            "turn": i * 2 + 2,
            "role": "assistant",
            "agent": result['agent'],
            "system_prompt": result['system_prompt'],
            "text": result['response_text'],
            "tool_calls": result['tool_calls'],
            "handoff": result['handoff'],
            "customer_sentiment": result['customer_sentiment'],
            "next_action": result['next_action']
        }
        
        full_conversation["turns"].append(agent_turn)
        full_conversation["agents_involved"].append(result['agent'])
        
        for tc in result['tool_calls']:
            if isinstance(tc, dict):
                full_conversation["tools_used"].append(tc['tool'])
        
        if result['handoff']['needed']:
            full_conversation["handoffs"].append({
                "at_turn": i * 2 + 2,
                "from": result['agent'],
                "to": result['handoff']['to_agent'],
                "reason": result['handoff']['reason']
            })
            current_agent = result['handoff']['to_agent']
        
        print(f"\n🤖 Agent Response ({result['agent']}):")
        print(f"   \"{result['response_text'][:100]}...\"")
        print(f"   Tools: {[tc['tool'] if isinstance(tc, dict) else tc for tc in result['tool_calls']]}")
        print(f"   Handoff: {result['handoff']['needed']} → {result['handoff']['to_agent']}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

# Clean up
full_conversation["agents_involved"] = list(set(full_conversation["agents_involved"]))
full_conversation["tools_used"] = list(set(full_conversation["tools_used"]))

# Save example
with open('GEMINI_GENERATED_EXAMPLE.json', 'w', encoding='utf-8') as f:
    json.dump(full_conversation, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 60)
print("📄 FULL GENERATED EXAMPLE SAVED TO: GEMINI_GENERATED_EXAMPLE.json")
print(f"\nSummary:")
print(f"  - Turns: {len(full_conversation['turns'])}")
print(f"  - Agents: {full_conversation['agents_involved']}")
print(f"  - Tools: {full_conversation['tools_used']}")
print(f"  - Handoffs: {len(full_conversation['handoffs'])}")

# Show one complete turn as example
print("\n🎯 EXAMPLE TURN WITH FULL AGENTIC CAPABILITIES:")
for turn in full_conversation['turns'][1:2]:  # Show second turn (first agent response)
    print(json.dumps(turn, ensure_ascii=False, indent=2))