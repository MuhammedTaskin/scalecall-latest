"""
Step 3: Simple Dialog Generators
Basic Q&A patterns for foundation training
"""
import random
from typing import List, Dict

class SimpleDialogGenerator:
    """Generate simple Turkish telco Q&A dialogs."""
    
    def __init__(self):
        self.greeting_patterns = [
            {
                "user": "Merhaba, yardım alabilir miyim?",
                "assistant": "Merhaba! eSIM hizmetlerimiz için size nasıl yardımcı olabilirim?"
            },
            {
                "user": "İyi günler, bilgi almak istiyorum.",
                "assistant": "İyi günler! Hangi konuda bilgi almak istiyorsunuz?"
            },
            {
                "user": "Selam, paket hakkında soru sormak istiyorum.",
                "assistant": "Selam! Paket konusunda size yardımcı olmaktan memnuniyet duyarım."
            }
        ]
        
        self.faq_patterns = [
            {
                "user": "eSIM nedir?",
                "assistant": "eSIM, fiziksel SIM kart olmadan telefon hattı kullanabileceğiniz dijital SIM teknolojisidir. Destekleyen cihazlarda hızlıca aktifleştirilebilir."
            },
            {
                "user": "Hangi cihazlar eSIM destekliyor?",
                "assistant": "iPhone XS ve sonrası, Samsung Galaxy S20+, Google Pixel serisi gibi yeni cihazlar eSIM'i destekler. Cihazınızın uyumluluğunu kontrol edebilirim."
            },
            {
                "user": "Kapsama alanınız nereler?",
                "assistant": "Türkiye genelinde 4.5G ve 5G kapsama sağlıyoruz. Hangi şehir için özel bilgi istiyorsunuz?"
            },
            {
                "user": "Fiyatlar nasıl?",
                "assistant": "Paket fiyatlarımız 59.99 TL'den başlıyor. Size uygun paketi bulmak için tercihlerinizi öğrenebilir miyim?"
            },
            {
                "user": "Aktivasyon ne kadar sürer?",
                "assistant": "eSIM aktivasyonu genellikle 5-10 dakika sürer. QR kod tarayarak hemen başlayabilirsiniz."
            },
            {
                "user": "Müşteri hizmetleri saatleri neler?",
                "assistant": "7/24 hizmet veriyoruz. İstediğiniz zaman bize ulaşabilirsiniz."
            },
            {
                "user": "İptal etmek istersem ne yapmalıyım?",
                "assistant": "İptal işlemi için kimlik doğrulaması gerekir. Size yardımcı olayım mı?"
            },
            {
                "user": "Yurtdışında kullanabilir miyim?",
                "assistant": "Evet, roaming paketlerimiz ile yurtdışında da kullanabilirsiniz. Hangi ülkeye gideceksiniz?"
            }
        ]
        
        self.coverage_patterns = [
            {
                "user": "İstanbul'da sinyal var mı?",
                "assistant": "İstanbul'da mükemmel 5G kapsaması sağlıyoruz. Hangi ilçeyi merak ediyorsunuz?"
            },
            {
                "user": "Ankara'da hız nasıl?",
                "assistant": "Ankara'da ortalama 100+ Mbps hız alıyoruz. Konum bazlı detay kontrol edebilirim."
            },
            {
                "user": "Kırsal alanda çekiyor mu?",
                "assistant": "Kırsal alanlarda da geniş kapsama sağlıyoruz. Hangi bölgeyi soruyorsunuz?"
            }
        ]
        
        self.general_support_patterns = [
            {
                "user": "Şifremi unuttum.",
                "assistant": "Şifre sıfırlama için kimlik doğrulaması yapalım. Size yardımcı olayım."
            },
            {
                "user": "Hesabım neden kilitlendi?",
                "assistant": "Hesap kilit sebeplerini kontrol edeyim. Önce kimliğinizi doğrulamamız gerekir."
            },
            {
                "user": "Faturam neden yüksek?",
                "assistant": "Fatura detaylarını inceleyebilirim. Kimlik doğrulaması sonrası açıklayabilirim."
            }
        ]
    
    def generate_greeting_dialog(self) -> List[Dict]:
        """Generate greeting conversation."""
        pattern = random.choice(self.greeting_patterns)
        return [
            {"role": "user", "content": [{"type": "text", "text": pattern["user"]}]},
            {"role": "assistant", "content": [{"type": "text", "text": pattern["assistant"]}]}
        ]
    
    def generate_faq_dialog(self) -> List[Dict]:
        """Generate FAQ conversation."""
        pattern = random.choice(self.faq_patterns)
        return [
            {"role": "user", "content": [{"type": "text", "text": pattern["user"]}]},
            {"role": "assistant", "content": [{"type": "text", "text": pattern["assistant"]}]}
        ]
    
    def generate_coverage_dialog(self) -> List[Dict]:
        """Generate coverage inquiry conversation."""
        pattern = random.choice(self.coverage_patterns)
        return [
            {"role": "user", "content": [{"type": "text", "text": pattern["user"]}]},
            {"role": "assistant", "content": [{"type": "text", "text": pattern["assistant"]}]}
        ]
    
    def generate_support_dialog(self) -> List[Dict]:
        """Generate general support conversation."""
        pattern = random.choice(self.general_support_patterns)
        return [
            {"role": "user", "content": [{"type": "text", "text": pattern["user"]}]},
            {"role": "assistant", "content": [{"type": "text", "text": pattern["assistant"]}]}
        ]
    
    def generate_simple_dialog(self) -> List[Dict]:
        """Generate random simple dialog."""
        dialog_types = [
            self.generate_greeting_dialog,
            self.generate_faq_dialog,
            self.generate_coverage_dialog,
            self.generate_support_dialog
        ]
        
        generator = random.choice(dialog_types)
        return generator()

print("✅ Step 3: Simple dialog generators ready")
