#!/usr/bin/env python3
"""
TEKNOFEST 2025 - ENTERPRISE DATABASE CONFIGURATION
Production Database Management System
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
import hashlib
import os

class EnterpriseDatabase:
    """Production-grade SQLite database for telecommunications platform"""
    
    def __init__(self, db_path: str = "telco_production.db"):
        self.db_path = db_path
        self.conn = None
        self.initialize_database()
    
    def initialize_database(self):
        """Initialize production database with all required tables"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        # Customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT PRIMARY KEY,
                phone_number TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT,
                account_status TEXT DEFAULT 'active',
                account_tier TEXT DEFAULT 'standard',
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Account balances table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS account_balances (
                balance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                current_balance REAL DEFAULT 0.0,
                credit_limit REAL DEFAULT 1000.0,
                last_payment_date TIMESTAMP,
                payment_status TEXT DEFAULT 'current',
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )
        """)
        
        # Subscription plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscription_plans (
                plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                plan_name TEXT NOT NULL,
                plan_type TEXT NOT NULL,
                data_limit_gb INTEGER,
                minutes_limit INTEGER,
                sms_limit INTEGER,
                monthly_fee REAL,
                activation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expiry_date TIMESTAMP,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )
        """)
        
        # Data usage tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_usage (
                usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                billing_period TEXT NOT NULL,
                data_used_gb REAL DEFAULT 0.0,
                data_remaining_gb REAL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )
        """)
        
        # eSIM management table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS esim_profiles (
                esim_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                iccid TEXT UNIQUE,
                activation_code TEXT UNIQUE,
                device_model TEXT,
                activation_status TEXT DEFAULT 'pending',
                activation_date TIMESTAMP,
                qr_code_data TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )
        """)
        
        # Support tickets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS support_tickets (
                ticket_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                issue_category TEXT NOT NULL,
                priority TEXT DEFAULT 'normal',
                status TEXT DEFAULT 'open',
                description TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_date TIMESTAMP,
                assigned_to TEXT,
                resolution TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )
        """)
        
        # Payment transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payment_transactions (
                transaction_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                amount REAL NOT NULL,
                payment_method TEXT,
                transaction_type TEXT,
                status TEXT DEFAULT 'pending',
                transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reference_number TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )
        """)
        
        # Network diagnostics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS network_diagnostics (
                diagnostic_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                signal_strength INTEGER,
                network_type TEXT,
                latency_ms INTEGER,
                packet_loss REAL,
                diagnostic_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                location TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )
        """)
        
        # AI interaction logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_interactions (
                interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT,
                session_id TEXT,
                request_text TEXT,
                detected_emotion TEXT,
                tools_executed TEXT,
                response_text TEXT,
                model_used TEXT,
                processing_time_ms INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Device compatibility table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_compatibility (
                device_id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_brand TEXT NOT NULL,
                device_model TEXT NOT NULL,
                esim_compatible BOOLEAN DEFAULT 0,
                network_5g BOOLEAN DEFAULT 0,
                network_4g BOOLEAN DEFAULT 1,
                volte_support BOOLEAN DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
        self._seed_initial_data()
    
    def _seed_initial_data(self):
        """Seed database with initial production data"""
        cursor = self.conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM customers")
        if cursor.fetchone()[0] > 0:
            return
        
        # Seed customers
        customers = [
            ("CUST001", "5551234567", "Ahmet Yılmaz", "ahmet.yilmaz@email.com", "active", "premium"),
            ("CUST002", "5559876543", "Ayşe Demir", "ayse.demir@email.com", "active", "standard"),
            ("CUST003", "5555555555", "Mehmet Kaya", "mehmet.kaya@email.com", "suspended", "basic"),
            ("CUST004", "5552223344", "Fatma Özkan", "fatma.ozkan@email.com", "active", "premium"),
            ("CUST005", "5556667788", "Ali Çelik", "ali.celik@email.com", "active", "standard")
        ]
        
        for customer in customers:
            cursor.execute("""
                INSERT INTO customers (customer_id, phone_number, full_name, email, account_status, account_tier)
                VALUES (?, ?, ?, ?, ?, ?)
            """, customer)
        
        # Seed account balances
        balances = [
            ("CUST001", 250.50, 2000.0, "2025-01-01", "current"),
            ("CUST002", -45.00, 1000.0, "2024-12-15", "overdue"),
            ("CUST003", 0.00, 500.0, "2024-11-30", "suspended"),
            ("CUST004", 500.00, 3000.0, "2025-01-10", "current"),
            ("CUST005", 125.75, 1500.0, "2025-01-05", "current")
        ]
        
        for balance in balances:
            cursor.execute("""
                INSERT INTO account_balances (customer_id, current_balance, credit_limit, last_payment_date, payment_status)
                VALUES (?, ?, ?, ?, ?)
            """, balance)
        
        # Seed subscription plans
        plans = [
            ("CUST001", "Premium Unlimited", "postpaid", 200, -1, 5000, 399.99),
            ("CUST002", "Standard 50GB", "postpaid", 50, 1000, 1000, 199.99),
            ("CUST003", "Basic 25GB", "prepaid", 25, 500, 500, 99.99),
            ("CUST004", "Premium Plus", "postpaid", 500, -1, -1, 599.99),
            ("CUST005", "Standard 100GB", "postpaid", 100, 2000, 2000, 299.99)
        ]
        
        for plan in plans:
            cursor.execute("""
                INSERT INTO subscription_plans (customer_id, plan_name, plan_type, data_limit_gb, minutes_limit, sms_limit, monthly_fee)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, plan)
        
        # Seed data usage
        usage = [
            ("CUST001", "2025-01", 45.7, 154.3),
            ("CUST002", "2025-01", 38.2, 11.8),
            ("CUST003", "2025-01", 24.9, 0.1),
            ("CUST004", "2025-01", 127.3, 372.7),
            ("CUST005", "2025-01", 67.8, 32.2)
        ]
        
        for use in usage:
            cursor.execute("""
                INSERT INTO data_usage (customer_id, billing_period, data_used_gb, data_remaining_gb)
                VALUES (?, ?, ?, ?)
            """, use)
        
        # Seed device compatibility
        devices = [
            ("Apple", "iPhone 15 Pro", 1, 1, 1, 1),
            ("Apple", "iPhone 14", 1, 1, 1, 1),
            ("Samsung", "Galaxy S24 Ultra", 1, 1, 1, 1),
            ("Samsung", "Galaxy S23", 1, 1, 1, 1),
            ("Xiaomi", "13 Pro", 1, 1, 1, 1),
            ("Nokia", "3310", 0, 0, 0, 0),
            ("Google", "Pixel 8 Pro", 1, 1, 1, 1)
        ]
        
        for device in devices:
            cursor.execute("""
                INSERT INTO device_compatibility (device_brand, device_model, esim_compatible, network_5g, network_4g, volte_support)
                VALUES (?, ?, ?, ?, ?, ?)
            """, device)
        
        self.conn.commit()
    
    def get_customer(self, phone: str) -> Optional[Dict]:
        """Retrieve customer information"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.*, ab.current_balance, ab.payment_status, sp.plan_name
            FROM customers c
            LEFT JOIN account_balances ab ON c.customer_id = ab.customer_id
            LEFT JOIN subscription_plans sp ON c.customer_id = sp.customer_id
            WHERE c.phone_number = ? AND sp.status = 'active'
        """, (phone,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_balance(self, customer_id: str) -> Optional[Dict]:
        """Get customer balance information"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT current_balance, credit_limit, payment_status, last_payment_date
            FROM account_balances
            WHERE customer_id = ?
        """, (customer_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_data_usage(self, customer_id: str) -> Optional[Dict]:
        """Get current data usage"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT data_used_gb, data_remaining_gb, billing_period, last_updated
            FROM data_usage
            WHERE customer_id = ?
            ORDER BY last_updated DESC
            LIMIT 1
        """, (customer_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def create_support_ticket(self, customer_id: str, issue: str, priority: str = "normal") -> str:
        """Create new support ticket"""
        ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{hashlib.md5(customer_id.encode()).hexdigest()[:6].upper()}"
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO support_tickets (ticket_id, customer_id, issue_category, priority, description)
            VALUES (?, ?, ?, ?, ?)
        """, (ticket_id, customer_id, "general", priority, issue))
        
        self.conn.commit()
        return ticket_id
    
    def log_ai_interaction(self, interaction_data: Dict):
        """Log AI interaction for analytics"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO ai_interactions (
                customer_id, session_id, request_text, detected_emotion,
                tools_executed, response_text, model_used, processing_time_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            interaction_data.get("customer_id"),
            interaction_data.get("session_id"),
            interaction_data.get("request_text"),
            interaction_data.get("emotion"),
            json.dumps(interaction_data.get("tools_executed", [])),
            interaction_data.get("response_text"),
            interaction_data.get("model_used"),
            interaction_data.get("processing_time_ms")
        ))
        
        self.conn.commit()
    
    def check_device_compatibility(self, device_model: str) -> Optional[Dict]:
        """Check device compatibility for eSIM and networks"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM device_compatibility
            WHERE LOWER(device_model) LIKE LOWER(?)
            LIMIT 1
        """, (f"%{device_model}%",))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_payment_history(self, customer_id: str, limit: int = 10) -> List[Dict]:
        """Get payment transaction history"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT transaction_id, amount, payment_method, status, transaction_date
            FROM payment_transactions
            WHERE customer_id = ?
            ORDER BY transaction_date DESC
            LIMIT ?
        """, (customer_id, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def create_esim_profile(self, customer_id: str, device_model: str) -> Dict:
        """Create new eSIM profile"""
        iccid = f"898600{datetime.now().strftime('%Y%m%d%H%M%S')}"
        activation_code = f"ESIM-{hashlib.sha256(f'{customer_id}{datetime.now()}'.encode()).hexdigest()[:12].upper()}"
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO esim_profiles (customer_id, iccid, activation_code, device_model, activation_status)
            VALUES (?, ?, ?, ?, 'pending')
        """, (customer_id, iccid, activation_code, device_model))
        
        self.conn.commit()
        
        return {
            "iccid": iccid,
            "activation_code": activation_code,
            "status": "pending"
        }
    
    def get_network_diagnostics(self, customer_id: str) -> Optional[Dict]:
        """Get latest network diagnostic data"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT signal_strength, network_type, latency_ms, packet_loss, diagnostic_date
            FROM network_diagnostics
            WHERE customer_id = ?
            ORDER BY diagnostic_date DESC
            LIMIT 1
        """, (customer_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        
        # Return mock diagnostic if no data
        return {
            "signal_strength": -65,
            "network_type": "5G",
            "latency_ms": 12,
            "packet_loss": 0.01,
            "diagnostic_date": datetime.now().isoformat()
        }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

# Database singleton instance
_db_instance = None

def get_database() -> EnterpriseDatabase:
    """Get or create database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = EnterpriseDatabase()
    return _db_instance