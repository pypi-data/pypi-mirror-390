"""
QuickInsights - Configuration Management System

Bu modül, kütüphanenin tüm konfigürasyon ayarlarını merkezi olarak yönetir
ve performans optimizasyonları sağlar.
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union, List
from dataclasses import dataclass, asdict
import logging

from .error_handling import ConfigurationError

logger = logging.getLogger(__name__)


@dataclass
class PerformanceConfig:
    """Performans konfigürasyonu"""

    max_memory_gb: float = 8.0
    parallel_workers: int = 4
    chunk_size: int = 10000
    cache_enabled: bool = True
    cache_size_mb: int = 1000
    gpu_enabled: bool = False
    gpu_memory_fraction: float = 0.8


@dataclass
class VisualizationConfig:
    """Görselleştirme konfigürasyonu"""

    default_backend: str = "plotly"  # 'matplotlib', 'seaborn', 'plotly'
    figure_size: tuple = (12, 8)
    dpi: int = 100
    style: str = "default"
    color_palette: str = "viridis"
    save_format: str = "png"
    interactive_mode: bool = True


@dataclass
class MLConfig:
    """Machine Learning konfigürasyonu"""

    random_state: int = 42
    test_size: float = 0.2
    cv_folds: int = 5
    n_jobs: int = -1
    verbose: bool = False
    early_stopping: bool = True
    model_persistence: bool = True


@dataclass
class DataConfig:
    """Veri işleme konfigürasyonu"""

    default_encoding: str = "utf-8"
    missing_value_strategies: List[str] = None
    outlier_detection_method: str = "iqr"  # 'iqr', 'zscore', 'isolation_forest'
    data_quality_threshold: float = 0.8
    auto_clean: bool = True
    preserve_original: bool = True


@dataclass
class LoggingConfig:
    """Loglama konfigürasyonu"""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_logging: bool = False
    log_file: str = "quickinsights.log"
    max_file_size_mb: int = 10
    backup_count: int = 5


class QuickInsightsConfig:
    """Merkezi konfigürasyon yöneticisi"""

    def __init__(self, config_file: Optional[Union[str, Path]] = None):
        """
        Konfigürasyon yöneticisi başlatıcısı

        Parameters
        ----------
        config_file : Optional[Union[str, Path]]
            Konfigürasyon dosyası yolu
        """
        self.config_file = Path(config_file) if config_file else None

        # Default konfigürasyonlar
        self.performance = PerformanceConfig()
        self.visualization = VisualizationConfig()
        self.ml = MLConfig()
        self.data = DataConfig()
        self.logging = LoggingConfig()

        # Environment variables'dan yükle
        self._load_from_environment()

        # Konfigürasyon dosyasından yükle
        if self.config_file and self.config_file.exists():
            self._load_from_file()

        # Sistem kaynaklarını kontrol et
        self._validate_system_resources()

        # Loglama ayarlarını uygula
        self._setup_logging()

    def _load_from_environment(self):
        """Environment variables'dan konfigürasyon yükler"""
        env_mappings = {
            "QI_MAX_MEMORY_GB": ("performance", "max_memory_gb", float),
            "QI_PARALLEL_WORKERS": ("performance", "parallel_workers", int),
            "QI_GPU_ENABLED": (
                "performance",
                "gpu_enabled",
                lambda x: x.lower() == "true",
            ),
            "QI_CACHE_ENABLED": (
                "performance",
                "cache_enabled",
                lambda x: x.lower() == "true",
            ),
            "QI_DEFAULT_BACKEND": ("visualization", "default_backend", str),
            "QI_RANDOM_STATE": ("ml", "random_state", int),
            "QI_VERBOSE": ("ml", "verbose", lambda x: x.lower() == "true"),
            "QI_LOG_LEVEL": ("logging", "level", str),
        }

        for env_var, (config_section, attr_name, converter) in env_mappings.items():
            if env_var in os.environ:
                try:
                    value = converter(os.environ[env_var])
                    setattr(getattr(self, config_section), attr_name, value)
                    logger.info(f"Environment variable loaded: {env_var} = {value}")
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid environment variable {env_var}: {e}")

    def _load_from_file(self):
        """Konfigürasyon dosyasından ayarları yükler"""
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            # Her bölümü güncelle
            for section_name, section_data in config_data.items():
                if hasattr(self, section_name):
                    section = getattr(self, section)
                    for key, value in section_data.items():
                        if hasattr(section, key):
                            setattr(section, key, value)

            logger.info(f"Configuration loaded from {self.config_file}")

        except Exception as e:
            logger.error(f"Failed to load configuration file: {e}")
            raise ConfigurationError(f"Konfigürasyon dosyası yüklenemedi: {e}")

    def _validate_system_resources(self):
        """Sistem kaynaklarını kontrol eder ve konfigürasyonu optimize eder"""
        import psutil

        # Memory kontrolü
        available_memory_gb = psutil.virtual_memory().total / (1024**3)
        if self.performance.max_memory_gb > available_memory_gb * 0.8:
            self.performance.max_memory_gb = available_memory_gb * 0.8
            logger.info(
                f"Memory limit adjusted to {self.performance.max_memory_gb:.1f} GB"
            )

        # CPU core sayısı kontrolü
        cpu_count = psutil.cpu_count()
        if self.performance.parallel_workers > cpu_count:
            self.performance.parallel_workers = cpu_count
            logger.info(f"Parallel workers adjusted to {cpu_count}")

        # GPU kontrolü
        if self.performance.gpu_enabled:
            try:
                import torch

                if torch.cuda.is_available():
                    gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / (
                        1024**3
                    )
                    if (
                        self.performance.gpu_memory_fraction * gpu_memory_gb
                        > available_memory_gb * 0.5
                    ):
                        self.performance.gpu_memory_fraction = (
                            available_memory_gb * 0.5
                        ) / gpu_memory_gb
                        logger.info(
                            f"GPU memory fraction adjusted to {self.performance.gpu_memory_fraction:.2f}"
                        )
                else:
                    self.performance.gpu_enabled = False
                    logger.warning(
                        "GPU requested but not available, disabling GPU support"
                    )
            except ImportError:
                self.performance.gpu_enabled = False
                logger.warning("PyTorch not available, disabling GPU support")

    def _setup_logging(self):
        """Loglama ayarlarını yapılandırır"""
        # Root logger'ı yapılandır
        logging.basicConfig(
            level=getattr(logging, self.logging.level.upper()),
            format=self.logging.format,
            force=True,
        )

        # File logging
        if self.logging.file_logging:
            from logging.handlers import RotatingFileHandler

            handler = RotatingFileHandler(
                self.logging.log_file,
                maxBytes=self.logging.max_file_size_mb * 1024 * 1024,
                backupCount=self.logging.backup_count,
            )
            handler.setFormatter(logging.Formatter(self.logging.format))

            # QuickInsights logger'ına ekle
            qi_logger = logging.getLogger("quickinsights")
            qi_logger.addHandler(handler)
            qi_logger.setLevel(getattr(logging, self.logging.level.upper()))

    def save_config(self, file_path: Optional[Union[str, Path]] = None) -> None:
        """
        Mevcut konfigürasyonu dosyaya kaydeder

        Parameters
        ----------
        file_path : Optional[Union[str, Path]]
            Kaydedilecek dosya yolu
        """
        if file_path is None:
            file_path = (
                self.config_file or Path.home() / ".quickinsights" / "config.json"
            )

        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        config_data = {
            "performance": asdict(self.performance),
            "visualization": asdict(self.visualization),
            "ml": asdict(self.ml),
            "data": asdict(self.data),
            "logging": asdict(self.logging),
        }

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Configuration saved to {file_path}")

        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise ConfigurationError(f"Konfigürasyon kaydedilemedi: {e}")

    def get_config_summary(self) -> Dict[str, Any]:
        """Konfigürasyon özeti döndürür"""
        return {
            "performance": asdict(self.performance),
            "visualization": asdict(self.visualization),
            "ml": asdict(self.ml),
            "data": asdict(self.data),
            "logging": asdict(self.logging),
            "config_file": str(self.config_file) if self.config_file else None,
        }

    def update_config(self, section: str, **updates) -> None:
        """
        Belirli bir bölümün konfigürasyonunu günceller

        Parameters
        ----------
        section : str
            Güncellenecek bölüm adı
        **updates : dict
            Güncellenecek ayarlar
        """
        if not hasattr(self, section):
            raise ConfigurationError(f"Bilinmeyen konfigürasyon bölümü: {section}")

        section_obj = getattr(self, section)

        for key, value in updates.items():
            if hasattr(section_obj, key):
                setattr(section_obj, key, value)
                logger.info(f"Configuration updated: {section}.{key} = {value}")
            else:
                logger.warning(f"Unknown configuration key: {section}.{key}")

    def reset_to_defaults(self, section: Optional[str] = None) -> None:
        """
        Konfigürasyonu varsayılan değerlere sıfırlar

        Parameters
        ----------
        section : Optional[str]
            Sıfırlanacak bölüm (None ise tümü)
        """
        if section is None:
            # Tüm bölümleri sıfırla
            self.performance = PerformanceConfig()
            self.visualization = VisualizationConfig()
            self.ml = MLConfig()
            self.data = DataConfig()
            self.logging = LoggingConfig()
            logger.info("All configurations reset to defaults")
        elif hasattr(self, section):
            # Belirli bölümü sıfırla
            section_classes = {
                "performance": PerformanceConfig,
                "visualization": VisualizationConfig,
                "ml": MLConfig,
                "data": DataConfig,
                "logging": LoggingConfig,
            }

            if section in section_classes:
                setattr(self, section, section_classes[section]())
                logger.info(f"Configuration section '{section}' reset to defaults")
            else:
                raise ConfigurationError(f"Bilinmeyen konfigürasyon bölümü: {section}")
        else:
            raise ConfigurationError(f"Bilinmeyen konfigürasyon bölümü: {section}")

    def validate_config(self) -> List[str]:
        """
        Konfigürasyon geçerliliğini kontrol eder

        Returns
        -------
        List[str]
            Hata mesajları listesi
        """
        errors = []

        # Performance validation
        if self.performance.max_memory_gb <= 0:
            errors.append("max_memory_gb must be positive")

        if self.performance.parallel_workers <= 0:
            errors.append("parallel_workers must be positive")

        if self.performance.chunk_size <= 0:
            errors.append("chunk_size must be positive")

        # ML validation
        if not (0 < self.ml.test_size < 1):
            errors.append("test_size must be between 0 and 1")

        if self.ml.cv_folds < 2:
            errors.append("cv_folds must be at least 2")

        # Data validation
        if not (0 <= self.data.data_quality_threshold <= 1):
            errors.append("data_quality_threshold must be between 0 and 1")

        return errors


# Global configuration instance
global_config = QuickInsightsConfig()


def get_config() -> QuickInsightsConfig:
    """Global konfigürasyon instance'ını döndürür"""
    return global_config


def update_global_config(section: str, **updates) -> None:
    """Global konfigürasyonu günceller"""
    global_config.update_config(section, **updates)


def reset_global_config(section: Optional[str] = None) -> None:
    """Global konfigürasyonu sıfırlar"""
    global_config.reset_to_defaults(section)
