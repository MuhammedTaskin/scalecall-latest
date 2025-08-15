#!/usr/bin/env python3
"""
STEP 1: GEMINI CONVERSATION GENERATOR FOR ELEVENLABS
Generates conversations with perfect tracking for voice generation
Each turn is indexed for ElevenLabs processing
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

class GeminiGeneratorForElevenLabs:
    """Generate trackable conversations for ElevenLabs TTS"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Create organized directory structure
        self.base_dir = "data/pipeline"
        self.conversations_dir = os.path.join(self.base_dir, "01_gemini_conversations")
        self.elevenlabs_queue_dir = os.path.join(self.base_dir, "02_elevenlabs_queue")
        self.audio_output_dir = os.path.join(self.base_dir, "03_audio_output")
        
        for dir_path in [self.conversations_dir, self.elevenlabs_queue_dir, self.audio_output_dir]:
            os.makedirs(dir_path, exist_ok=True)
    
    def generate_conversation_prompt(self, scenario_type: str, complexity: str) -> str:
        """Generate prompt for multi-agent conversation"""
        
        prompt = """Türkçe telekom çağrı merkezi konuşması oluştur. Multi-agent sistem: RouterAgent başlar, gerekirse specialist'e handoff yapar.

SENARYO: {scenario_type}
KARMAŞIKLIK: {complexity}

ÇIKTI FORMATI (ElevenLabs için optimize edilmiş):
{{
  "conversation_id": "conv_{timestamp}_{scenario_type}",
  "metadata": {{
    "scenario": "{scenario_type}",
    "complexity": "{complexity}",
    "customer_emotion_arc": ["frustrated", "angry", "relieved"],
    "agent_flow": ["RouterAgent", "TechAgent"],
    "total_turns": 10
  }},
  "customer_profile": {{
    "persona": "angry_young",
    "phone": "0555 123 45 67",
    "maiden_name": "Yıldız",
    "issue": "eSIM aktivasyon sorunu"
  }},
  "dialogue_for_tts": [
    {{
      "turn_id": "turn_001",
      "speaker": "customer",
      "text": "Alo? 3 gündür bu eSIM'i kuramıyorum yav, yeter artık!",
      "emotion": "angry",
      "voice_notes": {{
        "tone": "frustrated_angry",
        "speed": "fast",
        "emphasis": ["3 gündür", "yeter artık"]
      }},
      "duration_estimate": 3.5
    }},
    {{
      "turn_id": "turn_002", 
      "speaker": "agent",
      "agent_persona": "RouterAgent",
      "text": "Yaşadığınız sorun için çok özür dilerim. Hemen yardımcı olacağım, önce kimlik doğrulama yapalım.",
      "emotion": "professional_empathetic",
      "voice_notes": {{
        "tone": "calm_professional",
        "speed": "normal",
        "emphasis": ["çok özür dilerim", "hemen"]
      }},
      "tools_triggered": ["verify_user"],
      "duration_estimate": 4.0
    }},
    {{
      "turn_id": "turn_003",
      "speaker": "customer",
      "text": "Tamam, 0555 123 45 67, annemin kızlık soyadı... şey... Yıldız.",
      "emotion": "frustrated",
      "voice_notes": {{
        "tone": "frustrated_hesitant",
        "speed": "normal",
        "pause_after": ["soyadı...", "şey..."]
      }},
      "duration_estimate": 4.5
    }}
  ],
  "agent_handoffs": [
    {{
      "at_turn": 6,
      "from": "RouterAgent",
      "to": "TechAgent",
      "reason": "technical_expertise_needed",
      "handoff_text": "Teknik konuda uzman arkadaşıma aktarıyorum, o daha iyi yardımcı olacak."
    }}
  ],
  "tool_calls": [
    {{
      "turn_id": "turn_002",
      "tool": "verify_user",
      "arguments": {{"msisdn": "05551234567", "maiden_name": "Yıldız"}},
      "result_affects_next_turn": true
    }},
    {{
      "turn_id": "turn_008",
      "tool": "check_device_registration",
      "arguments": {{"imei": "359111222333444"}},
      "result_affects_next_turn": true
    }}
  ],
  "elevenlabs_config": {{
    "customer_voice": {{
      "voice_id": "to_be_assigned",
      "emotion_settings": {{
        "angry": {{"stability": 0.25, "similarity_boost": 0.8, "style": 0.9}},
        "frustrated": {{"stability": 0.35, "similarity_boost": 0.75, "style": 0.7}},
        "relieved": {{"stability": 0.6, "similarity_boost": 0.8, "style": 0.4}}
      }}
    }},
    "agent_voice": {{
      "voice_id": "to_be_assigned",
      "emotion_settings": {{
        "professional": {{"stability": 0.75, "similarity_boost": 0.85, "style": 0.2}}
      }}
    }}
  }}
}}

KURALLAR:
1. Her turn_id benzersiz olmalı (turn_001, turn_002...)
2. voice_notes içinde ton, hız, vurgu bilgileri olmalı
3. Doğal Türkçe: "yav", "ya", "valla", "işte", "şey" kullan
4. Kesintiler için pause_after kullan
5. Tool çağrıları mantıklı sırada olmalı
6. Handoff'lar scenario'ya uygun olmalı

{complexity} SEVİYESİ İÇİN:
- simple: 5-8 turn, 0-1 handoff
- medium: 8-12 turn, 1-2 handoff  
- complex: 12-20 turn, 2-3 handoff
- chaos: 20+ turn, 3+ handoff, kesintiler

ŞİMDİ {scenario_type} İÇİN {complexity} SEVİYESİNDE TAM KONUŞMA OLUŞTUR:"""

        return prompt.format(scenario_type=scenario_type, complexity=complexity, 
                            timestamp=datetime.now().strftime("%Y%m%d_%H%M%S"))
    
    def generate_single_conversation(self, scenario_type: str, complexity: str, index: int) -> Dict:
        """Generate a single conversation"""
        
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
            
            # Add tracking IDs
            conversation["generation_id"] = str(uuid.uuid4())
            conversation["generated_at"] = datetime.now().isoformat()
            conversation["index"] = index
            
            print(f"✅ Generated: {conversation['conversation_id']}")
            return conversation
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def create_elevenlabs_queue(self, conversation: Dict) -> List[Dict]:
        """Create ElevenLabs TTS queue from conversation"""
        
        queue = []
        conv_id = conversation["conversation_id"]
        
        # Available Turkish voices (you'll need to update with actual ElevenLabs voice IDs)
        turkish_voices = {
            "young_male": "21m00Tcm4TlvDq8ikWAM",
            "young_female": "AZnzlk1XvdvUeBnXmlld", 
            "elderly_female": "ThT5KcBeYPX3keUQqHPh",
            "business_male": "pMsXgVXv3BLzUgSXRplE",
            "agent_professional": "EXAVITQu4vr4xnSDxMaL"
        }
        
        # Assign voices based on persona
        customer_persona = conversation["customer_profile"]["persona"]
        customer_voice = {
            "angry_young": turkish_voices["young_male"],
            "confused_elderly": turkish_voices["elderly_female"],
            "business_professional": turkish_voices["business_male"],
            "frustrated_parent": turkish_voices["young_female"]
        }.get(customer_persona, turkish_voices["young_male"])
        
        for turn in conversation["dialogue_for_tts"]:
            queue_item = {
                "queue_id": f"{conv_id}_{turn['turn_id']}",
                "conversation_id": conv_id,
                "turn_id": turn["turn_id"],
                "speaker": turn["speaker"],
                "text": turn["text"],
                "voice_id": customer_voice if turn["speaker"] == "customer" else turkish_voices["agent_professional"],
                "emotion": turn["emotion"],
                "voice_settings": self._get_voice_settings(turn["emotion"]),
                "output_path": f"{self.audio_output_dir}/{conv_id}/{turn['turn_id']}.mp3",
                "status": "pending",
                "created_at": datetime.now().isoformat()
            }
            
            # Add voice notes for better TTS
            if "voice_notes" in turn:
                queue_item["voice_notes"] = turn["voice_notes"]
            
            queue.append(queue_item)
        
        return queue
    
    def _get_voice_settings(self, emotion: str) -> Dict:
        """Get ElevenLabs voice settings for emotion"""
        
        settings = {
            "angry": {"stability": 0.25, "similarity_boost": 0.8, "style": 0.9},
            "frustrated": {"stability": 0.35, "similarity_boost": 0.75, "style": 0.7},
            "frustrated_hesitant": {"stability": 0.4, "similarity_boost": 0.7, "style": 0.6},
            "professional_empathetic": {"stability": 0.7, "similarity_boost": 0.85, "style": 0.3},
            "professional": {"stability": 0.75, "similarity_boost": 0.85, "style": 0.2},
            "relieved": {"stability": 0.6, "similarity_boost": 0.8, "style": 0.4},
            "confused": {"stability": 0.8, "similarity_boost": 0.6, "style": 0.3}
        }
        
        return settings.get(emotion, {"stability": 0.5, "similarity_boost": 0.75, "style": 0.5})
    
    def generate_dataset(self, num_conversations: int = 10):
        """Generate complete dataset with ElevenLabs queue"""
        
        print("🚀 GEMINI GENERATOR FOR ELEVENLABS")
        print("=" * 60)
        print(f"📊 Generating {num_conversations} conversations...")
        print("=" * 60)
        
        scenarios = [
            ("esim_activation", "medium"),
            ("package_change", "medium"),
            ("billing_issue", "complex"),
            ("device_problem", "simple"),
            ("multi_issue", "complex"),
            ("escalation", "chaos")
        ]
        
        all_conversations = []
        elevenlabs_master_queue = []
        
        for i in range(num_conversations):
            scenario_type, complexity = random.choice(scenarios)
            
            print(f"\n📍 [{i+1}/{num_conversations}] Generating: {scenario_type} ({complexity})")
            
            # Generate conversation
            conversation = self.generate_single_conversation(scenario_type, complexity, i)
            
            if conversation:
                # Save conversation
                conv_file = os.path.join(self.conversations_dir, f"{conversation['conversation_id']}.json")
                with open(conv_file, "w", encoding="utf-8") as f:
                    json.dump(conversation, f, ensure_ascii=False, indent=2)
                
                # Create ElevenLabs queue
                queue_items = self.create_elevenlabs_queue(conversation)
                elevenlabs_master_queue.extend(queue_items)
                
                # Save individual queue file
                queue_file = os.path.join(self.elevenlabs_queue_dir, f"{conversation['conversation_id']}_queue.json")
                with open(queue_file, "w", encoding="utf-8") as f:
                    json.dump(queue_items, f, ensure_ascii=False, indent=2)
                
                all_conversations.append(conversation)
                
                print(f"   ✅ Conversation: {len(conversation['dialogue_for_tts'])} turns")
                print(f"   📝 Queue items: {len(queue_items)} audio files to generate")
            
            # Rate limiting
            import time
            time.sleep(1)
        
        # Create master tracking file
        tracking = {
            "generated_at": datetime.now().isoformat(),
            "statistics": {
                "total_conversations": len(all_conversations),
                "total_audio_files_needed": len(elevenlabs_master_queue),
                "scenarios": {},
                "complexity_distribution": {}
            },
            "conversations": [
                {
                    "id": c["conversation_id"],
                    "scenario": c["metadata"]["scenario"],
                    "turns": len(c["dialogue_for_tts"]),
                    "file": f"01_gemini_conversations/{c['conversation_id']}.json",
                    "queue": f"02_elevenlabs_queue/{c['conversation_id']}_queue.json"
                }
                for c in all_conversations
            ],
            "elevenlabs_queue_summary": {
                "total_items": len(elevenlabs_master_queue),
                "pending": len(elevenlabs_master_queue),
                "completed": 0,
                "failed": 0
            }
        }
        
        # Count scenarios and complexity
        for conv in all_conversations:
            scenario = conv["metadata"]["scenario"]
            complexity = conv["metadata"]["complexity"]
            tracking["statistics"]["scenarios"][scenario] = tracking["statistics"]["scenarios"].get(scenario, 0) + 1
            tracking["statistics"]["complexity_distribution"][complexity] = tracking["statistics"]["complexity_distribution"].get(complexity, 0) + 1
        
        # Save tracking file
        tracking_file = os.path.join(self.base_dir, "tracking.json")
        with open(tracking_file, "w", encoding="utf-8") as f:
            json.dump(tracking, f, ensure_ascii=False, indent=2)
        
        # Save master queue
        master_queue_file = os.path.join(self.elevenlabs_queue_dir, "MASTER_QUEUE.json")
        with open(master_queue_file, "w", encoding="utf-8") as f:
            json.dump({
                "created_at": datetime.now().isoformat(),
                "total_items": len(elevenlabs_master_queue),
                "items": elevenlabs_master_queue
            }, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 60)
        print("✅ GENERATION COMPLETE!")
        print(f"📁 Base directory: {self.base_dir}")
        print(f"📊 Conversations: {len(all_conversations)}")
        print(f"🎵 Audio files to generate: {len(elevenlabs_master_queue)}")
        print(f"📋 Tracking file: {tracking_file}")
        print(f"📜 Master queue: {master_queue_file}")
        print("=" * 60)
        print("\n🎯 NEXT STEP: Run step2_elevenlabs_voice_generator.py")
        
        return all_conversations, elevenlabs_master_queue

def main():
    """Main execution"""
    
    print("🔥 STEP 1: GEMINI CONVERSATION GENERATOR")
    print("📝 Creating trackable conversations for ElevenLabs TTS")
    print("")
    
    generator = GeminiGeneratorForElevenLabs()
    
    # Generate dataset
    conversations, queue = generator.generate_dataset(num_conversations=5)  # Start with 5 for testing
    
    # Show sample queue item
    if queue:
        print("\n📖 SAMPLE ELEVENLABS QUEUE ITEM:")
        print("=" * 60)
        sample = queue[0]
        for key, value in sample.items():
            if key != "text":
                print(f"{key}: {value}")
            else:
                print(f"text: {value[:80]}...")

if __name__ == "__main__":
    main()