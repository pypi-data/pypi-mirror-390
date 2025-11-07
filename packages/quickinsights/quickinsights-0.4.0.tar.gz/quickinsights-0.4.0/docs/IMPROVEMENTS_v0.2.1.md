# QuickInsights v0.2.1 - İyileştirmeler ve Yeni Özellikler

## 🚀 **Yeni Eklenen Özellikler**

### **1. 🔧 Kapsamlı Hata Yönetimi Sistemi**

#### **A. Custom Exception Sınıfları**
```python
import quickinsights as qi

# Veri doğrulama hataları
try:
    qi.ValidationUtils.validate_dataframe(invalid_data)
except qi.DataValidationError as e:
    print(e.get_user_friendly_message())  # ❌ Veri doğrulama hatası: ...
    print(e.get_technical_details())      # Teknik detaylar

# Performans hataları
try:
    # Büyük veri işlemi
    pass
except qi.PerformanceError as e:
    print(e.get_user_friendly_message())  # ⚡ Performans hatası: ...
```

#### **B. Merkezi Hata Yöneticisi**
```python
# Global hata yöneticisi
handler = qi.global_error_handler

# Hata istatistikleri
summary = handler.get_error_summary()
print(f"Toplam hata: {summary['total_errors']}")
print(f"Hata türleri: {summary['error_types']}")

# Hata geçmişini temizle
handler.clear_history()
```

#### **C. Güvenli Fonksiyon Çalıştırma**
```python
# Fonksiyonu güvenli şekilde çalıştır
success, result, error = qi.safe_execute(
    my_function, 
    arg1, arg2, 
    error_context={"operation": "data_analysis"}
)

if success:
    print(f"Sonuç: {result}")
else:
    print(f"Hata: {error}")
```

### **2. ⚙️ Merkezi Konfigürasyon Yönetimi**

#### **A. Konfigürasyon Erişimi**
```python
# Global konfigürasyon
config = qi.get_config()

# Performans ayarları
print(f"Maksimum bellek: {config.performance.max_memory_gb} GB")
print(f"Paralel işçi sayısı: {config.performance.parallel_workers}")

# Görselleştirme ayarları
print(f"Varsayılan backend: {config.visualization.default_backend}")
print(f"Figure boyutu: {config.visualization.figure_size}")

# ML ayarları
print(f"Random state: {config.ml.random_state}")
print(f"Test boyutu: {config.ml.test_size}")
```

#### **B. Konfigürasyon Güncelleme**
```python
# Belirli bölümü güncelle
qi.update_global_config('performance', max_memory_gb=16, parallel_workers=8)

# Konfigürasyonu kaydet
config.save_config('my_config.json')

# Varsayılanlara sıfırla
qi.reset_global_config('performance')  # Sadece performance
qi.reset_global_config()               # Tümü
```

#### **C. Environment Variables**
```bash
# Sistem seviyesinde konfigürasyon
export QI_MAX_MEMORY_GB=16
export QI_PARALLEL_WORKERS=8
export QI_GPU_ENABLED=true
export QI_LOG_LEVEL=DEBUG
```

### **3. 💾 Akıllı Önbellekleme Sistemi**

#### **A. Temel Önbellekleme**
```python
# Global önbellek
cache = qi.get_cache()

# Değer kaydet
cache.set("my_key", my_data)

# Değer al
result = cache.get("my_key", default_value)

# Önbellek istatistikleri
stats = cache.get_stats()
print(f"Hit rate: {stats['hit_rate']:.2%}")
print(f"Mevcut boyut: {stats['current_size_mb']:.1f} MB")
```

#### **B. Fonksiyon Önbellekleme**
```python
# Decorator ile otomatik önbellekleme
@qi.cache_function(max_age_seconds=3600, key_prefix="analysis")
def expensive_analysis(data):
    # Bu fonksiyon sonucu 1 saat boyunca önbellekte tutulur
    return complex_calculation(data)

# Manuel önbellekleme
def my_function(data):
    cache_key = f"my_function:{hash(str(data))}"
    
    # Önbellekten kontrol et
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result
    
    # Hesapla ve önbellekle
    result = expensive_calculation(data)
    cache.set(cache_key, result)
    return result
```

#### **C. Önbellek Optimizasyonu**
```python
# Otomatik optimizasyon
optimization = cache.optimize()
print(f"Temizlenen öğe: {optimization['items_removed']}")
print(f"Kazanılan bellek: {optimization['size_freed_mb']:.1f} MB")

# Kalıcı önbellekleme
persistent_cache = qi.SmartCache(
    max_size_mb=2000,
    persistence_enabled=True,
    cache_dir="./my_cache"
)
```

### **4. 🧠 Gelişmiş Bellek Yönetimi**

#### **A. DataFrame Bellek Optimizasyonu**
```python
# Otomatik bellek optimizasyonu
df = pd.read_csv('large_file.csv')
print(f"Orijinal bellek: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")

optimized_df = qi.optimize_dataframe_memory(df)
print(f"Optimize edilmiş bellek: {optimized_df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")

# Agresif optimizasyon (precision kaybı olabilir)
aggressive_df = qi.optimize_dataframe_memory(df, aggressive=True)
```

#### **B. Chunk Processing**
```python
# Büyük DataFrame'leri chunk'lar halinde işle
def process_chunk(chunk):
    return chunk.groupby('category').agg({'value': 'sum'})

result = qi.chunk_process_dataframe(
    large_df, 
    process_chunk,
    chunk_size=10000,
    parallel=True
)
```

#### **C. Bellek Profili ve İzleme**
```python
# Bellek profili çıkar
profile = qi.get_memory_profile(df)
print(f"Toplam bellek: {profile['total_memory_mb']:.1f} MB")
print(f"Optimizasyon potansiyeli: {profile['optimization_potential']['total_potential_mb']:.1f} MB")

# Bellek durumu
memory_status = qi.get_memory_manager().get_memory_status()
print(f"Mevcut kullanım: {memory_status['current_usage']['usage_percent']:.1f}%")

# Öneriler
for rec in memory_status['optimization_recommendations']:
    print(f"💡 {rec}")
```

## 📊 **Kullanım Örnekleri**

### **Örnek 1: Güvenli Veri Analizi**
```python
import quickinsights as qi
import pandas as pd

# Veri yükleme
try:
    df = qi.easy_load_data('data.csv')
except qi.DataValidationError as e:
    print(f"Veri yükleme hatası: {e.get_user_friendly_message()}")
    exit(1)

# Bellek optimizasyonu
df = qi.optimize_dataframe_memory(df)

# Güvenli analiz
success, result, error = qi.safe_execute(
    qi.analyze, 
    df, 
    error_context={"operation": "data_analysis"}
)

if success:
    print("Analiz tamamlandı!")
else:
    print(f"Analiz hatası: {error}")
```

### **Örnek 2: Performans Optimizasyonu**
```python
# Konfigürasyon ayarla
qi.update_global_config('performance', max_memory_gb=16, parallel_workers=8)

# Önbellekleme aktifleştir
cache = qi.get_cache()
cache.set("model", trained_model)

# Bellek izleme
with qi.get_memory_manager() as mm:
    # Büyük işlem
    result = qi.chunk_process_dataframe(large_df, complex_operation)
    
    # Bellek durumu
    status = mm.get_memory_status()
    print(f"Bellek kullanımı: {status['current_usage']['usage_percent']:.1f}%")
```

### **Örnek 3: Hata Yönetimi ve Loglama**
```python
# Hata yöneticisi ayarla
handler = qi.ErrorHandler(log_errors=True, show_traceback=True)

# Veri doğrulama
try:
    qi.ValidationUtils.validate_dataframe(df)
    qi.ValidationUtils.validate_column_exists(df, 'target')
    qi.ValidationUtils.validate_numeric_column(df, 'target')
except qi.DataValidationError as e:
    user_message = handler.handle_error(e, {"context": "data_validation"})
    print(user_message)
    
    # Teknik detaylar
    details = e.get_technical_details()
    print(f"Hata kodu: {details['error_code']}")
    print(f"Detaylar: {details['details']}")

# Hata özeti
summary = handler.get_error_summary()
print(f"Toplam hata: {summary['total_errors']}")
```

## 🔧 **Konfigürasyon Dosyası Örneği**

```json
{
  "performance": {
    "max_memory_gb": 16.0,
    "parallel_workers": 8,
    "chunk_size": 20000,
    "cache_enabled": true,
    "cache_size_mb": 2000,
    "gpu_enabled": false,
    "gpu_memory_fraction": 0.8
  },
  "visualization": {
    "default_backend": "plotly",
    "figure_size": [14, 10],
    "dpi": 100,
    "style": "default",
    "color_palette": "viridis",
    "save_format": "png",
    "interactive_mode": true
  },
  "ml": {
    "random_state": 42,
    "test_size": 0.2,
    "cv_folds": 5,
    "n_jobs": -1,
    "verbose": false,
    "early_stopping": true,
    "model_persistence": true
  },
  "data": {
    "default_encoding": "utf-8",
    "missing_value_strategies": ["drop", "impute", "interpolate"],
    "outlier_detection_method": "iqr",
    "data_quality_threshold": 0.8,
    "auto_clean": true,
    "preserve_original": true
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_logging": true,
    "log_file": "quickinsights.log",
    "max_file_size_mb": 10,
    "backup_count": 5
  }
}
```

## 🚨 **Önemli Notlar**

### **1. Geriye Uyumluluk**
- Tüm yeni özellikler mevcut kodlarla uyumlu
- Eski fonksiyonlar aynı şekilde çalışmaya devam ediyor
- Yeni özellikler opsiyonel

### **2. Performans Etkisi**
- Error handling: Minimal performans etkisi
- Configuration: Sadece başlangıçta yüklenir
- Caching: Performansı artırır
- Memory management: Bellek kullanımını optimize eder

### **3. Bağımlılıklar**
- `psutil`: Sistem kaynak izleme için
- Mevcut bağımlılıklar değişmedi

## 🔮 **Gelecek Planları**

### **v0.2.2 (1-2 hafta)**
- [ ] Test coverage %80+ yap
- [ ] API documentation tamamla
- [ ] Performance benchmarking ekle

### **v0.3.0 (1 ay)**
- [ ] Natural language interface
- [ ] Advanced AI features
- [ ] Real-time analytics

### **v0.4.0 (3 ay)**
- [ ] Cloud integration
- [ ] Enterprise features
- [ ] Advanced visualization

## 📞 **Destek ve Geri Bildirim**

Herhangi bir sorun yaşarsanız veya öneriniz varsa:
- GitHub Issues: [https://github.com/ErenAta16/quickinsight_library/issues](https://github.com/ErenAta16/quickinsight_library/issues)
- Email: erena6466@gmail.com

---

**QuickInsights v0.2.1** ile veri analizi daha güvenli, hızlı ve kullanıcı dostu hale geldi! 🎉


