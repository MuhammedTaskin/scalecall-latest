#!/usr/bin/env python3
"""
THE REAL TRAINING DATASET GENERATOR
This time we do it right - generate NEW agent responses for every audio input
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import google.generativeai as genai
from tqdm import tqdm
import random

# Configure Gemini
API_KEY = "AIzaSyBzC3ydAP1qKkGyRkJ9t1sp5D3QN9QyzsQ"
genai.configure(api_key=API_KEY)

# Use Gemini 2.5 Flash-Lite for speed and cost efficiency
model = genai.GenerativeModel(
    'gemini-2.5-flash-lite',  # Fastest and most cost-efficient
    generation_config={
        "temperature": 0.3,  # Low for consistency but not zero for variety
        "top_p": 0.9,
        "top_k": 40,
        "max_output_tokens": 1024
    }
)

# VALID TOOLS - The only 21 tools allowed
VALID_TOOLS = {
    "verify_user": "Verify customer identity",
    "get_customer_status": "Get customer account status", 
    "route_to_agent": "Transfer to specialized agent",
    "check_esim_status": "Check eSIM activation status",
    "check_device_imei": "Verify device compatibility",
    "reissue_activation_code": "Generate new eSIM QR code",
    "create_tech_ticket": "Create technical support ticket",
    "get_customer_plan": "Get current plan details",
    "list_all_plans": "List available plans",
    "change_customer_plan": "Change customer plan",
    "check_plan_compatibility": "Check plan compatibility",
    "get_last_bill": "Get latest bill details",
    "get_unpaid_amount": "Get unpaid balance",
    "apply_campaign_discount": "Apply discount",
    "create_payment_note": "Create payment note",
    "search_faq": "Search knowledge base",
    "get_common_solutions": "Get common solutions",
    "send_help_sms": "Send help via SMS",
    "create_info_ticket": "Create info ticket",
    "escalate_to_human": "Transfer to human agent",
    "end_conversation": "End the conversation"
}

# Agent tool mapping
AGENT_TOOLS = {
    "RouterAgent": ["verify_user", "get_customer_status", "route_to_agent", "escalate_to_human"],
    "TechAgent": ["check_esim_status", "check_device_imei", "reissue_activation_code", "create_tech_ticket", "escalate_to_human"],
    "BillingAgent": ["get_last_bill", "get_unpaid_amount", "apply_campaign_discount", "create_payment_note", "escalate_to_human"],
    "PlanAgent": ["get_customer_plan", "list_all_plans", "change_customer_plan", "check_plan_compatibility", "escalate_to_human"],
    "FAQAgent": ["search_faq", "get_common_solutions", "send_help_sms", "create_info_ticket", "escalate_to_human"]
}

class AudioResponseGenerator:
    """Generate proper agent responses for audio inputs"""
    
    def __init__(self):
        self.conversations = self._load_conversations()
        self.training_data = []
        
    def _load_conversations(self) -> List[Dict]:
        """Load the 76 selected conversations"""
        with open('data/selected_for_tts.json', 'r', encoding='utf-8') as f:
            selected = json.load(f)
        
        conversations = []
        for conv_info in selected['conversations']:
            conv_path = Path(conv_info['path'])
            if conv_path.exists():
                with open(conv_path, 'r', encoding='utf-8') as f:
                    conv = json.load(f)
                    conv['conv_id'] = conv_info['id']
                    conversations.append(conv)
        
        return conversations
    
    def _extract_customer_text(self, turn: Dict) -> str:
        """Extract text from potentially nested turn"""
        if isinstance(turn, dict):
            # Handle nested structure
            if len(turn) == 1 and list(turn.keys())[0].startswith('turn_'):
                turn = turn[list(turn.keys())[0]]
            return turn.get('text', '')
        return ''
    
    def generate_agent_response(self, 
                               customer_text: str, 
                               context: List[Dict],
                               current_agent: str,
                               turn_number: int) -> Dict:
        """
        Generate a NEW agent response using Gemini
        This is the CORE function that creates proper responses
        """
        
        # Build context string
        context_str = ""
        if context:
            for ctx in context[-4:]:  # Last 4 turns for context
                if ctx['type'] == 'customer':
                    context_str += f"Müşteri: {ctx['text']}\n"
                elif ctx['type'] == 'agent':
                    context_str += f"{ctx['agent']}: {ctx['text']}\n"
                    if ctx.get('tools'):
                        context_str += f"[Araçlar: {', '.join(ctx['tools'])}]\n"
        
        # Get available tools for this agent
        available_tools = AGENT_TOOLS.get(current_agent, [])
        
        # Smart prompt that generates REALISTIC responses
        prompt = f"""Sen bir Türk telekom şirketi çağrı merkezi temsilcisisin.
Şu anda {current_agent} rolündesin.

{"KONUŞMA GEÇMİŞİ:\n" + context_str if context_str else "Bu ilk konuşma."}

MÜŞTERİ ŞİMDİ SÖYLÜYOR:
"{customer_text}"

GÖREV:
1. Müşterinin ne dediğini anla
2. Uygun araçları seç (maksimum 2-3 araç)
3. Doğal, yardımcı bir Türkçe yanıt oluştur

Kullanabileceğin araçlar: {', '.join(available_tools)}

Yanıtını JSON formatında ver:
{{
  "tools": ["araç1", "araç2"],
  "response": "Türkçe yanıt"
}}

ÖNEMLİ KURALLAR:
- Müşteri kimlik doğrulama isterse önce verify_user kullan
- Teknik sorunlar için check_esim_status veya check_device_imei kullan
- Başka birime yönlendirme gerekiyorsa route_to_agent kullan
- Yanıt kısa ve öz olmalı (2-3 cümle)
- Samimi ama profesyonel ol
- Müşterinin aciliyetini anla ve ona göre davran"""

        try:
            response = model.generate_content(prompt)
            # Extract JSON from response
            text = response.text.strip()
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(text)
            
            # Validate tools
            valid_tools = [t for t in result.get('tools', []) if t in available_tools]
            
            return {
                "agent": current_agent,
                "tools": valid_tools,
                "response": result.get('response', 'Anlıyorum, hemen yardımcı oluyorum.')
            }
            
        except Exception as e:
            # Fallback response
            print(f"Generation error: {e}")
            
            # Smart fallback based on turn number
            if turn_number == 1:
                return {
                    "agent": current_agent,
                    "tools": ["verify_user"] if current_agent == "RouterAgent" else [],
                    "response": "Merhaba, size nasıl yardımcı olabilirim? Güvenliğiniz için kimlik doğrulaması yapmamız gerekiyor."
                }
            else:
                return {
                    "agent": current_agent,
                    "tools": [],
                    "response": "Anlıyorum, hemen ilgileniyorum. Bir saniye lütfen."
                }
    
    def determine_agent_flow(self, customer_text: str, turn_number: int, previous_agent: str = None) -> str:
        """Determine which agent should handle this turn"""
        
        text_lower = customer_text.lower()
        
        # First turn is always RouterAgent
        if turn_number == 1 or previous_agent is None:
            return "RouterAgent"
        
        # Smart agent routing based on keywords
        if any(word in text_lower for word in ['esim', 'aktiv', 'bağlan', 'internet', 'şebeke', 'kapsama']):
            return "TechAgent"
        elif any(word in text_lower for word in ['fatura', 'ödeme', 'borç', 'ücret', 'fiyat']):
            return "BillingAgent"
        elif any(word in text_lower for word in ['paket', 'tarife', 'kampanya', 'gb', 'dakika']):
            return "PlanAgent"
        elif any(word in text_lower for word in ['nasıl', 'nedir', 'bilgi', 'öğren']):
            return "FAQAgent"
        
        # Continue with previous agent if no clear routing
        return previous_agent if previous_agent else "RouterAgent"
    
    def process_conversation(self, conv: Dict) -> List[Dict]:
        """Process a single conversation and generate all training examples"""
        
        examples = []
        context = []
        previous_agent = None
        
        customer_turns = conv.get('customer_turns_for_tts', [])
        
        for i, turn in enumerate(customer_turns):
            turn_num = i + 1
            customer_text = self._extract_customer_text(turn)
            
            if not customer_text:
                continue
            
            # Determine which agent handles this
            current_agent = self.determine_agent_flow(customer_text, turn_num, previous_agent)
            
            # Generate agent response
            agent_response = self.generate_agent_response(
                customer_text, 
                context, 
                current_agent,
                turn_num
            )
            
            # Create training example
            audio_file = f"data/tts_audio_final/{conv['conv_id']}_turn_{turn_num}.mp3"
            
            if Path(audio_file).exists():
                example = {
                    "conversation_id": conv['conv_id'],
                    "turn": turn_num,
                    "audio": audio_file,
                    "context": context.copy(),  # Previous context
                    "customer_text": customer_text,  # For reference
                    "agent_response": agent_response
                }
                examples.append(example)
            
            # Update context for next turn
            context.append({
                "type": "customer",
                "text": customer_text
            })
            context.append({
                "type": "agent",
                "agent": current_agent,
                "text": agent_response['response'],
                "tools": agent_response['tools']
            })
            
            # Add simulated tool results if tools were called
            for tool in agent_response['tools']:
                if tool == "verify_user":
                    context.append({
                        "type": "tool_result",
                        "tool": tool,
                        "result": {"verified": True, "customer_id": f"CUS{random.randint(100000, 999999)}"}
                    })
                elif tool == "check_esim_status":
                    context.append({
                        "type": "tool_result",
                        "tool": tool,
                        "result": {"status": "inactive", "error": "activation_pending"}
                    })
                elif tool == "route_to_agent":
                    # Update agent after routing
                    if current_agent == "RouterAgent":
                        # Route to appropriate agent based on issue
                        if "esim" in customer_text.lower() or "teknik" in customer_text.lower():
                            previous_agent = "TechAgent"
                        elif "fatura" in customer_text.lower():
                            previous_agent = "BillingAgent"
                        else:
                            previous_agent = "PlanAgent"
                    context.append({
                        "type": "tool_result",
                        "tool": tool,
                        "result": {"success": True, "routed_to": previous_agent}
                    })
                # Add other tool results as needed
            
            # Update previous agent
            if agent_response['tools'] and "route_to_agent" not in agent_response['tools']:
                previous_agent = current_agent
            
            # Rate limit protection
            time.sleep(0.1)
        
        return examples
    
    def generate_complete_dataset(self) -> List[Dict]:
        """Generate the complete training dataset"""
        
        print("🚀 GENERATING INTELLIGENT TRAINING DATASET")
        print("=" * 60)
        
        all_examples = []
        
        # Process conversations with progress bar
        for conv in tqdm(self.conversations, desc="Processing conversations"):
            examples = self.process_conversation(conv)
            all_examples.extend(examples)
            
            # Rate limit protection (10 requests per minute for free tier)
            if len(all_examples) % 10 == 0:
                time.sleep(6)  # Wait 6 seconds every 10 requests
        
        print(f"\n✅ Generated {len(all_examples)} training examples")
        
        # Analyze generated data
        self._analyze_dataset(all_examples)
        
        return all_examples
    
    def _analyze_dataset(self, examples: List[Dict]):
        """Analyze the generated dataset"""
        
        agents = {}
        tools = {}
        
        for ex in examples:
            agent = ex['agent_response']['agent']
            agents[agent] = agents.get(agent, 0) + 1
            
            for tool in ex['agent_response']['tools']:
                tools[tool] = tools.get(tool, 0) + 1
        
        print("\n📊 DATASET ANALYSIS:")
        print("-" * 40)
        print(f"Total examples: {len(examples)}")
        print("\n👥 Agent distribution:")
        for agent, count in agents.items():
            print(f"  {agent}: {count}")
        print("\n🔧 Tool usage:")
        for tool, count in sorted(tools.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {tool}: {count}")
    
    def save_dataset(self, examples: List[Dict]):
        """Save the dataset in training format"""
        
        output_dir = Path("data/winning_dataset")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Format for Gemma 3N training
        training_data = []
        for ex in examples:
            training_item = {
                "audio": ex['audio'],
                "context": json.dumps(ex['context'], ensure_ascii=False),
                "output": json.dumps({
                    "agent": ex['agent_response']['agent'],
                    "tools": ex['agent_response']['tools'],
                    "response": ex['agent_response']['response']
                }, ensure_ascii=False)
            }
            training_data.append(training_item)
        
        # Save as JSONL
        with open(output_dir / "gemma3n_audio_training.jsonl", 'w', encoding='utf-8') as f:
            for item in training_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        # Save complete data for debugging
        with open(output_dir / "complete_examples.json", 'w', encoding='utf-8') as f:
            json.dump(examples, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Saved to {output_dir}/")
        print(f"  - gemma3n_audio_training.jsonl (for training)")
        print(f"  - complete_examples.json (for debugging)")
        
        # Create a sample to show quality
        print("\n🎯 SAMPLE GENERATED RESPONSE:")
        if examples:
            sample = examples[min(5, len(examples)-1)]  # Get 5th example or last
            print(f"Customer: {sample['customer_text'][:100]}...")
            print(f"Agent: {sample['agent_response']['agent']}")
            print(f"Tools: {sample['agent_response']['tools']}")
            print(f"Response: {sample['agent_response']['response']}")

def main():
    """Generate the winning dataset"""
    
    print("🏆 WINNING DATASET GENERATOR FOR TEKNOFEST 2025")
    print("=" * 60)
    print("This time we generate NEW agent responses for every audio")
    print("No copying, no memorization - pure generation")
    print()
    
    generator = AudioResponseGenerator()
    
    # Generate complete dataset
    examples = generator.generate_complete_dataset()
    
    # Save everything
    generator.save_dataset(examples)
    
    print("\n" + "=" * 60)
    print("✅ DATASET GENERATION COMPLETE!")
    print("\n🎯 What makes this dataset WINNING:")
    print("  1. NEW agent responses generated for each audio")
    print("  2. Proper conversation flow with context")
    print("  3. Smart tool selection based on customer needs")
    print("  4. Agent handoffs that make sense")
    print("  5. No memorization - actual generation")
    print("\n🚀 READY TO WIN TEKNOFEST 2025!")

if __name__ == "__main__":
    main()
