"""
QuickInsights - Advanced Memory Management System v2

This module provides comprehensive memory management features including:
- Real-time memory profiling and monitoring
- Intelligent cache management with size limits
- Memory leak detection and prevention
- Weak references and garbage collection optimization
"""

import psutil
import gc
import time
import threading
import logging
import weakref
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from contextlib import contextmanager
from collections import OrderedDict
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MemorySnapshot:
    """Memory usage snapshot at a specific point in time"""

    timestamp: float
    memory_rss: int  # Resident Set Size in bytes
    memory_vms: int  # Virtual Memory Size in bytes
    memory_percent: float
    cpu_percent: float
    gc_stats: Dict[str, Any]
    memory_trend: str = "stable"


@dataclass
class MemoryAlert:
    """Memory alert information"""

    timestamp: float
    alert_type: str
    message: str
    memory_usage_mb: float
    threshold_mb: float
    severity: str


class MemoryProfiler:
    """Real-time memory profiling and monitoring system"""

    def __init__(self, alert_threshold_mb: float = 100.0, leak_threshold: float = 0.1):
        self.process = psutil.Process()
        self.alert_threshold = alert_threshold_mb * 1024 * 1024  # Convert to bytes
        self.leak_threshold = leak_threshold  # 10% increase threshold
        self.snapshots: List[MemorySnapshot] = []
        self.alerts: List[MemoryAlert] = []
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.logger = logging.getLogger(__name__)
        self._lock = threading.RLock()  # Thread safety

        # Memory leak detection
        self.memory_trends = []
        self.leak_detection_enabled = True

        # Performance tracking
        self.performance_metrics = {
            "peak_memory": 0,
            "average_memory": 0,
            "memory_variance": 0,
            "gc_frequency": 0,
            "memory_growth_rate": 0,
            "leak_detection_count": 0,
            "cleanup_operations": 0,
        }

    def start_monitoring(self, interval: float = 1.0):
        """Start continuous memory monitoring"""
        if self.monitoring_active:
            self.logger.warning("Memory monitoring already active")
            return

        # Validate interval to prevent negative values
        if interval <= 0:
            self.logger.warning(f"Invalid interval {interval}s, using default 1.0s")
            interval = 1.0

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, args=(interval,), daemon=True
        )
        self.monitor_thread.start()
        self.logger.info(f"Memory monitoring started with {interval}s interval")

    def stop_monitoring(self):
        """Stop memory monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        self.logger.info("Memory monitoring stopped")

    def _monitor_loop(self, interval: float):
        """Main monitoring loop"""
        # Ensure interval is positive
        safe_interval = max(0.1, interval)  # Minimum 0.1 second
        
        while self.monitoring_active:
            try:
                snapshot = self._take_snapshot()
                self.snapshots.append(snapshot)

                # Update performance metrics
                self._update_performance_metrics()

                # Check for memory leaks
                if self.leak_detection_enabled:
                    self._check_memory_leak(snapshot)

                # Check for memory threshold alerts
                if snapshot.memory_rss > self.alert_threshold:
                    self._alert_high_memory(snapshot)

                # Garbage collection optimization
                self._optimize_garbage_collection(snapshot)

                time.sleep(safe_interval)
            except Exception as e:
                self.logger.error(f"Error in memory monitoring: {e}")
                time.sleep(safe_interval)

    def _take_snapshot(self) -> MemorySnapshot:
        """Take a memory usage snapshot"""
        memory_info = self.process.memory_info()
        cpu_percent = self.process.cpu_percent()

        # Get garbage collector statistics
        gc_stats = {
            "collections": gc.get_stats(),
            "counts": gc.get_count(),
            "thresholds": gc.get_threshold(),
        }

        # Calculate memory trend
        memory_trend = self._calculate_memory_trend()

        return MemorySnapshot(
            timestamp=time.time(),
            memory_rss=memory_info.rss,
            memory_vms=memory_info.vms,
            memory_percent=memory_info.rss / psutil.virtual_memory().total * 100,
            cpu_percent=cpu_percent,
            gc_stats=gc_stats,
            memory_trend=memory_trend,
        )

    def _calculate_memory_trend(self) -> str:
        """Calculate memory usage trend"""
        if len(self.snapshots) < 5:
            return "insufficient_data"

        # Get last 5 snapshots for trend analysis
        recent_snapshots = self.snapshots[-5:]
        memory_values = [s.memory_rss for s in recent_snapshots]

        if len(memory_values) >= 2:
            # Simple linear regression for trend
            x = np.arange(len(memory_values))
            slope = np.polyfit(x, memory_values, 1)[0]

            # Calculate percentage change
            if memory_values[0] > 0:
                percentage_change = (slope * len(memory_values)) / memory_values[0]

                if percentage_change > self.leak_threshold:
                    return "increasing"
                elif percentage_change < -self.leak_threshold:
                    return "decreasing"
                else:
                    return "stable"

        return "stable"

    def _check_memory_leak(self, snapshot: MemorySnapshot):
        """Check for potential memory leaks"""
        if len(self.snapshots) < 10:
            return

        # Calculate memory trend over last 10 snapshots
        recent_snapshots = self.snapshots[-10:]
        memory_values = [s.memory_rss for s in recent_snapshots]

        # Advanced leak detection using multiple methods
        leak_detected = False
        leak_reason = ""

        # Method 1: Linear trend analysis
        if len(memory_values) >= 5:
            x = np.arange(len(memory_values))
            slope = np.polyfit(x, memory_values, 1)[0]
            trend_percent = (
                (slope * len(memory_values)) / memory_values[0]
                if memory_values[0] > 0
                else 0
            )

            if trend_percent > self.leak_threshold:
                leak_detected = True
                leak_reason = f"Linear trend: {trend_percent:.2%} increase"

        # Method 2: Variance analysis
        if len(memory_values) >= 10:
            variance = np.var(memory_values)
            mean_memory = np.mean(memory_values)
            coefficient_of_variation = (
                np.sqrt(variance) / mean_memory if mean_memory > 0 else 0
            )

            if (
                coefficient_of_variation > 0.2
            ):  # High variance might indicate memory issues
                leak_detected = True
                leak_reason += f", High variance: {coefficient_of_variation:.2f}"

        # Method 3: Peak analysis
        peak_memory = max(memory_values)
        current_memory = memory_values[-1]
        if (
            peak_memory > current_memory * 1.5
        ):  # Significant drop might indicate cleanup
            leak_detected = False  # Recent cleanup detected

        if leak_detected:
            self._alert_memory_leak(snapshot, leak_reason)

    def _alert_high_memory(self, snapshot: MemorySnapshot):
        """Alert when memory usage exceeds threshold"""
        memory_mb = snapshot.memory_rss / 1024 / 1024
        threshold_mb = self.alert_threshold / 1024 / 1024

        alert = MemoryAlert(
            timestamp=snapshot.timestamp,
            alert_type="HIGH_MEMORY_USAGE",
            message=f"Memory usage {memory_mb:.1f}MB exceeds threshold {threshold_mb:.1f}MB",
            memory_usage_mb=memory_mb,
            threshold_mb=threshold_mb,
            severity="WARNING",
        )

        self.alerts.append(alert)
        self.logger.warning(f"⚠️ {alert.message}")

    def _alert_memory_leak(self, snapshot: MemorySnapshot, reason: str):
        """Alert when memory leak is detected"""
        alert = MemoryAlert(
            timestamp=snapshot.timestamp,
            alert_type="MEMORY_LEAK_DETECTED",
            message=f"Memory leak detected: {reason}",
            memory_usage_mb=snapshot.memory_rss / 1024 / 1024,
            threshold_mb=0,
            severity="CRITICAL",
        )

        self.alerts.append(alert)
        self.logger.warning(f"🚨 {alert.message}")

    def _optimize_garbage_collection(self, snapshot: MemorySnapshot):
        """Optimize garbage collection based on memory usage"""
        current_memory = snapshot.memory_rss
        memory_percent = snapshot.memory_percent

        # Clear old snapshots to prevent memory accumulation (thread-safe)
        with self._lock:
            if len(self.snapshots) > 100:
                self.snapshots = self.snapshots[-50:]  # Keep only last 50 snapshots
                
            # Clear old alerts
            if len(self.alerts) > 50:
                self.alerts = self.alerts[-25:]  # Keep only last 25 alerts

        # Trigger GC if memory usage is high
        if memory_percent > 80:
            collected = gc.collect()
            self.logger.info(
                f"Garbage collection triggered: {collected} objects collected, cache cleaned"
            )

        # Adjust GC thresholds based on memory pressure
        if memory_percent > 90:
            # Aggressive GC
            gc.set_threshold(100, 5, 5)
        elif memory_percent > 70:
            # Normal GC
            gc.set_threshold(700, 10, 10)
        else:
            # Conservative GC
            gc.set_threshold(700, 10, 10)

    def _update_performance_metrics(self):
        """Update performance metrics"""
        if not self.snapshots:
            return

        memory_values = [s.memory_rss for s in self.snapshots]

        self.performance_metrics.update(
            {
                "peak_memory": max(memory_values),
                "average_memory": np.mean(memory_values),
                "memory_variance": np.var(memory_values),
                "gc_frequency": len(
                    [s for s in self.snapshots if s.gc_stats["counts"][0] > 0]
                ),
            }
        )

    def get_memory_summary(self) -> Dict[str, Any]:
        """Get comprehensive memory usage summary"""
        if not self.snapshots:
            return {"error": "No memory snapshots available"}

        latest = self.snapshots[-1]
        peak = max(self.snapshots, key=lambda x: x.memory_rss)

        return {
            "current_memory_mb": latest.memory_rss / 1024 / 1024,
            "peak_memory_mb": peak.memory_rss / 1024 / 1024,
            "memory_trend": latest.memory_trend,
            "gc_stats": latest.gc_stats,
            "snapshots_count": len(self.snapshots),
            "monitoring_active": self.monitoring_active,
            "performance_metrics": self.performance_metrics,
            "alerts_count": len(self.alerts),
            "recent_alerts": [
                {
                    "timestamp": alert.timestamp,
                    "type": alert.alert_type,
                    "message": alert.message,
                    "severity": alert.severity,
                }
                for alert in self.alerts[-5:]  # Last 5 alerts
            ],
        }

    def export_memory_report(self, filepath: str = None) -> str:
        """Export detailed memory report"""
        if not filepath:
            filepath = f"memory_report_{int(time.time())}.json"

        import json

        report = {
            "summary": self.get_memory_summary(),
            "snapshots": [
                {
                    "timestamp": s.timestamp,
                    "memory_rss_mb": s.memory_rss / 1024 / 1024,
                    "memory_vms_mb": s.memory_vms / 1024 / 1024,
                    "memory_percent": s.memory_percent,
                    "cpu_percent": s.cpu_percent,
                    "memory_trend": s.memory_trend,
                }
                for s in self.snapshots
            ],
            "alerts": [
                {
                    "timestamp": a.timestamp,
                    "type": a.alert_type,
                    "message": a.message,
                    "severity": a.severity,
                }
                for a in self.alerts
            ],
        }

        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Memory report exported to {filepath}")
        return filepath
    
    def take_snapshot(self) -> MemorySnapshot:
        """Public method to take a memory snapshot"""
        snapshot = self._take_snapshot()
        with self._lock:
            self.snapshots.append(snapshot)
        return snapshot
    
    def get_current_snapshot(self) -> Optional[MemorySnapshot]:
        """Get the most recent memory snapshot"""
        if self.snapshots:
            return self.snapshots[-1]
        return self._take_snapshot()
    
    def optimize_memory(self) -> Dict[str, Any]:
        """Optimize memory usage by running garbage collection"""
        gc.collect()
        self.performance_metrics["cleanup_operations"] += 1
        
        # Get memory usage before and after
        if self.snapshots:
            before_mb = self.snapshots[-1].memory_rss / 1024 / 1024
        else:
            before_mb = 0
        
        snapshot = self._take_snapshot()
        after_mb = snapshot.memory_rss / 1024 / 1024
        
        return {
            "before_mb": before_mb,
            "after_mb": after_mb,
            "freed_mb": before_mb - after_mb,
            "success": True
        }
    
    def cleanup_memory(self):
        """Cleanup memory and optimize garbage collection"""
        gc.collect()
        self.performance_metrics["cleanup_operations"] += 1
        self.logger.info("Memory cleanup completed")


@contextmanager
def memory_profile(operation_name: str, profiler: MemoryProfiler):
    """Context manager for memory profiling of specific operations"""
    start_snapshot = profiler._take_snapshot()

    try:
        yield
    finally:
        end_snapshot = profiler._take_snapshot()

        memory_diff = end_snapshot.memory_rss - start_snapshot.memory_rss
        memory_diff_mb = memory_diff / 1024 / 1024

        profiler.logger.info(
            f"Memory profile for {operation_name}: "
            f"{memory_diff_mb:+.2f}MB "
            f"({start_snapshot.memory_rss / 1024 / 1024:.1f}MB -> "
            f"{end_snapshot.memory_rss / 1024 / 1024:.1f}MB)"
        )


class CacheEntry:
    """Individual cache entry with metadata"""

    def __init__(self, key: str, value: Any, ttl: Optional[float] = None):
        self.key = key
        self.value = value
        self.created_at = time.time()
        self.last_accessed = time.time()
        self.access_count = 0
        self.ttl = ttl  # Time to live in seconds
        self.size_estimate = self._estimate_size()

    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl

    def access(self):
        """Mark entry as accessed"""
        self.last_accessed = time.time()
        self.access_count += 1

    def get_age(self) -> float:
        """Get age of cache entry in seconds"""
        return time.time() - self.created_at

    def _estimate_size(self) -> int:
        """Estimate memory size of cache entry"""
        try:
            import sys

            return sys.getsizeof(self.value)
        except:
            return 1024  # Default estimate: 1KB


class IntelligentCache:
    """Advanced cache system with size limits and eviction policies"""

    def __init__(self, max_size: int = 1000, max_memory_mb: float = 100.0):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.weak_cache: weakref.WeakValueDictionary = weakref.WeakValueDictionary()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expirations": 0,
            "memory_usage_bytes": 0,
        }
        self.lock = threading.RLock()
        self.logger = logging.getLogger(__name__)

        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]

                # Check if expired
                if entry.is_expired():
                    del self.cache[key]
                    self.stats["expirations"] += 1
                    self.stats["misses"] += 1
                    self.stats["memory_usage_bytes"] -= entry.size_estimate
                    return None

                # Update access info
                entry.access()

                # Move to end (LRU behavior)
                self.cache.move_to_end(key)

                self.stats["hits"] += 1
                return entry.value

            self.stats["misses"] += 1
            return None

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """Set value in cache"""
        with self.lock:
            # Check if key already exists
            if key in self.cache:
                # Update existing entry
                old_entry = self.cache[key]
                self.stats["memory_usage_bytes"] -= old_entry.size_estimate

                entry = self.cache[key]
                entry.value = value
                entry.created_at = time.time()
                entry.ttl = ttl
                entry.access()
                entry.size_estimate = entry._estimate_size()
                self.stats["memory_usage_bytes"] += entry.size_estimate

                self.cache.move_to_end(key)
                return True

            # Create new entry
            entry = CacheEntry(key, value, ttl)

            # Check size limits
            if len(self.cache) >= self.max_size:
                self._evict_entries()

            # Check memory limits
            if (
                self.stats["memory_usage_bytes"] + entry.size_estimate
                > self.max_memory_bytes
            ):
                self._evict_memory_based()

            # Add to cache
            self.cache[key] = entry
            self.stats["memory_usage_bytes"] += entry.size_estimate

            return True

    def _evict_entries(self, count: int = 1):
        """Evict entries based on LRU policy"""
        evicted = 0
        for _ in range(min(count, len(self.cache))):
            if self.cache:
                key, entry = self.cache.popitem(last=False)
                evicted += 1
                self.stats["evictions"] += 1
                self.stats["memory_usage_bytes"] -= entry.size_estimate

        self.logger.info(f"Evicted {evicted} entries from cache")

    def _evict_memory_based(self):
        """Evict entries based on memory usage"""
        # Sort entries by access count and age (least valuable first)
        entries = [(key, entry) for key, entry in self.cache.items()]
        entries.sort(key=lambda x: (x[1].access_count, x[1].get_age()))

        # Evict least valuable entries
        evicted = 0
        while self.stats["memory_usage_bytes"] > self.max_memory_bytes and entries:
            key, entry = entries.pop(0)
            del self.cache[key]
            evicted += 1
            self.stats["evictions"] += 1
            self.stats["memory_usage_bytes"] -= entry.size_estimate

        self.logger.info(f"Memory-based eviction: {evicted} entries removed")

    def _cleanup_loop(self):
        """Background cleanup loop"""
        while True:
            try:
                time.sleep(60)  # Cleanup every minute
                self._cleanup_expired()
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")

    def _cleanup_expired(self):
        """Remove expired entries"""
        with self.lock:
            expired_keys = [
                key for key, entry in self.cache.items() if entry.is_expired()
            ]

            for key in expired_keys:
                entry = self.cache[key]
                del self.cache[key]
                self.stats["expirations"] += 1
                self.stats["memory_usage_bytes"] -= entry.size_estimate

            if expired_keys:
                self.logger.info(f"Cleaned up {len(expired_keys)} expired entries")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            hit_rate = (
                (self.stats["hits"] / (self.stats["hits"] + self.stats["misses"]))
                if (self.stats["hits"] + self.stats["misses"]) > 0
                else 0
            )

            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "memory_usage_mb": self.stats["memory_usage_bytes"] / 1024 / 1024,
                "max_memory_mb": self.max_memory_bytes / 1024 / 1024,
                "hit_rate": hit_rate,
                "stats": self.stats.copy(),
            }

    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.stats["memory_usage_bytes"] = 0
            self.logger.info("Cache cleared")

    def resize(self, new_max_size: int):
        """Resize cache to new maximum size"""
        with self.lock:
            self.max_size = new_max_size
            if len(self.cache) > new_max_size:
                self._evict_entries(len(self.cache) - new_max_size)
            self.logger.info(f"Cache resized to {new_max_size} entries")


# Convenience functions
def create_memory_profiler(alert_threshold_mb: float = 100.0) -> MemoryProfiler:
    """Create and configure a memory profiler"""
    return MemoryProfiler(alert_threshold_mb)


def create_intelligent_cache(
    max_size: int = 1000, max_memory_mb: float = 100.0
) -> IntelligentCache:
    """Create and configure an intelligent cache"""
    return IntelligentCache(max_size, max_memory_mb)


def get_memory_usage() -> Dict[str, float]:
    """Get current memory usage information"""
    process = psutil.Process()
    memory_info = process.memory_info()

    return {
        "rss_mb": memory_info.rss / 1024 / 1024,
        "vms_mb": memory_info.vms / 1024 / 1024,
        "percent": memory_info.rss / psutil.virtual_memory().total * 100,
    }
