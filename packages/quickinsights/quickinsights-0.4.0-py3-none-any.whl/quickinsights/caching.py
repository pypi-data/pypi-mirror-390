"""
Analysis Result Caching Module for QuickInsights

This module provides caching functionality for analysis results to avoid
recomputing expensive analyses on unchanged files.
"""

import os
import json
import hashlib
import pickle
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class AnalysisCache:
    """
    Cache manager for analysis results.
    
    Caches analysis results to disk to avoid recomputation when:
    - Same file is analyzed with same parameters
    - File hasn't been modified since last analysis
    """
    
    def __init__(self, cache_dir: Optional[Union[str, Path]] = None):
        """
        Initialize AnalysisCache.
        
        Parameters
        ----------
        cache_dir : str or Path, optional
            Directory for cache files. Defaults to .quickinsights_cache in user's home directory.
        """
        if cache_dir is None:
            # Use .quickinsights_cache in current working directory
            cache_dir = Path.cwd() / ".quickinsights_cache"
        else:
            cache_dir = Path(cache_dir)
        
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.debug(f"Cache directory: {self.cache_dir}")
    
    def _generate_cache_key(
        self,
        file_path: Union[str, Path],
        params: Dict[str, Any]
    ) -> str:
        """
        Generate a unique cache key for analysis parameters.
        
        Parameters
        ----------
        file_path : str or Path
            Path to the data file
        params : dict
            Analysis parameters (chunksize, show_plots, etc.)
        
        Returns
        -------
        str
            Cache key (hex hash)
        """
        file_path = Path(file_path).resolve()
        
        # Get file modification time
        try:
            mtime = file_path.stat().st_mtime
        except (OSError, FileNotFoundError):
            mtime = 0
        
        # Create a unique string from file path, mtime, and parameters
        key_components = [
            str(file_path),
            str(mtime),
            json.dumps(params, sort_keys=True)
        ]
        key_string = "|".join(key_components)
        
        # Generate hash
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()
        
        return key_hash
    
    def _get_cache_file_path(self, cache_key: str) -> Path:
        """Get the full path to cache file."""
        return self.cache_dir / f"{cache_key}.cache"
    
    def _get_metadata_file_path(self, cache_key: str) -> Path:
        """Get the full path to metadata file."""
        return self.cache_dir / f"{cache_key}.meta"
    
    def get(
        self,
        file_path: Union[str, Path],
        params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached analysis result if available and valid.
        
        Parameters
        ----------
        file_path : str or Path
            Path to the data file
        params : dict
            Analysis parameters
        
        Returns
        -------
        dict or None
            Cached result if available and valid, None otherwise
        """
        file_path = Path(file_path).resolve()
        
        # Check if file exists
        if not file_path.exists():
            return None
        
        # Generate cache key
        cache_key = self._generate_cache_key(file_path, params)
        cache_file = self._get_cache_file_path(cache_key)
        metadata_file = self._get_metadata_file_path(cache_key)
        
        # Check if cache exists
        if not cache_file.exists() or not metadata_file.exists():
            return None
        
        # Verify file hasn't changed
        try:
            current_mtime = file_path.stat().st_mtime
            
            # Load metadata
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            cached_mtime = metadata.get('file_mtime', 0)
            
            if abs(current_mtime - cached_mtime) > 0.1:  # Allow small floating point differences
                logger.debug(f"Cache invalidated: file modified (cache: {cached_mtime}, current: {current_mtime})")
                return None
            
        except (OSError, json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Error validating cache: {e}")
            return None
        
        # Load cached result
        try:
            with open(cache_file, 'rb') as f:
                result = pickle.load(f)
            
            logger.info(f"Cache hit for {file_path.name} (key: {cache_key[:8]}...)")
            return result
            
        except (pickle.UnpicklingError, IOError, EOFError) as e:
            logger.warning(f"Error loading cache: {e}")
            # Remove corrupted cache
            try:
                cache_file.unlink()
                metadata_file.unlink()
            except OSError:
                pass
            return None
    
    def set(
        self,
        file_path: Union[str, Path],
        params: Dict[str, Any],
        result: Dict[str, Any]
    ) -> None:
        """
        Cache analysis result.
        
        Parameters
        ----------
        file_path : str or Path
            Path to the data file
        params : dict
            Analysis parameters
        result : dict
            Analysis result to cache
        """
        file_path = Path(file_path).resolve()
        
        if not file_path.exists():
            logger.warning(f"Cannot cache result for non-existent file: {file_path}")
            return
        
        # Generate cache key
        cache_key = self._generate_cache_key(file_path, params)
        cache_file = self._get_cache_file_path(cache_key)
        metadata_file = self._get_metadata_file_path(cache_key)
        
        try:
            # Get file mtime
            mtime = file_path.stat().st_mtime
            
            # Save result
            with open(cache_file, 'wb') as f:
                pickle.dump(result, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Save metadata
            metadata = {
                'file_path': str(file_path),
                'file_mtime': mtime,
                'cache_key': cache_key,
                'cached_at': datetime.now().isoformat(),
                'params': params
            }
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Cached result for {file_path.name} (key: {cache_key[:8]}...)")
            
        except (OSError, IOError, pickle.PicklingError) as e:
            logger.warning(f"Error caching result: {e}")
    
    def invalidate(self, file_path: Union[str, Path]) -> int:
        """
        Invalidate all cache entries for a given file.
        
        Parameters
        ----------
        file_path : str or Path
            Path to the data file
        
        Returns
        -------
        int
            Number of cache entries invalidated
        """
        file_path = Path(file_path).resolve()
        invalidated = 0
        
        # Find all cache files for this file
        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                metadata_file = cache_file.with_suffix('.meta')
                if not metadata_file.exists():
                    continue
                
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                cached_file_path = metadata.get('file_path')
                if cached_file_path and Path(cached_file_path).resolve() == file_path:
                    cache_file.unlink()
                    metadata_file.unlink()
                    invalidated += 1
                    
            except (json.JSONDecodeError, OSError, KeyError):
                continue
        
        if invalidated > 0:
            logger.info(f"Invalidated {invalidated} cache entries for {file_path.name}")
        
        return invalidated
    
    def clear(self) -> int:
        """
        Clear all cache entries.
        
        Returns
        -------
        int
            Number of cache entries cleared
        """
        cleared = 0
        
        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                cache_file.unlink()
                metadata_file = cache_file.with_suffix('.meta')
                if metadata_file.exists():
                    metadata_file.unlink()
                cleared += 1
            except OSError:
                pass
        
        logger.info(f"Cleared {cleared} cache entries")
        return cleared
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns
        -------
        dict
            Cache statistics
        """
        cache_files = list(self.cache_dir.glob("*.cache"))
        total_size = sum(f.stat().st_size for f in cache_files if f.exists())
        
        return {
            'cache_dir': str(self.cache_dir),
            'num_entries': len(cache_files),
            'total_size_bytes': total_size,
            'total_size_mb': total_size / 1024 / 1024
        }


# Global cache instance
_global_cache: Optional[AnalysisCache] = None


def get_cache(cache_dir: Optional[Union[str, Path]] = None) -> AnalysisCache:
    """
    Get or create global cache instance.
    
    Parameters
    ----------
    cache_dir : str or Path, optional
        Custom cache directory
    
    Returns
    -------
    AnalysisCache
        Global cache instance
    """
    global _global_cache
    
    if _global_cache is None or cache_dir is not None:
        _global_cache = AnalysisCache(cache_dir=cache_dir)
    
    return _global_cache


def cached_analysis(
    cache_enabled: bool = True,
    cache_dir: Optional[Union[str, Path]] = None
):
    """
    Decorator for caching analysis results.
    
    Parameters
    ----------
    cache_enabled : bool
        Whether caching is enabled
    cache_dir : str or Path, optional
        Custom cache directory
    
    Examples
    --------
    >>> @cached_analysis()
    ... def analyze_file(file_path, **kwargs):
    ...     # analysis code
    ...     return result
    """
    def decorator(func):
        cache = get_cache(cache_dir)
        
        def wrapper(file_path: Union[str, Path], *args, **kwargs):
            # Only cache file paths, not DataFrames
            if not isinstance(file_path, (str, Path)):
                return func(file_path, *args, **kwargs)
            
            if not cache_enabled:
                return func(file_path, *args, **kwargs)
            
            # Build params dict
            import inspect
            sig = inspect.signature(func)
            bound = sig.bind(file_path, *args, **kwargs)
            bound.apply_defaults()
            
            # Extract relevant parameters (exclude file_path)
            params = {k: v for k, v in bound.arguments.items() if k != 'file_path'}
            
            # Try to get from cache
            cached_result = cache.get(file_path, params)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(file_path, *args, **kwargs)
            cache.set(file_path, params, result)
            
            return result
        
        return wrapper
    
    return decorator

