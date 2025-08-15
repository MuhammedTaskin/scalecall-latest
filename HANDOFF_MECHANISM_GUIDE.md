# 🎭 Agent Handoff Mechanism Guide

## How Persona Handoffs Work in Our System

### **Core Concept:**
- **ONE MODEL** handles all personas (RouterAgent, TechAgent, PlanAgent, BillingAgent, FAQAgent)
- **Persona switching** happens via **special JSON responses**, NOT tool calls
- The backend changes the system prompt when it sees a handoff request

### **Handoff JSON Format:**
```json
{"handoff":{"persona":"TechAgent","say":"Sizi teknik uzmanımıza yönlendiriyorum."}}
```

### **Available Personas:**
- **RouterAgent** - Main entry point, general routing
- **TechAgent** - Device compatibility, eSIM activation, coverage
- **PlanAgent** - Package changes, pricing, tariffs  
- **BillingAgent** - Payments, contracts, billing disputes
- **FAQAgent** - General information, common questions

### **When to Use Handoffs:**
1. **RouterAgent → TechAgent**: Device issues, eSIM problems, coverage complaints
2. **RouterAgent → PlanAgent**: Package changes, pricing questions
3. **RouterAgent → BillingAgent**: Payment issues, contract questions, billing disputes
4. **Any Agent → RouterAgent**: When outside expertise area

### **SFD Format for Handoffs:**
```
A: İhtiyacınız için sizi uzmanımıza aktarıyorum.
HANDOFF: TechAgent | "eSIM aktivasyonu için devraldım."
A: [Continued response as TechAgent]
```

### **Backend Processing:**
1. Model outputs handoff JSON
2. Backend updates system prompt to new persona
3. Model continues with new persona context
4. Conversation history is preserved

### **Training Data Examples:**

#### Example 1: Router → Tech
```
U: eSIM kurdum ama çalışmıyor
A: Teknik kontrolümüz için sizi uzmanımıza aktarıyorum.
HANDOFF: TechAgent | "Aktivasyon sorununu çözüyorum."
A: Cihaz uyumluluğunu kontrol ediyorum.
TOOL: {"tool_call":{"id":"call_123","name":"check_device_registration","arguments":{"imei":"123456789012345"}}}
```

#### Example 2: Router → Billing  
```
U: Faturamda hata var galiba
A: Faturalama uzmanımıza aktarıyorum.
HANDOFF: BillingAgent | "Fatura incelemesi için devraldım."
A: Hesap bilgilerinizi kontrol ediyorum.
TOOL: {"tool_call":{"id":"call_456","name":"get_user_info","arguments":{"customer_id":"1001"}}}
```

### **Key Training Points:**
- Handoffs should feel natural and helpful
- Always include a brief Turkish explanation ("say" field)
- Continue the conversation after handoff without breaking flow
- New persona should use appropriate tools for their expertise area
