"""
QuickInsights - Creative and Innovative Big Data Analysis Library

A Python library that goes beyond standard data analysis libraries like NumPy and Pandas,
providing creative insights, performance optimizations, and innovative features for both
large and small datasets.

Author: Eren Ata
Version: 0.4.0
"""

import warnings
from typing import Any, Dict, Optional

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# Version information
__version__ = "0.4.0"
__author__ = "Eren Ata"
__description__ = "Creative and Innovative Big Data Analysis Library"

# Core imports that are always available
from ._imports import check_dependencies
from .error_handling import QuickInsightsError, DataValidationError

# Lazy loading registry
_LAZY_IMPORTS: Dict[str, str] = {
    # Core analysis functions
    "analyze": "core",
    "analyze_numeric": "analysis.basic_analysis", 
    "analyze_categorical": "analysis.basic_analysis",
    "validate_dataframe": "analysis.basic_analysis",
    
    # Advanced analysis
    "analyze_correlations": "analysis.advanced_analysis",
    "analyze_outliers": "analysis.advanced_analysis",
    "analyze_distributions": "analysis.advanced_analysis",
    
    # AutoML functions
    "intelligent_model_selection": "automl.model_selection",
    
    # Visualization functions
    "create_radar_chart": "visualization.charts",
    "create_3d_scatter": "visualization.charts",
    "create_heatmap": "visualization.charts",
    "create_bubble_chart": "visualization.charts",
    
    # Utility functions
    "get_data_info": "utils",
    "detect_outliers": "utils",
    "create_output_directory": "utils",
    
    # Smart cleaning
    "smart_clean": "smart_cleaner",
    "analyze_data_quality": "smart_cleaner",
    
    # Performance optimization
    "PerformanceOptimizer": "performance_optimizer_v2",
    "create_performance_optimizer": "performance_optimizer_v2",
    
    # Dashboard
    "create_dashboard": "dashboard",
    "DashboardGenerator": "dashboard",
    
    # Plugin System
    "get_plugin_manager": "plugin_system",
    "register_plugin": "plugin_system",
    "unregister_plugin": "plugin_system",
    "execute_plugin": "plugin_system",
    "execute_plugins_by_type": "plugin_system",
    "discover_and_register_plugins": "plugin_system",
    
    # Advanced Configuration
    "get_advanced_config_manager": "advanced_config",
    "get_config_value": "advanced_config",
    "set_config_value": "advanced_config",
    "get_config_section": "advanced_config",
    "set_config_section": "advanced_config",
    
    # Async Operations
    "get_async_quickinsights": "async_core",
    "analyze_async": "async_core",
    "load_data_async": "async_core",
    "save_data_async": "async_core",
    
    # Profiling
    "CodeProfiler": "profiling",
    "profile_function": "profiling",
    "benchmark_function": "profiling",
    
    # Smart I/O
    "SmartDataLoader": "io",
    "load_data": "io",
    "analyze_from_file": "io",
    
    # Streaming Analysis
    "StreamingAnalyzer": "streaming",
    "StreamingAggregator": "streaming",
    "analyze_streaming": "streaming",
    
    # Caching
    "AnalysisCache": "caching",
    "get_cache": "caching",
    "cached_analysis": "caching",
    
    # Web API
    "create_app": "web_api",
    "run_server": "web_api",
    "create_flask_app": "web_api",
}

# Classes that need special handling
_CLASS_IMPORTS: Dict[str, str] = {
    "SmartCleaner": "smart_cleaner",
    "LazyAnalyzer": "core",
    "ErrorHandler": "error_handling",
    "ValidationUtils": "error_handling",
    "PluginManager": "plugin_system",
    "PluginInterface": "plugin_system",
    "AnalyzerPlugin": "plugin_system",
    "VisualizerPlugin": "plugin_system",
    "CleanerPlugin": "plugin_system",
    "AnalysisRequest": "web_api",
    "AnalysisResponse": "web_api",
    "ErrorResponse": "web_api",
    "MemoryInfo": "web_api",
    "PluginInfo": "plugin_system",
    "PluginType": "plugin_system",
    "PluginPriority": "plugin_system",
    "AdvancedConfigManager": "advanced_config",
    "ConfigTemplate": "advanced_config",
    "ConfigValidator": "advanced_config",
    "ConfigValidationRule": "advanced_config",
    "AsyncQuickInsights": "async_core",
    "AsyncTaskManager": "async_core",
    "AsyncDataLoader": "async_core",
    "AsyncDataSaver": "async_core",
    "AsyncAnalyzer": "async_core",
    "AsyncVisualizer": "async_core",
}

def __getattr__(name: str) -> Any:
    """
    Lazy import system for better performance and optional dependencies.
    
    This function is called when an attribute is accessed that doesn't exist
    in the module. It dynamically imports the requested function or class.
    
    Args:
        name: The name of the function or class to import
        
    Returns:
        The imported function or class
        
    Raises:
        AttributeError: If the requested name is not found
        ImportError: If the module cannot be imported
    """
    # Check if it's a lazy import
    if name in _LAZY_IMPORTS:
        module_path = _LAZY_IMPORTS[name]
        try:
            module = __import__(f"quickinsights.{module_path}", fromlist=[name])
            return getattr(module, name)
        except ImportError as e:
            raise ImportError(f"Could not import {name} from {module_path}: {e}")
    
    # Check if it's a class import
    if name in _CLASS_IMPORTS:
        module_path = _CLASS_IMPORTS[name]
        try:
            module = __import__(f"quickinsights.{module_path}", fromlist=[name])
            return getattr(module, name)
        except ImportError as e:
            raise ImportError(f"Could not import {name} from {module_path}: {e}")
    
    # Check for optimized modules (with fallback)
    if name.endswith("Optimized"):
        try:
            optimized_name = name.replace("Optimized", "_optimized")
            module = __import__(f"quickinsights.{optimized_name}", fromlist=[name])
            return getattr(module, name)
        except ImportError:
            # Fallback to regular module
            base_name = name.replace("Optimized", "")
            if base_name in _LAZY_IMPORTS:
                return __getattr__(base_name)
            else:
                raise AttributeError(f"Optimized module {name} not available and no fallback found")
    
    # Not found
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

def get_available_functions() -> Dict[str, str]:
    """
    Get a dictionary of all available functions and their module paths.
    
    Returns:
        Dictionary mapping function names to their module paths
    """
    return _LAZY_IMPORTS.copy()

def get_available_classes() -> Dict[str, str]:
    """
    Get a dictionary of all available classes and their module paths.
    
    Returns:
        Dictionary mapping class names to their module paths
    """
    return _CLASS_IMPORTS.copy()

def check_system_requirements() -> Dict[str, Any]:
    """
    Check system requirements and dependencies.
    
    Returns:
        Dictionary with system information and dependency status
    """
    return check_dependencies()

# Always available utility functions
def get_version() -> str:
    """Get the current version of QuickInsights."""
    return __version__

def get_author() -> str:
    """Get the author information."""
    return __author__

def get_description() -> str:
    """Get the library description."""
    return __description__

# Export commonly used items
__all__ = [
    # Version info
    "__version__",
    "__author__", 
    "__description__",
    
    # Core functions (lazy loaded)
    "analyze",
    "analyze_numeric",
    "analyze_categorical", 
    "validate_dataframe",
    
    # Advanced functions (lazy loaded)
    "analyze_correlations",
    "analyze_outliers",
    "analyze_distributions",
    
    # AutoML (lazy loaded)
    "intelligent_model_selection",
    
    # Visualization (lazy loaded)
    "create_radar_chart",
    "create_3d_scatter", 
    "create_heatmap",
    "create_bubble_chart",
    
    # Utilities (lazy loaded)
    "get_data_info",
    "detect_outliers",
    "create_output_directory",
    
    # Smart cleaning (lazy loaded)
    "smart_clean",
    "analyze_data_quality",
    
    # Classes (lazy loaded)
    "SmartCleaner",
    "LazyAnalyzer",
    "ErrorHandler",
    "ValidationUtils",
    "PerformanceOptimizer",
    "DashboardGenerator",
    
    # Utility functions (always available)
    "get_version",
    "get_author",
    "get_description",
    "get_available_functions",
    "get_available_classes",
    "check_system_requirements",
    "check_dependencies",
    
    # Error classes (always available)
    "QuickInsightsError",
    "DataValidationError",
    "MemoryError",
    "PluginError",
]