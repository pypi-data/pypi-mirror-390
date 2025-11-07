"""
QuickInsights - Comprehensive Error Handling and Validation Framework

Bu modül, kütüphanenin tüm hata durumlarını yönetir ve kullanıcı dostu
hata mesajları sağlar.
"""

import traceback
import sys
from typing import Any, Dict, Optional, Union, List
from pathlib import Path
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuickInsightsError(Exception):
    """QuickInsights kütüphanesi için temel exception sınıfı"""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = self._get_timestamp()

        super().__init__(self.message)

    def _get_timestamp(self) -> str:
        """Hata zamanını alır"""
        from datetime import datetime

        return datetime.now().isoformat()

    def get_user_friendly_message(self) -> str:
        """Kullanıcı dostu hata mesajı döndürür"""
        return f"❌ {self.message}"

    def get_technical_details(self) -> Dict[str, Any]:
        """Teknik detayları döndürür"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "timestamp": self.timestamp,
            "details": self.details,
        }


class DataValidationError(QuickInsightsError):
    """Veri doğrulama hataları için"""

    def __init__(
        self,
        message: str,
        column: Optional[str] = None,
        value: Optional[str] = None,
        expected_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = {
            "column": column,
            "value": value,
            "expected_type": expected_type,
        }
        if details:
            error_details.update(details)
        super().__init__(message, "DATA_VALIDATION_ERROR", error_details)

    def get_user_friendly_message(self) -> str:
        if self.details.get("column"):
            return f"❌ Veri doğrulama hatası: {self.details['column']} sütununda sorun var - {self.message}"
        return f"❌ Veri doğrulama hatası: {self.message}"


class PerformanceError(QuickInsightsError):
    """Performans ile ilgili hatalar için"""

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        resource_usage: Optional[Dict[str, Any]] = None,
    ):
        details = {"operation": operation, "resource_usage": resource_usage}
        super().__init__(message, "PERFORMANCE_ERROR", details)

    def get_user_friendly_message(self) -> str:
        return f"⚡ Performans hatası: {self.message}"


class DependencyError(QuickInsightsError):
    """Bağımlılık hataları için"""

    def __init__(
        self,
        message: str,
        missing_package: Optional[str] = None,
        required_version: Optional[str] = None,
    ):
        details = {
            "missing_package": missing_package,
            "required_version": required_version,
        }
        super().__init__(message, "DEPENDENCY_ERROR", details)

    def get_user_friendly_message(self) -> str:
        if self.details.get("missing_package"):
            return f"📦 Eksik paket: {self.details['missing_package']} - {self.message}"
        return f"📦 Bağımlılık hatası: {self.message}"


class ConfigurationError(QuickInsightsError):
    """Konfigürasyon hataları için"""

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        current_value: Optional[Any] = None,
    ):
        details = {
            "config_key": config_key,
            "current_value": str(current_value) if current_value is not None else None,
        }
        super().__init__(message, "CONFIGURATION_ERROR", details)

    def get_user_friendly_message(self) -> str:
        return f"⚙️ Konfigürasyon hatası: {self.message}"


class MemoryError(QuickInsightsError):
    """Memory ile ilgili hatalar için"""

    def __init__(
        self,
        message: str,
        memory_usage_mb: Optional[float] = None,
        memory_limit_mb: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = {
            "memory_usage_mb": memory_usage_mb,
            "memory_limit_mb": memory_limit_mb,
        }
        if details:
            error_details.update(details)
        super().__init__(message, "MEMORY_ERROR", error_details)

    def get_user_friendly_message(self) -> str:
        return f"💾 Bellek hatası: {self.message}"


class PluginError(QuickInsightsError):
    """Plugin ile ilgili hatalar için"""

    def __init__(
        self,
        message: str,
        plugin_name: Optional[str] = None,
        plugin_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = {
            "plugin_name": plugin_name,
            "plugin_type": plugin_type,
        }
        if details:
            error_details.update(details)
        super().__init__(message, "PLUGIN_ERROR", error_details)

    def get_user_friendly_message(self) -> str:
        return f"🔌 Plugin hatası: {self.message}"


class ValidationUtils:
    """Veri doğrulama yardımcı fonksiyonları"""

    @staticmethod
    def validate_dataframe(df: Any, allow_empty: bool = False) -> None:
        """
        DataFrame'in geçerli olup olmadığını kontrol eder

        Parameters
        ----------
        df : Any
            Kontrol edilecek veri
        allow_empty : bool, default=False
            Boş DataFrame'lere izin verilsin mi

        Raises
        ------
        DataValidationError
            DataFrame geçersizse
        """
        import pandas as pd

        if not isinstance(df, pd.DataFrame):
            raise DataValidationError(
                "Veri bir pandas DataFrame olmalıdır",
                expected_type="pandas.DataFrame",
                value=type(df).__name__,
            )

        if not allow_empty and df.empty:
            raise DataValidationError(
                "DataFrame boş olamaz", details={"shape": df.shape}
            )

    @staticmethod
    def validate_column_exists(df: Any, column_name: str) -> None:
        """
        Belirtilen sütunun DataFrame'de var olup olmadığını kontrol eder

        Parameters
        ----------
        df : Any
            Kontrol edilecek DataFrame
        column_name : str
            Aranacak sütun adı

        Raises
        ------
        DataValidationError
            Sütun bulunamazsa
        """
        ValidationUtils.validate_dataframe(df)

        if column_name not in df.columns:
            available_columns = list(df.columns)
            raise DataValidationError(
                f"'{column_name}' sütunu bulunamadı",
                column=column_name,
                details={"available_columns": available_columns},
            )

    @staticmethod
    def validate_numeric_column(df: Any, column_name: str) -> None:
        """
        Belirtilen sütunun sayısal olup olmadığını kontrol eder

        Parameters
        ----------
        df : Any
            Kontrol edilecek DataFrame
        column_name : str
            Kontrol edilecek sütun adı

        Raises
        ------
        DataValidationError
            Sütun sayısal değilse
        """
        ValidationUtils.validate_column_exists(df, column_name)

        import numpy as np

        if not np.issubdtype(df[column_name].dtype, np.number):
            raise DataValidationError(
                f"'{column_name}' sütunu sayısal olmalıdır",
                column=column_name,
                expected_type="numeric",
                value=str(df[column_name].dtype),
            )

    @staticmethod
    def validate_file_path(file_path: Union[str, Path]) -> None:
        """
        Dosya yolunun geçerli olup olmadığını kontrol eder

        Parameters
        ----------
        file_path : Union[str, Path]
            Kontrol edilecek dosya yolu

        Raises
        ------
        DataValidationError
            Dosya yolu geçersizse
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise DataValidationError(
                f"Dosya bulunamadı: {file_path}", value=str(file_path)
            )

        if not file_path.is_file():
            raise DataValidationError(
                f"'{file_path}' bir dosya değil", value=str(file_path)
            )


class ErrorHandler:
    """Merkezi hata yönetimi sınıfı"""

    def __init__(self, log_errors: bool = True, show_traceback: bool = False):
        self.log_errors = log_errors
        self.show_traceback = show_traceback
        self.error_count = 0
        self.error_history = []

    def handle_error(
        self, error: Exception, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Hatayı yakalar ve uygun şekilde işler

        Parameters
        ----------
        error : Exception
            Yakalanan hata
        context : Optional[Dict[str, Any]]
            Hata bağlamı

        Returns
        -------
        str
            Kullanıcı dostu hata mesajı
        """
        self.error_count += 1

        # Hata bilgilerini kaydet
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "timestamp": self._get_timestamp(),
        }

        if self.show_traceback:
            error_info["traceback"] = traceback.format_exc()

        self.error_history.append(error_info)

        # Hata mesajını oluştur
        if isinstance(error, QuickInsightsError):
            user_message = error.get_user_friendly_message()
        else:
            user_message = f"❌ Beklenmeyen hata: {str(error)}"

        # Loglama
        if self.log_errors:
            logger.error(f"Error #{self.error_count}: {error_info}")

        return user_message

    def get_error_summary(self) -> Dict[str, Any]:
        """Hata özeti döndürür"""
        return {
            "total_errors": self.error_count,
            "error_types": self._count_error_types(),
            "recent_errors": self.error_history[-5:] if self.error_history else [],
        }

    def _count_error_types(self) -> Dict[str, int]:
        """Hata türlerini sayar"""
        error_types = {}
        for error_info in self.error_history:
            error_type = error_info["error_type"]
            error_types[error_type] = error_types.get(error_type, 0) + 1
        return error_types

    def _get_timestamp(self) -> str:
        """Hata zamanını alır"""
        from datetime import datetime
        return datetime.now().isoformat()

    def clear_history(self) -> None:
        """Hata geçmişini temizler"""
        self.error_history = []
        self.error_count = 0
        logger.info("Error history cleared")


# Global error handler instance
_global_error_handler = ErrorHandler()


def handle_operation(operation: callable, *args, **kwargs) -> Any:
    """
    Decorator function to handle operations with standardized error handling.
    
    Parameters
    ----------
    operation : callable
        The operation to execute
    *args
        Positional arguments for the operation
    **kwargs
        Keyword arguments for the operation
        
    Returns
    -------
    Any
        The result of the operation
        
    Raises
    ------
    QuickInsightsError
        If the operation fails
    """
    try:
        return operation(*args, **kwargs)
    except QuickInsightsError:
        # Re-raise QuickInsights errors as-is
        raise
    except Exception as e:
        # Convert other exceptions to QuickInsightsError
        error_msg = f"Operation '{operation.__name__}' failed: {str(e)}"
        context = {
            "operation": operation.__name__,
            "args": str(args)[:100],  # Limit length
            "kwargs": str(kwargs)[:100]
        }
        
        user_message = _global_error_handler.handle_error(e, context)
        raise QuickInsightsError(error_msg, "OPERATION_ERROR", context) from e


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    return _global_error_handler


def reset_error_handler() -> None:
    """Reset the global error handler."""
    global _global_error_handler
    _global_error_handler = ErrorHandler()


def safe_execute(func, *args, error_context: Optional[Dict[str, Any]] = None, **kwargs):
    """
    Fonksiyonu güvenli şekilde çalıştırır ve hataları yakalar

    Parameters
    ----------
    func : callable
        Çalıştırılacak fonksiyon
    *args : tuple
        Fonksiyon argümanları
    error_context : Optional[Dict[str, Any]]
        Hata bağlamı
    **kwargs : dict
        Fonksiyon keyword argümanları

    Returns
    -------
    tuple
        (success: bool, result: Any, error_message: Optional[str])
    """
    try:
        result = func(*args, **kwargs)
        return True, result, None
    except Exception as e:
        error_message = _global_error_handler.handle_error(e, error_context)
        return False, None, error_message


def validate_inputs(**validations):
    """
    Input validation decorator

    Parameters
    ----------
    **validations : dict
        Validation kuralları

    Example
    -------
    @validate_inputs(
        df=ValidationUtils.validate_dataframe,
        column=ValidationUtils.validate_column_exists
    )
    def my_function(df, column):
        pass
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Validation logic here
            return func(*args, **kwargs)

        return wrapper

    return decorator
