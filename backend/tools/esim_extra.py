"""
eSIM-specific tools for activation steps and status tracking.
"""
import logging
from typing import Dict
from datetime import datetime, timedelta

import sys
import os
sys.path.append(os.path.dirname(__file__))

from .types import OperationResult

logger = logging.getLogger(__name__)


class ESIMTools:
    """eSIM-specific tool implementations."""
    
    def __init__(self):
        # Mock activation status tracking
        self.activation_states = {
            "12345": {
                "state": "active",
                "progress": 100,
                "last_updated": datetime.now().isoformat(),
                "steps_completed": ["pending", "downloading", "installing", "active"]
            },
            "67890": {
                "state": "installing", 
                "progress": 75,
                "last_updated": (datetime.now() - timedelta(minutes=5)).isoformat(),
                "steps_completed": ["pending", "downloading", "installing"]
            }
        }
    
    async def execute(self, tool_name: str, arguments: Dict) -> OperationResult:
        """Execute eSIM-specific tools."""
        try:
            if tool_name == "get_activation_steps":
                return await self._get_activation_steps(arguments)
            elif tool_name == "get_activation_status":
                return await self._get_activation_status(arguments)
            else:
                return OperationResult(
                    success=False,
                    error=f"Unknown eSIM tool: {tool_name}"
                )
        except Exception as e:
            logger.error(f"Error executing {tool_name}: {e}")
            return OperationResult(
                success=False,
                error="İşlem sırasında bir hata oluştu"
            )
    
    async def _get_activation_steps(self, args: Dict) -> OperationResult:
        """Get OS-specific activation instructions."""
        os_type = args.get("os_type", "").strip()
        
        if os_type == "iOS":
            steps = [
                "1. Ayarlar uygulamasını açın",
                "2. 'Hücresel' veya 'Mobil Veri' seçeneğine dokunun", 
                "3. 'Hücresel Plan Ekle' seçeneğini seçin",
                "4. QR kodu tarayın veya 'Ayrıntıları Elle Gir' seçeneğini kullanın",
                "5. LPA kodunu girin: [activation_code]",
                "6. 'Hücresel Plan Ekle' düğmesine dokunun",
                "7. Aktivasyon tamamlanana kadar bekleyin (2-5 dakika)",
                "8. Yeni eSIM'i varsayılan hat olarak ayarlayın"
            ]
        elif os_type == "Android":
            steps = [
                "1. Ayarlar uygulamasını açın",
                "2. 'Ağ ve İnternet' veya 'Bağlantılar' bölümüne gidin",
                "3. 'SIM kartlar' veya 'Mobil ağlar' seçeneğini seçin",
                "4. 'SIM kart ekle' veya '+' simgesine dokunun",
                "5. 'Bunun yerine SIM'i indir' seçeneğini seçin",
                "6. QR kodu tarayın veya LPA kodunu manuel girin",
                "7. 'İndir' düğmesine dokunun",
                "8. Aktivasyon işleminin tamamlanmasını bekleyin",
                "9. eSIM'i etkinleştirin ve veri planını seçin"
            ]
        else:
            return OperationResult(
                success=False,
                error="Desteklenmeyen işletim sistemi. iOS veya Android belirtin."
            )
        
        return OperationResult(
            success=True,
            data={
                "os_type": os_type,
                "steps": steps,
                "estimated_time": "5-10 dakika",
                "requirements": [
                    "Aktif internet bağlantısı",
                    "eSIM destekli cihaz",
                    "Aktivasyon kodu"
                ]
            }
        )
    
    async def _get_activation_status(self, args: Dict) -> OperationResult:
        """Check eSIM activation progress."""
        customer_id = args.get("customer_id")
        
        if customer_id not in self.activation_states:
            # Default state for new activations
            self.activation_states[customer_id] = {
                "state": "pending",
                "progress": 0,
                "last_updated": datetime.now().isoformat(),
                "steps_completed": []
            }
        
        status = self.activation_states[customer_id]
        
        # State machine progression
        state_info = {
            "pending": {
                "description": "Aktivasyon başlatılıyor",
                "next_step": "QR kodu tarayın veya LPA kodunu girin"
            },
            "downloading": {
                "description": "eSIM profili indiriliyor", 
                "next_step": "İndirme işlemi devam ediyor"
            },
            "installing": {
                "description": "eSIM profili yükleniyor",
                "next_step": "Kurulum tamamlanıyor"
            },
            "active": {
                "description": "eSIM başarıyla aktifleştirildi",
                "next_step": "Kullanıma hazır"
            },
            "failed": {
                "description": "Aktivasyon başarısız",
                "next_step": "Teknik destek ile iletişime geçin"
            }
        }
        
        current_state = status["state"]
        info = state_info.get(current_state, state_info["pending"])
        
        # Simulate progress for non-active states
        if current_state not in ["active", "failed"]:
            # Advance state occasionally for demo
            import random
            if random.random() < 0.3:  # 30% chance to advance
                states = ["pending", "downloading", "installing", "active"]
                current_idx = states.index(current_state)
                if current_idx < len(states) - 1:
                    new_state = states[current_idx + 1]
                    self.activation_states[customer_id]["state"] = new_state
                    self.activation_states[customer_id]["progress"] = (current_idx + 1) * 25
                    self.activation_states[customer_id]["last_updated"] = datetime.now().isoformat()
                    if new_state not in status["steps_completed"]:
                        self.activation_states[customer_id]["steps_completed"].append(new_state)
                    
                    # Update for response
                    current_state = new_state
                    info = state_info.get(current_state, info)
        
        return OperationResult(
            success=True,
            data={
                "customer_id": customer_id,
                "current_state": current_state,
                "progress_percentage": self.activation_states[customer_id]["progress"],
                "description": info["description"],
                "next_step": info["next_step"],
                "last_updated": self.activation_states[customer_id]["last_updated"],
                "estimated_completion": "2-5 dakika" if current_state != "active" else "Tamamlandı"
            }
        )
