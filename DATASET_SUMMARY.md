# Turkish Telco Dataset Summary

## Current Dataset Statistics (320+ conversations)

### Completed Datasets:
1. **Detailed Dataset** (`data/varied_dataset/conversations/`)
   - 26 conversations
   - Complex multi-turn with handoffs
   - Average 7 customer turns each

2. **Short Dataset** (`data/correct_flash_dataset/`)
   - 99 conversations  
   - Minimum 3 turns with proper handoffs
   - Focus on quick resolutions

3. **Smart Dataset** (`data/smart_flash_dataset/`)
   - 95 conversations
   - Proper tool usage patterns
   - 2-4 turns each

4. **Edge Cases Dataset** (`data/quick_varied_dataset/`)
   - 100 conversations
   - Emergency/urgent scenarios
   - Special situations (airport, driving, etc.)

### In Progress:
5. **Flash Heavy Dataset** (`data/flash_heavy_dataset/`)
   - 200 conversations (generating now)
   - Rich, nuanced conversations
   - Regional dialects and complex scenarios

## Total When Complete: 520+ Conversations

## Variation Dimensions:

### Customer Profiles:
- Tech executive
- Elderly retiree  
- Student abroad
- Small business owner
- Frequent traveler
- Parent with teenager
- Gig worker
- Rural customer

### Regional Variations:
- Istanbul (neutral, fast)
- Ankara (formal, moderate)
- Izmir (Aegean, relaxed)
- Antalya (Mediterranean, slow)
- Trabzon (Black Sea, fast)
- Erzurum (Eastern, formal)
- Adana (Southern, informal)
- Bursa (Marmara, moderate)
- Konya (Central, formal)
- Diyarbakir (Southeastern)

### Scenario Categories:
- Technical (eSIM, network, device, services)
- Billing (charges, payments, discounts, issues)
- Plans (changes, types, features, migrations)
- Account (security, management, porting, emergency)

### Conversation Dynamics:
- Straightforward
- Escalating
- Circular (repeating concerns)
- Interrupted (connection issues)
- Multi-issue
- Discovery (finding root cause)
- Negotiation
- Educational

### Urgency Levels:
- Critical (17%)
- High (6%)
- Normal (73%)
- Sensitive (4%)

## TTS Requirements:

### Character Counts:
- Existing 320 conversations: ~140k characters
- New 200 Flash Heavy: ~150k characters (estimated)
- **Total: ~290k characters**

### ElevenLabs Costs:
- Creator plan: 110k chars ($22/month)
- Pro plan: 500k chars ($99/month)
- **Need: Pro plan for full dataset**

### Voice Pool:
- 37 unique voices available
- 17 male, 20 female
- Personality-matched selection
- Regional accent support

## Agent Distribution:

### Primary Agents:
- RouterAgent (100% - always first)
- TechAgent (~40%)
- BillingAgent (~35%)
- PlanAgent (~20%)
- FAQAgent (~15%)

### Handoff Patterns:
- Single handoff: 65%
- Double handoff: 30%
- Triple handoff: 5%

## Tools Used (Top 10):
1. verify_user (100%)
2. route_to_agent (95%)
3. get_customer_status (80%)
4. check_esim_status (35%)
5. get_last_bill (30%)
6. get_customer_plan (25%)
7. apply_campaign_discount (20%)
8. create_tech_ticket (15%)
9. end_conversation (90%)
10. escalate_to_human (5%)

## Quality Metrics:

### Conversation Completeness:
- All have proper greetings
- Identity verification present
- Issue resolution attempted
- Proper closings

### Realism Features:
- Background noise mentions
- Connection issues
- Customer interruptions
- Emotional progressions
- Regional dialect markers
- Time context (morning rush, etc.)

## Next Steps:

1. **Complete Flash Heavy generation** (in progress)
2. **Select best 200 conversations** for TTS (within budget)
3. **Generate audio with ElevenLabs**
4. **Create training pairs** for Gemma 3N
5. **Fine-tune model** with persona switching

## Training Strategy:

### Single Model, Multiple Personas:
- Model: Gemma 3N (multimodal)
- Personas: 5 agents via prompt switching
- Tools: 21 defined, database-mapped
- Handoffs: Dynamic routing logic

### Training Format:
```json
{
  "audio": "base64_encoded_audio",
  "transcript": "customer_text",
  "agent_persona": "current_agent",
  "response": "agent_response",
  "tools": ["tools_to_trigger"],
  "handoff": "next_agent_if_needed"
}
```

## Competition Readiness:

✅ **Dataset Variety**: 520+ conversations covering all scenarios
✅ **Voice Diversity**: 37 unique voices with emotions
✅ **Tool Integration**: Implementable database operations
✅ **Handoff Logic**: Multi-agent coordination ready
✅ **Regional Support**: 10 Turkish regional variations
✅ **Edge Cases**: Emergency and special situations covered

**Estimated completion time**: 2-3 hours for full pipeline