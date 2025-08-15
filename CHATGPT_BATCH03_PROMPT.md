# ChatGPT Prompt for SFD v0.3 — Batch 03 (Turkish Telco Training Data)

You know our Turkish telco project perfectly. Batch 02 was good but had some issues - let's fix them and generate even better content.

## 🎯 Key Improvements for Batch 03:

### **Critical Fixes:**
1. **Tool Call IDs**: Every tool call MUST have a unique `"id"` field - you forgot these in Batch 02
2. **Shorter Tool Chains**: Max 3-4 tool calls per dialog (Batch 02 had some with 7+ calls)
3. **More Realistic ASR Noise**: Increase chaos level - more homophones, agglutinative splits
4. **Context Switching**: Include more mid-conversation topic changes
5. **Ambiguous Intent**: Add dialogs where user intent is unclear initially

### **Target for Batch 03:**
- **25 dialogs** with heavy focus on **ASR chaos**, **ambiguous intent**, **context switching**, **rural coverage**
- **60% noise ratio** (15/25 dialogs should have `noise: true`)
- **More error scenarios** and **edge cases**
- **Shorter tool chains** (1-3 calls typical, max 4)

## 📋 Required Format (SFD v0.3):

```
DIALOG_START
id: D046
scenario: context_switch|ambiguous_intent|rural_coverage|error_handling|persona_handoff
context: SIM|PLAN|BILLING|COVERAGE|MIXED
noise: true|false
quality: foundation|intermediate|advanced|expert|robustness|precision
U: [Turkish user input with realistic ASR noise]
A: [Turkish response ≤2 sentences]
TOOL: {"tool_call":{"id":"call_abc123","name":"tool_name","arguments":{...}}}
RESULT: {"success":true,"data":{...}} OR {"error":"error_type","message":"..."}
HANDOFF: TechAgent|PlanAgent|BillingAgent|FAQAgent | "Turkish handoff message"
A: [Turkish follow-up ≤2 sentences as new persona]
DIALOG_END
```

## 🎭 Specific Scenarios for Batch 03:

### **Heavy ASR Chaos (15 dialogs):**
- "mevsim" → eSIM, "esimim" → eSIM 
- "aymay" → IMEI, "imey numaram" → IMEI number
- "cekmiyo" → çekmiyor, "baglaniyo" → bağlanıyor
- "faturamın" → faturamda, "paketime" → paketimi
- "beş gebe" → 5GB, "on gebe" → 10GB
- "sile" → Şile, "uskudar" → Üsküdar  
- "iptal ediyim" → iptal etmek istiyorum

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

## 🚀 Generate Now:

Create **SFD v0.3 — Batch 03 (25 dialogs)** with:
- **Realistic Turkish ASR chaos** (60% noise)
- **Shorter tool chains** (1-3 calls typical)
- **Unique tool call IDs** for every TOOL
- **Ambiguous intents** requiring clarification
- **Context switches** mid-conversation
- **Rural coverage** scenarios
- **More error handling** edge cases

**Output as:** `chatgpt_batch03_sfd.md`

Begin now.
