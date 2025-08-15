# Simplified Telco Tools - Database Ready
## Tools that can actually be implemented with real data

### 🔄 RouterAgent Tools
```python
verify_user(msisdn: str, maiden_name: str) -> {verified: bool, customer_id: str}
# Simple DB lookup: customers table

get_customer_status(customer_id: str) -> {active: bool, plan_type: str, has_issues: bool}
# Simple DB lookup: customers table

route_to_agent(agent_type: str, reason: str) -> {routed: bool}
# Just logs the routing decision
```

### 🔧 TechAgent Tools
```python
check_esim_status(customer_id: str) -> {status: str, activation_date: str, error_code: str}
# Simple DB lookup: esim_activations table

check_device_imei(imei: str) -> {registered: bool, compatible: bool, model: str}
# Simple DB lookup: devices table

reissue_activation_code(customer_id: str) -> {new_code: str, sms_sent: bool}
# DB update: esim_activations table + generate code

create_tech_ticket(customer_id: str, issue_type: str) -> {ticket_id: str}
# DB insert: tickets table
```

### 📱 PlanAgent Tools
```python
get_customer_plan(customer_id: str) -> {plan_id: str, monthly_price: float, data_gb: int}
# Simple DB lookup: customer_plans table

list_all_plans() -> {plans: List[{id, name, price, data_gb}]}
# Simple DB lookup: plans_catalog table

change_customer_plan(customer_id: str, new_plan_id: str) -> {changed: bool, effective_date: str}
# DB update: customer_plans table

check_plan_compatibility(customer_id: str, plan_id: str) -> {compatible: bool, reason: str}
# Simple business logic check
```

### 💰 BillingAgent Tools
```python
get_last_bill(customer_id: str) -> {amount: float, paid: bool, due_date: str}
# Simple DB lookup: bills table

get_unpaid_amount(customer_id: str) -> {total: float, overdue: bool}
# DB query: bills table WHERE paid=false

apply_campaign_discount(customer_id: str, campaign_code: str) -> {applied: bool, discount_amount: float}
# DB lookup + update: campaigns table + bills table

create_payment_note(customer_id: str, note: str) -> {noted: bool}
# DB insert: customer_notes table
```

### ❓ FAQAgent Tools
```python
search_faq(keyword: str) -> {results: List[{question, answer}]}
# Simple DB search: faq table

get_common_solutions(issue_type: str) -> {solutions: List[str]}
# DB lookup: solutions table by category

send_help_sms(customer_id: str, template_id: str) -> {sent: bool}
# DB lookup: sms_templates + log to sms_history

create_info_ticket(customer_id: str, question: str) -> {ticket_id: str}
# DB insert: tickets table
```

### 🔀 Shared Tools (All Agents)
```python
escalate_to_human(reason: str) -> {escalated: bool}
# Simple flag/log

end_conversation(resolution: str) -> {ended: bool}
# Log the resolution
```

## Database Tables Needed

### customers
- customer_id (PK)
- msisdn (phone)
- name
- maiden_name
- plan_id
- status (active/suspended/cancelled)
- created_at

### esim_activations
- activation_id (PK)
- customer_id (FK)
- status (pending/active/failed)
- activation_code
- error_code
- created_at
- activated_at

### devices
- imei (PK)
- model
- manufacturer
- esim_compatible (bool)
- bands_supported (text)

### plans_catalog
- plan_id (PK)
- name
- monthly_price
- data_gb
- minutes
- sms_count
- active (bool)

### customer_plans
- customer_id (FK)
- plan_id (FK)
- start_date
- end_date
- status

### bills
- bill_id (PK)
- customer_id (FK)
- amount
- due_date
- paid (bool)
- paid_date
- month

### tickets
- ticket_id (PK)
- customer_id (FK)
- type (tech/billing/info)
- description
- status (open/closed)
- created_at

### faq
- faq_id (PK)
- category
- question
- answer
- keywords

### campaigns
- campaign_code (PK)
- discount_percent
- valid_until
- max_uses

### sms_templates
- template_id (PK)
- category
- content
- placeholders

## Example Tool Usage in Conversations

### eSIM Issue Flow
```python
# RouterAgent
verify_user("05551234567", "Yıldız") -> {verified: true, customer_id: "12345"}
get_customer_status("12345") -> {active: true, plan_type: "premium", has_issues: true}
route_to_agent("TechAgent", "esim_issue") -> {routed: true}

# TechAgent  
check_esim_status("12345") -> {status: "failed", activation_date: null, error_code: "E001"}
check_device_imei("359111222333444") -> {registered: true, compatible: true, model: "iPhone 15"}
reissue_activation_code("12345") -> {new_code: "QR123ABC", sms_sent: true}
```

### Billing Issue Flow
```python
# RouterAgent
verify_user("05556789012", "Demir") -> {verified: true, customer_id: "67890"}
route_to_agent("BillingAgent", "payment_issue") -> {routed: true}

# BillingAgent
get_last_bill("67890") -> {amount: 250.00, paid: false, due_date: "2024-01-15"}
get_unpaid_amount("67890") -> {total: 250.00, overdue: true}
apply_campaign_discount("67890", "WINTER25") -> {applied: true, discount_amount: 50.00}
```

## Implementation Notes

1. All tools do SIMPLE database operations
2. No complex calculations or diagnostics
3. Each tool maps to 1-2 DB queries max
4. Easy to mock for testing
5. Easy to generate synthetic data for training
6. Response formats are simple JSON
7. Tools can fail gracefully (return null/false)

## Why These Tools Work

✅ **Simple to implement**: Just DB queries
✅ **Easy to generate data**: We can create realistic customer/plan/bill data
✅ **Predictable responses**: Clear success/failure states
✅ **Real-world relevant**: These are actual telco operations
✅ **Training friendly**: Model can learn when to use each tool
✅ **Database ready**: Can be implemented with SQLite/PostgreSQL/Supabase immediately