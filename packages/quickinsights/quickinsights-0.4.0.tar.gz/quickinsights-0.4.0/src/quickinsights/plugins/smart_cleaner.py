"""
Smart Cleaner Plugin

Example plugin that demonstrates intelligent data cleaning capabilities.
"""

import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from plugin_system import (
    CleanerPlugin, 
    PluginInfo, 
    PluginType, 
    PluginPriority
)


class SmartCleanerPlugin(CleanerPlugin):
    """Smart data cleaner plugin with intelligent cleaning strategies"""
    
    def get_info(self) -> PluginInfo:
        """Get plugin information"""
        return PluginInfo(
            name="SmartCleaner",
            version="1.0.0",
            description="Intelligent data cleaning plugin with automatic strategy selection",
            author="QuickInsights Team",
            plugin_type=PluginType.CLEANER,
            priority=PluginPriority.HIGH,
            dependencies=["pandas", "numpy"],
            entry_point="smart_cleaner"
        )
    
    def initialize(self, context: Dict[str, Any]) -> None:
        """Initialize the plugin"""
        self.context = context
        self.initialized = True
        self.cleaning_strategies = {
            'missing_values': self._handle_missing_values,
            'outliers': self._handle_outliers,
            'duplicates': self._handle_duplicates,
            'data_types': self._handle_data_types,
            'inconsistencies': self._handle_inconsistencies
        }
    
    def clean(self, data: Any, **kwargs) -> Any:
        """Clean data using intelligent strategies"""
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Data must be a pandas DataFrame")
        
        # Create a copy to avoid modifying original data
        cleaned_data = data.copy()
        
        # Get cleaning options
        strategies = kwargs.get('strategies', list(self.cleaning_strategies.keys()))
        auto_detect = kwargs.get('auto_detect', True)
        report_changes = kwargs.get('report_changes', True)
        
        # Auto-detect cleaning needs if enabled
        if auto_detect:
            strategies = self._detect_cleaning_needs(cleaned_data, strategies)
        
        # Track changes
        changes_log = {
            "original_shape": data.shape,
            "strategies_applied": [],
            "changes_made": {}
        }
        
        # Apply cleaning strategies
        for strategy in strategies:
            if strategy in self.cleaning_strategies:
                try:
                    changes = self.cleaning_strategies[strategy](cleaned_data, **kwargs)
                    changes_log["strategies_applied"].append(strategy)
                    changes_log["changes_made"][strategy] = changes
                except Exception as e:
                    print(f"Warning: Failed to apply {strategy} strategy: {e}")
        
        changes_log["final_shape"] = cleaned_data.shape
        
        if report_changes:
            return {
                "cleaned_data": cleaned_data,
                "changes_log": changes_log,
                "summary": self._generate_cleaning_summary(changes_log)
            }
        else:
            return cleaned_data
    
    def _detect_cleaning_needs(self, data: pd.DataFrame, available_strategies: List[str]) -> List[str]:
        """Auto-detect what cleaning strategies are needed"""
        needed_strategies = []
        
        # Check for missing values
        if 'missing_values' in available_strategies and data.isnull().any().any():
            needed_strategies.append('missing_values')
        
        # Check for duplicates
        if 'duplicates' in available_strategies and data.duplicated().any():
            needed_strategies.append('duplicates')
        
        # Check for outliers in numeric columns
        if 'outliers' in available_strategies:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if self._has_outliers(data[col]):
                    needed_strategies.append('outliers')
                    break
        
        # Check for data type inconsistencies
        if 'data_types' in available_strategies:
            for col in data.columns:
                if self._has_type_inconsistencies(data[col]):
                    needed_strategies.append('data_types')
                    break
        
        # Check for inconsistencies in categorical data
        if 'inconsistencies' in available_strategies:
            categorical_cols = data.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                if self._has_inconsistencies(data[col]):
                    needed_strategies.append('inconsistencies')
                    break
        
        return needed_strategies
    
    def _handle_missing_values(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Handle missing values"""
        strategy = kwargs.get('missing_strategy', 'auto')
        threshold = kwargs.get('missing_threshold', 0.5)
        
        changes = {
            "missing_before": data.isnull().sum().to_dict(),
            "missing_after": {},
            "strategy_used": strategy
        }
        
        if strategy == 'auto':
            # Auto strategy: drop columns with >50% missing, fill others
            for col in data.columns:
                missing_ratio = data[col].isnull().sum() / len(data)
                if missing_ratio > threshold:
                    data.drop(columns=[col], inplace=True)
                else:
                    if data[col].dtype in ['object', 'category']:
                        data[col].fillna(data[col].mode()[0] if not data[col].mode().empty else 'Unknown', inplace=True)
                    else:
                        data[col].fillna(data[col].median(), inplace=True)
        
        elif strategy == 'drop':
            data.dropna(inplace=True)
        
        elif strategy == 'fill':
            fill_method = kwargs.get('fill_method', 'median')
            if fill_method == 'median':
                data.fillna(data.median(), inplace=True)
            elif fill_method == 'mean':
                data.fillna(data.mean(), inplace=True)
            elif fill_method == 'mode':
                for col in data.columns:
                    if data[col].dtype in ['object', 'category']:
                        mode_val = data[col].mode()[0] if not data[col].mode().empty else 'Unknown'
                        data[col].fillna(mode_val, inplace=True)
                    else:
                        data[col].fillna(data[col].median(), inplace=True)
        
        changes["missing_after"] = data.isnull().sum().to_dict()
        return changes
    
    def _handle_outliers(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Handle outliers"""
        method = kwargs.get('outlier_method', 'iqr')
        threshold = kwargs.get('outlier_threshold', 1.5)
        
        changes = {
            "outliers_before": {},
            "outliers_after": {},
            "method_used": method
        }
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            outliers_before = self._count_outliers(data[col], method, threshold)
            changes["outliers_before"][col] = outliers_before
            
            if method == 'iqr':
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                # Cap outliers instead of removing them
                data[col] = data[col].clip(lower=lower_bound, upper=upper_bound)
            
            elif method == 'zscore':
                z_scores = np.abs((data[col] - data[col].mean()) / data[col].std())
                data[col] = data[col].where(z_scores < threshold, data[col].median())
            
            outliers_after = self._count_outliers(data[col], method, threshold)
            changes["outliers_after"][col] = outliers_after
        
        return changes
    
    def _handle_duplicates(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Handle duplicate rows"""
        strategy = kwargs.get('duplicate_strategy', 'remove')
        
        changes = {
            "duplicates_before": data.duplicated().sum(),
            "duplicates_after": 0,
            "strategy_used": strategy
        }
        
        if strategy == 'remove':
            data.drop_duplicates(inplace=True)
        elif strategy == 'keep_first':
            data.drop_duplicates(keep='first', inplace=True)
        elif strategy == 'keep_last':
            data.drop_duplicates(keep='last', inplace=True)
        
        changes["duplicates_after"] = data.duplicated().sum()
        return changes
    
    def _handle_data_types(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Handle data type inconsistencies"""
        changes = {
            "type_changes": {},
            "conversion_errors": {}
        }
        
        for col in data.columns:
            original_type = str(data[col].dtype)
            
            # Try to convert to numeric if possible
            if data[col].dtype == 'object':
                try:
                    # Try to convert to numeric
                    numeric_data = pd.to_numeric(data[col], errors='coerce')
                    if not numeric_data.isnull().all():
                        data[col] = numeric_data
                        changes["type_changes"][col] = f"{original_type} -> {str(data[col].dtype)}"
                except:
                    # Try to convert to datetime
                    try:
                        datetime_data = pd.to_datetime(data[col], errors='coerce')
                        if not datetime_data.isnull().all():
                            data[col] = datetime_data
                            changes["type_changes"][col] = f"{original_type} -> {str(data[col].dtype)}"
                    except:
                        pass
        
        return changes
    
    def _handle_inconsistencies(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Handle inconsistencies in categorical data"""
        changes = {
            "inconsistencies_fixed": {}
        }
        
        categorical_cols = data.select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            # Standardize text (lowercase, strip whitespace)
            original_values = data[col].value_counts().to_dict()
            data[col] = data[col].astype(str).str.lower().str.strip()
            
            # Find and fix common inconsistencies
            value_mapping = self._create_value_mapping(data[col])
            if value_mapping:
                data[col] = data[col].map(value_mapping).fillna(data[col])
                changes["inconsistencies_fixed"][col] = value_mapping
        
        return changes
    
    def _has_outliers(self, series: pd.Series) -> bool:
        """Check if series has outliers"""
        if series.dtype not in [np.number]:
            return False
        
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        return ((series < lower_bound) | (series > upper_bound)).any()
    
    def _has_type_inconsistencies(self, series: pd.Series) -> bool:
        """Check if series has type inconsistencies"""
        if series.dtype == 'object':
            # Check if all values can be converted to numeric
            try:
                pd.to_numeric(series, errors='raise')
                return True
            except:
                pass
        return False
    
    def _has_inconsistencies(self, series: pd.Series) -> bool:
        """Check if series has inconsistencies"""
        if series.dtype == 'object':
            # Check for case inconsistencies
            unique_lower = series.str.lower().nunique()
            unique_original = series.nunique()
            return unique_lower < unique_original
        return False
    
    def _count_outliers(self, series: pd.Series, method: str, threshold: float) -> int:
        """Count outliers in a series"""
        if method == 'iqr':
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            return ((series < lower_bound) | (series > upper_bound)).sum()
        elif method == 'zscore':
            z_scores = np.abs((series - series.mean()) / series.std())
            return (z_scores > threshold).sum()
        return 0
    
    def _create_value_mapping(self, series: pd.Series) -> Dict[str, str]:
        """Create mapping for inconsistent values"""
        value_counts = series.value_counts()
        mapping = {}
        
        # Group similar values (simple approach)
        for value in value_counts.index:
            if value in mapping:
                continue
            
            # Find similar values (case-insensitive)
            similar_values = [v for v in value_counts.index 
                            if v.lower() == value.lower() and v != value]
            
            if similar_values:
                # Use the most frequent value as the standard
                all_values = [value] + similar_values
                standard_value = max(all_values, key=lambda x: value_counts[x])
                for v in all_values:
                    if v != standard_value:
                        mapping[v] = standard_value
        
        return mapping
    
    def _generate_cleaning_summary(self, changes_log: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of cleaning operations"""
        summary = {
            "total_strategies": len(changes_log["strategies_applied"]),
            "strategies_applied": changes_log["strategies_applied"],
            "shape_change": {
                "before": changes_log["original_shape"],
                "after": changes_log["final_shape"],
                "rows_removed": changes_log["original_shape"][0] - changes_log["final_shape"][0],
                "columns_removed": changes_log["original_shape"][1] - changes_log["final_shape"][1]
            }
        }
        
        # Count total changes
        total_changes = 0
        for strategy, changes in changes_log["changes_made"].items():
            if isinstance(changes, dict):
                total_changes += len(changes)
        
        summary["total_changes"] = total_changes
        return summary
    
    def cleanup(self) -> None:
        """Cleanup plugin resources"""
        self.initialized = False
        if hasattr(self, 'context'):
            del self.context
        if hasattr(self, 'cleaning_strategies'):
            del self.cleaning_strategies
