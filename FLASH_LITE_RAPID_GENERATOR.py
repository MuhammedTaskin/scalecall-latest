#!/usr/bin/env python3
"""
ULTRA FAST Dataset Generator with Gemini 2.5 Flash-Lite
Generates MANY SHORT conversations RAPIDLY
$0.10/1M tokens - 3X CHEAPER than Flash!
"""

import os
import json
import random
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import google.generativeai as genai

# Configure
GOOGLE_API_KEY = "AIzaSyBzC3ydAP1qKkGyRkJ9t1sp5D3QN9QyzsQ"
genai.configure(api_key=GOOGLE_API_KEY)

class RapidFlashLiteGenerator:
    def __init__(self):
        # FLASH-LITE MODEL - 3X CHEAPER, SUPER FAST!
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash-lite',
            safety_settings={
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE'
            }
        )
        
        # SHORT SCENARIOS for RAPID generation
        self.quick_scenarios = [
            "verify_and_route",  # Just verify user and route
            "quick_esim_check",  # Check status, give answer
            "bill_amount_query",  # How much do I owe?
            "plan_info_request",  # What's my current plan?
            "password_reset",  # Reset account password
            "service_outage_check",  # Is there an outage?
            "data_usage_query",  # How much data left?
            "payment_confirmation",  # Did my payment go through?
            "activation_status",  # Is my line active?
            "support_ticket_status"  # Check ticket status
        ]
        
        # FOCUSED TOOLS (only essentials)
        self.essential_tools = {
            "RouterAgent": ["verify_user", "route_to_agent"],
            "TechAgent": ["check_esim_status", "create_tech_ticket"],
            "BillingAgent": ["get_last_bill", "get_unpaid_amount"],
            "PlanAgent": ["get_customer_plan"],
            "FAQAgent": ["search_faq"],
            "Shared": ["escalate_to_human", "end_conversation"]
        }
        
        self.output_dir = "data/flash_lite_dataset"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_short_conversation(self, idx: int) -> dict:
        """Generate ONE SHORT conversation (3-6 turns)"""
        
        scenario = random.choice(self.quick_scenarios)
        persona = random.choice(["angry", "confused", "normal", "impatient", "polite"])
        
        prompt = f"""Türkçe telekom müşteri hizmeti KISA konuşması.

SENARYO: {scenario}
MÜŞTERİ: {persona}
UZUNLUK: 3-6 turn (ÇOK KISA!)

ÖRNEK AKIŞ:
1. Müşteri sorununu söyler
2. Agent kimlik doğrular (verify_user)
3. Agent sorunu çözer veya yönlendirir
4. Konuşma biter

JSON:
{{
  "id": "short_{idx:04d}",
  "scenario": "{scenario}",
  "customer_turns": [
    {{"turn": 1, "text": "Müşteri metni", "emotion": "{persona}"}},
    {{"turn": 3, "text": "Müşteri cevabı"}}
  ],
  "agent_responses": [
    {{"turn": 2, "agent": "RouterAgent", "text": "Agent cevabı", "tools": ["verify_user"]}},
    {{"turn": 4, "agent": "RouterAgent", "text": "Çözüm", "tools": ["end_conversation"]}}
  ]
}}

KISA ve ÖZ! Tool'ları doğru kullan: {list(self.essential_tools.keys())}"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.8,
                    max_output_tokens=2048,  # SHORT!
                )
            )
            
            # Parse JSON
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            
            conv = json.loads(text.strip())
            conv["generated_at"] = datetime.now().isoformat()
            
            return conv
            
        except Exception as e:
            print(f"  Error {idx}: {str(e)[:50]}")
            return None
    
    def generate_batch_parallel(self, num_conversations: int = 100):
        """Generate MANY conversations in PARALLEL"""
        
        print(f"🚀 FLASH-LITE RAPID GENERATOR")
        print(f"💰 Cost: $0.10/1M tokens (3X cheaper!)")
        print(f"⚡ Generating {num_conversations} SHORT conversations...")
        print("=" * 60)
        
        successful = []
        failed = 0
        
        # PARALLEL GENERATION with 5 workers
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.generate_short_conversation, i): i 
                for i in range(num_conversations)
            }
            
            for future in as_completed(futures):
                idx = futures[future]
                result = future.result()
                
                if result:
                    # Save immediately
                    filename = f"{self.output_dir}/short_{idx:04d}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    
                    successful.append(result)
                    print(f"  ✅ [{len(successful)}/{num_conversations}] Generated: {result['scenario']}")
                else:
                    failed += 1
                    print(f"  ❌ Failed: {idx}")
                
                # Rate limiting (Flash-Lite has higher limits)
                if len(successful) % 10 == 0:
                    time.sleep(1)
        
        print("\n" + "=" * 60)
        print(f"✅ GENERATION COMPLETE!")
        print(f"📊 Success: {len(successful)}/{num_conversations} ({100*len(successful)/num_conversations:.1f}%)")
        print(f"💾 Output: {self.output_dir}")
        print(f"⚡ Flash-Lite = SPEED + SAVINGS!")
        
        return successful

def main():
    generator = RapidFlashLiteGenerator()
    
    # Generate 100 SHORT conversations FAST
    conversations = generator.generate_batch_parallel(num_conversations=100)
    
    print(f"\n🎯 Next: Voice these with ElevenLabs Flash v2.5")
    print(f"📚 Total training data: {len(conversations) + 20} conversations")

if __name__ == "__main__":
    main()