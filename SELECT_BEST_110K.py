#!/usr/bin/env python3
"""
SELECT BEST 110K CHARACTERS
Strategic selection for maximum coverage within ElevenLabs limit
"""

import os
import json
from typing import Dict, List, Tuple
from collections import defaultdict

class BestConversationSelector:
    def __init__(self, char_limit: int = 110000):
        self.char_limit = char_limit
        self.selected = []
        self.total_chars = 0
        
        # Priority scoring weights
        self.priorities = {
            # Dataset priorities (higher = more important)
            "flash_heavy_dataset": 10,  # Rich, detailed, dialects
            "smart_flash_dataset": 8,   # Proper tool usage
            "correct_flash_dataset": 7, # Good handoffs
            "varied_dataset": 9,        # Complex multi-agent
            "quick_varied_dataset": 6,  # Edge cases (but less since we deleted many)
            "gemini_generated": 5,       # Older, less structured
            "flash_lite_dataset": 4,    # Simple
            "generated": 3,              # Unknown quality
        }
        
        # Coverage requirements
        self.required_coverage = {
            "tools": set(),
            "agents": set(),
            "handoff_patterns": set(),
            "scenarios": set(),
            "emotions": set(),
            "complexity_levels": set()
        }
    
    def analyze_conversation(self, conv_path: str) -> Dict:
        """Analyze a conversation for selection criteria"""
        
        try:
            with open(conv_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            return None
        
        # Handle list format (some files have multiple conversations)
        if isinstance(data, list):
            if len(data) == 0:
                return None
            conv = data[0]  # Take first conversation
        else:
            conv = data
        
        # Calculate character count
        char_count = 0
        customer_turns = conv.get('customer_turns_for_tts', conv.get('customer_turns', []))
        for turn in customer_turns:
            char_count += len(turn.get('text', ''))
        
        if char_count == 0:
            return None
        
        # Extract features for scoring
        features = {
            "path": conv_path,
            "id": conv.get('id', conv.get('conversation_id', 'unknown')),
            "chars": char_count,
            "turns": len(customer_turns),
            "tools": [],
            "agents": [],
            "has_handoff": False,
            "emotion_variety": set(),
            "scenario": None,
            "complexity": "medium",
            "dataset": self.get_dataset_name(conv_path)
        }
        
        # Extract tools
        for resp in conv.get('agent_responses', []):
            tools = resp.get('tools_triggered', resp.get('tools', []))
            # Handle both string and dict formats
            for tool in tools:
                if isinstance(tool, dict):
                    tool_name = tool.get('name', '')
                else:
                    tool_name = tool
                if tool_name:
                    features["tools"].append(tool_name)
            
            # Extract agents
            agent = resp.get('agent_persona', resp.get('agent', ''))
            if agent:
                features["agents"].append(agent)
        
        # Check handoffs
        if conv.get('agent_handoffs', []):
            features["has_handoff"] = True
        
        # Extract emotions
        for turn in customer_turns:
            emotion = turn.get('emotion', 'normal')
            features["emotion_variety"].add(emotion)
        
        # Scenario and complexity
        features["scenario"] = conv.get('scenario', conv.get('primary_issue', 'general'))
        features["complexity"] = conv.get('complexity', 'medium')
        
        return features
    
    def get_dataset_name(self, path: str) -> str:
        """Extract dataset name from path"""
        parts = path.split('/')
        for i, part in enumerate(parts):
            if part == 'data' and i + 1 < len(parts):
                return parts[i + 1]
        return "unknown"
    
    def calculate_score(self, features: Dict) -> float:
        """Calculate priority score for a conversation"""
        
        score = 0
        
        # Dataset priority
        dataset_priority = self.priorities.get(features["dataset"], 1)
        score += dataset_priority * 10
        
        # Tool diversity bonus
        unique_tools = set(features["tools"]) if features["tools"] else set()
        score += len(unique_tools) * 5
        
        # Agent diversity bonus
        unique_agents = set(features["agents"])
        score += len(unique_agents) * 8
        
        # Handoff bonus
        if features["has_handoff"]:
            score += 15
        
        # Emotion variety bonus
        score += len(features["emotion_variety"]) * 3
        
        # Complexity bonus
        if features["complexity"] == "complex":
            score += 20
        elif features["complexity"] == "urgent" or features["complexity"] == "critical":
            score += 25
        
        # Efficiency penalty (prefer shorter for same content)
        chars_per_turn = features["chars"] / max(features["turns"], 1)
        if chars_per_turn > 150:  # Long-winded
            score -= 5
        
        return score
    
    def select_best_conversations(self):
        """Select best conversations within char limit"""
        
        print("🎯 SELECTING BEST CONVERSATIONS FOR 110K LIMIT")
        print("="*70)
        
        # Analyze all conversations
        all_conversations = []
        
        for root, dirs, files in os.walk("data"):
            # Skip test and audio directories
            if "test" in root or "audio" in root or "tts" in root:
                continue
                
            for file in files:
                if file.endswith('.json'):
                    features = self.analyze_conversation(os.path.join(root, file))
                    if features and features["chars"] > 0:
                        features["score"] = self.calculate_score(features)
                        all_conversations.append(features)
        
        print(f"📊 Found {len(all_conversations)} valid conversations")
        
        # Sort by score (highest first)
        all_conversations.sort(key=lambda x: x["score"], reverse=True)
        
        # Select conversations
        selected = []
        total_chars = 0
        
        # Coverage tracking
        covered_tools = set()
        covered_agents = set()
        covered_scenarios = set()
        covered_emotions = set()
        dataset_counts = defaultdict(int)
        
        for conv in all_conversations:
            # Check if we can fit this conversation
            if total_chars + conv["chars"] > self.char_limit:
                continue
            
            # Add to selected
            selected.append(conv)
            total_chars += conv["chars"]
            
            # Update coverage
            if conv["tools"]:
                covered_tools.update(conv["tools"])
            if conv["agents"]:
                covered_agents.update(conv["agents"])
            covered_scenarios.add(conv["scenario"])
            covered_emotions.update(conv["emotion_variety"])
            dataset_counts[conv["dataset"]] += 1
            
            # Stop if we're close to limit
            if total_chars > self.char_limit * 0.95:
                break
        
        # Print results
        print(f"\n✅ SELECTION COMPLETE!")
        print(f"   Selected: {len(selected)} conversations")
        print(f"   Total chars: {total_chars:,} / {self.char_limit:,}")
        print(f"   Utilization: {100*total_chars/self.char_limit:.1f}%")
        
        print(f"\n📈 DATASET DISTRIBUTION:")
        for dataset, count in sorted(dataset_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {dataset}: {count}")
        
        print(f"\n🔧 COVERAGE:")
        print(f"   Unique tools: {len(covered_tools)}")
        print(f"   Unique agents: {len(covered_agents)}")
        print(f"   Scenarios: {len(covered_scenarios)}")
        print(f"   Emotions: {len(covered_emotions)}")
        
        # Save selection
        selection_file = "data/selected_for_tts.json"
        with open(selection_file, 'w') as f:
            json.dump({
                "metadata": {
                    "total_selected": len(selected),
                    "total_chars": total_chars,
                    "char_limit": self.char_limit
                },
                "conversations": [
                    {
                        "path": s["path"],
                        "id": s["id"],
                        "chars": s["chars"],
                        "score": s["score"],
                        "dataset": s["dataset"]
                    }
                    for s in selected
                ]
            }, f, indent=2)
        
        print(f"\n💾 Selection saved to: {selection_file}")
        
        return selected
    
    def generate_tts_script(self, selected: List[Dict]):
        """Generate ElevenLabs TTS script for selected conversations"""
        
        script = '''#!/usr/bin/env python3
"""
ElevenLabs TTS for Selected Best Conversations
Auto-generated to stay within 110k character limit
"""

import os
import json
import time
import requests
from datetime import datetime

ELEVENLABS_API_KEY = "sk_61bdd16dbc21a3820bfdb0601dc18db053a04ea7a8d77462"

class SelectedTTSGenerator:
    def __init__(self):
        self.api_key = ELEVENLABS_API_KEY
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        # Load selection
        with open("data/selected_for_tts.json", 'r') as f:
            self.selection = json.load(f)
        
        # 37 voices for variety
        self.voices = [
            "pNInz6obpgDQGcFmaJgB", "VR6AewLTigWG4xSOukaG", "yoZ06aMxZJJ28mfd3POQ",
            "21m00Tcm4TlvDq8ikWAM", "MF3mGyEYCl7XYWbV9V6O", "XB0fDUnXU5powFXDhCwa",
            # Add more voice IDs as needed
        ]
        
        self.output_dir = "data/tts_audio_final"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_all(self):
        """Generate TTS for all selected conversations"""
        
        print(f"🎤 Generating TTS for {len(self.selection['conversations'])} conversations")
        print(f"   Total characters: {self.selection['metadata']['total_chars']:,}")
        
        for i, conv_info in enumerate(self.selection['conversations']):
            # Load conversation
            with open(conv_info['path'], 'r') as f:
                conv = json.load(f)
            
            # Get voice (consistent per conversation)
            voice_id = self.voices[hash(conv_info['id']) % len(self.voices)]
            
            # Generate audio for each turn
            customer_turns = conv.get('customer_turns_for_tts', conv.get('customer_turns', []))
            for j, turn in enumerate(customer_turns):
                text = turn.get('text', '')
                if not text:
                    continue
                
                # Generate audio
                audio = self.text_to_speech(text, voice_id, turn.get('emotion', 'normal'))
                if audio:
                    filename = f"{self.output_dir}/{conv_info['id']}_turn_{j+1}.mp3"
                    with open(filename, 'wb') as f:
                        f.write(audio)
                
                time.sleep(0.3)  # Rate limit
            
            if (i + 1) % 10 == 0:
                print(f"   Progress: {i+1}/{len(self.selection['conversations'])}")
        
        print(f"✅ TTS generation complete!")
        print(f"📁 Audio files in: {self.output_dir}")
    
    def text_to_speech(self, text: str, voice_id: str, emotion: str) -> bytes:
        """Generate TTS with Flash v2.5"""
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        data = {
            "text": text,
            "model_id": "eleven_flash_v2_5",
            "language_code": "tr",
            "voice_settings": {
                "stability": 0.7 if emotion == "normal" else 0.4,
                "similarity_boost": 0.75,
                "use_speaker_boost": True
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=30)
            if response.status_code == 200:
                return response.content
        except:
            pass
        return None

if __name__ == "__main__":
    generator = SelectedTTSGenerator()
    generator.generate_all()
'''
        
        with open("GENERATE_TTS_SELECTED.py", 'w') as f:
            f.write(script)
        
        print(f"✅ TTS script generated: GENERATE_TTS_SELECTED.py")

def main():
    selector = BestConversationSelector(char_limit=110000)
    selected = selector.select_best_conversations()
    selector.generate_tts_script(selected)
    
    print("\n🎯 NEXT STEPS:")
    print("1. Run: python3 GENERATE_TTS_SELECTED.py")
    print("2. This will generate audio for best conversations")
    print("3. Stays within your 110k Creator plan limit!")

if __name__ == "__main__":
    main()