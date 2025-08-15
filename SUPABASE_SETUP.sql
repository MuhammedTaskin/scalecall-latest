-- 🚀 TEKNOFEST 2025 - SUPABASE DATABASE SCHEMA
-- Complete schema for agents, tools, and conversations

-- ============= 1. AGENTS TABLE =============
CREATE TABLE IF NOT EXISTS agents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    priority INTEGER DEFAULT 0,
    capabilities JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert 5 agents
INSERT INTO agents (name, description, priority, capabilities) VALUES
('RouterAgent', 'Initial routing and emotion detection agent', 100, '{"routing": true, "emotion_detection": true}'),
('TechAgent', 'Technical support and troubleshooting', 90, '{"technical": true, "diagnostics": true}'),
('BillingAgent', 'Billing and payment queries', 80, '{"billing": true, "payments": true}'),
('PlanAgent', 'Package and plan recommendations', 70, '{"plans": true, "recommendations": true}'),
('FAQAgent', 'General questions and information', 60, '{"faq": true, "knowledge_base": true}');

-- ============= 2. TOOLS TABLE =============
CREATE TABLE IF NOT EXISTS tools (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    parameters JSONB,
    returns JSONB,
    implementation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert 21 telco tools
INSERT INTO tools (name, category, description, parameters, returns) VALUES
-- Customer Operations (3 tools)
('verify_customer_identity', 'customer', 'Verify customer identity with security questions', 
 '{"customer_id": "string", "security_answers": "object"}', 
 '{"verified": "boolean", "confidence": "number"}'),

('check_customer_profile', 'customer', 'Get customer profile and history',
 '{"customer_id": "string"}',
 '{"profile": "object", "history": "array"}'),

('update_customer_information', 'customer', 'Update customer contact details',
 '{"customer_id": "string", "updates": "object"}',
 '{"success": "boolean", "updated_fields": "array"}'),

-- Technical Support (4 tools)
('check_device_compatibility', 'technical', 'Check if device supports eSIM',
 '{"imei": "string", "device_model": "string"}',
 '{"compatible": "boolean", "requirements": "array"}'),

('troubleshoot_connection', 'technical', 'Diagnose connection issues',
 '{"customer_id": "string", "issue_type": "string"}',
 '{"diagnosis": "object", "solutions": "array"}'),

('run_network_diagnostics', 'technical', 'Run network diagnostics',
 '{"location": "string", "network_type": "string"}',
 '{"signal_strength": "number", "network_status": "string"}'),

('check_coverage_area', 'technical', 'Check network coverage for location',
 '{"address": "string", "coordinates": "object"}',
 '{"coverage": "object", "quality": "string"}'),

-- Billing & Payments (4 tools)
('get_current_balance', 'billing', 'Get customer current balance',
 '{"customer_id": "string"}',
 '{"balance": "number", "currency": "string"}'),

('view_invoice_details', 'billing', 'Get detailed invoice information',
 '{"customer_id": "string", "invoice_id": "string"}',
 '{"invoice": "object", "items": "array"}'),

('process_payment', 'billing', 'Process customer payment',
 '{"customer_id": "string", "amount": "number", "method": "string"}',
 '{"transaction_id": "string", "status": "string"}'),

('setup_auto_payment', 'billing', 'Setup automatic payment',
 '{"customer_id": "string", "payment_method": "object"}',
 '{"auto_pay_id": "string", "active": "boolean"}'),

-- Plan Management (4 tools)
('list_available_packages', 'plan', 'List all available packages',
 '{"customer_type": "string", "usage_profile": "string"}',
 '{"packages": "array", "recommendations": "array"}'),

('change_current_plan', 'plan', 'Change customer plan',
 '{"customer_id": "string", "new_plan_id": "string"}',
 '{"success": "boolean", "effective_date": "string"}'),

('add_international_roaming', 'plan', 'Add international roaming package',
 '{"customer_id": "string", "countries": "array", "duration": "number"}',
 '{"roaming_id": "string", "cost": "number"}'),

('calculate_plan_cost', 'plan', 'Calculate plan cost with options',
 '{"plan_id": "string", "options": "array"}',
 '{"monthly_cost": "number", "setup_fee": "number"}'),

-- eSIM Operations (5 tools)
('issue_lpa_code', 'esim', 'Generate LPA code for eSIM',
 '{"customer_id": "string", "device_info": "object"}',
 '{"lpa_code": "string", "qr_code": "string"}'),

('activate_esim', 'esim', 'Activate eSIM profile',
 '{"lpa_code": "string", "confirmation_code": "string"}',
 '{"activated": "boolean", "profile_id": "string"}'),

('check_esim_status', 'esim', 'Check eSIM activation status',
 '{"profile_id": "string"}',
 '{"status": "string", "active_since": "string"}'),

('transfer_number_to_esim', 'esim', 'Transfer existing number to eSIM',
 '{"phone_number": "string", "esim_profile_id": "string"}',
 '{"transferred": "boolean", "completion_time": "string"}'),

('deactivate_esim', 'esim', 'Deactivate eSIM profile',
 '{"profile_id": "string", "reason": "string"}',
 '{"deactivated": "boolean", "timestamp": "string"}'),

-- Support (1 tool)
('create_support_ticket', 'support', 'Create priority support ticket',
 '{"customer_id": "string", "issue": "string", "priority": "string"}',
 '{"ticket_id": "string", "estimated_resolution": "string"}');

-- ============= 3. AGENT_TOOLS MAPPING =============
CREATE TABLE IF NOT EXISTS agent_tools (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    agent_id UUID REFERENCES agents(id),
    tool_id UUID REFERENCES tools(id),
    priority INTEGER DEFAULT 0,
    UNIQUE(agent_id, tool_id)
);

-- Map tools to agents
INSERT INTO agent_tools (agent_id, tool_id, priority)
SELECT 
    a.id as agent_id,
    t.id as tool_id,
    CASE 
        WHEN a.name = 'RouterAgent' AND t.category IN ('customer', 'support') THEN 100
        WHEN a.name = 'TechAgent' AND t.category = 'technical' THEN 100
        WHEN a.name = 'BillingAgent' AND t.category = 'billing' THEN 100
        WHEN a.name = 'PlanAgent' AND t.category = 'plan' THEN 100
        WHEN a.name = 'FAQAgent' AND t.category IN ('customer', 'plan') THEN 80
        ELSE 50
    END as priority
FROM agents a
CROSS JOIN tools t
WHERE 
    (a.name = 'RouterAgent' AND t.category IN ('customer', 'support')) OR
    (a.name = 'TechAgent' AND t.category IN ('technical', 'esim')) OR
    (a.name = 'BillingAgent' AND t.category = 'billing') OR
    (a.name = 'PlanAgent' AND t.category IN ('plan', 'billing')) OR
    (a.name = 'FAQAgent' AND t.category IN ('customer', 'plan', 'support'));

-- ============= 4. CONVERSATIONS TABLE =============
CREATE TABLE IF NOT EXISTS conversations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    customer_id VARCHAR(100),
    emotion VARCHAR(50),
    initial_query TEXT,
    agent_id UUID REFERENCES agents(id),
    tools_used JSONB,
    response TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============= 5. TOOL EXECUTIONS TABLE =============
CREATE TABLE IF NOT EXISTS tool_executions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    tool_id UUID REFERENCES tools(id),
    input_params JSONB,
    output_result JSONB,
    execution_time_ms INTEGER,
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============= 6. EMOTIONS TABLE =============
CREATE TABLE IF NOT EXISTS emotions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    arousal VARCHAR(20),
    valence VARCHAR(20),
    response_tone TEXT,
    priority INTEGER DEFAULT 0
);

INSERT INTO emotions (name, arousal, valence, response_tone, priority) VALUES
('angry', 'high', 'negative', 'understanding and calm', 100),
('frustrated', 'high', 'negative', 'patient and solution-focused', 90),
('confused', 'medium', 'negative', 'clear and step-by-step', 80),
('worried', 'medium', 'negative', 'reassuring and supportive', 80),
('sad', 'low', 'negative', 'empathetic and helpful', 70),
('neutral', 'medium', 'neutral', 'professional and efficient', 50),
('happy', 'high', 'positive', 'cheerful and engaging', 40),
('excited', 'high', 'positive', 'enthusiastic and positive', 30),
('satisfied', 'low', 'positive', 'appreciative and warm', 20);

-- ============= 7. INDEXES FOR PERFORMANCE =============
CREATE INDEX idx_conversations_customer ON conversations(customer_id);
CREATE INDEX idx_conversations_emotion ON conversations(emotion);
CREATE INDEX idx_conversations_agent ON conversations(agent_id);
CREATE INDEX idx_tool_executions_conversation ON tool_executions(conversation_id);
CREATE INDEX idx_tool_executions_tool ON tool_executions(tool_id);

-- ============= 8. RLS POLICIES =============
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE tools ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE tool_executions ENABLE ROW LEVEL SECURITY;

-- Public read access for agents and tools
CREATE POLICY "Public agents read" ON agents FOR SELECT USING (true);
CREATE POLICY "Public tools read" ON tools FOR SELECT USING (true);

-- Authenticated access for conversations
CREATE POLICY "Users can read own conversations" ON conversations 
    FOR SELECT USING (auth.uid()::text = customer_id);

CREATE POLICY "Users can create conversations" ON conversations 
    FOR INSERT WITH CHECK (auth.uid()::text = customer_id);

-- ============= 9. FUNCTIONS =============
-- Function to get best agent for query
CREATE OR REPLACE FUNCTION get_best_agent(
    p_emotion VARCHAR,
    p_query TEXT
) RETURNS UUID AS $$
DECLARE
    v_agent_id UUID;
BEGIN
    -- Logic to select best agent based on emotion and query
    SELECT a.id INTO v_agent_id
    FROM agents a
    WHERE 
        CASE 
            WHEN p_emotion IN ('angry', 'frustrated') THEN a.name = 'RouterAgent'
            WHEN p_query ILIKE '%fatura%' OR p_query ILIKE '%ödeme%' THEN a.name = 'BillingAgent'
            WHEN p_query ILIKE '%internet%' OR p_query ILIKE '%bağlantı%' THEN a.name = 'TechAgent'
            WHEN p_query ILIKE '%paket%' OR p_query ILIKE '%tarife%' THEN a.name = 'PlanAgent'
            WHEN p_query ILIKE '%esim%' THEN a.name = 'TechAgent'
            ELSE a.name = 'FAQAgent'
        END
    LIMIT 1;
    
    RETURN v_agent_id;
END;
$$ LANGUAGE plpgsql;

-- Function to get tools for agent
CREATE OR REPLACE FUNCTION get_agent_tools(p_agent_id UUID)
RETURNS TABLE(tool_name VARCHAR, tool_category VARCHAR, tool_params JSONB) AS $$
BEGIN
    RETURN QUERY
    SELECT t.name, t.category, t.parameters
    FROM tools t
    JOIN agent_tools at ON t.id = at.tool_id
    WHERE at.agent_id = p_agent_id
    ORDER BY at.priority DESC;
END;
$$ LANGUAGE plpgsql;

-- ============= 10. VIEWS =============
-- View for conversation analytics
CREATE VIEW conversation_analytics AS
SELECT 
    DATE(created_at) as date,
    emotion,
    COUNT(*) as count,
    AVG(COALESCE((metadata->>'response_time_ms')::INTEGER, 0)) as avg_response_time
FROM conversations
GROUP BY DATE(created_at), emotion;

-- View for tool usage
CREATE VIEW tool_usage_stats AS
SELECT 
    t.name as tool_name,
    t.category,
    COUNT(te.id) as usage_count,
    AVG(te.execution_time_ms) as avg_execution_time,
    SUM(CASE WHEN te.success THEN 1 ELSE 0 END)::FLOAT / COUNT(*)::FLOAT as success_rate
FROM tools t
LEFT JOIN tool_executions te ON t.id = te.tool_id
GROUP BY t.id, t.name, t.category;