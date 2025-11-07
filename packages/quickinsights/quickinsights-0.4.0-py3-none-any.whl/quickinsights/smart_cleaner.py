"""
QuickInsights - Smart Data Cleaning & Automation Module

Bu modül veri analistlerinin en çok zaman harcadığı veri temizleme işlemlerini otomatikleştirir.
Akıllı algoritmalar kullanarak en uygun temizleme stratejilerini önerir ve uygular.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")


class SmartCleaner:
    """
    Akıllı veri temizleme sistemi

    Veri kalitesi sorunlarını otomatik tespit eder ve en uygun çözümleri önerir/uygular.
    Machine learning tabanlı stratejiler kullanarak manuel müdahaleyi minimize eder.
    """

    def __init__(self, df: pd.DataFrame, target_column: Optional[str] = None):
        """
        SmartCleaner başlatıcısı

        Parameters
        ----------
        df : pd.DataFrame
            Temizlenecek veri seti
        target_column : str, optional
            Hedef değişken (supervised temizleme için)
        """
        self.original_df = df.copy()
        self.df = df.copy()
        self.target_column = target_column
        self.cleaning_log = []
        # Backward-compatibility alias expected by some callers/tests
        self.cleaning_history = self.cleaning_log
        self.suggestions = []

        # Veri tiplerini analiz et
        self._analyze_data_types()

    def _analyze_data_types(self):
        """Veri tiplerini detaylı analiz eder"""
        self.numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = self.df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()
        self.datetime_cols = self.df.select_dtypes(
            include=["datetime64"]
        ).columns.tolist()

        # Potential datetime columns (stored as object)
        self.potential_datetime_cols = []
        for col in self.categorical_cols:
            if self._is_likely_datetime(self.df[col]):
                self.potential_datetime_cols.append(col)

    def _is_likely_datetime(self, series: pd.Series, sample_size: int = 100) -> bool:
        """Bir sütunun datetime olma ihtimalini kontrol eder"""
        if len(series.dropna()) == 0:
            return False

        sample = series.dropna().sample(
            min(sample_size, len(series.dropna())), random_state=42
        )

        datetime_patterns = [
            r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
            r"\d{2}/\d{2}/\d{4}",  # MM/DD/YYYY
            r"\d{2}-\d{2}-\d{4}",  # MM-DD-YYYY
            r"\d{4}/\d{2}/\d{2}",  # YYYY/MM/DD
        ]

        import re

        matches = 0
        for value in sample.astype(str):
            for pattern in datetime_patterns:
                if re.match(pattern, value):
                    matches += 1
                    break

        return matches / len(sample) > 0.7  # 70% match threshold

    def auto_clean(
        self, aggressive: bool = False, preserve_original: bool = True
    ) -> Dict[str, Any]:
        """
        Otomatik veri temizleme işlemi yapar

        Parameters
        ----------
        aggressive : bool, default=False
            Agresif temizleme modunu aktifleştirir
        preserve_original : bool, default=True
            Orijinal veriyi korur

        Returns
        -------
        Dict[str, Any]
            Temizleme raporu ve sonuçları
        """

        if preserve_original:
            self.df = self.original_df.copy()

        cleaning_steps = []

        # 1. Datetime conversion
        datetime_fixes = self._fix_datetime_columns()
        if datetime_fixes["converted_columns"]:
            cleaning_steps.append(datetime_fixes)

        # 2. Missing data handling
        missing_fixes = self._handle_missing_data(aggressive=aggressive)
        if missing_fixes["actions_taken"]:
            cleaning_steps.append(missing_fixes)

        # 3. Duplicate removal
        duplicate_fixes = self._handle_duplicates(aggressive=aggressive)
        if duplicate_fixes["removed_count"] > 0:
            cleaning_steps.append(duplicate_fixes)

        # 4. Outlier handling
        outlier_fixes = self._handle_outliers(aggressive=aggressive)
        if outlier_fixes["actions_taken"]:
            cleaning_steps.append(outlier_fixes)

        # 5. Data type optimization
        type_fixes = self._optimize_data_types()
        if type_fixes["optimized_columns"]:
            cleaning_steps.append(type_fixes)

        # 6. Categorical data cleaning
        categorical_fixes = self._clean_categorical_data()
        if categorical_fixes["actions_taken"]:
            cleaning_steps.append(categorical_fixes)

        return {
            "original_shape": self.original_df.shape,
            "cleaned_shape": self.df.shape,
            "cleaning_steps": cleaning_steps,
            "quality_improvement": self._calculate_quality_improvement(),
            "recommendations": self._generate_post_cleaning_recommendations(),
            "cleaned_data": self.df,
            "cleaning_history": self.cleaning_log,
        }

    def _fix_datetime_columns(self) -> Dict[str, Any]:
        """Datetime sütunlarını düzeltir"""
        converted_columns = []
        errors = []

        for col in self.potential_datetime_cols:
            try:
                original_type = str(self.df[col].dtype)
                self.df[col] = pd.to_datetime(
                    self.df[col], errors="coerce", infer_datetime_format=True
                )

                # Check conversion success rate
                null_after = self.df[col].isnull().sum()
                null_before = self.original_df[col].isnull().sum()
                new_nulls = null_after - null_before

                if new_nulls / len(self.df) < 0.1:  # Less than 10% failed conversions
                    converted_columns.append(
                        {
                            "column": col,
                            "from_type": original_type,
                            "to_type": "datetime64[ns]",
                            "failed_conversions": new_nulls,
                        }
                    )
                    self.cleaning_log.append(f"✅ Converted '{col}' to datetime")
                else:
                    # Revert if too many failed conversions
                    self.df[col] = self.original_df[col].copy()
                    errors.append(
                        f"❌ Failed to convert '{col}' - too many parsing errors"
                    )

            except Exception as e:
                errors.append(f"❌ Error converting '{col}': {str(e)}")

        return {
            "step": "datetime_conversion",
            "converted_columns": converted_columns,
            "errors": errors,
        }

    def _handle_missing_data(self, aggressive: bool = False) -> Dict[str, Any]:
        """Eksik verileri akıllı yöntemlerle doldurur"""
        actions_taken = []

        missing_analysis = self.df.isnull().sum()
        missing_columns = missing_analysis[missing_analysis > 0]

        if len(missing_columns) == 0:
            return {"step": "missing_data_handling", "actions_taken": []}

        for col in missing_columns.index:
            missing_count = missing_columns[col]
            missing_pct = missing_count / len(self.df)

            if missing_pct > 0.8 and aggressive:
                # Drop column if >80% missing and aggressive mode
                self.df.drop(columns=[col], inplace=True)
                actions_taken.append(
                    {
                        "column": col,
                        "action": "dropped_column",
                        "reason": f"{missing_pct:.1%} missing data",
                        "missing_count": missing_count,
                    }
                )
                self.cleaning_log.append(
                    f"🗑️ Dropped column '{col}' ({missing_pct:.1%} missing)"
                )

            elif missing_pct > 0.5:
                # High missing rate - just flag for manual review
                self.suggestions.append(
                    f"⚠️ Column '{col}' has {missing_pct:.1%} missing - consider dropping or manual imputation"
                )

            elif col in self.numeric_cols:
                # Numeric column imputation
                strategy = self._choose_numeric_imputation_strategy(col)

                if strategy == "median":
                    fill_value = self.df[col].median()
                    self.df[col].fillna(fill_value, inplace=True)
                    actions_taken.append(
                        {
                            "column": col,
                            "action": "filled_median",
                            "fill_value": fill_value,
                            "missing_count": missing_count,
                        }
                    )
                    self.cleaning_log.append(
                        f"📊 Filled '{col}' missing values with median ({fill_value:.2f})"
                    )

                elif strategy == "mean":
                    fill_value = self.df[col].mean()
                    self.df[col].fillna(fill_value, inplace=True)
                    actions_taken.append(
                        {
                            "column": col,
                            "action": "filled_mean",
                            "fill_value": fill_value,
                            "missing_count": missing_count,
                        }
                    )
                    self.cleaning_log.append(
                        f"📊 Filled '{col}' missing values with mean ({fill_value:.2f})"
                    )

                elif strategy == "mode":
                    fill_value = (
                        self.df[col].mode().iloc[0]
                        if not self.df[col].mode().empty
                        else 0
                    )
                    self.df[col].fillna(fill_value, inplace=True)
                    actions_taken.append(
                        {
                            "column": col,
                            "action": "filled_mode",
                            "fill_value": fill_value,
                            "missing_count": missing_count,
                        }
                    )
                    self.cleaning_log.append(
                        f"📊 Filled '{col}' missing values with mode ({fill_value})"
                    )

            elif col in self.categorical_cols:
                # Categorical column imputation
                if missing_pct < 0.2:  # Less than 20% missing
                    mode_value = (
                        self.df[col].mode().iloc[0]
                        if not self.df[col].mode().empty
                        else "Unknown"
                    )
                    self.df[col].fillna(mode_value, inplace=True)
                    actions_taken.append(
                        {
                            "column": col,
                            "action": "filled_mode",
                            "fill_value": mode_value,
                            "missing_count": missing_count,
                        }
                    )
                    self.cleaning_log.append(
                        f"📝 Filled '{col}' missing values with mode ('{mode_value}')"
                    )
                else:
                    # Create 'Missing' category for high missing rate
                    self.df[col].fillna("Missing_Data", inplace=True)
                    actions_taken.append(
                        {
                            "column": col,
                            "action": "filled_missing_category",
                            "fill_value": "Missing_Data",
                            "missing_count": missing_count,
                        }
                    )
                    self.cleaning_log.append(
                        f"📝 Created 'Missing_Data' category for '{col}'"
                    )

        return {"step": "missing_data_handling", "actions_taken": actions_taken}

    def _choose_numeric_imputation_strategy(self, column: str) -> str:
        """Sayısal sütun için en uygun imputation stratejisini seçer"""
        col_data = self.df[column].dropna()

        if len(col_data) == 0:
            return "median"  # Default fallback

        # Check distribution
        skewness = abs(col_data.skew())

        # Check for outliers
        Q1 = col_data.quantile(0.25)
        Q3 = col_data.quantile(0.75)
        IQR = Q3 - Q1
        outliers = col_data[(col_data < Q1 - 1.5 * IQR) | (col_data > Q3 + 1.5 * IQR)]
        outlier_ratio = len(outliers) / len(col_data)

        # Decision logic
        if skewness > 1 or outlier_ratio > 0.1:
            return "median"  # Use median for skewed data or data with outliers
        elif col_data.nunique() < 10:
            return "mode"  # Use mode for categorical-like numeric data
        else:
            return "mean"  # Use mean for normal-ish distributions

    def _handle_duplicates(self, aggressive: bool = False) -> Dict[str, Any]:
        """Duplicate kayıtları yönetir"""
        initial_count = len(self.df)

        # Find duplicates
        duplicate_mask = self.df.duplicated()
        duplicate_count = duplicate_mask.sum()

        if duplicate_count == 0:
            return {"step": "duplicate_handling", "removed_count": 0}

        duplicate_pct = duplicate_count / len(self.df)

        if duplicate_pct > 0.05 or aggressive:  # >5% duplicates or aggressive mode
            self.df.drop_duplicates(inplace=True)
            final_count = len(self.df)
            removed_count = initial_count - final_count

            self.cleaning_log.append(
                f"🔄 Removed {removed_count} duplicate rows ({duplicate_pct:.1%})"
            )

            return {
                "step": "duplicate_handling",
                "removed_count": removed_count,
                "duplicate_percentage": duplicate_pct,
            }
        else:
            self.suggestions.append(
                f"💡 {duplicate_count} duplicate rows detected ({duplicate_pct:.1%}) - consider manual review"
            )
            return {"step": "duplicate_handling", "removed_count": 0}

    def _handle_outliers(self, aggressive: bool = False) -> Dict[str, Any]:
        """Outlier'ları akıllı yöntemlerle yönetir"""
        actions_taken = []

        for col in self.numeric_cols:
            if col == self.target_column:
                continue  # Don't modify target variable

            outliers = self._detect_outliers(self.df[col])
            outlier_count = len(outliers)
            outlier_pct = outlier_count / len(self.df)

            if outlier_pct > 0.1:  # More than 10% outliers
                if aggressive and outlier_pct < 0.3:  # Remove if <30% and aggressive
                    self.df = self.df[~outliers]
                    actions_taken.append(
                        {
                            "column": col,
                            "action": "removed_outliers",
                            "removed_count": outlier_count,
                            "outlier_percentage": outlier_pct,
                        }
                    )
                    self.cleaning_log.append(
                        f"🎯 Removed {outlier_count} outliers from '{col}' ({outlier_pct:.1%})"
                    )

                elif outlier_pct < 0.2:  # Cap outliers if <20%
                    Q1 = self.df[col].quantile(0.25)
                    Q3 = self.df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR

                    self.df[col] = np.clip(self.df[col], lower_bound, upper_bound)
                    actions_taken.append(
                        {
                            "column": col,
                            "action": "capped_outliers",
                            "outlier_count": outlier_count,
                            "bounds": (lower_bound, upper_bound),
                        }
                    )
                    self.cleaning_log.append(
                        f"📐 Capped outliers in '{col}' to [{lower_bound:.2f}, {upper_bound:.2f}]"
                    )

                else:
                    self.suggestions.append(
                        f"⚠️ Column '{col}' has {outlier_pct:.1%} outliers - manual review recommended"
                    )

        return {"step": "outlier_handling", "actions_taken": actions_taken}

    def _detect_outliers(self, series: pd.Series) -> pd.Series:
        """IQR yöntemi ile outlier'ları tespit eder"""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        return (series < lower_bound) | (series > upper_bound)

    def _optimize_data_types(self) -> Dict[str, Any]:
        """Veri tiplerini optimize eder"""
        optimized_columns = []

        # Optimize integers
        for col in self.df.select_dtypes(include=["int64"]).columns:
            original_memory = self.df[col].memory_usage(deep=True)

            col_min = self.df[col].min()
            col_max = self.df[col].max()

            if col_min >= -128 and col_max <= 127:
                self.df[col] = self.df[col].astype("int8")
                new_memory = self.df[col].memory_usage(deep=True)
                optimized_columns.append(
                    {
                        "column": col,
                        "from_type": "int64",
                        "to_type": "int8",
                        "memory_saved_mb": (original_memory - new_memory) / 1024**2,
                    }
                )
            elif col_min >= -32768 and col_max <= 32767:
                self.df[col] = self.df[col].astype("int16")
                new_memory = self.df[col].memory_usage(deep=True)
                optimized_columns.append(
                    {
                        "column": col,
                        "from_type": "int64",
                        "to_type": "int16",
                        "memory_saved_mb": (original_memory - new_memory) / 1024**2,
                    }
                )
            elif col_min >= -2147483648 and col_max <= 2147483647:
                self.df[col] = self.df[col].astype("int32")
                new_memory = self.df[col].memory_usage(deep=True)
                optimized_columns.append(
                    {
                        "column": col,
                        "from_type": "int64",
                        "to_type": "int32",
                        "memory_saved_mb": (original_memory - new_memory) / 1024**2,
                    }
                )

        # Optimize floats
        for col in self.df.select_dtypes(include=["float64"]).columns:
            original_memory = self.df[col].memory_usage(deep=True)
            self.df[col] = pd.to_numeric(self.df[col], downcast="float")
            new_memory = self.df[col].memory_usage(deep=True)

            if original_memory != new_memory:
                optimized_columns.append(
                    {
                        "column": col,
                        "from_type": "float64",
                        "to_type": str(self.df[col].dtype),
                        "memory_saved_mb": (original_memory - new_memory) / 1024**2,
                    }
                )

        # Convert to category
        for col in self.df.select_dtypes(include=["object"]).columns:
            if col not in self.potential_datetime_cols:
                unique_ratio = self.df[col].nunique() / len(self.df)
                if unique_ratio < 0.5:  # Less than 50% unique values
                    original_memory = self.df[col].memory_usage(deep=True)
                    self.df[col] = self.df[col].astype("category")
                    new_memory = self.df[col].memory_usage(deep=True)

                    optimized_columns.append(
                        {
                            "column": col,
                            "from_type": "object",
                            "to_type": "category",
                            "memory_saved_mb": (original_memory - new_memory)
                            / 1024**2,
                        }
                    )

        total_memory_saved = sum([col["memory_saved_mb"] for col in optimized_columns])
        if optimized_columns:
            self.cleaning_log.append(
                f"💾 Optimized data types - saved {total_memory_saved:.2f} MB"
            )

        return {
            "step": "data_type_optimization",
            "optimized_columns": optimized_columns,
            "total_memory_saved_mb": total_memory_saved,
        }

    def _clean_categorical_data(self) -> Dict[str, Any]:
        """Kategorik verileri temizler"""
        actions_taken = []

        for col in self.categorical_cols:
            if col in self.df.columns:  # Column might have been dropped
                original_unique = self.df[col].nunique()

                # Trim whitespace and standardize case
                if self.df[col].dtype == "object":
                    self.df[col] = self.df[col].astype(str).str.strip().str.title()

                    # Remove very rare categories (less than 1% frequency)
                    value_counts = self.df[col].value_counts()
                    rare_threshold = len(self.df) * 0.01  # 1% threshold
                    rare_categories = value_counts[
                        value_counts < rare_threshold
                    ].index.tolist()

                    if (
                        len(rare_categories) > 0
                        and len(rare_categories) < original_unique * 0.3
                    ):  # Don't group if >30% are rare
                        self.df[col] = self.df[col].replace(
                            rare_categories, "Other_Category"
                        )
                        actions_taken.append(
                            {
                                "column": col,
                                "action": "grouped_rare_categories",
                                "rare_categories_count": len(rare_categories),
                                "threshold_pct": 1.0,
                            }
                        )
                        self.cleaning_log.append(
                            f"🏷️ Grouped {len(rare_categories)} rare categories in '{col}' as 'Other_Category'"
                        )

                new_unique = self.df[col].nunique()
                if new_unique != original_unique:
                    actions_taken.append(
                        {
                            "column": col,
                            "action": "standardized_text",
                            "unique_before": original_unique,
                            "unique_after": new_unique,
                        }
                    )

        return {"step": "categorical_data_cleaning", "actions_taken": actions_taken}

    def _calculate_quality_improvement(self) -> Dict[str, float]:
        """Temizleme sonrası kalite iyileşmesini hesaplar"""

        # Safeguards for empty dataframes to avoid division by zero
        original_size = max(1, self.original_df.size)
        current_size = max(1, self.df.size)
        original_len = max(1, len(self.original_df))
        current_len = max(1, len(self.df))

        # Original quality metrics
        original_missing_pct = (
            self.original_df.isnull().sum().sum() / original_size
        ) * 100
        original_duplicates_pct = (
            self.original_df.duplicated().sum() / original_len
        ) * 100

        # Current quality metrics
        current_missing_pct = (self.df.isnull().sum().sum() / current_size) * 100
        current_duplicates_pct = (self.df.duplicated().sum() / current_len) * 100

        # Memory efficiency
        original_memory = self.original_df.memory_usage(deep=True).sum() / 1024**2
        current_memory = self.df.memory_usage(deep=True).sum() / 1024**2
        memory_reduction_pct = (
            0.0
            if original_memory == 0
            else ((original_memory - current_memory) / original_memory) * 100
        )

        row_reduction_pct = (
            0.0
            if original_len == 0
            else ((len(self.original_df) - len(self.df)) / original_len) * 100
        )

        return {
            "missing_data_reduction_pct": original_missing_pct - current_missing_pct,
            "duplicate_reduction_pct": original_duplicates_pct - current_duplicates_pct,
            "memory_reduction_pct": memory_reduction_pct,
            "row_reduction_pct": row_reduction_pct,
        }

    # Public convenience methods expected by external callers/tests
    def clean(
        self, df: Optional[pd.DataFrame] = None, aggressive: bool = False
    ) -> Dict[str, Any]:
        """Runs auto_clean; optionally sets a new dataframe before cleaning."""
        if df is not None:
            self.original_df = df.copy()
            self.df = df.copy()
            self._analyze_data_types()
        return self.auto_clean(aggressive=aggressive, preserve_original=True)

    def handle_duplicates(
        self, df: pd.DataFrame, strategy: str = "remove"
    ) -> pd.DataFrame:
        """Public API to handle duplicates on a provided dataframe.
        - strategy='remove': drop duplicate rows
        - strategy='keep_first': keep first occurrences (same as drop_duplicates)
        - strategy='keep_last': keep last occurrences
        - strategy='flag': add a boolean column '_is_duplicate' and return
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")
        if df.empty:
            return df.copy()

        if strategy in ("remove", "keep_first"):
            return df.drop_duplicates()
        if strategy == "keep_last":
            return df.drop_duplicates(keep="last")
        if strategy == "flag":
            result = df.copy()
            result["_is_duplicate"] = result.duplicated()
            return result
        # default fallback
        return df.drop_duplicates()

    def handle_outliers(
        self,
        df: pd.DataFrame,
        columns: Optional[List[str]] = None,
        method: str = "iqr",
        aggressive: bool = False,
    ) -> pd.DataFrame:
        """Public API to handle outliers for specified columns using IQR.
        Removes rows with values outside [Q1-1.5*IQR, Q3+1.5*IQR] if aggressive,
        otherwise caps values to the bounds.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")
        if df.empty:
            return df.copy()

        result = df.copy()
        target_columns = (
            columns
            if columns is not None
            else result.select_dtypes(include=[np.number]).columns.tolist()
        )
        for col in target_columns:
            if col not in result.columns:
                continue
            series = result[col].dropna()
            if series.empty:
                continue
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            if aggressive:
                result = result[(result[col] >= lower) & (result[col] <= upper)]
            else:
                result[col] = np.clip(result[col], lower, upper)
        return result

    def optimize_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Public API to optimize data types and return the optimized dataframe."""
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")
        self.original_df = df.copy()
        self.df = df.copy()
        self._analyze_data_types()
        self._optimize_data_types()
        return self.df

    def _generate_post_cleaning_recommendations(self) -> List[str]:
        """Temizleme sonrası öneriler üretir"""
        recommendations = []

        # Data shape changes
        original_shape = self.original_df.shape
        current_shape = self.df.shape

        if current_shape[0] < original_shape[0]:
            row_loss_pct = (
                (original_shape[0] - current_shape[0]) / original_shape[0]
            ) * 100
            if row_loss_pct > 10:
                recommendations.append(
                    f"⚠️ Lost {row_loss_pct:.1f}% of rows during cleaning - verify this is acceptable"
                )

        if current_shape[1] < original_shape[1]:
            col_loss = original_shape[1] - current_shape[1]
            recommendations.append(
                f"📝 Dropped {col_loss} columns - document reasoning for stakeholders"
            )

        # Missing data
        remaining_missing = self.df.isnull().sum().sum()
        if remaining_missing > 0:
            recommendations.append(
                "🔍 Review remaining missing values for domain-specific imputation"
            )

        # Data types
        if len(self.df.select_dtypes(include=["object"]).columns) > 0:
            recommendations.append(
                "🏷️ Consider encoding categorical variables for machine learning"
            )

        # Next steps
        recommendations.append("📊 Run exploratory data analysis on cleaned dataset")
        recommendations.append("🎯 Validate data quality with domain experts")

        return recommendations


def smart_clean(
    df: pd.DataFrame, target_column: Optional[str] = None, aggressive: bool = False
) -> Dict[str, Any]:
    """
    Convenience function for quick smart cleaning

    Parameters
    ----------
    df : pd.DataFrame
        Temizlenecek veri seti
    target_column : str, optional
        Hedef değişken
    aggressive : bool, default=False
        Agresif temizleme modu

    Returns
    -------
    Dict[str, Any]
        Temizleme raporu ve temizlenmiş veri
    """
    cleaner = SmartCleaner(df, target_column)
    return cleaner.auto_clean(aggressive=aggressive)


def analyze_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Veri kalitesini detaylı analiz eder

    Parameters
    ----------
    df : pd.DataFrame
        Analiz edilecek veri seti

    Returns
    -------
    Dict[str, Any]
        Detaylı veri kalitesi raporu
    """

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    quality_report = {
        "overview": {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024**2,
            "data_types": {
                "numeric": len(numeric_cols),
                "categorical": len(categorical_cols),
                "other": len(df.columns) - len(numeric_cols) - len(categorical_cols),
            },
        },
        "missing_data": {
            "total_missing": df.isnull().sum().sum(),
            "missing_percentage": (df.isnull().sum().sum() / df.size) * 100,
            "columns_with_missing": df.isnull().sum()[df.isnull().sum() > 0].to_dict(),
            "missing_patterns": df.isnull().sum().value_counts().to_dict(),
        },
        "duplicates": {
            "duplicate_rows": df.duplicated().sum(),
            "duplicate_percentage": (df.duplicated().sum() / len(df)) * 100,
            "unique_rows": len(df) - df.duplicated().sum(),
        },
        "data_consistency": {},
        "recommendations": [],
    }

    # Analyze consistency issues
    consistency_issues = []

    for col in categorical_cols:
        if df[col].dtype == "object":
            # Check for whitespace issues
            has_leading_trailing_spaces = (
                df[col].astype(str).str.strip().ne(df[col].astype(str)).any()
            )
            if has_leading_trailing_spaces:
                consistency_issues.append(f"'{col}' has leading/trailing whitespace")

            # Check for case inconsistency
            unique_values = df[col].dropna().unique()
            if len(unique_values) > 1:
                case_variants = {}
                for val in unique_values:
                    lower_val = str(val).lower().strip()
                    if lower_val in case_variants:
                        case_variants[lower_val].append(val)
                    else:
                        case_variants[lower_val] = [val]

                for lower_val, variants in case_variants.items():
                    if len(variants) > 1:
                        consistency_issues.append(
                            f"'{col}' has case variants: {variants}"
                        )
                        break  # Only report first few to avoid spam

    quality_report["data_consistency"]["issues"] = consistency_issues

    # Generate recommendations
    recommendations = []

    if quality_report["missing_data"]["missing_percentage"] > 20:
        recommendations.append(
            "🔴 High missing data rate (>20%) - investigate data collection process"
        )
    elif quality_report["missing_data"]["missing_percentage"] > 5:
        recommendations.append("🟡 Moderate missing data - plan imputation strategy")

    if quality_report["duplicates"]["duplicate_percentage"] > 5:
        recommendations.append("🔴 High duplicate rate (>5%) - investigate and remove")
    elif quality_report["duplicates"]["duplicate_percentage"] > 0:
        recommendations.append("🟡 Some duplicates detected - verify if intentional")

    if len(consistency_issues) > 0:
        recommendations.append(
            "🟡 Data consistency issues detected - standardize formatting"
        )

    if quality_report["overview"]["memory_usage_mb"] > 1000:  # >1GB
        recommendations.append("💾 Large dataset - consider data type optimization")

    quality_report["recommendations"] = recommendations

    return quality_report
