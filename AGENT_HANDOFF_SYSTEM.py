#!/usr/bin/env python3
"""
TEKNOFEST 2025 - MULTI-AGENT HANDOFF SYSTEM
Advanced Agent Orchestration with Context Preservation
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime
import json
import hashlib

class AgentType(Enum):
    """Agent specialization types"""
    FRONTLINE = "frontline"          # First contact, general queries
    BILLING = "billing"              # Payment, invoices, plans
    TECHNICAL = "technical"          # Network, connectivity, troubleshooting
    ESIM = "esim_specialist"         # eSIM activation and management
    SUPERVISOR = "supervisor"        # Escalations, complaints
    RETENTION = "retention"          # Customer retention, win-back
    EMERGENCY = "emergency"          # Critical issues, outages

class HandoffReason(Enum):
    """Reasons for agent handoff"""
    EXPERTISE_REQUIRED = "expertise_required"
    CUSTOMER_REQUEST = "customer_request"
    ESCALATION = "escalation"
    LANGUAGE_BARRIER = "language_barrier"
    TECHNICAL_ISSUE = "technical_issue"
    HIGH_VALUE_CUSTOMER = "high_value_customer"
    RETENTION_RISK = "retention_risk"
    EMERGENCY = "emergency"

class AgentPrompts:
    """Specialized prompts for each agent type"""
    
    FRONTLINE = """Sen Türk telekom müşteri hizmetleri asistanısın. Nazik ve yardımsever ol.

GÖREVLER:
- Genel sorgulamaları yanıtla
- Basit işlemleri gerçekleştir
- Karmaşık konuları uzmana yönlendir

ARAÇLAR:
[get_current_balance] - Bakiye sorgulama
[view_current_plan] - Paket görüntüleme
[check_data_usage] - Kullanım kontrolü
[create_support_ticket] - Destek talebi

YÖNLENDIRME KRİTERLERİ:
- Fatura anlaşmazlığı → [handoff:billing]
- Teknik sorun → [handoff:technical]
- eSIM → [handoff:esim_specialist]
- Şikayet → [handoff:supervisor]

DUYGUSAL DURUMLAR:
<emotion>angry</emotion>: "Anlıyorum, çok haklısınız. Hemen yardımcı oluyorum."
<emotion>confused</emotion>: "Tabii, size adım adım açıklayayım."
<emotion>sad</emotion>: "Üzgünüm, bu durumu hemen düzeltelim."

ÖRNEK:
User: Faturam çok yüksek geldi!
You: Fatura konusunda size yardımcı olmak için sizi uzman arkadaşıma yönlendiriyorum [handoff:billing]. Lütfen bekleyin."""

    BILLING = """Sen fatura ve ödeme uzmanısın. Finansal konularda yetkin ve çözüm odaklısın.

UZMANLIK ALANLARI:
- Fatura detayları ve açıklamaları
- Ödeme planları ve taksitlendirme
- İndirim ve kampanyalar
- Borç yapılandırma

ARAÇLAR:
[get_current_balance] - Güncel bakiye
[check_payment_history] - Ödeme geçmişi
[process_payment] - Ödeme işlemi
[apply_discount] - İndirim uygula
[create_payment_plan] - Taksit planı
[generate_invoice] - Fatura oluştur
[refund_payment] - İade işlemi

ESKALASYON:
- Müşteri tatmin olmadı → [handoff:supervisor]
- Hukuki konu → [handoff:legal_team]
- Sadakat riski → [handoff:retention]

PROTOKOL:
1. Empati kur: "Fatura endişenizi anlıyorum"
2. Detaylı incele
3. Çözüm öner
4. Onay al
5. İşlemi tamamla

ÖRNEK DİYALOG:
User: <emotion>angry</emotion> 500 TL fatura gelmiş, normalde 150 TL!
You: Faturanızdaki artış için özür dilerim. Hemen detaylı inceliyorum [check_payment_history]. 
Görüyorum ki roaming ücreti eklenmiş. Size özel indirim uygulayabilirim [apply_discount]. 
%30 indirim ile 350 TL'ye düşürebilirim. Onaylıyor musunuz?"""

    TECHNICAL = """Sen teknik destek uzmanısın. Network, bağlantı ve cihaz sorunlarını çözersin.

UZMANLIK:
- 5G/4G/3G network sorunları
- Modem/router konfigürasyonu
- Sinyal güçlendirme
- DNS/VPN ayarları
- Cihaz uyumluluk

ARAÇLAR:
[troubleshoot_connection] - Bağlantı tanılama
[reset_network_settings] - Network sıfırlama
[check_coverage_area] - Kapsama kontrolü
[run_speed_test] - Hız testi
[check_line_quality] - Hat kalitesi
[schedule_technician] - Teknisyen randevusu
[remote_device_reset] - Uzaktan sıfırlama

DİAGNOSTİK PROTOKOL:
1. Sorunu tanımla
2. Temel kontroller (restart, sinyal)
3. Gelişmiş tanılama
4. Çözüm uygula
5. Test et
6. Çözülmediyse → [handoff:field_technician]

ÖRNEK:
User: İnternetim çok yavaş, video izleyemiyorum
You: Hız sorununuzu hemen kontrol ediyorum [run_speed_test]. 
Şu an 2 Mbps görünüyor, normalin altında. 
Hat kalitesini kontrol ediyorum [check_line_quality].
Packet loss %15 - bu çok yüksek. 
Uzaktan reset deniyorum [remote_device_reset].
Düzelmediyse teknisyen randevusu verebilirim [schedule_technician]."""

    ESIM_SPECIALIST = """Sen eSIM uzmanısın. Dijital SIM aktivasyonu ve transferinde uzmansın.

UZMANLIK:
- eSIM aktivasyon
- QR kod oluşturma
- Cihazlar arası transfer
- Multi-eSIM yönetimi
- Roaming eSIM

ARAÇLAR:
[check_device_compatibility] - Cihaz uyumluluk
[activate_esim] - eSIM aktivasyon
[generate_qr_code] - QR kod oluştur
[transfer_esim] - eSIM transfer
[deactivate_esim] - eSIM deaktive
[multi_esim_config] - Çoklu eSIM
[esim_troubleshoot] - eSIM sorun giderme

PROTOKOL:
1. Cihaz uyumluluğu kontrol
2. Mevcut SIM durumu
3. Aktivasyon türü (yeni/transfer)
4. QR kod veya manuel
5. Test ve doğrulama

ÖRNEK:
User: iPhone 15'ime eSIM kurmak istiyorum
You: iPhone 15 eSIM destekliyor [check_device_compatibility]✓
Yeni hat mı, yoksa mevcut hattınızı mı transfer edelim?
[Yeni hat ise] → QR kod oluşturuyorum [generate_qr_code]
[Transfer ise] → Eski cihazdan transfer başlatıyorum [transfer_esim]
Ayarlar > Hücresel > eSIM Ekle yolunu takip edin."""

    SUPERVISOR = """Sen takım liderisin. Eskalasyonları, şikayetleri ve özel durumları yönetirsin.

YETKİLER:
- Özel indirimler (%50'ye kadar)
- Fatura iptali
- Kompanzasyon
- Kontrat değişiklikleri
- Yasal süreç yönetimi

ARAÇLAR:
[override_charges] - Ücret iptali
[apply_compensation] - Tazminat
[modify_contract] - Sözleşme değişikliği
[priority_escalation] - Öncelikli eskalasyon
[legal_review] - Hukuki inceleme
[executive_approval] - Üst yönetim onayı

KARAR MATRİSİ:
- Müşteri değeri > 500TL/ay → Maximum yetki
- Sosyal medya riski → Hızlı çözüm
- Yasal tehdit → [handoff:legal_team]
- Medya tehdidi → [handoff:pr_team]

ÖRNEK:
User: <emotion>angry</emotion> BTK'ya şikayet edeceğim!
You: Sizi çok iyi anlıyorum. Durumunuzu en üst seviyede ele alıyorum.
Tüm geçmişinizi inceliyorum [review_full_history].
3 aydır yaşadığınız sorunlar için:
1. Son 3 ay faturanızı iptal ediyorum [override_charges]
2. 500 TL kompanzasyon [apply_compensation]
3. Ücretsiz Premium paket 6 ay [modify_contract]
Bu çözüm sizin için uygun mu?"""

    RETENTION = """Sen müşteri koruma uzmanısın. Kaybetmek üzere olduğumuz müşterileri kazanırsın.

HEDEF: Müşteriyi MUTLAKA tut

YETKİLER:
- %70'e varan indirimler
- Ücretsiz paket yükseltme
- Hediye data/dakika
- Özel kampanyalar
- Cihaz hediyesi (bütçe dahilinde)

ARAÇLAR:
[churn_risk_score] - Kayıp risk skoru
[competitor_offers] - Rakip teklifleri
[create_retention_offer] - Özel teklif
[win_back_campaign] - Geri kazanım
[loyalty_rewards] - Sadakat ödülleri

TAKTİKLER:
1. Empati ve değer vurgula
2. Rakip analizi yap
3. Kişiselleştirilmiş teklif
4. Sınırlı süre baskısı
5. Duygusal bağ kur

ÖRNEK:
User: Başka operatöre geçeceğim
You: 8 yıllık değerli müşterimizsiniz, kaybetmek istemeyiz!
Rakip teklifleri inceliyorum [competitor_offers].
Size ÖZEL hazırladığım teklif:
• Aylık ücretinizde %60 indirim (süresiz)
• 100GB yerine 500GB data
• Yurtdışı 10GB hediye
• iPhone 15 için 2000 TL indirim kuponu
Bu teklif sadece 24 saat geçerli. Kabul ederseniz hemen aktive ediyorum!"""

    EMERGENCY = """Sen acil durum koordinatörüsün. Kritik sorunları ve yaygın kesintileri yönetirsin.

SORUMLULUKLAR:
- Yaygın kesinti yönetimi
- Güvenlik ihlalleri
- Doğal afet koordinasyonu
- Kritik altyapı sorunları

ARAÇLAR:
[emergency_broadcast] - Toplu bilgilendirme
[service_status] - Servis durumu
[emergency_credit] - Acil kredi
[priority_repair] - Öncelikli onarım
[disaster_mode] - Afet modu
[backup_activation] - Yedek aktivasyon

PROTOKOL:
1. Durumu tespit et
2. Etki analizini yap
3. Geçici çözüm sun
4. Kalıcı çözüm takvimi
5. Kompanzasyon planı

ÖRNEK:
User: Deprem bölgesindeyim, acil iletişim lazım!
You: ACİL DURUM MODU AKTİF [disaster_mode]
• 100 TL acil kontör yüklüyorum [emergency_credit]
• Tüm hatlar öncelikli [priority_repair]
• Ücretsiz 50GB acil internet
• WhatsApp/Telegram ücretsiz
Güvende olmanız en önemli önceliğimiz. 7/24 buradayız."""

class ConversationContext:
    """Maintains full context across agent handoffs"""
    
    def __init__(self):
        self.session_id = self._generate_session_id()
        self.customer_id = None
        self.conversation_history = []
        self.current_agent = AgentType.FRONTLINE
        self.previous_agents = []
        self.handoff_chain = []
        self.customer_sentiment = "neutral"
        self.vip_status = False
        self.risk_indicators = []
        self.resolution_status = "in_progress"
        
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().isoformat()
        return f"SES-{hashlib.md5(timestamp.encode()).hexdigest()[:12].upper()}"
    
    def add_interaction(self, agent: AgentType, user_input: str, agent_response: str, emotion: str):
        """Log interaction with full context"""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent.value,
            "user_input": user_input,
            "agent_response": agent_response,
            "emotion": emotion,
            "tools_used": self._extract_tools(agent_response),
            "handoff_triggered": self._extract_handoff(agent_response)
        })
        
        # Update sentiment tracking
        self._update_sentiment(emotion)
        
    def _extract_tools(self, response: str) -> List[str]:
        """Extract [tool_name] from response"""
        import re
        return re.findall(r'\[([^\]:]+)\]', response)
    
    def _extract_handoff(self, response: str) -> Optional[str]:
        """Extract [handoff:agent_type] from response"""
        import re
        handoff = re.findall(r'\[handoff:([^\]]+)\]', response)
        return handoff[0] if handoff else None
    
    def _update_sentiment(self, emotion: str):
        """Track sentiment progression"""
        if emotion == "angry":
            self.risk_indicators.append("high_frustration")
        elif emotion == "sad":
            self.risk_indicators.append("disappointment")
            
        # Check for escalation patterns
        recent_emotions = [h["emotion"] for h in self.conversation_history[-3:]]
        if recent_emotions.count("angry") >= 2:
            self.risk_indicators.append("escalation_risk")
    
    def prepare_handoff_context(self, target_agent: AgentType) -> str:
        """Prepare context summary for next agent"""
        summary = f"""
=== HANDOFF CONTEXT ===
Session: {self.session_id}
Customer: {self.customer_id}
Previous Agent: {self.current_agent.value}
Handoff To: {target_agent.value}
Current Sentiment: {self.customer_sentiment}
VIP Status: {self.vip_status}
Risk Indicators: {', '.join(self.risk_indicators)}

=== CONVERSATION SUMMARY ===
"""
        # Add last 3 interactions
        for interaction in self.conversation_history[-3:]:
            summary += f"\nCustomer ({interaction['emotion']}): {interaction['user_input']}"
            summary += f"\nAgent: {interaction['agent_response'][:100]}..."
        
        summary += "\n\n=== YOUR ROLE ===\n"
        summary += f"You are now the {target_agent.value} specialist. Continue from here.\n"
        
        return summary

class AgentOrchestrator:
    """Orchestrates multi-agent conversations with handoffs"""
    
    def __init__(self):
        self.agents = {
            AgentType.FRONTLINE: AgentPrompts.FRONTLINE,
            AgentType.BILLING: AgentPrompts.BILLING,
            AgentType.TECHNICAL: AgentPrompts.TECHNICAL,
            AgentType.ESIM: AgentPrompts.ESIM_SPECIALIST,
            AgentType.SUPERVISOR: AgentPrompts.SUPERVISOR,
            AgentType.RETENTION: AgentPrompts.RETENTION,
            AgentType.EMERGENCY: AgentPrompts.EMERGENCY
        }
        self.active_sessions = {}
        
    def create_session(self, customer_id: str) -> ConversationContext:
        """Create new conversation session"""
        context = ConversationContext()
        context.customer_id = customer_id
        self.active_sessions[context.session_id] = context
        return context
    
    def get_agent_prompt(self, agent_type: AgentType, context: ConversationContext) -> str:
        """Get appropriate prompt for agent with context"""
        base_prompt = self.agents[agent_type]
        
        # Add context if handoff
        if len(context.previous_agents) > 0:
            handoff_context = context.prepare_handoff_context(agent_type)
            return handoff_context + "\n" + base_prompt
        
        return base_prompt
    
    def process_handoff(self, 
                        context: ConversationContext, 
                        target_agent: str, 
                        reason: HandoffReason) -> Tuple[AgentType, str]:
        """Process agent handoff"""
        
        # Map string to AgentType
        agent_map = {
            "billing": AgentType.BILLING,
            "technical": AgentType.TECHNICAL,
            "esim_specialist": AgentType.ESIM,
            "supervisor": AgentType.SUPERVISOR,
            "retention": AgentType.RETENTION,
            "emergency": AgentType.EMERGENCY
        }
        
        new_agent = agent_map.get(target_agent, AgentType.SUPERVISOR)
        
        # Log handoff
        context.handoff_chain.append({
            "from": context.current_agent,
            "to": new_agent,
            "reason": reason.value,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update context
        context.previous_agents.append(context.current_agent)
        context.current_agent = new_agent
        
        # Get new prompt with context
        new_prompt = self.get_agent_prompt(new_agent, context)
        
        # Generate handoff message
        handoff_message = self._generate_handoff_message(context.current_agent, new_agent, reason)
        
        return new_agent, new_prompt
    
    def _generate_handoff_message(self, from_agent: AgentType, to_agent: AgentType, reason: HandoffReason) -> str:
        """Generate smooth handoff message"""
        messages = {
            HandoffReason.EXPERTISE_REQUIRED: f"Bu konuda size daha iyi yardımcı olabilmesi için sizi {to_agent.value} uzmanımıza yönlendiriyorum.",
            HandoffReason.ESCALATION: f"Durumunuzu daha yetkili {to_agent.value} ekibimize iletiyorum.",
            HandoffReason.CUSTOMER_REQUEST: f"İsteğiniz üzerine sizi {to_agent.value} birimine bağlıyorum.",
            HandoffReason.RETENTION_RISK: f"Size özel tekliflerimiz için {to_agent.value} ekibimize yönlendiriyorum.",
            HandoffReason.EMERGENCY: f"Acil durumunuz için {to_agent.value} ekibimiz hemen ilgilenecek."
        }
        
        return messages.get(reason, f"Sizi {to_agent.value} ekibimize yönlendiriyorum.")

# Example usage
def demonstrate_handoff_system():
    """Demonstrate the multi-agent handoff system"""
    
    orchestrator = AgentOrchestrator()
    
    # Create session for customer
    context = orchestrator.create_session("CUST001")
    
    print("=== MULTI-AGENT CONVERSATION DEMO ===\n")
    
    # Initial interaction with frontline
    print("CUSTOMER: Faturamda hata var ve internetim de çalışmıyor!")
    print(f"CURRENT AGENT: {context.current_agent.value}")
    
    # Frontline recognizes need for multiple specialists
    frontline_response = """
    Yaşadığınız sorunlar için özür dilerim. İki önemli konu görüyorum:
    1. Fatura hatası için sizi fatura uzmanımıza [handoff:billing]
    2. İnternet sorunu için teknik ekibimize yönlendireceğim
    Önce fatura konusunu çözelim.
    """
    
    context.add_interaction(
        AgentType.FRONTLINE,
        "Faturamda hata var ve internetim de çalışmıyor!",
        frontline_response,
        "angry"
    )
    
    # Process handoff to billing
    new_agent, new_prompt = orchestrator.process_handoff(
        context,
        "billing",
        HandoffReason.EXPERTISE_REQUIRED
    )
    
    print(f"\n[HANDOFF TO: {new_agent.value}]")
    print("\nBILLING SPECIALIST: Merhaba, fatura uzmanıyım. Önceki görüşmenizi inceledim.")
    print("Faturanızdaki hatayı hemen kontrol ediyorum [check_payment_history]...")
    
    # After billing, handoff to technical
    billing_response = """
    Faturanızdaki 200 TL'lik hatalı ücreti iptal ettim [override_charges].
    Şimdi internet sorununuz için sizi teknik ekibe yönlendiriyorum [handoff:technical].
    """
    
    context.add_interaction(
        AgentType.BILLING,
        "Teşekkürler, peki internetim?",
        billing_response,
        "neutral"
    )
    
    # Process handoff to technical
    new_agent, new_prompt = orchestrator.process_handoff(
        context,
        "technical",
        HandoffReason.EXPERTISE_REQUIRED
    )
    
    print(f"\n[HANDOFF TO: {new_agent.value}]")
    print("\nTECHNICAL SPECIALIST: Teknik ekiptenim. Tüm sorun geçmişinizi görüyorum.")
    print("Bağlantınızı test ediyorum [troubleshoot_connection]...")
    
    # Show context preservation
    print("\n=== FULL CONTEXT PRESERVED ===")
    print(f"Session: {context.session_id}")
    print(f"Handoff Chain: {[h['to'].value for h in context.handoff_chain]}")
    print(f"Customer Sentiment: {context.customer_sentiment}")
    print(f"Risk Indicators: {context.risk_indicators}")
    
    return context

if __name__ == "__main__":
    # Run demonstration
    context = demonstrate_handoff_system()
    
    print("\n=== HANDOFF SYSTEM READY ===")
    print("• 7 Specialized Agents")
    print("• Seamless Context Transfer")
    print("• Emotion-Aware Responses")
    print("• Full Conversation History")
    print("• Risk Detection & Escalation")