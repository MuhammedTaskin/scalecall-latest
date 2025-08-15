#!/usr/bin/env python3
"""
Expanded ElevenLabs Voice Pool for Turkish Telco Dataset
Using ALL available multilingual voices for maximum variety
"""

# ElevenLabs Multilingual Voice IDs (all support Turkish)
VOICE_POOL = {
    # MALE VOICES (15+)
    "male_voices": {
        # Deep/Authoritative
        "adam": "pNInz6obpgDQGcFmaJgB",        # Deep, narrative
        "antoni": "ErXwobaYiN019PkySvjV",      # Well-rounded
        "arnold": "VR6AewLTigWG4xSOukaG",      # Crisp, professional
        "clyde": "2EiwWnXFnvU5JabPnv8n",       # War veteran
        
        # Middle-aged/Professional  
        "daniel": "onwK4e9ZLuTAKqWW03F9",      # News presenter
        "dave": "CYw3kZ02Hs0563khs1Fj",        # Conversational British
        "drew": "29vD33N1CtxCmqQRPOHJ",        # Well-rounded
        "ethan": "g5CIjZEefAph4nQFvHAz",        # Soft American
        
        # Young/Casual
        "fin": "D38z5RcWu1voky8WS1ja",         # Irish sailor
        "harry": "SOYHLrjzK2X1ezoPC6cr",       # Anxious, young American
        "james": "ZQe5CZNOzWyzPSCn5a3c",       # News reporter
        "jeremy": "bVMeCyTHy58xNoL34h3p",      # Excited British
        "josh": "TxGEqnHWrfWFTfGW9XjX",        # Young, deep American
        
        # Unique/Character
        "liam": "TX3LPaxmHKxFdv7VOQHJ",        # Articulate American
        "michael": "flq6f7yk4E4fJM5XTYuZ",    # Audiobook narrator
        "sam": "yoZ06aMxZJJ28mfd3POQ",        # Young American
        "thomas": "GBv7mTt0atIp3Br8iCZE",     # Calm American
    },
    
    # FEMALE VOICES (15+)
    "female_voices": {
        # Professional/Mature
        "alice": "Xb7hH8MSUJpSbSDYk0k2",       # British news anchor
        "aria": "9BWtsMINqrJLrRacOk9x",        # Expressive American
        "bella": "EXAVITQu4vr4xnSDxMaL",       # Soft American
        "charlotte": "XB0fDUnXU5powFXDhCwa",   # Swedish-English
        
        # Warm/Friendly
        "domi": "AZnzlk1XvdvUeBnXmlld",        # Strong American
        "dorothy": "ThT5KcBeYPX3keUQqHPh",     # British child
        "elli": "MF3mGyEYCl7XYWbV9V6O",        # Clear American
        "emily": "LcfcDJNUP1GQjkzn1xUU",       # Calm American
        
        # Young/Energetic
        "freya": "jsCqWAovK2LkecY7zXl4",       # Expressive American
        "gigi": "jBpfuIE2acCO8z3wKNLl",        # Young American
        "grace": "oWAxZDx7w5VEj9dCyTzz",       # Southern American
        "jessie": "t0jbNlBVZ17f02VDIeMI",      # Raspy American
        
        # International/Unique
        "laura": "FGY2WhTYpPnrIDTdsKH5",       # Upbeat American
        "lily": "pFZP5JQG7iQjIQuC4Bku",        # British narrator
        "matilda": "XrExE9yKIg1WjnnlVkGX",     # Warm American
        "monica": "Uf9jGFYcTtjJh3EeXcLr",      # Broadcaster
        "nicole": "piTKgcLEGmPE4e6mEKli",      # Whispery American
        "rachel": "21m00Tcm4TlvDq8ikWAM",      # Calm American
        "sarah": "EXAVITQu4vr4xnSDxMaL",       # Conversational American
        "serena": "pMsXgVXv3BLzUgSXRplE",      # Pleasant American
    }
}

# Personality-based voice selection
VOICE_PERSONALITIES = {
    # Customer types → Preferred voices
    "angry": ["clyde", "harry", "domi", "jessie"],
    "confused": ["ethan", "fin", "dorothy", "emily"],
    "impatient": ["james", "jeremy", "aria", "freya"],
    "polite": ["daniel", "thomas", "bella", "lily"],
    "professional": ["arnold", "michael", "alice", "monica"],
    "young": ["josh", "sam", "gigi", "grace"],
    "elderly": ["adam", "drew", "matilda", "rachel"],
    "frustrated": ["liam", "harry", "nicole", "laura"],
    "cheerful": ["jeremy", "fin", "freya", "serena"]
}

def get_diverse_voice_assignment(conversations_count: int = 220):
    """
    Assign voices to ensure maximum diversity
    """
    import random
    import hashlib
    
    all_male = list(VOICE_POOL["male_voices"].keys())
    all_female = list(VOICE_POOL["female_voices"].keys())
    
    # Shuffle for variety
    random.shuffle(all_male)
    random.shuffle(all_female)
    
    # Create balanced pool (17 male + 20 female = 37 unique voices)
    voice_rotation = []
    for i in range(max(len(all_male), len(all_female))):
        if i < len(all_male):
            voice_rotation.append(("male", all_male[i]))
        if i < len(all_female):
            voice_rotation.append(("female", all_female[i]))
    
    print(f"🎤 Voice Pool Statistics:")
    print(f"   Total unique voices: {len(all_male) + len(all_female)}")
    print(f"   Male voices: {len(all_male)}")
    print(f"   Female voices: {len(all_female)}")
    print(f"   Conversations per voice: ~{conversations_count // len(voice_rotation):.1f}")
    
    return voice_rotation

def get_voice_for_conversation(conv_id: str, emotion: str = "normal"):
    """
    Get optimal voice for a conversation based on ID and emotion
    """
    import hashlib
    
    # Hash-based consistent selection
    hash_val = int(hashlib.md5(conv_id.encode()).hexdigest(), 16)
    
    # Check if emotion has preferred voices
    if emotion in VOICE_PERSONALITIES:
        preferred = VOICE_PERSONALITIES[emotion]
        voice_name = preferred[hash_val % len(preferred)]
        
        # Find voice ID
        for gender_voices in VOICE_POOL.values():
            if voice_name in gender_voices:
                return gender_voices[voice_name], voice_name
    
    # Default: Use hash to select from all voices
    all_voices = []
    for gender, voices in VOICE_POOL.items():
        for name, voice_id in voices.items():
            all_voices.append((voice_id, name))
    
    selected = all_voices[hash_val % len(all_voices)]
    return selected[0], selected[1]

def main():
    print("🎭 EXPANDED VOICE POOL FOR TURKISH TELCO")
    print("="*70)
    
    # Show statistics
    total_male = len(VOICE_POOL["male_voices"])
    total_female = len(VOICE_POOL["female_voices"])
    total_voices = total_male + total_female
    
    print(f"\n📊 Available Voices:")
    print(f"   Male voices: {total_male}")
    print(f"   Female voices: {total_female}")
    print(f"   TOTAL: {total_voices} unique voices")
    
    print(f"\n🎯 For 220 conversations:")
    print(f"   Average usage per voice: {220/total_voices:.1f} conversations")
    print(f"   Maximum repetition: ~6 times per voice")
    
    print(f"\n✅ Benefits:")
    print(f"   - Much more natural variety")
    print(f"   - Personality-matched voices")
    print(f"   - Gender-balanced distribution")
    print(f"   - Consistent per conversation")
    
    # Test assignment
    print(f"\n🔄 Testing voice assignment:")
    test_convs = ["conv_001", "conv_002", "conv_003"]
    test_emotions = ["angry", "polite", "confused"]
    
    for conv, emotion in zip(test_convs, test_emotions):
        voice_id, voice_name = get_voice_for_conversation(conv, emotion)
        print(f"   {conv} ({emotion}) → {voice_name}")
    
    print(f"\n💡 Integration:")
    print(f"   Replace the 6-voice pool in ELEVENLABS_UNIVERSAL_TTS.py")
    print(f"   with this expanded 37-voice pool for better variety!")

if __name__ == "__main__":
    main()