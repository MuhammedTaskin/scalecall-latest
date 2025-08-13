"""
Telecom tool implementations with realistic mock logic.
"""
import json
import uuid
import logging
from typing import Dict, Any
from datetime import datetime, timedelta

import sys
import os
sys.path.append(os.path.dirname(__file__))

from .types import OperationResult

logger = logging.getLogger(__name__)


class TelecomTools:
    """Implementation of core telecom tools with realistic mock data."""
    
    def __init__(self):
        # Mock customer database
        self.customers = {
            "12345": {
                "customer_id": "12345",
                "name": "Ahmet Yılmaz",
                "msisdn": "905551234567",
                "maiden_name": "Kaya",
                "package_id": "premium_10gb",
                "contract_end": "2024-12-31",
                "payment_status": "active",
                "device_imei": "123456789012345",
                "activation_status": "active",
                "created_at": "2024-01-15"
            },
            "67890": {
                "customer_id": "67890", 
                "name": "Fatma Demir",
                "msisdn": "905559876543",
                "maiden_name": "Özkan",
                "package_id": "basic_5gb",
                "contract_end": "2024-11-30",
                "payment_status": "active",
                "device_imei": "987654321098765",
                "activation_status": "pending",
                "created_at": "2024-02-20"
            }
        }
        
        # Mock packages
        self.packages = {
            "basic_5gb": {
                "id": "basic_5gb",
                "name": "Temel 5GB",
                "data": "5GB",
                "price": 99.99,
                "validity": "30 gün",
                "features": ["5GB yüksek hız internet", "Sınırsız konuşma", "1000 SMS"]
            },
            "premium_10gb": {
                "id": "premium_10gb", 
                "name": "Premium 10GB",
                "data": "10GB",
                "price": 149.99,
                "validity": "30 gün",
                "features": ["10GB yüksek hız internet", "Sınırsız konuşma", "Sınırsız SMS", "5G destekli"]
            },
            "unlimited": {
                "id": "unlimited",
                "name": "Sınırsız",
                "data": "Sınırsız",
                "price": 299.99,
                "validity": "30 gün", 
                "features": ["Sınırsız yüksek hız internet", "Sınırsız konuşma", "Sınırsız SMS", "5G destekli", "Uluslararası 100 dakika"]
            }
        }
        
        # Ticket counter
        self.ticket_counter = 1000
    
    def _mask_sensitive_data(self, data: str) -> str:
        """Mask sensitive information for logging."""
        if not data:
            return data
        if len(data) > 6:
            return data[:3] + "*" * (len(data) - 6) + data[-3:]
        return "*" * len(data)
    
    async def execute(self, tool_name: str, arguments: Dict) -> OperationResult:
        """Execute the specified telecom tool."""
        try:
            if tool_name == "verify_user":
                return await self._verify_user(arguments)
            elif tool_name == "get_user_info":
                return await self._get_user_info(arguments)
            elif tool_name == "check_device_registration":
                return await self._check_device_registration(arguments)
            elif tool_name == "reissue_activation_code":
                return await self._reissue_activation_code(arguments)
            elif tool_name == "get_available_packages":
                return await self._get_available_packages(arguments)
            elif tool_name == "change_package":
                return await self._change_package(arguments)
            elif tool_name == "create_support_ticket":
                return await self._create_support_ticket(arguments)
            else:
                return OperationResult(
                    success=False,
                    error=f"Unknown tool: {tool_name}"
                )
        except Exception as e:
            logger.error(f"Error executing {tool_name}: {e}")
            return OperationResult(
                success=False,
                error="İşlem sırasında bir hata oluştu"
            )
    
    async def _verify_user(self, args: Dict) -> OperationResult:
        """Verify customer identity."""
        maiden_name = args.get("maiden_name", "").strip().lower()
        msisdn = args.get("msisdn", "").strip()
        
        # Log masked data
        logger.info(f"Verifying user: MSISDN {self._mask_sensitive_data(msisdn)}")
        
        # Find customer by phone number and maiden name
        for customer_id, customer in self.customers.items():
            if (customer["msisdn"] == msisdn and 
                customer["maiden_name"].lower() == maiden_name):
                
                return OperationResult(
                    success=True,
                    data={
                        "customer_id": customer_id,
                        "name": customer["name"],
                        "verified": True
                    }
                )
        
        return OperationResult(
            success=False,
            error="Kimlik doğrulama başarısız. Lütfen bilgilerinizi kontrol edin."
        )
    
    async def _get_user_info(self, args: Dict) -> OperationResult:
        """Get customer account information."""
        customer_id = args.get("customer_id")
        
        if customer_id not in self.customers:
            return OperationResult(
                success=False,
                error="Müşteri bulunamadı"
            )
        
        customer = self.customers[customer_id]
        package = self.packages.get(customer["package_id"], {})
        
        return OperationResult(
            success=True,
            data={
                "customer_id": customer_id,
                "name": customer["name"],
                "msisdn": self._mask_sensitive_data(customer["msisdn"]),
                "current_package": package.get("name", "Bilinmiyor"),
                "package_data": package.get("data", "Bilinmiyor"),
                "contract_end": customer["contract_end"],
                "payment_status": customer["payment_status"],
                "activation_status": customer["activation_status"]
            }
        )
    
    async def _check_device_registration(self, args: Dict) -> OperationResult:
        """Check device registration status."""
        imei = args.get("imei", "").strip()
        
        logger.info(f"Checking device: IMEI {self._mask_sensitive_data(imei)}")
        
        # Find customer by IMEI
        for customer_id, customer in self.customers.items():
            if customer["device_imei"] == imei:
                return OperationResult(
                    success=True,
                    data={
                        "imei": self._mask_sensitive_data(imei),
                        "registered": True,
                        "customer_id": customer_id,
                        "activation_status": customer["activation_status"],
                        "device_compatible": True
                    }
                )
        
        # Device not found - could be new device
        return OperationResult(
            success=True,
            data={
                "imei": self._mask_sensitive_data(imei),
                "registered": False,
                "device_compatible": True,
                "can_register": True
            }
        )
    
    async def _reissue_activation_code(self, args: Dict) -> OperationResult:
        """Generate new eSIM activation code."""
        customer_id = args.get("customer_id")
        
        if customer_id not in self.customers:
            return OperationResult(
                success=False,
                error="Müşteri bulunamadı"
            )
        
        # Generate mock LPA code
        lpa_code = f"LPA:1$sm-dp-plus.example.com${uuid.uuid4().hex[:16]}$activation-code-{customer_id}"
        
        logger.info(f"Generated activation code for customer {customer_id}")
        
        return OperationResult(
            success=True,
            data={
                "activation_code": lpa_code,
                "qr_code_url": f"/qr/{customer_id}",
                "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
                "instructions": "Bu kodu eSIM ayarlarından tarayın veya manuel olarak girin"
            }
        )
    
    async def _get_available_packages(self, args: Dict) -> OperationResult:
        """Get available packages for customer."""
        customer_id = args.get("customer_id")
        country_code = args.get("country_code", "TR")
        
        if customer_id not in self.customers:
            return OperationResult(
                success=False,
                error="Müşteri bulunamadı"
            )
        
        current_customer = self.customers[customer_id]
        current_package_id = current_customer["package_id"]
        
        # Filter packages (exclude current)
        available = []
        for pkg_id, pkg in self.packages.items():
            if pkg_id != current_package_id:
                available.append({
                    "id": pkg_id,
                    "name": pkg["name"],
                    "data": pkg["data"],
                    "price": pkg["price"],
                    "features": pkg["features"][:3]  # Show first 3 features
                })
        
        return OperationResult(
            success=True,
            data={
                "packages": available,
                "current_package": self.packages[current_package_id]["name"]
            }
        )
    
    async def _change_package(self, args: Dict) -> OperationResult:
        """Change customer package."""
        customer_id = args.get("customer_id")
        package_id = args.get("package_id")
        
        if customer_id not in self.customers:
            return OperationResult(
                success=False,
                error="Müşteri bulunamadı"
            )
        
        if package_id not in self.packages:
            return OperationResult(
                success=False,
                error="Geçersiz paket seçimi"
            )
        
        old_package = self.packages[self.customers[customer_id]["package_id"]]
        new_package = self.packages[package_id]
        price_diff = new_package["price"] - old_package["price"]
        
        # Update customer package
        self.customers[customer_id]["package_id"] = package_id
        
        logger.info(f"Package changed for customer {customer_id}: {old_package['name']} -> {new_package['name']}")
        
        return OperationResult(
            success=True,
            data={
                "old_package": old_package["name"],
                "new_package": new_package["name"],
                "price_difference": price_diff,
                "effective_date": datetime.now().date().isoformat(),
                "confirmation_id": f"PKG-{uuid.uuid4().hex[:8].upper()}"
            }
        )
    
    async def _create_support_ticket(self, args: Dict) -> OperationResult:
        """Create customer support ticket."""
        customer_id = args.get("customer_id")
        subject = args.get("subject")
        description = args.get("description")
        priority = args.get("priority", "medium")
        
        if customer_id not in self.customers:
            return OperationResult(
                success=False,
                error="Müşteri bulunamadı"
            )
        
        # Generate ticket
        self.ticket_counter += 1
        ticket_id = f"TKT-{self.ticket_counter}"
        
        logger.info(f"Created support ticket {ticket_id} for customer {customer_id}")
        
        return OperationResult(
            success=True,
            data={
                "ticket_id": ticket_id,
                "status": "open",
                "priority": priority,
                "created_at": datetime.now().isoformat(),
                "estimated_resolution": "24-48 saat içinde"
            }
        )
