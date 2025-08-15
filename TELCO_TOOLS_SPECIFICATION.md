# Telco Call Center Tools Specification
## TEKNOFEST 2025 Competition

This document defines ALL tools available in the system. The dataset generator MUST use ONLY these tools.

## Tool Categories by Agent

### 🔄 RouterAgent Tools
```python
verify_user(msisdn: str, maiden_name: str) -> {verified: bool, customer_id: str}
# Verify customer identity using phone number and security question

get_customer_profile(customer_id: str) -> {name: str, plan: str, status: str}  
# Get basic customer information for routing decisions

check_recent_tickets(customer_id: str) -> {tickets: List[dict], count: int}
# Check if customer has recent support tickets

route_to_agent(agent_type: str, reason: str) -> {success: bool, agent_id: str}
# Route customer to specialized agent
```

### 🔧 TechAgent Tools
```python
check_esim_status(customer_id: str) -> {status: str, error_code: str}
# Check eSIM activation status and any errors

check_device_compatibility(imei: str) -> {compatible: bool, supports_5g: bool}
# Verify if device supports eSIM and network bands

diagnose_network_issue(msisdn: str, location: str) -> {coverage: str, issues: List}
# Check network coverage and known issues in area

reissue_esim_profile(customer_id: str) -> {qr_code_sent: bool, sms_sent: bool}
# Generate and send new eSIM activation QR code

reset_network_settings(customer_id: str) -> {reset_initiated: bool}
# Remotely trigger network settings reset

create_technical_ticket(customer_id: str, issue: str) -> {ticket_id: str}
# Create ticket for field technician visit
```

### 📱 PlanAgent Tools  
```python
get_current_plan(customer_id: str) -> {plan_name: str, data_gb: int, price: float}
# Get customer's current plan details

list_available_plans(customer_type: str) -> {plans: List[dict]}
# List all available plans for customer type

calculate_plan_cost(plan_id: str, addons: List) -> {monthly: float, total: float}
# Calculate total cost with taxes and fees

change_plan(customer_id: str, new_plan_id: str) -> {success: bool, effective_date: str}
# Change customer's plan

add_addon_package(customer_id: str, addon_id: str) -> {success: bool}
# Add extra data/minutes/roaming package

check_upgrade_eligibility(customer_id: str) -> {eligible: bool, options: List}
# Check if customer eligible for device/plan upgrade
```

### 💰 BillingAgent Tools
```python
get_current_bill(customer_id: str) -> {amount: float, due_date: str, items: List}
# Get current month's bill details

get_billing_history(customer_id: str, months: int) -> {bills: List[dict]}
# Get billing history for specified months

explain_charges(bill_id: str, charge_type: str) -> {explanation: str, breakdown: dict}
# Explain specific charges on bill

apply_discount(customer_id: str, discount_code: str) -> {success: bool, amount: float}
# Apply promotional discount to account

setup_payment_plan(customer_id: str, installments: int) -> {plan_id: str, monthly: float}
# Setup installment payment plan

process_refund(customer_id: str, amount: float, reason: str) -> {refund_id: str}
# Process refund for overcharge or error
```

### ❓ FAQAgent Tools
```python
search_knowledge_base(query: str) -> {articles: List[dict], top_match: str}
# Search help articles and FAQs

get_faq_answer(faq_id: str) -> {question: str, answer: str, related: List}
# Get specific FAQ with related articles

send_instructions_sms(customer_id: str, instruction_type: str) -> {sent: bool}
# Send setup/troubleshooting instructions via SMS

create_general_ticket(customer_id: str, issue: str) -> {ticket_id: str}
# Create general support ticket

check_service_status() -> {services: dict, maintenance: List}
# Check system-wide service status
```

### 🔀 Shared System Tools (All Agents)
```python
transfer_to_human(reason: str, priority: str) -> {queue_position: int, wait_time: int}
# Escalate to human agent when needed

schedule_callback(customer_id: str, datetime: str) -> {callback_id: str}
# Schedule follow-up call

update_customer_notes(customer_id: str, notes: str) -> {success: bool}
# Add notes to customer profile

log_interaction(customer_id: str, summary: str, resolution: str) -> {log_id: str}
# Log conversation for quality and training
```

## Tool Usage Rules

1. **Identity Verification**: Always use `verify_user` before any sensitive operations
2. **Tool Chaining**: Some tools naturally chain (e.g., `check_esim_status` → `reissue_esim_profile`)
3. **Error Handling**: All tools return success/failure status
4. **Logging**: Always use `log_interaction` at conversation end
5. **Escalation**: Use `transfer_to_human` when:
   - Customer explicitly requests human agent
   - Issue cannot be resolved with available tools
   - Customer is very frustrated (3+ negative turns)

## Implementation Priority

### Phase 1 (Must Have - Competition MVP)
- verify_user
- check_esim_status
- reissue_esim_profile
- get_current_plan
- list_available_plans
- transfer_to_human

### Phase 2 (Should Have)
- get_current_bill
- search_knowledge_base
- create_technical_ticket
- change_plan

### Phase 3 (Nice to Have)
- All remaining tools

## Dataset Generation Guidelines

When generating synthetic conversations:
1. Use ONLY tools from this specification
2. Use exact tool names and parameters
3. Include realistic tool responses
4. Show tool failures occasionally (20% rate)
5. Chain tools logically based on context
6. Each conversation should use 2-5 different tools
7. RouterAgent always uses verify_user first
8. Specialized agents use their domain tools

## Example Tool Sequences

### eSIM Activation Issue
1. RouterAgent: verify_user → get_customer_profile → route_to_agent
2. TechAgent: check_esim_status → check_device_compatibility → reissue_esim_profile

### Billing Complaint  
1. RouterAgent: verify_user → check_recent_tickets → route_to_agent
2. BillingAgent: get_current_bill → explain_charges → apply_discount

### Plan Upgrade
1. RouterAgent: verify_user → route_to_agent
2. PlanAgent: get_current_plan → check_upgrade_eligibility → list_available_plans → calculate_plan_cost → change_plan

This specification is FINAL for the competition. All generated datasets must conform to these tools.