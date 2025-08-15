# 🎯 FINAL CORRECT ChatGPT Prompt - Real Phone Call Flow

EVET KANKA! Şimdi anladım! Caller ID var, agent sadece onay alıyor!

## 📞 REAL CALL CENTER FLOW:

### **Standard Call Opening:**
```
Agent: Merhaba, Türk Telekom eSIM hizmetleri, size nasıl yardımcı olabilirim?
User: [Problem explanation - eSIM, paket, fatura etc.]
Agent: Kimlik doğrulaması için, aradığınız numara 0 555 344 88 11 bu mu?
User: Evet / Hayır
[If evet: continue, if hayır: ask for correct number]
```

## 📋 SFD v0.3 Format (Real Call Center):

```
DIALOG_START
id: D046
scenario: phone_confirmation|multi_step|persona_handoff|error_handling
context: SIM|PLAN|BILLING|COVERAGE|MIXED
noise: true|false
quality: foundation|intermediate|advanced|expert|robustness|precision
A: Merhaba, Türk Telekom eSIM hizmetleri, size nasıl yardımcı olabilirim?
U: [Turkish user problem with ASR noise]
A: Kimlik doğrulaması için, aradığınız numara 0 555 344 88 11 bu mu?
U: Evet
TOOL: {"tool_call":{"id":"call_123","name":"verify_user","arguments":{"maiden_name":"system_detected","msisdn":"905553448811"}}}
RESULT: {"success":true,"customer_id":"12345","name":"Ali Doğan"}
A: Teşekkürler Ali bey, size nasıl yardımcı olabilirim?
[Continue with actual problem solving...]
DIALOG_END
```

## 🎯 Generate 25 Real Call Center Dialogs:

### **Call Opening Pattern (ALL 25 dialogs):**
- Agent: Standard greeting
- User: Problem statement  
- Agent: "Aradığınız numara 0 555 344 88 11 bu mu?" (WITH BREAKS)
- User: Evet/Hayır confirmation
- Continue with problem solving

### **Problem Categories:**

#### **eSIM Issues (8 dialogs):**
```
A: Merhaba, Türk Telekom eSIM hizmetleri, size nasıl yardımcı olabilirim?
U: mevsim kurulum yapamiyorum, kod geldi ama calismio
A: Aradığınız numara 0 532 123 45 67 bu mu?
U: evet
TOOL: {"tool_call":{"id":"call_abc","name":"verify_user","arguments":{"maiden_name":"system","msisdn":"905321234567"}}}
RESULT: {"success":true,"customer_id":"1001","name":"Ahmet Yılmaz"}
A: Ahmet bey, eSIM kurulum sorununuzu çözüyorum.
[Continue with eSIM troubleshooting...]
```

#### **Package Changes (6 dialogs):**
```
A: Merhaba, Türk Telekom eSIM hizmetleri, size nasıl yardımcı olabilirim?
U: paketimi degistirmek istiyorum, 5 gebeden 10 gebeye gecmek istiyorum
A: Aradığınız numara 0 555 987 65 43 bu mu?
U: evet
TOOL: {"tool_call":{"id":"call_def","name":"verify_user","arguments":{"maiden_name":"system","msisdn":"905559876543"}}}
RESULT: {"success":true,"customer_id":"1002","name":"Fatma Demir"}
HANDOFF: PlanAgent | "Paket değişikliği için uzmanımıza aktarıyorum."
A: Fatma hanım, mevcut paketinizi kontrol ediyorum.
[Continue with package change...]
```

#### **Billing Issues (5 dialogs):**
```
A: Merhaba, Türk Telekom eSIM hizmetleri, size nasıl yardımcı olabilirim?
U: faturamda hata var galiba, cok yuksek geldi
A: Aradığınız numara 0 544 111 22 33 bu mu?
U: evet
TOOL: {"tool_call":{"id":"call_ghi","name":"verify_user","arguments":{"maiden_name":"system","msisdn":"905441112233"}}}
RESULT: {"success":true,"customer_id":"1003","name":"Mehmet Kaya"}
HANDOFF: BillingAgent | "Fatura konuları için uzmanımıza yönlendiriyorum."
A: Mehmet bey, fatura detaylarınızı inceliyorum.
[Continue with billing issue...]
```

#### **Coverage/Technical (4 dialogs):**
```
A: Merhaba, Türk Telekom eSIM hizmetleri, size nasıl yardımcı olabilirim?
U: sile'de sinyal cekmiyo, ne yapabilirim?
A: Aradığınız numara 0 533 777 88 99 bu mu?
U: evet
TOOL: {"tool_call":{"id":"call_jkl","name":"verify_user","arguments":{"maiden_name":"system","msisdn":"905337778899"}}}
RESULT: {"success":true,"customer_id":"1004","name":"Ayşe Özkan"}
HANDOFF: TechAgent | "Teknik destek için uzmanımıza aktarıyorum."
A: Ayşe hanım, bölge kapsama durumunu kontrol ediyorum.
[Continue with coverage check...]
```

#### **Wrong Number Cases (2 dialogs):**
```
A: Merhaba, Türk Telekom eSIM hizmetleri, size nasıl yardımcı olabilirim?
U: esim sorunu var
A: Aradığınız numara 0 555 123 45 67 bu mu?
U: hayır, benim numaram 0 532 987 65 43
A: Teşekkürler, 0 532 987 65 43 doğru mu?
U: evet
TOOL: {"tool_call":{"id":"call_mno","name":"verify_user","arguments":{"maiden_name":"system","msisdn":"905329876543"}}}
RESULT: {"success":true,"customer_id":"1005","name":"Hüseyin Şahin"}
A: Hüseyin bey, eSIM sorununuzu çözüyorum.
[Continue...]
```

## 🔧 EXACT BACKEND FORMATS:

### **Phone Confirmation (TTS Format):**
- "0 555 344 88 11" (WITH SPACES for clear TTS)
- "0 532 123 45 67" 
- "0 544 777 88 99"

### **Tool Calls:**
```json
{"tool_call":{"id":"call_unique","name":"verify_user","arguments":{"maiden_name":"system","msisdn":"905553448811"}}}
```

## 🚨 KEY POINTS:
- ✅ **EVERY dialog starts with standard greeting**
- ✅ **Phone number confirmation with TTS breaks**
- ✅ **Caller ID assumed, just confirming**
- ✅ **Real call center flow**
- ✅ **Backend compatible formats**
- ✅ **Heavy Turkish ASR noise** (60% of dialogs)

## 📝 OUTPUT:
Generate **SFD v0.3 — Real Call Center Batch (25 dialogs)** as `chatgpt_real_callcenter_batch.md`

**Begin now!**
