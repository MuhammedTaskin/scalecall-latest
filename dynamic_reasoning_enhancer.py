"""
Dynamic Reasoning Enhancer
Ensures model learns flexible reasoning rather than memorizing patterns
"""
import random
import json
import uuid
from typing import Dict, List, Tuple
from dataset_step1_foundation import TurkishTelcoFoundation

class DynamicReasoningEnhancer(TurkishTelcoFoundation):
    """Enhances dataset for flexible reasoning and prevents memorization."""
    
    def __init__(self):
        super().__init__()
        
        # Reasoning templates that force dynamic thinking
        self.reasoning_triggers = [
            "Bu durumda hangi aracı kullanmalıyım?",
            "Müşterinin ihtiyacını anlamak için ne yapmalıyım?", 
            "Bu bilgiyle bir sonraki adım ne olmalı?",
            "Hangi uzman bu konuya daha iyi yardımcı olabilir?",
            "Bu hatayı nasıl müşteriye nazikçe açıklayabilirim?"
        ]
        
        # Variable conversation flows to prevent memorization
        self.flow_variations = {
            "verification_first": ["verify_user", "get_user_info", "action"],
            "device_check_first": ["check_device_registration", "verify_user", "action"],
            "info_gathering": ["get_user_info", "verify_user", "action"],
            "direct_action": ["verify_user", "action"]
        }
        
        # Error scenarios that require flexible handling
        self.error_scenarios = [
            {
                "error_type": "user_not_found",
                "error_message": "Kullanıcı bulunamadı",
                "expected_reasoning": "Alternative verification methods or registration",
                "flexible_responses": [
                    "Bu bilgilerle müşteri bulunamadı. Alternatif doğrulama yöntemi deneyelim.",
                    "Sistemde kayıt yok gibi görünüyor. Yeni kayıt oluşturmanız gerekebilir.",
                    "Bilgiler eşleşmiyor. Telefon numaranızı tekrar kontrol edebilir miyiz?"
                ]
            },
            {
                "error_type": "device_incompatible", 
                "error_message": "Cihaz eSIM desteklemiyor",
                "expected_reasoning": "Suggest alternatives or provide compatibility info",
                "flexible_responses": [
                    "Cihazınız eSIM desteklemiyor. Fiziksel SIM seçeneklerini gösterebilirim.",
                    "Bu model için eSIM uyumluluğu yok. Alternatif çözümleri değerlendirelim.",
                    "Cihaz uyumsuzluğu tespit edildi. Farklı aktivasyon yöntemleri mevcut."
                ]
            },
            {
                "error_type": "package_unavailable",
                "error_message": "Seçilen paket mevcut değil", 
                "expected_reasoning": "Suggest similar packages or alternatives",
                "flexible_responses": [
                    "Bu paket şu an mevcut değil. Benzer özellikli alternatifleri gösterebilirim.",
                    "Seçtiğiniz tarife geçici olarak durdurulmuş. Yakın seçenekleri değerlendirelim.",
                    "Maalesef bu paket artık sunulmuyor. Size uygun yeni seçenekler var."
                ]
            }
        ]
        
        # Ambiguous scenarios that require reasoning
        self.ambiguous_scenarios = [
            {
                "user_input": "Internetim yavaş",
                "possible_causes": ["coverage", "device", "package_limit", "technical"],
                "reasoning_required": "Determine root cause through questioning",
                "follow_up_questions": [
                    "Hangi bölgedesiniz? Kapsama kontrol edeyim.",
                    "Veri kotanız dolmuş olabilir. Paket durumunuzu kontrol edelim.",
                    "Cihaz ayarlarında bir sorun olabilir. IMEI kontrolü yapalım."
                ]
            },
            {
                "user_input": "Fatura yüksek geldi",
                "possible_causes": ["usage_spike", "package_change", "extra_services", "billing_error"],
                "reasoning_required": "Investigate billing details systematically",
                "follow_up_questions": [
                    "Bu ay kullanım alışkanlığınızda değişiklik oldu mu?",
                    "Ek hizmet aldınız mı? Detaylı fatura kontrolü yapalım.",
                    "Paket değişikliği olmuş olabilir. Geçmişi inceleyelim."
                ]
            }
        ]
    
    def generate_reasoning_chains(self, base_dialog: Dict) -> List[Dict]:
        """Generate multiple reasoning variations of the same scenario."""
        variations = []
        
        # Original dialog
        variations.append(base_dialog)
        
        # Variation 1: Different tool order
        varied_dialog1 = self._vary_tool_sequence(base_dialog)
        if varied_dialog1:
            variations.append(varied_dialog1)
        
        # Variation 2: With error handling
        error_dialog = self._add_error_scenario(base_dialog)
        if error_dialog:
            variations.append(error_dialog)
        
        # Variation 3: Ambiguous start requiring clarification
        ambiguous_dialog = self._add_ambiguity(base_dialog)
        if ambiguous_dialog:
            variations.append(ambiguous_dialog)
        
        # Variation 4: Context switch mid-flow
        context_switch_dialog = self._add_context_switch(base_dialog)
        if context_switch_dialog:
            variations.append(context_switch_dialog)
        
        return variations
    
    def _vary_tool_sequence(self, base_dialog: Dict) -> Dict:
        """Create variation with different but valid tool sequence."""
        if base_dialog.get("scenario_type") != "multi_step":
            return None
        
        # Find a different valid flow
        current_flow = self._extract_tool_sequence(base_dialog)
        if not current_flow:
            return None
        
        # Try different flow pattern
        alternative_flows = [
            ["check_device_registration", "verify_user", "get_user_info"],
            ["get_user_info", "verify_user", "check_device_registration"],
            ["verify_user", "get_user_info", "get_available_packages"]
        ]
        
        for alt_flow in alternative_flows:
            if alt_flow != current_flow[:len(alt_flow)]:
                return self._rebuild_dialog_with_flow(base_dialog, alt_flow)
        
        return None
    
    def _add_error_scenario(self, base_dialog: Dict) -> Dict:
        """Add error handling to dialog for reasoning training."""
        error_scenario = random.choice(self.error_scenarios)
        
        # Find first tool call in dialog
        error_dialog = base_dialog.copy()
        conversations = error_dialog["conversations"].copy()
        
        # Insert error after first tool call
        for i, turn in enumerate(conversations):
            if turn["role"] == "assistant" and "tool_call" in turn["content"][0]["text"]:
                # Next turn should be error result
                if i + 1 < len(conversations) and conversations[i + 1]["role"] == "user":
                    # Replace success with error
                    error_result = {
                        "success": False,
                        "error": error_scenario["error_message"]
                    }
                    conversations[i + 1]["content"][0]["text"] = f"<tool_result>{json.dumps(error_result, ensure_ascii=False)}</tool_result>"
                    
                    # Add flexible error handling response
                    if i + 2 < len(conversations) and conversations[i + 2]["role"] == "assistant":
                        flexible_response = random.choice(error_scenario["flexible_responses"])
                        conversations[i + 2]["content"][0]["text"] = flexible_response
                    
                    break
        
        error_dialog["conversations"] = conversations
        error_dialog["scenario_type"] = f"{base_dialog.get('scenario_type', '')}_with_error"
        error_dialog["has_error_handling"] = True
        
        return error_dialog
    
    def _add_ambiguity(self, base_dialog: Dict) -> Dict:
        """Add ambiguous user input requiring clarification."""
        ambiguous_scenario = random.choice(self.ambiguous_scenarios)
        
        ambiguous_dialog = base_dialog.copy()
        conversations = []
        
        # Start with ambiguous input
        conversations.append({
            "role": "user",
            "content": [{"type": "text", "text": ambiguous_scenario["user_input"]}]
        })
        
        # Assistant asks clarifying question
        clarifying_question = random.choice(ambiguous_scenario["follow_up_questions"])
        conversations.append({
            "role": "assistant", 
            "content": [{"type": "text", "text": clarifying_question}]
        })
        
        # User provides clarification
        conversations.append({
            "role": "user",
            "content": [{"type": "text", "text": "Kapsama sorunlu sanırım, kontrol eder misiniz?"}]
        })
        
        # Then continue with appropriate tool calls
        original_conversations = base_dialog["conversations"][1:]  # Skip original first turn
        conversations.extend(original_conversations)
        
        ambiguous_dialog["conversations"] = conversations
        ambiguous_dialog["scenario_type"] = f"ambiguous_{base_dialog.get('scenario_type', '')}"
        ambiguous_dialog["requires_clarification"] = True
        
        return ambiguous_dialog
    
    def _add_context_switch(self, base_dialog: Dict) -> Dict:
        """Add mid-conversation context switch for reasoning."""
        if len(base_dialog["conversations"]) < 4:
            return None
        
        context_dialog = base_dialog.copy()
        conversations = context_dialog["conversations"].copy()
        
        # Insert interruption after 2-3 turns
        interruption_point = random.randint(2, min(4, len(conversations) - 2))
        
        # Interruption scenarios
        interruptions = [
            "Dur bir dakika, daha acil bir sorun var. İnternetim hiç çalışmıyor!",
            "Bekleyin, önce fatura konusunu halletmem lazım.",
            "Aslında paket değil, cihaz sorunu var sanırım.",
            "Pardon, başka bir konu daha öncelikli."
        ]
        
        interruption_text = random.choice(interruptions)
        
        # Insert interruption
        interruption_turn = {
            "role": "user",
            "content": [{"type": "text", "text": interruption_text}]
        }
        
        # Assistant acknowledges and switches context
        acknowledgment = "Anlıyorum, o konuya odaklanalım. " + self.create_handoff_json("TechAgent")
        acknowledgment_turn = {
            "role": "assistant",
            "content": [{"type": "text", "text": acknowledgment}]
        }
        
        # Insert at interruption point
        conversations.insert(interruption_point, interruption_turn)
        conversations.insert(interruption_point + 1, acknowledgment_turn)
        
        context_dialog["conversations"] = conversations
        context_dialog["scenario_type"] = f"interrupted_{base_dialog.get('scenario_type', '')}"
        context_dialog["has_interruption"] = True
        
        return context_dialog
    
    def generate_reasoning_validation_set(self, size: int = 1000) -> List[Dict]:
        """Generate validation set focused on reasoning assessment."""
        reasoning_dialogs = []
        
        # Generate base scenarios
        for _ in range(size // 4):
            # Create base dialog
            customer_data = self.generate_customer_data()
            
            # Generate scenario that requires multi-step reasoning
            scenario_types = [
                self._generate_diagnostic_scenario,
                self._generate_comparison_scenario,
                self._generate_constraint_scenario,
                self._generate_escalation_scenario
            ]
            
            generator = random.choice(scenario_types)
            dialog = generator(customer_data)
            reasoning_dialogs.append(dialog)
        
        return reasoning_dialogs
    
    def _generate_diagnostic_scenario(self, customer_data: Dict) -> Dict:
        """Generate scenario requiring diagnostic reasoning."""
        return {
            "conversations": [
                {"role": "user", "content": [{"type": "text", "text": "eSIM kurulumu yaptım ama çalışmıyor, ne yapmalıyım?"}]},
                {"role": "assistant", "content": [{"type": "text", "text": "Sorunu tespit etmek için adım adım kontrol edelim. Önce cihazınızı doğrulayalım."}]},
                {"role": "assistant", "content": [{"type": "text", "text": self.create_tool_call_json("check_device_registration", {"imei": customer_data["imei"]})}]},
                {"role": "user", "content": [{"type": "text", "text": self.create_tool_result(True, {"registered": True, "activation_status": "failed"})}]},
                {"role": "assistant", "content": [{"type": "text", "text": "Cihaz kayıtlı ama aktivasyon başarısız. Aktivasyon durumunu detaylı kontrol edelim."}]},
                {"role": "assistant", "content": [{"type": "text", "text": self.create_tool_call_json("get_activation_status", {"customer_id": customer_data["customer_id"]})}]},
                {"role": "user", "content": [{"type": "text", "text": self.create_tool_result(True, {"current_state": "failed", "description": "LPA kod hatası"})}]},
                {"role": "assistant", "content": [{"type": "text", "text": "LPA kodunda hata tespit edildi. Yeni aktivasyon kodu üretip sorunu çözelim."}]}
            ],
            "scenario_type": "diagnostic_reasoning",
            "context": "SIM",
            "reasoning_type": "diagnostic",
            "customer_data": customer_data
        }
    
    def _generate_comparison_scenario(self, customer_data: Dict) -> Dict:
        """Generate scenario requiring comparison reasoning."""
        return {
            "conversations": [
                {"role": "user", "content": [{"type": "text", "text": "Hangi paket daha avantajlı, karar veremiyorum."}]},
                {"role": "assistant", "content": [{"type": "text", "text": "Size en uygun paketi bulmak için kullanım durumunuzu anlayalım. Önce mevcut paketinizi kontrol edeyim."}]},
                {"role": "assistant", "content": [{"type": "text", "text": self.create_tool_call_json("get_user_info", {"customer_id": customer_data["customer_id"]})}]},
                {"role": "user", "content": [{"type": "text", "text": self.create_tool_result(True, {"current_package": "basic_5gb", "usage_pattern": "heavy_user"})}]},
                {"role": "assistant", "content": [{"type": "text", "text": "Yoğun kullanıcısınız. Mevcut seçenekleri getirip ihtiyacınıza göre karşılaştıralım."}]},
                {"role": "assistant", "content": [{"type": "text", "text": self.create_tool_call_json("get_available_packages", {"customer_id": customer_data["customer_id"]})}]},
                {"role": "user", "content": [{"type": "text", "text": self.create_tool_result(True, {"packages": [{"id": "premium_10gb", "price": 149.99}, {"id": "unlimited", "price": 299.99}]})}]},
                {"role": "assistant", "content": [{"type": "text", "text": "Kullanımınıza göre Premium 10GB daha ekonomik. Unlimited sadece çok yoğun kullanımda avantajlı."}]}
            ],
            "scenario_type": "comparison_reasoning", 
            "context": "PLAN",
            "reasoning_type": "comparison",
            "customer_data": customer_data
        }
    
    def _extract_tool_sequence(self, dialog: Dict) -> List[str]:
        """Extract tool sequence from dialog."""
        tools = []
        for turn in dialog["conversations"]:
            if turn["role"] == "assistant" and "tool_call" in turn["content"][0]["text"]:
                try:
                    parsed = json.loads(turn["content"][0]["text"])
                    tools.append(parsed["tool_call"]["name"])
                except:
                    pass
        return tools
    
    def _rebuild_dialog_with_flow(self, base_dialog: Dict, new_flow: List[str]) -> Dict:
        """Rebuild dialog with new tool flow."""
        # This is a simplified version - in practice you'd rebuild the entire conversation
        new_dialog = base_dialog.copy()
        new_dialog["scenario_type"] = f"reordered_{base_dialog.get('scenario_type', '')}"
        new_dialog["tool_sequence_variant"] = new_flow
        return new_dialog

print("✅ Dynamic reasoning enhancer ready - prevents memorization, ensures flexibility")
