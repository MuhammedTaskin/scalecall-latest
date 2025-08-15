"""
Turkish text normalizer for telco domain with ASR noise handling.
Handles diacritics, homophones, numbers, and context-aware disambiguation.
"""
import json
import re
from typing import Dict, List, Optional
from pathlib import Path


class TurkishNormalizer:
    """Context-aware Turkish text normalizer for telco domain."""
    
    def __init__(self, confusions_path: str = "confusions_tr.json"):
        """Initialize normalizer with confusion lexicon."""
        self.confusions = self._load_confusions(confusions_path)
        self.diacritic_map = self._build_diacritic_map()
        self.number_words = self.confusions.get("numbers", {})
        
    def _load_confusions(self, path: str) -> Dict:
        """Load confusion lexicon from JSON."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback to minimal lexicon
            return {
                "telecom_core": {
                    "eSIM": ["esim", "e sim", "mevsim", "eşim"],
                    "taahhüt": ["taahut", "tahhut", "taahhut"],
                    "IMEI": ["imei", "aymay", "imey"]
                }
            }
    
    def _build_diacritic_map(self) -> Dict[str, str]:
        """Build character mapping for diacritic restoration."""
        return {
            'i': 'ı', 'I': 'İ', 'o': 'ö', 'O': 'Ö',
            'u': 'ü', 'U': 'Ü', 'c': 'ç', 'C': 'Ç',
            's': 'ş', 'S': 'Ş', 'g': 'ğ', 'G': 'Ğ'
        }
    
    def normalize_text(self, text: str, context: str = "GENERAL") -> str:
        """
        Main normalization function.
        
        Args:
            text: Input text to normalize
            context: Domain context (SIM, PLAN, BILLING, COVERAGE, GENERAL)
            
        Returns:
            Normalized text
        """
        if not text:
            return text
            
        # Clean and lowercase for processing
        normalized = text.strip().lower()
        
        # Apply normalization steps
        normalized = self._normalize_telecom_terms(normalized, context)
        normalized = self._normalize_numbers_currency(normalized)
        normalized = self._restore_diacritics_selective(normalized)
        normalized = self._fix_common_typos(normalized)
        
        return normalized
    
    def _normalize_telecom_terms(self, text: str, context: str) -> str:
        """Normalize telecom-specific terms with context awareness."""
        telecom_core = self.confusions.get("telecom_core", {})
        context_rules = self.confusions.get("context_disambiguation", {}).get(context, {})
        
        # Apply context-specific rules first
        for canonical, replacement in context_rules.items():
            pattern = r'\b' + re.escape(canonical) + r'\b'
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Apply general telecom term normalization
        for canonical, variants in telecom_core.items():
            for variant in variants:
                pattern = r'\b' + re.escape(variant) + r'\b'
                text = re.sub(pattern, canonical, text, flags=re.IGNORECASE)
        
        return text
    
    def _normalize_numbers_currency(self, text: str) -> str:
        """Convert Turkish number words to digits and normalize currency."""
        # Number word conversion
        for word, digit in self.number_words.items():
            pattern = r'\b' + re.escape(word) + r'\b'
            text = re.sub(pattern, str(digit), text, flags=re.IGNORECASE)
        
        # Currency normalization
        text = re.sub(r'\b(\d+)\s*(lira|₺|tl)\b', r'\1 TL', text, flags=re.IGNORECASE)
        
        # Phone number patterns (last 4 digits)
        text = re.sub(r'son\s*(\d{4})', r'son dört hanesi \1', text)
        
        # Date patterns
        months = self.confusions.get("months", {})
        for month_name, month_num in months.items():
            pattern = r'\b' + re.escape(month_name) + r'\b'
            text = re.sub(pattern, month_num, text, flags=re.IGNORECASE)
        
        return text
    
    def _restore_diacritics_selective(self, text: str) -> str:
        """Selectively restore diacritics for known terms."""
        # City names
        cities = self.confusions.get("cities", {})
        for canonical, variants in cities.items():
            for variant in variants:
                pattern = r'\b' + re.escape(variant) + r'\b'
                text = re.sub(pattern, canonical, text, flags=re.IGNORECASE)
        
        return text
    
    def _fix_common_typos(self, text: str) -> str:
        """Fix common typos and morphological variations."""
        typos = self.confusions.get("common_typos", {})
        for typo, correct in typos.items():
            pattern = r'\b' + re.escape(typo) + r'\b'
            text = re.sub(pattern, correct, text, flags=re.IGNORECASE)
        
        return text
    
    def extract_phone_last4(self, text: str) -> Optional[str]:
        """Extract phone number last 4 digits from text."""
        patterns = [
            r'(?:son|last)\s*(?:dört|4)\s*(?:hane|digit)[sı]*\s*(\d{4})',
            r'(\d{4})\s*(?:ile|with|son)',
            r'numaramın?\s*sonu?\s*(\d{4})',
            r'(\d{4})\s*ile\s*(?:doğrula|verify)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def extract_imei(self, text: str) -> Optional[str]:
        """Extract IMEI from text."""
        # Look for 15-digit IMEI patterns
        pattern = r'\b(\d{15})\b'
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        
        # Look for formatted IMEI
        pattern = r'\b(\d{2}-\d{6}-\d{6}-\d{1})\b'
        match = re.search(pattern, text)
        if match:
            return match.group(1).replace('-', '')
        
        return None
    
    def extract_package_id(self, text: str) -> Optional[str]:
        """Extract package ID from text."""
        patterns = [
            r'\b(basic_\w+)\b',
            r'\b(premium_\w+)\b', 
            r'\b(unlimited)\b',
            r'\b([A-Z]{2,}\d+(?:GB|MB)?)\b'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).lower()
        
        return None
    
    def get_domain_context(self, text: str) -> str:
        """Determine domain context from text content."""
        text_lower = text.lower()
        
        sim_keywords = ['esim', 'sim', 'aktivasyon', 'profil', 'qr', 'lpa', 'imei']
        plan_keywords = ['paket', 'tarife', 'plan', 'abonelik', 'değiştir', 'yükselt']
        billing_keywords = ['fatura', 'ödeme', 'borç', 'para', 'tl', 'lira', 'ücret']
        coverage_keywords = ['çekmiyor', 'sinyal', 'kapsama', 'bağlantı', 'ağ']
        
        if any(keyword in text_lower for keyword in sim_keywords):
            return "SIM"
        elif any(keyword in text_lower for keyword in plan_keywords):
            return "PLAN"
        elif any(keyword in text_lower for keyword in billing_keywords):
            return "BILLING"
        elif any(keyword in text_lower for keyword in coverage_keywords):
            return "COVERAGE"
        else:
            return "GENERAL"


def normalize_for_tools(text: str, context: str = None) -> str:
    """
    Convenience function for normalizing text before tool calls.
    """
    normalizer = TurkishNormalizer()
    
    if context is None:
        context = normalizer.get_domain_context(text)
    
    return normalizer.normalize_text(text, context)


if __name__ == "__main__":
    # Test the normalizer
    normalizer = TurkishNormalizer()
    
    test_cases = [
        ("mevsim kodu nasıl alınıyor", "SIM"),
        ("paketimi değiştirmek istiyorum", "PLAN"),
        ("faturamı ödemek istiyorum", "BILLING"),
        ("internet çekmiyor", "COVERAGE"),
        ("aymay numaram 123456789012345", "SIM")
    ]
    
    for text, context in test_cases:
        normalized = normalizer.normalize_text(text, context)
        print(f"Input: {text}")
        print(f"Context: {context}")
        print(f"Normalized: {normalized}")
        print("-" * 50)
