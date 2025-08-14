"""
Supabase-integrated telecom tool implementations.
"""
import json
import uuid
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from .types import OperationResult
from lib.supabase_client import create_supabase_admin

logger = logging.getLogger(__name__)


class SupabaseTelecomTools:
    """Implementation of core telecom tools with Supabase integration."""
    
    def __init__(self):
        self.supabase = create_supabase_admin()
        if not self.supabase:
            logger.warning("Supabase not available, using fallback mode")
            self._init_fallback_data()
    
    def _init_fallback_data(self):
        """Initialize fallback data when Supabase is not available."""
        # Fallback customer database for testing
        self.customers = {
            "12345": {
                "customer_id": "12345",
                "name": "Ali Doğan",
                "msisdn": "05551234567",
                "maiden_name": "Kaya",
                "package_id": "premium_10gb",
                "activation_status": "active",
                "device_imei": "359111222333444"
            },
            "67890": {
                "customer_id": "67890", 
                "name": "Fatma Demir",
                "msisdn": "05556789012",
                "maiden_name": "Demir",
                "package_id": "basic_5gb",
                "activation_status": "pending",
                "device_imei": "357999123456789"
            },
            "11223": {
                "customer_id": "11223",
                "name": "Elif Yıldız",
                "msisdn": "05551122334",
                "maiden_name": "Yıldız",
                "package_id": "family_20gb",
                "activation_status": "active",
                "device_imei": "359888777666555"
            },
            "44556": {
                "customer_id": "44556",
                "name": "Mehmet Kaya",
                "msisdn": "05554455667",
                "maiden_name": "Kaya",
                "package_id": "basic_5gb",
                "activation_status": "failed",
                "device_imei": "357999123456789"
            },
            "78901": {
                "customer_id": "78901",
                "name": "Zeynep Koç",
                "msisdn": "05557890123",
                "maiden_name": "Koç",
                "package_id": "premium_10gb",
                "activation_status": "failed",
                "device_imei": "359123456789012"
            }
        }
        
        self.packages = {
            "basic_5gb": {"id": "basic_5gb", "name": "Temel 5GB", "price": 99.99},
            "premium_10gb": {"id": "premium_10gb", "name": "Premium 10GB", "price": 149.99},
            "family_20gb": {"id": "family_20gb", "name": "Aile 20GB", "price": 199.99},
            "unlimited": {"id": "unlimited", "name": "Sınırsız", "price": 299.99}
        }
        
        self.ticket_counter = 1000

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
        """Verify customer identity using Supabase."""
        maiden_name = args.get("maiden_name", "").strip()
        msisdn = args.get("msisdn", "").strip()
        
        if not maiden_name or not msisdn:
            return OperationResult(
                success=False,
                error="Eksik bilgi: Kızlık soyadı ve telefon numarası gerekli"
            )
        
        try:
            if self.supabase:
                # Query Supabase for customer
                response = self.supabase.table("customers").select("*").eq("msisdn", msisdn).eq("maiden_name", maiden_name).execute()
                
                if response.data and len(response.data) > 0:
                    customer = response.data[0]
                    return OperationResult(
                        success=True,
                        data={
                            "customer_id": customer["customer_id"],
                            "name": customer["name"],
                            "msisdn": customer["msisdn"]
                        }
                    )
                else:
                    return OperationResult(
                        success=False,
                        error="Müşteri bilgileri uyuşmuyor"
                    )
            else:
                # Fallback mode
                for customer_id, customer in self.customers.items():
                    if customer["msisdn"] == msisdn and customer["maiden_name"] == maiden_name:
                        return OperationResult(
                            success=True,
                            data={
                                "customer_id": customer_id,
                                "name": customer["name"],
                                "msisdn": customer["msisdn"]
                            }
                        )
                
                return OperationResult(
                    success=False,
                    error="Müşteri bilgileri uyuşmuyor"
                )
                
        except Exception as e:
            logger.error(f"Error in verify_user: {e}")
            return OperationResult(
                success=False,
                error="Doğrulama sırasında hata oluştu"
            )

    async def _get_user_info(self, args: Dict) -> OperationResult:
        """Get customer information from Supabase."""
        customer_id = args.get("customer_id", "").strip()
        
        if not customer_id:
            return OperationResult(
                success=False,
                error="Müşteri ID gerekli"
            )
        
        try:
            if self.supabase:
                # Get customer with package info
                customer_response = self.supabase.table("customers").select("*").eq("customer_id", customer_id).execute()
                
                if not customer_response.data:
                    return OperationResult(
                        success=False,
                        error="Müşteri bulunamadı"
                    )
                
                customer = customer_response.data[0]
                
                # Get current package
                package_response = self.supabase.table("customer_packages").select("*, packages(*)").eq("customer_id", customer_id).eq("is_active", True).execute()
                
                package_info = None
                if package_response.data:
                    package_info = package_response.data[0]["packages"]
                
                return OperationResult(
                    success=True,
                    data={
                        "customer": customer,
                        "package": package_info
                    }
                )
            else:
                # Fallback mode
                if customer_id in self.customers:
                    customer = self.customers[customer_id]
                    package_id = customer.get("package_id")
                    package = self.packages.get(package_id, {})
                    
                    return OperationResult(
                        success=True,
                        data={
                            "customer": customer,
                            "package": package
                        }
                    )
                else:
                    return OperationResult(
                        success=False,
                        error="Müşteri bulunamadı"
                    )
                    
        except Exception as e:
            logger.error(f"Error in get_user_info: {e}")
            return OperationResult(
                success=False,
                error="Müşteri bilgileri alınırken hata oluştu"
            )

    async def _check_device_registration(self, args: Dict) -> OperationResult:
        """Check device compatibility from Supabase."""
        customer_id = args.get("customer_id", "").strip()
        imei = args.get("imei", "").strip()
        
        if not customer_id or not imei:
            return OperationResult(
                success=False,
                error="Müşteri ID ve IMEI gerekli"
            )
        
        try:
            if self.supabase:
                # Check device compatibility
                device_response = self.supabase.table("device_compatibility").select("*").eq("imei", imei).execute()
                
                if device_response.data:
                    device = device_response.data[0]
                    return OperationResult(
                        success=True,
                        data={
                            "registered": device["registered"],
                            "esim_supported": device["esim_supported"],
                            "brand": device["brand"],
                            "model": device["model"]
                        }
                    )
                else:
                    # Unknown device - assume not supported
                    return OperationResult(
                        success=True,
                        data={
                            "registered": False,
                            "esim_supported": False,
                            "brand": "Unknown",
                            "model": "Unknown"
                        }
                    )
            else:
                # Fallback mode - simple IMEI check
                known_devices = {
                    "359111222333444": {"brand": "Apple", "model": "iPhone 15", "esim_supported": True, "registered": True},
                    "357999123456789": {"brand": "Samsung", "model": "Galaxy S23", "esim_supported": True, "registered": True},
                    "359888777666555": {"brand": "Google", "model": "Pixel 8", "esim_supported": True, "registered": True},
                    "359123456789012": {"brand": "Apple", "model": "iPhone 14", "esim_supported": True, "registered": True}
                }
                
                device_info = known_devices.get(imei, {
                    "brand": "Unknown", "model": "Unknown", "esim_supported": False, "registered": False
                })
                
                return OperationResult(
                    success=True,
                    data=device_info
                )
                
        except Exception as e:
            logger.error(f"Error in check_device_registration: {e}")
            return OperationResult(
                success=False,
                error="Cihaz kontrolü sırasında hata oluştu"
            )

    async def _reissue_activation_code(self, args: Dict) -> OperationResult:
        """Generate new activation code and store in Supabase."""
        customer_id = args.get("customer_id", "").strip()
        
        if not customer_id:
            return OperationResult(
                success=False,
                error="Müşteri ID gerekli"
            )
        
        try:
            # Generate new activation code
            code_suffix = str(uuid.uuid4())[:8].upper()
            activation_code = f"LPA:1$sp${customer_id[:4]}-{code_suffix}"
            
            if self.supabase:
                # Update or create eSIM profile
                esim_response = self.supabase.table("esim_profiles").select("*").eq("customer_id", customer_id).execute()
                
                if esim_response.data:
                    # Update existing profile
                    esim_id = esim_response.data[0]["esim_id"]
                    self.supabase.table("esim_profiles").update({
                        "activation_code": activation_code,
                        "status": "pending"
                    }).eq("esim_id", esim_id).execute()
                else:
                    # Create new profile
                    esim_id = f"esim_{customer_id}_{int(datetime.now().timestamp())}"
                    self.supabase.table("esim_profiles").insert({
                        "esim_id": esim_id,
                        "customer_id": customer_id,
                        "activation_code": activation_code,
                        "status": "pending"
                    }).execute()
            
            return OperationResult(
                success=True,
                data={
                    "code": activation_code,
                    "customer_id": customer_id
                }
            )
            
        except Exception as e:
            logger.error(f"Error in reissue_activation_code: {e}")
            return OperationResult(
                success=False,
                error="Aktivasyon kodu oluşturulurken hata oluştu"
            )

    async def _get_available_packages(self, args: Dict) -> OperationResult:
        """Get available packages from Supabase."""
        customer_id = args.get("customer_id", "").strip()
        
        try:
            if self.supabase:
                # Get all active packages
                packages_response = self.supabase.table("packages").select("*").eq("is_active", True).execute()
                
                packages = []
                for pkg in packages_response.data:
                    packages.append({
                        "id": pkg["package_id"],
                        "name": pkg["name"],
                        "price": float(pkg["price"]),
                        "data_gb": pkg.get("data_gb", 0)
                    })
                
                return OperationResult(
                    success=True,
                    data={"packages": packages}
                )
            else:
                # Fallback mode
                packages = list(self.packages.values())
                return OperationResult(
                    success=True,
                    data={"packages": packages}
                )
                
        except Exception as e:
            logger.error(f"Error in get_available_packages: {e}")
            return OperationResult(
                success=False,
                error="Paket bilgileri alınırken hata oluştu"
            )

    async def _change_package(self, args: Dict) -> OperationResult:
        """Change customer package in Supabase."""
        customer_id = args.get("customer_id", "").strip()
        package_id = args.get("package_id", "").strip()
        
        if not customer_id or not package_id:
            return OperationResult(
                success=False,
                error="Müşteri ID ve paket ID gerekli"
            )
        
        try:
            if self.supabase:
                # Deactivate current package
                self.supabase.table("customer_packages").update({
                    "is_active": False
                }).eq("customer_id", customer_id).eq("is_active", True).execute()
                
                # Add new package
                self.supabase.table("customer_packages").insert({
                    "customer_id": customer_id,
                    "package_id": package_id,
                    "is_active": True
                }).execute()
                
                return OperationResult(
                    success=True,
                    data={
                        "customer_id": customer_id,
                        "new_package_id": package_id,
                        "message": "Paket değişikliği 24 saat içinde aktif olacaktır"
                    }
                )
            else:
                # Fallback mode
                if customer_id in self.customers:
                    old_package = self.customers[customer_id].get("package_id", "")
                    self.customers[customer_id]["package_id"] = package_id
                    
                    return OperationResult(
                        success=True,
                        data={
                            "customer_id": customer_id,
                            "old_package_id": old_package,
                            "new_package_id": package_id,
                            "message": "Paket değişikliği tamamlandı"
                        }
                    )
                else:
                    return OperationResult(
                        success=False,
                        error="Müşteri bulunamadı"
                    )
                    
        except Exception as e:
            logger.error(f"Error in change_package: {e}")
            return OperationResult(
                success=False,
                error="Paket değişikliği sırasında hata oluştu"
            )

    async def _create_support_ticket(self, args: Dict) -> OperationResult:
        """Create support ticket in Supabase."""
        customer_id = args.get("customer_id", "").strip()
        issue_type = args.get("issue_type", "").strip()
        description = args.get("description", "").strip()
        
        if not customer_id or not issue_type or not description:
            return OperationResult(
                success=False,
                error="Müşteri ID, sorun türü ve açıklama gerekli"
            )
        
        try:
            ticket_id = f"TKT-{self.ticket_counter}"
            self.ticket_counter += 1
            
            if self.supabase:
                # Insert ticket into Supabase
                self.supabase.table("support_tickets").insert({
                    "ticket_id": ticket_id,
                    "customer_id": customer_id,
                    "issue_type": issue_type,
                    "description": description,
                    "status": "open"
                }).execute()
            
            return OperationResult(
                success=True,
                data={
                    "ticket_id": ticket_id,
                    "customer_id": customer_id,
                    "issue_type": issue_type,
                    "status": "open"
                }
            )
            
        except Exception as e:
            logger.error(f"Error in create_support_ticket: {e}")
            return OperationResult(
                success=False,
                error="Destek talebi oluşturulurken hata oluştu"
            )
