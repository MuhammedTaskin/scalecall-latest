# 🧠 Smart GPT Prompt - Leveraging Our Project Knowledge

**For the GPT that helped build this Turkish telco agent system**

---

# CONTEXT: You Know This Project!

You've been helping me build a **competition-winning Turkish telco AI agent** system. We've designed:

- ✅ **Backend tool schemas** (verify_user, get_user_info, etc.)
- ✅ **Multi-persona system** (RouterAgent, TechAgent, PlanAgent, BillingAgent, FAQAgent)
- ✅ **Turkish ASR noise patterns** (eSIM→"mevsim", çekmiyor→"cekmiyor")
- ✅ **Conversation format** with tool calls and handoffs
- ✅ **Quality requirements** for competition

## 🎯 NEW TASK: Generate the Actual Training Dataset

I need you to **CREATE THE ACTUAL DATASET FILES** for training. Generate **100 high-quality Turkish telco dialogs** using all the knowledge we've built together.

## 📁 FILE STRUCTURE TO CREATE:

Create these files directly:

1. **`chatgpt_generated_dialogs.json`** - Main dataset (100 dialogs)
2. **`chatgpt_samples.json`** - First 10 for quick review
3. **`chatgpt_analysis.md`** - Your analysis of what you generated

## 🎯 EXACT SPECIFICATIONS (You Know These!):

### **Dialog Format:**
```json
{
  "conversations": [
    {"role": "user", "content": [{"type": "text", "text": "Turkish user input with potential ASR noise"}]},
    {"role": "assistant", "content": [{"type": "text", "text": "Turkish response OR tool_call JSON"}]},
    {"role": "user", "content": [{"type": "text", "text": "<tool_result>{mock_tool_response}</tool_result>"}]},
    {"role": "assistant", "content": [{"type": "text", "text": "Turkish follow-up (≤2 sentences)"}]}
  ],
  "scenario_type": "single_tool|multi_step|context_switch|persona_handoff|error_handling",
  "context": "SIM|PLAN|BILLING|COVERAGE|GENERAL|MIXED",
  "has_noise": true/false,
  "quality_tier": "foundation|intermediate|advanced|expert|precision|robustness"
}
```

### **Tool Call Format:**
```json
{"tool_call":{"id":"uuid-string","name":"tool_name","arguments":{...}}}
```

### **Persona Handoff Format:**
```json
{"handoff":{"persona":"TargetAgent","say":"Turkish handoff message"}}
```

### **Tool Result Format:**
```html
<tool_result>{"success":true,"data":{...}}</tool_result>
```

## 🛠️ AVAILABLE TOOLS (From Our Backend):

1. **`verify_user(maiden_name, msisdn)`** → Customer verification
2. **`get_user_info(customer_id)`** → Account information
3. **`check_device_registration(imei)`** → Device compatibility  
4. **`reissue_activation_code(customer_id)`** → New eSIM code
5. **`get_activation_steps(os_type)`** → iOS/Android instructions
6. **`get_activation_status(customer_id)`** → Activation progress
7. **`get_available_packages(customer_id)`** → Available plans
8. **`change_package(customer_id, package_id)`** → Change plan
9. **`create_support_ticket(customer_id, subject, description, priority)`** → Support ticket

## 🇹🇷 TURKISH ASR NOISE PATTERNS (We Defined Together):

Apply to **40% of user inputs**:

### **Core Telco Terms:**
- eSIM → "esim", "e sim", "mevsim", "eşim", "e-sim"
- IMEI → "imei", "aymay", "imey", "cihaz kodu"
- aktivasyon → "aktivasyon kodu", "etkinleştirme", "açma kodu"
- paket → "paketi", "paketim", "tarife", "plan"
- çekmiyor → "cekmiyor", "çekmiyo", "yok sinyalim"

### **Diacritic Loss:**
- ı→i, ğ→g, ü→u, ş→s, ö→o, ç→c
- "değiştirmek" → "degistirmek"
- "yükseltmek" → "yukseltmek"

### **Number/Currency:**
- "beş GB" → "5 gb", "bes gb"
- "yüz lira" → "100 lira", "yuz lira"
- "on iki ay" → "12 ay", "on iki ay"

## 🎭 PERSONA RULES (From Our Design):

### **RouterAgent (Default):**
- General inquiries, routing decisions
- **ALWAYS verify user first** before account operations
- Hand off to specialists when needed
- Tools: `verify_user`, `get_user_info`, `create_support_ticket`

### **TechAgent:**
- Device issues, eSIM activation, coverage problems
- Technical diagnostics and step-by-step solutions
- Tools: `check_device_registration`, `get_activation_steps`, `get_activation_status`, `reissue_activation_code`

### **PlanAgent:**
- Package changes, comparisons, upselling
- Pricing discussions and feature explanations
- Tools: `get_available_packages`, `change_package`, `get_user_info`

### **BillingAgent:**
- Payment issues, billing disputes, account credits
- Financial troubleshooting and explanations
- Tools: `get_user_info`, `create_support_ticket`

### **FAQAgent:**
- General information, policies, simple Q&A
- Educational responses (minimal tool usage)
- Tools: Generally none (text responses)

## 📊 DIALOG DISTRIBUTION (Generate This Mix):

- **25 Single Tool Dialogs** (simple tool usage)
- **30 Multi-Step Decision Chains** (3+ tool sequence)
- **20 Context Switching Dialogs** (topic changes mid-conversation)
- **15 Persona Handoff Dialogs** (specialist routing)
- **10 Error Handling Dialogs** (tool failures with recovery)

## 🚀 REALISTIC MOCK DATA (Use These):

### **Customer Data:**
- **Names:** Ahmet Yılmaz, Fatma Demir, Mehmet Kaya, Ayşe Özkan, Mustafa Çelik, Hatice Arslan, Ali Doğan, Zeynep Koç, Hüseyin Şahin, Elif Yıldız
- **Maiden Names:** Kaya, Özkan, Demir, Çelik, Yılmaz, Arslan, Doğan, Koç, Şahin, Yıldız
- **Phone Numbers:** 905551234567, 905559876543, 905551122334, 905554455667
- **Customer IDs:** 12345, 67890, 11223, 44556, 78901
- **IMEI Numbers:** 123456789012345, 987654321098765, 112233445566778

### **Package Data:**
- **basic_5gb:** "Temel 5GB", 99.99 TL, "5GB yüksek hız internet, Sınırsız konuşma, 1000 SMS"
- **premium_10gb:** "Premium 10GB", 149.99 TL, "10GB yüksek hız internet, Sınırsız konuşma, Sınırsız SMS, 5G destekli"  
- **unlimited:** "Sınırsız", 299.99 TL, "Sınırsız yüksek hız internet, Sınırsız konuşma, Sınırsız SMS, 5G destekli"
- **family_20gb:** "Aile 20GB", 199.99 TL, "20GB paylaşımlı internet, 4 hat, Sınırsız konuşma"

## 🎯 TURKISH LANGUAGE REQUIREMENTS:

### **Assistant Responses:**
- **≤2 sentences maximum** per response
- **Professional and polite** tone
- **Include Turkish politeness markers:** "hanım/bey", "size", "yardımcı olabilirim"
- **Natural Turkish flow** (not machine-translated)

### **Examples:**
- "Kimlik doğrulama başarılı, Ahmet bey. Size nasıl yardımcı olabilirim?"
- "Cihazınız eSIM uyumlu görünüyor. Aktivasyon kodunuzu hazırlayabilirim."
- "Paket değişikliği için sizi tarife uzmanımıza yönlendiriyorum."

## ⭐ QUALITY REQUIREMENTS (Competition Standards):

### **Must Have:**
- ✅ **Perfect JSON syntax** (no formatting errors)
- ✅ **Logical tool sequences** (verify → access → action)
- ✅ **Customer data consistency** throughout dialog
- ✅ **Realistic Turkish conversation flow**
- ✅ **Proper error handling** when tools fail

### **Advanced Features:**
- ✅ **Context switching** (user changes topic mid-conversation)
- ✅ **Ambiguous requests** requiring clarification
- ✅ **Multiple solution paths** for same problem
- ✅ **Graceful error recovery** with alternatives

## 🚀 EXECUTION INSTRUCTIONS:

1. **Generate 100 dialogs** following the distribution above
2. **Apply ASR noise to 40%** of user inputs
3. **Ensure variety** in complexity and scenarios
4. **Use realistic mock data** consistently
5. **Create files directly** with the generated content
6. **Include analysis** of what you generated

## 🎯 START GENERATING!

You know this project inside and out. Create the training dataset that will make this Turkish telco agent win the competition!

**Focus on:**
- **Realistic customer scenarios** (actual Turkish telco problems)
- **Natural conversation flow** (how real people talk)
- **Dynamic tool usage** (context-driven decisions, not patterns)
- **Competition-level quality** (precise, error-free, comprehensive)

Generate the files and let's complete this elite system! 🏆
