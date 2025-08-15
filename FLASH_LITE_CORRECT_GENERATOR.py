#!/usr/bin/env python3
"""
Flash-Lite Generator with CORRECT structure (like regular Flash)
SHORT (minimum 3 turns) but with PROPER handoffs and tools
"""

import os
import json
import random
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import google.generativeai as genai

GOOGLE_API_KEY = "AIzaSyBzC3ydAP1qKkGyRkJ9t1sp5D3QN9QyzsQ"
genai.configure(api_key=GOOGLE_API_KEY)

class CorrectFlashLiteGenerator:
    def __init__(self):
        # Use Flash-Lite for SPEED
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash-lite',
            safety_settings={
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE'
            }
        )
        
        # SHORT scenarios with HANDOFFS
        self.short_scenarios = [
            {
                "issue": "esim_quick_fix",
                "handoff": ["RouterAgent", "TechAgent"],
                "min_turns": 6  # 3 customer, 3 agent
            },
            {
                "issue": "bill_question",
                "handoff": ["RouterAgent", "BillingAgent"],
                "min_turns": 6
            },
            {
                "issue": "plan_upgrade",
                "handoff": ["RouterAgent", "PlanAgent"],
                "min_turns": 6
            },
            {
                "issue": "payment_issue",
                "handoff": ["RouterAgent", "BillingAgent"],
                "min_turns": 8
            },
            {
                "issue": "tech_problem",
                "handoff": ["RouterAgent", "TechAgent"],
                "min_turns": 6
            },
            {
                "issue": "general_help",
                "handoff": ["RouterAgent", "FAQAgent"],
                "min_turns": 6
            }
        ]
        
        self.personas = ["angry", "confused", "normal", "impatient", "polite"]
        
        self.output_dir = "data/correct_flash_dataset"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_correct_conversation(self, idx: int) -> dict:
        """Generate SHORT but CORRECT conversation with handoffs"""
        
        scenario = random.choice(self.short_scenarios)
        persona = random.choice(self.personas)
        
        # EXACT SAME PROMPT STRUCTURE AS REGULAR FLASH
        prompt = f"""Türkçe telekom çağrı merkezi KISA konuşması. HANDOFF OLMALI!

SENARYO: {scenario['issue']}
MÜŞTERİ: {persona}
AGENT AKIŞI: {' → '.join(scenario['handoff'])}
UZUNLUK: Minimum {scenario['min_turns']} turn (3 müşteri, 3+ agent)

KURALLLAR:
1. RouterAgent ALWAYS starts with verify_user
2. RouterAgent MUST use route_to_agent for handoff
3. Second agent MUST use their specific tools
4. MUST have agent_handoffs section

TOOLS:
RouterAgent: verify_user, get_customer_status, route_to_agent
TechAgent: check_esim_status, check_device_imei, reissue_activation_code, create_tech_ticket
BillingAgent: get_last_bill, get_unpaid_amount, apply_campaign_discount, create_payment_note
PlanAgent: get_customer_plan, list_all_plans, change_customer_plan, check_plan_compatibility
FAQAgent: search_faq, get_common_solutions, send_help_sms, create_info_ticket
Shared: escalate_to_human, end_conversation

JSON FORMAT (EXACTLY LIKE REGULAR FLASH):
{{
  "conversation_id": "short_{idx:04d}_{scenario['issue']}",
  "metadata": {{
    "scenario": "{scenario['issue']}",
    "handoff_pattern": {json.dumps(scenario['handoff'])}
  }},
  "customer_profile": {{
    "persona": "{persona}",
    "phone": "0555 123 45 67"
  }},
  "customer_turns_for_tts": [
    {{"turn_id": "turn_001", "text": "Müşteri sorunu", "emotion": "{persona}"}},
    {{"turn_id": "turn_003", "text": "Müşteri bilgi verir"}},
    {{"turn_id": "turn_005", "text": "Müşteri cevap"}}
  ],
  "agent_responses": [
    {{"turn_id": "turn_002", "agent_persona": "RouterAgent", "text": "Kimlik doğrulama", "tools_triggered": ["verify_user"], "handoff": null}},
    {{"turn_id": "turn_004", "agent_persona": "RouterAgent", "text": "Yönlendirme", "tools_triggered": ["get_customer_status", "route_to_agent"], "handoff": {{"to": "{scenario['handoff'][1]}"}}}},
    {{"turn_id": "turn_006", "agent_persona": "{scenario['handoff'][1]}", "text": "Çözüm", "tools_triggered": ["specific_tool", "end_conversation"], "handoff": null}}
  ],
  "agent_handoffs": [
    {{"at_turn": 4, "from": "RouterAgent", "to": "{scenario['handoff'][1]}", "reason": "{scenario['issue']}"}}
  ],
  "tool_calls": [
    {{"turn_id": "turn_002", "tool": "verify_user", "arguments": {{}}, "result": true}},
    {{"turn_id": "turn_004", "tool": "route_to_agent", "arguments": {{}}, "result": true}}
  ]
}}

MINIMUM 3 CUSTOMER TURNS, HANDOFF REQUIRED!"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=4096,
                )
            )
            
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            
            # Clean JSON
            import re
            text = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)
            text = re.sub(r'"turn_id":\s*"turn_id":', r'"turn_id":', text)
            text = re.sub(r',\s*}', '}', text)
            text = re.sub(r',\s*]', ']', text)
            
            conv = json.loads(text.strip())
            conv["generated_at"] = datetime.now().isoformat()
            conv["index"] = idx
            
            # VERIFY it has handoffs
            if "agent_handoffs" in conv and len(conv.get("agent_handoffs", [])) > 0:
                return conv
            else:
                print(f"  ⚠️ No handoff in {idx}, retrying...")
                return None
                
        except Exception as e:
            print(f"  Error {idx}: {str(e)[:50]}")
            return None
    
    def generate_batch(self, num_conversations: int = 100):
        """Generate CORRECT short conversations"""
        
        print(f"🎯 CORRECT FLASH-LITE GENERATOR")
        print(f"✅ Generating {num_conversations} SHORT but CORRECT conversations")
        print(f"🔄 All will have handoffs like regular Flash")
        print("=" * 60)
        
        successful = []
        failed = 0
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.generate_correct_conversation, i): i 
                for i in range(num_conversations)
            }
            
            for future in as_completed(futures):
                idx = futures[future]
                result = future.result()
                
                if result:
                    filename = f"{self.output_dir}/short_{idx:04d}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    
                    successful.append(result)
                    
                    if len(successful) % 10 == 0:
                        print(f"  ✅ Progress: {len(successful)}/{num_conversations}")
                else:
                    failed += 1
                
                if len(successful) % 20 == 0:
                    time.sleep(2)  # Rate limit
        
        # Verify handoffs
        handoff_count = 0
        for conv in successful:
            if "agent_handoffs" in conv and len(conv.get("agent_handoffs", [])) > 0:
                handoff_count += 1
        
        print("\n" + "=" * 60)
        print(f"✅ GENERATION COMPLETE!")
        print(f"📊 Success: {len(successful)}/{num_conversations} ({100*len(successful)/num_conversations:.1f}%)")
        print(f"🔄 Conversations with handoffs: {handoff_count}/{len(successful)}")
        print(f"💾 Output: {self.output_dir}")
        
        return successful

def main():
    generator = CorrectFlashLiteGenerator()
    
    # Generate 100 CORRECT short conversations
    conversations = generator.generate_batch(num_conversations=100)
    
    print(f"\n🎯 These are SHORT but CORRECT!")
    print(f"📚 Minimum 3 turns each with proper handoffs")

if __name__ == "__main__":
    main()