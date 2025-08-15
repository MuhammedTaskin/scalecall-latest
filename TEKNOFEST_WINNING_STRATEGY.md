# TEKNOFEST 2025 - KAZANMA STRATEJİSİ 🏆

## 🎯 KRİTİK: Puanlama Sistemi
**SKOR = Model Çıktı Doğruluğu** (sunum ikincil)

## ⏰ Zaman Planı (24 saat kaldı)

### PHASE 1: Dataset & Training (0-12 saat)
#### Ekip 1: Dataset Finalizasyon
- [ ] 500+ konuşma tamamla (Flash Heavy devam)
- [ ] ElevenLabs TTS - 200 konuşma ses
- [ ] Training format hazırla

#### Ekip 2: Model Eğitimi
- [ ] Gemma 3N fine-tuning başlat
- [ ] Persona switching mekanizması
- [ ] Tool calling entegrasyonu

### PHASE 2: Test Sistemi (12-18 saat) 🔴 KRİTİK
#### Ekip 1: Test Dataset Oluştur
```python
test_scenarios = [
    # Edge cases
    "Yurtdışında telefon çalındı",
    "Acil arama yapamıyorum",
    "Faturada haksız ücret",
    
    # Complex multi-issue
    "eSIM + fatura + plan değişikliği",
    "Numara taşıma + roaming + teknik",
    
    # Emotion handling
    "Çok sinirli müşteri",
    "Yaşlı ve kafası karışık",
    "Acelesinde işadamı",
    
    # Regional dialects
    "Karadeniz aksanı + teknik sorun",
    "Güneydoğu + fatura itirazı",
    
    # Tool chain tests
    "5+ tool kullanımı gereken",
    "3 agent handoff gereken",
    
    # Interruption handling
    "Bağlantı kopuyor",
    "Arka planda bebek ağlıyor",
    
    # 100+ test senaryosu
]
```

#### Ekip 2: Otomatik Test Pipeline
```python
class ModelTester:
    def __init__(self):
        self.test_cases = load_test_cases()
        self.model = load_model()
        
    def run_tests(self):
        results = []
        for test in self.test_cases:
            output = self.model.generate(test.input)
            score = self.evaluate(output, test.expected)
            results.append({
                "test": test.id,
                "score": score,
                "issues": self.identify_issues(output)
            })
        return results
    
    def identify_issues(self, output):
        # Tool doğruluğu
        # Handoff mantığı
        # Duygu uyumu
        # Çözüm kalitesi
        pass
```

### PHASE 3: Sürekli İyileştirme (18-24 saat)
#### Döngü:
1. **Test et** → Sorunları bul
2. **Fine-tune** → Modeli güncelle
3. **Test et** → Skor arttı mı?
4. **Tekrarla** → Son dakikaya kadar

## 📈 Başarı Metrikleri

### Vadi Test Kategorileri (Tahmin):
1. **Tool Accuracy** (30%)
   - Doğru tool seçimi
   - Parametre doğruluğu
   - Tool chain mantığı

2. **Handoff Logic** (20%)
   - Doğru agent yönlendirme
   - Context preservation
   - Handoff timing

3. **Problem Resolution** (30%)
   - Sorunu çözme kalitesi
   - Adım sayısı optimizasyonu
   - Müşteri memnuniyeti

4. **Language Quality** (20%)
   - Türkçe doğruluğu
   - Diyalog doğallığı
   - Empati ve profesyonellik

## 🔥 Kritik Farklar

### Bizim Avantajlarımız:
1. **500+ çeşitli konuşma** (diğerleri 100-200)
2. **37 farklı ses** (diğerleri 5-10)
3. **10 bölgesel diyalekt** (diğerleri yok)
4. **100+ edge case** (diğerleri standart)
5. **Otomatik test pipeline** (ŞİMDİ KURACAĞIZ)

### Yapılacaklar:
1. **TEST DATASET** - 200+ senaryo HEMEN
2. **AUTO-TESTER** - Sürekli test scripti
3. **SCORER** - Kendi skorlama sistemimiz
4. **MONITOR** - Canlı performans takibi

## 🏁 Son 4 Saat Stratejisi

### "Hail Mary" Optimizasyonları:
- Temperature tuning
- Tool threshold ayarı
- Handoff agresifliği
- Emergency fallback logic
- Timeout handling

### Test Odakları:
- En çok hata yapılan 10 senaryo
- Vadi'nin muhtemel edge case'leri
- Yarışmacıların kaçıracağı detaylar

## 💡 Önemli Notlar

**Geçen yıl 3.nün tavsiyesi:**
> "Test verisini geç oluşturduk, en başında olsaydı biri modelde çalışırken diğeri test edip sorunları not edebilirdi"

**BİZ:** Test sistemini ŞİMDİ kuruyoruz! 12 saat test & iyileştirme = 🏆

## 🎯 Hedef

**Vadi Test Skoru:** %95+
- Tool accuracy: %98
- Handoff success: %95
- Resolution quality: %93
- Language quality: %96

**Final Sıralama:** TOP 3 🥇🥈🥉