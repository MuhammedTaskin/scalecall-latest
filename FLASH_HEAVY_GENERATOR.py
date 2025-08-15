#!/usr/bin/env python3
"""
Flash Heavy Generator - Using ONLY Flash (not Lite) for quality
Generates rich, complex conversations with maximum variation
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

class FlashHeavyGenerator:
    def __init__(self):
        # ONLY Flash model for quality
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash',
            safety_settings={
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE'
            }
        )
        
        # Rich scenario combinations
        self.scenario_matrix = {
            "technical": {
                "esim": ["activation", "transfer", "multi_device", "qr_expired", "compatibility"],
                "network": ["5g_issues", "roaming", "no_signal", "slow_speed", "congestion"],
                "device": ["hotspot", "wifi_calling", "volte", "dual_sim", "carrier_settings"],
                "services": ["sms", "mms", "voicemail", "call_forwarding", "caller_id"]
            },
            "billing": {
                "charges": ["unexpected", "roaming", "overage", "international", "premium_sms"],
                "payments": ["failed", "arrangement", "autopay", "refund", "dispute"],
                "discounts": ["promotional", "loyalty", "corporate", "student", "senior"],
                "issues": ["double_billing", "wrong_plan", "missing_credit", "tax_error", "late_fee"]
            },
            "plans": {
                "changes": ["upgrade", "downgrade", "addon", "removal", "suspension"],
                "types": ["unlimited", "family", "business", "prepaid", "international"],
                "features": ["data_rollover", "hotspot", "streaming", "cloud_storage", "security"],
                "migrations": ["prepaid_to_postpaid", "individual_to_family", "consumer_to_business"]
            },
            "account": {
                "security": ["password_reset", "two_factor", "unauthorized_access", "sim_swap", "fraud"],
                "management": ["authorized_users", "billing_address", "email_update", "merge_accounts"],
                "porting": ["number_in", "number_out", "status_check", "port_protection"],
                "emergency": ["lost_device", "stolen_device", "suspend_line", "international_block"]
            }
        }
        
        # Complex customer profiles
        self.customer_profiles = [
            {
                "type": "tech_executive",
                "traits": ["demanding", "knowledgeable", "time_sensitive"],
                "context": "managing multiple business lines",
                "emotion_pattern": ["professional", "impatient", "frustrated", "satisfied"]
            },
            {
                "type": "elderly_retiree",
                "traits": ["confused", "patient", "needs_repetition"],
                "context": "first smartphone user",
                "emotion_pattern": ["confused", "worried", "grateful", "happy"]
            },
            {
                "type": "student_abroad",
                "traits": ["anxious", "budget_conscious", "tech_savvy"],
                "context": "studying overseas",
                "emotion_pattern": ["worried", "concerned", "relieved", "thankful"]
            },
            {
                "type": "small_business_owner",
                "traits": ["practical", "cost_focused", "busy"],
                "context": "managing employee lines",
                "emotion_pattern": ["businesslike", "questioning", "negotiating", "satisfied"]
            },
            {
                "type": "frequent_traveler",
                "traits": ["experienced", "specific_needs", "impatient"],
                "context": "international roaming issues",
                "emotion_pattern": ["direct", "frustrated", "demanding", "accepting"]
            },
            {
                "type": "parent_teenager",
                "traits": ["concerned", "protective", "cost_aware"],
                "context": "managing family plan",
                "emotion_pattern": ["worried", "questioning", "firm", "relieved"]
            },
            {
                "type": "gig_worker",
                "traits": ["flexible", "app_dependent", "connectivity_critical"],
                "context": "needs reliable service for work",
                "emotion_pattern": ["stressed", "urgent", "persistent", "grateful"]
            },
            {
                "type": "rural_customer",
                "traits": ["practical", "coverage_focused", "loyal"],
                "context": "limited service options",
                "emotion_pattern": ["patient", "explaining", "hopeful", "understanding"]
            }
        ]
        
        # Conversation dynamics
        self.dynamics = [
            "straightforward",  # Simple flow
            "escalating",      # Getting more complex
            "circular",        # Customer repeats concerns
            "interrupted",     # Connection issues/background noise
            "multi_issue",     # Multiple problems
            "discovery",       # Uncovering root cause
            "negotiation",     # Seeking better deal
            "educational"      # Agent teaches customer
        ]
        
        # Regional Turkish variations
        self.turkish_regions = {
            "istanbul": {"dialect": "neutral", "pace": "fast", "formality": "medium"},
            "ankara": {"dialect": "formal", "pace": "moderate", "formality": "high"},
            "izmir": {"dialect": "aegean", "pace": "relaxed", "formality": "low"},
            "antalya": {"dialect": "mediterranean", "pace": "slow", "formality": "low"},
            "trabzon": {"dialect": "blacksea", "pace": "fast", "formality": "medium"},
            "erzurum": {"dialect": "eastern", "pace": "slow", "formality": "high"},
            "adana": {"dialect": "southern", "pace": "fast", "formality": "low"},
            "bursa": {"dialect": "marmara", "pace": "moderate", "formality": "medium"},
            "konya": {"dialect": "central", "pace": "slow", "formality": "high"},
            "diyarbakir": {"dialect": "southeastern", "pace": "moderate", "formality": "medium"}
        }
        
        self.output_dir = "data/flash_heavy_dataset"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # STRICT tool definitions - ONLY USE THESE
        self.allowed_tools = [
            "verify_user", "get_customer_status", "route_to_agent",
            "check_esim_status", "check_device_imei", "reissue_activation_code", "create_tech_ticket",
            "get_customer_plan", "list_all_plans", "change_customer_plan", "check_plan_compatibility",
            "get_last_bill", "get_unpaid_amount", "apply_campaign_discount", "create_payment_note",
            "search_faq", "get_common_solutions", "send_help_sms", "create_info_ticket",
            "escalate_to_human", "end_conversation"
        ]
    
    def create_complex_scenario(self):
        """Create a complex, multi-layered scenario"""
        
        # Pick primary and secondary issues
        primary_category = random.choice(list(self.scenario_matrix.keys()))
        primary_subcategory = random.choice(list(self.scenario_matrix[primary_category].keys()))
        primary_issue = random.choice(self.scenario_matrix[primary_category][primary_subcategory])
        
        # Sometimes add secondary issue
        has_secondary = random.random() > 0.6
        if has_secondary:
            secondary_category = random.choice(list(self.scenario_matrix.keys()))
            secondary_subcategory = random.choice(list(self.scenario_matrix[secondary_category].keys()))
            secondary_issue = random.choice(self.scenario_matrix[secondary_category][secondary_subcategory])
        else:
            secondary_issue = None
        
        return {
            "primary": f"{primary_category}_{primary_subcategory}_{primary_issue}",
            "secondary": f"{secondary_category}_{secondary_subcategory}_{secondary_issue}" if secondary_issue else None,
            "complexity": "complex" if has_secondary else "medium"
        }
    
    def generate_rich_conversation(self, idx: int) -> dict:
        """Generate one rich, detailed conversation"""
        
        scenario = self.create_complex_scenario()
        profile = random.choice(self.customer_profiles)
        region = random.choice(list(self.turkish_regions.keys()))
        region_info = self.turkish_regions[region]
        dynamic = random.choice(self.dynamics)
        
        # Determine conversation length based on complexity
        if scenario["complexity"] == "complex":
            min_turns = 10
            max_turns = 16
        else:
            min_turns = 6
            max_turns = 12
        
        turns = random.randint(min_turns, max_turns)
        
        # Agent flow based on scenario
        if "technical" in scenario["primary"]:
            agents = ["RouterAgent", "TechAgent"]
        elif "billing" in scenario["primary"]:
            agents = ["RouterAgent", "BillingAgent"]
        elif "plans" in scenario["primary"]:
            agents = ["RouterAgent", "PlanAgent"]
        else:
            agents = ["RouterAgent", "FAQAgent"]
        
        # Add third agent for complex scenarios
        if scenario["secondary"]:
            if "billing" in scenario["secondary"] and "BillingAgent" not in agents:
                agents.append("BillingAgent")
            elif "technical" in scenario["secondary"] and "TechAgent" not in agents:
                agents.append("TechAgent")
            elif "plans" in scenario["secondary"] and "PlanAgent" not in agents:
                agents.append("PlanAgent")
        
        prompt = f"""Generate RICH Turkish telco conversation with depth and nuance.

PRIMARY ISSUE: {scenario["primary"]}
SECONDARY ISSUE: {scenario["secondary"] if scenario["secondary"] else "none"}
CUSTOMER PROFILE: {profile["type"]}
TRAITS: {', '.join(profile["traits"])}
CONTEXT: {profile["context"]}
REGION: {region} ({region_info["dialect"]} dialect, {region_info["pace"]} pace, {region_info["formality"]} formality)
CONVERSATION DYNAMIC: {dynamic}
EMOTIONAL JOURNEY: {' → '.join(profile["emotion_pattern"])}
AGENT FLOW: {' → '.join(agents)}
TARGET LENGTH: {turns} turns

REQUIREMENTS:
1. Customer speaks with {region} regional characteristics
2. Show {profile["type"]} personality consistently
3. Include {profile["context"]} naturally in conversation
4. Follow {dynamic} conversation pattern
5. Emotions evolve: {' → '.join(profile["emotion_pattern"])}
6. ONLY use these tools: {', '.join(self.allowed_tools[:10])}
   (verify_user, get_customer_status, route_to_agent, check_esim_status, get_last_bill, etc.)
7. Include natural pauses, clarifications, interruptions
8. Make dialogue authentic and varied
9. Show problem-solving process realistically
10. If secondary issue exists, discover it during conversation

OUTPUT JSON:
{{
  "id": "flash_heavy_{idx:04d}",
  "primary_issue": "{scenario["primary"]}",
  "secondary_issue": {json.dumps(scenario["secondary"])},
  "customer_profile": "{profile["type"]}",
  "region": "{region}",
  "dialect_info": {json.dumps(region_info)},
  "conversation_dynamic": "{dynamic}",
  "complexity": "{scenario["complexity"]}",
  "metadata": {{
    "context": "{profile["context"]}",
    "traits": {json.dumps(profile["traits"])},
    "emotional_journey": {json.dumps(profile["emotion_pattern"])}
  }},
  "customer_turns_for_tts": [
    {{
      "turn_id": "turn_001",
      "text": "...",
      "emotion": "{profile["emotion_pattern"][0]}",
      "dialect_markers": ["{region_info["dialect"]}"],
      "pace": "{region_info["pace"]}",
      "background_context": "{profile["context"]}"
    }}
  ],
  "agent_responses": [
    {{
      "turn_id": "turn_002",
      "agent_persona": "RouterAgent",
      "text": "...",
      "tools_triggered": ["verify_user"],
      "formality_level": "{region_info["formality"]}"
    }}
  ],
  "agent_handoffs": [
    {{
      "at_turn": 4,
      "from": "RouterAgent",
      "to": "...",
      "reason": "...",
      "context_preserved": true
    }}
  ],
  "conversation_notes": {{
    "resolution": "how the issue was resolved",
    "customer_satisfaction": "final emotional state",
    "follow_up_needed": true/false
  }}
}}

Create a REALISTIC, NUANCED conversation that feels authentic!"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.8,
                    max_output_tokens=8192,  # Allow longer for rich content
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
            conv["model"] = "flash"
            conv["index"] = idx
            
            return conv
            
        except Exception as e:
            print(f"  Error {idx}: {str(e)[:100]}")
            return None
    
    def generate_heavy_batch(self, total: int = 200):
        """Generate batch with Flash only"""
        
        print(f"\n{'='*80}")
        print(f"🔥 FLASH HEAVY GENERATOR")
        print(f"🎯 Generating {total} rich conversations")
        print(f"📊 Using ONLY Flash model for quality")
        print(f"🌍 {len(self.turkish_regions)} regional variations")
        print(f"👥 {len(self.customer_profiles)} customer profiles")
        print(f"🎭 {len(self.dynamics)} conversation dynamics")
        print(f"{'='*80}\n")
        
        successful = []
        failed = 0
        
        with ThreadPoolExecutor(max_workers=5) as executor:  # Less parallelism for Flash
            futures = {
                executor.submit(self.generate_rich_conversation, i): i 
                for i in range(total)
            }
            
            for future in as_completed(futures):
                idx = futures[future]
                result = future.result()
                
                if result:
                    filename = f"{self.output_dir}/flash_heavy_{idx:04d}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    
                    successful.append(result)
                    
                    if len(successful) % 10 == 0:
                        print(f"  ✅ Progress: {len(successful)}/{total}")
                        time.sleep(3)  # Rate limit for Flash
                else:
                    failed += 1
                
                if len(successful) % 25 == 0:
                    time.sleep(5)  # Longer pause
        
        # Detailed statistics
        print(f"\n{'='*80}")
        print(f"📊 GENERATION COMPLETE!")
        print(f"✅ Success: {len(successful)}/{total} ({100*len(successful)/total:.1f}%)")
        if failed > 0:
            print(f"❌ Failed: {failed}")
        
        # Analyze richness
        complexities = {"complex": 0, "medium": 0}
        regions = {}
        profiles = {}
        dynamics = {}
        has_secondary = 0
        
        for conv in successful:
            complexities[conv.get("complexity", "medium")] += 1
            regions[conv.get("region", "unknown")] = regions.get(conv.get("region", "unknown"), 0) + 1
            profiles[conv.get("customer_profile", "unknown")] = profiles.get(conv.get("customer_profile", "unknown"), 0) + 1
            dynamics[conv.get("conversation_dynamic", "unknown")] = dynamics.get(conv.get("conversation_dynamic", "unknown"), 0) + 1
            if conv.get("secondary_issue"):
                has_secondary += 1
        
        print(f"\n📈 RICHNESS ANALYSIS:")
        print(f"  Complex scenarios: {complexities.get('complex', 0)}/{len(successful)}")
        print(f"  Multi-issue conversations: {has_secondary}")
        print(f"  Unique regions used: {len(regions)}")
        print(f"  Unique profiles used: {len(profiles)}")
        print(f"  Unique dynamics used: {len(dynamics)}")
        
        # Character count
        total_chars = 0
        for conv in successful:
            for turn in conv.get('customer_turns_for_tts', []):
                total_chars += len(turn.get('text', ''))
        
        print(f"\n📝 TTS Requirements:")
        print(f"  Total characters: {total_chars:,}")
        print(f"  Average per conversation: {total_chars//len(successful):,}")
        
        print(f"\n💾 Output: {self.output_dir}")
        
        return successful

def main():
    generator = FlashHeavyGenerator()
    
    # Generate 200 rich conversations
    conversations = generator.generate_heavy_batch(total=200)
    
    print(f"\n🎯 Quality over quantity!")
    print(f"   These conversations are richer and more varied")
    print(f"   Better for training a sophisticated model")

if __name__ == "__main__":
    main()