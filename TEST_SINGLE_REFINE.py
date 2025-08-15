#!/usr/bin/env python3
"""
Test refining a single conversation
"""

import json
from pathlib import Path
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key="AIzaSyBzC3ydAP1qKkGyRkJ9t1sp5D3QN9QyzsQ")

generation_config = {
    "temperature": 0.1,
    "top_p": 0.9,
    "top_k": 20,
    "max_output_tokens": 1000,
    "candidate_count": 1
}

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    generation_config=generation_config
)

# Load first conversation
with open('data/selected_for_tts.json', 'r') as f:
    selected = json.load(f)

first_conv_path = Path(selected['conversations'][0]['path'])
conv_id = selected['conversations'][0]['id']

print(f"📊 Testing with: {conv_id}")

with open(first_conv_path, 'r') as f:
    conv = json.load(f)

# Get first turn
customer_turns = conv.get('customer_turns_for_tts', [])
agent_responses = conv.get('agent_responses', [])

if customer_turns and agent_responses:
    # Get first customer turn
    customer_turn = customer_turns[0]
    if isinstance(customer_turn, dict):
        if len(customer_turn) == 1 and list(customer_turn.keys())[0].startswith('turn_'):
            turn_key = list(customer_turn.keys())[0]
            customer_turn = customer_turn[turn_key]
    
    customer_text = customer_turn.get('text', '')
    customer_emotion = customer_turn.get('emotion', 'normal')
    
    # Get first agent response
    agent_response = agent_responses[0]
    agent_text = agent_response.get('text', '')
    agent_name = agent_response.get('agent_persona', 'RouterAgent')
    tools = agent_response.get('tools_triggered', [])
    
    print(f"\n📢 Customer ({customer_emotion}):")
    print(f"   \"{customer_text[:100]}...\"")
    
    print(f"\n🤖 Current agent response:")
    print(f"   Agent: {agent_name}")
    print(f"   Text: \"{agent_text[:100]}...\"")
    print(f"   Tools: {tools}")
    
    # Check audio
    audio_file = f"data/tts_audio_final/{conv_id}_turn_1.mp3"
    print(f"\n🎵 Audio file: {audio_file}")
    print(f"   Exists: {Path(audio_file).exists()}")
    
    # Refine with Gemini
    prompt = f"""Refine this Turkish telco training data.

CUSTOMER SAYS (in audio):
"{customer_text}"
Emotion: {customer_emotion}

AGENT RESPONSE TO REFINE:
Agent: {agent_name}
Response: "{agent_text}"
Tools: {tools}

Generate a refined output in THIS EXACT FORMAT:
<agent>{agent_name}</agent>
<tools>verify_user(tc_no=12345678910, mother_maiden_name=AY)->{{verified:true, customer_id:CUS123456}}</tools>
<response>{agent_text}</response>

Add realistic tool parameters and results. Keep the response in Turkish."""

    print("\n📡 Calling Gemini to refine...")
    
    try:
        response = model.generate_content(prompt)
        refined = response.text.strip()
        
        print("\n✅ REFINED OUTPUT:")
        print(refined)
        
        # Create training pair
        training_pair = {
            "audio": audio_file,
            "text": refined
        }
        
        print("\n📄 TRAINING PAIR:")
        print(json.dumps(training_pair, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"\n❌ Error: {e}")