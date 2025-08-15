"""
Step 7: Noise Application to Existing Dialogs
Apply Turkish ASR noise to user turns while preserving assistant quality
"""
import random
from typing import Dict, List
from dataset_step2_noise import TurkishNoiseGenerator

class NoiseApplicationEngine:
    """Apply noise to existing dialogs for robustness training."""
    
    def __init__(self):
        self.noise_generator = TurkishNoiseGenerator()
        
        # Noise application strategies
        self.noise_strategies = [
            "telecom_heavy",     # Focus on telecom confusions
            "diacritic_removal", # Heavy diacritic loss
            "spacing_errors",    # Word boundary issues  
            "mixed_light",       # Light mixed noise
            "mixed_heavy"        # Heavy mixed noise
        ]
    
    def apply_noise_to_dialog(self, dialog_data: Dict, noise_strategy: str = "mixed_light") -> Dict:
        """Apply noise to user turns in a dialog."""
        conversations = dialog_data["conversations"].copy()
        noisy_conversations = []
        
        for turn in conversations:
            if turn["role"] == "user":
                # Don't apply noise to tool_result messages
                user_text = turn["content"][0]["text"]
                
                if not user_text.startswith("<tool_result>"):
                    # Apply noise based on strategy
                    if noise_strategy == "telecom_heavy":
                        noisy_text = self._apply_telecom_heavy_noise(user_text)
                    elif noise_strategy == "diacritic_removal":
                        noisy_text = self._apply_diacritic_noise(user_text)
                    elif noise_strategy == "spacing_errors":
                        noisy_text = self._apply_spacing_noise(user_text)
                    elif noise_strategy == "mixed_light":
                        noisy_text = self.noise_generator.generate_noisy_text(user_text, noise_level=0.3)
                    elif noise_strategy == "mixed_heavy":
                        noisy_text = self.noise_generator.generate_noisy_text(user_text, noise_level=0.6)
                    else:
                        noisy_text = self.noise_generator.generate_noisy_text(user_text, noise_level=0.4)
                    
                    # Create new turn with noisy text
                    noisy_turn = {
                        "role": "user",
                        "content": [{"type": "text", "text": noisy_text}]
                    }
                    noisy_conversations.append(noisy_turn)
                else:
                    # Keep tool_result messages unchanged
                    noisy_conversations.append(turn)
            else:
                # Keep assistant messages unchanged
                noisy_conversations.append(turn)
        
        # Update dialog data
        noisy_dialog = dialog_data.copy()
        noisy_dialog["conversations"] = noisy_conversations
        noisy_dialog["has_noise"] = True
        noisy_dialog["noise_strategy"] = noise_strategy
        
        return noisy_dialog
    
    def _apply_telecom_heavy_noise(self, text: str) -> str:
        """Apply heavy telecom-specific noise."""
        noisy_text = text
        
        # Apply telecom confusions multiple times
        for _ in range(random.randint(1, 3)):
            noisy_text = self.noise_generator.apply_telecom_confusion(noisy_text)
        
        # Add some diacritic removal
        if random.random() < 0.5:
            noisy_text = self.noise_generator.remove_diacritics(noisy_text)
        
        return noisy_text
    
    def _apply_diacritic_noise(self, text: str) -> str:
        """Apply heavy diacritic removal."""
        noisy_text = self.noise_generator.remove_diacritics(text)
        
        # Add some spacing issues
        if random.random() < 0.3:
            noisy_text = self.noise_generator.apply_spacing_errors(noisy_text)
        
        return noisy_text
    
    def _apply_spacing_noise(self, text: str) -> str:
        """Apply spacing and word boundary errors."""
        noisy_text = text
        
        # Apply spacing errors multiple times
        for _ in range(random.randint(1, 2)):
            noisy_text = self.noise_generator.apply_spacing_errors(noisy_text)
        
        # Add some typos
        if random.random() < 0.4:
            noisy_text = self.noise_generator.apply_typos(noisy_text)
        
        return noisy_text
    
    def create_noise_variants(self, clean_dialog: Dict, num_variants: int = 2) -> List[Dict]:
        """Create multiple noise variants of a clean dialog."""
        variants = []
        
        for i in range(num_variants):
            strategy = random.choice(self.noise_strategies)
            noisy_variant = self.apply_noise_to_dialog(clean_dialog, strategy)
            noisy_variant["variant_id"] = i + 1
            variants.append(noisy_variant)
        
        return variants
    
    def generate_esim_confusion_dialogs(self) -> List[Dict]:
        """Generate specific eSIM confusion scenarios."""
        esim_confusions = [
            {
                "clean": "eSIM aktivasyon kodu istiyorum",
                "noisy_variants": [
                    "mevsim aktivasyon kodu istiyorum",
                    "eşim aktivasyon kodu istiyorum", 
                    "e sim aktivasyon kodu istiyorum",
                    "esim aktivasyon kodu istiyorum"
                ]
            },
            {
                "clean": "eSIM destekliyor mu telefonum?",
                "noisy_variants": [
                    "mevsim destekliyor mu telefonum?",
                    "e-sim destekliyor mu telefonum?",
                    "esim destekliyor mu telefonum?",
                    "elektronik sim destekliyor mu telefonum?"
                ]
            },
            {
                "clean": "IMEI numaramı kontrol eder misiniz?",
                "noisy_variants": [
                    "aymay numaramı kontrol eder misiniz?",
                    "imey numaramı kontrol eder misiniz?",
                    "imay numaramı kontrol eder misiniz?",
                    "cihaz kodumu kontrol eder misiniz?"
                ]
            }
        ]
        
        confusion_dialogs = []
        
        for confusion_set in esim_confusions:
            for noisy_variant in confusion_set["noisy_variants"]:
                dialog = {
                    "conversations": [
                        {"role": "user", "content": [{"type": "text", "text": noisy_variant}]},
                        {"role": "assistant", "content": [{"type": "text", "text": "Tabii ki, size yardımcı olayım. Önce kimlik doğrulaması yapalım."}]}
                    ],
                    "scenario_type": "esim_confusion_focused",
                    "context": "SIM",
                    "has_noise": True,
                    "noise_strategy": "telecom_confusion",
                    "clean_intent": confusion_set["clean"],
                    "noisy_input": noisy_variant
                }
                confusion_dialogs.append(dialog)
        
        return confusion_dialogs
    
    def generate_number_confusion_dialogs(self) -> List[Dict]:
        """Generate number and date confusion scenarios."""
        number_confusions = [
            {
                "clean": "Son dört hanesi 1234",
                "noisy_variants": [
                    "son dort hanesi 1234",
                    "son 4 hanesi 1234", 
                    "son dört hane 1234",
                    "son dört numara 1234"
                ]
            },
            {
                "clean": "Beş GB paketim var",
                "noisy_variants": [
                    "5 gb paketim var",
                    "bes gb paketim var",
                    "beş cib paketim var",
                    "5 cebe paketim var"
                ]
            },
            {
                "clean": "Yüz elli lira ödedim",
                "noisy_variants": [
                    "150 lira odedim",
                    "yuz elli tl odedim",
                    "150 tl ödedim",
                    "bir yüz elli lira ödedim"
                ]
            }
        ]
        
        number_dialogs = []
        
        for confusion_set in number_confusions:
            for noisy_variant in confusion_set["noisy_variants"]:
                dialog = {
                    "conversations": [
                        {"role": "user", "content": [{"type": "text", "text": noisy_variant}]},
                        {"role": "assistant", "content": [{"type": "text", "text": "Anladım, bilgilerinizi kontrol ediyorum."}]}
                    ],
                    "scenario_type": "number_confusion_focused", 
                    "context": "GENERAL",
                    "has_noise": True,
                    "noise_strategy": "number_confusion",
                    "clean_intent": confusion_set["clean"],
                    "noisy_input": noisy_variant
                }
                number_dialogs.append(dialog)
        
        return number_dialogs

print("✅ Step 7: Noise application engine ready")
