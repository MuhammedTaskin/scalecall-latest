"""
Anti-Memorization Training System
Ensures model learns reasoning patterns rather than memorizing responses
"""
import random
import json
from typing import Dict, List, Any
from dataset_step1_foundation import TurkishTelcoFoundation

class AntiMemorizationTrainer(TurkishTelcoFoundation):
    """Advanced training techniques to prevent memorization and encourage reasoning."""
    
    def __init__(self):
        super().__init__()
        
        # Variable response templates for same intent
        self.response_variations = {
            "verification_success": [
                "Kimlik doğrulama başarılı, {name} hanım/bey. Size nasıl yardımcı olabilirim?",
                "Doğrulama tamam, {name}. Hangi işlemi yapmak istiyorsunuz?", 
                "Merhaba {name}, kimliğiniz onaylandı. Devam edebiliriz.",
                "Hoş geldiniz {name}, sistem doğrulaması tamamlandı. Ne yapabilirim?",
                "Kimlik kontrolü başarılı. Merhaba {name}, yardımcı olmaya hazırım."
            ],
            "tool_call_reasoning": [
                "Bu durumda {tool_name} aracını kullanmam gerekiyor.",
                "Size yardımcı olmak için {tool_name} kontrolü yapmalıyım.",
                "İhtiyacınızı karşılamak adına {tool_name} çağrısı yapıyorum.",
                "Doğru bilgiyi almanız için {tool_name} sorgusu gerekli.",
                "En iyi hizmeti verebilmek için {tool_name} kontrol ediyorum."
            ],
            "error_handling": [
                "Bir sorun oluştu, alternatif çözüm arıyorum.",
                "Bu yöntem çalışmadı, farklı bir yaklaşım deneyeceğim.",
                "Teknik bir engel var, başka bir yol deneyelim.",
                "Sistem hatası tespit edildi, çözüm üretiyorum.",
                "Beklenmedik durum, yeni strateji belirliyorum."
            ]
        }
        
        # Reasoning explanation templates
        self.reasoning_explanations = [
            "Çünkü bu durum için en uygun araç bu.",
            "Bu bilgiyi almak için gerekli adım.",
            "Güvenlik protokolü gereği bu kontrolü yapmalıyım.",
            "Size en iyi hizmeti verebilmek için bu gerekli.",
            "Doğru işlemi yapabilmek için bu bilgi şart."
        ]
        
        # Context variation patterns
        self.context_variations = {
            "formal": {
                "greeting": "Sayın müşterimiz",
                "politeness": "lütfen",
                "closing": "İyi günler dilerim"
            },
            "friendly": {
                "greeting": "Merhaba",
                "politeness": "rica etsem", 
                "closing": "Size yardımcı olmaktan memnunum"
            },
            "professional": {
                "greeting": "Hoş geldiniz",
                "politeness": "gerekirse",
                "closing": "Başka sorunuz var mı?"
            }
        }
    
    def generate_reasoning_diverse_dataset(self, base_dialogs: List[Dict], 
                                         variation_factor: int = 5) -> List[Dict]:
        """Generate multiple diverse variations of each dialog to prevent memorization."""
        diverse_dataset = []
        
        for base_dialog in base_dialogs:
            # Original dialog
            diverse_dataset.append(base_dialog)
            
            # Generate variations
            for i in range(variation_factor - 1):
                varied_dialog = self._create_dialog_variation(base_dialog, variation_id=i)
                diverse_dataset.append(varied_dialog)
        
        return diverse_dataset
    
    def _create_dialog_variation(self, base_dialog: Dict, variation_id: int) -> Dict:
        """Create a variation of the dialog with different expressions but same logic."""
        variation = base_dialog.copy()
        conversations = []
        
        # Choose context style for this variation
        context_style = random.choice(["formal", "friendly", "professional"])
        
        for turn in base_dialog["conversations"]:
            if turn["role"] == "user":
                # Vary user expressions while keeping intent
                varied_user_turn = self._vary_user_expression(turn)
                conversations.append(varied_user_turn)
                
            elif turn["role"] == "assistant":
                content = turn["content"][0]["text"]
                
                # Don't vary JSON structures - keep them exact
                if content.startswith("{") and content.endswith("}"):
                    conversations.append(turn)
                else:
                    # Vary natural language responses
                    varied_assistant_turn = self._vary_assistant_response(
                        turn, context_style, base_dialog.get("customer_data", {})
                    )
                    conversations.append(varied_assistant_turn)
            else:
                conversations.append(turn)
        
        variation["conversations"] = conversations
        variation["variation_id"] = variation_id
        variation["context_style"] = context_style
        
        return variation
    
    def _vary_user_expression(self, user_turn: Dict) -> Dict:
        """Vary user expressions while preserving intent."""
        original_text = user_turn["content"][0]["text"]
        
        # Skip tool_result messages
        if original_text.startswith("<tool_result>"):
            return user_turn
        
        # Simple expression variations for common patterns
        variations = {
            "kimlik doğrulama": ["kimlik onayı", "doğrulama yapma", "kendimi tanıtma"],
            "paket değiştir": ["tarife değişikliği", "plan değiştirme", "abonelik güncelleme"],
            "aktivasyon kodu": ["etkinleştirme kodu", "QR kod", "kurulum kodu"],
            "cihaz kontrol": ["telefon kontrol", "uyumluluk kontrol", "IMEI kontrol"]
        }
        
        varied_text = original_text
        for original, alternatives in variations.items():
            if original in original_text.lower():
                alternative = random.choice(alternatives)
                varied_text = original_text.lower().replace(original, alternative)
                break
        
        varied_turn = user_turn.copy()
        varied_turn["content"][0]["text"] = varied_text
        return varied_turn
    
    def _vary_assistant_response(self, assistant_turn: Dict, context_style: str, 
                               customer_data: Dict) -> Dict:
        """Vary assistant responses while maintaining meaning and tool calling logic."""
        original_text = assistant_turn["content"][0]["text"]
        
        # Apply context style
        style_config = self.context_variations[context_style]
        
        # Identify response type and vary accordingly
        if "doğrulama" in original_text and "başarılı" in original_text:
            # Verification success responses
            template = random.choice(self.response_variations["verification_success"])
            customer_name = customer_data.get("name", "değerli müşterimiz")
            varied_text = template.format(name=customer_name)
            
        elif "kontrol" in original_text or "sorgu" in original_text:
            # Tool reasoning responses  
            varied_text = self._vary_tool_reasoning_response(original_text)
            
        elif "hata" in original_text or "sorun" in original_text:
            # Error handling responses
            varied_text = random.choice(self.response_variations["error_handling"])
            
        else:
            # General response variation
            varied_text = self._apply_general_variations(original_text, style_config)
        
        varied_turn = assistant_turn.copy()
        varied_turn["content"][0]["text"] = varied_text
        return varied_turn
    
    def _vary_tool_reasoning_response(self, original_text: str) -> str:
        """Vary tool reasoning explanations."""
        # Extract potential tool name from context
        tools = ["verify_user", "get_user_info", "check_device_registration", 
                "get_available_packages", "reissue_activation_code"]
        
        detected_tool = None
        for tool in tools:
            if tool.replace("_", " ") in original_text:
                detected_tool = tool
                break
        
        if detected_tool:
            template = random.choice(self.response_variations["tool_call_reasoning"])
            tool_display = detected_tool.replace("_", " ").replace("get ", "").replace("check ", "")
            return template.format(tool_name=tool_display)
        
        return original_text
    
    def _apply_general_variations(self, text: str, style_config: Dict) -> str:
        """Apply general stylistic variations."""
        varied_text = text
        
        # Add politeness markers based on style
        if style_config["politeness"] not in varied_text:
            varied_text = f"{varied_text} {style_config['politeness']}"
        
        # Vary sentence connectors
        connectors = {
            "şimdi": ["artık", "bundan sonra", "bu aşamada"],
            "önce": ["ilk olarak", "başlangıçta", "başta"],
            "sonra": ["daha sonra", "ardından", "takiben"]
        }
        
        for original, alternatives in connectors.items():
            if original in varied_text:
                alternative = random.choice(alternatives)
                varied_text = varied_text.replace(original, alternative)
                break
        
        return varied_text
    
    def generate_adversarial_test_cases(self, base_scenarios: List[Dict]) -> List[Dict]:
        """Generate adversarial test cases to check reasoning vs memorization."""
        adversarial_cases = []
        
        for base_scenario in base_scenarios:
            # Case 1: Same user intent but completely different context
            adversarial_1 = self._create_context_shifted_case(base_scenario)
            adversarial_cases.append(adversarial_1)
            
            # Case 2: Novel error conditions not seen in training
            adversarial_2 = self._create_novel_error_case(base_scenario)
            adversarial_cases.append(adversarial_2)
            
            # Case 3: Reverse tool sequence requirement
            adversarial_3 = self._create_reverse_sequence_case(base_scenario)
            adversarial_cases.append(adversarial_3)
            
            # Case 4: Hybrid scenario combining multiple intents
            adversarial_4 = self._create_hybrid_intent_case(base_scenario)
            adversarial_cases.append(adversarial_4)
        
        return adversarial_cases
    
    def _create_context_shifted_case(self, base_scenario: Dict) -> Dict:
        """Create case with same logic but different context details."""
        shifted_case = base_scenario.copy()
        
        # Change all specific details but keep logic
        new_customer_data = self.generate_customer_data()
        shifted_case["customer_data"] = new_customer_data
        
        # Update conversations with new data
        conversations = []
        for turn in base_scenario["conversations"]:
            if turn["role"] == "assistant" and "tool_call" in turn["content"][0]["text"]:
                # Update tool call arguments with new customer data
                try:
                    tool_call = json.loads(turn["content"][0]["text"])
                    if "maiden_name" in tool_call["tool_call"]["arguments"]:
                        tool_call["tool_call"]["arguments"]["maiden_name"] = new_customer_data["maiden_name"]
                    if "msisdn" in tool_call["tool_call"]["arguments"]:
                        tool_call["tool_call"]["arguments"]["msisdn"] = new_customer_data["msisdn"]
                    if "imei" in tool_call["tool_call"]["arguments"]:
                        tool_call["tool_call"]["arguments"]["imei"] = new_customer_data["imei"]
                    
                    updated_turn = turn.copy()
                    updated_turn["content"][0]["text"] = json.dumps(tool_call, ensure_ascii=False)
                    conversations.append(updated_turn)
                except:
                    conversations.append(turn)
            else:
                conversations.append(turn)
        
        shifted_case["conversations"] = conversations
        shifted_case["test_type"] = "context_shifted"
        
        return shifted_case
    
    def _create_novel_error_case(self, base_scenario: Dict) -> Dict:
        """Create case with novel error conditions."""
        error_case = base_scenario.copy()
        
        # Novel error messages not seen in training
        novel_errors = [
            "Geçici sistem bakımı nedeniyle işlem yapılamıyor",
            "Bölgesel ağ yoğunluğu tespit edildi",
            "Güvenlik protokolü güncellemesi gerekli",
            "Cihaz yazılımı uyumsuzluğu bulundu"
        ]
        
        conversations = error_case["conversations"].copy()
        
        # Find first tool result and replace with novel error
        for i, turn in enumerate(conversations):
            if turn["role"] == "user" and turn["content"][0]["text"].startswith("<tool_result>"):
                novel_error = random.choice(novel_errors)
                error_result = {"success": False, "error": novel_error}
                conversations[i]["content"][0]["text"] = f"<tool_result>{json.dumps(error_result, ensure_ascii=False)}</tool_result>"
                break
        
        error_case["conversations"] = conversations
        error_case["test_type"] = "novel_error"
        
        return error_case
    
    def _create_reverse_sequence_case(self, base_scenario: Dict) -> Dict:
        """Create case requiring reverse of typical tool sequence."""
        reverse_case = base_scenario.copy()
        reverse_case["test_type"] = "reverse_sequence"
        
        # This would require the model to reason that sometimes
        # device check should come before verification, etc.
        # Implementation would rebuild conversation with logical reverse sequence
        
        return reverse_case
    
    def _create_hybrid_intent_case(self, base_scenario: Dict) -> Dict:
        """Create case combining multiple user intents."""
        hybrid_case = base_scenario.copy()
        
        # Combine multiple intents in user request
        hybrid_request = "Paket değiştirmek istiyorum ama önce faturamda hata olup olmadığını kontrol edebilir misiniz? Ayrıca eSIM aktivasyonu da yapacağım."
        
        conversations = [
            {"role": "user", "content": [{"type": "text", "text": hybrid_request}]},
            {"role": "assistant", "content": [{"type": "text", "text": "Üç farklı konunuz var. Öncelik sırası nasıl olsun? Fatura kontrolü, paket değişikliği ve eSIM aktivasyonu."}]}
        ]
        
        hybrid_case["conversations"] = conversations
        hybrid_case["test_type"] = "hybrid_intent"
        
        return hybrid_case
    
    def create_reasoning_validation_prompts(self) -> List[Dict]:
        """Create prompts specifically designed to test reasoning vs memorization."""
        validation_prompts = [
            {
                "prompt": "Müşteri hiç görmediğim bir hata kodu veriyor. Ne yapmalıyım?",
                "expected_reasoning": "create_support_ticket with detailed description",
                "reasoning_test": "Novel situation handling"
            },
            {
                "prompt": "İki farklı paket arasında kararsız kalan müşteriye nasıl yardım ederim?",
                "expected_reasoning": "get_user_info to understand usage, then compare packages",
                "reasoning_test": "Comparison methodology"
            },
            {
                "prompt": "Sistem şu an yavaş çalışıyor, müşteri acelesi var. Nasıl hareket etmeliyim?",
                "expected_reasoning": "Prioritize, explain situation, provide alternatives",
                "reasoning_test": "Crisis management"
            },
            {
                "prompt": "Müşteri kızgın ve sürekli konu değiştiriyor. Nasıl yönetmeliyim?",
                "expected_reasoning": "Listen, acknowledge, guide conversation systematically",
                "reasoning_test": "Difficult customer handling"
            }
        ]
        
        return validation_prompts

print("✅ Anti-memorization trainer ready - ensures flexible reasoning over pattern matching")
