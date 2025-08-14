-- Create telecom system tables for customer data
-- This migration creates the core tables needed for the e-SIM call center system

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    msisdn TEXT UNIQUE NOT NULL,
    maiden_name TEXT NOT NULL,
    birth_date DATE,
    id_last_4 TEXT,
    contract_end DATE,
    payment_status TEXT DEFAULT 'active',
    device_imei TEXT,
    activation_status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Packages table
CREATE TABLE IF NOT EXISTS packages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    package_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    data_gb INTEGER,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Customer packages (current subscription)
CREATE TABLE IF NOT EXISTS customer_packages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id TEXT NOT NULL REFERENCES customers(customer_id),
    package_id TEXT NOT NULL REFERENCES packages(package_id),
    start_date TIMESTAMPTZ DEFAULT NOW(),
    end_date TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- eSIM profiles
CREATE TABLE IF NOT EXISTS esim_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    esim_id TEXT UNIQUE NOT NULL,
    customer_id TEXT NOT NULL REFERENCES customers(customer_id),
    activation_code TEXT,
    status TEXT DEFAULT 'pending', -- pending, active, suspended, cancelled
    device_brand TEXT,
    device_model TEXT,
    os_type TEXT, -- iOS, Android
    created_at TIMESTAMPTZ DEFAULT NOW(),
    activated_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ
);

-- Support tickets
CREATE TABLE IF NOT EXISTS support_tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id TEXT UNIQUE NOT NULL,
    customer_id TEXT NOT NULL REFERENCES customers(customer_id),
    issue_type TEXT NOT NULL, -- technical, billing, complaint, request, activation
    description TEXT NOT NULL,
    status TEXT DEFAULT 'open', -- open, in_progress, resolved, closed
    priority TEXT DEFAULT 'medium', -- low, medium, high, urgent
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

-- Device compatibility
CREATE TABLE IF NOT EXISTS device_compatibility (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    imei TEXT UNIQUE NOT NULL,
    brand TEXT,
    model TEXT,
    esim_supported BOOLEAN DEFAULT false,
    registered BOOLEAN DEFAULT false,
    last_checked TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE packages ENABLE ROW LEVEL SECURITY;
ALTER TABLE customer_packages ENABLE ROW LEVEL SECURITY;
ALTER TABLE esim_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE support_tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE device_compatibility ENABLE ROW LEVEL SECURITY;

-- RLS Policies for customers (admin access for call center)
CREATE POLICY "Allow admin access to customers" ON customers
    FOR ALL USING (true); -- Call center agents need full access

CREATE POLICY "Allow admin access to packages" ON packages
    FOR ALL USING (true);

CREATE POLICY "Allow admin access to customer_packages" ON customer_packages
    FOR ALL USING (true);

CREATE POLICY "Allow admin access to esim_profiles" ON esim_profiles
    FOR ALL USING (true);

CREATE POLICY "Allow admin access to support_tickets" ON support_tickets
    FOR ALL USING (true);

CREATE POLICY "Allow admin access to device_compatibility" ON device_compatibility
    FOR ALL USING (true);

-- Insert sample data matching the example dialogs
INSERT INTO customers (customer_id, name, msisdn, maiden_name, birth_date, id_last_4, contract_end, payment_status, device_imei, activation_status) VALUES
('12345', 'Ali Doğan', '05551234567', 'Kaya', '1985-05-15', '1234', '2024-12-31', 'active', '359111222333444', 'active'),
('67890', 'Fatma Demir', '05556789012', 'Demir', '1990-12-03', '5678', '2024-11-30', 'active', '357999123456789', 'pending'),
('11223', 'Elif Yıldız', '05551122334', 'Yıldız', '1988-08-20', '9012', '2024-12-31', 'active', '359888777666555', 'active'),
('44556', 'Mehmet Kaya', '05554455667', 'Kaya', '1992-03-10', '3456', '2024-11-30', 'active', '357999123456789', 'failed'),
('78901', 'Zeynep Koç', '05557890123', 'Koç', '1987-11-25', '7890', '2024-12-31', 'active', '359123456789012', 'failed')
ON CONFLICT (customer_id) DO NOTHING;

-- Insert package data
INSERT INTO packages (package_id, name, price, data_gb, description) VALUES
('basic_5gb', 'Temel 5GB', 99.99, 5, 'Aylık 5GB internet paketi'),
('premium_10gb', 'Premium 10GB', 149.99, 10, 'Aylık 10GB internet paketi'),
('family_20gb', 'Aile 20GB', 199.99, 20, 'Aile için 20GB paylaşımlı paket'),
('unlimited', 'Sınırsız', 299.99, -1, 'Sınırsız internet paketi')
ON CONFLICT (package_id) DO NOTHING;

-- Insert customer package assignments
INSERT INTO customer_packages (customer_id, package_id) VALUES
('12345', 'premium_10gb'),
('67890', 'basic_5gb'),
('11223', 'family_20gb'),
('44556', 'basic_5gb'),
('78901', 'premium_10gb')
ON CONFLICT DO NOTHING;

-- Insert eSIM profiles
INSERT INTO esim_profiles (esim_id, customer_id, activation_code, status, device_brand, device_model, os_type, expires_at) VALUES
('esim_12345_001', '12345', 'LPA:1$sp$D046-AB12', 'active', 'Apple', 'iPhone 15', 'iOS', '2024-12-31'),
('esim_67890_001', '67890', 'LPA:1$sp$D047-ZX90', 'pending', 'Samsung', 'Galaxy S23', 'Android', '2024-11-30'),
('esim_11223_001', '11223', 'LPA:1$sp$D048-NEW1', 'active', 'Google', 'Pixel 8', 'Android', '2024-12-31'),
('esim_44556_001', '44556', 'LPA:1$sp$D049-ERR1', 'failed', 'Unknown', 'Unknown', 'Unknown', '2024-11-30'),
('esim_78901_001', '78901', 'LPA:1$sp$D050-OK23', 'failed', 'Apple', 'iPhone 14', 'iOS', '2024-12-31')
ON CONFLICT (esim_id) DO NOTHING;

-- Insert device compatibility data
INSERT INTO device_compatibility (imei, brand, model, esim_supported, registered) VALUES
('359111222333444', 'Apple', 'iPhone 15', true, true),
('357999123456789', 'Samsung', 'Galaxy S23', true, true),
('359888777666555', 'Google', 'Pixel 8', true, true),
('359123456789012', 'Apple', 'iPhone 14', true, true),
('123456789012345', 'Unknown', 'Unsupported', false, false)
ON CONFLICT (imei) DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_customers_msisdn ON customers(msisdn);
CREATE INDEX IF NOT EXISTS idx_customers_customer_id ON customers(customer_id);
CREATE INDEX IF NOT EXISTS idx_esim_profiles_customer_id ON esim_profiles(customer_id);
CREATE INDEX IF NOT EXISTS idx_device_compatibility_imei ON device_compatibility(imei);
CREATE INDEX IF NOT EXISTS idx_support_tickets_customer_id ON support_tickets(customer_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at triggers
CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
