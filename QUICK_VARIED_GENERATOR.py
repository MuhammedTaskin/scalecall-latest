#!/usr/bin/env python3
"""
Quick Varied Generator - Generate 100 more varied conversations FAST
Focus on edge cases and underrepresented scenarios
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

class QuickVariedGenerator:
    def __init__(self):
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash-lite',  # Fast!
            safety_settings={
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE'
            }
        )
        
        # Edge cases and unique scenarios
        self.edge_scenarios = [
            # Urgent/Emergency
            {"case": "phone_stolen_abroad", "urgency": "critical", "agents": ["RouterAgent", "TechAgent", "BillingAgent"]},
            {"case": "fraud_alert", "urgency": "critical", "agents": ["RouterAgent", "BillingAgent", "escalate_to_human"]},
            {"case": "emergency_call_not_working", "urgency": "critical", "agents": ["RouterAgent", "TechAgent", "escalate_to_human"]},
            
            # Complex Multi-Issue
            {"case": "multiple_lines_different_issues", "urgency": "normal", "agents": ["RouterAgent", "PlanAgent", "BillingAgent", "TechAgent"]},
            {"case": "corporate_account_migration", "urgency": "normal", "agents": ["RouterAgent", "PlanAgent", "BillingAgent"]},
            {"case": "family_plan_divorce_split", "urgency": "sensitive", "agents": ["RouterAgent", "PlanAgent", "BillingAgent"]},
            
            # Regulatory/Legal
            {"case": "number_portability_dispute", "urgency": "normal", "agents": ["RouterAgent", "TechAgent", "FAQAgent"]},
            {"case": "data_privacy_request", "urgency": "normal", "agents": ["RouterAgent", "FAQAgent", "escalate_to_human"]},
            {"case": "contract_cancellation_penalty", "urgency": "normal", "agents": ["RouterAgent", "BillingAgent", "FAQAgent"]},
            
            # Technical Edge Cases
            {"case": "esim_multiple_devices", "urgency": "normal", "agents": ["RouterAgent", "TechAgent"]},
            {"case": "5g_intermittent_drops", "urgency": "normal", "agents": ["RouterAgent", "TechAgent", "PlanAgent"]},
            {"case": "voip_integration_issues", "urgency": "normal", "agents": ["RouterAgent", "TechAgent", "FAQAgent"]},
            
            # Billing Anomalies
            {"case": "cryptocurrency_payment", "urgency": "normal", "agents": ["RouterAgent", "BillingAgent", "FAQAgent"]},
            {"case": "international_roaming_shock", "urgency": "high", "agents": ["RouterAgent", "BillingAgent", "TechAgent"]},
            {"case": "promotional_stacking_error", "urgency": "normal", "agents": ["RouterAgent", "BillingAgent", "PlanAgent"]},
            
            # Service Combinations
            {"case": "tv_internet_mobile_bundle", "urgency": "normal", "agents": ["RouterAgent", "PlanAgent", "BillingAgent"]},
            {"case": "iot_device_connectivity", "urgency": "normal", "agents": ["RouterAgent", "TechAgent", "PlanAgent"]},
            {"case": "smartwatch_esim_pairing", "urgency": "normal", "agents": ["RouterAgent", "TechAgent"]},
        ]
        
        # Unique customer situations
        self.customer_situations = [
            "calling_from_airport",
            "driving_cant_stop",
            "baby_crying_background",
            "poor_connection_breaking_up",
            "using_translator_app",
            "first_time_smartphone_user",
            "switching_from_competitor",
            "moving_abroad_tomorrow",
            "company_paying_bill",
            "student_on_budget"
        ]
        
        # Emotional progressions
        self.emotional_arcs = [
            ["confused", "frustrated", "angry", "satisfied"],
            ["polite", "concerned", "worried", "relieved"],
            ["angry", "impatient", "understanding", "thankful"],
            ["cheerful", "confused", "frustrated", "happy"],
            ["suspicious", "questioning", "convinced", "satisfied"]
        ]
        
        self.output_dir = "data/quick_varied_dataset"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_edge_conversation(self, idx: int) -> dict:
        """Generate edge case conversation"""
        
        scenario = random.choice(self.edge_scenarios)
        situation = random.choice(self.customer_situations)
        emotional_arc = random.choice(self.emotional_arcs)
        
        prompt = f"""Generate UNIQUE Turkish telco conversation with edge case.

EDGE CASE: {scenario["case"]}
URGENCY: {scenario["urgency"]}
SITUATION: Customer is {situation}
EMOTIONAL ARC: {' → '.join(emotional_arc)}
AGENTS: {' → '.join(scenario["agents"][:3])}  # Max 3 for speed

SPECIAL REQUIREMENTS:
1. Show the {situation} naturally in dialogue
2. Customer emotion evolves: {' → '.join(emotional_arc)}
3. Handle {scenario["urgency"]} urgency appropriately
4. Agents show empathy and problem-solving
5. Include realistic background/context

JSON OUTPUT (keep it focused):
{{
  "id": "edge_{idx:04d}",
  "edge_case": "{scenario['case']}",
  "situation": "{situation}",
  "urgency": "{scenario['urgency']}",
  "customer_turns_for_tts": [
    {{"turn_id": "turn_001", "text": "...", "emotion": "{emotional_arc[0]}", "context": "{situation}"}}
  ],
  "agent_responses": [
    {{"turn_id": "turn_002", "agent_persona": "RouterAgent", "text": "...", "tools_triggered": ["verify_user"]}}
  ],
  "agent_handoffs": [
    {{"at_turn": 4, "from": "RouterAgent", "to": "...", "reason": "{scenario['case']}"}}
  ]
}}

Make it REALISTIC and handle the edge case properly!"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.85,
                    max_output_tokens=3072,
                )
            )
            
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            
            import re
            text = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)
            text = re.sub(r',\s*}', '}', text)
            text = re.sub(r',\s*]', ']', text)
            
            conv = json.loads(text.strip())
            conv["generated_at"] = datetime.now().isoformat()
            
            return conv
            
        except Exception as e:
            print(f"  Error {idx}: {str(e)[:50]}")
            return None
    
    def generate_batch(self, num: int = 100):
        """Generate batch of edge cases"""
        
        print(f"🎯 QUICK VARIED GENERATOR")
        print(f"📊 Generating {num} edge case conversations")
        print(f"⚡ Using Flash-Lite for speed")
        print("="*60)
        
        successful = []
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(self.generate_edge_conversation, i): i 
                for i in range(num)
            }
            
            for future in as_completed(futures):
                idx = futures[future]
                result = future.result()
                
                if result:
                    filename = f"{self.output_dir}/edge_{idx:04d}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    successful.append(result)
                    
                    if len(successful) % 20 == 0:
                        print(f"  ✅ Progress: {len(successful)}/{num}")
                        time.sleep(1)
        
        print(f"\n✅ Generated {len(successful)} edge cases")
        print(f"📁 Output: {self.output_dir}")
        
        # Quick stats
        urgencies = {}
        for conv in successful:
            urg = conv.get('urgency', 'normal')
            urgencies[urg] = urgencies.get(urg, 0) + 1
        
        print(f"📊 Urgency distribution: {urgencies}")
        
        return successful

def main():
    generator = QuickVariedGenerator()
    conversations = generator.generate_batch(100)
    
    # Character count
    chars = sum(
        len(turn.get('text', ''))
        for conv in conversations
        for turn in conv.get('customer_turns_for_tts', [])
    )
    
    print(f"\n📝 Additional TTS needed: {chars:,} characters")

if __name__ == "__main__":
    main()