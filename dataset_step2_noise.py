"""
Step 2: Turkish Noise Augmentation System
Advanced ASR noise patterns for robust training
"""
import re
import random
from typing import Dict, List

class TurkishNoiseGenerator:
    """Advanced Turkish ASR noise generator for robust training."""
    
    def __init__(self):
        # Turkish telecom confusion patterns
        self.telecom_confusions = {
            "eSIM": ["esim", "e sim", "e-sim", "ESİM", "mevsim", "eşim", "e sim kartı", "elektronik sim"],
            "taahhüt": ["taahut", "tahhut", "taahhut", "tahüt", "taahhüt sözleşmesi", "taahüt sözleşmesi"],
            "paket": ["paketi", "paketim", "paket im", "tarife", "plan", "abonelik"],
            "kota": ["koota", "kotaa", "veri kotası", "internet kotası"],
            "çekmiyor": ["cekmiyor", "çekmiyo", "cekmiyo", "çek miyor", "çekme", "yok sinyalim"],
            "kapsama": ["kapsama alanı", "kapsama alanim", "kapsama alani", "sinyal", "çekim"],
            "fatura": ["fatıra", "fatrura", "fatura mı", "faturamı", "fatüra", "ödeme"],
            "IMEI": ["imei", "aymay", "imey", "imay", "cihaz kodu", "telefon kodu"],
            "MSISDN": ["msisdn", "mesajın", "msizdn", "numara", "telefon numarası"],
            "LTE": ["elte", "el te", "4.5g", "4 buçuk g"],
            "4.5G": ["dört buçuk g", "4 bucuk g", "4,5g", "dört nokta beş g"],
            "5G": ["beş g", "beşci", "5 g", "beşinci nesil"],
            "SMS": ["esemes", "mesaj", "kısa mesaj", "sms mesajı"],
            "TL": ["tl", "lira", "₺", "türk lirası", "para"],
            "aktivasyon": ["aktivasyon kodu", "aktifleştirme", "etkinleştirme", "açma kodu"],
            "LPA": ["lpa", "lpa kodu", "aktivasyon kodu", "qr kod", "profil kodu"]
        }
        
        # Diacritic removal patterns
        self.diacritic_map = {
            "ı": "i", "İ": "I", "ğ": "g", "Ğ": "G", "ü": "u", "Ü": "U",
            "ş": "s", "Ş": "S", "ö": "o", "Ö": "O", "ç": "c", "Ç": "C"
        }
        
        # Number word confusions
        self.number_confusions = {
            "bir": ["bi", "1"], "iki": ["2", "ike"], "üç": ["3", "uç"], 
            "dört": ["4", "dort"], "beş": ["5", "bes"], "altı": ["6", "alti"],
            "yedi": ["7"], "sekiz": ["8"], "dokuz": ["9"], "on": ["10"]
        }
        
        # Common Turkish typos and colloquialisms
        self.common_typos = {
            "değiştirmek": ["degistirmek", "değiştirek", "degistirek"],
            "yükseltmek": ["yukseltmek", "yukseltek"],
            "düşürmek": ["dusurmek", "dusurrek"],
            "gönder": ["gonder", "gondr"],
            "kontrol": ["kontrole", "kontrl"],
            "istiyorum": ["istiyom", "istiom", "istiyrum"]
        }
    
    def apply_telecom_confusion(self, text: str) -> str:
        """Apply telecom-specific confusion patterns."""
        for canonical, variants in self.telecom_confusions.items():
            if canonical.lower() in text.lower():
                if random.random() < 0.4:  # 40% chance to apply confusion
                    variant = random.choice(variants)
                    pattern = r'\b' + re.escape(canonical) + r'\b'
                    text = re.sub(pattern, variant, text, flags=re.IGNORECASE)
                    break
        return text
    
    def remove_diacritics(self, text: str) -> str:
        """Remove Turkish diacritics (common ASR error)."""
        if random.random() < 0.3:  # 30% chance
            for diacritic, plain in self.diacritic_map.items():
                text = text.replace(diacritic, plain)
        return text
    
    def apply_spacing_errors(self, text: str) -> str:
        """Apply spacing errors (merge/split words)."""
        if random.random() < 0.2:  # 20% chance
            words = text.split()
            if len(words) > 1:
                if random.choice([True, False]):
                    # Merge two words
                    idx = random.randint(0, len(words) - 2)
                    words[idx] = words[idx] + words[idx + 1]
                    words.pop(idx + 1)
                else:
                    # Split a word
                    word_idx = random.randint(0, len(words) - 1)
                    word = words[word_idx]
                    if len(word) > 4:
                        split_point = len(word) // 2
                        words[word_idx] = word[:split_point] + " " + word[split_point:]
            text = " ".join(words)
        return text
    
    def apply_casing_errors(self, text: str) -> str:
        """Apply random casing errors."""
        if random.random() < 0.15:  # 15% chance
            if random.choice([True, False]):
                text = text.upper()
            else:
                text = text.lower()
        return text
    
    def apply_typos(self, text: str) -> str:
        """Apply common Turkish typos."""
        for correct, typos in self.common_typos.items():
            if correct in text.lower():
                if random.random() < 0.25:  # 25% chance
                    typo = random.choice(typos)
                    pattern = r'\b' + re.escape(correct) + r'\b'
                    text = re.sub(pattern, typo, text, flags=re.IGNORECASE)
                    break
        return text
    
    def apply_number_confusion(self, text: str) -> str:
        """Apply number word confusions."""
        for word, variants in self.number_confusions.items():
            if word in text.lower():
                if random.random() < 0.3:  # 30% chance
                    variant = random.choice(variants)
                    pattern = r'\b' + re.escape(word) + r'\b'
                    text = re.sub(pattern, variant, text, flags=re.IGNORECASE)
                    break
        return text
    
    def generate_noisy_text(self, clean_text: str, noise_level: float = 0.4) -> str:
        """Apply multiple noise transformations to text."""
        if random.random() > noise_level:
            return clean_text
        
        noisy_text = clean_text
        
        # Apply noise transformations randomly
        noise_functions = [
            self.apply_telecom_confusion,
            self.remove_diacritics,
            self.apply_spacing_errors,
            self.apply_casing_errors,
            self.apply_typos,
            self.apply_number_confusion
        ]
        
        # Apply 1-3 noise transformations
        num_transformations = random.randint(1, 3)
        selected_functions = random.sample(noise_functions, min(num_transformations, len(noise_functions)))
        
        for noise_func in selected_functions:
            noisy_text = noise_func(noisy_text)
        
        return noisy_text

print("✅ Step 2: Turkish noise generator ready")
