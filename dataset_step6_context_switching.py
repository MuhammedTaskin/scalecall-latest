"""
Step 6: Advanced Context Switching Dialogs
Handling interruptions and topic changes mid-conversation
"""
import random
from typing import List, Dict
from dataset_step1_foundation import TurkishTelcoFoundation

class ContextSwitchingGenerator(TurkishTelcoFoundation):
    """Generate dialogs with context switches and interruption handling."""
    
    def __init__(self):
        super().__init__()
        
        # Context switch scenarios - customer changes topic mid-conversation
        self.interruption_scenarios = [
            {
                "initial_topic": "package_change",
                "interrupt_topic": "billing_complaint",
                "interrupt_phrases": [
                    "Aslında bekleyin, faturamda bir sorun var önce onu halledebilir miyiz?",
                    "Dur bir dakika, fatura konusu daha acil, onu konuşalım",
                    "Şimdi fark ettim, bu ay fatura çok yüksek gelmiş, ne yapacağız?"
                ]
            },
            {
                "initial_topic": "esim_activation", 
                "interrupt_topic": "device_issue",
                "interrupt_phrases": [
                    "Bekleyin, telefonum eSIM destekliyor mu emin değilim",
                    "Dur, önce cihazımı kontrol edin destekliyor mu",
                    "Aslında IMEI kontrolü yapabilir misiniz önce?"
                ]
            },
            {
                "initial_topic": "billing_inquiry",
                "interrupt_topic": "urgent_activation",
                "interrupt_phrases": [
                    "Pardon, daha acil bir durum var, eSIM'im çalışmıyor",
                    "Aslında fatura sonra, şu an internete bağlanamıyorum",
                    "Bekleyin, önce aktivasyon sorunu çözelim, acele var"
                ]
            },
            {
                "initial_topic": "package_inquiry",
                "interrupt_topic": "technical_support",
                "interrupt_phrases": [
                    "Dur bir saniye, sinyal problemi yaşıyorum önce onu çözelim",
                    "Aslında paket değil, kapsama sorunu var sanırım",
                    "Bekleyin, internet çekmiyor telefonum, bu daha önemli"
                ]
            }
        ]
        
        # Recovery phrases for agents
        self.recovery_phrases = [
            "Tabii ki, şimdi o konuya odaklanalım.",
            "Anlıyorum, önce bu sorunu çözelim.",
            "Elbette, daha acil konuyu halledebiliriz.",
            "Tamam, o konu öncelikli, hemen bakalım."
        ]
    
    def generate_package_to_billing_switch(self) -> Dict:
        """Generate package change interrupted by billing issue."""
        customer_data = self.generate_customer_data()
        interrupt_phrase = random.choice([
            "Aslında bekleyin, faturamda bir sorun var önce onu halledebilir miyiz?",
            "Dur bir dakika, fatura konusu daha acil, onu konuşalım"
        ])
        
        conversation = [
            # 1. Initial package inquiry
            {"role": "user", "content": [{"type": "text", "text": "Paket seçeneklerimi görmek istiyorum"}]},
            
            # 2. Start verification for package change
            {"role": "assistant", "content": [{"type": "text", "text": self.create_tool_call_json("verify_user", {
                "maiden_name": customer_data["maiden_name"],
                "msisdn": customer_data["msisdn"]
            })}]},
            
            # 3. Verification result
            {"role": "user", "content": [{"type": "text", "text": self.create_tool_result(True, {
                "customer_id": customer_data["customer_id"],
                "name": customer_data["name"],
                "verified": True
            })}]},
            
            # 4. About to get packages, but customer interrupts
            {"role": "assistant", "content": [{"type": "text", "text": "Mükemmel, şimdi size uygun paketleri getiriyorum..."}]},
            
            # 5. CONTEXT SWITCH - Customer interrupts with billing issue
            {"role": "user", "content": [{"type": "text", "text": interrupt_phrase}]},
            
            # 6. Agent acknowledges switch and handoff to BillingAgent
            {"role": "assistant", "content": [{"type": "text", "text": "Tabii ki, fatura konusu daha acil. " + self.create_handoff_json("BillingAgent", "Faturalama uzmanımıza geçiyorum.")}]},
            
            # 7. Get user info for billing context
            {"role": "assistant", "content": [{"type": "text", "text": self.create_tool_call_json("get_user_info", {
                "customer_id": customer_data["customer_id"]
            })}]},
            
            # 8. User info result
            {"role": "user", "content": [{"type": "text", "text": self.create_tool_result(True, {
                "customer_id": customer_data["customer_id"],
                "name": customer_data["name"],
                "current_package": customer_data["current_package"]["name"],
                "payment_status": "overdue",
                "last_payment": "2024-01-01",
                "outstanding_amount": 275.50
            })}]},
            
            # 9. Address billing issue
            {"role": "assistant", "content": [{"type": "text", "text": 
                f"Görüyorum ki 275.50 TL ödenmemiş borcunuz var. Ödeme planı yapabiliriz, nasıl ilerlemek istersiniz?"}]},
            
            # 10. Customer resolves billing first
            {"role": "user", "content": [{"type": "text", "text": "Şimdi ödeme yapayım, sonra paket konusuna dönelim"}]},
            
            # 11. Agent acknowledges and prepares for topic return
            {"role": "assistant", "content": [{"type": "text", "text": 
                "Mükemmel, ödeme sonrası paket seçeneklerini size sunabilirim. Önce ödeme işleminizi tamamlayın."}]}
        ]
        
        return {
            "conversations": conversation,
            "scenario_type": "context_switch_package_to_billing",
            "context": "MIXED",
            "has_noise": False,
            "customer_data": customer_data,
            "initial_intent": "package_inquiry",
            "switched_intent": "billing_issue",
            "handoffs": ["BillingAgent"],
            "context_switches": 1
        }
    
    def generate_esim_to_device_switch(self) -> Dict:
        """Generate eSIM activation interrupted by device compatibility question."""
        customer_data = self.generate_customer_data()
        
        conversation = [
            # 1. eSIM activation request
            {"role": "user", "content": [{"type": "text", "text": "eSIM aktivasyon yapmak istiyorum"}]},
            
            # 2. Handoff to TechAgent
            {"role": "assistant", "content": [{"type": "text", "text": self.create_handoff_json("TechAgent", "Teknik uzmanımıza yönlendiriyorum.")}]},
            
            # 3. Start verification
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
            
            # 5. About to proceed with activation
            {"role": "assistant", "content": [{"type": "text", "text": "Harika, şimdi aktivasyon kodunuzu hazırlıyorum..."}]},
            
            # 6. CONTEXT SWITCH - Device compatibility concern
            {"role": "user", "content": [{"type": "text", "text": "Bekleyin, telefonum eSIM destekliyor mu emin değilim, önce kontrol eder misiniz?"}]},
            
            # 7. Agent switches to device check
            {"role": "assistant", "content": [{"type": "text", "text": "Elbette, önce cihaz uyumluluğunu kontrol edelim. " + self.create_tool_call_json("check_device_registration", {
                "imei": customer_data["imei"]
            })}]},
            
            # 8. Device check result
            {"role": "user", "content": [{"type": "text", "text": self.create_tool_result(True, {
                "imei": customer_data["imei"][:5] + "*****" + customer_data["imei"][-3:],
                "registered": True,
                "device_compatible": True,
                "activation_status": "ready"
            })}]},
            
            # 9. Confirm compatibility and return to original flow
            {"role": "assistant", "content": [{"type": "text", "text": 
                "Mükemmel! Cihazınız eSIM uyumlu ve sisteme kayıtlı. Şimdi aktivasyon kodunuzu hazırlayabilirim."}]},
            
            # 10. Continue with original activation flow
            {"role": "assistant", "content": [{"type": "text", "text": self.create_tool_call_json("reissue_activation_code", {
                "customer_id": customer_data["customer_id"]
            })}]},
            
            # 11. Activation code result
            {"role": "user", "content": [{"type": "text", "text": self.create_tool_result(True, {
                "activation_code": f"LPA:1$sm-dp-plus.example.com${random.randint(100000, 999999)}",
                "qr_code_url": f"/qr/{customer_data['customer_id']}",
                "expires_at": "24 saat"
            })}]},
            
            # 12. Complete activation flow
            {"role": "assistant", "content": [{"type": "text", "text": 
                "eSIM kodunuz hazır! Cihaz uyumlu olduğunu doğruladığımıza göre sorunsuz aktifleştirebilirsiniz."}]}
        ]
        
        return {
            "conversations": conversation,
            "scenario_type": "context_switch_esim_to_device",
            "context": "SIM",
            "has_noise": False,
            "customer_data": customer_data,
            "initial_intent": "esim_activation",
            "switched_intent": "device_check",
            "handoffs": ["TechAgent"],
            "context_switches": 1
        }
    
    def generate_urgent_priority_switch(self) -> Dict:
        """Generate dialog where customer switches to urgent priority issue."""
        customer_data = self.generate_customer_data()
        
        conversation = [
            # 1. Normal billing inquiry
            {"role": "user", "content": [{"type": "text", "text": "Fatura detaylarımı görebilir miyim?"}]},
            
            # 2. Start normal flow
            {"role": "assistant", "content": [{"type": "text", "text": self.create_tool_call_json("verify_user", {
                "maiden_name": customer_data["maiden_name"],
                "msisdn": customer_data["msisdn"]
            })}]},
            
            # 3. Verification result
            {"role": "user", "content": [{"type": "text", "text": self.create_tool_result(True, {
                "customer_id": customer_data["customer_id"],
                "name": customer_data["name"],
                "verified": True
            })}]},
            
            # 4. URGENT CONTEXT SWITCH - Service outage
            {"role": "user", "content": [{"type": "text", "text": "Pardon, daha acil bir durum var! İnternetim hiç çalışmıyor, toplantıya giremiyorum!"}]},
            
            # 5. Agent prioritizes urgent issue and handoff
            {"role": "assistant", "content": [{"type": "text", "text": "Anlıyorum, bu acil durum! " + self.create_handoff_json("TechAgent", "Hemen teknik uzmanımıza bağlıyorum.")}]},
            
            # 6. Check device status for connectivity
            {"role": "assistant", "content": [{"type": "text", "text": self.create_tool_call_json("check_device_registration", {
                "imei": customer_data["imei"]
            })}]},
            
            # 7. Device status - shows issue
            {"role": "user", "content": [{"type": "text", "text": self.create_tool_result(True, {
                "imei": customer_data["imei"][:5] + "*****" + customer_data["imei"][-3:],
                "registered": True,
                "device_compatible": True,
                "activation_status": "connection_error",
                "last_connection": "2024-01-20 08:00"
            })}]},
            
            # 8. Check activation status
            {"role": "assistant", "content": [{"type": "text", "text": self.create_tool_call_json("get_activation_status", {
                "customer_id": customer_data["customer_id"]
            })}]},
            
            # 9. Status shows problem
            {"role": "user", "content": [{"type": "text", "text": self.create_tool_result(True, {
                "customer_id": customer_data["customer_id"],
                "current_state": "failed",
                "progress_percentage": 0,
                "description": "Bağlantı hatası tespit edildi",
                "next_step": "Yeniden aktivasyon gerekli"
            })}]},
            
            # 10. Create urgent support ticket
            {"role": "assistant", "content": [{"type": "text", "text": self.create_tool_call_json("create_support_ticket", {
                "customer_id": customer_data["customer_id"],
                "subject": "ACİL: İnternet Bağlantı Sorunu",
                "description": "Müşteri toplantı nedeniyle acil internet erişimi ihtiyacı bildiriyor",
                "priority": "high"
            })}]},
            
            # 11. Ticket created
            {"role": "user", "content": [{"type": "text", "text": self.create_tool_result(True, {
                "ticket_id": f"URG-{random.randint(10000, 99999)}",
                "status": "high_priority",
                "priority": "high",
                "estimated_resolution": "30 dakika içinde"
            })}]},
            
            # 12. Immediate resolution steps
            {"role": "assistant", "content": [{"type": "text", "text": 
                "Acil destek kaydınız oluşturuldu! 30 dakika içinde çözüm sağlayacağız. Şimdi yeniden aktivasyon deneyebiliriz."}]}
        ]
        
        return {
            "conversations": conversation,
            "scenario_type": "urgent_priority_switch",
            "context": "MIXED",
            "has_noise": False,
            "customer_data": customer_data,
            "initial_intent": "billing_inquiry",
            "switched_intent": "urgent_technical",
            "handoffs": ["TechAgent"],
            "context_switches": 1,
            "urgency_level": "high"
        }
    
    def generate_context_switch_dialog(self) -> Dict:
        """Generate random context switching dialog."""
        generators = [
            self.generate_package_to_billing_switch,
            self.generate_esim_to_device_switch,
            self.generate_urgent_priority_switch
        ]
        
        generator = random.choice(generators)
        return generator()

print("✅ Step 6: Context switching generators ready")
