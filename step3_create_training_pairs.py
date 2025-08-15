#!/usr/bin/env python3
"""
STEP 3: CREATE TRAINING PAIRS FOR GEMMA 3N
Combines Gemini conversations + ElevenLabs audio into training data
"""

import os
import json
from typing import List, Dict, Any
from datetime import datetime

class TrainingPairCreator:
    """Create training pairs from conversations and audio"""
    
    def __init__(self):
        self.base_dir = "data/pipeline"
        self.conversations_dir = os.path.join(self.base_dir, "01_gemini_conversations")
        self.audio_dir = os.path.join(self.base_dir, "03_audio_output")
        self.training_dir = os.path.join(self.base_dir, "04_training_pairs")
        os.makedirs(self.training_dir, exist_ok=True)
    
    def create_training_pairs(self, conversation: Dict) -> List[Dict]:
        """
        Create training pairs from a conversation
        
        LOGIC:
        - Input: Customer audio + current persona + history
        - Output: Agent response + tools + handoff (if any)
        """
        
        training_pairs = []
        conv_id = conversation["conversation_id"]
        dialogue = conversation["dialogue_for_tts"]
        
        # Track conversation history
        history = []
        current_persona = "RouterAgent"  # Always starts with RouterAgent
        
        for i in range(len(dialogue)):
            turn = dialogue[i]
            
            # Only create pairs for customer → agent interactions
            if turn["speaker"] == "customer":
                # Look for the next agent response
                if i + 1 < len(dialogue) and dialogue[i + 1]["speaker"] == "agent":
                    agent_turn = dialogue[i + 1]
                    
                    # Create training pair
                    training_pair = {
                        "pair_id": f"{conv_id}_pair_{i//2:03d}",
                        "conversation_id": conv_id,
                        
                        # INPUT (what model receives)
                        "input": {
                            # Customer audio file
                            "audio_file": f"{self.audio_dir}/{conv_id}/{turn['turn_id']}.mp3",
                            
                            # Current agent persona (system prompt indicator)
                            "current_persona": agent_turn.get("agent_persona", current_persona),
                            
                            # Conversation history (for context)
                            "history": history.copy(),
                            
                            # Customer emotion (from voice)
                            "customer_emotion": turn.get("emotion", "neutral"),
                            
                            # Turn number (for tracking)
                            "turn_number": i
                        },
                        
                        # OUTPUT (what model should produce)
                        "output": {
                            # Agent's text response
                            "response_text": agent_turn["text"],
                            
                            # Tools to call
                            "tools_to_call": agent_turn.get("tools_triggered", []),
                            
                            # Handoff decision (if any)
                            "handoff": None,
                            
                            # Response emotion
                            "response_emotion": agent_turn.get("emotion", "professional")
                        },
                        
                        # METADATA (for evaluation)
                        "metadata": {
                            "scenario": conversation["metadata"]["scenario"],
                            "complexity": conversation["metadata"]["complexity"],
                            "customer_issue": conversation["customer_profile"]["issue"]
                        }
                    }
                    
                    # Check for handoff in agent flow
                    for handoff in conversation.get("agent_handoffs", []):
                        if handoff["at_turn"] == i + 1:
                            training_pair["output"]["handoff"] = {
                                "to_persona": handoff["to"],
                                "reason": handoff["reason"]
                            }
                            # Update current persona for next turns
                            current_persona = handoff["to"]
                            break
                    
                    training_pairs.append(training_pair)
                    
                    # Add to history
                    history.append({
                        "speaker": "customer",
                        "text": turn["text"],
                        "emotion": turn.get("emotion")
                    })
                    history.append({
                        "speaker": "agent",
                        "text": agent_turn["text"],
                        "persona": agent_turn.get("agent_persona", current_persona),
                        "tools": agent_turn.get("tools_triggered", [])
                    })
        
        return training_pairs
    
    def create_multimodal_format(self, training_pair: Dict) -> Dict:
        """
        Convert to Gemma 3N multimodal training format
        """
        
        return {
            "id": training_pair["pair_id"],
            
            # Multimodal input
            "messages": [
                {
                    "role": "system",
                    "content": self._get_system_prompt(training_pair["input"]["current_persona"])
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "audio",
                            "audio": training_pair["input"]["audio_file"]
                        },
                        {
                            "type": "text",
                            "text": f"History: {json.dumps(training_pair['input']['history'], ensure_ascii=False)}"
                        }
                    ]
                },
                {
                    "role": "assistant",
                    "content": self._format_assistant_response(training_pair["output"])
                }
            ]
        }
    
    def _get_system_prompt(self, persona: str) -> str:
        """Get system prompt for persona"""
        
        prompts = {
            "RouterAgent": "You are RouterAgent. Verify users and route to specialists.",
            "TechAgent": "You are TechAgent. Handle technical issues and eSIM activation.",
            "PlanAgent": "You are PlanAgent. Handle package changes and pricing.",
            "BillingAgent": "You are BillingAgent. Handle payments and billing issues.",
            "FAQAgent": "You are FAQAgent. Answer general questions."
        }
        
        return prompts.get(persona, prompts["RouterAgent"])
    
    def _format_assistant_response(self, output: Dict) -> str:
        """Format assistant response with tools and handoff"""
        
        response = output["response_text"]
        
        # Add tool calls
        if output["tools_to_call"]:
            for tool in output["tools_to_call"]:
                response += f'\n{{"tool_call": {{"name": "{tool}"}}}}'
        
        # Add handoff
        if output["handoff"]:
            response += f'\n{{"handoff": {{"persona": "{output["handoff"]["to_persona"]}"}}}}'
        
        return response
    
    def process_all_conversations(self):
        """Process all conversations to create training pairs"""
        
        print("🚀 CREATING TRAINING PAIRS")
        print("=" * 60)
        
        # Load tracking file
        tracking_file = os.path.join(self.base_dir, "tracking.json")
        with open(tracking_file, "r", encoding="utf-8") as f:
            tracking = json.load(f)
        
        all_training_pairs = []
        all_multimodal_pairs = []
        
        # Process each conversation
        for conv_info in tracking["conversations"]:
            conv_file = os.path.join(self.base_dir, conv_info["file"])
            
            print(f"\n📍 Processing: {conv_info['id']}")
            
            # Load conversation
            with open(conv_file, "r", encoding="utf-8") as f:
                conversation = json.load(f)
            
            # Create training pairs
            training_pairs = self.create_training_pairs(conversation)
            all_training_pairs.extend(training_pairs)
            
            # Convert to multimodal format
            for pair in training_pairs:
                multimodal_pair = self.create_multimodal_format(pair)
                all_multimodal_pairs.append(multimodal_pair)
            
            print(f"   ✅ Created {len(training_pairs)} training pairs")
        
        # Save training pairs
        training_file = os.path.join(self.training_dir, "training_pairs.json")
        with open(training_file, "w", encoding="utf-8") as f:
            json.dump({
                "created_at": datetime.now().isoformat(),
                "total_pairs": len(all_training_pairs),
                "pairs": all_training_pairs
            }, f, ensure_ascii=False, indent=2)
        
        # Save multimodal format
        multimodal_file = os.path.join(self.training_dir, "gemma3n_training_data.json")
        with open(multimodal_file, "w", encoding="utf-8") as f:
            json.dump({
                "created_at": datetime.now().isoformat(),
                "model": "gemma-3n-multimodal",
                "total_examples": len(all_multimodal_pairs),
                "examples": all_multimodal_pairs
            }, f, ensure_ascii=False, indent=2)
        
        # Create summary
        summary = {
            "total_training_pairs": len(all_training_pairs),
            "personas_used": {},
            "tools_used": {},
            "handoffs": 0
        }
        
        for pair in all_training_pairs:
            # Count personas
            persona = pair["input"]["current_persona"]
            summary["personas_used"][persona] = summary["personas_used"].get(persona, 0) + 1
            
            # Count tools
            for tool in pair["output"]["tools_to_call"]:
                summary["tools_used"][tool] = summary["tools_used"].get(tool, 0) + 1
            
            # Count handoffs
            if pair["output"]["handoff"]:
                summary["handoffs"] += 1
        
        print("\n" + "=" * 60)
        print("✅ TRAINING PAIRS CREATED!")
        print(f"📊 Total pairs: {summary['total_training_pairs']}")
        print(f"🤖 Personas: {list(summary['personas_used'].keys())}")
        print(f"🔧 Tools: {list(summary['tools_used'].keys())}")
        print(f"🔄 Handoffs: {summary['handoffs']}")
        print(f"📄 Training file: {training_file}")
        print(f"📄 Multimodal file: {multimodal_file}")
        print("=" * 60)
        
        return all_training_pairs

def main():
    """Main execution"""
    
    print("🔥 STEP 3: CREATE TRAINING PAIRS")
    print("📝 Combining conversations + audio into training data")
    print("")
    
    creator = TrainingPairCreator()
    
    # Process all conversations
    training_pairs = creator.process_all_conversations()
    
    # Show sample pair
    if training_pairs:
        print("\n📖 SAMPLE TRAINING PAIR:")
        print("=" * 60)
        sample = training_pairs[0]
        print("INPUT:")
        print(f"  Audio: {sample['input']['audio_file']}")
        print(f"  Persona: {sample['input']['current_persona']}")
        print(f"  Emotion: {sample['input']['customer_emotion']}")
        print("\nOUTPUT:")
        print(f"  Response: {sample['output']['response_text'][:100]}...")
        print(f"  Tools: {sample['output']['tools_to_call']}")
        print(f"  Handoff: {sample['output']['handoff']}")

if __name__ == "__main__":
    main()