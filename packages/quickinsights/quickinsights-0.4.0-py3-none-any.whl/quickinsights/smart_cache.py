"""
QuickInsights - Smart Caching System

Bu modül, akıllı önbellekleme ile performansı artırır ve bellek kullanımını optimize eder.
LRU (Least Recently Used) algoritması ve bellek yönetimi ile çalışır.
"""

import time
import hashlib
import pickle
import gzip
from typing import Any, Dict, Optional, Tuple, List, Union
from collections import OrderedDict
import logging
import psutil
from pathlib import Path

from .error_handling import PerformanceError
from .config import get_config

logger = logging.getLogger(__name__)


class CacheItem:
    """Önbellek öğesi sınıfı"""

    def __init__(
        self,
        key: str,
        value: Any,
        size_bytes: int,
        access_count: int = 0,
        last_access: float = None,
    ):
        self.key = key
        self.value = value
        self.size_bytes = size_bytes
        self.access_count = access_count
        self.last_access = last_access or time.time()
        self.created_at = time.time()

    def update_access(self):
        """Erişim bilgilerini günceller"""
        self.access_count += 1
        self.last_access = time.time()

    def get_age(self) -> float:
        """Öğenin yaşını saniye cinsinden döndürür"""
        return time.time() - self.created_at

    def get_access_score(self) -> float:
        """Erişim skorunu hesaplar (LRU için)"""
        # Son erişim zamanı ve erişim sayısına göre skor
        time_factor = 1.0 / (time.time() - self.last_access + 1)
        access_factor = self.access_count
        return time_factor * access_factor


class SmartCache:
    """Akıllı önbellekleme sistemi"""

    def __init__(
        self,
        max_size_mb: float = 1000,
        compression_threshold_mb: float = 1.0,
        persistence_enabled: bool = False,
        cache_dir: Optional[Union[str, Path]] = None,
    ):
        """
        SmartCache başlatıcısı

        Parameters
        ----------
        max_size_mb : float, default=1000
            Maksimum önbellek boyutu (MB)
        compression_threshold_mb : float, default=1.0
            Sıkıştırma eşiği (MB)
        persistence_enabled : bool, default=False
            Kalıcı önbellekleme aktif mi
        cache_dir : Optional[Union[str, Path]]
            Önbellek dizini
        """
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.compression_threshold_bytes = compression_threshold_mb * 1024 * 1024
        self.persistence_enabled = persistence_enabled

        # Önbellek dizini
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        elif persistence_enabled:
            self.cache_dir = Path.home() / ".quickinsights" / "cache"
        else:
            self.cache_dir = None

        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Önbellek verileri
        self.cache: OrderedDict[str, CacheItem] = OrderedDict()
        self.current_size_bytes = 0
        self.hit_count = 0
        self.miss_count = 0
        self.eviction_count = 0

        # İstatistikler
        self.stats = {
            "total_requests": 0,
            "total_sets": 0,
            "total_evictions": 0,
            "compression_savings": 0,
            "memory_usage": [],
        }

        # Konfigürasyondan yükle
        self._load_config()

        # Kalıcı önbellekten yükle
        if self.persistence_enabled:
            self._load_persistent_cache()

    def _load_config(self):
        """Konfigürasyondan ayarları yükler"""
        try:
            config = get_config()
            self.max_size_bytes = config.performance.cache_size_mb * 1024 * 1024
            logger.info(
                f"Cache configuration loaded: max_size={self.max_size_bytes / (1024*1024):.1f} MB"
            )
        except Exception as e:
            logger.warning(f"Failed to load cache configuration: {e}")

    def _load_persistent_cache(self):
        """Kalıcı önbellekten veri yükler"""
        if not self.cache_dir:
            return

        try:
            cache_file = self.cache_dir / "cache_metadata.pkl"
            if cache_file.exists():
                with open(cache_file, "rb") as f:
                    metadata = pickle.load(f)

                # Metadata'dan önbellek boyutunu kontrol et
                if metadata.get("total_size", 0) > self.max_size_bytes:
                    logger.info("Persistent cache exceeds size limit, will be trimmed")

                # Önbellek dosyalarını yükle
                for key, item_info in metadata.get("items", {}).items():
                    cache_file = self.cache_dir / f"{key}.cache"
                    if cache_file.exists():
                        try:
                            with open(cache_file, "rb") as f:
                                if item_info.get("compressed", False):
                                    data = gzip.decompress(f.read())
                                else:
                                    data = f.read()

                                value = pickle.loads(data)
                                self._add_item(key, value, item_info["size"])
                        except Exception as e:
                            logger.warning(f"Failed to load cache item {key}: {e}")
                            # Bozuk dosyayı sil
                            cache_file.unlink(missing_ok=True)

                logger.info(f"Persistent cache loaded: {len(self.cache)} items")

        except Exception as e:
            logger.warning(f"Failed to load persistent cache: {e}")

    def _save_persistent_cache(self):
        """Önbelleği kalıcı olarak kaydeder"""
        if not self.cache_dir or not self.persistence_enabled:
            return

        try:
            # Metadata oluştur
            metadata = {"total_size": self.current_size_bytes, "items": {}}

            # Her öğe için metadata
            for key, item in self.cache.items():
                cache_file = self.cache_dir / f"{key}.cache"

                # Değeri kaydet
                data = pickle.dumps(item.value)
                if item.size_bytes > self.compression_threshold_bytes:
                    data = gzip.compress(data)
                    compressed = True
                else:
                    compressed = False

                with open(cache_file, "wb") as f:
                    f.write(data)

                metadata["items"][key] = {
                    "size": item.size_bytes,
                    "compressed": compressed,
                    "access_count": item.access_count,
                    "last_access": item.last_access,
                }

            # Metadata'yı kaydet
            with open(self.cache_dir / "cache_metadata.pkl", "wb") as f:
                pickle.dump(metadata, f)

            logger.debug(f"Persistent cache saved: {len(self.cache)} items")

        except Exception as e:
            logger.error(f"Failed to save persistent cache: {e}")

    def _add_item(self, key: str, value: Any, size_bytes: int) -> None:
        """Önbelleğe yeni öğe ekler"""
        item = CacheItem(key, value, size_bytes)
        self.cache[key] = item
        self.current_size_bytes += size_bytes
        self.stats["total_sets"] += 1

        # Boyut kontrolü
        if self.current_size_bytes > self.max_size_bytes:
            self._evict_items()

    def _evict_items(self) -> None:
        """Gereksiz öğeleri önbellekten çıkarır"""
        if self.current_size_bytes <= self.max_size_bytes:
            return

        # LRU algoritması ile öğeleri sırala
        items_to_evict = []
        for key, item in self.cache.items():
            score = item.get_access_score()
            items_to_evict.append((key, item, score))

        # En düşük skorlu öğeleri çıkar
        items_to_evict.sort(key=lambda x: x[2])

        evicted_size = 0
        for key, item, _ in items_to_evict:
            if self.current_size_bytes - evicted_size <= self.max_size_bytes * 0.8:
                break

            evicted_size += item.size_bytes
            del self.cache[key]
            self.eviction_count += 1
            self.stats["total_evictions"] += 1

        self.current_size_bytes -= evicted_size
        logger.debug(f"Evicted {evicted_size / (1024*1024):.2f} MB from cache")

    def _estimate_size(self, value: Any) -> int:
        """Değerin boyutunu tahmin eder"""
        try:
            # Pickle ile boyut tahmini
            data = pickle.dumps(value)
            return len(data)
        except Exception:
            # Fallback: basit boyut tahmini
            if hasattr(value, "__sizeof__"):
                return value.__sizeof__()
            else:
                return 1024  # Default 1KB

    def get(self, key: str, default: Any = None) -> Any:
        """
        Önbellekten değer alır

        Parameters
        ----------
        key : str
            Aranacak anahtar
        default : Any, default=None
            Bulunamazsa döndürülecek varsayılan değer

        Returns
        -------
        Any
            Önbellekteki değer veya varsayılan değer
        """
        self.stats["total_requests"] += 1

        if key in self.cache:
            # Hit: öğeyi güncelle ve başa taşı
            item = self.cache[key]
            item.update_access()
            self.cache.move_to_end(key, last=False)
            self.hit_count += 1

            # İstatistikleri güncelle
            self._update_stats()

            return item.value
        else:
            # Miss
            self.miss_count += 1
            return default

    def set(self, key: str, value: Any, size_bytes: Optional[int] = None) -> None:
        """
        Önbelleğe değer kaydeder

        Parameters
        ----------
        key : str
            Anahtar
        value : Any
            Kaydedilecek değer
        size_bytes : Optional[int], default=None
            Değerin boyutu (None ise otomatik hesaplanır)
        """
        if size_bytes is None:
            size_bytes = self._estimate_size(value)

        # Mevcut öğeyi güncelle
        if key in self.cache:
            old_item = self.cache[key]
            self.current_size_bytes -= old_item.size_bytes
            del self.cache[key]

        # Yeni öğeyi ekle
        self._add_item(key, value, size_bytes)

        # Kalıcı önbelleğe kaydet
        if self.persistence_enabled:
            self._save_persistent_cache()

    def delete(self, key: str) -> bool:
        """
        Önbellekten öğe siler

        Parameters
        ----------
        key : str
            Silinecek anahtar

        Returns
        -------
        bool
            Silme başarılı mı
        """
        if key in self.cache:
            item = self.cache[key]
            self.current_size_bytes -= item.size_bytes
            del self.cache[key]

            # Kalıcı önbellekten de sil
            if self.persistence_enabled and self.cache_dir:
                cache_file = self.cache_dir / f"{key}.cache"
                cache_file.unlink(missing_ok=True)

            return True
        return False

    def clear(self) -> None:
        """Tüm önbelleği temizler"""
        self.cache.clear()
        self.current_size_bytes = 0
        self.hit_count = 0
        self.miss_count = 0
        self.eviction_count = 0

        # Kalıcı önbelleği de temizle
        if self.persistence_enabled and self.cache_dir:
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
            metadata_file = self.cache_dir / "cache_metadata.pkl"
            metadata_file.unlink(missing_ok=True)

        logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Önbellek istatistiklerini döndürür"""
        hit_rate = self.hit_count / max(1, self.hit_count + self.miss_count)

        return {
            "total_requests": self.stats["total_requests"],
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate,
            "total_sets": self.stats["total_sets"],
            "total_evictions": self.stats["total_evictions"],
            "current_size_mb": self.current_size_bytes / (1024 * 1024),
            "max_size_mb": self.max_size_bytes / (1024 * 1024),
            "item_count": len(self.cache),
            "compression_savings_mb": self.stats["compression_savings"] / (1024 * 1024),
        }

    def _update_stats(self):
        """İstatistikleri günceller"""
        # Memory usage tracking
        if len(self.stats["memory_usage"]) >= 100:
            self.stats["memory_usage"] = self.stats["memory_usage"][-50:]

        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            self.stats["memory_usage"].append(
                {
                    "timestamp": time.time(),
                    "rss_mb": memory_info.rss / (1024 * 1024),
                    "vms_mb": memory_info.vms / (1024 * 1024),
                }
            )
        except Exception:
            pass

    def optimize(self) -> Dict[str, Any]:
        """Önbelleği optimize eder"""
        optimization_results = {
            "items_removed": 0,
            "size_freed_mb": 0,
            "compression_applied": 0,
        }

        # Eski öğeleri temizle (1 saatten eski)
        current_time = time.time()
        items_to_remove = []

        for key, item in self.cache.items():
            if current_time - item.last_access > 3600:  # 1 saat
                items_to_remove.append(key)

        for key in items_to_remove:
            size_freed = self.cache[key].size_bytes
            self.delete(key)
            optimization_results["items_removed"] += 1
            optimization_results["size_freed_mb"] += size_freed / (1024 * 1024)

        # Sıkıştırma uygula
        for key, item in self.cache.items():
            if item.size_bytes > self.compression_threshold_bytes and not hasattr(
                item.value, "_compressed"
            ):
                try:
                    compressed_data = gzip.compress(pickle.dumps(item.value))
                    if len(compressed_data) < item.size_bytes:
                        # Sıkıştırılmış veriyi kaydet
                        item.value = compressed_data
                        old_size = item.size_bytes
                        item.size_bytes = len(compressed_data)
                        self.current_size_bytes -= old_size - item.size_bytes
                        item.value._compressed = True
                        optimization_results["compression_applied"] += 1
                        self.stats["compression_savings"] += old_size - item.size_bytes
                except Exception:
                    pass

        logger.info(f"Cache optimization completed: {optimization_results}")
        return optimization_results

    def get_memory_usage_trend(self) -> List[Dict[str, float]]:
        """Memory kullanım trendini döndürür"""
        return self.stats["memory_usage"]


# Global cache instance
global_cache = SmartCache()


def get_cache() -> SmartCache:
    """Global önbellek instance'ını döndürür"""
    return global_cache


def cache_function(max_age_seconds: Optional[float] = None, key_prefix: str = ""):
    """
    Fonksiyon sonuçlarını önbellekleme decorator'ı

    Parameters
    ----------
    max_age_seconds : Optional[float]
        Maksimum önbellek yaşı (saniye)
    key_prefix : str
        Anahtar ön eki
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Cache key oluştur
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"

            # Önbellekten kontrol et
            cached_result = global_cache.get(cache_key)
            if cached_result is not None:
                # Yaş kontrolü
                if max_age_seconds is None:
                    return cached_result

                # Cache item'ı bul ve yaşını kontrol et
                if cache_key in global_cache.cache:
                    item = global_cache.cache[cache_key]
                    if time.time() - item.created_at < max_age_seconds:
                        return cached_result
                    else:
                        # Süresi dolmuş, sil
                        global_cache.delete(cache_key)

            # Fonksiyonu çalıştır ve sonucu önbellekle
            result = func(*args, **kwargs)
            global_cache.set(cache_key, result)

            return result

        return wrapper

    return decorator
