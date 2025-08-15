#!/usr/bin/env python3
"""
ELITE TURKISH TELCO AUDIO DATASET GENERATOR
Using ElevenLabs API to create synthetic Turkish call center conversations
This will DESTROY the competition with perfect audio quality
"""

import os
import json
import asyncio
import random
from typing import List, Dict, Any
from datetime import datetime
import base64
from pathlib import Path

# ElevenLabs imports
from elevenlabs import ElevenLabs, Voice, VoiceSettings, play, save
from elevenlabs.client import AsyncElevenLabs

class EliteTurkishTelcoGenerator:
    """Generate elite Turkish telco call center conversations with ElevenLabs"""
    
    def __init__(self, api_key: str = None):
        self.client = ElevenLabs(api_key=api_key or os.getenv("ELEVENLABS_API_KEY"))
        self.async_client = AsyncElevenLabs(api_key=api_key or os.getenv("ELEVENLABS_API_KEY"))
        
        # Turkish voice IDs from ElevenLabs (we'll use existing voices)
        self.voice_profiles = {
            "agent_professional": {
                "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel - professional
                "settings": VoiceSettings(stability=0.75, similarity_boost=0.75, style=0.2, use_speaker_boost=True)
            },
            "customer_angry": {
                "voice_id": "AZnzlk1XvdvUeBnXmlld",  # Domi - expressive
                "settings": VoiceSettings(stability=0.3, similarity_boost=0.8, style=0.9, use_speaker_boost=True)
            },
            "customer_elderly": {
                "voice_id": "ThT5KcBeYPX3keUQqHPh",  # Dorothy - older voice
                "settings": VoiceSettings(stability=0.9, similarity_boost=0.7, style=0.1, use_speaker_boost=True)
            },
            "customer_young": {
                "voice_id": "jBpfuIE2acCO8z3wKNLl",  # Gigi - young energetic
                "settings": VoiceSettings(stability=0.5, similarity_boost=0.75, style=0.6, use_speaker_boost=True)
            },
            "customer_business": {
                "voice_id": "pMsXgVXv3BLzUgSXRplE",  # Serena - business-like
                "settings": VoiceSettings(stability=0.8, similarity_boost=0.8, style=0.3, use_speaker_boost=True)
            }
        }
        
        # Model selection for Turkish
        self.model_id = "eleven_multilingual_v2"  # Best quality for Turkish
        self.turbo_model = "eleven_turbo_v2_5"  # For faster generation
        
        self.output_dir = Path("data/synthetic_audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_telco_scenarios(self) -> List[Dict[str, Any]]:
        """Generate diverse Turkish telco scenarios with tool calls"""
        
        scenarios = []
        
        # Scenario templates with increasing complexity
        templates = [
            # Simple scenarios
            {
                "type": "esim_activation",
                "customer_type": "young",
                "emotion": "frustrated",
                "dialogue": [
                    ("customer", "Merhaba, eSIM'imi 3 gündür aktifleştiremiyorum, yardım eder misiniz?"),
                    ("agent", "Merhaba, memnuniyetle yardımcı olurum. Önce kimlik doğrulaması yapalım. Telefon numaranızı alabilir miyim?"),
                    ("customer", "Tabi, 0555 123 45 67"),
                    ("agent", "Teşekkürler, annenizin kızlık soyadını da alabilir miyim?"),
                    ("customer", "Yıldız... şey, Yıldız olması lazım"),
                    ("agent", "Doğrulama tamamlandı. eSIM aktivasyonunuzu kontrol ediyorum."),
                    ("agent", "Cihazınızın IMEI numarasını alabilir miyim? Ayarlar > Genel > Hakkında kısmında bulabilirsiniz."),
                    ("customer", "Bir saniye... 359111222333444"),
                    ("agent", "Cihazınız uyumlu görünüyor. Yeni bir aktivasyon kodu üretiyorum."),
                    ("agent", "Kodunuz hazır: LPA:1$sm-dp.turkcell.com.tr$ABC123XYZ. iOS mu Android mi kullanıyorsunuz?"),
                    ("customer", "iOS kullanıyorum, iPhone 14"),
                    ("agent", "Mükemmel. Ayarlar > Hücresel > eSIM Ekle'ye gidin ve bu kodu girin. Sonra uçak modunu 10 saniye açıp kapatın."),
                    ("customer", "Tamam deniyorum... Çalıştı! Teşekkür ederim!"),
                    ("agent", "Rica ederim, iyi günler dilerim!")
                ],
                "tools": ["verify_user", "check_device_registration", "reissue_activation_code"],
                "interruptions": [5, 9],  # Customer interrupts at these points
                "context_switches": []
            },
            
            # Medium complexity - with context switch
            {
                "type": "package_upgrade_with_complaint",
                "customer_type": "business",
                "emotion": "assertive",
                "dialogue": [
                    ("customer", "Merhaba, paketimi değiştirmek istiyorum ama önce bir şikayetim var"),
                    ("agent", "Merhaba, önce kimlik doğrulaması yapalım. Telefon numaranızı söyler misiniz?"),
                    ("customer", "0532 987 65 43, ama önce şunu söyleyeyim, geçen ay fazla fatura geldi"),
                    ("agent", "Anlıyorum, hem faturanızı hem de paket değişikliğinizi kontrol edeceğim. Annenizin kızlık soyadı?"),
                    ("customer", "Demir"),
                    ("agent", "Teşekkürler Mehmet Bey, doğrulama tamamlandı. Önce faturanızı kontrol ediyorum."),
                    ("agent", "Faturanızda roaming ücreti görünüyor. Yurtdışında mıydınız?"),
                    ("customer", "Evet Almanya'daydım ama bilgilendirme yapılmadı. Neyse, şimdi paket değişikliği yapalım"),
                    ("agent", "Roaming konusunu not aldım, size SMS ile bilgi göndereceğim. Şimdi paketinize bakalım."),
                    ("agent", "Şu an 10GB pakettesiniz. Hangi paketi tercih edersiniz?"),
                    ("customer", "20GB'lık aile paketi var mı? Eşim ve çocuklarım da kullanacak"),
                    ("agent", "Evet, Family 20GB paketimiz 249 TL. 4 hatta kadar paylaşımlı kullanım sunuyor."),
                    ("customer", "Tamam onu istiyorum, hemen geçiş yapabilir miyiz?"),
                    ("agent", "Geçişi başlatıyorum. Onay SMS'i gelecek, onayladıktan sonra aktif olacak."),
                    ("customer", "Tamam, teşekkürler. Roaming konusunu da unutmayın"),
                    ("agent", "Kesinlikle, ticket numaranız TKT-1234. 24 saat içinde dönüş yapılacak. İyi günler!")
                ],
                "tools": ["verify_user", "check_billing", "get_available_packages", "change_package", "create_support_ticket"],
                "interruptions": [2, 7, 14],
                "context_switches": ["complaint_to_package", "package_to_complaint"]
            },
            
            # Complex scenario - multiple context switches and emotional changes
            {
                "type": "technical_support_escalation",
                "customer_type": "elderly",
                "emotion": "confused_to_angry",
                "dialogue": [
                    ("customer", "Alo? Merhaba yavrum, bu telefon sürekli kapanıyor, eSIM diye bir şey çıkıyor"),
                    ("agent", "Merhaba, size yardımcı olayım. Önce sizi tanıyalım. Telefon numaranız nedir?"),
                    ("customer", "Numaramı mı? Bekle bakayım... 0541... yok 0542... 0542 678 90 12"),
                    ("agent", "Teşekkürler. Güvenlik için annenizin kızlık soyadını sorabilir miyim?"),
                    ("customer", "Annemin mi? Ah, Gül'dü rahmetli... Gül"),
                    ("agent", "Teşekkürler Elif Hanım. eSIM durumunuzu kontrol ediyorum."),
                    ("customer", "Bu eSIM ne yavrum? Ben anlamıyorum bunlardan. Eskiden SIM kart vardı"),
                    ("agent", "eSIM dijital SIM kart demek. Fiziksel kart yerine dijital olarak telefona yükleniyor."),
                    ("customer", "Dijital mi? Ben öyle şey istemiyorum! Normal kart istiyorum!"),
                    ("agent", "Anlıyorum. Size fiziksel SIM kart gönderebiliriz. Adresinizi doğrulayabilir miyim?"),
                    ("customer", "Adres mi? Bir dakika... Kızım! KIZıM! Adresimiz ne?"),
                    ("customer", "Pardon, kızım söyledi. Atatürk Mahallesi, Cumhuriyet Caddesi No:45"),
                    ("agent", "Teşekkürler. Fiziksel SIM kartı yarın kargoya vereceğiz."),
                    ("customer", "Yarın mı? Ama telefon şimdi çalışmıyor! Ne yapacağım ben?"),
                    ("agent", "eSIM'i geçici olarak aktifleştirebilirim, kart gelene kadar kullanırsınız."),
                    ("customer", "Yapma öyle şeyler! Başıma bela açma! Ben beklerim"),
                    ("agent", "Tamam Elif Hanım, yarın kargoda. Takip numarası SMS ile gelecek."),
                    ("customer", "SMS mi? O da ne? Mesaj mı diyorsun?"),
                    ("agent", "Evet, kısa mesaj gelecek telefonunuza."),
                    ("customer", "Tamam yavrum, sağ ol. Allah razı olsun"),
                    ("agent", "Rica ederim, sağlıklı günler dilerim!")
                ],
                "tools": ["verify_user", "check_esim_status", "request_physical_sim", "create_support_ticket"],
                "interruptions": [3, 10, 11, 15, 17],
                "context_switches": ["technical_to_emotional", "solution_rejection", "confusion_escalation"]
            }
        ]
        
        # Generate variations of each template
        for template in templates:
            for i in range(3):  # 3 variations per template
                scenario = template.copy()
                scenario["id"] = f"{template['type']}_{i+1}"
                scenario["timestamp"] = datetime.now().isoformat()
                scenario["duration_estimate"] = len(template["dialogue"]) * 3  # seconds
                scenarios.append(scenario)
        
        return scenarios
    
    async def generate_audio_for_turn(self, text: str, voice_profile: str, scenario_id: str, turn_idx: int) -> str:
        """Generate audio for a single conversation turn"""
        
        voice_config = self.voice_profiles[voice_profile]
        
        # Generate audio
        audio = await self.async_client.text_to_speech.convert_async(
            text=text,
            voice_id=voice_config["voice_id"],
            model_id=self.model_id,
            voice_settings=voice_config["settings"],
            output_format="mp3_44100_128"
        )
        
        # Save audio file
        filename = f"{scenario_id}_turn_{turn_idx:03d}_{voice_profile}.mp3"
        filepath = self.output_dir / filename
        
        with open(filepath, "wb") as f:
            async for chunk in audio:
                if chunk:
                    f.write(chunk)
        
        return str(filepath)
    
    async def generate_full_conversation(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete conversation audio with metadata"""
        
        print(f"🎯 Generating scenario: {scenario['id']}")
        
        conversation_data = {
            "scenario_id": scenario["id"],
            "type": scenario["type"],
            "customer_emotion": scenario["emotion"],
            "tools_used": scenario["tools"],
            "interruptions": scenario["interruptions"],
            "context_switches": scenario["context_switches"],
            "audio_files": [],
            "transcript": [],
            "multimodal_training_data": []
        }
        
        # Determine voice profiles
        customer_voice = f"customer_{scenario['customer_type']}"
        agent_voice = "agent_professional"
        
        # Generate audio for each turn
        for idx, (speaker, text) in enumerate(scenario["dialogue"]):
            print(f"  📢 Generating turn {idx+1}/{len(scenario['dialogue'])}: {speaker}")
            
            voice_profile = agent_voice if speaker == "agent" else customer_voice
            
            # Generate audio
            audio_file = await self.generate_audio_for_turn(
                text=text,
                voice_profile=voice_profile,
                scenario_id=scenario["id"],
                turn_idx=idx
            )
            
            # Determine which tools are called at this turn
            tools_at_turn = []
            if speaker == "agent":
                # Simulate tool calls based on conversation flow
                if "kimlik doğrulama" in text.lower() or "telefon numara" in text.lower():
                    tools_at_turn.append("verify_user")
                elif "imei" in text.lower() or "cihaz" in text.lower():
                    tools_at_turn.append("check_device_registration")
                elif "kod" in text.lower() and "aktivasyon" in text.lower():
                    tools_at_turn.append("reissue_activation_code")
                elif "paket" in text.lower():
                    tools_at_turn.append("get_available_packages")
            
            # Create training data entry
            training_entry = {
                "audio_file": audio_file,
                "text": text,
                "speaker": speaker,
                "turn_index": idx,
                "tools_called": tools_at_turn,
                "is_interruption": idx in scenario.get("interruptions", []),
                "context_switch": any(cs for cs in scenario.get("context_switches", []) if idx in range(idx-1, idx+2)),
                "emotion_level": self._calculate_emotion_level(text, scenario["emotion"])
            }
            
            conversation_data["audio_files"].append(audio_file)
            conversation_data["transcript"].append({"speaker": speaker, "text": text})
            conversation_data["multimodal_training_data"].append(training_entry)
        
        # Save metadata
        metadata_file = self.output_dir / f"{scenario['id']}_metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(conversation_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Scenario {scenario['id']} complete!")
        
        return conversation_data
    
    def _calculate_emotion_level(self, text: str, base_emotion: str) -> float:
        """Calculate emotion intensity from text"""
        
        emotion_keywords = {
            "angry": ["yeter", "bıktım", "rezalet", "skandal", "berbat", "saçma"],
            "frustrated": ["olmıyor", "çalışmıyor", "anlamıyorum", "yapamıyorum", "zor"],
            "confused": ["ne", "nasıl", "anlamadım", "bilmiyorum", "emin değilim"],
            "happy": ["teşekkür", "sağol", "harika", "süper", "mükemmel"],
            "urgent": ["acil", "hemen", "şimdi", "bekleyemem", "önemli"]
        }
        
        text_lower = text.lower()
        
        # Check for emotion keywords
        max_score = 0.3  # Base emotion level
        for emotion, keywords in emotion_keywords.items():
            if emotion in base_emotion:
                max_score = 0.6
            for keyword in keywords:
                if keyword in text_lower:
                    max_score = min(1.0, max_score + 0.2)
        
        # Check for punctuation intensity
        if "!" in text:
            max_score = min(1.0, max_score + 0.1 * text.count("!"))
        if "?" in text:
            max_score = min(1.0, max_score + 0.05 * text.count("?"))
        
        return max_score
    
    async def generate_dataset(self, num_scenarios: int = 100):
        """Generate complete dataset with progress tracking"""
        
        print("🚀 ELITE TURKISH TELCO AUDIO DATASET GENERATOR")
        print("=" * 60)
        print(f"📊 Generating {num_scenarios} scenarios...")
        print("=" * 60)
        
        # Generate scenario templates
        base_scenarios = self.generate_telco_scenarios()
        
        # Expand to requested number
        scenarios = []
        while len(scenarios) < num_scenarios:
            for base in base_scenarios:
                if len(scenarios) >= num_scenarios:
                    break
                # Create variation
                variation = base.copy()
                variation["id"] = f"{base['type']}_v{len(scenarios)+1}"
                scenarios.append(variation)
        
        # Generate audio for each scenario
        all_conversations = []
        
        for i, scenario in enumerate(scenarios):
            print(f"\n📍 Progress: {i+1}/{num_scenarios}")
            try:
                conversation_data = await self.generate_full_conversation(scenario)
                all_conversations.append(conversation_data)
            except Exception as e:
                print(f"❌ Error generating scenario {scenario['id']}: {e}")
                continue
        
        # Save complete dataset manifest
        manifest_file = self.output_dir / "dataset_manifest.json"
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "total_scenarios": len(all_conversations),
                "model_used": self.model_id,
                "conversations": all_conversations
            }, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 60)
        print(f"✅ DATASET GENERATION COMPLETE!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📊 Total scenarios: {len(all_conversations)}")
        print(f"🎵 Total audio files: {sum(len(c['audio_files']) for c in all_conversations)}")
        print("=" * 60)
        
        return all_conversations

async def main():
    """Main execution"""
    
    # Set your ElevenLabs API key
    # os.environ["ELEVENLABS_API_KEY"] = "your_api_key_here"
    
    generator = EliteTurkishTelcoGenerator()
    
    # Generate dataset
    await generator.generate_dataset(num_scenarios=10)  # Start with 10 for testing

if __name__ == "__main__":
    print("🔥 STARTING ELITE DATASET GENERATION...")
    print("⚡ This will create the most advanced Turkish telco audio dataset ever!")
    print("")
    asyncio.run(main())