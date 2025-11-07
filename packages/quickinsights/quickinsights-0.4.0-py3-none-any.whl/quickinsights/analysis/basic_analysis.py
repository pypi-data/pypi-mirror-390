"""
Basic Analysis Functions

Core analysis functions extracted from core.py for better modularity.
"""

import os
from typing import Any, Dict
import numpy as np
import pandas as pd

from ..utils import detect_outliers, get_data_info
from ..visualizer import (
    box_plots as viz_box_plots,
    correlation_matrix,
    distribution_plots,
    summary_stats as viz_summary_stats,
)


def validate_dataframe(df: Any) -> bool:
    """Check if DataFrame is valid with enhanced validation."""
    from ..error_handling import ValidationUtils, DataValidationError
    
    # Basic validation
    ValidationUtils.validate_dataframe(df)
    
    # Enhanced validation
    if df.empty:
        raise DataValidationError(
            "DataFrame is empty", 
            details={"rows": 0, "columns": 0}
        )
    
    # Check for reasonable size limits
    if df.shape[0] > 10_000_000:  # 10M rows
        raise DataValidationError(
            f"DataFrame too large: {df.shape[0]} rows. Maximum allowed: 10,000,000",
            details={"rows": df.shape[0], "max_rows": 10_000_000}
        )
    
    # Check memory usage (only for very large DataFrames)
    try:
        memory_mb = df.memory_usage(deep=True).sum() / 1024**2
        if memory_mb > 2000:  # 2GB - more lenient
            raise DataValidationError(
                f"DataFrame too large in memory: {memory_mb:.1f}MB. Maximum allowed: 2000MB",
                details={"memory_mb": memory_mb, "max_memory_mb": 2000}
            )
    except Exception:
        # If memory calculation fails, skip the check
        pass
    
    return True


def analyze(
    df: pd.DataFrame,
    show_plots: bool = True,
    save_plots: bool = False,
    output_dir: str = "./quickinsights_output",
) -> Dict[str, Any]:
    """Perform comprehensive analysis on dataset."""
    # DataFrame validation
    validate_dataframe(df)

    print("🔍 QuickInsights - Dataset Analysis Starting...")
    print("=" * 60)

    # Create output directory
    if save_plots:
        os.makedirs(output_dir, exist_ok=True)
        print(f"📁 Output directory: {output_dir}")

    # Dataset information
    print("\n📊 Dataset Information:")
    print(f"   📏 Size: {df.shape[0]} rows, {df.shape[1]} columns")
    memory_mb = df.memory_usage(deep=True).sum() / 1024**2
    print(f"   💾 Memory usage: {memory_mb:.2f} MB")

    # Data types
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    print(f"   🔢 Numeric variables: {len(numeric_cols)}")
    print(f"   📝 Categorical variables: {len(categorical_cols)}")

    # Missing value analysis
    missing_data = df.isnull().sum()
    if missing_data.sum() > 0:
        print("\n⚠️  Missing Values:")
        for col, missing_count in missing_data[missing_data > 0].items():
            percentage = (missing_count / len(df)) * 100
            print(f"   {col}: {missing_count} ({percentage:.1f}%)")
    else:
        print("\n✅ No missing values found!")

    # Analysis sections
    print("\n🔢 Numeric Variable Analysis:")
    numeric_results = analyze_numeric(df)

    print("\n📝 Categorical Variable Analysis:")
    categorical_results = analyze_categorical(df)

    # Visualization
    if show_plots or save_plots:
        if save_plots:
            print("\n📈 Creating and saving visualizations...")
        else:
            print("\n📈 Creating visualizations...")

        # Create visualizations
        try:
            if len(numeric_cols) > 0:
                # Correlation matrix
                correlation_matrix(
                    df[numeric_cols], save_plots=save_plots, output_dir=output_dir
                )

                # Distribution plots
                distribution_plots(
                    df[numeric_cols], save_plots=save_plots, output_dir=output_dir
                )

                # Box plots
                viz_box_plots(
                    df[numeric_cols], save_plot=save_plots, output_dir=output_dir
                )

            if len(categorical_cols) > 0:
                # Categorical analysis plots
                for col in categorical_cols:
                    if (
                        df[col].nunique() <= 20
                    ):  # Only plot if not too many unique values
                        viz_summary_stats(df)

        except Exception as e:
            print(f"⚠️  Visualization error: {e}")

    # Summary statistics
    print("\n📊 Summary Statistics:")
    summary_stats = {
        "dataset_info": {
            "rows": df.shape[0],
            "columns": df.shape[1],
            "memory_mb": df.memory_usage(deep=True).sum() / 1024**2,
            "missing_values": missing_data.sum(),
            "duplicate_rows": df.duplicated().sum(),
        },
        "numeric_analysis": numeric_results,
        "categorical_analysis": categorical_results,
    }

    print(f"   📏 Total rows: {summary_stats['dataset_info']['rows']}")
    print(f"   📊 Total columns: {summary_stats['dataset_info']['columns']}")
    print(f"   💾 Memory usage: {summary_stats['dataset_info']['memory_mb']:.2f} MB")
    print(f"   ❓ Missing values: {summary_stats['dataset_info']['missing_values']}")
    print(f"   🔄 Duplicate rows: {summary_stats['dataset_info']['duplicate_rows']}")

    print("\n✅ Analysis completed!")

    return summary_stats


def analyze_numeric(
    df: pd.DataFrame,
    show_plots: bool = True,
    save_plots: bool = False,
    output_dir: str = "./quickinsights_output",
) -> Dict[str, Any]:
    """Perform detailed analysis on numeric variables."""
    from ..error_handling import DataValidationError
    
    # Validate input
    if not isinstance(df, pd.DataFrame):
        raise DataValidationError(f"Expected DataFrame, got {type(df).__name__}")
    
    results = {}
    
    # Only analyze numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if not numeric_cols:
        print("   🔢 No numeric variables found")
        return results
    
    # Vectorized operations for better performance
    numeric_df = df[numeric_cols]
    
    for col in numeric_cols:
        col_data = numeric_df[col].dropna()
        
        if len(col_data) == 0:
            continue
            
        # Basic statistics - vectorized
        stats = {
            "count": len(col_data),
            "mean": float(col_data.mean()),
            "std": float(col_data.std()),
            "min": float(col_data.min()),
            "max": float(col_data.max()),
            "median": float(col_data.median()),
            "q25": float(col_data.quantile(0.25)),
            "q75": float(col_data.quantile(0.75)),
        }
        
        # Outlier detection - only for this column
        outliers = detect_outliers(numeric_df[[col]], columns=[col])
        stats["outliers_count"] = outliers.get(col, {}).get("count", 0)
        stats["outliers_percentage"] = outliers.get(col, {}).get("percentage", 0)
        
        results[col] = stats
        
        # Print results
        print(f"   📊 {col}:")
        print(f"      Mean: {stats['mean']:.2f}")
        print(f"      Std: {stats['std']:.2f}")
        print(f"      Range: [{stats['min']:.2f}, {stats['max']:.2f}]")
        print(f"      Outliers: {stats['outliers_count']} ({stats['outliers_percentage']:.1f}%)")
    
    return results


def analyze_categorical(
    df: pd.DataFrame,
    show_plots: bool = True,
    save_plots: bool = False,
    output_dir: str = "./quickinsights_output",
) -> Dict[str, Any]:
    """Perform detailed analysis on categorical variables."""
    from ..error_handling import DataValidationError
    
    # Validate input
    if not isinstance(df, pd.DataFrame):
        raise DataValidationError(f"Expected DataFrame, got {type(df).__name__}")
    
    results = {}
    
    # Only analyze categorical columns
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    
    if not categorical_cols:
        print("   📝 No categorical variables found")
        return results
    
    for col in categorical_cols:
        col_data = df[col].dropna()
        
        if len(col_data) == 0:
            continue
            
        # Value counts
        value_counts = col_data.value_counts()
        
        # Basic statistics
        stats = {
            "count": len(col_data),
            "unique_values": len(value_counts),
            "most_common": value_counts.index[0] if len(value_counts) > 0 else None,
            "most_common_count": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
            "most_common_percentage": (value_counts.iloc[0] / len(col_data)) * 100 if len(value_counts) > 0 else 0,
        }
        
        results[col] = stats
        
        # Print results
        print(f"   📝 {col}:")
        print(f"      Unique values: {stats['unique_values']}")
        print(f"      Most common: {stats['most_common']} ({stats['most_common_percentage']:.1f}%)")
        
        # Show top values
        if len(value_counts) <= 10:
            print(f"      Top values: {dict(value_counts.head())}")
        else:
            print(f"      Top 5 values: {dict(value_counts.head())}")
    
    return results
