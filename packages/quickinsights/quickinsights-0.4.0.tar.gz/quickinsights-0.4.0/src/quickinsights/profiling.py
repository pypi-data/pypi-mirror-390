"""
Performance Profiling and Bottleneck Detection for QuickInsights

Provides comprehensive profiling capabilities to identify performance bottlenecks
and optimization opportunities.
"""

import cProfile
import pstats
import io
import time
import functools
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
import json
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@dataclass
class FunctionProfile:
    """Profile information for a single function"""
    name: str
    ncalls: int
    tottime: float
    cumtime: float
    callers: List[str] = field(default_factory=list)
    percentage: float = 0.0


@dataclass
class ProfilingReport:
    """Comprehensive profiling report"""
    total_time: float
    functions: List[FunctionProfile]
    bottlenecks: List[FunctionProfile]
    recommendations: List[str]
    timestamp: str


class CodeProfiler:
    """Code profiler for bottleneck detection"""
    
    def __init__(self):
        self.profiler = cProfile.Profile()
        self.profiles: List[ProfilingReport] = []
    
    @contextmanager
    def profile(self, output_file: Optional[str] = None):
        """Context manager for profiling code blocks"""
        self.profiler.enable()
        try:
            yield
        finally:
            self.profiler.disable()
            
            if output_file:
                self.profiler.dump_stats(output_file)
    
    def profile_function(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """Profile a function execution"""
        self.profiler.enable()
        try:
            result = func(*args, **kwargs)
        finally:
            self.profiler.disable()
        
        return self._analyze_profile(result)
    
    def _analyze_profile(self, result: Any) -> Dict[str, Any]:
        """Analyze profiling data"""
        stream = io.StringIO()
        stats = pstats.Stats(self.profiler, stream=stream)
        stats.sort_stats('cumulative')
        
        # Get statistics
        stats.print_stats(50)  # Top 50 functions
        stats_output = stream.getvalue()
        
        # Parse function statistics
        functions = []
        total_time = 0.0
        
        for line in stats_output.split('\n'):
            if line.strip() and 'function' not in line.lower() and 'ncalls' not in line:
                parts = line.split()
                if len(parts) >= 5:
                    try:
                        ncalls = parts[0]
                        tottime = float(parts[1]) if parts[1] != '-' else 0.0
                        cumtime = float(parts[2]) if parts[2] != '-' else 0.0
                        func_name = ' '.join(parts[5:]) if len(parts) > 5 else parts[-1]
                        
                        functions.append(FunctionProfile(
                            name=func_name,
                            ncalls=ncalls,
                            tottime=tottime,
                            cumtime=cumtime
                        ))
                        
                        total_time = max(total_time, cumtime)
                    except (ValueError, IndexError):
                        continue
        
        # Calculate percentages
        for func in functions:
            if total_time > 0:
                func.percentage = (func.cumtime / total_time) * 100
        
        # Identify bottlenecks (>10% of total time)
        bottlenecks = [
            func for func in functions
            if func.percentage > 10.0
        ]
        
        # Generate recommendations
        recommendations = self._generate_recommendations(functions, bottlenecks)
        
        report = ProfilingReport(
            total_time=total_time,
            functions=functions[:20],  # Top 20
            bottlenecks=bottlenecks,
            recommendations=recommendations,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        self.profiles.append(report)
        
        return {
            "result": result,
            "report": report,
            "stats_output": stats_output
        }
    
    def _generate_recommendations(
        self,
        functions: List[FunctionProfile],
        bottlenecks: List[FunctionProfile]
    ) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Check for pandas operations
        pandas_ops = [
            f for f in functions
            if 'pandas' in f.name.lower() or 'pandas' in f.name
        ]
        if pandas_ops:
            slow_pandas = [f for f in pandas_ops if f.cumtime > 0.1]
            if slow_pandas:
                recommendations.append(
                    f"Consider vectorization for pandas operations: {len(slow_pandas)} slow operations detected"
                )
        
        # Check for numpy operations
        numpy_ops = [
            f for f in functions
            if 'numpy' in f.name.lower() or 'numpy' in f.name
        ]
        if numpy_ops:
            recommendations.append(
                "NumPy operations detected - consider using numba JIT compilation for hot paths"
            )
        
        # Check for I/O operations
        io_ops = [
            f for f in functions
            if any(keyword in f.name.lower() for keyword in ['read', 'write', 'csv', 'file', 'io'])
        ]
        if io_ops:
            slow_io = [f for f in io_ops if f.cumtime > 0.1]
            if slow_io:
                recommendations.append(
                    f"Consider async I/O or chunked reading for file operations: {len(slow_io)} slow I/O operations"
                )
        
        # Check for loops
        loop_ops = [
            f for f in functions
            if any(keyword in f.name.lower() for keyword in ['loop', 'iter', 'for', 'while'])
        ]
        if loop_ops:
            recommendations.append(
                "Loop operations detected - consider vectorization or parallel processing"
            )
        
        # Check for recursive calls
        recursive_ops = [
            f for f in functions
            if f.ncalls != '1' and isinstance(f.ncalls, str) and '/' in str(f.ncalls)
        ]
        if recursive_ops:
            recommendations.append(
                "Recursive functions detected - consider iterative implementations for better performance"
            )
        
        # Bottleneck-specific recommendations
        if bottlenecks:
            recommendations.append(
                f"Focus optimization efforts on {len(bottlenecks)} identified bottlenecks (>10% of execution time)"
            )
        
        return recommendations
    
    def export_report(self, output_file: str, format: str = "json") -> str:
        """Export profiling report to file"""
        if not self.profiles:
            raise ValueError("No profiling data available")
        
        latest_report = self.profiles[-1]
        
        if format == "json":
            report_dict = {
                "total_time": latest_report.total_time,
                "functions": [
                    {
                        "name": f.name,
                        "ncalls": f.ncalls,
                        "tottime": f.tottime,
                        "cumtime": f.cumtime,
                        "percentage": f.percentage
                    }
                    for f in latest_report.functions
                ],
                "bottlenecks": [
                    {
                        "name": f.name,
                        "ncalls": f.ncalls,
                        "tottime": f.tottime,
                        "cumtime": f.cumtime,
                        "percentage": f.percentage
                    }
                    for f in latest_report.bottlenecks
                ],
                "recommendations": latest_report.recommendations,
                "timestamp": latest_report.timestamp
            }
            
            with open(output_file, 'w') as f:
                json.dump(report_dict, f, indent=2)
        
        elif format == "text":
            with open(output_file, 'w') as f:
                f.write("="*60 + "\n")
                f.write("PROFILING REPORT\n")
                f.write("="*60 + "\n\n")
                f.write(f"Total Time: {latest_report.total_time:.4f} seconds\n")
                f.write(f"Timestamp: {latest_report.timestamp}\n\n")
                
                f.write("Top Functions:\n")
                f.write("-"*60 + "\n")
                for i, func in enumerate(latest_report.functions[:20], 1):
                    f.write(f"{i}. {func.name}\n")
                    f.write(f"   Cumulative Time: {func.cumtime:.4f}s ({func.percentage:.1f}%)\n")
                    f.write(f"   Self Time: {func.tottime:.4f}s\n")
                    f.write(f"   Calls: {func.ncalls}\n\n")
                
                f.write("Bottlenecks:\n")
                f.write("-"*60 + "\n")
                for i, bottleneck in enumerate(latest_report.bottlenecks, 1):
                    f.write(f"{i}. {bottleneck.name}\n")
                    f.write(f"   Time: {bottleneck.cumtime:.4f}s ({bottleneck.percentage:.1f}%)\n\n")
                
                f.write("Recommendations:\n")
                f.write("-"*60 + "\n")
                for i, rec in enumerate(latest_report.recommendations, 1):
                    f.write(f"{i}. {rec}\n")
        
        return output_file
    
    def get_bottlenecks(self) -> List[FunctionProfile]:
        """Get identified bottlenecks"""
        if not self.profiles:
            return []
        return self.profiles[-1].bottlenecks
    
    def get_recommendations(self) -> List[str]:
        """Get optimization recommendations"""
        if not self.profiles:
            return []
        return self.profiles[-1].recommendations


class MemoryProfiler:
    """Memory profiling for memory bottlenecks"""
    
    def __init__(self):
        self.snapshots: List[Dict[str, float]] = []
    
    @contextmanager
    def profile(self):
        """Context manager for memory profiling"""
        import psutil
        process = psutil.Process()
        
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        peak_memory = initial_memory
        
        try:
            yield
        finally:
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            peak_memory = max(peak_memory, current_memory)
            
            self.snapshots.append({
                "initial_mb": initial_memory,
                "peak_mb": peak_memory,
                "current_mb": current_memory,
                "increase_mb": peak_memory - initial_memory
            })
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory profiling statistics"""
        if not self.snapshots:
            return {}
        
        return {
            "snapshots": len(self.snapshots),
            "avg_increase_mb": sum(s["increase_mb"] for s in self.snapshots) / len(self.snapshots),
            "max_increase_mb": max(s["increase_mb"] for s in self.snapshots),
            "avg_peak_mb": sum(s["peak_mb"] for s in self.snapshots) / len(self.snapshots)
        }


def profile_function(func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """Convenience function to profile a function"""
    profiler = CodeProfiler()
    return profiler.profile_function(func, *args, **kwargs)


def benchmark_function(
    func: Callable,
    iterations: int = 10,
    *args,
    **kwargs
) -> Dict[str, Any]:
    """Benchmark a function with multiple iterations"""
    times = []
    
    # Warm up
    func(*args, **kwargs)
    
    # Benchmark
    for _ in range(iterations):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        execution_time = time.perf_counter() - start_time
        times.append(execution_time)
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    std_time = (sum((t - avg_time) ** 2 for t in times) / len(times)) ** 0.5
    
    return {
        "result": result,
        "iterations": iterations,
        "avg_time": avg_time,
        "min_time": min_time,
        "max_time": max_time,
        "std_time": std_time,
        "total_time": sum(times)
    }

