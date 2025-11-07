"""
Advanced Analyzer Plugin

Example plugin that demonstrates advanced data analysis capabilities.
"""

import pandas as pd
import numpy as np
from typing import Any, Dict, List
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from plugin_system import (
    AnalyzerPlugin, 
    PluginInfo, 
    PluginType, 
    PluginPriority
)


class AdvancedAnalyzerPlugin(AnalyzerPlugin):
    """Advanced data analyzer plugin with statistical analysis"""
    
    def get_info(self) -> PluginInfo:
        """Get plugin information"""
        return PluginInfo(
            name="AdvancedAnalyzer",
            version="1.0.0",
            description="Advanced statistical analysis plugin with correlation and distribution analysis",
            author="QuickInsights Team",
            plugin_type=PluginType.ANALYZER,
            priority=PluginPriority.HIGH,
            dependencies=["pandas", "numpy", "scipy"],
            entry_point="advanced_analyzer"
        )
    
    def initialize(self, context: Dict[str, Any]) -> None:
        """Initialize the plugin"""
        self.context = context
        self.initialized = True
    
    def analyze(self, data: Any, **kwargs) -> Dict[str, Any]:
        """Perform advanced analysis on data"""
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Data must be a pandas DataFrame")
        
        results = {
            "plugin_name": "AdvancedAnalyzer",
            "analysis_type": "advanced_statistical",
            "timestamp": pd.Timestamp.now().isoformat(),
            "data_shape": data.shape,
            "statistics": {}
        }
        
        # Basic statistics
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            results["statistics"]["descriptive"] = data[numeric_cols].describe().to_dict()
        
        # Correlation analysis
        if len(numeric_cols) > 1:
            correlation_matrix = data[numeric_cols].corr()
            results["statistics"]["correlations"] = correlation_matrix.to_dict()
            
            # Find strong correlations
            strong_correlations = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_value = correlation_matrix.iloc[i, j]
                    if abs(corr_value) > 0.7:  # Strong correlation threshold
                        strong_correlations.append({
                            "column1": correlation_matrix.columns[i],
                            "column2": correlation_matrix.columns[j],
                            "correlation": corr_value
                        })
            results["statistics"]["strong_correlations"] = strong_correlations
        
        # Distribution analysis
        distribution_info = {}
        for col in numeric_cols:
            col_data = data[col].dropna()
            if len(col_data) > 0:
                distribution_info[col] = {
                    "skewness": float(col_data.skew()),
                    "kurtosis": float(col_data.kurtosis()),
                    "is_normal": abs(col_data.skew()) < 0.5 and abs(col_data.kurtosis()) < 0.5
                }
        results["statistics"]["distributions"] = distribution_info
        
        # Outlier detection using IQR method
        outlier_info = {}
        for col in numeric_cols:
            col_data = data[col].dropna()
            if len(col_data) > 0:
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]
                outlier_info[col] = {
                    "count": len(outliers),
                    "percentage": len(outliers) / len(col_data) * 100,
                    "values": outliers.tolist() if len(outliers) <= 10 else outliers.head(10).tolist()
                }
        results["statistics"]["outliers"] = outlier_info
        
        # Data quality metrics
        quality_metrics = {
            "missing_values": data.isnull().sum().to_dict(),
            "duplicate_rows": data.duplicated().sum(),
            "memory_usage": data.memory_usage(deep=True).sum(),
            "data_types": data.dtypes.astype(str).to_dict()
        }
        results["statistics"]["data_quality"] = quality_metrics
        
        return results
    
    def cleanup(self) -> None:
        """Cleanup plugin resources"""
        self.initialized = False
        if hasattr(self, 'context'):
            del self.context
