#!/usr/bin/env python3
"""
STEP 1: GEMINI CONVERSATION GENERATOR FOR ELEVENLABS (FIXED)
Generates conversations with safety settings disabled
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
        # Configure model with disabled safety settings
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash',
            safety_settings={
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE'
            }
        )
        
        # Create organized directory structure
        self.base_dir = "data/pipeline"
        self.conversations_dir = os.path.join(self.base_dir, "01_gemini_conversations")
        self.elevenlabs_queue_dir = os.path.join(self.base_dir, "02_elevenlabs_queue")
        self.audio_output_dir = os.path.join(self.base_dir, "03_audio_output")
        
        for dir_path in [self.conversations_dir, self.elevenlabs_queue_dir, self.audio_output_dir]:
            os.makedirs(dir_path, exist_ok=True)
    
    def generate_conversation_prompt(self, scenario_type: str, complexity: str) -> str:
        """Generate prompt for multi-agent conversation"""
        
        prompt = """Türkçe telekom çağrı merkezi konuşması oluştur. JSON formatında olmalı.

SENARYO: {scenario_type}
KARMAŞIKLIK: {complexity}

JSON ÇIKTI:
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
      "text": "Merhaba, 3 gündür eSIM kuramıyorum, yardım eder misiniz?",
      "emotion": "frustrated",
      "voice_notes": {{
        "tone": "frustrated",
        "speed": "normal",
        "emphasis": ["3 gündür", "yardım"]
      }},
      "duration_estimate": 3.5
    }},
    {{
      "turn_id": "turn_002",
      "speaker": "agent",
      "agent_persona": "RouterAgent",
      "text": "Merhaba, yaşadığınız sorun için özür dilerim. Size yardımcı olacağım. Önce kimlik doğrulama yapmamız gerekiyor.",
      "emotion": "professional",
      "voice_notes": {{
        "tone": "calm_professional",
        "speed": "normal",
        "emphasis": ["özür dilerim", "yardımcı olacağım"]
      }},
      "tools_triggered": ["verify_user"],
      "duration_estimate": 4.0
    }},
    {{
      "turn_id": "turn_003",
      "speaker": "customer",
      "text": "Tamam, telefon numaram 0555 123 45 67",
      "emotion": "neutral",
      "voice_notes": {{
        "tone": "neutral",
        "speed": "normal",
        "emphasis": []
      }},
      "duration_estimate": 3.0
    }},
    {{
      "turn_id": "turn_004",
      "speaker": "agent",
      "agent_persona": "RouterAgent",
      "text": "Teşekkür ederim. Annenizin kızlık soyadını da alabilir miyim?",
      "emotion": "professional",
      "voice_notes": {{
        "tone": "professional",
        "speed": "normal",
        "emphasis": []
      }},
      "tools_triggered": [],
      "duration_estimate": 3.0
    }},
    {{
      "turn_id": "turn_005",
      "speaker": "customer",
      "text": "Yıldız, annemin kızlık soyadı Yıldız",
      "emotion": "neutral",
      "voice_notes": {{
        "tone": "neutral",
        "speed": "normal",
        "emphasis": ["Yıldız"]
      }},
      "duration_estimate": 2.5
    }},
    {{
      "turn_id": "turn_006",
      "speaker": "agent",
      "agent_persona": "RouterAgent",
      "text": "Doğrulama tamamlandı. eSIM aktivasyon sorununuz için sizi teknik desteğe yönlendiriyorum.",
      "emotion": "professional",
      "voice_notes": {{
        "tone": "professional",
        "speed": "normal",
        "emphasis": ["teknik desteğe"]
      }},
      "tools_triggered": ["verify_user"],
      "duration_estimate": 4.0
    }},
    {{
      "turn_id": "turn_007",
      "speaker": "agent",
      "agent_persona": "TechAgent",
      "text": "Merhaba, ben teknik destek uzmanı. eSIM aktivasyon sorununuzu çözeceğim. Cihazınızın IMEI numarasını alabilir miyim?",
      "emotion": "professional",
      "voice_notes": {{
        "tone": "professional",
        "speed": "normal",
        "emphasis": ["IMEI numarasını"]
      }},
      "tools_triggered": [],
      "duration_estimate": 4.5
    }},
    {{
      "turn_id": "turn_008",
      "speaker": "customer",
      "text": "IMEI mi? Bir saniye bakıyorum... 359111222333444",
      "emotion": "confused",
      "voice_notes": {{
        "tone": "confused",
        "speed": "slow",
        "emphasis": ["IMEI mi"]
      }},
      "duration_estimate": 4.0
    }},
    {{
      "turn_id": "turn_009",
      "speaker": "agent",
      "agent_persona": "TechAgent",
      "text": "Teşekkürler. Cihazınızı kontrol ediyorum. Cihazınız uyumlu görünüyor. Yeni bir aktivasyon kodu oluşturuyorum.",
      "emotion": "professional",
      "voice_notes": {{
        "tone": "professional",
        "speed": "normal",
        "emphasis": ["uyumlu", "yeni bir aktivasyon kodu"]
      }},
      "tools_triggered": ["check_device_registration", "reissue_activation_code"],
      "duration_estimate": 5.0
    }},
    {{
      "turn_id": "turn_010",
      "speaker": "customer",
      "text": "Tamam, teşekkür ederim. Umarım bu sefer çalışır.",
      "emotion": "hopeful",
      "voice_notes": {{
        "tone": "hopeful",
        "speed": "normal",
        "emphasis": ["bu sefer çalışır"]
      }},
      "duration_estimate": 3.0
    }}
  ],
  "agent_handoffs": [
    {{
      "at_turn": 6,
      "from": "RouterAgent",
      "to": "TechAgent",
      "reason": "technical_expertise_needed",
      "handoff_text": "Teknik desteğe yönlendiriyorum"
    }}
  ],
  "tool_calls": [
    {{
      "turn_id": "turn_006",
      "tool": "verify_user",
      "arguments": {{"msisdn": "05551234567", "maiden_name": "Yıldız"}},
      "result_affects_next_turn": true
    }},
    {{
      "turn_id": "turn_009",
      "tool": "check_device_registration",
      "arguments": {{"imei": "359111222333444"}},
      "result_affects_next_turn": true
    }},
    {{
      "turn_id": "turn_009",
      "tool": "reissue_activation_code",
      "arguments": {{"customer_id": "12345"}},
      "result_affects_next_turn": true
    }}
  ],
  "elevenlabs_config": {{
    "customer_voice": {{
      "voice_id": "to_be_assigned",
      "emotion_settings": {{
        "frustrated": {{"stability": 0.35, "similarity_boost": 0.75, "style": 0.7}},
        "neutral": {{"stability": 0.5, "similarity_boost": 0.75, "style": 0.5}},
        "confused": {{"stability": 0.4, "similarity_boost": 0.7, "style": 0.6}},
        "hopeful": {{"stability": 0.6, "similarity_boost": 0.8, "style": 0.4}}
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

Yukarıdaki formatta {complexity} seviyesinde bir konuşma oluştur. Sadece JSON döndür."""

        return prompt.format(
            scenario_type=scenario_type, 
            complexity=complexity, 
            timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
        )
    
    def generate_single_conversation(self, scenario_type: str, complexity: str, index: int) -> Dict:
        """Generate a single conversation"""
        
        prompt = self.generate_conversation_prompt(scenario_type, complexity)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.8,  # Slightly lower for more consistent JSON
                    top_p=0.9,
                    top_k=40,
                    max_output_tokens=4000,
                )
            )
            
            # Check if response was blocked
            if not response.parts:
                print(f"   ⚠️ Response blocked by safety filters. Retrying...")
                return None
            
            response_text = response.text
            
            # Try to extract JSON
            try:
                # Clean up response
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0]
                
                # Parse JSON
                conversation = json.loads(response_text.strip())
                
                # Add tracking IDs
                conversation["generation_id"] = str(uuid.uuid4())
                conversation["generated_at"] = datetime.now().isoformat()
                conversation["index"] = index
                
                print(f"   ✅ Generated: {conversation.get('conversation_id', f'conv_{index}')}")
                return conversation
                
            except json.JSONDecodeError as je:
                print(f"   ❌ JSON parsing error: {je}")
                # Try to fix common JSON issues
                try:
                    # Remove trailing commas
                    import re
                    response_text = re.sub(r',\s*}', '}', response_text)
                    response_text = re.sub(r',\s*]', ']', response_text)
                    conversation = json.loads(response_text)
                    
                    conversation["generation_id"] = str(uuid.uuid4())
                    conversation["generated_at"] = datetime.now().isoformat()
                    conversation["index"] = index
                    
                    print(f"   ✅ Fixed and generated: {conversation.get('conversation_id', f'conv_{index}')}")
                    return conversation
                except:
                    return None
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def create_elevenlabs_queue(self, conversation: Dict) -> List[Dict]:
        """Create ElevenLabs TTS queue from conversation"""
        
        queue = []
        conv_id = conversation.get("conversation_id", f"conv_{conversation.get('index', 0)}")
        
        # Available Turkish voices (you'll need to update with actual ElevenLabs voice IDs)
        turkish_voices = {
            "young_male": "21m00Tcm4TlvDq8ikWAM",
            "young_female": "AZnzlk1XvdvUeBnXmlld", 
            "elderly_female": "ThT5KcBeYPX3keUQqHPh",
            "business_male": "pMsXgVXv3BLzUgSXRplE",
            "agent_professional": "EXAVITQu4vr4xnSDxMaL"
        }
        
        # Assign voices based on persona
        customer_persona = conversation.get("customer_profile", {}).get("persona", "angry_young")
        customer_voice = {
            "angry_young": turkish_voices["young_male"],
            "confused_elderly": turkish_voices["elderly_female"],
            "business_professional": turkish_voices["business_male"],
            "frustrated_parent": turkish_voices["young_female"]
        }.get(customer_persona, turkish_voices["young_male"])
        
        for turn in conversation.get("dialogue_for_tts", []):
            queue_item = {
                "queue_id": f"{conv_id}_{turn['turn_id']}",
                "conversation_id": conv_id,
                "turn_id": turn["turn_id"],
                "speaker": turn["speaker"],
                "text": turn["text"],
                "voice_id": customer_voice if turn["speaker"] == "customer" else turkish_voices["agent_professional"],
                "emotion": turn.get("emotion", "neutral"),
                "voice_settings": self._get_voice_settings(turn.get("emotion", "neutral")),
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
            "neutral": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.5},
            "professional": {"stability": 0.75, "similarity_boost": 0.85, "style": 0.2},
            "confused": {"stability": 0.4, "similarity_boost": 0.7, "style": 0.6},
            "hopeful": {"stability": 0.6, "similarity_boost": 0.8, "style": 0.4}
        }
        
        return settings.get(emotion, settings["neutral"])
    
    def generate_dataset(self, num_conversations: int = 10):
        """Generate complete dataset with ElevenLabs queue"""
        
        print("🚀 GEMINI GENERATOR FOR ELEVENLABS (FIXED)")
        print("=" * 60)
        print(f"📊 Generating {num_conversations} conversations...")
        print("🔓 Safety settings: DISABLED")
        print("=" * 60)
        
        scenarios = [
            ("esim_activation", "simple"),
            ("esim_activation", "medium"),
            ("package_change", "simple"),
            ("package_change", "medium"),
            ("billing_issue", "medium"),
            ("device_problem", "simple"),
            ("multi_issue", "complex")
        ]
        
        all_conversations = []
        elevenlabs_master_queue = []
        
        for i in range(num_conversations):
            scenario_type, complexity = random.choice(scenarios)
            
            print(f"\n📍 [{i+1}/{num_conversations}] Generating: {scenario_type} ({complexity})")
            
            # Try up to 3 times if generation fails
            conversation = None
            for attempt in range(3):
                conversation = self.generate_single_conversation(scenario_type, complexity, i)
                if conversation:
                    break
                else:
                    print(f"   🔄 Retrying... (attempt {attempt+2}/3)")
            
            if conversation:
                # Save conversation
                conv_id = conversation.get("conversation_id", f"conv_{i:03d}")
                conv_file = os.path.join(self.conversations_dir, f"{conv_id}.json")
                with open(conv_file, "w", encoding="utf-8") as f:
                    json.dump(conversation, f, ensure_ascii=False, indent=2)
                
                # Create ElevenLabs queue
                queue_items = self.create_elevenlabs_queue(conversation)
                elevenlabs_master_queue.extend(queue_items)
                
                # Save individual queue file
                queue_file = os.path.join(self.elevenlabs_queue_dir, f"{conv_id}_queue.json")
                with open(queue_file, "w", encoding="utf-8") as f:
                    json.dump(queue_items, f, ensure_ascii=False, indent=2)
                
                all_conversations.append(conversation)
                
                dialogue_count = len(conversation.get("dialogue_for_tts", []))
                print(f"   ✅ Conversation: {dialogue_count} turns")
                print(f"   📝 Queue items: {len(queue_items)} audio files to generate")
            else:
                print(f"   ❌ Failed to generate after 3 attempts")
            
            # Rate limiting
            import time
            time.sleep(2)  # Increased delay
        
        # Create tracking file
        tracking = {
            "generated_at": datetime.now().isoformat(),
            "statistics": {
                "total_conversations": len(all_conversations),
                "total_audio_files_needed": len(elevenlabs_master_queue),
                "scenarios": {},
                "complexity_distribution": {}
            },
            "conversations": []
        }
        
        for conv in all_conversations:
            conv_id = conv.get("conversation_id", f"conv_{conv.get('index', 0)}")
            tracking["conversations"].append({
                "id": conv_id,
                "scenario": conv.get("metadata", {}).get("scenario", "unknown"),
                "turns": len(conv.get("dialogue_for_tts", [])),
                "file": f"01_gemini_conversations/{conv_id}.json",
                "queue": f"02_elevenlabs_queue/{conv_id}_queue.json"
            })
            
            # Count scenarios and complexity
            scenario = conv.get("metadata", {}).get("scenario", "unknown")
            complexity = conv.get("metadata", {}).get("complexity", "unknown")
            tracking["statistics"]["scenarios"][scenario] = tracking["statistics"]["scenarios"].get(scenario, 0) + 1
            tracking["statistics"]["complexity_distribution"][complexity] = tracking["statistics"]["complexity_distribution"].get(complexity, 0) + 1
        
        # Save tracking file
        tracking_file = os.path.join(self.base_dir, "tracking.json")
        with open(tracking_file, "w", encoding="utf-8") as f:
            json.dump(tracking, f, ensure_ascii=False, indent=2)
        
        # Save master queue
        if elevenlabs_master_queue:
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
        if elevenlabs_master_queue:
            print(f"📜 Master queue: {master_queue_file}")
        print("=" * 60)
        print("\n🎯 NEXT: Review conversations, then run ElevenLabs voice generation")
        
        return all_conversations, elevenlabs_master_queue

def main():
    """Main execution"""
    
    print("🔥 STEP 1: GEMINI CONVERSATION GENERATOR (FIXED)")
    print("📝 Creating trackable conversations for ElevenLabs TTS")
    print("🔓 Safety settings disabled for realistic conversations")
    print("")
    
    generator = GeminiGeneratorForElevenLabs()
    
    # Generate dataset
    conversations, queue = generator.generate_dataset(num_conversations=5)  # Start with 5 for testing
    
    # Show sample
    if conversations and len(conversations) > 0:
        print("\n📖 SAMPLE CONVERSATION:")
        print("=" * 60)
        sample = conversations[0]
        print(f"ID: {sample.get('conversation_id', 'unknown')}")
        print(f"Scenario: {sample.get('metadata', {}).get('scenario', 'unknown')}")
        print(f"Customer: {sample.get('customer_profile', {}).get('persona', 'unknown')}")
        
        # Show first 3 turns
        dialogue = sample.get("dialogue_for_tts", [])
        if dialogue:
            print(f"\nFirst {min(3, len(dialogue))} turns:")
            for turn in dialogue[:3]:
                speaker = turn.get("speaker", "unknown")
                text = turn.get("text", "")[:80]
                print(f"  [{speaker}]: {text}...")

if __name__ == "__main__":
    main()