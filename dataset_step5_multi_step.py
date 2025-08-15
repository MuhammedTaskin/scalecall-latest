"""
Step 5: Multi-Step Dialog Chains
Complex decision trees with persona handoffs
"""
import random
from typing import List, Dict
from dataset_step1_foundation import TurkishTelcoFoundation

class MultiStepDialogGenerator(TurkishTelcoFoundation):
    """Generate complex multi-step dialogs with dynamic reasoning and handoffs."""
    
    def __init__(self):
        super().__init__()
        
        # Complex scenario templates
        self.package_change_scenarios = [
            "Paketimi değiştirmek istiyorum, daha uygun seçenekler var mı?",
            "Mevcut tarifem pahalı geliyor, ne önerirsiniz?",
            "Daha fazla internet ihtiyacım var, yükseltebilir miyiz?",
            "Paket değişikliği yapmak istiyorum, seçenekleri görebilir miyim?"
        ]
        
        self.esim_setup_scenarios = [
            "eSIM almak istiyorum, nasıl başlarız?",
            "Yeni eSIM kurulumu için yardım lazım",
            "eSIM aktivasyonu yapmak istiyorum",
            "Telefona eSIM kurmak istiyorum"
        ]
        
        self.billing_dispute_scenarios = [
            "Faturamda hata var gibi, kontrol eder misiniz?",
            "Bu ay fatura yüksek geldi, neden olabilir?",
            "Fatura itirazım var, nasıl çözebiliriz?",
            "Ödeme konusunda sorun yaşıyorum"
        ]
    
    def generate_package_change_dialog(self) -> Dict:
        """Generate complete package change flow with handoff."""
        customer_data = self.generate_customer_data()
        user_intent = random.choice(self.package_change_scenarios)
        
        conversation = [
            # 1. Initial request
            {"role": "user", "content": [{"type": "text", "text": user_intent}]},
            
            # 2. Handoff to PlanAgent
            {"role": "assistant", "content": [{"type": "text", "text": self.create_handoff_json(
                "PlanAgent", "Sizi tarife uzmanımıza bağlıyorum.")}]},
            
            # 3. PlanAgent starts - verify user first
            {"role": "assistant", "content": [{"type": "text", "text": self.create_tool_call_json("verify_user", {
                "maiden_name": customer_data["maiden_name"],
                "msisdn": customer_data["msisdn"]
            })}]},
            
            # 4. Verification result
            {"role": "user", "content": [{"type": "text", "text": self.create_tool_result(True, {
                "customer_id": customer_data["customer_id"],
                "name": customer_data["name"],
                "verified": True
            })}]},
            
            # 5. Get current user info
            {"role": "assistant", "content": [{"type": "text", "text": self.create_tool_call_json("get_user_info", {
                "customer_id": customer_data["customer_id"]
            })}]},
            
            # 6. User info result
            {"role": "user", "content": [{"type": "text", "text": self.create_tool_result(True, {
                "customer_id": customer_data["customer_id"],
                "name": customer_data["name"],
                "current_package": customer_data["current_package"]["name"],
                "package_data": customer_data["current_package"]["data"],
                "contract_end": customer_data["contract_end"],
                "payment_status": customer_data["payment_status"]
            })}]},
            
            # 7. Get available packages
            {"role": "assistant", "content": [{"type": "text", "text": self.create_tool_call_json("get_available_packages", {
                "customer_id": customer_data["customer_id"]
            })}]},
            
            # 8. Package options result
            {"role": "user", "content": [{"type": "text", "text": self.create_tool_result(True, {
                "packages": random.sample(self.packages, 3),
                "current_package": customer_data["current_package"]["name"]
            })}]},
            
            # 9. Present options to customer
            {"role": "assistant", "content": [{"type": "text", "text": 
                f"Merhaba {customer_data['name']}, şu an {customer_data['current_package']['name']} kullanıyorsunuz. Size 3 uygun seçenek buldum, hangisini tercih edersiniz?"}]},
            
            # 10. Customer chooses
            {"role": "user", "content": [{"type": "text", "text": "Premium 10GB paketini seçiyorum."}]},
            
            # 11. Confirm and execute change
            {"role": "assistant", "content": [{"type": "text", "text": self.create_tool_call_json("change_package", {
                "customer_id": customer_data["customer_id"],
                "package_id": "premium_10gb"
            })}]},
            
            # 12. Change result
            {"role": "user", "content": [{"type": "text", "text": self.create_tool_result(True, {
                "old_package": customer_data["current_package"]["name"],
                "new_package": "Premium 10GB",
                "price_difference": 50.00,
                "effective_date": "2024-02-01",
                "confirmation_id": f"PKG-{random.randint(10000, 99999)}"
            })}]},
            
            # 13. Final confirmation
            {"role": "assistant", "content": [{"type": "text", "text": 
                "Paket değişikliğiniz başarıyla tamamlandı. Premium 10GB paketiniz yarın aktif olacak, onay kodunuz gönderildi."}]}
        ]
        
        return {
            "conversations": conversation,
            "scenario_type": "multi_step_package_change",
            "context": "PLAN",
            "has_noise": False,
            "customer_data": customer_data,
            "tools_used": ["verify_user", "get_user_info", "get_available_packages", "change_package"],
            "handoffs": ["PlanAgent"]
        }
    
    def generate_esim_setup_dialog(self) -> Dict:
        """Generate complete eSIM setup flow with technical handoff."""
        customer_data = self.generate_customer_data()
        user_intent = random.choice(self.esim_setup_scenarios)
        os_type = random.choice(["iOS", "Android"])
        
        conversation = [
            # 1. Initial eSIM request
            {"role": "user", "content": [{"type": "text", "text": user_intent}]},
            
            # 2. Handoff to TechAgent
            {"role": "assistant", "content": [{"type": "text", "text": self.create_handoff_json(
                "TechAgent", "Sizi teknik uzmanımıza yönlendiriyorum.")}]},
            
            # 3. Verify user
            {"role": "assistant", "content": [{"type": "text", "text": self.create_tool_call_json("verify_user", {
                "maiden_name": customer_data["maiden_name"],
                "msisdn": customer_data["msisdn"]
            })}]},
            
            # 4. Verification result
            {"role": "user", "content": [{"type": "text", "text": self.create_tool_result(True, {
                "customer_id": customer_data["customer_id"],
                "name": customer_data["name"],
                "verified": True
            })}]},
            
            # 5. Check device compatibility
            {"role": "assistant", "content": [{"type": "text", "text": self.create_tool_call_json("check_device_registration", {
                "imei": customer_data["imei"]
            })}]},
            
            # 6. Device check result
            {"role": "user", "content": [{"type": "text", "text": self.create_tool_result(True, {
                "imei": customer_data["imei"][:5] + "*****" + customer_data["imei"][-3:],
                "registered": True,
                "device_compatible": True,
                "activation_status": "pending"
            })}]},
            
            # 7. Generate activation code
            {"role": "assistant", "content": [{"type": "text", "text": self.create_tool_call_json("reissue_activation_code", {
                "customer_id": customer_data["customer_id"]
            })}]},
            
            # 8. Activation code result
            {"role": "user", "content": [{"type": "text", "text": self.create_tool_result(True, {
                "activation_code": f"LPA:1$sm-dp-plus.example.com${random.randint(100000, 999999)}$activation-code-{customer_data['customer_id']}",
                "qr_code_url": f"/qr/{customer_data['customer_id']}",
                "expires_at": "24 saat",
                "instructions": "Bu kodu eSIM ayarlarından tarayın"
            })}]},
            
            # 9. Get activation steps
            {"role": "assistant", "content": [{"type": "text", "text": self.create_tool_call_json("get_activation_steps", {
                "os_type": os_type
            })}]},
            
            # 10. Steps result
            {"role": "user", "content": [{"type": "text", "text": self.create_tool_result(True, {
                "os_type": os_type,
                "steps": [
                    "1. Ayarlar uygulamasını açın",
                    "2. 'Hücresel' bölümüne gidin",
                    "3. 'eSIM Ekle' seçeneğini seçin",
                    "4. QR kodu tarayın",
                    "5. Aktivasyon tamamlanmasını bekleyin"
                ],
                "estimated_time": "5-10 dakika"
            })}]},
            
            # 11. Provide complete instructions
            {"role": "assistant", "content": [{"type": "text", "text": 
                f"Mükemmel {customer_data['name']}, eSIM kodunuz hazır. {os_type} cihazınız için adım adım kurulum talimatlarını gönderdim, 5-10 dakikada tamamlanır."}]},
            
            # 12. Customer asks about status
            {"role": "user", "content": [{"type": "text", "text": "Kurulumu yaptım, aktif mi kontrol eder misiniz?"}]},
            
            # 13. Check activation status
            {"role": "assistant", "content": [{"type": "text", "text": self.create_tool_call_json("get_activation_status", {
                "customer_id": customer_data["customer_id"]
            })}]},
            
            # 14. Status result
            {"role": "user", "content": [{"type": "text", "text": self.create_tool_result(True, {
                "customer_id": customer_data["customer_id"],
                "current_state": "active",
                "progress_percentage": 100,
                "description": "eSIM başarıyla aktifleştirildi",
                "next_step": "Kullanıma hazır"
            })}]},
            
            # 15. Final confirmation
            {"role": "assistant", "content": [{"type": "text", "text": 
                "Harika! eSIM'iniz başarıyla aktif oldu ve kullanıma hazır. İyi kullanımlar!"}]}
        ]
        
        return {
            "conversations": conversation,
            "scenario_type": "multi_step_esim_setup",
            "context": "SIM",
            "has_noise": False,
            "customer_data": customer_data,
            "tools_used": ["verify_user", "check_device_registration", "reissue_activation_code", "get_activation_steps", "get_activation_status"],
            "handoffs": ["TechAgent"],
            "os_type": os_type
        }
    
    def generate_billing_dispute_dialog(self) -> Dict:
        """Generate billing dispute resolution flow."""
        customer_data = self.generate_customer_data()
        user_intent = random.choice(self.billing_dispute_scenarios)
        
        conversation = [
            # 1. Billing complaint
            {"role": "user", "content": [{"type": "text", "text": user_intent}]},
            
            # 2. Handoff to BillingAgent
            {"role": "assistant", "content": [{"type": "text", "text": self.create_handoff_json(
                "BillingAgent", "Sizi faturalama uzmanımıza bağlıyorum.")}]},
            
            # 3. Verify user for financial data
            {"role": "assistant", "content": [{"type": "text", "text": self.create_tool_call_json("verify_user", {
                "maiden_name": customer_data["maiden_name"],
                "msisdn": customer_data["msisdn"]
            })}]},
            
            # 4. Verification result
            {"role": "user", "content": [{"type": "text", "text": self.create_tool_result(True, {
                "customer_id": customer_data["customer_id"],
                "name": customer_data["name"],
                "verified": True
            })}]},
            
            # 5. Get detailed user info including billing
            {"role": "assistant", "content": [{"type": "text", "text": self.create_tool_call_json("get_user_info", {
                "customer_id": customer_data["customer_id"]
            })}]},
            
            # 6. User info with billing details
            {"role": "user", "content": [{"type": "text", "text": self.create_tool_result(True, {
                "customer_id": customer_data["customer_id"],
                "name": customer_data["name"],
                "current_package": customer_data["current_package"]["name"],
                "payment_status": customer_data["payment_status"],
                "last_payment": "2024-01-15",
                "outstanding_amount": random.uniform(0, 200),
                "billing_cycle": "Monthly"
            })}]},
            
            # 7. Explain findings and create support ticket
            {"role": "assistant", "content": [{"type": "text", "text": self.create_tool_call_json("create_support_ticket", {
                "customer_id": customer_data["customer_id"],
                "subject": "Fatura İtirazı",
                "description": "Müşteri fatura tutarında hata olduğunu belirtiyor, detaylı inceleme gerekli",
                "priority": "medium"
            })}]},
            
            # 8. Ticket creation result
            {"role": "user", "content": [{"type": "text", "text": self.create_tool_result(True, {
                "ticket_id": f"TKT-{random.randint(10000, 99999)}",
                "status": "open",
                "priority": "medium",
                "estimated_resolution": "24-48 saat içinde"
            })}]},
            
            # 9. Final resolution
            {"role": "assistant", "content": [{"type": "text", "text": 
                f"Fatura itirazınız kayıt altına alındı, {customer_data['name']}. 24-48 saat içinde detaylı inceleme sonucu size dönüş yapacağız."}]}
        ]
        
        return {
            "conversations": conversation,
            "scenario_type": "multi_step_billing_dispute",
            "context": "BILLING",
            "has_noise": False,
            "customer_data": customer_data,
            "tools_used": ["verify_user", "get_user_info", "create_support_ticket"],
            "handoffs": ["BillingAgent"]
        }
    
    def generate_multi_step_dialog(self) -> Dict:
        """Generate random multi-step dialog."""
        generators = [
            self.generate_package_change_dialog,
            self.generate_esim_setup_dialog,
            self.generate_billing_dispute_dialog
        ]
        
        generator = random.choice(generators)
        return generator()

print("✅ Step 5: Multi-step dialog generators ready")
