# Turkish Telco Call Center Dataset Generation Prompt

## System Prompt for Gemini/GPT

You are an expert in creating realistic Turkish call center conversations. Generate natural dialogues between customers and agents for a telecom company's eSIM service.

## Conversation Requirements

### Customer Types & Emotions
1. **Angry Young Adult (25%)** - eSIM failures, service issues
2. **Confused Elderly (20%)** - Technology confusion, need help
3. **Business Professional (20%)** - Time-sensitive, assertive
4. **Frustrated Parent (20%)** - Family plan issues, multiple lines
5. **Tech-Savvy Impatient (15%)** - Knows the issue, wants quick fix

### Conversation Complexity Levels

#### Level 1: Simple (30%)
- 1-2 tool calls
- Single issue resolution
- 5-8 conversation turns
- Examples: Balance check, status inquiry

#### Level 2: Medium (40%)
- 3-4 tool calls
- Single issue with verification
- 8-15 conversation turns
- Examples: Package change, eSIM activation

#### Level 3: Complex (20%)
- 5+ tool calls
- Multiple related issues
- 15-25 conversation turns
- Examples: Billing dispute + package change

#### Level 4: Chaos (10%)
- Context switches mid-conversation
- Customer interruptions
- Emotional escalation
- 20+ conversation turns

### Turkish Language Guidelines

#### Natural Speech Patterns
- Use colloquialisms: "yav", "ya", "valla", "işte"
- Include hesitations: "şey", "yani", "ee", "hmm"
- Filler words: "böyle", "öyle", "falan", "filan"

#### Formality Switching
- Young → Informal: "sen", casual tone
- Elderly → Formal: "siz", respectful tone
- Business → Professional but efficient

#### Common Expressions
- Frustration: "Yeter artık!", "Bıktım valla", "Rezalet bir durum"
- Confusion: "Anlamadım ki", "Nasıl yani?", "Ne demek bu?"
- Agreement: "Tamam", "Olur", "Anlaştık"
- Gratitude: "Sağ olun", "Teşekkürler", "Allah razı olsun"

### Tool Call Patterns

Tools should be called implicitly based on conversation flow:

```
Customer: "eSIM'im çalışmıyor"
→ Triggers: [verify_user, check_device_registration, reissue_activation_code]

Customer: "Paketimi değiştirmek istiyorum"
→ Triggers: [verify_user, get_available_packages, change_package]

Customer: "Faturamda hata var"
→ Triggers: [verify_user, check_billing, create_support_ticket]
```

### Realistic Scenarios

#### Scenario 1: eSIM Activation Failure
```json
{
  "setup": "Customer tried self-activation, failed multiple times",
  "emotion_arc": "frustrated → angry → relieved",
  "complications": ["Wrong IMEI", "Device not compatible", "Previous activation pending"],
  "resolution": "New activation code + guided steps"
}
```

#### Scenario 2: Elderly Package Confusion
```json
{
  "setup": "Elderly customer doesn't understand current package",
  "emotion_arc": "confused → anxious → grateful",
  "complications": ["Doesn't know phone model", "Confuses GB with TL", "Needs family member help"],
  "resolution": "Simple explanation + SMS confirmation"
}
```

#### Scenario 3: Business Escalation
```json
{
  "setup": "Business customer, international roaming not working",
  "emotion_arc": "professional → impatient → demanding",
  "complications": ["In airport", "Flight in 30 minutes", "Threatens to switch provider"],
  "resolution": "Emergency activation + manager callback"
}
```

### Interruption Patterns

Include realistic interruptions:
```
Agent: "Öncelikle kimlik doğrula—"
Customer: "—Kimlik doğrulama mı? Ben zaten 3 kere aradım bugün!"

Agent: "IMEI numaranızı kontrol edebilir miy—"
Customer: "—IMEI mi? O ne? Nerede yazıyor?"
```

### Context Switches

Natural topic changes:
```
Customer: "Paketimi değiştirmek istiyorum... Aslında dur, önce şu fatura konusunu halledelim"
Customer: "eSIM kurulumu yapıyoruz tamam da, bu arada yurtdışı paketleri nasıl?"
```

### Output Format

```json
{
  "id": "conv_001",
  "metadata": {
    "type": "esim_activation_complex",
    "customer_persona": "angry_young",
    "duration_seconds": 240,
    "resolution": "success"
  },
  "dialogue": [
    {
      "turn": 1,
      "speaker": "customer",
      "text": "Alo? 3 gündür bu eSIM'i kuramıyorum, yeter artık!",
      "emotion": "angry",
      "timestamp": 0.0
    },
    {
      "turn": 2,
      "speaker": "agent",
      "text": "Merhaba, yaşadığınız sıkıntı için özür dilerim. Size yardımcı olmak için önce kimlik doğrulaması yapmam gerekiyor. Telefon numaranızı alabilir miyim?",
      "emotion": "professional_empathetic",
      "tools_triggered": ["verify_user"],
      "timestamp": 3.5
    }
  ],
  "tools_sequence": ["verify_user", "check_device_registration", "check_previous_attempts", "reissue_activation_code"],
  "interruption_points": [5, 12, 18],
  "context_switches": [
    {
      "at_turn": 8,
      "from": "technical_issue",
      "to": "billing_complaint",
      "trigger": "customer_mention"
    }
  ],
  "key_information": {
    "phone_number": "0555 123 45 67",
    "maiden_name": "Yıldız",
    "imei": "359111222333444",
    "device": "iPhone 14",
    "issue": "activation_failed_multiple",
    "package": "premium_10gb"
  }
}
```

### Validation Checklist

Each conversation must have:
- [ ] Natural Turkish dialogue
- [ ] Appropriate emotion progression
- [ ] Realistic tool call sequence
- [ ] At least one complication
- [ ] Clear resolution or escalation
- [ ] Proper timing estimates
- [ ] Cultural appropriateness

### Edge Cases to Include

1. **Network outage** - Nothing works, must apologize
2. **System maintenance** - Limited tools available
3. **Fraud suspicion** - Extra verification needed
4. **VIP customer** - Priority handling
5. **Technical limitation** - Device doesn't support eSIM
6. **Payment issue** - Can't change package due to debt
7. **Contract lock** - Can't change due to commitment
8. **Language barrier** - Customer struggles with technical terms

Generate 100 unique conversations following these guidelines, ensuring diversity in scenarios, emotions, and resolutions.