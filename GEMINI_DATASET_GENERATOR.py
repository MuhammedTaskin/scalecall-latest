#!/usr/bin/env python3
"""
GEMINI 2.5 FLASH TURKISH TELCO DATASET GENERATOR
Generates realistic Turkish call center conversations with proper indexing for training
"""

import os
import json
import random
from typing import List, Dict, Any
from datetime import datetime
import google.generativeai as genai

# Configure Gemini
GOOGLE_API_KEY = "AIzaSyBzC3ydAP1qKkGyRkJ9t1sp5D3QN9QyzsQ"
genai.configure(api_key=GOOGLE_API_KEY)

class GeminiDatasetGenerator:
    """Generate Turkish telco conversations using Gemini 2.5 Flash"""
    
    def __init__(self):
        # Initialize Gemini 2.5 Flash
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.output_dir = "data/gemini_generated"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create structured directories for training
        self.conversations_dir = os.path.join(self.output_dir, "conversations")
        self.audio_mapping_dir = os.path.join(self.output_dir, "audio_mappings")
        os.makedirs(self.conversations_dir, exist_ok=True)
        os.makedirs(self.audio_mapping_dir, exist_ok=True)
        
    def generate_conversation_prompt(self, scenario_type: str, complexity: str) -> str:
        """Create detailed prompt for conversation generation"""
        
        base_prompt = """Sen Türkçe telekom çağrı merkezi diyalogları uzmanısın. Gerçekçi müşteri-temsilci konuşmaları oluştur.

SENARYO TİPİ: {scenario_type}
KARMAŞIKLIK: {complexity}

Aşağıdaki JSON formatında TAM BİR KONUŞMA oluştur. Her turn için audio dosyası oluşturulacağını düşünerek yapılandır:

{{
  "id": "benzersiz_id",
  "metadata": {{
    "type": "senaryo_tipi",
    "customer_persona": "müşteri_tipi",
    "duration_seconds": sayı,
    "resolution": "success/fail/escalation"
  }},
  "dialogue": [
    {{
      "turn_id": "turn_001",
      "turn": 1,
      "speaker": "customer",
      "text": "Türkçe konuşma metni",
      "emotion": "angry",
      "timestamp": 0.0,
      "audio_duration": 3.5,
      "tools_triggered": []
    }},
    {{
      "turn_id": "turn_002",
      "turn": 2,
      "speaker": "agent",
      "text": "Türkçe yanıt",
      "emotion": "professional",
      "timestamp": 3.5,
      "audio_duration": 4.2,
      "tools_triggered": ["verify_user"]
    }}
  ],
  "audio_plan": {{
    "customer_voice": "angry_young",
    "agent_voice": "professional",
    "total_duration": 120,
    "audio_files_count": 20
  }},
  "tools_sequence": ["verify_user", "check_device_registration", ...],
  "training_segments": [
    {{
      "segment_id": "seg_001",
      "customer_turns": [1, 3, 5],
      "agent_response_turn": 6,
      "tools_called": ["verify_user", "check_device"],
      "context": "esim_activation_problem"
    }}
  ],
  "interruption_points": [5, 12],
  "context_switches": [
    {{
      "at_turn": 8,
      "from": "technical",
      "to": "billing",
      "trigger": "customer_mention"
    }}
  ],
  "key_information": {{
    "phone_number": "0555 123 45 67",
    "maiden_name": "Yıldız",
    "imei": "359111222333444",
    "device": "iPhone 14",
    "issue": "esim_activation_failed",
    "package": "premium_10gb"
  }}
}}

KURALLAR:
1. Her turn_id benzersiz olmalı (turn_001, turn_002, ...)
2. audio_duration gerçekçi olmalı (1-10 saniye arası)
3. training_segments modelin öğreneceği bölümleri tanımlamalı
4. Müşteri duyguları değişmeli (angry→frustrated→relieved)
5. Araç çağrıları doğru turn'lerde olmalı

ÖRNEKLER:
- "Yav, 3 gündür uğraşıyorum bu eSIM'le!" (angry, 2.5 sn)
- "Anlıyorum efendim, hemen kontrol ediyorum." (professional, 3.0 sn)
- "Şey... IMEI mi dediniz? O ne?" (confused, 2.0 sn)

ŞİMDİ {scenario_type} İÇİN {complexity} SEVİYESİNDE KONUŞMA OLUŞTUR:"""

        return base_prompt.format(scenario_type=scenario_type, complexity=complexity)
    
    def generate_single_conversation(self, scenario_type: str, complexity: str, index: int) -> Dict:
        """Generate a single conversation using Gemini"""
        
        prompt = self.generate_conversation_prompt(scenario_type, complexity)
        
        try:
            # Generate with Gemini 2.5 Flash
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.9,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=3000,
                )
            )
            
            # Extract JSON from response
            response_text = response.text
            
            # Clean up response to get valid JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            # Parse JSON
            conversation = json.loads(response_text.strip())
            
            # Add unique ID if not present
            if "id" not in conversation or not conversation["id"]:
                conversation["id"] = f"{scenario_type}_{complexity}_{index:03d}"
            
            # Add audio file mapping for each turn
            for turn in conversation.get("dialogue", []):
                turn["audio_file"] = f"audio/{conversation['id']}/{turn.get('turn_id', f'turn_{turn['turn']:03d}')}.mp3"
                turn["text_file"] = f"text/{conversation['id']}/{turn.get('turn_id', f'turn_{turn['turn']:03d}')}.txt"
            
            print(f"✅ Generated: {conversation['id']}")
            return conversation
            
        except Exception as e:
            print(f"❌ Error generating conversation: {e}")
            return None
    
    def create_audio_mapping(self, conversation: Dict) -> Dict:
        """Create mapping file for audio generation"""
        
        mapping = {
            "conversation_id": conversation["id"],
            "metadata": conversation["metadata"],
            "audio_generation_plan": [],
            "training_data": []
        }
        
        # Create audio generation plan
        for turn in conversation.get("dialogue", []):
            audio_item = {
                "turn_id": turn.get("turn_id"),
                "speaker": turn["speaker"],
                "text": turn["text"],
                "emotion": turn["emotion"],
                "voice_profile": "customer_" + turn["emotion"] if turn["speaker"] == "customer" else "agent_professional",
                "audio_file": turn.get("audio_file"),
                "duration_estimate": turn.get("audio_duration", 3.0)
            }
            mapping["audio_generation_plan"].append(audio_item)
        
        # Create training data structure
        for segment in conversation.get("training_segments", []):
            training_item = {
                "segment_id": segment["segment_id"],
                "input_audio_files": [f"audio/{conversation['id']}/turn_{t:03d}.mp3" for t in segment.get("customer_turns", [])],
                "output": {
                    "agent_text": conversation["dialogue"][segment["agent_response_turn"]-1]["text"] if segment.get("agent_response_turn") else "",
                    "tools": segment.get("tools_called", []),
                    "context": segment.get("context")
                }
            }
            mapping["training_data"].append(training_item)
        
        return mapping
    
    def generate_dataset(self, num_conversations: int = 10):
        """Generate complete dataset with proper structure for training"""
        
        print("🚀 GEMINI 2.5 FLASH DATASET GENERATOR")
        print("=" * 60)
        print(f"📊 Generating {num_conversations} conversations...")
        print("=" * 60)
        
        # Scenario distribution
        scenarios = [
            # Simple (30%)
            ("balance_check", "simple"),
            ("status_inquiry", "simple"),
            ("basic_info", "simple"),
            
            # Medium (40%)
            ("esim_activation", "medium"),
            ("package_change", "medium"),
            ("billing_inquiry", "medium"),
            ("device_registration", "medium"),
            
            # Complex (20%)
            ("multi_issue", "complex"),
            ("escalation_needed", "complex"),
            
            # Chaos (10%)
            ("interruptions_chaos", "chaos"),
        ]
        
        conversations = []
        audio_mappings = []
        
        for i in range(num_conversations):
            # Select scenario based on distribution
            scenario_type, complexity = random.choice(scenarios)
            
            print(f"\n📍 Generating {i+1}/{num_conversations}: {scenario_type} ({complexity})")
            
            conversation = self.generate_single_conversation(scenario_type, complexity, i)
            
            if conversation:
                conversations.append(conversation)
                
                # Save individual conversation
                conv_file = os.path.join(self.conversations_dir, f"{conversation['id']}.json")
                with open(conv_file, "w", encoding="utf-8") as f:
                    json.dump(conversation, f, ensure_ascii=False, indent=2)
                
                # Create and save audio mapping
                audio_mapping = self.create_audio_mapping(conversation)
                audio_mappings.append(audio_mapping)
                
                mapping_file = os.path.join(self.audio_mapping_dir, f"{conversation['id']}_mapping.json")
                with open(mapping_file, "w", encoding="utf-8") as f:
                    json.dump(audio_mapping, f, ensure_ascii=False, indent=2)
            
            # Small delay to avoid rate limiting
            import time
            time.sleep(1)
        
        # Save complete dataset with all mappings
        dataset = {
            "generated_at": datetime.now().isoformat(),
            "total_conversations": len(conversations),
            "model": "gemini-2.5-flash",
            "structure": {
                "conversations_dir": self.conversations_dir,
                "audio_mapping_dir": self.audio_mapping_dir,
                "total_audio_files_needed": sum(len(c.get("dialogue", [])) for c in conversations),
                "total_training_segments": sum(len(c.get("training_segments", [])) for c in conversations)
            },
            "conversations": conversations,
            "audio_mappings": audio_mappings
        }
        
        dataset_file = os.path.join(self.output_dir, "turkish_telco_dataset.json")
        with open(dataset_file, "w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        
        # Create index file for easy access
        index = {
            "conversations": {c["id"]: f"conversations/{c['id']}.json" for c in conversations},
            "audio_mappings": {m["conversation_id"]: f"audio_mappings/{m['conversation_id']}_mapping.json" for m in audio_mappings},
            "stats": {
                "total_conversations": len(conversations),
                "total_turns": sum(len(c.get("dialogue", [])) for c in conversations),
                "scenarios": {}
            }
        }
        
        # Count scenarios
        for c in conversations:
            scenario = c.get("metadata", {}).get("type", "unknown")
            index["stats"]["scenarios"][scenario] = index["stats"]["scenarios"].get(scenario, 0) + 1
        
        index_file = os.path.join(self.output_dir, "dataset_index.json")
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 60)
        print(f"✅ DATASET GENERATION COMPLETE!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📊 Total conversations: {len(conversations)}")
        print(f"🎵 Total audio files needed: {index['stats']['total_turns']}")
        print(f"📄 Main dataset: {dataset_file}")
        print(f"📑 Index file: {index_file}")
        print("=" * 60)
        
        return conversations

def main():
    """Main execution"""
    
    print("🔥 STARTING GEMINI 2.5 FLASH DATASET GENERATION...")
    print("⚡ Using API Key: AIzaSy...zsQ")
    print("📝 This will create structured data for audio generation and training")
    print("")
    
    generator = GeminiDatasetGenerator()
    
    # Generate 10 conversations first (for testing)
    conversations = generator.generate_dataset(num_conversations=10)
    
    # Show sample conversation
    if conversations:
        print("\n📖 SAMPLE CONVERSATION STRUCTURE:")
        print("=" * 60)
        sample = conversations[0]
        print(f"ID: {sample['id']}")
        print(f"Type: {sample.get('metadata', {}).get('type')}")
        print(f"Customer: {sample.get('metadata', {}).get('customer_persona')}")
        print(f"Tools: {sample.get('tools_sequence', [])}")
        print(f"\nFirst 3 turns with audio mapping:")
        for turn in sample.get('dialogue', [])[:3]:
            print(f"  [{turn['speaker']}] Turn {turn['turn']}:")
            print(f"    Text: {turn['text'][:80]}...")
            print(f"    Audio: {turn.get('audio_file', 'N/A')}")
            print(f"    Emotion: {turn.get('emotion', 'N/A')}")

if __name__ == "__main__":
    main()
