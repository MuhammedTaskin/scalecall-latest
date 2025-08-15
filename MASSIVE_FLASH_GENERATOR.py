#!/usr/bin/env python3
"""
MASSIVE Flash Generator - Generate 500+ varied conversations
Uses both Flash and Flash-Lite for maximum speed and variation
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

class MassiveFlashGenerator:
    def __init__(self):
        # Use BOTH models for variation
        self.flash_model = genai.GenerativeModel(
            'gemini-2.5-flash',
            safety_settings={
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE'
            }
        )
        
        self.flash_lite_model = genai.GenerativeModel(
            'gemini-2.5-flash-lite',
            safety_settings={
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE'
            }
        )
        
        # MASSIVE scenario variety
        self.scenarios = [
            # Technical Issues (50+ variations)
            {"type": "esim_activation_failed", "complexity": "simple", "handoffs": ["RouterAgent", "TechAgent"]},
            {"type": "esim_qr_expired", "complexity": "medium", "handoffs": ["RouterAgent", "TechAgent", "BillingAgent"]},
            {"type": "esim_device_incompatible", "complexity": "complex", "handoffs": ["RouterAgent", "TechAgent", "FAQAgent"]},
            {"type": "network_no_signal", "complexity": "simple", "handoffs": ["RouterAgent", "TechAgent"]},
            {"type": "network_slow_4g", "complexity": "medium", "handoffs": ["RouterAgent", "TechAgent", "PlanAgent"]},
            {"type": "network_roaming_issues", "complexity": "complex", "handoffs": ["RouterAgent", "TechAgent", "BillingAgent"]},
            {"type": "sms_not_working", "complexity": "simple", "handoffs": ["RouterAgent", "TechAgent"]},
            {"type": "mms_failed", "complexity": "medium", "handoffs": ["RouterAgent", "TechAgent", "FAQAgent"]},
            {"type": "voicemail_setup", "complexity": "simple", "handoffs": ["RouterAgent", "FAQAgent"]},
            {"type": "international_calls_blocked", "complexity": "medium", "handoffs": ["RouterAgent", "TechAgent", "BillingAgent"]},
            {"type": "wifi_calling_setup", "complexity": "complex", "handoffs": ["RouterAgent", "TechAgent", "FAQAgent"]},
            {"type": "5g_not_working", "complexity": "medium", "handoffs": ["RouterAgent", "TechAgent", "PlanAgent"]},
            {"type": "hotspot_issues", "complexity": "simple", "handoffs": ["RouterAgent", "TechAgent"]},
            {"type": "dual_sim_problems", "complexity": "complex", "handoffs": ["RouterAgent", "TechAgent"]},
            
            # Billing Issues (50+ variations)
            {"type": "unexpected_charge", "complexity": "simple", "handoffs": ["RouterAgent", "BillingAgent"]},
            {"type": "double_billing", "complexity": "medium", "handoffs": ["RouterAgent", "BillingAgent"]},
            {"type": "roaming_charges", "complexity": "complex", "handoffs": ["RouterAgent", "BillingAgent", "TechAgent"]},
            {"type": "payment_failed", "complexity": "simple", "handoffs": ["RouterAgent", "BillingAgent"]},
            {"type": "credit_card_expired", "complexity": "simple", "handoffs": ["RouterAgent", "BillingAgent"]},
            {"type": "autopay_setup", "complexity": "medium", "handoffs": ["RouterAgent", "BillingAgent", "FAQAgent"]},
            {"type": "refund_request", "complexity": "complex", "handoffs": ["RouterAgent", "BillingAgent"]},
            {"type": "bill_explanation", "complexity": "simple", "handoffs": ["RouterAgent", "BillingAgent"]},
            {"type": "promotional_discount_missing", "complexity": "medium", "handoffs": ["RouterAgent", "BillingAgent", "PlanAgent"]},
            {"type": "family_plan_billing", "complexity": "complex", "handoffs": ["RouterAgent", "BillingAgent", "PlanAgent"]},
            {"type": "corporate_discount", "complexity": "medium", "handoffs": ["RouterAgent", "BillingAgent"]},
            {"type": "student_discount", "complexity": "simple", "handoffs": ["RouterAgent", "BillingAgent", "FAQAgent"]},
            {"type": "payment_arrangement", "complexity": "complex", "handoffs": ["RouterAgent", "BillingAgent"]},
            {"type": "bill_dispute", "complexity": "complex", "handoffs": ["RouterAgent", "BillingAgent"]},
            
            # Plan Changes (40+ variations)
            {"type": "upgrade_to_unlimited", "complexity": "simple", "handoffs": ["RouterAgent", "PlanAgent"]},
            {"type": "downgrade_plan", "complexity": "medium", "handoffs": ["RouterAgent", "PlanAgent", "BillingAgent"]},
            {"type": "add_international", "complexity": "simple", "handoffs": ["RouterAgent", "PlanAgent"]},
            {"type": "family_plan_add_line", "complexity": "complex", "handoffs": ["RouterAgent", "PlanAgent", "BillingAgent"]},
            {"type": "remove_family_member", "complexity": "medium", "handoffs": ["RouterAgent", "PlanAgent"]},
            {"type": "data_addon", "complexity": "simple", "handoffs": ["RouterAgent", "PlanAgent"]},
            {"type": "temporary_plan_change", "complexity": "medium", "handoffs": ["RouterAgent", "PlanAgent", "BillingAgent"]},
            {"type": "business_plan_inquiry", "complexity": "complex", "handoffs": ["RouterAgent", "PlanAgent", "FAQAgent"]},
            {"type": "prepaid_to_postpaid", "complexity": "complex", "handoffs": ["RouterAgent", "PlanAgent", "BillingAgent"]},
            {"type": "compare_plans", "complexity": "simple", "handoffs": ["RouterAgent", "PlanAgent"]},
            {"type": "seasonal_plan", "complexity": "medium", "handoffs": ["RouterAgent", "PlanAgent"]},
            {"type": "travel_package", "complexity": "simple", "handoffs": ["RouterAgent", "PlanAgent", "FAQAgent"]},
            
            # Account Management (30+ variations)
            {"type": "password_reset", "complexity": "simple", "handoffs": ["RouterAgent", "FAQAgent"]},
            {"type": "account_suspended", "complexity": "complex", "handoffs": ["RouterAgent", "BillingAgent"]},
            {"type": "change_phone_number", "complexity": "medium", "handoffs": ["RouterAgent", "TechAgent"]},
            {"type": "port_number_in", "complexity": "complex", "handoffs": ["RouterAgent", "TechAgent", "FAQAgent"]},
            {"type": "port_number_out", "complexity": "medium", "handoffs": ["RouterAgent", "TechAgent"]},
            {"type": "sim_swap", "complexity": "simple", "handoffs": ["RouterAgent", "TechAgent"]},
            {"type": "lost_phone", "complexity": "urgent", "handoffs": ["RouterAgent", "TechAgent", "BillingAgent"]},
            {"type": "stolen_phone", "complexity": "urgent", "handoffs": ["RouterAgent", "TechAgent", "BillingAgent"]},
            {"type": "account_merger", "complexity": "complex", "handoffs": ["RouterAgent", "PlanAgent", "BillingAgent"]},
            {"type": "authorized_user_add", "complexity": "medium", "handoffs": ["RouterAgent", "FAQAgent"]},
            {"type": "privacy_settings", "complexity": "simple", "handoffs": ["RouterAgent", "FAQAgent"]},
            
            # Service Inquiries (30+ variations)
            {"type": "coverage_check", "complexity": "simple", "handoffs": ["RouterAgent", "FAQAgent"]},
            {"type": "5g_availability", "complexity": "simple", "handoffs": ["RouterAgent", "TechAgent", "FAQAgent"]},
            {"type": "new_customer_offer", "complexity": "medium", "handoffs": ["RouterAgent", "PlanAgent"]},
            {"type": "loyalty_rewards", "complexity": "simple", "handoffs": ["RouterAgent", "BillingAgent", "FAQAgent"]},
            {"type": "device_upgrade", "complexity": "medium", "handoffs": ["RouterAgent", "PlanAgent", "BillingAgent"]},
            {"type": "insurance_claim", "complexity": "complex", "handoffs": ["RouterAgent", "BillingAgent", "FAQAgent"]},
            {"type": "app_not_working", "complexity": "simple", "handoffs": ["RouterAgent", "TechAgent", "FAQAgent"]},
            {"type": "website_issue", "complexity": "simple", "handoffs": ["RouterAgent", "FAQAgent"]},
            {"type": "store_location", "complexity": "simple", "handoffs": ["RouterAgent", "FAQAgent"]},
            {"type": "complaint_escalation", "complexity": "urgent", "handoffs": ["RouterAgent", "escalate_to_human"]},
        ]
        
        # Customer personas with behaviors
        self.personas = [
            {"type": "angry", "traits": ["impatient", "demanding", "interrupting"]},
            {"type": "confused", "traits": ["uncertain", "asking_many_questions", "needs_repetition"]},
            {"type": "polite", "traits": ["patient", "thankful", "understanding"]},
            {"type": "tech_savvy", "traits": ["uses_technical_terms", "specific", "knowledgeable"]},
            {"type": "elderly", "traits": ["slow", "needs_simple_explanation", "repeats_information"]},
            {"type": "business", "traits": ["professional", "time_conscious", "result_oriented"]},
            {"type": "frustrated", "traits": ["previously_called", "exhausted", "skeptical"]},
            {"type": "cheerful", "traits": ["friendly", "talkative", "positive"]},
            {"type": "suspicious", "traits": ["questioning_everything", "paranoid", "defensive"]},
            {"type": "rushed", "traits": ["in_hurry", "brief_responses", "impatient"]},
        ]
        
        # Time contexts
        self.time_contexts = [
            "morning_commute", "lunch_break", "evening_home", "late_night",
            "weekend", "holiday", "business_hours", "after_hours"
        ]
        
        # Regional dialects/accents (Turkish)
        self.regions = [
            "istanbul", "ankara", "izmir", "antalya", "bursa", 
            "adana", "konya", "trabzon", "erzurum", "diyarbakir"
        ]
        
        self.output_dir = "data/massive_flash_dataset"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_conversation(self, idx: int, use_lite: bool = False) -> dict:
        """Generate one varied conversation"""
        
        model = self.flash_lite_model if use_lite else self.flash_model
        scenario = random.choice(self.scenarios)
        persona = random.choice(self.personas)
        time_context = random.choice(self.time_contexts)
        region = random.choice(self.regions)
        
        # Vary conversation length
        if scenario["complexity"] == "simple":
            turns = random.randint(4, 6)
        elif scenario["complexity"] == "medium":
            turns = random.randint(6, 10)
        else:
            turns = random.randint(8, 14)
        
        prompt = f"""Generate Turkish telco call center conversation.

SCENARIO: {scenario["type"]}
COMPLEXITY: {scenario["complexity"]}
CUSTOMER: {persona["type"]} from {region}
TRAITS: {', '.join(persona["traits"])}
TIME: {time_context}
AGENTS: {' → '.join(scenario["handoffs"])}
LENGTH: {turns} total turns

REQUIREMENTS:
1. Customer speaks with {region} dialect/accent hints
2. Show {persona["type"]} personality throughout
3. Include time context naturally (e.g., rushed if morning_commute)
4. Agents must handoff as specified
5. Use realistic tools from our defined set
6. Include natural interruptions/clarifications
7. Make it feel REAL and VARIED

OUTPUT JSON:
{{
  "id": "massive_{idx:04d}",
  "scenario": "{scenario['type']}",
  "complexity": "{scenario['complexity']}",
  "persona": "{persona['type']}",
  "region": "{region}",
  "time_context": "{time_context}",
  "customer_turns_for_tts": [
    {{"turn_id": "turn_001", "text": "...", "emotion": "{persona['type']}", "dialect_hints": ["{region}"]}}
  ],
  "agent_responses": [
    {{"turn_id": "turn_002", "agent_persona": "RouterAgent", "text": "...", "tools_triggered": ["verify_user"]}}
  ],
  "agent_handoffs": [
    {{"at_turn": 4, "from": "RouterAgent", "to": "...", "reason": "..."}}
  ]
}}

Make it UNIQUE and REALISTIC!"""
        
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.9,  # Higher for more variation
                    max_output_tokens=4096,
                )
            )
            
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            
            # Clean JSON
            import re
            text = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)
            text = re.sub(r',\s*}', '}', text)
            text = re.sub(r',\s*]', ']', text)
            
            conv = json.loads(text.strip())
            conv["generated_at"] = datetime.now().isoformat()
            conv["model"] = "flash-lite" if use_lite else "flash"
            
            return conv
            
        except Exception as e:
            print(f"  Error {idx}: {str(e)[:50]}")
            return None
    
    def generate_massive_batch(self, total: int = 500):
        """Generate MASSIVE dataset"""
        
        print(f"\n{'='*80}")
        print(f"🚀 MASSIVE FLASH GENERATOR")
        print(f"🎯 Generating {total} varied conversations")
        print(f"📊 {len(self.scenarios)} scenario types")
        print(f"👥 {len(self.personas)} persona types")
        print(f"🌍 {len(self.regions)} regional variants")
        print(f"{'='*80}\n")
        
        successful = []
        failed = 0
        
        # Use both models for variety
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {}
            for i in range(total):
                # Alternate between Flash and Flash-Lite
                use_lite = (i % 3 == 0)  # 1/3 with lite, 2/3 with regular
                futures[executor.submit(self.generate_conversation, i, use_lite)] = i
            
            for future in as_completed(futures):
                idx = futures[future]
                result = future.result()
                
                if result:
                    filename = f"{self.output_dir}/massive_{idx:04d}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    
                    successful.append(result)
                    
                    if len(successful) % 50 == 0:
                        print(f"  ✅ Progress: {len(successful)}/{total}")
                        time.sleep(2)  # Rate limit pause
                else:
                    failed += 1
                
                if len(successful) % 100 == 0:
                    time.sleep(5)  # Longer pause every 100
        
        # Statistics
        print(f"\n{'='*80}")
        print(f"📊 GENERATION COMPLETE!")
        print(f"✅ Success: {len(successful)}/{total} ({100*len(successful)/total:.1f}%)")
        
        # Analyze variety
        scenarios_used = {}
        personas_used = {}
        regions_used = {}
        complexities = {}
        
        for conv in successful:
            scenarios_used[conv.get('scenario', 'unknown')] = scenarios_used.get(conv.get('scenario', 'unknown'), 0) + 1
            personas_used[conv.get('persona', 'unknown')] = personas_used.get(conv.get('persona', 'unknown'), 0) + 1
            regions_used[conv.get('region', 'unknown')] = regions_used.get(conv.get('region', 'unknown'), 0) + 1
            complexities[conv.get('complexity', 'unknown')] = complexities.get(conv.get('complexity', 'unknown'), 0) + 1
        
        print(f"\n📈 VARIETY ANALYSIS:")
        print(f"  Unique scenarios: {len(scenarios_used)}")
        print(f"  Unique personas: {len(personas_used)}")
        print(f"  Unique regions: {len(regions_used)}")
        print(f"  Complexity distribution: {complexities}")
        
        print(f"\n💾 Output: {self.output_dir}")
        print(f"🔊 Ready for TTS generation!")
        
        return successful

def main():
    generator = MassiveFlashGenerator()
    
    # Generate 500 conversations!
    conversations = generator.generate_massive_batch(total=500)
    
    # Calculate TTS requirements
    total_chars = 0
    for conv in conversations:
        for turn in conv.get('customer_turns_for_tts', []):
            total_chars += len(turn.get('text', ''))
    
    print(f"\n📝 TTS Requirements:")
    print(f"  Total characters: {total_chars:,}")
    print(f"  ElevenLabs cost: ~${total_chars // 5000} (at Creator pricing)")
    print(f"  Generation time: ~{len(conversations) * 3 // 60} minutes")

if __name__ == "__main__":
    main()