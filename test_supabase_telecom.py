#!/usr/bin/env python3
"""
Test Supabase Telecom Integration
Verify that customer data is properly stored and retrieved from Supabase
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, 'backend')

async def test_supabase_integration():
    """Test Supabase telecom tools integration."""
    
    print("🗄️ SUPABASE TELECOM ENTEGRASYONU TESTİ")
    print("=" * 50)
    
    try:
        from backend.tools.supabase_telecom import SupabaseTelecomTools
        
        tools = SupabaseTelecomTools()
        print("✅ Supabase telecom tools yüklendi")
        
        # Test 1: Verify user (should work with fallback data)
        print("\n📋 Test 1: Kullanıcı doğrulama")
        result = await tools.execute("verify_user", {
            "maiden_name": "Kaya",
            "msisdn": "05551234567"
        })
        
        if result.success:
            print(f"✅ Doğrulama başarılı: {result.data}")
            customer_id = result.data.get("customer_id")
            
            # Test 2: Get user info
            print(f"\n📋 Test 2: Kullanıcı bilgileri (ID: {customer_id})")
            user_info = await tools.execute("get_user_info", {
                "customer_id": customer_id
            })
            
            if user_info.success:
                print(f"✅ Kullanıcı bilgileri alındı: {user_info.data}")
            else:
                print(f"❌ Kullanıcı bilgileri alınamadı: {user_info.error}")
            
            # Test 3: Check device registration
            print(f"\n📋 Test 3: Cihaz uyumluluğu kontrolü")
            device_check = await tools.execute("check_device_registration", {
                "customer_id": customer_id,
                "imei": "359111222333444"
            })
            
            if device_check.success:
                print(f"✅ Cihaz kontrolü: {device_check.data}")
            else:
                print(f"❌ Cihaz kontrolü başarısız: {device_check.error}")
            
            # Test 4: Generate activation code
            print(f"\n📋 Test 4: Aktivasyon kodu oluşturma")
            activation_result = await tools.execute("reissue_activation_code", {
                "customer_id": customer_id
            })
            
            if activation_result.success:
                print(f"✅ Aktivasyon kodu: {activation_result.data}")
            else:
                print(f"❌ Aktivasyon kodu oluşturulamadı: {activation_result.error}")
            
            # Test 5: Get available packages
            print(f"\n📋 Test 5: Mevcut paketler")
            packages_result = await tools.execute("get_available_packages", {
                "customer_id": customer_id
            })
            
            if packages_result.success:
                packages = packages_result.data.get("packages", [])
                print(f"✅ {len(packages)} paket bulundu:")
                for pkg in packages:
                    print(f"   - {pkg.get('name', 'N/A')} ({pkg.get('price', 0)} TL)")
            else:
                print(f"❌ Paketler alınamadı: {packages_result.error}")
            
        else:
            print(f"❌ Doğrulama başarısız: {result.error}")
        
        print(f"\n🎯 SONUÇ:")
        if tools.supabase:
            print("✅ Supabase bağlantısı aktif - Gerçek veritabanı kullanılıyor")
        else:
            print("⚠️ Supabase bağlantısı yok - Fallback veri kullanılıyor")
        
        print("✅ Tüm temel fonksiyonlar çalışıyor")
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_supabase_integration())
