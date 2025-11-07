"""
Streaming Analysis Module for QuickInsights

This module provides memory-efficient streaming analysis for large datasets
by processing data in chunks and aggregating results incrementally.
"""

import logging
import gc
from typing import Dict, List, Any, Optional, Iterator, Union
from pathlib import Path
import pandas as pd
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)


class StreamingAggregator:
    """
    Aggregator for streaming statistics calculation.
    
    Uses online algorithms for incremental computation of statistics:
    - Mean: Welford's online algorithm
    - Variance: Welford's online algorithm
    - Min/Max: Incremental updates
    - Quantiles: Approximate using reservoir sampling (future enhancement)
    """
    
    def __init__(self, max_categorical_values: int = 1000):
        """
        Initialize StreamingAggregator.
        
        Parameters
        ----------
        max_categorical_values : int
            Maximum number of unique values to track per categorical column.
            Prevents memory explosion for high-cardinality columns.
        """
        self.count = defaultdict(int)  # Count per column
        self.sum = defaultdict(float)
        self.min = {}
        self.max = {}
        self.mean = defaultdict(float)
        self.m2 = defaultdict(float)  # Sum of squared differences from mean (for variance)
        self.missing_count = defaultdict(int)
        self.value_counts = defaultdict(lambda: defaultdict(int))  # For categorical
        self.max_categorical_values = max_categorical_values
        self.total_rows = 0
    
    def update(self, chunk: pd.DataFrame) -> None:
        """Update aggregator with a new chunk."""
        self.total_rows += len(chunk)
        
        # Process numeric columns
        numeric_cols = chunk.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            col_data = chunk[col].dropna()
            
            if len(col_data) == 0:
                self.missing_count[col] += len(chunk)
                continue
            
            # Update missing count (use scalar)
            missing_scalar = int(chunk[col].isna().sum())
            self.missing_count[col] += missing_scalar
            
            # Update sum (convert to scalar immediately)
            col_sum = float(col_data.sum())
            self.sum[col] += col_sum
            
            # Update min/max (convert to scalar immediately)
            chunk_min = float(col_data.min())
            chunk_max = float(col_data.max())
            
            if col not in self.min:
                self.min[col] = chunk_min
                self.max[col] = chunk_max
            else:
                self.min[col] = min(self.min[col], chunk_min)
                self.max[col] = max(self.max[col], chunk_max)
            
            # Welford's online algorithm for mean and variance
            chunk_count = len(col_data)
            old_count = self.count[col]
            old_mean = self.mean[col] if old_count > 0 else 0.0
            
            total_count = old_count + chunk_count
            if total_count > 0:
                new_mean = (old_mean * old_count + col_sum) / total_count
                
                # Update M2 for variance calculation (avoid pandas Series operations)
                if old_count > 0:
                    # Calculate variance incrementally using scalar operations
                    # M2_new = M2_old + sum((x - old_mean) * (x - new_mean))
                    # Use numpy operations for efficiency, but convert to scalar immediately
                    variance_update = float(((col_data - old_mean) * (col_data - new_mean)).sum())
                    self.m2[col] += variance_update
                else:
                    # First chunk - calculate initial variance
                    self.m2[col] = float(((col_data - new_mean) ** 2).sum())
                
                self.mean[col] = new_mean
                self.count[col] = total_count
            
            # Explicitly delete intermediate Series to free memory
            del col_data
        
        # Process categorical columns
        categorical_cols = chunk.select_dtypes(include=["object", "category"]).columns
        for col in categorical_cols:
            col_data = chunk[col].dropna()
            
            # Update missing count (use scalar)
            missing_scalar = int(chunk[col].isna().sum())
            self.missing_count[col] += missing_scalar
            
            # Update value counts with memory limit
            value_counts = col_data.value_counts()
            
            # Limit number of unique values to prevent memory explosion
            current_unique_count = len(self.value_counts[col])
            
            if current_unique_count < self.max_categorical_values:
                # Still have room, add all values
                for value, count in value_counts.items():
                    # Convert value to string to avoid pandas object references
                    value_str = str(value)
                    self.value_counts[col][value_str] += int(count)
                    
                    # Check if we've exceeded limit
                    if len(self.value_counts[col]) >= self.max_categorical_values:
                        break
            else:
                # Already at limit, only update existing values
                for value, count in value_counts.items():
                    value_str = str(value)
                    if value_str in self.value_counts[col]:
                        self.value_counts[col][value_str] += int(count)
            
            # Explicitly delete intermediate Series
            del col_data, value_counts
    
    def get_numeric_stats(self) -> Dict[str, Dict[str, float]]:
        """Get aggregated numeric statistics."""
        stats = {}
        
        for col in self.sum.keys():
            if col in self.mean:
                count = self.count.get(col, 0)
                variance = self.m2[col] / count if count > 1 else 0.0
                std = np.sqrt(variance) if variance > 0 else 0.0
                
                stats[col] = {
                    "count": int(count),
                    "mean": float(self.mean[col]),
                    "std": float(std),
                    "min": float(self.min.get(col, 0)),
                    "max": float(self.max.get(col, 0)),
                    "sum": float(self.sum[col]),
                    "missing_count": int(self.missing_count.get(col, 0)),
                    "missing_percentage": (self.missing_count.get(col, 0) / self.total_rows * 100) if self.total_rows > 0 else 0.0
                }
        
        return stats
    
    def get_categorical_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get aggregated categorical statistics."""
        stats = {}
        
        for col, value_counts in self.value_counts.items():
            total_count = sum(value_counts.values())
            missing_count = self.missing_count.get(col, 0)
            
            if total_count == 0:
                continue
            
            # Find most common
            most_common_value = max(value_counts.items(), key=lambda x: x[1])
            
            stats[col] = {
                "count": int(total_count),
                "unique_values": len(value_counts),
                "most_common": most_common_value[0],
                "most_common_count": int(most_common_value[1]),
                "most_common_percentage": (most_common_value[1] / total_count * 100) if total_count > 0 else 0.0,
                "missing_count": int(missing_count),
                "missing_percentage": (missing_count / self.total_rows * 100) if self.total_rows > 0 else 0.0,
                "top_values": dict(sorted(value_counts.items(), key=lambda x: x[1], reverse=True)[:10])
            }
        
        return stats


class StreamingAnalyzer:
    """
    Memory-efficient streaming analyzer for large datasets.
    
    Processes data in chunks and aggregates statistics incrementally,
    allowing analysis of datasets larger than available RAM.
    """
    
    def __init__(self, chunksize: int = 100_000):
        """
        Initialize StreamingAnalyzer.
        
        Parameters
        ----------
        chunksize : int
            Number of rows to process in each chunk
        """
        self.chunksize = chunksize
        self.aggregator = StreamingAggregator()
    
    def analyze(
        self,
        data_source: Union[str, Path, Iterator[pd.DataFrame]],
        show_plots: bool = False,
        save_plots: bool = False,
        output_dir: str = "./quickinsights_output",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Analyze data using streaming approach.
        
        Parameters
        ----------
        data_source : str, Path, or Iterator[pd.DataFrame]
            File path or iterator of DataFrames
        show_plots : bool
            Whether to display plots (not recommended for streaming)
        save_plots : bool
            Whether to save plots
        output_dir : str
            Output directory for saved plots
        **kwargs
            Additional arguments for data loading
        
        Returns
        -------
        dict
            Analysis results
        """
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        logger.info(f"Starting streaming analysis (chunksize={self.chunksize})")
        logger.info(f"Initial memory: {initial_memory:.2f} MB")
        
        # Reset aggregator
        self.aggregator = StreamingAggregator()
        
        # Get data iterator
        if isinstance(data_source, (str, Path)):
            from .io import load_data
            chunks = load_data(data_source, chunksize=self.chunksize, **kwargs)
        else:
            chunks = data_source
        
        # Process chunks
        chunk_count = 0
        total_rows = 0
        peak_memory = initial_memory
        
        try:
            for chunk in chunks:
                chunk_count += 1
                total_rows += len(chunk)
                
                # Update aggregator
                self.aggregator.update(chunk)
                
                # Explicitly delete chunk and force garbage collection
                del chunk
                
                # Aggressive garbage collection every 10 chunks to prevent memory buildup
                if chunk_count % 10 == 0:
                    gc.collect()
                
                # Monitor memory
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                peak_memory = max(peak_memory, current_memory)
                
                if chunk_count % 10 == 0:
                    logger.info(f"Processed {chunk_count} chunks, {total_rows:,} rows, "
                              f"Memory: {current_memory:.2f} MB")
            
            # Final garbage collection before generating results
            gc.collect()
            
            # Get aggregated results
            numeric_stats = self.aggregator.get_numeric_stats()
            categorical_stats = self.aggregator.get_categorical_stats()
            
            # Store missing values count before clearing aggregator
            total_missing_values = sum(self.aggregator.missing_count.values())
            
            # Clear aggregator's internal structures to free memory
            # (results are already extracted, so we can clear)
            self.aggregator = None
            
            # Final garbage collection after clearing aggregator
            gc.collect()
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Compile results
            results = {
                "dataset_info": {
                    "rows": total_rows,
                    "columns": len(numeric_stats) + len(categorical_stats),
                    "numeric_columns": len(numeric_stats),
                    "categorical_columns": len(categorical_stats),
                    "chunks_processed": chunk_count,
                    "chunksize": self.chunksize,
                    "memory_initial_mb": initial_memory,
                    "memory_peak_mb": peak_memory,
                    "memory_final_mb": final_memory,
                    "memory_used_mb": peak_memory - initial_memory,
                    "total_missing_values": total_missing_values
                },
                "numeric_analysis": numeric_stats,
                "categorical_analysis": categorical_stats
            }
            
            logger.info(f"Streaming analysis completed: {total_rows:,} rows, "
                       f"{chunk_count} chunks, Peak memory: {peak_memory:.2f} MB")
            
            return results
            
        except Exception as e:
            logger.error(f"Streaming analysis failed: {e}")
            raise


def analyze_streaming(
    file_path: Union[str, Path],
    chunksize: int = 100_000,
    show_plots: bool = False,
    save_plots: bool = False,
    output_dir: str = "./quickinsights_output",
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function for streaming analysis.
    
    Parameters
    ----------
    file_path : str or Path
        Path to data file
    chunksize : int
        Number of rows per chunk (default: 100,000)
    show_plots : bool
        Whether to display plots
    save_plots : bool
        Whether to save plots
    output_dir : str
        Output directory
    **kwargs
        Additional arguments for data loading
    
    Returns
    -------
    dict
        Analysis results
    
    Examples
    --------
    >>> from quickinsights.streaming import analyze_streaming
    >>> result = analyze_streaming('large_data.csv', chunksize=50000)
    """
    analyzer = StreamingAnalyzer(chunksize=chunksize)
    return analyzer.analyze(
        file_path,
        show_plots=show_plots,
        save_plots=save_plots,
        output_dir=output_dir,
        **kwargs
    )

