#!/usr/bin/env python3
"""
Test Gemini generation with a single example
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
    "max_output_tokens": 1500,
    "candidate_count": 1
}

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    generation_config=generation_config
)

# Test with actual customer turn
customer_text = "Alo, merhaba. Acil bir durumum var. eSIM'im aktive olmuyor ve ben yurtdışında okuyorum, internetsiz kaldım."
customer_emotion = "worried"
current_agent = "RouterAgent"
turn_index = 0

prompt = f"""Generate a Turkish telco agent response with full agentic capabilities.

Customer ({customer_emotion}): "{customer_text}"
Current Agent: {current_agent}
Turn: {turn_index + 1}

RULES:
- RouterAgent always verifies user first (turn 1)
- Use these exact tools: verify_user for turn 1, then get_customer_status and route_to_agent
- Include tool execution with params and results
- System prompt in Turkish

Return ONLY this JSON structure:
{{
    "agent": "{current_agent}",
    "system_prompt": "Sen bir Türk telekom müşteri yönlendirme uzmanısın. Müşterileri doğru departmana yönlendirirsin.",
    "response_text": "Professional Turkish response here",
    "tool_calls": [
        {{
            "tool": "verify_user",
            "params": {{"tc_no": "12345678901", "mother_maiden_name": "AY"}},
            "result": {{"verified": true, "customer_id": "CUS123456", "name": "Müşteri"}},
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
        "predicted_next": "concerned"
    }},
    "next_action": "wait_for_customer_response"
}}"""

print("🔍 Testing Gemini generation...")
print(f"Customer: {customer_text}")
print(f"Emotion: {customer_emotion}")
print(f"Agent: {current_agent}")
print(f"Turn: {turn_index + 1}")
print("\n📡 Calling Gemini API...")

try:
    response = model.generate_content(prompt)
    text = response.text.strip()
    
    # Clean JSON
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    
    result = json.loads(text)
    
    print("\n✅ GENERATED RESPONSE:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # Validate
    print("\n🔍 VALIDATION:")
    print(f"  ✓ Agent: {result.get('agent')}")
    print(f"  ✓ System prompt: {'✓' if result.get('system_prompt') else '✗'}")
    print(f"  ✓ Response text: {result.get('response_text')[:50]}...")
    print(f"  ✓ Tool calls: {len(result.get('tool_calls', []))} tools")
    
    if result.get('tool_calls'):
        for tc in result['tool_calls']:
            print(f"    - {tc['tool']}: params={bool(tc.get('params'))}, result={bool(tc.get('result'))}, duration={tc.get('duration_ms')}ms")
    
    print(f"  ✓ Handoff: {result.get('handoff', {}).get('needed')}")
    print(f"  ✓ Sentiment: {result.get('customer_sentiment', {}).get('current')} → {result.get('customer_sentiment', {}).get('predicted_next')}")
    print(f"  ✓ Next action: {result.get('next_action')}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print(f"Raw response: {response.text if 'response' in locals() else 'No response'}")