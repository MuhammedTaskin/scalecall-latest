#!/usr/bin/env python3
"""
Supabase Professional e-SIM Agent
Complete professional call center agent with Supabase integration
"""
import asyncio
import json
import sys
import os
from typing import Dict, List, Any, Optional

# Add backend to path
sys.path.insert(0, 'backend')

from tools.registry import ToolRegistry

class SupabaseProfessionalAgent:
    """Professional e-SIM call center agent with Supabase integration."""
    
    def __init__(self):
        self.tool_registry = ToolRegistry()
        self.conversation_state = {
            "verified": False,
            "customer_id": None,
            "customer_name": None,
            "current_step": "greeting"
        }

    async def process_message(self, user_input: str) -> str:
        """Process user message with professional call center behavior."""
        
        print(f"🎯 Kullanıcı mesajı: {user_input}")
        print(f"📊 Mevcut durum: {self.conversation_state}")
        
        # Check if user is providing phone number
        if self._is_phone_number(user_input):
            return await self._handle_phone_verification(user_input)
        
        # Check if user is providing maiden name after phone
        if (self.conversation_state.get("waiting_for_maiden_name") and 
            not self.conversation_state["verified"]):
            return await self._handle_maiden_name_verification(user_input)
        
        # If not verified yet, ask for verification
        if not self.conversation_state["verified"]:
            return await self._request_verification(user_input)
        
        # Process verified user requests
        return await self._handle_verified_request(user_input)

    def _is_phone_number(self, text: str) -> bool:
        """Check if text contains a phone number."""
        # Convert spoken numbers to digits
        cleaned = text.replace(" ", "")
        replacements = {
            "sıfır": "0", "bir": "1", "iki": "2", "üç": "3", "dört": "4",
            "beş": "5", "altı": "6", "yedi": "7", "sekiz": "8", "dokuz": "9"
        }
        
        for word, digit in replacements.items():
            cleaned = cleaned.replace(word, digit)
        
        # Check for phone number patterns
        return any(len(part) >= 10 and part.isdigit() for part in cleaned.split())

    def _extract_phone_number(self, text: str) -> str:
        """Extract phone number from text."""
        # Convert spoken numbers to digits
        replacements = {
            "sıfır": "0", "bir": "1", "iki": "2", "üç": "3", "dört": "4",
            "beş": "5", "altı": "6", "yedi": "7", "sekiz": "8", "dokuz": "9"
        }
        
        cleaned = text.lower()
        for word, digit in replacements.items():
            cleaned = cleaned.replace(word, digit)
        
        # Extract digits
        digits = ''.join(c for c in cleaned if c.isdigit())
        
        # Format as Turkish mobile number
        if len(digits) >= 10:
            if digits.startswith('0'):
                return digits[:11]  # 05551234567
            else:
                return '0' + digits[:10]  # Add leading 0
        
        return digits

    async def _handle_phone_verification(self, user_input: str) -> str:
        """Handle phone number verification step."""
        phone = self._extract_phone_number(user_input)
        print(f"📱 Çıkarılan telefon: {phone}")
        
        self.conversation_state["phone"] = phone
        self.conversation_state["waiting_for_maiden_name"] = True
        
        return "Teşekkürler; annenizin kızlık soyadını da alabilir miyim?"

    async def _handle_maiden_name_verification(self, user_input: str) -> str:
        """Handle maiden name verification step."""
        # Extract maiden name (clean up common words)
        maiden_name = user_input.strip().replace("değil", "").replace("şey", "").replace("evet", "").replace(",", "").strip()
        
        # Take the last meaningful word
        words = [w for w in maiden_name.split() if len(w) > 2]
        if words:
            maiden_name = words[-1].title()
        
        print(f"👩 Kızlık soyadı: {maiden_name}")
        
        # Call verify_user tool
        try:
            result = await self.tool_registry.execute("verify_user", {
                "maiden_name": maiden_name,
                "msisdn": self.conversation_state["phone"]
            })
            
            print(f"🔍 Doğrulama sonucu: {result}")
            
            if result.get("success"):
                self.conversation_state["verified"] = True
                self.conversation_state["customer_id"] = result.get("data", {}).get("customer_id")
                self.conversation_state["customer_name"] = result.get("data", {}).get("name", "")
                self.conversation_state["waiting_for_maiden_name"] = False
                
                # Get customer name for personalized response
                customer_name = result.get("data", {}).get("name", "").split()[0]  # First name
                return f"{customer_name} bey/hanım, doğrulama tamamdır. Size nasıl yardımcı olabilirim?"
            else:
                self.conversation_state["waiting_for_maiden_name"] = False
                return "Üzgünüm, bilgiler uyuşmuyor. Lütfen telefon numaranızı tekrar konuşur gibi söyleyin."
                
        except Exception as e:
            print(f"❌ Doğrulama hatası: {e}")
            return "Doğrulama sırasında bir sorun oluştu. Lütfen tekrar deneyin."

    async def _request_verification(self, user_input: str) -> str:
        """Request user verification."""
        return "Memnuniyetle yardımcı olurum; önce kimlik doğrulaması yapalım. Telefon numaranızı konuşur gibi söyleyin lütfen."

    async def _handle_verified_request(self, user_input: str) -> str:
        """Handle requests from verified users."""
        customer_id = self.conversation_state["customer_id"]
        
        # Analyze user intent
        intent = self._analyze_intent(user_input)
        print(f"🎯 Tespit edilen niyet: {intent}")
        
        if intent == "esim_activation":
            return await self._handle_esim_activation(customer_id, user_input)
        elif intent == "package_change":
            return await self._handle_package_change(customer_id, user_input)
        elif intent == "activation_problem":
            return await self._handle_activation_problem(customer_id, user_input)
        elif intent == "device_check":
            return await self._handle_device_check(customer_id, user_input)
        else:
            return await self._handle_general_request(customer_id, user_input)

    def _analyze_intent(self, text: str) -> str:
        """Analyze user intent from text."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["mevsim", "esim", "aktivasyon", "kurdum", "aktive"]):
            if any(word in text_lower for word in ["sinyal yok", "çalışmıyor", "sorun", "hata"]):
                return "activation_problem"
            else:
                return "esim_activation"
        elif any(word in text_lower for word in ["paket", "tarife", "değiştir", "geç"]):
            return "package_change"
        elif any(word in text_lower for word in ["imei", "cihaz", "uyumlu", "telefon"]):
            return "device_check"
        else:
            return "general"

    async def _handle_esim_activation(self, customer_id: str, user_input: str) -> str:
        """Handle eSIM activation requests."""
        try:
            # Check if IMEI is mentioned
            if "imei" in user_input.lower() or "aymay" in user_input.lower():
                imei = self._extract_imei(user_input)
                if imei:
                    return await self._check_device_compatibility(customer_id, imei)
            
            # Generate new activation code
            result = await self.tool_registry.execute("reissue_activation_code", {
                "customer_id": customer_id
            })
            
            if result.get("success"):
                code = result.get("data", {}).get("code", "")
                return f"Yeni bir aktivasyon kodu üreteyim. Kodunuz hazır: {code}. iOS mu Android mi kullanıyorsunuz?"
            else:
                return "Kod üretiminde sorun oluştu. Teknik ekibe yönlendiriyorum."
                
        except Exception as e:
            print(f"❌ Aktivasyon hatası: {e}")
            return "Aktivasyon işleminde sorun oluştu. Lütfen tekrar deneyin."

    async def _handle_activation_problem(self, customer_id: str, user_input: str) -> str:
        """Handle activation problems."""
        try:
            # Generate new code for activation problems
            code_result = await self.tool_registry.execute("reissue_activation_code", {
                "customer_id": customer_id
            })
            
            if code_result.get("success"):
                code = code_result.get("data", {}).get("code", "")
                return f"Yeniden deneyelim; yeni bir kod üretiyorum: {code}. Kodu girip uçak modunu 10 saniye açıp kapatın; olmazsa tekrar yazın."
            else:
                return "Kod üretiminde sorun oluştu. Teknik destek ile görüştüreyim."
            
        except Exception as e:
            print(f"❌ Aktivasyon sorunu hatası: {e}")
            return "Sorun giderme sırasında hata oluştu. Teknik destek ile görüştüreyim."

    async def _handle_package_change(self, customer_id: str, user_input: str) -> str:
        """Handle package change requests."""
        try:
            # Get available packages
            packages_result = await self.tool_registry.execute("get_available_packages", {
                "customer_id": customer_id
            })
            
            if packages_result.get("success"):
                packages = packages_result.get("data", {}).get("packages", [])
                
                # Simple package recommendation based on text
                if "10" in user_input or "on" in user_input:
                    target_package = "premium_10gb"
                elif "20" in user_input or "aile" in user_input:
                    target_package = "family_20gb"
                elif "sınırsız" in user_input or "unlimited" in user_input:
                    target_package = "unlimited"
                else:
                    # Show options
                    package_list = ", ".join([f"{p.get('name', '')} ({p.get('price', 0)} TL)" for p in packages])
                    return f"Mevcut paketinizi ve seçenekleri kontrol ediyorum. Uygun paketler: {package_list}. Hangisini seçersiniz?"
                
                # Execute package change
                change_result = await self.tool_registry.execute("change_package", {
                    "customer_id": customer_id,
                    "package_id": target_package
                })
                
                if change_result.get("success"):
                    message = change_result.get("data", {}).get("message", "onay SMS'i gelecektir")
                    return f"Geçişi başlattım; {message}."
                else:
                    return "Paket değişikliğinde sorun oluştu. Tekrar deneyelim."
            
            return "Paket seçeneklerini kontrol ediyorum."
            
        except Exception as e:
            print(f"❌ Paket değişikliği hatası: {e}")
            return "Paket değişikliği sırasında sorun oluştu."

    async def _check_device_compatibility(self, customer_id: str, imei: str) -> str:
        """Check device compatibility."""
        try:
            result = await self.tool_registry.execute("check_device_registration", {
                "customer_id": customer_id,
                "imei": imei
            })
            
            if result.get("success"):
                data = result.get("data", {})
                if data.get("esim_supported"):
                    brand = data.get("brand", "")
                    model = data.get("model", "")
                    return f"Uyumlu görünüyor ({brand} {model}); yeni bir aktivasyon kodu üreteyim."
                else:
                    return "Bu model eSIM desteklemiyor; fiziksel SIM ile devam etmenizi öneririm."
            else:
                return "Cihaz kontrolünde sorun oluştu. IMEI'yi tekrar kontrol eder misiniz?"
                
        except Exception as e:
            print(f"❌ Cihaz kontrol hatası: {e}")
            return "Cihaz uyumluluğu kontrol edilirken sorun oluştu."

    def _extract_imei(self, text: str) -> str:
        """Extract IMEI from text."""
        # Find sequences of 15 digits
        import re
        numbers = re.findall(r'\d+', text)
        for num in numbers:
            if len(num) == 15:
                return num
        return ""

    async def _handle_device_check(self, customer_id: str, user_input: str) -> str:
        """Handle device compatibility checks."""
        imei = self._extract_imei(user_input)
        if imei:
            return await self._check_device_compatibility(customer_id, imei)
        else:
            return "IMEI 15 rakam olmalı; tekrar eder misiniz?"

    async def _handle_general_request(self, customer_id: str, user_input: str) -> str:
        """Handle general requests."""
        return "Size başka nasıl yardımcı olabilirim? e-SIM aktivasyon, paket değişikliği veya teknik destek konularında yardımcı olabilirim."

    def reset_conversation(self):
        """Reset conversation state."""
        self.conversation_state = {
            "verified": False,
            "customer_id": None,
            "customer_name": None,
            "current_step": "greeting"
        }

async def main():
    """Interactive demo of the Supabase professional agent."""
    agent = SupabaseProfessionalAgent()
    
    print("🏢 SUPABASE PROFESSIONAL e-SIM AGENT")
    print("=" * 60)
    print("✅ Gerçek Supabase veritabanı entegrasyonu")
    print("✅ Profesyonel çağrı merkezi davranışı")
    print("✅ Örnek dialog senaryoları destekleniyor")
    print("")
    print("Test senaryoları:")
    print("1. 'mevsim kurdum ama sinyal yok, yardim edin'")
    print("2. 'paketi mi degistirsem; bes gebe yetmiyo'")
    print("3. 'imey numaram 359111222333444; uyumlu mu mevsim?'")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\n👤 Siz: ").strip()
            if user_input.lower() in ['quit', 'exit', 'çık']:
                break
            
            if user_input.lower() == 'reset':
                agent.reset_conversation()
                print("🔄 Konuşma sıfırlandı")
                continue
            
            response = await agent.process_message(user_input)
            print(f"🤖 Agent: {response}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Hata: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n👋 Görüşmek üzere!")

if __name__ == "__main__":
    asyncio.run(main())
