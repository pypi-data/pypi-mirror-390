"""
QuickInsights - Advanced Memory Management System

Bu modül, büyük veri setleri için gelişmiş bellek yönetimi sağlar.
DataFrame optimizasyonu, chunk processing ve memory monitoring özellikleri içerir.
"""

import psutil
import gc
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Union, Tuple, Callable
import logging
import warnings
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading

from .error_handling import PerformanceError
from .config import get_config
from .smart_cache import get_cache

logger = logging.getLogger(__name__)


class MemoryManager:
    """Gelişmiş bellek yönetimi sistemi"""

    def __init__(
        self, max_memory_gb: Optional[float] = None, enable_monitoring: bool = True
    ):
        """
        MemoryManager başlatıcısı

        Parameters
        ----------
        max_memory_gb : Optional[float]
            Maksimum bellek kullanımı (GB)
        enable_monitoring : bool, default=True
            Bellek izleme aktif mi
        """
        # Konfigürasyondan yükle
        config = get_config()
        self.max_memory_bytes = (
            max_memory_gb or config.performance.max_memory_gb
        ) * 1024**3
        self.chunk_size = config.performance.chunk_size
        self.parallel_workers = config.performance.parallel_workers

        # Bellek izleme
        self.enable_monitoring = enable_monitoring
        self.memory_history = []
        self.monitoring_thread = None
        self.stop_monitoring = threading.Event()

        # Cache referansı
        self.cache = get_cache()

        # Bellek kullanım istatistikleri
        self.stats = {
            "total_optimizations": 0,
            "memory_saved_mb": 0,
            "chunk_operations": 0,
            "gc_collections": 0,
        }

        # Monitoring başlat
        if self.enable_monitoring:
            self._start_monitoring()

    def _start_monitoring(self):
        """Bellek izlemeyi başlatır"""

        def monitor_memory():
            while not self.stop_monitoring.is_set():
                try:
                    memory_info = self._get_memory_info()
                    self.memory_history.append(memory_info)

                    # History'yi sınırla
                    if len(self.memory_history) > 1000:
                        self.memory_history = self.memory_history[-500:]

                    # Bellek uyarısı kontrol et
                    if memory_info["usage_percent"] > 80:
                        logger.warning(
                            f"High memory usage: {memory_info['usage_percent']:.1f}%"
                        )
                        self._emergency_cleanup()

                    time.sleep(5)  # 5 saniyede bir kontrol

                except Exception as e:
                    logger.error(f"Memory monitoring error: {e}")
                    time.sleep(10)

        self.monitoring_thread = threading.Thread(target=monitor_memory, daemon=True)
        self.monitoring_thread.start()
        logger.info("Memory monitoring started")

    def _stop_monitoring(self):
        """Bellek izlemeyi durdurur"""
        if self.monitoring_thread:
            self.stop_monitoring.set()
            self.monitoring_thread.join(timeout=5)
            logger.info("Memory monitoring stopped")

    def _get_memory_info(self) -> Dict[str, Any]:
        """Mevcut bellek bilgilerini alır"""
        process = psutil.Process()
        memory_info = process.memory_info()
        virtual_memory = psutil.virtual_memory()

        return {
            "timestamp": time.time(),
            "rss_mb": memory_info.rss / 1024**2,
            "vms_mb": memory_info.vms / 1024**2,
            "available_gb": virtual_memory.available / 1024**3,
            "total_gb": virtual_memory.total / 1024**3,
            "usage_percent": virtual_memory.percent,
            "swap_percent": psutil.swap_memory().percent
            if hasattr(psutil, "swap_memory")
            else 0,
        }

    def _emergency_cleanup(self):
        """Acil bellek temizliği"""
        logger.warning("Emergency memory cleanup initiated")

        # Garbage collection
        collected = gc.collect()
        self.stats["gc_collections"] += 1
        logger.info(f"Emergency GC collected {collected} objects")

        # Cache temizliği
        if self.cache:
            cache_stats = self.cache.get_stats()
            if cache_stats["current_size_mb"] > 100:  # 100MB'dan büyükse
                self.cache.optimize()
                logger.info("Cache optimized during emergency cleanup")

    def optimize_dataframe(
        self, df: pd.DataFrame, aggressive: bool = False
    ) -> pd.DataFrame:
        """
        DataFrame bellek kullanımını optimize eder

        Parameters
        ----------
        df : pd.DataFrame
            Optimize edilecek DataFrame
        aggressive : bool, default=False
            Agresif optimizasyon modu

        Returns
        -------
        pd.DataFrame
            Optimize edilmiş DataFrame
        """
        if df.empty:
            return df

        original_memory = df.memory_usage(deep=True).sum()
        optimized_df = df.copy()

        # Numeric sütunları optimize et
        for col in optimized_df.select_dtypes(include=[np.number]).columns:
            col_type = optimized_df[col].dtype

            # Integer optimizasyonu
            if np.issubdtype(col_type, np.integer):
                col_min = optimized_df[col].min()
                col_max = optimized_df[col].min()

                if (
                    col_min >= np.iinfo(np.int8).min
                    and col_max <= np.iinfo(np.int8).max
                ):
                    optimized_df[col] = optimized_df[col].astype(np.int8)
                elif (
                    col_min >= np.iinfo(np.int16).min
                    and col_max <= np.iinfo(np.int16).max
                ):
                    optimized_df[col] = optimized_df[col].astype(np.int16)
                elif (
                    col_min >= np.iinfo(np.int32).min
                    and col_max <= np.iinfo(np.int32).max
                ):
                    optimized_df[col] = optimized_df[col].astype(np.int32)

            # Float optimizasyonu
            elif np.issubdtype(col_type, np.floating):
                if aggressive:
                    optimized_df[col] = optimized_df[col].astype(np.float32)
                else:
                    # Precision kaybı olmadan optimize et
                    if optimized_df[col].dtype == np.float64:
                        # 32-bit'e dönüştürülebilir mi kontrol et
                        try:
                            test_col = optimized_df[col].astype(np.float32)
                            if np.allclose(optimized_df[col], test_col, rtol=1e-5):
                                optimized_df[col] = test_col
                        except:
                            pass

        # Categorical sütunları optimize et
        for col in optimized_df.select_dtypes(include=["object"]).columns:
            if (
                optimized_df[col].nunique() / len(optimized_df) < 0.5
            ):  # 50%'den az unique değer
                optimized_df[col] = optimized_df[col].astype("category")

        # Datetime sütunları optimize et
        for col in optimized_df.select_dtypes(include=["datetime64"]).columns:
            if aggressive:
                optimized_df[col] = pd.to_datetime(optimized_df[col], format="%Y-%m-%d")

        optimized_memory = optimized_df.memory_usage(deep=True).sum()
        memory_saved = original_memory - optimized_memory

        self.stats["total_optimizations"] += 1
        self.stats["memory_saved_mb"] += memory_saved / 1024**2

        logger.info(f"DataFrame optimized: {memory_saved / 1024**2:.2f} MB saved")

        return optimized_df

    def chunk_processing(
        self,
        df: pd.DataFrame,
        operation: Callable,
        chunk_size: Optional[int] = None,
        parallel: bool = True,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Büyük DataFrame'leri chunk'lar halinde işler

        Parameters
        ----------
        df : pd.DataFrame
            İşlenecek DataFrame
        operation : Callable
            Her chunk'a uygulanacak işlem
        chunk_size : Optional[int]
            Chunk boyutu (None ise config'den alınır)
        parallel : bool, default=True
            Paralel işleme kullanılsın mı
        **kwargs : dict
            Operation fonksiyonuna geçirilecek ek parametreler

        Returns
        -------
        pd.DataFrame
            İşlenmiş DataFrame
        """
        if chunk_size is None:
            chunk_size = self.chunk_size

        if len(df) <= chunk_size:
            # Tek chunk olarak işle
            return operation(df, **kwargs)

        self.stats["chunk_operations"] += 1

        # Chunk'lara böl
        chunks = [df[i : i + chunk_size] for i in range(0, len(df), chunk_size)]

        if parallel and len(chunks) > 1:
            # Paralel işleme
            with ThreadPoolExecutor(max_workers=self.parallel_workers) as executor:
                futures = [
                    executor.submit(operation, chunk, **kwargs) for chunk in chunks
                ]
                results = [future.result() for future in futures]
        else:
            # Sıralı işleme
            results = [operation(chunk, **kwargs) for chunk in chunks]

        # Sonuçları birleştir
        if isinstance(results[0], pd.DataFrame):
            final_result = pd.concat(results, ignore_index=True)
        else:
            final_result = results

        logger.info(f"Chunk processing completed: {len(chunks)} chunks processed")
        return final_result

    def memory_efficient_apply(
        self, df: pd.DataFrame, func: Callable, axis: int = 0, **kwargs
    ) -> pd.Series:
        """
        Bellek dostu apply işlemi

        Parameters
        ----------
        df : pd.DataFrame
            İşlenecek DataFrame
        func : Callable
            Uygulanacak fonksiyon
        axis : int, default=0
            Uygulama ekseni (0: satırlar, 1: sütunlar)
        **kwargs : dict
            Fonksiyona geçirilecek ek parametreler

        Returns
        -------
        pd.Series
            Sonuç serisi
        """
        if axis == 0:  # Satır bazında
            return self.chunk_processing(
                df, lambda chunk: chunk.apply(func, axis=axis, **kwargs)
            )
        else:  # Sütun bazında
            return df.apply(func, axis=axis, **kwargs)

    def smart_groupby(
        self,
        df: pd.DataFrame,
        by: Union[str, List[str]],
        operation: str = "mean",
        **kwargs,
    ) -> pd.DataFrame:
        """
        Bellek dostu groupby işlemi

        Parameters
        ----------
        df : pd.DataFrame
            İşlenecek DataFrame
        by : Union[str, List[str]]
            Gruplama kriteri
        operation : str, default='mean'
            Uygulanacak işlem
        **kwargs : dict
            Ek parametreler

        Returns
        -------
        pd.DataFrame
            Gruplandırılmış sonuç
        """
        if len(df) <= self.chunk_size:
            # Küçük DataFrame için normal groupby
            return getattr(df.groupby(by), operation)(**kwargs)

        # Büyük DataFrame için chunk-based groupby
        def chunk_groupby(chunk):
            return getattr(chunk.groupby(by), operation)(**kwargs)

        result = self.chunk_processing(df, chunk_groupby)

        # Sonuçları birleştir ve tekrar grupla
        if isinstance(result, list):
            combined = pd.concat(result, ignore_index=True)
            return getattr(combined.groupby(by), operation)(**kwargs)

        return result

    def memory_profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        DataFrame bellek profilini çıkarır

        Parameters
        ----------
        df : pd.DataFrame
            Profillenecek DataFrame

        Returns
        -------
        Dict[str, Any]
            Bellek profili
        """
        memory_usage = df.memory_usage(deep=True)

        profile = {
            "total_memory_mb": memory_usage.sum() / 1024**2,
            "columns": {},
            "dtypes": {},
            "optimization_potential": {},
        }

        for col in df.columns:
            col_memory = memory_usage[col] / 1024**2
            col_type = str(df[col].dtype)

            profile["columns"][col] = {
                "memory_mb": col_memory,
                "dtype": col_type,
                "unique_count": df[col].nunique(),
                "null_count": df[col].isnull().sum(),
            }

            # Dtype bazında memory
            if col_type not in profile["dtypes"]:
                profile["dtypes"][col_type] = 0
            profile["dtypes"][col_type] += col_memory

        # Optimizasyon potansiyeli
        profile["optimization_potential"] = self._calculate_optimization_potential(df)

        return profile

    def _calculate_optimization_potential(self, df: pd.DataFrame) -> Dict[str, float]:
        """Optimizasyon potansiyelini hesaplar"""
        potential = {
            "integer_optimization_mb": 0,
            "float_optimization_mb": 0,
            "categorical_optimization_mb": 0,
            "total_potential_mb": 0,
        }

        for col in df.select_dtypes(include=[np.number]).columns:
            col_type = df[col].dtype
            col_memory = df[col].memory_usage(deep=True)

            if np.issubdtype(col_type, np.integer):
                # Integer optimizasyon potansiyeli
                if col_type == np.int64:
                    potential["integer_optimization_mb"] += col_memory * 0.5 / 1024**2

            elif np.issubdtype(col_type, np.floating):
                # Float optimizasyon potansiyeli
                if col_type == np.float64:
                    potential["float_optimization_mb"] += col_memory * 0.5 / 1024**2

        # Categorical optimizasyon potansiyeli
        for col in df.select_dtypes(include=["object"]).columns:
            if df[col].nunique() / len(df) < 0.5:
                col_memory = df[col].memory_usage(deep=True)
                potential["categorical_optimization_mb"] += col_memory * 0.3 / 1024**2

        potential["total_potential_mb"] = sum(
            [
                potential["integer_optimization_mb"],
                potential["float_optimization_mb"],
                potential["categorical_optimization_mb"],
            ]
        )

        return potential

    def get_memory_status(self) -> Dict[str, Any]:
        """Mevcut bellek durumunu döndürür"""
        current_memory = self._get_memory_info()

        return {
            "current_usage": current_memory,
            "limits": {
                "max_memory_gb": self.max_memory_bytes / 1024**3,
                "available_memory_gb": current_memory["available_gb"],
            },
            "stats": self.stats,
            "cache_stats": self.cache.get_stats() if self.cache else None,
            "optimization_recommendations": self._get_optimization_recommendations(),
        }

    def _get_optimization_recommendations(self) -> List[str]:
        """Bellek optimizasyon önerilerini döndürür"""
        recommendations = []
        current_memory = self._get_memory_info()

        if current_memory["usage_percent"] > 80:
            recommendations.append(
                "High memory usage detected. Consider optimizing DataFrames or using chunk processing."
            )

        if current_memory["swap_percent"] > 20:
            recommendations.append(
                "High swap usage detected. Consider reducing memory footprint."
            )

        if self.cache:
            cache_stats = self.cache.get_stats()
            if cache_stats["hit_rate"] < 0.3:
                recommendations.append(
                    "Low cache hit rate. Consider adjusting cache size or eviction strategy."
                )

        if len(self.memory_history) > 10:
            recent_usage = [h["usage_percent"] for h in self.memory_history[-10:]]
            if max(recent_usage) - min(recent_usage) > 30:
                recommendations.append(
                    "High memory usage variability. Consider implementing memory pooling."
                )

        return recommendations

    def cleanup(self):
        """Bellek temizliği yapar"""
        # Garbage collection
        collected = gc.collect()
        self.stats["gc_collections"] += 1

        # Cache temizliği
        if self.cache:
            self.cache.optimize()

        # Monitoring durdur
        self._stop_monitoring()

        logger.info(f"Memory cleanup completed. GC collected {collected} objects")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()


# Global memory manager instance
global_memory_manager = MemoryManager()


def get_memory_manager() -> MemoryManager:
    """Global memory manager instance'ını döndürür"""
    return global_memory_manager


def optimize_dataframe_memory(
    df: pd.DataFrame, aggressive: bool = False
) -> pd.DataFrame:
    """DataFrame bellek optimizasyonu için convenience fonksiyon"""
    return global_memory_manager.optimize_dataframe(df, aggressive)


def chunk_process_dataframe(
    df: pd.DataFrame, operation: Callable, **kwargs
) -> pd.DataFrame:
    """Chunk processing için convenience fonksiyon"""
    return global_memory_manager.chunk_processing(df, operation, **kwargs)


def get_memory_profile(df: pd.DataFrame) -> Dict[str, Any]:
    """DataFrame bellek profili için convenience fonksiyon"""
    return global_memory_manager.memory_profile(df)
