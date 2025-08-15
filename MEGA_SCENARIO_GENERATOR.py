"""
🚀 MEGA SCENARIO GENERATOR - ULTIMATE TURKISH TELCO DATASET
⚡ ALWAYS AND ALWAYS AND ALWAYS USE GEMINI 2.5 FLASH!
🔥 COMPREHENSIVE COVERAGE OF ALL POSSIBLE SCENARIOS!
"""

import google.generativeai as genai
import json
import time
import random
from datetime import datetime
from typing import Dict, List, Any

# ⚡ ALWAYS AND ALWAYS AND ALWAYS USE GEMINI 2.5 FLASH!
GEMINI_API_KEY = "AIzaSyBzC3ydAP1qKkGyRkJ9t1sp5D3QN9QyzsQ"
genai.configure(api_key=GEMINI_API_KEY)

class MegaScenarioGenerator:
    """Ultimate comprehensive Turkish telco scenario generator."""
    
    def __init__(self):
        # ⚡ ALWAYS AND ALWAYS AND ALWAYS USE GEMINI 2.5 FLASH!
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        # MEGA SCENARIO CATEGORIES
        self.scenarios = {
            # eSIM SCENARIOS (30+ variations)
            "esim_scenarios": [
                "eSIM activation failed", "eSIM code not received", "eSIM stuck in pending",
                "eSIM device compatibility", "eSIM QR code issues", "eSIM manual setup",
                "eSIM transfer between devices", "eSIM dual SIM setup", "eSIM international roaming",
                "eSIM backup/restore", "eSIM profile deletion", "eSIM carrier switch",
                "eSIM iOS setup", "eSIM Android setup", "eSIM Windows phone",
                "eSIM smartwatch setup", "eSIM tablet setup", "eSIM laptop setup",
                "eSIM family sharing", "eSIM business account", "eSIM temporary disable",
                "eSIM reactivation", "eSIM network selection", "eSIM APN settings",
                "eSIM VoLTE enable", "eSIM 5G setup", "eSIM carrier aggregation",
                "eSIM speed issues", "eSIM battery drain", "eSIM signal problems"
            ],
            
            # DEVICE SCENARIOS (25+ variations)
            "device_scenarios": [
                "iPhone compatibility", "Samsung compatibility", "Xiaomi compatibility",
                "Huawei compatibility", "Oppo compatibility", "Vivo compatibility",
                "Google Pixel compatibility", "OnePlus compatibility", "Sony compatibility",
                "Nokia compatibility", "iPad compatibility", "Samsung tablet",
                "smartwatch compatibility", "laptop compatibility", "router compatibility",
                "old device upgrade", "IMEI not registered", "stolen device report",
                "device unlock request", "device blacklist check", "warranty status",
                "repair service", "device insurance", "device trade-in", "device financing"
            ],
            
            # PACKAGE SCENARIOS (40+ variations)
            "package_scenarios": [
                "5GB to 10GB upgrade", "10GB to 20GB upgrade", "20GB to unlimited",
                "unlimited to limited", "family plan setup", "business plan inquiry",
                "student discount", "senior citizen discount", "loyalty discount",
                "seasonal promotions", "bundle packages", "voice-only plan",
                "data-only plan", "international roaming", "Europe roaming",
                "worldwide roaming", "roaming addon", "extra data purchase",
                "speed boost addon", "hotspot addon", "music streaming addon",
                "video streaming addon", "gaming addon", "social media addon",
                "early contract termination", "contract renewal", "postpaid to prepaid",
                "prepaid to postpaid", "corporate account", "government discount",
                "NGO discount", "disabled person discount", "veteran discount",
                "package downgrade", "temporary suspension", "vacation hold",
                "payment plan setup", "auto-pay setup", "billing cycle change",
                "shared data plan", "multi-line discount", "friend referral"
            ],
            
            # BILLING SCENARIOS (35+ variations)
            "billing_scenarios": [
                "high bill complaint", "billing error dispute", "payment failure",
                "credit card declined", "bank transfer failed", "direct debit setup",
                "payment method change", "billing address change", "tax exemption",
                "corporate billing", "invoice request", "payment history",
                "credit limit inquiry", "deposit requirement", "refund request",
                "overpayment refund", "duplicate charge", "unauthorized charge",
                "late payment fee", "reconnection fee", "early termination fee",
                "international charge dispute", "roaming charge dispute", "premium service charge",
                "third-party billing", "carrier billing", "subscription management",
                "auto-renewal disable", "promotional credit", "loyalty credit",
                "compensation request", "service credit", "billing cycle inquiry",
                "tax calculation", "receipt request", "payment proof"
            ],
            
            # TECHNICAL SCENARIOS (30+ variations)
            "technical_scenarios": [
                "no signal coverage", "weak signal strength", "call drops frequently",
                "SMS not sending", "SMS not receiving", "MMS issues",
                "internet speed slow", "connection timeout", "DNS issues",
                "VPN problems", "hotspot not working", "tethering issues",
                "VoLTE problems", "WiFi calling issues", "video call problems",
                "app connectivity", "streaming issues", "gaming lag",
                "network congestion", "tower maintenance", "outage report",
                "interference issues", "building coverage", "basement coverage",
                "rural area coverage", "highway coverage", "airport coverage",
                "metro coverage", "tunnel coverage", "elevator issues",
                "weather impact coverage"
            ],
            
            # CUSTOMER SERVICE SCENARIOS (25+ variations)
            "service_scenarios": [
                "complaint escalation", "service quality feedback", "technical support",
                "account security", "password reset", "PIN change",
                "number portability", "number change request", "caller ID issues",
                "call forwarding", "call waiting", "call blocking",
                "Do Not Disturb setup", "voicemail setup", "voicemail retrieval",
                "conference calling", "international calling", "premium numbers",
                "emergency services", "accessibility services", "language preference",
                "communication preference", "marketing opt-out", "data privacy",
                "GDPR request"
            ],
            
            # EMERGENCY SCENARIOS (15+ variations)
            "emergency_scenarios": [
                "service outage", "natural disaster impact", "emergency contact",
                "urgent reconnection", "hospital/medical emergency", "police report",
                "fraud alert", "identity theft", "unauthorized access",
                "SIM swap attack", "account compromise", "suspicious activity",
                "lost phone emergency", "stolen device", "emergency roaming"
            ],
            
            # BUSINESS SCENARIOS (20+ variations)
            "business_scenarios": [
                "corporate account setup", "bulk device orders", "enterprise solutions",
                "IoT connectivity", "M2M services", "fleet management",
                "employee management", "cost center billing", "volume discounts",
                "dedicated account manager", "SLA agreements", "priority support",
                "custom solutions", "API integration", "white-label services",
                "partner program", "reseller inquiry", "wholesale pricing",
                "government contracts", "public sector"
            ]
        }
        
        # MEGA CONTEXT VARIATIONS
        self.contexts = [
            "SIM", "PLAN", "BILLING", "COVERAGE", "DEVICE", "TECHNICAL", 
            "EMERGENCY", "BUSINESS", "MIXED", "COMPLEX"
        ]
        
        # MEGA QUALITY TIERS
        self.quality_tiers = [
            "foundation", "intermediate", "advanced", "expert", 
            "precision", "robustness", "elite", "ultimate"
        ]
        
        # MEGA NOISE PATTERNS
        self.noise_patterns = {
            "heavy": ["eSIM → mevsim", "IMEI → aymay", "gigabyte → giga bayt", "çekmiyor → cekmiyo"],
            "medium": ["değiştirmek → degistirmek", "paket → paketi", "müşteri → musteri"],
            "light": ["5GB → beş GB", "WiFi → vayfi", "internet → interneti"]
        }
        
        # LOCATION SCENARIOS
        self.locations = [
            "İstanbul Avrupa", "İstanbul Anadolu", "Ankara", "İzmir", "Bursa", "Antalya",
            "Gaziantep", "Konya", "Şanlıurfa", "Kayseri", "Mersin", "Eskişehir",
            "Diyarbakır", "Samsun", "Denizli", "Şile", "Silivri", "Çatalca",
            "Gökçeada", "Bozcaada", "Uludağ", "Pamukkale", "Kapadokya", "Bodrum",
            "Marmaris", "Alanya", "Trabzon", "Erzurum", "Van", "Mardin",
            "kırsal kesim", "dağlık bölge", "sahil kenarı", "metro istasyonu",
            "AVM içi", "bodrum kat", "asansör", "tünel", "otoyol", "havalimanı"
        ]
    
    def create_mega_prompt(self, scenario_type: str, count: int = 50) -> str:
        """Create ultimate comprehensive prompt for specific scenario type."""
        
        scenarios = self.scenarios.get(scenario_type, [])
        
        return f"""
🚀 MEGA TURKISH TELCO DATASET GENERATION
⚡ ALWAYS AND ALWAYS AND ALWAYS USE GEMINI 2.5 FLASH!

Generate {count} ULTRA-COMPREHENSIVE Turkish telco customer service dialogs focusing on: {scenario_type.upper()}

📞 MANDATORY CALL CENTER FLOW:
1. Agent: "Merhaba, Türk Telekom eSIM hizmetleri, size nasıl yardımcı olabilirim?"
2. Customer: [Problem with realistic Turkish ASR noise]
3. Agent: "Aradığınız numara 0 555 XXX XX XX bu mu?" (TTS-friendly spacing)
4. Customer: "Evet" or "Hayır" + correction
5. Tool: verify_user with full msisdn
6. Continue problem solving...

🎯 SCENARIO FOCUS: {scenario_type}
Target scenarios: {scenarios[:20]}  # First 20 scenarios

📋 STRICT JSON FORMAT:
```json
{{
  "conversations": [
    {{"role": "assistant", "content": [{{"type": "text", "text": "Merhaba, Türk Telekom eSIM hizmetleri..."}}]}},
    {{"role": "user", "content": [{{"type": "text", "text": "[Turkish with realistic ASR noise]"}}]}},
    {{"role": "assistant", "content": [{{"type": "text", "text": "Aradığınız numara 0 555 XXX XX XX bu mu?"}}]}},
    {{"role": "user", "content": [{{"type": "text", "text": "Evet"}}]}},
    {{"role": "assistant", "content": [{{"type": "text", "text": "{{\\"tool_call\\":{{\\"id\\":\\"call_unique\\",\\"name\\":\\"verify_user\\",\\"arguments\\":{{\\"maiden_name\\":\\"system\\",\\"msisdn\\":\\"905551234567\\"}}}}}}"}}]}},
    {{"role": "user", "content": [{{"type": "text", "text": "<tool_result>{{\\"success\\":true,\\"customer_id\\":\\"12345\\",\\"name\\":\\"Ali Doğan\\"}}</tool_result>"}}]}},
    {{"role": "assistant", "content": [{{"type": "text", "text": "[Continue problem solving...]"}}]}}
  ],
  "id": "D001",
  "scenario": "{scenario_type}|phone_confirmation|[additional_tags]",
  "context": "[SIM|PLAN|BILLING|COVERAGE|DEVICE|TECHNICAL|EMERGENCY|BUSINESS|MIXED]",
  "noise": true,
  "quality": "[foundation|intermediate|advanced|expert|precision|robustness|elite|ultimate]"
}}
```

🔧 BACKEND COMPATIBLE TOOLS:
- verify_user(maiden_name="system", msisdn="905551234567")
- get_user_info(customer_id="12345")
- check_device_registration(customer_id="12345", imei="359123456789012")
- reissue_activation_code(customer_id="12345")
- get_activation_steps(os_type="iOS|Android")
- get_activation_status(customer_id="12345")
- get_available_packages(customer_id="12345")
- change_package(customer_id="12345", package_id="premium_10gb")
- create_support_ticket(customer_id="12345", subject="Issue", description="Details", priority="normal|high")

🎭 ADVANCED SCENARIOS TO INCLUDE:
- Wrong number corrections
- Failed verifications
- System errors/timeouts
- Multi-step complex flows
- Persona handoffs (RouterAgent→TechAgent/PlanAgent/BillingAgent)
- Context switches mid-conversation
- Error recovery scenarios
- Edge cases and unusual requests

🔊 REALISTIC TURKISH ASR NOISE (60% of dialogs):
- "eSIM" → "E sim", "İsim", "ESIM"
- "IMEI" → "İMEİ", "aymay", "imey"
- "çekmiyor" → "cekmiyor", "çekmiyo"
- "değiştirmek" → "degistirmek"
- "paket" → "paketi", "paketim"
- "5GB" → "beş GB", "beş gigabyte"
- "müşteri" → "musteri"
- Numbers: "sıfır beş beş beş" for "0555"

🏢 LOCATION SCENARIOS:
Include various locations: İstanbul, Ankara, İzmir, Şile, kırsal kesim, dağlık bölge, AVM içi, bodrum kat, etc.

🎯 QUALITY DISTRIBUTION:
- 20% foundation (simple scenarios)
- 30% intermediate (standard complexity)
- 30% advanced (multi-step flows)
- 15% expert (complex edge cases)  
- 5% ultimate (extremely complex scenarios)

⚡ GENERATE {count} DIALOGS NOW!
Output as clean JSON array - NO markdown formatting, NO extra text!
"""

    def generate_mega_scenario_batch(self, scenario_type: str, count: int = 50) -> List[Dict]:
        """Generate mega batch for specific scenario type."""
        
        prompt = self.create_mega_prompt(scenario_type, count)
        
        try:
            print(f"🚀 Generating {count} {scenario_type} scenarios with Gemini 2.5 Flash...")
            start_time = time.time()
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.9,  # Higher creativity
                    top_p=0.95,
                    top_k=50,
                    max_output_tokens=8192,
                )
            )
            
            generation_time = time.time() - start_time
            print(f"⚡ Generated in {generation_time:.2f} seconds!")
            
            # Parse JSON response
            if hasattr(response, 'text') and response.text:
                # Clean the response
                json_text = response.text.strip()
                if json_text.startswith('```json'):
                    json_text = json_text.replace('```json', '').replace('```', '').strip()
                
                try:
                    dialogs = json.loads(json_text)
                    if isinstance(dialogs, list):
                        print(f"✅ Successfully parsed {len(dialogs)} dialogs")
                        return dialogs
                    else:
                        print("❌ Response is not a list")
                        return []
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    print(f"Response preview: {json_text[:200]}...")
                    return []
            else:
                print("❌ No response text received")
                return []
                
        except Exception as e:
            print(f"❌ Error generating {scenario_type} batch: {e}")
            return []
    
    def generate_comprehensive_dataset(self, dialogs_per_scenario: int = 50) -> Dict[str, Any]:
        """Generate comprehensive dataset covering ALL scenarios."""
        
        print("🚀 STARTING MEGA COMPREHENSIVE DATASET GENERATION")
        print("⚡ ALWAYS AND ALWAYS AND ALWAYS USE GEMINI 2.5 FLASH!")
        print("=" * 80)
        
        all_dialogs = []
        scenario_results = {}
        total_start_time = time.time()
        
        for scenario_type in self.scenarios.keys():
            print(f"\n🎯 Processing {scenario_type}...")
            
            batch_dialogs = self.generate_mega_scenario_batch(scenario_type, dialogs_per_scenario)
            
            if batch_dialogs:
                all_dialogs.extend(batch_dialogs)
                scenario_results[scenario_type] = len(batch_dialogs)
                print(f"✅ {scenario_type}: {len(batch_dialogs)} dialogs")
                
                # Save individual scenario batch
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                scenario_file = f"data/mega_generated/{scenario_type}_{len(batch_dialogs)}_{timestamp}.json"
                
                import os
                os.makedirs("data/mega_generated", exist_ok=True)
                
                with open(scenario_file, 'w', encoding='utf-8') as f:
                    json.dump(batch_dialogs, f, indent=2, ensure_ascii=False)
                
                print(f"💾 Saved: {scenario_file}")
            else:
                scenario_results[scenario_type] = 0
                print(f"❌ {scenario_type}: FAILED")
            
            # Rate limiting
            time.sleep(2)
        
        total_time = time.time() - total_start_time
        
        # Final comprehensive results
        print("\n" + "🏆" * 80)
        print("🎉 MEGA COMPREHENSIVE DATASET GENERATION COMPLETE!")
        print(f"⏱️ Total time: {total_time/60:.1f} minutes")
        print(f"📊 Total dialogs: {len(all_dialogs)}")
        print("\n📋 Scenario breakdown:")
        for scenario, count in scenario_results.items():
            print(f"   {scenario}: {count} dialogs")
        
        # Save master dataset
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        master_file = f"data/mega_generated/MEGA_COMPREHENSIVE_{len(all_dialogs)}_{timestamp}.json"
        
        with open(master_file, 'w', encoding='utf-8') as f:
            json.dump(all_dialogs, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 MASTER DATASET SAVED: {master_file}")
        print("🏆" * 80)
        
        return {
            "total_dialogs": len(all_dialogs),
            "scenario_results": scenario_results,
            "generation_time": total_time,
            "master_file": master_file,
            "all_dialogs": all_dialogs
        }

def main():
    """Main mega generation function."""
    print("🚀 MEGA SCENARIO GENERATOR - ULTIMATE TURKISH TELCO DATASET")
    print("⚡ ALWAYS AND ALWAYS AND ALWAYS USE GEMINI 2.5 FLASH!")
    print("🔥 COMPREHENSIVE COVERAGE OF ALL POSSIBLE SCENARIOS!")
    print("=" * 80)
    
    generator = MegaScenarioGenerator()
    
    # Start mega generation
    print(f"🎯 Scenarios to generate: {list(generator.scenarios.keys())}")
    print(f"📊 Estimated total dialogs: {len(generator.scenarios) * 50} (50 per scenario)")
    
    confirm = input("\n🚀 Start mega generation? (y/n): ")
    if confirm.lower() != 'y':
        print("❌ Generation cancelled")
        return
    
    # Generate comprehensive dataset
    results = generator.generate_comprehensive_dataset(dialogs_per_scenario=50)
    
    print(f"\n🎉 MEGA GENERATION COMPLETE!")
    print(f"📊 Final results: {results['total_dialogs']} dialogs")
    print(f"💾 Master file: {results['master_file']}")

if __name__ == "__main__":
    main()
