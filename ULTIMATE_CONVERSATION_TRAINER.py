#!/usr/bin/env python3
"""
ULTIMATE CONVERSATION-BASED TRAINER FOR GEMMA 3N
This is THE training pipeline that will win TEKNOFEST 2025
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time

# ========================================
# CRITICAL CONFIGURATION
# ========================================

# These are the ONLY valid tools (21 total)
VALID_TOOLS = {
    "verify_user", "get_customer_status", "route_to_agent",
    "check_esim_status", "check_device_imei", "reissue_activation_code", "create_tech_ticket",
    "get_customer_plan", "list_all_plans", "change_customer_plan", "check_plan_compatibility",
    "get_last_bill", "get_unpaid_amount", "apply_campaign_discount", "create_payment_note",
    "search_faq", "get_common_solutions", "send_help_sms", "create_info_ticket",
    "escalate_to_human", "end_conversation"
}

# Valid agents
VALID_AGENTS = ["RouterAgent", "TechAgent", "BillingAgent", "PlanAgent", "FAQAgent"]

# Tool to agent mapping
TOOL_AGENT_MAP = {
    "verify_user": ["RouterAgent"],
    "get_customer_status": ["RouterAgent"],
    "route_to_agent": ["RouterAgent", "TechAgent", "BillingAgent", "PlanAgent", "FAQAgent"],
    "check_esim_status": ["TechAgent"],
    "check_device_imei": ["TechAgent"],
    "reissue_activation_code": ["TechAgent"],
    "create_tech_ticket": ["TechAgent"],
    "get_customer_plan": ["PlanAgent"],
    "list_all_plans": ["PlanAgent"],
    "change_customer_plan": ["PlanAgent"],
    "check_plan_compatibility": ["PlanAgent"],
    "get_last_bill": ["BillingAgent"],
    "get_unpaid_amount": ["BillingAgent"],
    "apply_campaign_discount": ["BillingAgent"],
    "create_payment_note": ["BillingAgent"],
    "search_faq": ["FAQAgent"],
    "get_common_solutions": ["FAQAgent"],
    "send_help_sms": ["FAQAgent"],
    "create_info_ticket": ["FAQAgent"],
    "escalate_to_human": VALID_AGENTS,
    "end_conversation": VALID_AGENTS
}

# Tool result templates (for realistic responses)
TOOL_RESULTS = {
    "verify_user": lambda: {"verified": True, "customer_id": f"CUS{random.randint(100000, 999999)}"},
    "get_customer_status": lambda: {"status": "active", "plan": "Genç Tarife 10GB", "balance": 0},
    "route_to_agent": lambda: {"success": True, "agent_assigned": random.choice(VALID_AGENTS)},
    "check_esim_status": lambda: {"status": random.choice(["inactive", "pending", "error"]), "attempts": random.randint(1, 5)},
    "check_device_imei": lambda: {"compatible": True, "model": "iPhone 14 Pro", "esim_capable": True},
    "reissue_activation_code": lambda: {"qr_code": f"QR{random.randint(100000, 999999)}", "sms_sent": True, "expires": "24h"},
    "create_tech_ticket": lambda: {"ticket_id": f"TT{random.randint(100000, 999999)}", "priority": "high"},
    "get_customer_plan": lambda: {"plan": "Genç Tarife 10GB", "data_remaining": "2.3GB", "renewal_date": "2025-09-01"},
    "list_all_plans": lambda: {"plans": [{"name": "Akademisyen 25GB", "price": 250}, {"name": "Unlimited", "price": 400}]},
    "change_customer_plan": lambda: {"success": True, "new_plan": "Akademisyen 25GB", "effective_date": "2025-08-15"},
    "check_plan_compatibility": lambda: {"compatible": True, "requirements_met": True},
    "get_last_bill": lambda: {"amount": 245.50, "due_date": "2025-08-20", "paid": False},
    "get_unpaid_amount": lambda: {"total": 245.50, "overdue": False},
    "apply_campaign_discount": lambda: {"success": True, "discount_amount": 50, "new_total": 195.50},
    "create_payment_note": lambda: {"note_id": f"PN{random.randint(100000, 999999)}", "recorded": True},
    "search_faq": lambda: {"results": ["eSIM Aktivasyon Rehberi", "Cihaz Uyumluluğu"], "found": True},
    "get_common_solutions": lambda: {"solutions": ["Cihazı yeniden başlatın", "Ayarları sıfırlayın"]},
    "send_help_sms": lambda: {"sent": True, "message_id": f"SMS{random.randint(100000, 999999)}"},
    "create_info_ticket": lambda: {"ticket_id": f"IT{random.randint(100000, 999999)}", "category": "general"},
    "escalate_to_human": lambda: {"queue_position": random.randint(1, 10), "estimated_wait": "3 dakika"},
    "end_conversation": lambda: {"conversation_logged": True, "satisfaction_survey_sent": True}
}

class ConversationTrainer:
    """The ultimate training data generator for Gemma 3N"""
    
    def __init__(self, api_key: str):
        """Initialize with Gemini API"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # DETERMINISTIC configuration for consistency
        self.generation_config = {
            "temperature": 0.1,  # Very low for deterministic output
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
            "candidate_count": 1
        }
        
    def load_conversations(self) -> List[Dict]:
        """Load all 76 selected conversations with audio mappings"""
        with open('data/selected_for_tts.json', 'r', encoding='utf-8') as f:
            selected = json.load(f)
        
        conversations = []
        for conv_info in selected['conversations']:
            conv_path = Path(conv_info['path'])
            if not conv_path.exists():
                continue
                
            with open(conv_path, 'r', encoding='utf-8') as f:
                conv_data = json.load(f)
            
            # Add audio file mappings
            conv_id = conv_info['id']
            conv_data['conv_id'] = conv_id
            conv_data['audio_files'] = []
            
            # Map audio files to customer turns
            for i, turn in enumerate(conv_data.get('customer_turns_for_tts', [])):
                audio_file = f"data/tts_audio_final/{conv_id}_turn_{i+1}.mp3"
                if Path(audio_file).exists():
                    conv_data['audio_files'].append({
                        "turn": i + 1,
                        "audio": audio_file,
                        "text": self._extract_turn_text(turn)
                    })
            
            conversations.append(conv_data)
        
        return conversations
    
    def _extract_turn_text(self, turn: Dict) -> str:
        """Extract text from potentially nested turn structure"""
        if isinstance(turn, dict):
            # Handle nested structure like {"turn_010": {...}}
            if len(turn) == 1 and list(turn.keys())[0].startswith('turn_'):
                turn_key = list(turn.keys())[0]
                turn = turn[turn_key]
            return turn.get('text', '')
        return ''
    
    def create_training_example(self, conversation: Dict, turn_index: int) -> Optional[Dict]:
        """
        Create a single training example from a conversation at a specific turn
        This is THE KEY function that creates the magic
        """
        
        audio_files = conversation.get('audio_files', [])
        agent_responses = conversation.get('agent_responses', [])
        
        if turn_index >= len(audio_files) or turn_index >= len(agent_responses):
            return None
        
        # Build conversation history (all previous turns as TEXT)
        history = []
        
        for i in range(turn_index):
            # Add customer turn (as transcribed text)
            if i < len(audio_files):
                history.append({
                    "turn": i * 2 + 1,
                    "type": "customer",
                    "text": audio_files[i]['text']
                })
            
            # Add agent response
            if i < len(agent_responses):
                agent_resp = agent_responses[i]
                agent = self._fix_agent_name(agent_resp.get('agent_persona', 'RouterAgent'))
                tools = self._fix_tool_names(agent_resp.get('tools_triggered', []))
                
                history.append({
                    "turn": i * 2 + 2,
                    "type": "agent",
                    "agent": agent,
                    "text": agent_resp.get('text', ''),
                    "tools": tools
                })
                
                # Add tool results (simulated)
                for tool in tools:
                    if tool in TOOL_RESULTS:
                        history.append({
                            "turn": i * 2 + 2.5,  # Sub-turn for tool result
                            "type": "tool_result",
                            "tool": tool,
                            "result": TOOL_RESULTS[tool]()
                        })
        
        # Current audio input (THIS is the only audio in the input)
        current_audio = audio_files[turn_index]['audio']
        
        # Expected output (what the model should generate)
        current_agent_response = agent_responses[turn_index]
        expected_agent = self._fix_agent_name(current_agent_response.get('agent_persona', 'RouterAgent'))
        expected_tools = self._fix_tool_names(current_agent_response.get('tools_triggered', []))
        expected_response = current_agent_response.get('text', '')
        
        return {
            "context": {
                "conversation_id": conversation.get('conv_id'),
                "turn_number": turn_index + 1,
                "history": history  # All previous turns as TEXT
            },
            "input": {
                "audio": current_audio  # ONLY current turn as audio
            },
            "output": {
                "agent": expected_agent,
                "tools": expected_tools,
                "response": expected_response
            }
        }
    
    def _fix_agent_name(self, agent: str) -> str:
        """Fix agent names to match valid set"""
        agent_map = {
            "TechnicalSupportAgent": "TechAgent",
            "TechnicalAgent": "TechAgent",
            "BillingSupport": "BillingAgent",
            "PlanSupport": "PlanAgent",
            "FAQSupport": "FAQAgent",
            "Router": "RouterAgent"
        }
        return agent_map.get(agent, agent if agent in VALID_AGENTS else "RouterAgent")
    
    def _fix_tool_names(self, tools: List) -> List[str]:
        """Fix and validate tool names"""
        valid_tools = []
        for tool in tools:
            if isinstance(tool, dict):
                tool = tool.get('name', tool.get('tool', ''))
            if tool in VALID_TOOLS:
                valid_tools.append(tool)
        return valid_tools
    
    def enhance_with_gemini(self, training_example: Dict) -> Dict:
        """
        Use Gemini to enhance the agent response with better context awareness
        This makes the responses more natural and context-aware
        """
        
        prompt = f"""You are enhancing a Turkish telco call center AI training dataset.

Given this conversation history and current input, improve the agent's response to be more natural and context-aware.

CONVERSATION HISTORY:
{json.dumps(training_example['context']['history'], ensure_ascii=False, indent=2)}

CURRENT CUSTOMER INPUT (audio transcription):
{training_example['input'].get('transcription', 'Audio file: ' + training_example['input']['audio'])}

CURRENT AGENT STATE:
- Agent: {training_example['output']['agent']}
- Tools to call: {training_example['output']['tools']}
- Original response: {training_example['output']['response']}

Generate an improved Turkish response that:
1. References the conversation history naturally
2. Uses the specified tools appropriately
3. Maintains the agent's persona
4. Is empathetic and professional
5. Is concise (max 2-3 sentences)

Return ONLY the improved response text in Turkish, nothing else."""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            improved_response = response.text.strip()
            if improved_response and len(improved_response) > 10:
                training_example['output']['response'] = improved_response
        except Exception as e:
            print(f"Gemini enhancement failed: {e}")
        
        return training_example
    
    def generate_complete_dataset(self, enhance_with_gemini: bool = True) -> List[Dict]:
        """
        Generate the complete training dataset for all conversations
        This is the MASTER function that creates everything
        """
        
        print("🚀 GENERATING ULTIMATE TRAINING DATASET")
        print("=" * 60)
        
        # Load all conversations
        conversations = self.load_conversations()
        print(f"📁 Loaded {len(conversations)} conversations")
        
        training_data = []
        
        # Process each conversation
        for conv in tqdm(conversations, desc="Processing conversations"):
            audio_files = conv.get('audio_files', [])
            agent_responses = conv.get('agent_responses', [])
            
            # Create training examples for each turn
            num_turns = min(len(audio_files), len(agent_responses))
            
            for turn_idx in range(num_turns):
                example = self.create_training_example(conv, turn_idx)
                
                if example:
                    # Optionally enhance with Gemini
                    if enhance_with_gemini and turn_idx % 3 == 0:  # Enhance every 3rd example
                        example = self.enhance_with_gemini(example)
                    
                    training_data.append(example)
        
        print(f"\n✅ Generated {len(training_data)} training examples")
        
        # Analyze the dataset
        self._analyze_dataset(training_data)
        
        return training_data
    
    def _analyze_dataset(self, training_data: List[Dict]):
        """Analyze and report on the generated dataset"""
        
        # Count agents
        agent_counts = {}
        for ex in training_data:
            agent = ex['output']['agent']
            agent_counts[agent] = agent_counts.get(agent, 0) + 1
        
        # Count tools
        tool_counts = {}
        for ex in training_data:
            for tool in ex['output']['tools']:
                tool_counts[tool] = tool_counts.get(tool, 0) + 1
        
        print("\n📊 DATASET ANALYSIS:")
        print("-" * 40)
        
        print("\n👥 Agent Distribution:")
        for agent, count in sorted(agent_counts.items()):
            print(f"   {agent}: {count} examples")
        
        print("\n🔧 Top 10 Tools Used:")
        for tool, count in sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {tool}: {count} times")
        
        # Check unused tools
        used_tools = set(tool_counts.keys())
        unused_tools = VALID_TOOLS - used_tools
        if unused_tools:
            print(f"\n⚠️ Unused tools: {unused_tools}")
    
    def save_dataset(self, training_data: List[Dict], output_dir: str = "data/ultimate_training"):
        """Save the training dataset in multiple formats"""
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Format 1: Complete JSON (for debugging)
        with open(output_path / "complete_training.json", 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        
        # Format 2: JSONL for training
        with open(output_path / "gemma3n_training.jsonl", 'w', encoding='utf-8') as f:
            for example in training_data:
                # Simplified format for actual training
                training_item = {
                    "audio": example['input']['audio'],
                    "context": json.dumps(example['context'], ensure_ascii=False),
                    "output": json.dumps(example['output'], ensure_ascii=False)
                }
                f.write(json.dumps(training_item, ensure_ascii=False) + '\n')
        
        # Format 3: Conversational format (alternative training style)
        with open(output_path / "conversational_training.jsonl", 'w', encoding='utf-8') as f:
            for example in training_data:
                # Create a conversational format
                conv_text = self._format_as_conversation(example)
                f.write(json.dumps({"text": conv_text}, ensure_ascii=False) + '\n')
        
        print(f"\n💾 Saved training data to {output_dir}/")
        print(f"   - complete_training.json (full debug data)")
        print(f"   - gemma3n_training.jsonl (for model training)")
        print(f"   - conversational_training.jsonl (alternative format)")
    
    def _format_as_conversation(self, example: Dict) -> str:
        """Format training example as a conversation string"""
        
        parts = []
        
        # Add context
        parts.append("[CONTEXT]")
        for item in example['context']['history'][-3:]:  # Last 3 turns for context
            if item['type'] == 'customer':
                parts.append(f"Customer: {item['text']}")
            elif item['type'] == 'agent':
                parts.append(f"{item['agent']}: {item['text']}")
                if item.get('tools'):
                    parts.append(f"[Tools: {', '.join(item['tools'])}]")
        
        # Add current input marker
        parts.append(f"\n[CURRENT AUDIO: {example['input']['audio']}]")
        
        # Add expected output
        parts.append(f"\n[GENERATE]")
        parts.append(f"Agent: {example['output']['agent']}")
        parts.append(f"Tools: {', '.join(example['output']['tools'])}")
        parts.append(f"Response: {example['output']['response']}")
        
        return '\n'.join(parts)

def main():
    """Create the ultimate training dataset"""
    
    print("🏆 ULTIMATE CONVERSATION-BASED TRAINER FOR TEKNOFEST 2025")
    print("=" * 60)
    
    # Use the API key
    API_KEY = "AIzaSyBzC3ydAP1qKkGyRkJ9t1sp5D3QN9QyzsQ"
    
    # Initialize trainer
    trainer = ConversationTrainer(API_KEY)
    
    # Generate complete dataset
    print("\n🎯 Starting dataset generation...")
    training_data = trainer.generate_complete_dataset(enhance_with_gemini=True)
    
    # Save in multiple formats
    trainer.save_dataset(training_data)
    
    print("\n" + "=" * 60)
    print("✅ DATASET GENERATION COMPLETE!")
    print("\n🎯 What we created:")
    print("   1. Full conversation context as text (memory efficient)")
    print("   2. Current input as audio (matches production)")
    print("   3. Expected output with agent, tools, and response")
    print("\n🚀 This dataset will train Gemma 3N to:")
    print("   - Understand conversation context")
    print("   - Process current audio input")
    print("   - Generate appropriate agent responses")
    print("   - Call the right tools at the right time")
    print("   - Handle handoffs and state transitions")
    print("\n🏆 READY FOR TEKNOFEST 2025!")

if __name__ == "__main__":
    main()