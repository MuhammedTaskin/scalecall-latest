#!/usr/bin/env python3
"""
ELITE MULTI-AGENT TURKISH TELCO DATASET GENERATOR
Generates conversations with RouterAgent → Specialist handoffs
Aligned with the actual agent architecture
"""

import os
import json
import random
import uuid
from typing import List, Dict, Any
from datetime import datetime
import google.generativeai as genai

# Configure Gemini
GOOGLE_API_KEY = "AIzaSyBzC3ydAP1qKkGyRkJ9t1sp5D3QN9QyzsQ"
genai.configure(api_key=GOOGLE_API_KEY)

class EliteMultiAgentGenerator:
    """Generate multi-agent Turkish telco conversations"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.output_dir = "data/multi_agent_dataset"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Agent personas and their tools
        self.agents = {
            "RouterAgent": {
                "tools": ["verify_user", "get_user_info", "check_device_registration", 
                         "reissue_activation_code", "get_activation_steps", "get_activation_status",
                         "get_available_packages", "change_package", "create_support_ticket"],
                "handoffs": ["TechAgent", "PlanAgent", "BillingAgent", "FAQAgent"]
            },
            "TechAgent": {
                "tools": ["check_device_registration", "reissue_activation_code", 
                         "get_activation_steps", "get_activation_status", "create_support_ticket"],
                "focus": "device compatibility, eSIM activation, technical issues"
            },
            "PlanAgent": {
                "tools": ["get_available_packages", "change_package", "get_user_info", "create_support_ticket"],
                "focus": "data packages, pricing, plan changes"
            },
            "BillingAgent": {
                "tools": ["get_user_info", "create_support_ticket", "get_available_packages"],
                "focus": "payments, contracts, billing disputes"
            },
            "FAQAgent": {
                "tools": ["create_support_ticket", "get_available_packages"],
                "focus": "general information, common questions"
            }
        }
        
    def generate_conversation_prompt(self, scenario_type: str, complexity: str) -> str:
        """Create prompt for multi-agent conversation generation"""
        
        prompt = """Sen Turkish telco çağrı merkezi multi-agent sistem uzmanısın. 
RouterAgent ile başlayıp gerektiğinde specialist agent'lara handoff yapan gerçekçi konuşmalar oluştur.

SENARYO: {scenario_type}
KARMAŞIKLIK: {complexity}

AGENT SİSTEMİ:
1. RouterAgent - İlk karşılama, kimlik doğrulama, yönlendirme
2. TechAgent - Teknik sorunlar, eSIM aktivasyon, cihaz uyumluluk
3. PlanAgent - Paket değişiklikleri, fiyatlandırma
4. BillingAgent - Fatura, ödeme, sözleşme sorunları
5. FAQAgent - Genel bilgi, sık sorulan sorular

JSON FORMAT:
{{
  "conversation_id": "conv_{complexity}_{scenario_type}_001",
  "metadata": {{
    "scenario": "{scenario_type}",
    "complexity": "{complexity}",
    "customer_emotion_arc": ["frustrated", "angry", "relieved"],
    "resolution": "success/fail/escalation",
    "total_duration_seconds": 180
  }},
  "customer_profile": {{
    "persona": "angry_young/confused_elderly/business_professional",
    "phone": "0555XXXXXXX",
    "maiden_name": "Yıldız",
    "imei": "359111222333444",
    "current_package": "premium_10gb",
    "issue": "esim_activation_failed"
  }},
  "agent_flow": [
    {{
      "agent": "RouterAgent",
      "turns": [1, 2, 3],
      "tools_called": ["verify_user"],
      "handoff_to": "TechAgent",
      "handoff_reason": "technical_issue_detected"
    }},
    {{
      "agent": "TechAgent", 
      "turns": [4, 5, 6, 7],
      "tools_called": ["check_device_registration", "reissue_activation_code"],
      "handoff_to": null,
      "resolution": "issue_resolved"
    }}
  ],
  "dialogue": [
    {{
      "turn": 1,
      "speaker": "customer",
      "text": "Yav 3 gündür bu eSIM'i kuramıyorum, rezalet!",
      "emotion": "angry",
      "voice_profile": "angry_young",
      "timestamp": 0.0,
      "duration": 3.5
    }},
    {{
      "turn": 2,
      "speaker": "agent",
      "current_agent": "RouterAgent",
      "text": "Yaşadığınız sorun için özür dilerim. Önce kimlik doğrulama yapalım, telefon numaranız?",
      "emotion": "professional",
      "tools_triggered": ["verify_user"],
      "timestamp": 3.5,
      "duration": 4.0
    }},
    {{
      "turn": 3,
      "speaker": "customer",
      "text": "0555 123 45 67, anne kızlık soyadı Yıldız",
      "emotion": "frustrated",
      "voice_profile": "angry_young",
      "timestamp": 7.5,
      "duration": 3.0
    }},
    {{
      "turn": 4,
      "speaker": "agent",
      "current_agent": "RouterAgent",
      "text": "Doğrulama tamamlandı. Teknik konuda uzman arkadaşıma yönlendiriyorum.",
      "emotion": "professional",
      "handoff": {{"to": "TechAgent", "reason": "esim_activation_issue"}},
      "timestamp": 10.5,
      "duration": 3.5
    }},
    {{
      "turn": 5,
      "speaker": "agent",
      "current_agent": "TechAgent",
      "text": "Merhaba, ben teknik destek uzmanı. IMEI numaranızı kontrol edeyim.",
      "emotion": "professional",
      "tools_triggered": ["check_device_registration"],
      "timestamp": 14.0,
      "duration": 3.5
    }}
  ],
  "tool_calls": [
    {{
      "turn": 2,
      "agent": "RouterAgent",
      "tool": "verify_user",
      "arguments": {{"msisdn": "05551234567", "maiden_name": "Yıldız"}},
      "result": {{"success": true, "customer_id": "12345"}}
    }},
    {{
      "turn": 5,
      "agent": "TechAgent",
      "tool": "check_device_registration",
      "arguments": {{"imei": "359111222333444"}},
      "result": {{"registered": false, "compatible": true}}
    }}
  ],
  "training_segments": [
    {{
      "segment_id": "seg_001",
      "input": {{
        "customer_audio": "turns_1_3_5.mp3",
        "context": "esim_activation_failure"
      }},
      "output": {{
        "agent_response": "RouterAgent verifies then handoffs to TechAgent",
        "tools_sequence": ["verify_user", "check_device_registration", "reissue_activation_code"],
        "handoffs": [{{"from": "RouterAgent", "to": "TechAgent", "reason": "technical"}}]
      }}
    }}
  ],
  "interruptions": [
    {{
      "at_turn": 8,
      "type": "context_switch",
      "from_topic": "technical",
      "to_topic": "billing",
      "customer_text": "Bir dakika, faturamda da sorun var aslında..."
    }}
  ]
}}

KURALLAR:
1. RouterAgent MUTLAKA verify_user ile başlamalı
2. Handoff mantıklı olmalı (teknik→TechAgent, fatura→BillingAgent)
3. Her agent kendi tool'larını kullanmalı
4. Müşteri kesintileri ve konu değişiklikleri olmalı
5. Gerçekçi Türkçe (yav, valla, işte, şey kullan)
6. {complexity} seviyesine göre handoff sayısı:
   - simple: 0-1 handoff
   - medium: 1-2 handoff
   - complex: 2-3 handoff
   - chaos: 3+ handoff + kesintiler

SENARYOLAR:
- esim_activation: RouterAgent → TechAgent
- package_change: RouterAgent → PlanAgent
- billing_dispute: RouterAgent → BillingAgent
- multi_issue: RouterAgent → TechAgent → BillingAgent
- escalation: RouterAgent → TechAgent → create_support_ticket

ŞİMDİ {scenario_type} için {complexity} seviyesinde KONUŞMA OLUŞTUR:"""

        return prompt.format(scenario_type=scenario_type, complexity=complexity)
    
    def generate_single_conversation(self, scenario_type: str, complexity: str, index: int) -> Dict:
        """Generate a single multi-agent conversation"""
        
        prompt = self.generate_conversation_prompt(scenario_type, complexity)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.9,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=4000,
                )
            )
            
            response_text = response.text
            
            # Extract JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            conversation = json.loads(response_text.strip())
            
            # Ensure unique ID
            if "conversation_id" not in conversation:
                conversation["conversation_id"] = f"conv_{complexity}_{scenario_type}_{index:03d}"
            
            # Add audio file mappings for each turn
            for turn in conversation.get("dialogue", []):
                turn_id = f"turn_{turn['turn']:03d}"
                conv_id = conversation["conversation_id"]
                
                if turn["speaker"] == "customer":
                    turn["audio_file"] = f"audio/{conv_id}/customer_{turn_id}.mp3"
                    turn["voice_settings"] = self.get_voice_settings(turn.get("emotion", "neutral"))
                else:
                    turn["audio_file"] = f"audio/{conv_id}/agent_{turn_id}.mp3"
                    turn["tts_voice"] = "agent_professional"
            
            print(f"✅ Generated: {conversation['conversation_id']}")
            return conversation
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def get_voice_settings(self, emotion: str) -> Dict:
        """Get ElevenLabs voice settings for emotion"""
        
        settings = {
            "angry": {"stability": 0.25, "similarity_boost": 0.8, "style": 0.9},
            "frustrated": {"stability": 0.35, "similarity_boost": 0.75, "style": 0.7},
            "confused": {"stability": 0.8, "similarity_boost": 0.6, "style": 0.3},
            "neutral": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.5},
            "relieved": {"stability": 0.6, "similarity_boost": 0.8, "style": 0.4},
            "professional": {"stability": 0.75, "similarity_boost": 0.85, "style": 0.2}
        }
        
        return settings.get(emotion, settings["neutral"])
    
    def create_training_manifest(self, conversations: List[Dict]) -> Dict:
        """Create training manifest for Gemma 3N fine-tuning"""
        
        manifest = {
            "dataset_version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "model_architecture": "gemma-3n-multimodal",
            "training_config": {
                "input_type": "audio",
                "output_type": "text_and_tools",
                "personas": list(self.agents.keys()),
                "total_conversations": len(conversations),
                "features": {
                    "handoffs": True,
                    "multi_agent": True,
                    "tool_calling": True,
                    "emotion_detection": True,
                    "context_switching": True
                }
            },
            "training_examples": []
        }
        
        for conv in conversations:
            # Extract training examples from each conversation
            for segment in conv.get("training_segments", []):
                example = {
                    "id": f"{conv['conversation_id']}_{segment['segment_id']}",
                    "input": {
                        "audio_files": segment["input"].get("customer_audio"),
                        "context": segment["input"].get("context")
                    },
                    "expected_output": {
                        "agent_response": segment["output"].get("agent_response"),
                        "tools": segment["output"].get("tools_sequence", []),
                        "handoffs": segment["output"].get("handoffs", [])
                    }
                }
                manifest["training_examples"].append(example)
        
        return manifest
    
    def generate_dataset(self, num_conversations: int = 10):
        """Generate complete multi-agent dataset"""
        
        print("🚀 ELITE MULTI-AGENT DATASET GENERATOR")
        print("=" * 60)
        print(f"📊 Generating {num_conversations} multi-agent conversations...")
        print("🤖 Agents: RouterAgent, TechAgent, PlanAgent, BillingAgent, FAQAgent")
        print("=" * 60)
        
        # Scenario distribution aligned with agent specialties
        scenarios = [
            # Technical scenarios (30%) - TechAgent
            ("esim_activation_failed", "medium"),
            ("device_compatibility", "simple"),
            ("network_issues", "medium"),
            
            # Plan scenarios (25%) - PlanAgent
            ("package_upgrade", "medium"),
            ("data_limit_exceeded", "simple"),
            ("international_roaming", "complex"),
            
            # Billing scenarios (20%) - BillingAgent
            ("billing_dispute", "complex"),
            ("payment_failed", "medium"),
            ("contract_termination", "complex"),
            
            # Multi-issue scenarios (15%) - Multiple agents
            ("technical_and_billing", "complex"),
            ("full_escalation", "chaos"),
            
            # General scenarios (10%) - FAQAgent
            ("general_inquiry", "simple"),
            ("coverage_check", "simple")
        ]
        
        conversations = []
        
        for i in range(num_conversations):
            scenario_type, complexity = random.choice(scenarios)
            
            print(f"\n📍 Generating {i+1}/{num_conversations}: {scenario_type} ({complexity})")
            
            conversation = self.generate_single_conversation(scenario_type, complexity, i)
            
            if conversation:
                conversations.append(conversation)
                
                # Save individual conversation
                conv_file = os.path.join(self.output_dir, f"{conversation['conversation_id']}.json")
                with open(conv_file, "w", encoding="utf-8") as f:
                    json.dump(conversation, f, ensure_ascii=False, indent=2)
            
            # Avoid rate limiting
            import time
            time.sleep(1)
        
        # Create training manifest
        manifest = self.create_training_manifest(conversations)
        manifest_file = os.path.join(self.output_dir, "training_manifest.json")
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        
        # Create complete dataset
        dataset = {
            "generated_at": datetime.now().isoformat(),
            "generator": "gemini-2.5-flash",
            "architecture": "multi-agent-handoff",
            "statistics": {
                "total_conversations": len(conversations),
                "total_turns": sum(len(c.get("dialogue", [])) for c in conversations),
                "total_handoffs": sum(len(c.get("agent_flow", [])) - 1 for c in conversations),
                "total_tool_calls": sum(len(c.get("tool_calls", [])) for c in conversations),
                "agents_used": list(self.agents.keys())
            },
            "conversations": conversations
        }
        
        dataset_file = os.path.join(self.output_dir, "multi_agent_dataset.json")
        with open(dataset_file, "w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 60)
        print(f"✅ MULTI-AGENT DATASET COMPLETE!")
        print(f"📁 Output: {self.output_dir}")
        print(f"📊 Conversations: {len(conversations)}")
        print(f"🔄 Total handoffs: {dataset['statistics']['total_handoffs']}")
        print(f"🔧 Total tool calls: {dataset['statistics']['total_tool_calls']}")
        print(f"📄 Training manifest: {manifest_file}")
        print("=" * 60)
        
        # Show sample conversation flow
        if conversations:
            sample = conversations[0]
            print(f"\n📖 SAMPLE AGENT FLOW:")
            print(f"Scenario: {sample['metadata']['scenario']}")
            for flow in sample.get("agent_flow", []):
                print(f"  → {flow['agent']}: turns {flow['turns']}, tools: {flow.get('tools_called', [])}")
                if flow.get("handoff_to"):
                    print(f"    ↪ Handoff to {flow['handoff_to']}: {flow.get('handoff_reason')}")
        
        return conversations

def main():
    """Main execution"""
    
    print("🔥 STARTING ELITE MULTI-AGENT DATASET GENERATION...")
    print("⚡ This creates RouterAgent → Specialist handoff conversations")
    print("🎯 Aligned with actual agent architecture")
    print("")
    
    generator = EliteMultiAgentGenerator()
    
    # Generate dataset
    conversations = generator.generate_dataset(num_conversations=10)
    
    print("\n✨ Ready for ElevenLabs voice generation and Gemma 3N training!")

if __name__ == "__main__":
    main()