"""
Smart Data Loader Module for QuickInsights

This module provides intelligent data loading with automatic format optimization:
- Automatic format detection and preference for faster formats (Parquet over CSV)
- Automatic conversion and caching of slow formats
- Seamless integration with existing code
"""

import os
import time
import hashlib
from pathlib import Path
from typing import Union, Optional, Dict, Any, Iterator
import logging

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class SmartDataLoader:
    """
    Intelligent data loader that automatically prefers faster formats.
    
    Features:
    - Automatically checks for Parquet version when CSV is requested
    - Converts and caches slow formats to fast formats
    - Maintains backward compatibility
    - Performance-optimized I/O operations
    """
    
    # Format performance mapping (higher = faster)
    FORMAT_PERFORMANCE = {
        '.parquet': 100,
        '.feather': 95,
        '.h5': 90,
        '.csv': 10,
        '.xlsx': 8,
        '.xls': 7,
        '.json': 5,
    }
    
    # Format conversion mapping (slow -> fast)
    FORMAT_CONVERSION = {
        '.csv': '.parquet',
        '.xlsx': '.parquet',
        '.xls': '.parquet',
        '.json': '.parquet',
    }
    
    def __init__(
        self,
        enable_cache: bool = True,
        cache_dir: Optional[Union[str, Path]] = None,
        compression: str = 'snappy',
        verify_cache: bool = True
    ):
        """
        Initialize SmartDataLoader.
        
        Parameters
        ----------
        enable_cache : bool
            Enable automatic conversion and caching of slow formats
        cache_dir : str or Path, optional
            Directory for cached files. Defaults to same directory as source file
        compression : str
            Compression algorithm for Parquet files ('snappy', 'gzip', 'brotli', 'lz4')
        verify_cache : bool
            Verify cached file integrity by checking modification times
        """
        self.enable_cache = enable_cache
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.compression = compression
        self.verify_cache = verify_cache
        
        # Statistics
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'conversions': 0,
            'total_loads': 0,
            'time_saved_seconds': 0.0
        }
    
    def load(
        self,
        file_path: Union[str, Path],
        chunksize: Optional[int] = None,
        **kwargs
    ) -> Union[pd.DataFrame, 'Iterator[pd.DataFrame]']:
        """
        Load data from file with intelligent format optimization.
        
        This method:
        1. Checks if a faster format version exists (e.g., .parquet for .csv)
        2. Uses faster format if available and newer
        3. Optionally converts and caches slow formats to fast formats
        4. Falls back to original format if needed
        
        Parameters
        ----------
        file_path : str or Path
            Path to data file (supports CSV, Excel, JSON, Parquet, etc.)
        chunksize : int, optional
            If provided, returns an iterator of DataFrames instead of single DataFrame.
            Useful for processing large files in chunks to reduce memory usage.
        **kwargs
            Additional arguments passed to pandas read functions
        
        Returns
        -------
        pd.DataFrame or Iterator[pd.DataFrame]
            Loaded DataFrame or iterator of DataFrames if chunksize is provided
        
        Examples
        --------
        >>> loader = SmartDataLoader()
        >>> df = loader.load('data.csv')  # Automatically uses data.parquet if available
        >>> df = loader.load('data.xlsx')  # Converts and caches to data.parquet
        """
        file_path = Path(file_path)
        self.stats['total_loads'] += 1
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Chunked loading mode
        if chunksize is not None:
            return self._load_chunked(file_path, chunksize, **kwargs)
        
        # Check for faster format alternatives
        fast_format_path = self._find_fast_format(file_path)
        
        if fast_format_path and fast_format_path.exists():
            # Use fast format if it's newer or cache verification is disabled
            if not self.verify_cache or self._is_cache_valid(file_path, fast_format_path):
                logger.info(f"Using optimized format: {fast_format_path}")
                df = self._load_fast_format(fast_format_path, **kwargs)
                self.stats['cache_hits'] += 1
                return df
            else:
                logger.info(f"Cache outdated, reloading from source: {file_path}")
        
        # Load from original format
        start_time = time.perf_counter()
        df = self._load_original_format(file_path, **kwargs)
        load_time = time.perf_counter() - start_time
        
        # Convert and cache if enabled
        if self.enable_cache:
            cache_path = self._get_cache_path(file_path)
            if cache_path and cache_path.suffix != file_path.suffix:
                try:
                    self._convert_and_cache(df, file_path, cache_path)
                    self.stats['conversions'] += 1
                    logger.info(f"Cached optimized format: {cache_path}")
                except Exception as e:
                    logger.warning(f"Failed to cache file: {e}")
        
        self.stats['cache_misses'] += 1
        return df
    
    def _find_fast_format(self, file_path: Path) -> Optional[Path]:
        """Find faster format alternative for given file."""
        suffix = file_path.suffix.lower()
        
        if suffix not in self.FORMAT_CONVERSION:
            return None
        
        fast_suffix = self.FORMAT_CONVERSION[suffix]
        fast_path = file_path.with_suffix(fast_suffix)
        
        return fast_path
    
    def _is_cache_valid(self, source_path: Path, cache_path: Path) -> bool:
        """Check if cached file is valid (newer than source)."""
        if not cache_path.exists():
            return False
        
        source_mtime = source_path.stat().st_mtime
        cache_mtime = cache_path.stat().st_mtime
        
        return cache_mtime >= source_mtime
    
    def _get_cache_path(self, file_path: Path) -> Optional[Path]:
        """Get cache path for file."""
        suffix = file_path.suffix.lower()
        
        if suffix not in self.FORMAT_CONVERSION:
            return None
        
        fast_suffix = self.FORMAT_CONVERSION[suffix]
        
        if self.cache_dir:
            # Use custom cache directory
            cache_filename = file_path.stem + fast_suffix
            return self.cache_dir / cache_filename
        else:
            # Use same directory as source
            return file_path.with_suffix(fast_suffix)
    
    def _load_original_format(self, file_path: Path, **kwargs) -> pd.DataFrame:
        """Load data from original format."""
        suffix = file_path.suffix.lower()
        
        if suffix == '.csv':
            return pd.read_csv(file_path, **kwargs)
        elif suffix in ['.xlsx', '.xls']:
            return pd.read_excel(file_path, **kwargs)
        elif suffix == '.json':
            return pd.read_json(file_path, **kwargs)
        elif suffix == '.parquet':
            return pd.read_parquet(file_path, **kwargs)
        elif suffix == '.feather':
            return pd.read_feather(file_path, **kwargs)
        elif suffix in ['.h5', '.hdf5']:
            return pd.read_hdf(file_path, **kwargs)
        else:
            # Try CSV as fallback
            try:
                return pd.read_csv(file_path, **kwargs)
            except Exception:
                raise ValueError(f"Unsupported file format: {suffix}")
    
    def _load_fast_format(self, file_path: Path, **kwargs) -> pd.DataFrame:
        """Load data from fast format (Parquet, Feather, etc.)."""
        suffix = file_path.suffix.lower()
        
        if suffix == '.parquet':
            return pd.read_parquet(file_path, **kwargs)
        elif suffix == '.feather':
            return pd.read_feather(file_path, **kwargs)
        elif suffix in ['.h5', '.hdf5']:
            return pd.read_hdf(file_path, **kwargs)
        else:
            return pd.read_parquet(file_path, **kwargs)
    
    def _load_chunked(
        self,
        file_path: Path,
        chunksize: int,
        **kwargs
    ):
        """Load data in chunks (generator)."""
        suffix = file_path.suffix.lower()
        
        # Check for fast format first
        fast_format_path = self._find_fast_format(file_path)
        if fast_format_path and fast_format_path.exists():
            if not self.verify_cache or self._is_cache_valid(file_path, fast_format_path):
                logger.info(f"Using optimized format for chunked loading: {fast_format_path}")
                yield from self._load_fast_format_chunked(fast_format_path, chunksize, **kwargs)
                return
        
        # Load from original format in chunks
        if suffix == '.csv':
            for chunk in pd.read_csv(file_path, chunksize=chunksize, **kwargs):
                yield chunk
        elif suffix == '.parquet':
            # Parquet doesn't support chunksize directly, use iter_batches
            try:
                import pyarrow.parquet as pq
                parquet_file = pq.ParquetFile(file_path)
                for batch in parquet_file.iter_batches(batch_size=chunksize):
                    yield batch.to_pandas()
            except ImportError:
                # Fallback: read all and chunk
                df = pd.read_parquet(file_path, **kwargs)
                for i in range(0, len(df), chunksize):
                    yield df.iloc[i:i + chunksize]
        elif suffix in ['.xlsx', '.xls']:
            # Excel doesn't support chunksize, read all and chunk
            df = pd.read_excel(file_path, **kwargs)
            for i in range(0, len(df), chunksize):
                yield df.iloc[i:i + chunksize]
        elif suffix == '.json':
            # JSON doesn't support chunksize, read all and chunk
            df = pd.read_json(file_path, **kwargs)
            for i in range(0, len(df), chunksize):
                yield df.iloc[i:i + chunksize]
        else:
            # Fallback to CSV
            for chunk in pd.read_csv(file_path, chunksize=chunksize, **kwargs):
                yield chunk
    
    def _load_fast_format_chunked(
        self,
        file_path: Path,
        chunksize: int,
        **kwargs
    ):
        """Load fast format in chunks."""
        suffix = file_path.suffix.lower()
        
        if suffix == '.parquet':
            try:
                import pyarrow.parquet as pq
                parquet_file = pq.ParquetFile(file_path)
                for batch in parquet_file.iter_batches(batch_size=chunksize):
                    yield batch.to_pandas()
            except ImportError:
                # Fallback: read all and chunk
                df = pd.read_parquet(file_path, **kwargs)
                for i in range(0, len(df), chunksize):
                    yield df.iloc[i:i + chunksize]
        else:
            # Fallback to regular chunked loading
            yield from self._load_chunked(file_path, chunksize, **kwargs)
    
    def _convert_and_cache(
        self,
        df: pd.DataFrame,
        source_path: Path,
        cache_path: Path
    ) -> None:
        """Convert DataFrame to fast format and save to cache."""
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        suffix = cache_path.suffix.lower()
        
        if suffix == '.parquet':
            df.to_parquet(
                cache_path,
                compression=self.compression,
                index=False
            )
        elif suffix == '.feather':
            df.to_feather(cache_path)
        elif suffix in ['.h5', '.hdf5']:
            df.to_hdf(cache_path, key='data', mode='w')
        else:
            # Default to Parquet
            df.to_parquet(
                cache_path,
                compression=self.compression,
                index=False
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get loader statistics."""
        cache_hit_rate = (
            self.stats['cache_hits'] / self.stats['total_loads'] * 100
            if self.stats['total_loads'] > 0 else 0
        )
        
        return {
            **self.stats,
            'cache_hit_rate_percent': cache_hit_rate,
            'enable_cache': self.enable_cache,
            'compression': self.compression
        }
    
    def reset_stats(self) -> None:
        """Reset statistics."""
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'conversions': 0,
            'total_loads': 0,
            'time_saved_seconds': 0.0
        }


# Global instance for convenience
_default_loader = SmartDataLoader()


def load_data(
    file_path: Union[str, Path],
    enable_cache: bool = True,
    chunksize: Optional[int] = None,
    **kwargs
) -> Union[pd.DataFrame, Iterator[pd.DataFrame]]:
    """
    Convenience function to load data with smart format optimization.
    
    Parameters
    ----------
    file_path : str or Path
        Path to data file
    enable_cache : bool
        Enable automatic conversion and caching
    chunksize : int, optional
        If provided, returns an iterator of DataFrames for chunked processing
    **kwargs
        Additional arguments for pandas read functions
    
    Returns
    -------
    pd.DataFrame or Iterator[pd.DataFrame]
        Loaded DataFrame or iterator if chunksize is provided
    
    Examples
    --------
    >>> from quickinsights.io import load_data
    >>> df = load_data('data.csv')  # Automatically uses data.parquet if available
    >>> # Chunked loading
    >>> for chunk in load_data('large_data.csv', chunksize=10000):
    ...     process(chunk)
    """
    loader = SmartDataLoader(enable_cache=enable_cache)
    return loader.load(file_path, chunksize=chunksize, **kwargs)


def analyze_from_file(
    file_path: Union[str, Path],
    show_plots: bool = True,
    save_plots: bool = False,
    output_dir: str = "./quickinsights_output",
    enable_cache: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Load data from file and analyze it with smart format optimization.
    
    This function combines smart data loading with analysis, providing
    a seamless experience for file-based analysis.
    
    Parameters
    ----------
    file_path : str or Path
        Path to data file (CSV, Excel, JSON, Parquet, etc.)
    show_plots : bool
        Whether to display plots
    save_plots : bool
        Whether to save plots
    output_dir : str
        Output directory for saved plots
    enable_cache : bool
        Enable automatic format conversion and caching
    **kwargs
        Additional arguments for pandas read functions
    
    Returns
    -------
    dict
        Analysis results
    
    Examples
    --------
    >>> from quickinsights.io import analyze_from_file
    >>> result = analyze_from_file('data.csv')  # Uses Parquet if available
    """
    from .analysis.basic_analysis import analyze as analyze_data
    
    # Load data with smart loader
    df = load_data(file_path, enable_cache=enable_cache, **kwargs)
    
    # Perform analysis
    return analyze_data(df, show_plots=show_plots, save_plots=save_plots, output_dir=output_dir)

