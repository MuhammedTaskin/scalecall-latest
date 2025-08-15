#!/usr/bin/env python3
"""
ULTIMATE VARIED DATASET GENERATOR
Creates HIGHLY DIVERSE conversations for GENERALIZATION
Runs in background with real-time tracking
"""

import os
import json
import random
import uuid
from typing import List, Dict, Any
from datetime import datetime
import google.generativeai as genai
import time

# Configure Gemini
GOOGLE_API_KEY = "AIzaSyBzC3ydAP1qKkGyRkJ9t1sp5D3QN9QyzsQ"
genai.configure(api_key=GOOGLE_API_KEY)

class UltimateVariedDatasetGenerator:
    """Generate HIGHLY VARIED conversations for model generalization"""
    
    def __init__(self):
        # Configure model with disabled safety - using Flash-Lite for speed
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash',  # Using regular flash (flash-lite not in SDK yet)
            safety_settings={
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE'
            }
        )
        
        # DEFINED TOOLS - SIMPLE & IMPLEMENTABLE
        self.available_tools = {
            "RouterAgent": [
                "verify_user",  # (msisdn, maiden_name) -> {verified, customer_id}
                "get_customer_status",  # (customer_id) -> {active, plan_type, has_issues}
                "route_to_agent"  # (agent_type, reason) -> {routed}
            ],
            "TechAgent": [
                "check_esim_status",  # (customer_id) -> {status, activation_date, error_code}
                "check_device_imei",  # (imei) -> {registered, compatible, model}
                "reissue_activation_code",  # (customer_id) -> {new_code, sms_sent}
                "create_tech_ticket"  # (customer_id, issue_type) -> {ticket_id}
            ],
            "PlanAgent": [
                "get_customer_plan",  # (customer_id) -> {plan_id, monthly_price, data_gb}
                "list_all_plans",  # () -> {plans}
                "change_customer_plan",  # (customer_id, new_plan_id) -> {changed, effective_date}
                "check_plan_compatibility"  # (customer_id, plan_id) -> {compatible, reason}
            ],
            "BillingAgent": [
                "get_last_bill",  # (customer_id) -> {amount, paid, due_date}
                "get_unpaid_amount",  # (customer_id) -> {total, overdue}
                "apply_campaign_discount",  # (customer_id, campaign_code) -> {applied, discount_amount}
                "create_payment_note"  # (customer_id, note) -> {noted}
            ],
            "FAQAgent": [
                "search_faq",  # (keyword) -> {results}
                "get_common_solutions",  # (issue_type) -> {solutions}
                "send_help_sms",  # (customer_id, template_id) -> {sent}
                "create_info_ticket"  # (customer_id, question) -> {ticket_id}
            ],
            "Shared": [
                "escalate_to_human",  # (reason) -> {escalated}
                "end_conversation"  # (resolution) -> {ended}
            ]
        }
        
        # Directories
        self.base_dir = "data/varied_dataset"
        self.conversations_dir = os.path.join(self.base_dir, "conversations")
        self.tracking_dir = os.path.join(self.base_dir, "tracking")
        
        for dir_path in [self.conversations_dir, self.tracking_dir]:
            os.makedirs(dir_path, exist_ok=True)
        
        # VARIATION PARAMETERS FOR GENERALIZATION
        self.variations = {
            "customer_personas": [
                "angry_young",
                "confused_elderly", 
                "business_professional",
                "frustrated_parent",
                "tech_savvy_impatient",
                "polite_but_firm",
                "passive_aggressive",
                "overly_chatty",
                "suspicious_paranoid",
                "cheerful_optimistic"
            ],
            
            "issues": [
                "esim_activation_failed",
                "esim_qr_code_not_working",
                "device_not_compatible",
                "package_too_expensive",
                "international_roaming_issue",
                "billing_overcharge",
                "contract_termination_request",
                "family_plan_problems",
                "network_coverage_complaint",
                "previous_ticket_followup",
                "multiple_esim_management",
                "corporate_account_issue",
                "payment_method_problem",
                "data_speed_complaint",
                "unauthorized_charges"
            ],
            
            "handoff_patterns": [
                ["RouterAgent"],  # No handoff
                ["RouterAgent", "TechAgent"],
                ["RouterAgent", "PlanAgent"],
                ["RouterAgent", "BillingAgent"],
                ["RouterAgent", "FAQAgent"],
                ["RouterAgent", "TechAgent", "BillingAgent"],
                ["RouterAgent", "PlanAgent", "BillingAgent"],
                ["RouterAgent", "TechAgent", "PlanAgent"],
                ["RouterAgent", "FAQAgent", "TechAgent"],
                ["RouterAgent", "BillingAgent", "TechAgent", "PlanAgent"]  # Complex
            ],
            
            "complexity_levels": [
                "trivial",  # 3-5 turns
                "simple",   # 5-8 turns
                "medium",   # 8-12 turns
                "complex",  # 12-18 turns
                "chaos"     # 18+ turns with interruptions
            ],
            
            "interruption_types": [
                "none",
                "topic_change",
                "emotional_escalation",
                "connection_issue",
                "background_noise",
                "multiple_issues",
                "misunderstanding",
                "impatience_interruption"
            ],
            
            "resolution_types": [
                "fully_resolved",
                "partially_resolved",
                "escalated_to_human",
                "customer_hangup",
                "scheduled_callback",
                "ticket_created",
                "transferred_department"
            ]
        }
    
    def generate_varied_prompt(self, params: Dict) -> str:
        """Generate prompt with specific variation parameters"""
        
        prompt = """Türkçe telekom çağrı merkezi konuşması oluştur. ÇOK ÇEŞİTLİ ve GERÇEK olmalı.

PARAMETRELER:
- Müşteri Tipi: {persona}
- Sorun: {issue}
- Agent Akışı: {handoff_pattern}
- Karmaşıklık: {complexity}
- Kesinti: {interruption}
- Çözüm: {resolution}

ÇEŞITLILIK KURALLARI:
1. Müşteri kişiliğine uygun konuşma tarzı kullan
2. Sorun tipine göre teknik detay seviyesi ayarla
3. Agent handoff'ları MANTIKLI ve DOĞAL olmalı
4. Kesintiler varsa gerçekçi yerleştir
5. Farklı tool kombinasyonları kullan

ÇOK ÖNEMLİ:
- customer_turns_for_tts: SADECE MÜŞTERİ SESLERİ için (ElevenLabs TTS'e gidecek)
- agent_responses: SADECE AGENT CEVAPLARI (TEXT ONLY - SES YOK, TTS YOK!)

TOOL KURALLARI - ÇOK ÖNEMLİ:
RouterAgent tools: verify_user, get_customer_status, route_to_agent
TechAgent tools: check_esim_status, check_device_imei, reissue_activation_code, create_tech_ticket
PlanAgent tools: get_customer_plan, list_all_plans, change_customer_plan, check_plan_compatibility
BillingAgent tools: get_last_bill, get_unpaid_amount, apply_campaign_discount, create_payment_note
FAQAgent tools: search_faq, get_common_solutions, send_help_sms, create_info_ticket
Shared tools: escalate_to_human, end_conversation

SADECE BU TOOL'LAR KULLANILACAK! Başka tool isimleri YARATMA!

JSON ÇIKTI:
{{
  "conversation_id": "conv_{timestamp}_{issue}_{persona}",
  "metadata": {{
    "scenario": "{issue}",
    "complexity": "{complexity}",
    "persona": "{persona}",
    "handoff_pattern": {handoff_pattern_json},
    "interruption_type": "{interruption}",
    "resolution": "{resolution}"
  }},
  "customer_profile": {{
    "persona": "{persona}",
    "phone": "{phone}",
    "maiden_name": "{maiden_name}",
    "issue": "{issue}",
    "background": "{background}"
  }},
  "customer_turns_for_tts": [
    {{
      "turn_id": "turn_001",
      "text": "Müşteri kişiliğine uygun giriş cümlesi",
      "emotion": "kişiliğe uygun duygu",
      "voice_notes": {{
        "tone": "ton",
        "speed": "hız",
        "emphasis": ["vurgular"]
      }}
    }}
  ],
  "agent_responses": [
    {{
      "turn_id": "turn_002",
      "agent_persona": "RouterAgent",
      "text": "Agent'ın müşteriye cevabı - SADECE TEXT, SES YOK",
      "tools_triggered": [],
      "handoff": null
    }}
  ],
  "agent_handoffs": [],
  "tool_calls": []
}}

ŞİMDİ ÇOK ÇEŞİTLİ BİR KONUŞMA OLUŞTUR. Her şey farklı olsun!"""

        # Generate random but consistent details
        phone = f"055{random.randint(1,9)} {random.randint(100,999)} {random.randint(10,99)} {random.randint(10,99)}"
        maiden_names = ["Yıldız", "Demir", "Kaya", "Çelik", "Arslan", "Güneş", "Ay", "Bulut", "Deniz", "Orman"]
        backgrounds = [
            "Öğrenci", "Emekli", "İş insanı", "Ev hanımı", "Öğretmen", 
            "Mühendis", "Doktor", "Esnaf", "Memur", "Serbest meslek"
        ]
        
        return prompt.format(
            persona=params["persona"],
            issue=params["issue"],
            handoff_pattern=" → ".join(params["handoff_pattern"]),
            handoff_pattern_json=json.dumps(params["handoff_pattern"]),
            complexity=params["complexity"],
            interruption=params["interruption"],
            resolution=params["resolution"],
            timestamp=datetime.now().strftime("%Y%m%d_%H%M%S"),
            phone=phone,
            maiden_name=random.choice(maiden_names),
            background=random.choice(backgrounds)
        )
    
    def generate_single_conversation(self, index: int) -> Dict:
        """Generate a single VARIED conversation"""
        
        # Pick random parameters for MAXIMUM VARIATION
        params = {
            "persona": random.choice(self.variations["customer_personas"]),
            "issue": random.choice(self.variations["issues"]),
            "handoff_pattern": random.choice(self.variations["handoff_patterns"]),
            "complexity": random.choice(self.variations["complexity_levels"]),
            "interruption": random.choice(self.variations["interruption_types"]),
            "resolution": random.choice(self.variations["resolution_types"])
        }
        
        print(f"   🎲 Params: {params['persona']} | {params['issue'][:20]}... | {params['complexity']}")
        
        prompt = self.generate_varied_prompt(params)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.9,  # High for variation
                    top_p=0.95,
                    top_k=50,  # Increased for more variation
                    max_output_tokens=16384,  # Maximum for complex chaos conversations
                )
            )
            
            if not response.parts:
                print(f"   ⚠️ Response blocked. Retrying with different params...")
                return None
            
            response_text = response.text
            
            # Extract JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            # Clean any JSON comments (shouldn't be there but just in case)
            import re
            response_text = re.sub(r'//.*?$', '', response_text, flags=re.MULTILINE)
            response_text = re.sub(r'/\*.*?\*/', '', response_text, flags=re.DOTALL)
            
            # Try to fix common JSON issues
            # Fix duplicate "turn_id": prefix
            response_text = re.sub(r'"turn_id":\s*"turn_id":', r'"turn_id":', response_text)
            
            # Remove trailing commas before closing brackets
            response_text = re.sub(r',\s*}', '}', response_text)
            response_text = re.sub(r',\s*]', ']', response_text)
            
            conversation = json.loads(response_text.strip())
            
            # Add metadata
            conversation["generation_id"] = str(uuid.uuid4())
            conversation["generated_at"] = datetime.now().isoformat()
            conversation["index"] = index
            conversation["variation_params"] = params
            
            return conversation
            
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON Error: {str(e)}")
            # Save the problematic response for debugging
            error_file = os.path.join(self.tracking_dir, f"error_{index}.txt")
            with open(error_file, "w") as f:
                f.write(f"Error: {str(e)}\n\n")
                f.write(f"Response:\n{response_text if 'response_text' in locals() else 'No response text'}")
            return None
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}...")
            return None
    
    def update_tracking(self, status: Dict):
        """Update tracking file for real-time monitoring"""
        
        tracking_file = os.path.join(self.tracking_dir, "generation_status.json")
        
        with open(tracking_file, "w") as f:
            json.dump(status, f, indent=2)
        
        # Also create a simple text file for easy monitoring
        status_file = os.path.join(self.tracking_dir, "current_status.txt")
        with open(status_file, "w") as f:
            f.write(f"DATASET GENERATION STATUS\n")
            f.write(f"========================\n")
            f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Progress: {status['completed']}/{status['total']}\n")
            f.write(f"Success Rate: {status['success_rate']:.1f}%\n")
            f.write(f"Last Generated: {status.get('last_generated', 'N/A')}\n")
            f.write(f"Status: {status.get('current_status', 'Running')}\n")
    
    def generate_dataset(self, num_conversations: int = 100):
        """Generate HIGHLY VARIED dataset with tracking"""
        
        print("🚀 ULTIMATE VARIED DATASET GENERATOR")
        print("=" * 60)
        print(f"📊 Generating {num_conversations} VARIED conversations...")
        print(f"🎯 Personas: {len(self.variations['customer_personas'])} types")
        print(f"🔧 Issues: {len(self.variations['issues'])} types")
        print(f"🔄 Handoff patterns: {len(self.variations['handoff_patterns'])} types")
        print("=" * 60)
        
        all_conversations = []
        tracking_status = {
            "total": num_conversations,
            "completed": 0,
            "successful": 0,
            "failed": 0,
            "success_rate": 0,
            "start_time": datetime.now().isoformat(),
            "current_status": "Starting...",
            "variations_used": {
                "personas": {},
                "issues": {},
                "handoffs": {},
                "resolutions": {}
            }
        }
        
        # Update initial status
        self.update_tracking(tracking_status)
        
        for i in range(num_conversations):
            print(f"\n📍 [{i+1}/{num_conversations}] Generating VARIED conversation...")
            tracking_status["current_status"] = f"Generating {i+1}/{num_conversations}"
            
            # Try up to 3 times with different parameters
            conversation = None
            for attempt in range(3):
                conversation = self.generate_single_conversation(i)
                if conversation:
                    break
                time.sleep(2)  # Wait before retry
            
            if conversation:
                # Save conversation
                conv_id = conversation.get("conversation_id", f"conv_{i:04d}")
                conv_file = os.path.join(self.conversations_dir, f"{conv_id}.json")
                with open(conv_file, "w", encoding="utf-8") as f:
                    json.dump(conversation, f, ensure_ascii=False, indent=2)
                
                all_conversations.append(conversation)
                tracking_status["successful"] += 1
                tracking_status["last_generated"] = conv_id
                
                # Track variations
                params = conversation.get("variation_params", {})
                for key in ["persona", "issue"]:
                    if key in params:
                        val = params[key]
                        if key + "s" in tracking_status["variations_used"]:
                            tracking_status["variations_used"][key + "s"][val] = \
                                tracking_status["variations_used"][key + "s"].get(val, 0) + 1
                
                print(f"   ✅ Generated: {conv_id}")
                print(f"   📊 Turns: {len(conversation.get('dialogue_for_tts', []))}")
            else:
                tracking_status["failed"] += 1
                print(f"   ❌ Failed after 3 attempts")
            
            # Update tracking
            tracking_status["completed"] = i + 1
            tracking_status["success_rate"] = (tracking_status["successful"] / tracking_status["completed"]) * 100
            self.update_tracking(tracking_status)
            
            # Rate limiting
            time.sleep(3)
        
        # Final summary
        tracking_status["current_status"] = "Complete"
        tracking_status["end_time"] = datetime.now().isoformat()
        self.update_tracking(tracking_status)
        
        # Save master dataset file
        dataset = {
            "generated_at": datetime.now().isoformat(),
            "statistics": {
                "total_conversations": len(all_conversations),
                "success_rate": tracking_status["success_rate"],
                "variations_coverage": tracking_status["variations_used"]
            },
            "conversations": all_conversations
        }
        
        dataset_file = os.path.join(self.base_dir, "varied_dataset.json")
        with open(dataset_file, "w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 60)
        print("✅ VARIED DATASET GENERATION COMPLETE!")
        print(f"📁 Base directory: {self.base_dir}")
        print(f"📊 Successful: {tracking_status['successful']}/{num_conversations}")
        print(f"📈 Success rate: {tracking_status['success_rate']:.1f}%")
        print(f"📋 Tracking: {self.tracking_dir}/current_status.txt")
        print("=" * 60)
        
        # Show variation coverage
        print("\n📊 VARIATION COVERAGE:")
        for category, counts in tracking_status["variations_used"].items():
            if counts:
                print(f"  {category}: {len(counts)} unique types used")
        
        return all_conversations

def main():
    """Main execution"""
    
    print("🔥 STARTING ULTIMATE VARIED DATASET GENERATION")
    print("📝 This will create HIGHLY DIVERSE conversations for GENERALIZATION")
    print("📊 You can monitor progress in: data/varied_dataset/tracking/current_status.txt")
    print("")
    
    generator = UltimateVariedDatasetGenerator()
    
    # Generate large varied dataset
    # Start with 20 for testing, then increase to 100+
    conversations = generator.generate_dataset(num_conversations=20)
    
    print("\n✨ Dataset ready for ElevenLabs voicing!")
    print("💡 The model will learn from MAXIMUM VARIATION")

if __name__ == "__main__":
    main()