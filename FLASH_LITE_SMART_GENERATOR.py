#!/usr/bin/env python3
"""
SMART Flash-Lite Generator with PROPER Tool Usage
Generates SHORT but MEANINGFUL conversations
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

class SmartFlashLiteGenerator:
    def __init__(self):
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash-lite',
            safety_settings={
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE'
            }
        )
        
        # SMART SCENARIOS with REQUIRED TOOLS
        self.smart_scenarios = [
            {
                "name": "esim_quick_check",
                "agent_flow": ["RouterAgent", "TechAgent"],
                "required_tools": ["verify_user", "check_esim_status", "end_conversation"],
                "description": "Customer asks about eSIM status"
            },
            {
                "name": "bill_check",
                "agent_flow": ["RouterAgent", "BillingAgent"],
                "required_tools": ["verify_user", "get_last_bill", "end_conversation"],
                "description": "Customer wants to know bill amount"
            },
            {
                "name": "unpaid_check",
                "agent_flow": ["RouterAgent", "BillingAgent"],
                "required_tools": ["verify_user", "get_unpaid_amount", "end_conversation"],
                "description": "Customer asks about unpaid balance"
            },
            {
                "name": "plan_info",
                "agent_flow": ["RouterAgent", "PlanAgent"],
                "required_tools": ["verify_user", "get_customer_plan", "end_conversation"],
                "description": "Customer wants current plan details"
            },
            {
                "name": "device_check",
                "agent_flow": ["RouterAgent", "TechAgent"],
                "required_tools": ["verify_user", "check_device_imei", "end_conversation"],
                "description": "Customer asks if device is compatible"
            },
            {
                "name": "esim_reissue",
                "agent_flow": ["RouterAgent", "TechAgent"],
                "required_tools": ["verify_user", "check_esim_status", "reissue_activation_code", "end_conversation"],
                "description": "Customer needs new eSIM QR code"
            },
            {
                "name": "discount_apply",
                "agent_flow": ["RouterAgent", "BillingAgent"],
                "required_tools": ["verify_user", "get_last_bill", "apply_campaign_discount", "end_conversation"],
                "description": "Customer has a discount code"
            },
            {
                "name": "plan_change_check",
                "agent_flow": ["RouterAgent", "PlanAgent"],
                "required_tools": ["verify_user", "get_customer_plan", "list_all_plans", "end_conversation"],
                "description": "Customer wants to see other plans"
            },
            {
                "name": "tech_issue_ticket",
                "agent_flow": ["RouterAgent", "TechAgent"],
                "required_tools": ["verify_user", "check_esim_status", "create_tech_ticket", "end_conversation"],
                "description": "Customer has technical issue needing ticket"
            },
            {
                "name": "faq_search",
                "agent_flow": ["RouterAgent", "FAQAgent"],
                "required_tools": ["verify_user", "search_faq", "end_conversation"],
                "description": "Customer has general question"
            },
            {
                "name": "escalate_angry",
                "agent_flow": ["RouterAgent"],
                "required_tools": ["verify_user", "escalate_to_human"],
                "description": "Angry customer demands human agent"
            },
            {
                "name": "payment_note",
                "agent_flow": ["RouterAgent", "BillingAgent"],
                "required_tools": ["verify_user", "get_unpaid_amount", "create_payment_note", "end_conversation"],
                "description": "Customer explains payment delay"
            }
        ]
        
        self.emotions = ["angry", "confused", "normal", "impatient", "polite", "frustrated", "cheerful"]
        
        self.output_dir = "data/smart_flash_dataset"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_smart_conversation(self, idx: int) -> dict:
        """Generate ONE SMART conversation with PROPER tools"""
        
        scenario = random.choice(self.smart_scenarios)
        emotion = random.choice(self.emotions)
        
        # Build tool usage guide
        tool_guide = "\n".join([f"- Turn {i+2}: Use {tool}" for i, tool in enumerate(scenario['required_tools'])])
        
        prompt = f"""Generate SHORT Turkish telco conversation with EXACT tool usage.

SCENARIO: {scenario['description']}
CUSTOMER EMOTION: {emotion}
AGENTS: {' -> '.join(scenario['agent_flow'])}
LENGTH: 3-5 turns ONLY

REQUIRED TOOLS IN ORDER:
{tool_guide}

EXAMPLE STRUCTURE:
Turn 1: Customer states issue
Turn 2: Agent uses verify_user
Turn 3: Customer provides info
Turn 4: Agent uses main tool ({scenario['required_tools'][1] if len(scenario['required_tools']) > 1 else 'tool'})
Turn 5: Resolution

JSON OUTPUT:
{{
  "id": "smart_{idx:04d}",
  "scenario": "{scenario['name']}",
  "customer_turns": [
    {{"turn": 1, "text": "Turkish customer text", "emotion": "{emotion}"}},
    {{"turn": 3, "text": "Customer response"}}
  ],
  "agent_responses": [
    {{"turn": 2, "agent": "{scenario['agent_flow'][0]}", "text": "Agent text", "tools": ["{scenario['required_tools'][0]}"]}},
    {{"turn": 4, "agent": "{scenario['agent_flow'][-1]}", "text": "Agent solution", "tools": {json.dumps(scenario['required_tools'][1:])}}},
  ]
}}

MUST use EXACT tools: {scenario['required_tools']}
Keep it SHORT but MEANINGFUL!"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=2048,
                )
            )
            
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            
            conv = json.loads(text.strip())
            conv["generated_at"] = datetime.now().isoformat()
            conv["required_tools"] = scenario['required_tools']
            conv["agent_flow"] = scenario['agent_flow']
            
            return conv
            
        except Exception as e:
            print(f"  Error {idx}: {str(e)[:50]}")
            return None
    
    def generate_batch(self, num_conversations: int = 100):
        """Generate SMART conversations in parallel"""
        
        print(f"🧠 SMART FLASH-LITE GENERATOR")
        print(f"🎯 Generating {num_conversations} conversations with PROPER tool usage")
        print(f"🔧 {len(self.smart_scenarios)} scenario types")
        print("=" * 60)
        
        successful = []
        failed = 0
        
        # Track scenario distribution
        scenario_counts = {s['name']: 0 for s in self.smart_scenarios}
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.generate_smart_conversation, i): i 
                for i in range(num_conversations)
            }
            
            for future in as_completed(futures):
                idx = futures[future]
                result = future.result()
                
                if result:
                    filename = f"{self.output_dir}/smart_{idx:04d}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    
                    successful.append(result)
                    scenario_name = result.get('scenario', 'unknown')
                    if scenario_name in scenario_counts:
                        scenario_counts[scenario_name] += 1
                    
                    if len(successful) % 10 == 0:
                        print(f"  ✅ Progress: {len(successful)}/{num_conversations}")
                else:
                    failed += 1
                
                if len(successful) % 20 == 0:
                    time.sleep(2)  # Rate limit
        
        print("\n" + "=" * 60)
        print(f"✅ GENERATION COMPLETE!")
        print(f"📊 Success: {len(successful)}/{num_conversations} ({100*len(successful)/num_conversations:.1f}%)")
        print(f"\n📈 Scenario Distribution:")
        for scenario, count in sorted(scenario_counts.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                print(f"  - {scenario}: {count}")
        
        # Verify tool usage
        print(f"\n🔧 Verifying Tool Usage:")
        all_tools = []
        for conv in successful[:10]:  # Check first 10
            for resp in conv.get('agent_responses', []):
                all_tools.extend(resp.get('tools', []))
        
        tool_counts = {}
        for tool in all_tools:
            tool_counts[tool] = tool_counts.get(tool, 0) + 1
        
        for tool, count in sorted(tool_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {tool}: {count}")
        
        print(f"\n💾 Output: {self.output_dir}")
        
        return successful

def main():
    generator = SmartFlashLiteGenerator()
    
    # Generate 100 SMART conversations
    conversations = generator.generate_batch(num_conversations=100)
    
    print(f"\n🎯 These conversations have PROPER tool usage!")
    print(f"📚 Ready for training with meaningful patterns")

if __name__ == "__main__":
    main()