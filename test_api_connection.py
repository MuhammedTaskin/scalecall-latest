#!/usr/bin/env python3
"""
Test API Connection
Simple test to verify Gemini API key works
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, 'backend')

async def test_api():
    """Test Gemini API connection."""
    
    print("🔑 API BAĞLANTI TESTİ")
    print("="*30)
    
    try:
        from backend.professional_esim_agent import ProfessionalESIMAgent
        
        print("✅ Professional agent modülü yüklendi")
        
        # Initialize agent
        agent = ProfessionalESIMAgent()
        print("✅ Agent başlatıldı")
        
        # Test simple message
        test_message = "Merhaba, test mesajı"
        print(f"📤 Test mesajı gönderiliyor: '{test_message}'")
        
        response = await agent.process_message(test_message)
        print(f"📥 Agent yanıtı: {response}")
        
        print("\n✅ API BAĞLANTISI BAŞARILI!")
        
    except Exception as e:
        print(f"❌ API BAĞLANTI HATASI: {e}")
        print("\n🔧 Çözüm önerileri:")
        print("1. GEMINI_API_KEY environment variable'ını kontrol edin")
        print("2. API key'in geçerli olduğunu doğrulayın")
        print("3. İnternet bağlantınızı kontrol edin")

if __name__ == "__main__":
    asyncio.run(test_api())
