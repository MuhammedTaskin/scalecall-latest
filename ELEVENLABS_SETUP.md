# ElevenLabs TTS Setup - FAST TRACK

## 1. Get API Key (2 min)
1. Go to https://elevenlabs.io
2. Sign up/Login
3. Go to Profile → API Keys
4. Copy your API key

## 2. Update Script (30 sec)
```python
# In ELEVENLABS_FAST_TTS.py, line 13:
ELEVENLABS_API_KEY = "your_actual_api_key_here"
```

## 3. Run TTS Generation (5-10 min for 20 conversations)
```bash
python3 ELEVENLABS_FAST_TTS.py
```

## KEY OPTIMIZATIONS:
- Using `eleven_flash_v2_5` model (75ms latency vs 300ms)
- 3 parallel workers for speed
- Turkish-optimized voices
- Emotion-based voice settings

## Voice IDs Being Used:
- Male Young: 21m00Tcm4TlvDq8ikWAM (Josh)
- Male Middle: VR6AewLTigWG4xSOukaG (Arnold)
- Female Young: EXAVITQu4vr4xnSDxMaL (Bella)
- Female Middle: MF3mGyEYCl7XYWbV9V6O (Elli)
- Female Elderly: XrExE9yKIg1WjnnlVkGX (Lily)
- Male Elderly: N2lVS1w4EtoT3dr4eOWO (Callum)

## Output Structure:
```
data/varied_dataset/audio/
├── conv_001/
│   ├── turn_001.mp3
│   ├── turn_003.mp3
│   └── turn_005.mp3
└── conv_002/
    ├── turn_001.mp3
    └── turn_003.mp3
```

## Next Steps After TTS:
1. Create training pairs (audio → agent response)
2. Format for Gemma 3N fine-tuning
3. Start training overnight