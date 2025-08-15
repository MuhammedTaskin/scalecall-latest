# 🚀 ULTIMATE ChatGPT Prompt - Backend Compatible Turkish Telco Training Data

You know our project perfectly. Here's the FINAL, BACKEND-COMPATIBLE prompt that fixes all critical issues.

## 🎯 CRITICAL BACKEND COMPATIBILITY FIXES:

### **Phone Number Validation Flow (ESSENTIAL):**
```
U: Son 4 hane 7788
A: Numaranız 0555 344 88 11 mi?
U: Evet
TOOL: {"tool_call":{"id":"call_123","name":"verify_user","arguments":{"maiden_name":"extracted","msisdn":"905553448811"}}}
```

**OR if user says no:**
```
U: Hayır
A: Numaranızı 0555 ile başlayarak söyler misiniz?
U: 0532 123 45 67
TOOL: {"tool_call":{"id":"call_456","name":"verify_user","arguments":{"maiden_name":"extracted","msisdn":"905321234567"}}}
```

### **Backend Parameter Rules (MANDATORY):**
- ✅ Use `"customer_id"` (never `user_id`)
- ✅ Use `"msisdn"` with full number (never `phone_last4`)
- ✅ Agent MUST confirm phone numbers in TTS-friendly format: "0555 344 88 11"
- ✅ Every tool call needs unique `"id":"call_xyz123"`

## 📋 SFD v0.3 Format (Backend Compatible):

```
DIALOG_START
id: D046
scenario: phone_validation|multi_step|context_switch|ambiguous_intent|persona_handoff|error_handling
context: SIM|PLAN|BILLING|COVERAGE|MIXED
noise: true|false
quality: foundation|intermediate|advanced|expert|robustness|precision
U: [Turkish user input with ASR noise]
A: [Turkish response ≤2 sentences]
U: [User provides partial phone info]
A: Numaranız 0555 344 88 11 mi?
U: Evet/Hayır
[If Hayır: Ask for full number, get confirmation]
TOOL: {"tool_call":{"id":"call_unique","name":"verify_user","arguments":{"maiden_name":"X","msisdn":"905553448811"}}}
RESULT: {"success":true,"customer_id":"12345","name":"Ali Doğan"}
TOOL: {"tool_call":{"id":"call_unique2","name":"get_user_info","arguments":{"customer_id":"12345"}}}
RESULT: {"success":true,"package":{"id":"basic_5gb","price":99.99}}
HANDOFF: TechAgent | "Sizi teknik uzmanımıza aktarıyorum."
A: [Continue as new persona]
DIALOG_END
```

## 🎯 Generate 25 Dialogs with These Patterns:

### **Phone Validation Dialogs (8 dialogs):**
- User gives last 4 digits → Agent confirms full number
- User says "no" → Agent asks for full number → Confirms again
- ASR confusion on numbers → Agent repeats back for confirmation
- Include TTS-friendly spacing: "0555 344 88 11"

### **Longer Multi-Step Chains (8 dialogs):**
- 4-6 tool calls with phone validation
- Complex flows: verify → check device → generate eSIM → get steps
- Context switches mid-conversation
- Error handling with retry flows

### **Heavy ASR Chaos (15 dialogs total):**
- "mevsim kurulmadi" → eSIM kurulmadı
- "aymay: üç beş dokuz..." → IMEI: 359...
- "sıfır beş beş beş" → 0555
- "cekmiyo hiç" → çekmiyor hiç
- "paketimi beş gebeyden on gebeye" → 5GB'den 10GB'ye

### **Ambiguous Intent → Clarification (6 dialogs):**
- "Problem var" → "Hangi konuda problem yaşıyorsunuz?"
- "Çalışmıyor" → "Neyin çalışmadığını belirtir misiniz?"
- "Değiştirmek istiyorum" → "Neyi değiştirmek istiyorsunuz?"

### **Persona Handoffs (8 dialogs):**
- RouterAgent → TechAgent: "Cihaz problemleri için teknik uzmanımıza aktarıyorum."
- RouterAgent → PlanAgent: "Tarife seçenekleri için uzmanımıza bağlıyorum."
- RouterAgent → BillingAgent: "Fatura konuları için uzmanımıza yönlendiriyorum."

### **Error Handling & Edge Cases (5 dialogs):**
- Wrong IMEI format → Agent asks for correction
- System timeout → Agent offers alternatives
- Invalid customer data → Agent guides through verification

## 🔧 EXACT BACKEND TOOL FORMATS:

```json
// Phone verification with confirmation
{"tool_call":{"id":"call_abc123","name":"verify_user","arguments":{"maiden_name":"Kaya","msisdn":"905553448811"}}}

// All subsequent tools use customer_id
{"tool_call":{"id":"call_def456","name":"get_user_info","arguments":{"customer_id":"12345"}}}
{"tool_call":{"id":"call_ghi789","name":"check_device_registration","arguments":{"customer_id":"12345","imei":"359123456789012"}}}
{"tool_call":{"id":"call_jkl012","name":"reissue_activation_code","arguments":{"customer_id":"12345"}}}
{"tool_call":{"id":"call_mno345","name":"get_activation_steps","arguments":{"os_type":"iOS"}}}
{"tool_call":{"id":"call_pqr678","name":"get_activation_status","arguments":{"customer_id":"12345"}}}
{"tool_call":{"id":"call_stu901","name":"get_available_packages","arguments":{"customer_id":"12345"}}}
{"tool_call":{"id":"call_vwx234","name":"change_package","arguments":{"customer_id":"12345","package_id":"premium_10gb"}}}
{"tool_call":{"id":"call_yzA567","name":"create_support_ticket","arguments":{"customer_id":"12345","subject":"eSIM activation issue","description":"Cannot activate eSIM code","priority":"normal"}}}
```

## 🎭 Dialog Length Strategy:
- **Training dialogs**: 6-10 exchanges (teachable patterns)
- **Real deployment**: Model will naturally extend to 15+ exchanges
- **Focus**: Teach verification flows, tool patterns, handoffs, error handling
- **Result**: Model learns to handle any conversation length

## 🚀 SUCCESS CRITERIA:
- ✅ Phone number confirmation in every dialog with verification
- ✅ TTS-friendly number reading: "0555 344 88 11"
- ✅ Backend-compatible parameter names
- ✅ Unique tool call IDs
- ✅ Realistic Turkish ASR noise (60% of dialogs)
- ✅ Complex multi-step flows with handoffs
- ✅ Error handling and edge cases

## 📝 OUTPUT REQUEST:
Generate **SFD v0.3 — Batch 03 (25 dialogs)** as `chatgpt_batch03_ultimate.md`

**Remember**: Every dialog should feel like a REAL Turkish customer service conversation with proper phone validation, realistic ASR errors, and backend-compatible tool formats.

**Begin generating now!**