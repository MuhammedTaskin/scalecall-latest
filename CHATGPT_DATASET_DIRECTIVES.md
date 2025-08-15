# ChatGPT Dataset Generation Directives
## Turkish Telco Agent Synthetic Data Creation

### 🎯 **MISSION**
Generate **high-quality Turkish telco customer service dialogs** for training an AI agent that must:
- Handle tool calls dynamically (no static patterns)
- Switch between personas (RouterAgent, TechAgent, PlanAgent, BillingAgent, FAQAgent)
- Manage context switches and interruptions
- Be robust to Turkish ASR noise (eSIM/mevsim confusions)

---

## 📋 **EXACT FORMAT REQUIRED**

### **Dialog Structure** (JSON)
```json
{
  "conversations": [
    {"role": "user", "content": [{"type": "text", "text": "Turkish user input"}]},
    {"role": "assistant", "content": [{"type": "text", "text": "Turkish response OR tool_call JSON"}]},
    {"role": "user", "content": [{"type": "text", "text": "<tool_result>{result_json}</tool_result>"}]},
    {"role": "assistant", "content": [{"type": "text", "text": "Turkish follow-up response"}]}
  ],
  "scenario_type": "single_tool|multi_step|context_switch",
  "context": "SIM|PLAN|BILLING|COVERAGE|GENERAL",
  "has_noise": false,
  "quality_tier": "advanced"
}
```

### **Tool Call Format** (EXACT)
```json
{"tool_call":{"id":"uuid","name":"verify_user","arguments":{"maiden_name":"Kaya","msisdn":"905551234567"}}}
```

### **Handoff Format** (EXACT)
```json
{"handoff":{"persona":"TechAgent","say":"Sizi teknik uzmanımıza yönlendiriyorum."}}
```

### **Tool Result Format** (EXACT)
```json
<tool_result>{"success":true,"data":{"customer_id":"12345","name":"Ahmet Yılmaz","verified":true}}</tool_result>
```

---

## 🛠️ **AVAILABLE TOOLS**

### **Verification & Info**
- `verify_user(maiden_name, msisdn)` → Customer verification
- `get_user_info(customer_id)` → Account information

### **Device & eSIM**
- `check_device_registration(imei)` → Device compatibility
- `reissue_activation_code(customer_id)` → New eSIM code
- `get_activation_steps(os_type)` → iOS/Android instructions
- `get_activation_status(customer_id)` → Activation progress

### **Packages & Billing**
- `get_available_packages(customer_id)` → Available plans
- `change_package(customer_id, package_id)` → Change plan
- `create_support_ticket(customer_id, subject, description, priority)` → Support ticket

---

## 🎭 **PERSONA RULES**

### **RouterAgent** (Default)
- General inquiries and routing
- Always verify user first
- Hand off to specialists when needed

### **TechAgent** 
- Device issues, eSIM activation, coverage
- Technical diagnostics and solutions
- IMEI checks and compatibility

### **PlanAgent**
- Package changes and comparisons
- Pricing and features
- Contract modifications

### **BillingAgent**
- Payment issues and disputes
- Billing inquiries and adjustments
- Account credit and refunds

### **FAQAgent**
- General information
- Policies and procedures
- Simple Q&A

---

## 🇹🇷 **TURKISH LANGUAGE RULES**

### **Assistant Responses**
- ≤2 sentences maximum
- Polite and professional
- Include: "hanım/bey", "size", "yardımcı"
- Examples:
  - "Kimlik doğrulama başarılı, Ahmet bey. Size nasıl yardımcı olabilirim?"
  - "Cihazınız eSIM uyumlu. Aktivasyon kodunuzu hazırlayabilirim."

### **Turkish ASR Noise Patterns**
Apply these corruptions to user inputs:

#### **eSIM Confusions**
- eSIM → "esim", "e sim", "mevsim", "eşim", "e-sim"
- IMEI → "imei", "aymay", "imey", "cihaz kodu"
- aktivasyon → "aktivasyon kodu", "etkinleştirme", "açma kodu"

#### **Diacritic Loss**
- ı→i, ğ→g, ü→u, ş→s, ö→o, ç→c
- "çekmiyor" → "cekmiyor", "çekmiyo"
- "değiştirmek" → "degistirmek"

#### **Number Confusions**
- "beş GB" → "5 gb", "bes gb"
- "yüz lira" → "100 lira", "yuz lira"
- "son dört" → "son 4", "son dort"

---

## 📊 **SCENARIO TYPES TO GENERATE**

### **1. Single Tool Dialogs** (25%)
Simple tool usage with 1-2 tool calls:
```
User: "Kimlik doğrulama yapmak istiyorum"
Assistant: {"tool_call":{"name":"verify_user",...}}
User: <tool_result>{"success":true,...}</tool_result>
Assistant: "Doğrulama başarılı. Size nasıl yardımcı olabilirim?"
```

### **2. Multi-Step Decision Chains** (30%)
Complex flows with 3+ tools:
```
verify_user → get_user_info → get_available_packages → change_package
```

### **3. Context Switching** (15%)
Mid-conversation topic changes:
```
User starts package inquiry → interrupts with urgent billing issue → agent switches context gracefully
```

### **4. Persona Handoffs** (15%)
Agent recognizes need for specialist:
```
RouterAgent → detects device issue → hands off to TechAgent → continues with technical tools
```

### **5. Error Handling** (15%)
Tool failures with graceful recovery:
```
Tool fails → agent explains politely → suggests alternatives → creates support ticket if needed
```

---

## 🎯 **QUALITY REQUIREMENTS**

### **Must Have**
- ✅ Valid JSON tool calls (no extra text around them)
- ✅ Turkish responses ≤2 sentences
- ✅ Logical tool sequences
- ✅ Customer data consistency within dialog
- ✅ Proper persona handoff when appropriate

### **Advanced Features**
- ✅ ASR noise in user inputs (35% of dialogs)
- ✅ Context switching mid-conversation
- ✅ Error scenarios with recovery
- ✅ Ambiguous requests requiring clarification
- ✅ Multiple valid tool paths for same goal

---

## 🚀 **EXAMPLE GENERATION PROMPT**

**"Generate 50 Turkish telco customer service dialogs following the exact format above. Include:**
- **20 single-tool dialogs** (verification, device check, package inquiry)
- **15 multi-step dialogs** (package change flow, eSIM setup flow)
- **10 context switching dialogs** (topic changes mid-conversation)
- **5 error handling dialogs** (tool failures with recovery)

**Apply Turkish ASR noise to 35% of user inputs. Ensure all tool calls are valid JSON. Keep assistant responses ≤2 sentences in natural Turkish."**

---

## 📝 **SAMPLE DIALOG FORMATS**

### **Single Tool Example**
```json
{
  "conversations": [
    {"role": "user", "content": [{"type": "text", "text": "mevsim aktivasyon kodu istiyorum"}]},
    {"role": "assistant", "content": [{"type": "text", "text": "eSIM aktivasyon kodu için önce kimlik doğrulaması yapalım."}]},
    {"role": "assistant", "content": [{"type": "text", "text": "{\"tool_call\":{\"id\":\"abc123\",\"name\":\"verify_user\",\"arguments\":{\"maiden_name\":\"Kaya\",\"msisdn\":\"905551234567\"}}}"}]},
    {"role": "user", "content": [{"type": "text", "text": "<tool_result>{\"success\":true,\"data\":{\"customer_id\":\"12345\",\"name\":\"Ahmet Yılmaz\",\"verified\":true}}</tool_result>"}]},
    {"role": "assistant", "content": [{"type": "text", "text": "Doğrulama tamam, Ahmet bey. eSIM kodunuzu hazırlıyorum."}]}
  ],
  "scenario_type": "single_tool",
  "context": "SIM",
  "has_noise": true,
  "quality_tier": "advanced"
}
```

### **Context Switch Example**
```json
{
  "conversations": [
    {"role": "user", "content": [{"type": "text", "text": "Paket seçeneklerimi görmek istiyorum"}]},
    {"role": "assistant", "content": [{"type": "text", "text": "Paket seçenekleri için kimlik doğrulaması yapayım."}]},
    {"role": "user", "content": [{"type": "text", "text": "Dur bekleyin, daha acil fatura sorunum var!"}]},
    {"role": "assistant", "content": [{"type": "text", "text": "Anlıyorum, fatura konusu öncelikli. {\"handoff\":{\"persona\":\"BillingAgent\",\"say\":\"Faturalama uzmanımıza bağlıyorum.\"}}"}]},
    {"role": "assistant", "content": [{"type": "text", "text": "Fatura sorununuz için yardımcı olayım. Kimlik doğrulaması yapabilir miyim?"}]}
  ],
  "scenario_type": "context_switch_package_to_billing",
  "context": "MIXED",
  "has_noise": false,
  "quality_tier": "expert"
}
```

---

## ⚡ **READY TO USE**

Copy these directives to ChatGPT and request:

**"Using these exact specifications, generate 100 high-quality Turkish telco customer service dialogs in the specified JSON format. Focus on realistic scenarios, proper tool usage, and natural Turkish conversation flow."**

This will give you additional high-quality synthetic data to complement the 25,000 dialogs we already generated!
