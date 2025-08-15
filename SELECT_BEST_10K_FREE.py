#!/usr/bin/env python3
"""
SELECT BEST 10K CHARACTERS FOR FREE TIER
Ultra strategic selection for maximum impact with minimal budget
"""

import os
import json
from typing import Dict, List
from collections import defaultdict

class FreeTierSelector:
    def __init__(self):
        self.char_limit = 10000  # FREE tier limit
        
        # Load previous selection
        with open("data/selected_for_tts.json", 'r') as f:
            self.full_selection = json.load(f)
    
    def select_critical_conversations(self):
        """Select only the most critical conversations for FREE tier"""
        
        print("🎯 SELECTING CRITICAL 10K FOR FREE TIER")
        print("="*70)
        
        # Strategy: Pick conversations that demonstrate:
        # 1. All 5 agents (at least 1 each)
        # 2. Handoffs (critical for multi-agent)
        # 3. Tool diversity
        # 4. Short but complete scenarios
        
        selected = []
        total_chars = 0
        
        # Coverage tracking
        covered_agents = set()
        covered_tools = set()
        has_handoff = False
        
        # Sort by score (already sorted in selected_for_tts.json)
        for conv_info in self.full_selection['conversations']:
            # Skip if over limit
            if total_chars + conv_info['chars'] > self.char_limit:
                continue
            
            # Load actual conversation to check features
            with open(conv_info['path'], 'r') as f:
                conv = json.load(f)
            
            # Extract features
            agents = set()
            tools = set()
            handoff = False
            
            for resp in conv.get('agent_responses', []):
                agent = resp.get('agent_persona', resp.get('agent', ''))
                if agent:
                    agents.add(agent)
                
                tool_list = resp.get('tools_triggered', resp.get('tools', []))
                for tool in tool_list:
                    if isinstance(tool, dict):
                        tools.add(tool.get('name', ''))
                    else:
                        tools.add(tool)
            
            if conv.get('agent_handoffs', []):
                handoff = True
            
            # Scoring logic for FREE tier
            priority_score = 0
            
            # New agent coverage is critical
            new_agents = agents - covered_agents
            if new_agents:
                priority_score += len(new_agents) * 100
            
            # Handoff is critical (but only need a few)
            if handoff and not has_handoff:
                priority_score += 200
            elif handoff and len(selected) < 3:  # Want 2-3 handoff examples
                priority_score += 50
            
            # New tools are valuable
            new_tools = tools - covered_tools
            priority_score += len(new_tools) * 10
            
            # Prefer shorter conversations for efficiency
            if conv_info['chars'] < 1500:
                priority_score += 30
            
            # Skip if doesn't add value
            if priority_score < 50 and len(selected) > 5:
                continue
            
            # Add to selection
            selected.append({
                **conv_info,
                "agents": list(agents),
                "tools": list(tools),
                "has_handoff": handoff,
                "priority": priority_score
            })
            
            total_chars += conv_info['chars']
            covered_agents.update(agents)
            covered_tools.update(tools)
            if handoff:
                has_handoff = True
            
            # Stop if close to limit
            if total_chars > self.char_limit * 0.95:
                break
        
        # Print results
        print(f"\n✅ FREE TIER SELECTION:")
        print(f"   Selected: {len(selected)} conversations")
        print(f"   Total chars: {total_chars:,} / {self.char_limit:,}")
        print(f"   Utilization: {100*total_chars/self.char_limit:.1f}%")
        
        print(f"\n📊 COVERAGE:")
        print(f"   Agents covered: {covered_agents}")
        print(f"   Unique tools: {len(covered_tools)}")
        print(f"   Has handoff examples: {has_handoff}")
        
        print(f"\n🎯 SELECTED CONVERSATIONS:")
        for i, conv in enumerate(selected, 1):
            print(f"   {i}. {conv['id'][:20]}... ({conv['chars']} chars)")
            print(f"      Agents: {', '.join(conv['agents'])}")
            if conv['has_handoff']:
                print(f"      ⭐ HAS HANDOFF")
        
        # Save selection
        with open("data/selected_for_free_tier.json", 'w') as f:
            json.dump({
                "metadata": {
                    "total_selected": len(selected),
                    "total_chars": total_chars,
                    "char_limit": self.char_limit,
                    "plan": "FREE_TIER"
                },
                "conversations": selected
            }, f, indent=2)
        
        print(f"\n💾 Saved to: data/selected_for_free_tier.json")
        
        return selected
    
    def generate_free_tts_script(self, selected):
        """Generate TTS script for FREE tier"""
        
        script = '''#!/usr/bin/env python3
"""
ElevenLabs FREE TIER TTS Generator
Maximum impact with 10k character limit
"""

import os
import json
import time
import requests

# You can get a FREE API key from ElevenLabs
ELEVENLABS_API_KEY = "YOUR_FREE_API_KEY_HERE"

class FreeTierTTS:
    def __init__(self):
        self.api_key = ELEVENLABS_API_KEY
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        # Load selection
        with open("data/selected_for_free_tier.json", 'r') as f:
            self.selection = json.load(f)
        
        # Use default voices (no cloning in free tier)
        self.voices = [
            "21m00Tcm4TlvDq8ikWAM",  # Adam
            "AZnzlk1XvdvUeBnXmlld",  # Domi
            "EXAVITQu4vr4xnSDxMaL",  # Bella
        ]
        
        self.output_dir = "data/tts_audio_free"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_all(self):
        """Generate TTS for critical conversations"""
        
        print(f"🎤 Generating TTS for {len(self.selection['conversations'])} critical conversations")
        print(f"   Using FREE tier: {self.selection['metadata']['total_chars']:,} / 10,000 chars")
        
        for i, conv_info in enumerate(self.selection['conversations']):
            print(f"\\n📢 Processing: {conv_info['id']}")
            print(f"   Agents: {', '.join(conv_info['agents'])}")
            
            # Load conversation
            with open(conv_info['path'], 'r') as f:
                conv = json.load(f)
            
            # Get voice (rotate through available)
            voice_id = self.voices[i % len(self.voices)]
            
            # Generate audio for each turn
            customer_turns = conv.get('customer_turns_for_tts', conv.get('customer_turns', []))
            for j, turn in enumerate(customer_turns):
                text = turn.get('text', '')
                if not text:
                    continue
                
                print(f"   Turn {j+1}: {len(text)} chars")
                
                # Generate audio
                audio = self.text_to_speech(text, voice_id)
                if audio:
                    filename = f"{self.output_dir}/{conv_info['id']}_turn_{j+1}.mp3"
                    with open(filename, 'wb') as f:
                        f.write(audio)
                    print(f"   ✓ Saved: {filename}")
                
                time.sleep(0.5)  # Rate limit for free tier
        
        print(f"\\n✅ FREE TIER TTS COMPLETE!")
        print(f"📁 Audio files in: {self.output_dir}")
    
    def text_to_speech(self, text: str, voice_id: str) -> bytes:
        """Generate TTS with free tier"""
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",  # Free tier model
            "language_code": "tr",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=30)
            if response.status_code == 200:
                return response.content
            else:
                print(f"   ⚠️ Error: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
        return None

if __name__ == "__main__":
    print("🚀 FREE TIER TTS GENERATOR")
    print("="*60)
    
    if ELEVENLABS_API_KEY == "YOUR_FREE_API_KEY_HERE":
        print("⚠️ Please add your FREE ElevenLabs API key!")
        print("1. Go to https://elevenlabs.io")
        print("2. Sign up for FREE account")
        print("3. Get your API key from settings")
        print("4. Replace YOUR_FREE_API_KEY_HERE in this script")
    else:
        generator = FreeTierTTS()
        generator.generate_all()
'''
        
        with open("GENERATE_TTS_FREE_TIER.py", 'w') as f:
            f.write(script)
        
        print(f"✅ FREE tier TTS script: GENERATE_TTS_FREE_TIER.py")

def main():
    selector = FreeTierSelector()
    selected = selector.select_critical_conversations()
    selector.generate_free_tts_script(selected)
    
    print("\n" + "="*70)
    print("🎯 FREE TIER STRATEGY COMPLETE!")
    print("   Maximum impact with ZERO budget")
    print("   Covers all agents and critical scenarios")
    print("\n📝 Next steps:")
    print("   1. Sign up for FREE ElevenLabs account")
    print("   2. Get your API key")
    print("   3. Run: python3 GENERATE_TTS_FREE_TIER.py")

if __name__ == "__main__":
    main()