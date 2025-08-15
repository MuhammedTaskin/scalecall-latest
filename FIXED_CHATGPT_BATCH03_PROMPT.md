# ChatGPT Prompt for SFD v0.3 — Batch 03 (Turkish Telco Training Data) - BACKEND COMPATIBLE

🚨 **CRITICAL**: This prompt fixes backend compatibility issues!

## 🎯 Key Improvements for Batch 03:

### **Critical Backend Compatibility Fixes:**
1. **Tool Call IDs**: Every tool call MUST have a unique `"id"` field
2. **CORRECT Parameter Names**: 
   - Use `"customer_id"` NOT `"user_id"`
   - Use `"msisdn"` NOT `"phone_last4"`
3. **Verification Flow**: `verify_user` returns `customer_id`, use it in all subsequent tools
4. **Shorter Tool Chains**: Max 3-4 tool calls per dialog
5. **More Realistic ASR Noise**: Increase chaos level

### **Target for Batch 03:**
- **25 dialogs** with heavy focus on **ASR chaos**, **ambiguous intent**, **context switching**, **rural coverage**
- **60% noise ratio** (15/25 dialogs should have `noise: true`)
- **Backend-compatible tool formats**
- **Shorter tool chains** (1-3 calls typical, max 4)

## 📋 Required Format (SFD v0.3 - Backend Compatible):

```
DIALOG_START
id: D046
scenario: context_switch|ambiguous_intent|rural_coverage|error_handling|persona_handoff
context: SIM|PLAN|BILLING|COVERAGE|MIXED
noise: true|false
quality: foundation|intermediate|advanced|expert|robustness|precision
U: [Turkish user input with realistic ASR noise]
A: [Turkish response ≤2 sentences]
TOOL: {"tool_call":{"id":"call_abc123","name":"verify_user","arguments":{"maiden_name":"X","msisdn":"905551234567"}}}
RESULT: {"success":true,"customer_id":"12345","name":"Ali Doğan"}
TOOL: {"tool_call":{"id":"call_def456","name":"get_user_info","arguments":{"customer_id":"12345"}}}
RESULT: {"success":true,"package":{"id":"basic_5gb","price":99.99}}
HANDOFF: TechAgent|PlanAgent|BillingAgent|FAQAgent | "Turkish handoff message"
A: [Turkish follow-up ≤2 sentences as new persona]
DIALOG_END
```

## 🔧 EXACT BACKEND TOOL FORMATS:

### **verify_user (FIXED):**
```json
{"tool_call":{"id":"call_123","name":"verify_user","arguments":{"maiden_name":"Kaya","msisdn":"905551234567"}}}
```
**Returns:** `{"success":true,"customer_id":"12345","name":"Ali Doğan"}`

### **All Other Tools (FIXED):**
```json
{"tool_call":{"id":"call_456","name":"get_user_info","arguments":{"customer_id":"12345"}}}
{"tool_call":{"id":"call_789","name":"check_device_registration","arguments":{"customer_id":"12345","imei":"123456789012345"}}}
{"tool_call":{"id":"call_012","name":"reissue_activation_code","arguments":{"customer_id":"12345"}}}
{"tool_call":{"id":"call_345","name":"get_activation_steps","arguments":{"os_type":"iOS"}}}
{"tool_call":{"id":"call_678","name":"get_activation_status","arguments":{"customer_id":"12345"}}}
{"tool_call":{"id":"call_901","name":"get_available_packages","arguments":{"customer_id":"12345"}}}
{"tool_call":{"id":"call_234","name":"change_package","arguments":{"customer_id":"12345","package_id":"premium_10gb"}}}
{"tool_call":{"id":"call_567","name":"create_support_ticket","arguments":{"customer_id":"12345","subject":"Issue","description":"Problem description","priority":"normal"}}}
```

## 🎭 Specific Scenarios for Batch 03:

### **Heavy ASR Chaos (15 dialogs):**
- "mevsim" → eSIM, "esimim" → eSIM 
- "aymay" → IMEI, "imey numaram" → IMEI number
- "cekmiyo" → çekmiyor, "baglaniyo" → bağlanıyor
- "faturamın" → faturamda, "paketime" → paketimi
- "beş gebe" → 5GB, "on gebe" → 10GB
- "sile" → Şile, "uskudar" → Üsküdar  

### **Ambiguous Intent (8 dialogs):**
- User says "problem var" without specifying what
- "değiştirmek istiyorum" without saying what to change
- "çalışmıyor" without context
- "yardım lazım" with no details

### **Context Switching (6 dialogs):**
- Start with eSIM, suddenly switch to billing
- Begin with coverage complaint, jump to package change
- Mix device registration with family plan questions

### **Persona Handoffs (8 dialogs):**
- RouterAgent → TechAgent (for eSIM/device issues)
- RouterAgent → PlanAgent (for package changes)
- RouterAgent → BillingAgent (for payment/contract issues)
- Use format: `HANDOFF: TechAgent | "Sizi teknik uzmanımıza aktarıyorum."`

### **Rural/Coverage Focus (4 dialogs):**
- Villages: "Gökçeada'da", "Bozcaada'da", "Şile köyünde"
- Mountains: "Uludağ'da", "dağlık bölgede"
- Remote areas: "sahil kenarında", "kırsal kesimde"

## 🚨 CRITICAL BACKEND COMPATIBILITY RULES:

1. **Always use `customer_id`** (never `user_id`)
2. **Always use `msisdn`** (never `phone_last4`)
3. **verify_user must include full phone number**
4. **Every tool call needs unique ID**
5. **Follow exact backend argument names**

## 🚀 Generate Now:

Create **SFD v0.3 — Batch 03 (25 dialogs)** with:
- **Backend-compatible tool formats**
- **Realistic Turkish ASR chaos** (60% noise)
- **Shorter tool chains** (1-3 calls typical)
- **Unique tool call IDs** for every TOOL
- **Correct parameter names** (customer_id, msisdn)
- **Ambiguous intents** requiring clarification
- **Context switches** mid-conversation
- **Persona handoffs** with proper format
- **Rural coverage** scenarios

**Output as:** `chatgpt_batch03_fixed_sfd.md`

Begin now.
