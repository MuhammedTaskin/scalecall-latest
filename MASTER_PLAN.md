# 🚀 MASTER PLAN: TURKISH TELCO AI AGENT
## TEKNOFEST 2025 - 28 Hour Sprint

---

## 🎯 COMPETITION REQUIREMENTS SUMMARY
- **Dynamic Tool Selection:** NO hardcoded if/else, agent must reason
- **Context Switching:** Handle interruptions and topic changes  
- **Multi-step Chains:** Complex decision flows based on previous results
- **Mock Systems:** Simulate backend telco systems
- **State Management:** Memory and conversation history
- **100+ Test Cases:** Diverse scenarios with metrics
- **Open Source Only:** No proprietary solutions

---

## 💡 OUR SECRET WEAPONS

### 1. **GEMMA 3N MULTIMODAL ADVANTAGE**
- **NATIVE AUDIO UNDERSTANDING** - Processes Turkish audio directly
- **140 languages** including Turkish
- **100+ spoken languages** for ASR
- **No separate STT needed** - Direct audio→tool mapping
- **6 tokens/second** audio processing (160ms per token)

### 2. **ELEVENLABS SYNTHETIC DATASET**
- Generate realistic Turkish conversations
- Control emotions via voice settings
- Multiple Turkish voices available
- Create angry, confused, happy customers programmatically

---

## 📊 ARCHITECTURE OVERVIEW

```
TRAINING PIPELINE:
1. Gemini generates conversations → JSON
2. ElevenLabs voices them (rotating speakers) → MP3  
3. Create training pairs → Fine-tune Gemma 3N

INFERENCE PIPELINE:
Customer Audio → Gemma 3N → Tools + Text → ElevenLabs TTS → Agent Audio
```

---

## 🛠️ IMPLEMENTATION PHASES

### **PHASE 1: Dataset Generation (6 hours)**

#### 1.1 Conversation Generation
```python
# Using Gemini/GPT to generate 1000+ conversations
SCENARIOS = {
    "simple": ["balance_check", "status_inquiry"],  # 30%
    "medium": ["package_change", "esim_activation"],  # 40%
    "complex": ["multi_issue", "escalation"],  # 20%
    "chaos": ["interruptions", "context_switches"]  # 10%
}
```

#### 1.2 Voice Generation Strategy
```python
# ElevenLabs emotion settings
EMOTIONS = {
    "angry": {"stability": 0.25, "style": 0.9},
    "confused": {"stability": 0.8, "style": 0.3},
    "frustrated": {"stability": 0.35, "style": 0.7},
    "professional": {"stability": 0.75, "style": 0.2}
}

# Voice rotation to prevent memorization
VOICES = ["Belma", "Rachel", "Domi", "Antoni", ...]
```

#### 1.3 Training Data Format
```json
{
  "audio": "path/to/customer_audio.mp3",
  "transcript": "Merhaba, eSIM'im çalışmıyor",
  "agent_response": "Kimlik doğrulama yapalım",
  "tools": ["verify_user", "check_device"],
  "emotion": "frustrated",
  "interruptions": [15, 32]
}
```

---

### **PHASE 2: Mock Tool Implementation (2 hours)**

#### Available Tools
1. `verify_user` - Phone + maiden name verification
2. `check_device_registration` - IMEI validation
3. `reissue_activation_code` - Generate eSIM codes
4. `get_available_packages` - List packages
5. `change_package` - Upgrade/downgrade
6. `check_billing` - Invoice queries
7. `create_support_ticket` - Complaints
8. `transfer_to_human` - Escalation

#### Dynamic Discovery
- Model learns tools through exploration
- No hardcoded tool list in prompts
- Self-discovers capabilities

---

### **PHASE 3: Fine-tuning Pipeline (8 hours)**

#### 3.1 Data Preparation
```python
# Convert audio+text+tools to training format
training_data = {
    "input": {
        "audio": audio_embedding,  # Gemma 3N processes directly
        "context": previous_tools
    },
    "output": {
        "text": "Agent response in Turkish",
        "tools": ["tool1", "tool2"],
        "parameters": {...}
    }
}
```

#### 3.2 Training Configuration
```python
# Gemma 3N with LoRA
config = {
    "model": "gemma-3n-E4B-it",
    "lora_r": 8,
    "lora_alpha": 8,
    "learning_rate": 2e-4,
    "batch_size": 4,
    "max_seq_length": 1024,
    "finetune_audio": True,
    "finetune_text": True
}
```

---

### **PHASE 4: Evaluation System (2 hours)**

#### Metrics
1. **Tool Accuracy:** Correct tool selection rate
2. **Context Retention:** Maintains conversation thread
3. **Emotion Alignment:** Response matches customer emotion
4. **Resolution Rate:** Successfully resolves issues
5. **Interruption Handling:** Gracefully manages topic changes

#### Test Scenarios (100+)
- Different difficulty levels
- Edge cases and failures
- Real-world complexity

---

### **PHASE 5: Demo & Presentation (2 hours)**

#### Demo Features
1. Live voice input processing
2. Real-time tool execution visualization
3. Emotion detection display
4. Context switching demonstration
5. Multiple scenario walkthroughs

#### Documentation
- System architecture
- Implementation details
- Performance metrics
- Scalability analysis (100K calls/day)

---

## 🎮 EXECUTION TIMELINE

| Hour | Task | Status |
|------|------|--------|
| 0-2 | Dataset generation with Gemini | 🔄 |
| 2-6 | ElevenLabs voice synthesis | ⏳ |
| 6-8 | Mock tool implementation | ⏳ |
| 8-16 | Gemma 3N fine-tuning | ⏳ |
| 16-18 | Evaluation pipeline | ⏳ |
| 18-20 | Integration & testing | ⏳ |
| 20-24 | Demo preparation | ⏳ |
| 24-26 | Documentation | ⏳ |
| 26-28 | Final testing & submission | ⏳ |

---

## 🔑 KEY DIFFERENTIATORS

1. **Multimodal Native:** Direct audio understanding, not transcription
2. **Emotional Intelligence:** Responds to voice tone, not just words
3. **Dynamic Tool Discovery:** Learns tools, doesn't memorize
4. **Anti-memorization:** Voice rotation prevents overfitting
5. **Production Ready:** Scalable to 100K calls/day

---

## 🚨 CRITICAL SUCCESS FACTORS

1. **Quality over Quantity:** 100 perfect scenarios > 1000 mediocre ones
2. **Real Emotions:** Use ElevenLabs settings to create genuine anger/confusion
3. **Tool Reasoning:** Model must explain WHY it calls each tool
4. **Graceful Failures:** Some calls should escalate to human
5. **Turkish Nuances:** Formal/informal, regional expressions, cultural context

---

## 📝 NOTES & REMINDERS

- Keep it simple but powerful
- Focus on dynamic reasoning, not static flows
- Test with edge cases early
- Document everything for judges
- Show clear metrics and KPIs
- Demonstrate scalability calculations

---

**LET'S FUCKING WIN THIS! 🏆**