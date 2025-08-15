"""
Step 1: Foundation - Core Turkish Dataset Generator
Elite Turkish Telco Dataset for Single Model Training
"""
import json
import random
import uuid
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

class TurkishTelcoFoundation:
    """Foundation class for Turkish telco dataset generation."""
    
    def __init__(self):
        # Turkish customer names (realistic)
        self.turkish_names = [
            "Ahmet Yılmaz", "Fatma Demir", "Mehmet Kaya", "Ayşe Özkan", "Mustafa Çelik",
            "Hatice Arslan", "Ali Doğan", "Zeynep Koç", "Hüseyin Şahin", "Elif Yıldız",
            "Ömer Aksoy", "Büşra Özdemir", "Serkan Polat", "Merve Tuncer", "Burak Aydın",
            "Seda Yıldırım", "Tolga Eren", "Gamze Kılıç", "Emre Güneş", "Deniz Aktaş"
        ]
        
        # Maiden names for verification
        self.maiden_names = [
            "Kaya", "Özkan", "Demir", "Çelik", "Yılmaz", "Arslan", "Doğan", "Koç",
            "Şahin", "Yıldız", "Aksoy", "Özdemir", "Polat", "Tuncer", "Aydın",
            "Kılıç", "Güneş", "Aktaş", "Eren", "Yıldırım"
        ]
        
        # Turkish cities for coverage scenarios
        self.turkish_cities = [
            "İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Adana", "Konya",
            "Şanlıurfa", "Gaziantep", "Kocaeli", "Mersin", "Diyarbakır", "Hatay",
            "Manisa", "Kayseri", "Samsun", "Balıkesir", "Kahramanmaraş", "Van"
        ]
        
        # Package definitions (realistic Turkish telecom)
        self.packages = [
            {
                "id": "basic_5gb", 
                "name": "Temel 5GB", 
                "price": 99.99, 
                "data": "5GB",
                "features": ["5GB yüksek hız internet", "Sınırsız konuşma", "1000 SMS"]
            },
            {
                "id": "premium_10gb", 
                "name": "Premium 10GB", 
                "price": 149.99, 
                "data": "10GB",
                "features": ["10GB yüksek hız internet", "Sınırsız konuşma", "Sınırsız SMS", "5G destekli"]
            },
            {
                "id": "unlimited", 
                "name": "Sınırsız", 
                "price": 299.99, 
                "data": "Sınırsız",
                "features": ["Sınırsız yüksek hız internet", "Sınırsız konuşma", "Sınırsız SMS", "5G destekli", "Uluslararası 100 dakika"]
            },
            {
                "id": "student_3gb", 
                "name": "Öğrenci 3GB", 
                "price": 59.99, 
                "data": "3GB",
                "features": ["3GB yüksek hız internet", "Sınırsız konuşma", "500 SMS", "Öğrenci indirimi"]
            },
            {
                "id": "business_25gb", 
                "name": "İş 25GB", 
                "price": 399.99, 
                "data": "25GB",
                "features": ["25GB yüksek hız internet", "Sınırsız konuşma", "Sınırsız SMS", "İş destek hattı"]
            },
            {
                "id": "family_15gb", 
                "name": "Aile 15GB", 
                "price": 199.99, 
                "data": "15GB",
                "features": ["15GB paylaşımlı internet", "Aile içi ücretsiz", "Çocuk güvenlik filtresi"]
            }
        ]
    
    def generate_customer_data(self) -> Dict:
        """Generate realistic Turkish customer data."""
        return {
            "customer_id": str(random.randint(10000, 99999)),
            "name": random.choice(self.turkish_names),
            "maiden_name": random.choice(self.maiden_names),
            "msisdn": f"9055{random.randint(10000000, 99999999)}",
            "phone_last4": str(random.randint(1000, 9999)),
            "imei": "".join([str(random.randint(0, 9)) for _ in range(15)]),
            "current_package": random.choice(self.packages),
            "city": random.choice(self.turkish_cities),
            "contract_end": (datetime.now() + timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
            "payment_status": random.choice(["active", "pending", "overdue"]),
            "activation_status": random.choice(["active", "pending", "installing", "failed"])
        }
    
    def create_tool_call_json(self, tool_name: str, arguments: Dict) -> str:
        """Create properly formatted tool call JSON."""
        return json.dumps({
            "tool_call": {
                "id": str(uuid.uuid4()),
                "name": tool_name,
                "arguments": arguments
            }
        }, ensure_ascii=False)
    
    def create_handoff_json(self, persona: str, message: str = None) -> str:
        """Create persona handoff JSON."""
        handoff_data = {"handoff": {"persona": persona}}
        if message:
            handoff_data["handoff"]["say"] = message
        return json.dumps(handoff_data, ensure_ascii=False)
    
    def create_tool_result(self, success: bool, data: Dict = None, error: str = None) -> str:
        """Create tool result for user message."""
        result = {"success": success}
        if data:
            result["data"] = data
        if error:
            result["error"] = error
        return f"<tool_result>{json.dumps(result, ensure_ascii=False)}</tool_result>"

print("✅ Step 1: Foundation classes initialized")
