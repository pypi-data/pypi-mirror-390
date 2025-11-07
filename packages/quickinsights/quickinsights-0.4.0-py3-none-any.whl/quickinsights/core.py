"""
QuickInsights Core Analysis Module

This module contains the main analysis functions for datasets.
"""

import os
from pathlib import Path
from typing import Any, Dict, Union, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .utils import detect_outliers, get_data_info
from .visualizer import correlation_matrix, distribution_plots


def validate_dataframe(df: Any) -> bool:
    """
    Check if DataFrame is valid.

    Parameters
    ----------
    df : Any
        Data to check

    Returns
    -------
    bool
        True if DataFrame is valid, False otherwise

    Raises
    ------
    DataValidationError
        If DataFrame is invalid
    """
    from .error_handling import ValidationUtils

    ValidationUtils.validate_dataframe(df)
    return True


def analyze(
    df: Union[pd.DataFrame, str, Path],
    show_plots: bool = True,
    save_plots: bool = False,
    output_dir: str = "./quickinsights_output",
    enable_cache: bool = True,
    chunksize: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Perform comprehensive analysis on dataset.
    
    This function now supports both DataFrame and file path inputs.
    When a file path is provided, SmartDataLoader is used for optimal performance.
    
    Parameters
    ----------
    df : pd.DataFrame, str, or Path
        DataFrame to analyze or path to data file
    show_plots : bool
        Whether to display plots
    save_plots : bool
        Whether to save plots
    output_dir : str
        Output directory for saved plots
    enable_cache : bool
        Enable automatic format conversion and caching (only for file paths)
    chunksize : int, optional
        If provided for file paths, enables streaming analysis mode.
        Processes data in chunks to reduce memory usage.
        Recommended for large files (>100MB).
    **kwargs
        Additional arguments for pandas read functions (only for file paths)
    
    Returns
    -------
    dict
        Analysis results
    
    Examples
    --------
    >>> # Analyze DataFrame
    >>> result = analyze(df, show_plots=False)
    
    >>> # Analyze from file (automatically uses Parquet if available)
    >>> result = analyze('data.csv', enable_cache=True)
    """
    # Import here to avoid circular imports
    from .analysis.basic_analysis import analyze as analyze_data
    
    # Check if input is a file path
    if isinstance(df, (str, Path)):
        # Use analysis result caching if enabled
        use_result_cache = enable_cache  # Reuse enable_cache flag for result caching
        
        if use_result_cache:
            from .caching import get_cache
            
            cache = get_cache()
            
            # Build cache parameters
            cache_params = {
                'chunksize': chunksize,
                'show_plots': show_plots,
                'save_plots': save_plots,
                'output_dir': output_dir,
                **kwargs
            }
            
            # Try to get from cache
            cached_result = cache.get(df, cache_params)
            if cached_result is not None:
                return cached_result
        
        # Check if chunksize is provided for streaming analysis
        if chunksize is not None:
            from .streaming import analyze_streaming
            result = analyze_streaming(
                df,
                chunksize=chunksize,
                show_plots=show_plots,
                save_plots=save_plots,
                output_dir=output_dir,
                enable_cache=enable_cache,
                **kwargs
            )
        else:
            from .io import load_data
            # Load data with smart loader
            df_loaded = load_data(df, enable_cache=enable_cache, **kwargs)
            # Perform analysis
            result = analyze_data(df_loaded, show_plots, save_plots, output_dir)
        
        # Cache result if enabled
        if use_result_cache:
            from .caching import get_cache
            cache = get_cache()
            cache_params = {
                'chunksize': chunksize,
                'show_plots': show_plots,
                'save_plots': save_plots,
                'output_dir': output_dir,
                **kwargs
            }
            cache.set(df, cache_params, result)
        
        return result
    
    # Perform analysis on DataFrame (no caching for DataFrames)
    return analyze_data(df, show_plots, save_plots, output_dir)


def analyze_numeric(
    df: pd.DataFrame,
    show_plots: bool = True,
    save_plots: bool = False,
    output_dir: str = "./quickinsights_output",
) -> Dict[str, Any]:
    """Perform detailed analysis on numeric variables."""
    from .analysis.basic_analysis import analyze_numeric as analyze_numeric_data
    from .error_handling import DataValidationError
    
    # Validate input
    if not isinstance(df, pd.DataFrame):
        raise DataValidationError(f"Expected DataFrame, got {type(df).__name__}")
    
    return analyze_numeric_data(df, show_plots, save_plots, output_dir)


def analyze_categorical(
    df: pd.DataFrame,
    show_plots: bool = True,
    save_plots: bool = False,
    output_dir: str = "./quickinsights_output",
) -> Dict[str, Any]:
    """Perform detailed analysis on categorical variables."""
    from .analysis.basic_analysis import analyze_categorical as analyze_categorical_data
    from .error_handling import DataValidationError
    
    # Validate input
    if not isinstance(df, pd.DataFrame):
        raise DataValidationError(f"Expected DataFrame, got {type(df).__name__}")
    
    return analyze_categorical_data(df, show_plots, save_plots, output_dir)


def summary_stats(
    df: pd.DataFrame,
    save_plots: bool = False,
    output_dir: str = "./quickinsights_output",
) -> Dict[str, Dict[str, float]]:
    """
    Calculate summary statistics for a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe to analyze
    save_plots : bool, default=False
        Whether to save plots
    output_dir : str, default="./quickinsights_output"
        Directory to save plots

    Returns
    -------
    Dict[str, Dict[str, float]]
        Summary statistics for each column
    """
    stats = {}

    for col in df.columns:
        if df[col].dtype in ["int64", "float64"]:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                stats[col] = {
                    "mean": float(col_data.mean()),
                    "median": float(col_data.median()),
                    "std": float(col_data.std()),
                    "min": float(col_data.min()),
                    "max": float(col_data.max()),
                    "q1": float(col_data.quantile(0.25)),
                    "q3": float(col_data.quantile(0.75)),
                }

    return stats


def box_plots(
    df: pd.DataFrame,
    save_plot: bool = False,
    output_dir: str = "./quickinsights_output",
) -> None:
    """
    Create box plots for numeric variables.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing only numeric variables
    save_plot : bool, default=False
        Whether to save plots
    output_dir : str, default="./quickinsights_output"
        Directory to save plots
    """
    if df.empty:
        print("⚠️  No numeric variables found for box plots!")
        return

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) == 0:
        print("⚠️  No numeric variables found for box plots!")
        return

    print(f"\n📦 Creating box plots ({len(numeric_cols)} variables)...")

    # Create box plots
    fig, axes = plt.subplots(1, len(numeric_cols), figsize=(5 * len(numeric_cols), 6))

    if len(numeric_cols) == 1:
        axes = [axes]

    for i, col in enumerate(numeric_cols):
        df[col].plot(kind="box", ax=axes[i])
        axes[i].set_title(f"Box Plot - {col}")
        axes[i].set_ylabel("Value")

    plt.tight_layout()

    if save_plot:
        output_dir = create_output_directory(output_dir)
        plt.savefig(f"{output_dir}/box_plots.png", dpi=300, bbox_inches="tight")
        print(f"💾 Box plots saved: {output_dir}/box_plots.png")
        plt.close()
    else:
        plt.show()


def create_interactive_plots(
    df: pd.DataFrame,
    save_html: bool = False,
    output_dir: str = "./quickinsights_output",
) -> None:
    """
    Create interactive plots for numeric variables.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing only numeric variables
    save_html : bool, default=False
        Whether to save HTML files
    output_dir : str, default="./quickinsights_output"
        Directory to save files
    """
    if df.empty:
        print("⚠️  No numeric variables found for interactive plots!")
        return

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) == 0:
        print("⚠️  No numeric variables found for interactive plots!")
        return

    print(f"\n🎨 Creating interactive plots ({len(numeric_cols)} variables)...")

    try:
        import plotly.express as px

        # Scatter plot matrix
        if len(numeric_cols) > 1:
            fig = px.scatter_matrix(df[numeric_cols], title="Scatter Plot Matrix")

            if save_html:
                output_dir = create_output_directory(output_dir)
                fig.write_html(f"{output_dir}/scatter_matrix.html")
                print(f"💾 Scatter matrix saved: {output_dir}/scatter_matrix.html")
            else:
                fig.show()

        # Histogram's
        for col in numeric_cols:
            fig = px.histogram(df, x=col, title=f"Histogram - {col}")

            if save_html:
                output_dir = create_output_directory(output_dir)
                fig.write_html(f"{output_dir}/histogram_{col}.html")
                print(f"💾 Histogram saved: {output_dir}/histogram_{col}.html")
            else:
                fig.show()

    except ImportError:
        print("⚠️  Plotly not found. Interactive plots cannot be created.")
        print("   Installation: pip install plotly")


def create_output_directory(output_dir: str) -> str:
    """
    Create output directory.

    Parameters
    ----------
    output_dir : str
        Path to create

    Returns
    -------
    str
        Created path
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Output directory created: {output_dir}")
    return output_dir


class LazyAnalyzer:
    """
    Lazy evaluation for data analysis.

    This class performs analyses only when needed and caches results.
    This makes repeated analyses much faster.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialize LazyAnalyzer.

        Parameters
        ----------
        df : pd.DataFrame
            Dataset to analyze
        """
        self.df = df
        self._results: Dict[str, Any] = {}
        self._data_info: Optional[Dict[str, Any]] = None
        self._numeric_analysis: Optional[Dict[str, Any]] = None
        self._categorical_analysis: Optional[Dict[str, Any]] = None
        self._correlation_matrix: Optional[pd.DataFrame] = None
        self._outliers: Optional[Dict[str, Any]] = None

        # Determine column types without copying the dataframe
        self._numeric_cols = df.select_dtypes(include=[np.number]).columns
        self._categorical_cols = df.select_dtypes(
            include=["object", "category"]
        ).columns

        print("🚀 LazyAnalyzer initialized!")
        print(f"   📊 Dataset size: {df.shape}")
        memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
        print(f"   💾 Memory usage: {memory_mb:.2f} MB")

    def get_data_info(self) -> Dict[str, Any]:
        """Get general dataset information (lazy)"""
        if self._data_info is None:
            print("🔍 Calculating dataset information...")
            self._data_info = get_data_info(self.df)
        return self._data_info

    def get_numeric_analysis(self) -> Dict[str, Any]:
        """Get numeric analysis results (lazy)"""
        if self._numeric_analysis is None:
            print("🔢 Performing numeric analysis...")
            if len(self._numeric_cols) > 0:
                self._numeric_analysis = analyze_numeric(
                    self.df[self._numeric_cols], show_plots=False
                )
            else:
                self._numeric_analysis = {}
        return self._numeric_analysis

    def get_categorical_analysis(self) -> Dict[str, Any]:
        """Get categorical analysis results (lazy)"""
        if self._categorical_analysis is None:
            print("🏷️  Performing categorical analysis...")
            if len(self._categorical_cols) > 0:
                self._categorical_analysis = analyze_categorical(
                    self.df[self._categorical_cols], show_plots=False
                )
            else:
                self._categorical_analysis = {}
        return self._categorical_analysis

    def get_correlation_matrix(self) -> pd.DataFrame:
        """Get correlation matrix (lazy)"""
        if self._correlation_matrix is None:
            print("📊 Calculating correlation matrix...")
            if len(self._numeric_cols) > 1:
                # Calculate correlation
                self._correlation_matrix = self.df[self._numeric_cols].corr()
            else:
                self._correlation_matrix = pd.DataFrame()
        return self._correlation_matrix

    def get_outliers(
        self, method: str = "iqr", threshold: float = 1.5
    ) -> Dict[str, Any]:
        """Get outliers (lazy)"""
        if self._outliers is None:
            print("⚠️  Detecting outliers...")
            if len(self._numeric_cols) > 0:
                self._outliers = detect_outliers(
                    self.df[self._numeric_cols], method=method
                )
            else:
                self._outliers = {}
        return self._outliers

    def compute(self) -> Dict[str, Any]:
        """Perform all analyses and return results"""
        print("🚀 Performing all analyses...")

        results = {
            "data_info": self.get_data_info(),
            "numeric_analysis": self.get_numeric_analysis(),
            "categorical_analysis": self.get_categorical_analysis(),
            "correlation_matrix": self.get_correlation_matrix(),
            "outliers": self.get_outliers(),
        }

        print("✅ All analyses completed!")
        return results

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all analyses"""
        print("📋 Performing all analyses for summary...")

        summary = {
            "data_info": self.get_data_info(),
            "numeric_analysis": self.get_numeric_analysis(),
            "categorical_analysis": self.get_categorical_analysis(),
            "correlation_matrix": self.get_correlation_matrix(),
            "outliers": self.get_outliers(),
        }

        return summary

    def show_plots(
        self, save_plots: bool = False, output_dir: str = "./quickinsights_output"
    ) -> None:
        """Display visualizations"""
        print("📈 Creating visualizations...")

        # Correlation matrix
        if len(self._numeric_cols) > 1:
            correlation_matrix(
                self.df[self._numeric_cols],
                save_plots=save_plots,
                output_dir=output_dir,
            )

        # Distribution plots
        if len(self._numeric_cols) > 0:
            distribution_plots(
                self.df[self._numeric_cols],
                save_plots=save_plots,
                output_dir=output_dir,
            )

    def get_cache_status(self) -> Dict[str, bool]:
        """Show cache status"""
        status = {
            "data_info": self._data_info is not None,
            "numeric_analysis": self._numeric_analysis is not None,
            "categorical_analysis": self._categorical_analysis is not None,
            "correlation_matrix": self._correlation_matrix is not None,
            "outliers": self._outliers is not None,
        }

        print("📊 Cache Status:")
        for key, cached in status.items():
            status_icon = "✅" if cached else "⏳"
            cache_text = "Cached" if cached else "Not yet calculated"
            print(f"   {status_icon} {key}: {cache_text}")

        return status


    def clear_cache(self) -> None:
    
        """Clear cache"""
        self._results = {}
        self._data_info = None
        self._numeric_analysis = None
        self._categorical_analysis = None
        self._correlation_matrix = None
        self._outliers = None
        print("🗑️  Cache cleared!")
