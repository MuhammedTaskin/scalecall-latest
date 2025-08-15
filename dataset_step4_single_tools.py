"""
Step 4: Single Tool Call Dialogs
Dynamic tool selection with reasoning
"""
import random
from typing import List, Dict
from dataset_step1_foundation import TurkishTelcoFoundation

class SingleToolDialogGenerator(TurkishTelcoFoundation):
    """Generate dialogs with single tool calls and dynamic reasoning."""
    
    def __init__(self):
        super().__init__()
        
        # Tool call scenarios with natural Turkish intents
        self.verification_scenarios = [
            {
                "user_intent": "Kimlik doğrulama yapmak istiyorum",
                "natural_variations": [
                    "Kendimi doğrulatmak istiyorum",
                    "Kimliğimi onaylatabilir miyim?",
                    "Doğrulama yapmanız gerekiyor mu?",
                    "İşlem için kimlik kontrolü lazım mı?"
                ]
            },
            {
                "user_intent": "Hesabıma girmek istiyorum",
                "natural_variations": [
                    "Hesap bilgilerimi görmek istiyorum",
                    "Bilgilerimi kontrol etmek istiyorum",
                    "Hesabımı görüntüleyebilir miyim?"
                ]
            }
        ]
        
        self.device_scenarios = [
            {
                "user_intent": "Cihazımı kontrol ettirin",
                "natural_variations": [
                    "IMEI numaram kayıtlı mı?",
                    "Telefonum eSIM destekliyor mu?",
                    "Cihaz uyumluluğunu kontrol edin",
                    "Bu telefon çalışır mı sizde?"
                ]
            }
        ]
        
        self.activation_scenarios = [
            {
                "user_intent": "Aktivasyon kodu istiyorum",
                "natural_variations": [
                    "eSIM kodu lazım",
                    "QR kod gönderebilir misiniz?",
                    "Yeni aktivasyon kodu",
                    "Kod süresi dolmuş, yenisini alabilir miyim?"
                ]
            }
        ]
        
        self.package_inquiry_scenarios = [
            {
                "user_intent": "Paket seçeneklerini görmek istiyorum",
                "natural_variations": [
                    "Hangi paketleriniz var?",
                    "Mevcut tarifeler neler?",
                    "Paket listesini alabilir miyim?",
                    "Ne tür planlarınız var?"
                ]
            }
        ]
    
    def generate_verification_dialog(self, customer_data: Dict) -> List[Dict]:
        """Generate verification dialog with dynamic tool calling."""
        scenario = random.choice(self.verification_scenarios)
        user_text = random.choice([scenario["user_intent"]] + scenario["natural_variations"])
        
        # Tool call
        tool_call = self.create_tool_call_json("verify_user", {
            "maiden_name": customer_data["maiden_name"],
            "msisdn": customer_data["msisdn"]
        })
        
        # Tool result
        tool_result = self.create_tool_result(True, {
            "customer_id": customer_data["customer_id"],
            "name": customer_data["name"],
            "verified": True
        })
        
        # Natural response
        responses = [
            f"Kimlik doğrulama başarılı, {customer_data['name']} hanım/bey. Size nasıl yardımcı olabilirim?",
            f"Doğrulama tamam, {customer_data['name']}. Hangi işlemi yapmak istiyorsunuz?",
            f"Merhaba {customer_data['name']}, kimliğiniz onaylandı. Devam edebiliriz."
        ]
        
        return [
            {"role": "user", "content": [{"type": "text", "text": user_text}]},
            {"role": "assistant", "content": [{"type": "text", "text": tool_call}]},
            {"role": "user", "content": [{"type": "text", "text": tool_result}]},
            {"role": "assistant", "content": [{"type": "text", "text": random.choice(responses)}]}
        ]
    
    def generate_device_check_dialog(self, customer_data: Dict) -> List[Dict]:
        """Generate device check dialog."""
        scenario = random.choice(self.device_scenarios)
        user_text = random.choice([scenario["user_intent"]] + scenario["natural_variations"])
        
        # Sometimes include IMEI in user message
        if random.choice([True, False]):
            user_text += f" IMEI: {customer_data['imei']}"
        
        tool_call = self.create_tool_call_json("check_device_registration", {
            "imei": customer_data["imei"]
        })
        
        is_registered = random.choice([True, False])
        tool_result = self.create_tool_result(True, {
            "imei": customer_data["imei"][:5] + "*****" + customer_data["imei"][-3:],
            "registered": is_registered,
            "device_compatible": True,
            "activation_status": customer_data["activation_status"]
        })
        
        if is_registered:
            responses = [
                "Cihazınız kayıtlı ve eSIM uyumlu. Aktivasyon işlemine geçebiliriz.",
                "Telefonunuz sistemimizde mevcut. eSIM kurulumu yapabiliriz.",
                "Cihaz kontrolü tamam. Aktivasyon kodunuzu hazırlayabilirim."
            ]
        else:
            responses = [
                "Cihazınız henüz kayıtlı değil ama eSIM uyumlu. Kayıt işlemini başlatayım mı?",
                "Yeni cihaz tespit ettim. Kayıt için gerekli işlemleri yapabiliriz.",
                "Bu telefon henüz sistemde yok. Ekleyip aktivasyon yapalım."
            ]
        
        return [
            {"role": "user", "content": [{"type": "text", "text": user_text}]},
            {"role": "assistant", "content": [{"type": "text", "text": tool_call}]},
            {"role": "user", "content": [{"type": "text", "text": tool_result}]},
            {"role": "assistant", "content": [{"type": "text", "text": random.choice(responses)}]}
        ]
    
    def generate_activation_code_dialog(self, customer_data: Dict) -> List[Dict]:
        """Generate activation code request dialog."""
        scenario = random.choice(self.activation_scenarios)
        user_text = random.choice([scenario["user_intent"]] + scenario["natural_variations"])
        
        tool_call = self.create_tool_call_json("reissue_activation_code", {
            "customer_id": customer_data["customer_id"]
        })
        
        lpa_code = f"LPA:1$sm-dp-plus.example.com${random.randint(100000, 999999)}$activation-code-{customer_data['customer_id']}"
        tool_result = self.create_tool_result(True, {
            "activation_code": lpa_code,
            "qr_code_url": f"/qr/{customer_data['customer_id']}",
            "expires_at": "24 saat",
            "instructions": "Bu kodu eSIM ayarlarından tarayın veya manuel olarak girin"
        })
        
        responses = [
            "Yeni aktivasyon kodunuz hazır. QR kod veya manuel giriş ile kullanabilirsiniz.",
            "eSIM kodunuz oluşturuldu. 24 saat geçerli, hemen kullanabilirsiniz.",
            "Aktivasyon kodu gönderildi. Telefon ayarlarından tarayabilirsiniz."
        ]
        
        return [
            {"role": "user", "content": [{"type": "text", "text": user_text}]},
            {"role": "assistant", "content": [{"type": "text", "text": tool_call}]},
            {"role": "user", "content": [{"type": "text", "text": tool_result}]},
            {"role": "assistant", "content": [{"type": "text", "text": random.choice(responses)}]}
        ]
    
    def generate_package_inquiry_dialog(self, customer_data: Dict) -> List[Dict]:
        """Generate package inquiry dialog."""
        scenario = random.choice(self.package_inquiry_scenarios)
        user_text = random.choice([scenario["user_intent"]] + scenario["natural_variations"])
        
        tool_call = self.create_tool_call_json("get_available_packages", {
            "customer_id": customer_data["customer_id"]
        })
        
        # Select 2-3 available packages
        available_packages = random.sample(self.packages, random.randint(2, 3))
        tool_result = self.create_tool_result(True, {
            "packages": available_packages,
            "current_package": customer_data["current_package"]["name"]
        })
        
        responses = [
            f"Mevcut {len(available_packages)} paket seçeneğiniz var. Hangisi ilginizi çekiyor?",
            f"Size uygun {len(available_packages)} tarife buldum. Detaylarını açıklayayım mı?",
            f"Şu an {len(available_packages)} farklı paket mevcut. Karşılaştırma yapalım mı?"
        ]
        
        return [
            {"role": "user", "content": [{"type": "text", "text": user_text}]},
            {"role": "assistant", "content": [{"type": "text", "text": tool_call}]},
            {"role": "user", "content": [{"type": "text", "text": tool_result}]},
            {"role": "assistant", "content": [{"type": "text", "text": random.choice(responses)}]}
        ]
    
    def generate_single_tool_dialog(self) -> Dict:
        """Generate random single tool dialog."""
        customer_data = self.generate_customer_data()
        
        dialog_generators = [
            self.generate_verification_dialog,
            self.generate_device_check_dialog,
            self.generate_activation_code_dialog,
            self.generate_package_inquiry_dialog
        ]
        
        generator = random.choice(dialog_generators)
        conversation = generator(customer_data)
        
        return {
            "conversations": conversation,
            "scenario_type": "single_tool",
            "context": random.choice(["SIM", "PLAN", "BILLING", "COVERAGE"]),
            "has_noise": False,
            "customer_data": customer_data
        }

print("✅ Step 4: Single tool dialog generators ready")
