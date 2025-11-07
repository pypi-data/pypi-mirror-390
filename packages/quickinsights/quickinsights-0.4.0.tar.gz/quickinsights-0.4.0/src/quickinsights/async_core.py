"""
Async-First Architecture for QuickInsights

Provides async/await support for all core operations, enabling
concurrent processing and better performance for I/O operations.
"""

import asyncio
import aiofiles
import aiohttp
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional, Union, Callable, Awaitable, Tuple
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from collections import OrderedDict

from .error_handling import QuickInsightsError, PerformanceError
from .advanced_config import get_advanced_config_manager

logger = logging.getLogger(__name__)


class AsyncOperationType(Enum):
    """Types of async operations"""
    ANALYSIS = "analysis"
    VISUALIZATION = "visualization"
    DATA_LOADING = "data_loading"
    DATA_SAVING = "data_saving"
    MODEL_TRAINING = "model_training"
    MODEL_PREDICTION = "model_prediction"
    CUSTOM = "custom"


@dataclass
class AsyncTask:
    """Async task information"""
    task_id: str
    operation_type: AsyncOperationType
    function: Callable[..., Any]  # Proper type hint for Callable
    args: Tuple[Any, ...]  # Proper tuple type hint
    kwargs: Dict[str, Any]  # Proper dict type hint
    priority: int = 0
    created_at: float = 0.0
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Any = None
    error: Optional[Exception] = None


class AsyncTaskManager:
    """Manages async tasks with priority and resource management"""
    
    def __init__(self, max_concurrent_tasks: int = 10, max_completed_tasks: int = 1000):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.max_completed_tasks = max_completed_tasks  # Limit to prevent memory leak
        self.tasks: Dict[str, AsyncTask] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_queue: List[AsyncTask] = []
        # Use OrderedDict for LRU eviction of completed tasks
        self.completed_tasks: OrderedDict[str, AsyncTask] = OrderedDict()
        self.lock = asyncio.Lock()
        self.executor: Optional[ThreadPoolExecutor] = ThreadPoolExecutor(max_workers=max_concurrent_tasks)
        self._shutdown = False
        
    async def submit_task(
        self,
        task_id: str,
        operation_type: AsyncOperationType,
        function: Callable[..., Any],
        *args: Any,
        priority: int = 0,
        **kwargs: Any
    ) -> str:
        """Submit an async task"""
        async with self.lock:
            task = AsyncTask(
                task_id=task_id,
                operation_type=operation_type,
                function=function,
                args=args,
                kwargs=kwargs,
                priority=priority,
                created_at=time.time()
            )
            
            self.tasks[task_id] = task
            self.task_queue.append(task)
            
            # Sort by priority (higher priority first)
            self.task_queue.sort(key=lambda t: t.priority, reverse=True)
            
            # Start task if we have capacity
            await self._start_next_task()
            
            return task_id
    
    async def _start_next_task(self):
        """Start the next task in queue if capacity allows"""
        if len(self.running_tasks) >= self.max_concurrent_tasks:
            return
        
        if not self.task_queue:
            return
        
        task = self.task_queue.pop(0)
        task.started_at = time.time()
        
        # Create asyncio task
        asyncio_task = asyncio.create_task(self._execute_task(task))
        self.running_tasks[task.task_id] = asyncio_task
        
        # Add done callback - use safe callback wrapper
        asyncio_task.add_done_callback(
            lambda t: self._safe_task_completed_callback(task.task_id, t)
        )
    
    async def _execute_task(self, task: AsyncTask) -> Any:
        """Execute a task"""
        try:
            # Check if function is async
            if asyncio.iscoroutinefunction(task.function):
                result = await task.function(*task.args, **task.kwargs)
            else:
                # Run sync function in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.executor,
                    task.function,
                    *task.args,
                    **task.kwargs
                )
            
            task.result = result
            task.completed_at = time.time()
            
            return result
            
        except Exception as e:
            task.error = e
            task.completed_at = time.time()
            logger.error(f"Task {task.task_id} failed: {e}")
            raise
    
    def _safe_task_completed_callback(self, task_id: str, asyncio_task: asyncio.Task) -> None:
        """Safe callback wrapper that schedules async task completion"""
        # Create task in event loop if it exists
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Schedule task completion in running loop
                loop.create_task(self._task_completed(task_id, asyncio_task))
            else:
                # If no running loop, run in new task
                asyncio.run(self._task_completed(task_id, asyncio_task))
        except RuntimeError:
            # No event loop, create one
            asyncio.run(self._task_completed(task_id, asyncio_task))
    
    async def _task_completed(self, task_id: str, asyncio_task: asyncio.Task) -> None:
        """Handle task completion"""
        async with self.lock:
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
            
            if task_id in self.tasks:
                task = self.tasks[task_id]
                # Update task with result or error
                try:
                    task.result = asyncio_task.result()
                except Exception as e:
                    task.error = e
                task.completed_at = time.time()
                
                # Add to completed tasks with LRU eviction
                self._add_completed_task(task_id, task)
                del self.tasks[task_id]
            
            # Start next task
            await self._start_next_task()
    
    def _add_completed_task(self, task_id: str, task: AsyncTask) -> None:
        """Add completed task with LRU eviction to prevent memory leak"""
        # Remove oldest if at limit
        if len(self.completed_tasks) >= self.max_completed_tasks:
            # Remove oldest (first) item
            self.completed_tasks.popitem(last=False)
        
        # Add new task (most recent)
        self.completed_tasks[task_id] = task
        # Move to end (most recently used)
        self.completed_tasks.move_to_end(task_id)
    
    async def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """Wait for a specific task to complete"""
        # Check running tasks first (thread-safe)
        task_ref: Optional[asyncio.Task] = None
        async with self.lock:
            if task_id in self.running_tasks:
                task_ref = self.running_tasks[task_id]
            elif task_id in self.completed_tasks:
                task = self.completed_tasks[task_id]
                if task.error:
                    raise task.error
                # Move to end (LRU)
                self.completed_tasks.move_to_end(task_id)
                return task.result
            else:
                raise QuickInsightsError(f"Task {task_id} not found")
        
        # Wait for running task outside lock
        if task_ref is not None:
            try:
                return await asyncio.wait_for(task_ref, timeout=timeout)
            except asyncio.TimeoutError:
                raise QuickInsightsError(f"Task {task_id} timed out after {timeout} seconds")
        
        raise QuickInsightsError(f"Task {task_id} not found")
    
    async def wait_for_all_tasks(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Wait for all tasks to complete"""
        # Get snapshot of running tasks (thread-safe)
        async with self.lock:
            if not self.running_tasks:
                return {}
            running_snapshot = dict(self.running_tasks)
        
        # Wait outside lock to avoid blocking
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*running_snapshot.values(), return_exceptions=True),
                timeout=timeout
            )
            
            return dict(zip(running_snapshot.keys(), results))
            
        except asyncio.TimeoutError:
            raise QuickInsightsError(f"Tasks timed out after {timeout} seconds")
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            return {
                "status": "queued",
                "created_at": task.created_at,
                "priority": task.priority
            }
        
        if task_id in self.running_tasks:
            task = self.tasks.get(task_id)
            if task:
                return {
                    "status": "running",
                    "created_at": task.created_at,
                    "started_at": task.started_at,
                    "priority": task.priority
                }
        
        if task_id in self.completed_tasks:
            task = self.completed_tasks[task_id]
            return {
                "status": "completed" if not task.error else "failed",
                "created_at": task.created_at,
                "started_at": task.started_at,
                "completed_at": task.completed_at,
                "error": str(task.error) if task.error else None
            }
        
        return None
    
    def get_all_tasks_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all tasks"""
        status = {}
        
        for task_id in self.tasks:
            status[task_id] = self.get_task_status(task_id)
        
        for task_id in self.running_tasks:
            status[task_id] = self.get_task_status(task_id)
        
        for task_id in self.completed_tasks:
            status[task_id] = self.get_task_status(task_id)
        
        return status
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        async with self.lock:
            if task_id in self.running_tasks:
                self.running_tasks[task_id].cancel()
                del self.running_tasks[task_id]
                return True
            
            if task_id in self.tasks:
                self.tasks[task_id].error = QuickInsightsError(f"Task {task_id} was cancelled")
                self.completed_tasks[task_id] = self.tasks[task_id]
                del self.tasks[task_id]
                return True
            
            return False
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self._shutdown:
            return
        
        self._shutdown = True
        
        # Cancel all running tasks
        for task in self.running_tasks.values():
            if not task.done():
                task.cancel()
        
        # Wait for cancellation with timeout
        if self.running_tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self.running_tasks.values(), return_exceptions=True),
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                logger.warning("Some tasks did not complete during cleanup")
        
        # Shutdown executor properly
        if self.executor is not None:
            try:
                self.executor.shutdown(wait=True, cancel_futures=True)
            except Exception as e:
                logger.error(f"Error shutting down executor: {e}")
            finally:
                self.executor = None
        
        # Clear completed tasks to free memory
        self.completed_tasks.clear()
        self.tasks.clear()
        self.running_tasks.clear()
        self.task_queue.clear()


class AsyncDataLoader:
    """Async data loading utilities with connection pooling"""
    
    # Shared executor for I/O operations (quick-win: reuse executor)
    _executor: Optional[ThreadPoolExecutor] = None
    _session: Optional[aiohttp.ClientSession] = None
    
    @classmethod
    def _get_executor(cls) -> ThreadPoolExecutor:
        """Get or create shared executor (connection pooling benefit)"""
        if cls._executor is None:
            cls._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="qi_loader")
        return cls._executor
    
    @classmethod
    async def _get_session(cls) -> aiohttp.ClientSession:
        """Get or create shared aiohttp session (connection pooling)"""
        if cls._session is None or cls._session.closed:
            # Connection pooling: reuse connections
            connector = aiohttp.TCPConnector(
                limit=100,  # Max connections
                limit_per_host=10,  # Max per host
                ttl_dns_cache=300,  # DNS cache TTL
                force_close=False  # Keep connections alive
            )
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            cls._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )
        return cls._session
    
    @classmethod
    async def cleanup(cls) -> None:
        """Cleanup shared resources"""
        if cls._session is not None and not cls._session.closed:
            await cls._session.close()
            cls._session = None
        if cls._executor is not None:
            cls._executor.shutdown(wait=False)
            cls._executor = None
    
    @classmethod
    async def load_csv(cls, file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """Load CSV file asynchronously (optimized with shared executor)"""
        loop = asyncio.get_event_loop()
        executor = cls._get_executor()
        
        def _load_csv():
            return pd.read_csv(file_path, **kwargs)
        
        return await loop.run_in_executor(executor, _load_csv)
    
    @classmethod
    async def load_excel(cls, file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """Load Excel file asynchronously (optimized with shared executor)"""
        loop = asyncio.get_event_loop()
        executor = cls._get_executor()
        
        def _load_excel():
            return pd.read_excel(file_path, **kwargs)
        
        return await loop.run_in_executor(executor, _load_excel)
    
    @classmethod
    async def load_json(cls, file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """Load JSON file asynchronously (optimized with shared executor)"""
        loop = asyncio.get_event_loop()
        executor = cls._get_executor()
        
        def _load_json():
            return pd.read_json(file_path, **kwargs)
        
        return await loop.run_in_executor(executor, _load_json)
    
    @classmethod
    async def load_parquet(cls, file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """Load Parquet file asynchronously (optimized with shared executor)"""
        loop = asyncio.get_event_loop()
        executor = cls._get_executor()
        
        def _load_parquet():
            return pd.read_parquet(file_path, **kwargs)
        
        return await loop.run_in_executor(executor, _load_parquet)
    
    @classmethod
    async def load_from_url(cls, url: str, **kwargs) -> pd.DataFrame:
        """Load data from URL asynchronously (optimized with connection pooling)"""
        session = await cls._get_session()
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.read()
                
                # Determine format from URL or content
                if url.endswith('.csv'):
                    return await cls.load_csv_from_bytes(content, **kwargs)
                elif url.endswith('.json'):
                    return await cls.load_json_from_bytes(content, **kwargs)
                else:
                    raise QuickInsightsError(f"Unsupported URL format: {url}")
            else:
                raise QuickInsightsError(f"Failed to load data from URL: {response.status}")
    
    @classmethod
    async def load_csv_from_bytes(cls, content: bytes, **kwargs) -> pd.DataFrame:
        """Load CSV from bytes (optimized with shared executor)"""
        import io
        
        loop = asyncio.get_event_loop()
        executor = cls._get_executor()
        
        def _load_csv():
            return pd.read_csv(io.BytesIO(content), **kwargs)
        
        return await loop.run_in_executor(executor, _load_csv)
    
    @classmethod
    async def load_json_from_bytes(cls, content: bytes, **kwargs) -> pd.DataFrame:
        """Load JSON from bytes (optimized with shared executor)"""
        import io
        
        loop = asyncio.get_event_loop()
        executor = cls._get_executor()
        
        def _load_json():
            return pd.read_json(io.BytesIO(content), **kwargs)
        
        return await loop.run_in_executor(executor, _load_json)


class AsyncDataSaver:
    """Async data saving utilities with shared executor"""
    
    # Shared executor for I/O operations (quick-win: reuse executor)
    _executor: Optional[ThreadPoolExecutor] = None
    
    @classmethod
    def _get_executor(cls) -> ThreadPoolExecutor:
        """Get or create shared executor (connection pooling benefit)"""
        if cls._executor is None:
            cls._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="qi_saver")
        return cls._executor
    
    @classmethod
    async def cleanup(cls) -> None:
        """Cleanup shared resources"""
        if cls._executor is not None:
            cls._executor.shutdown(wait=False)
            cls._executor = None
    
    @classmethod
    async def save_csv(cls, df: pd.DataFrame, file_path: Union[str, Path], **kwargs) -> None:
        """Save DataFrame to CSV asynchronously (optimized with shared executor)"""
        loop = asyncio.get_event_loop()
        executor = cls._get_executor()
        
        def _save_csv():
            df.to_csv(file_path, index=False, **kwargs)
        
        await loop.run_in_executor(executor, _save_csv)
    
    @classmethod
    async def save_excel(cls, df: pd.DataFrame, file_path: Union[str, Path], **kwargs) -> None:
        """Save DataFrame to Excel asynchronously (optimized with shared executor)"""
        loop = asyncio.get_event_loop()
        executor = cls._get_executor()
        
        def _save_excel():
            df.to_excel(file_path, **kwargs)
        
        await loop.run_in_executor(executor, _save_excel)
    
    @classmethod
    async def save_json(cls, df: pd.DataFrame, file_path: Union[str, Path], **kwargs) -> None:
        """Save DataFrame to JSON asynchronously (optimized with shared executor)"""
        loop = asyncio.get_event_loop()
        executor = cls._get_executor()
        
        def _save_json():
            df.to_json(file_path, **kwargs)
        
        await loop.run_in_executor(executor, _save_json)
    
    @classmethod
    async def save_parquet(cls, df: pd.DataFrame, file_path: Union[str, Path], **kwargs) -> None:
        """Save DataFrame to Parquet asynchronously (optimized with shared executor)"""
        loop = asyncio.get_event_loop()
        executor = cls._get_executor()
        
        def _save_parquet():
            df.to_parquet(file_path, **kwargs)
        
        await loop.run_in_executor(executor, _save_parquet)


class AsyncAnalyzer:
    """Async data analysis operations"""
    
    def __init__(self, task_manager: AsyncTaskManager):
        self.task_manager = task_manager
    
    async def analyze_async(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Async data analysis"""
        loop = asyncio.get_event_loop()
        
        def _analyze():
            # Import here to avoid circular imports
            from .analysis.basic_analysis import analyze
            return analyze(df, **kwargs)
        
        return await loop.run_in_executor(None, _analyze)
    
    async def analyze_numeric_async(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Async numeric analysis"""
        loop = asyncio.get_event_loop()
        
        def _analyze_numeric():
            from .analysis.basic_analysis import analyze_numeric
            return analyze_numeric(df, **kwargs)
        
        return await loop.run_in_executor(None, _analyze_numeric)
    
    async def analyze_categorical_async(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Async categorical analysis"""
        loop = asyncio.get_event_loop()
        
        def _analyze_categorical():
            from .analysis.basic_analysis import analyze_categorical
            return analyze_categorical(df, **kwargs)
        
        return await loop.run_in_executor(None, _analyze_categorical)
    
    async def analyze_multiple_datasets(
        self,
        datasets: List[pd.DataFrame],
        analysis_type: str = "full",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Analyze multiple datasets concurrently"""
        tasks = []
        
        for i, df in enumerate(datasets):
            if analysis_type == "full":
                task_id = await self.task_manager.submit_task(
                    f"analyze_{i}",
                    AsyncOperationType.ANALYSIS,
                    self.analyze_async,
                    df,
                    **kwargs
                )
            elif analysis_type == "numeric":
                task_id = await self.task_manager.submit_task(
                    f"analyze_numeric_{i}",
                    AsyncOperationType.ANALYSIS,
                    self.analyze_numeric_async,
                    df,
                    **kwargs
                )
            elif analysis_type == "categorical":
                task_id = await self.task_manager.submit_task(
                    f"analyze_categorical_{i}",
                    AsyncOperationType.ANALYSIS,
                    self.analyze_categorical_async,
                    df,
                    **kwargs
                )
            else:
                raise QuickInsightsError(f"Unsupported analysis type: {analysis_type}")
            
            tasks.append(task_id)
        
        # Wait for all tasks to complete
        results = []
        for task_id in tasks:
            result = await self.task_manager.wait_for_task(task_id)
            results.append(result)
        
        return results


class AsyncVisualizer:
    """Async visualization operations"""
    
    def __init__(self, task_manager: AsyncTaskManager):
        self.task_manager = task_manager
    
    async def create_visualization_async(
        self,
        data: Any,
        chart_type: str,
        **kwargs
    ) -> Any:
        """Create visualization asynchronously"""
        loop = asyncio.get_event_loop()
        
        def _create_visualization():
            # Import here to avoid circular imports
            from .visualization.charts import create_chart
            return create_chart(data, chart_type, **kwargs)
        
        return await loop.run_in_executor(None, _create_visualization)
    
    async def create_multiple_visualizations(
        self,
        data_list: List[Any],
        chart_types: List[str],
        **kwargs
    ) -> List[Any]:
        """Create multiple visualizations concurrently"""
        tasks = []
        
        for i, (data, chart_type) in enumerate(zip(data_list, chart_types)):
            task_id = await self.task_manager.submit_task(
                f"visualization_{i}",
                AsyncOperationType.VISUALIZATION,
                self.create_visualization_async,
                data,
                chart_type,
                **kwargs
            )
            tasks.append(task_id)
        
        # Wait for all tasks to complete
        results = []
        for task_id in tasks:
            result = await self.task_manager.wait_for_task(task_id)
            results.append(result)
        
        return results


class AsyncQuickInsights:
    """Main async interface for QuickInsights"""
    
    def __init__(self, max_concurrent_tasks: int = 10):
        self.task_manager = AsyncTaskManager(max_concurrent_tasks)
        self.data_loader = AsyncDataLoader()
        self.data_saver = AsyncDataSaver()
        self.analyzer = AsyncAnalyzer(self.task_manager)
        self.visualizer = AsyncVisualizer(self.task_manager)
    
    async def load_data(self, source: Union[str, Path], **kwargs) -> pd.DataFrame:
        """Load data from various sources asynchronously"""
        source = Path(source)
        
        if source.suffix.lower() == '.csv':
            return await self.data_loader.load_csv(source, **kwargs)
        elif source.suffix.lower() in ['.xlsx', '.xls']:
            return await self.data_loader.load_excel(source, **kwargs)
        elif source.suffix.lower() == '.json':
            return await self.data_loader.load_json(source, **kwargs)
        elif source.suffix.lower() == '.parquet':
            return await self.data_loader.load_parquet(source, **kwargs)
        elif str(source).startswith('http'):
            return await self.data_loader.load_from_url(str(source), **kwargs)
        else:
            raise QuickInsightsError(f"Unsupported file format: {source.suffix}")
    
    async def save_data(
        self,
        df: pd.DataFrame,
        file_path: Union[str, Path],
        **kwargs
    ) -> None:
        """Save data to various formats asynchronously"""
        file_path = Path(file_path)
        
        if file_path.suffix.lower() == '.csv':
            await self.data_saver.save_csv(df, file_path, **kwargs)
        elif file_path.suffix.lower() in ['.xlsx', '.xls']:
            await self.data_saver.save_excel(df, file_path, **kwargs)
        elif file_path.suffix.lower() == '.json':
            await self.data_saver.save_json(df, file_path, **kwargs)
        elif file_path.suffix.lower() == '.parquet':
            await self.data_saver.save_parquet(df, file_path, **kwargs)
        else:
            raise QuickInsightsError(f"Unsupported file format: {file_path.suffix}")
    
    async def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Analyze data asynchronously"""
        return await self.analyzer.analyze_async(df, **kwargs)
    
    async def analyze_async(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Alias for analyze method for backward compatibility"""
        return await self.analyze(df, **kwargs)
    
    async def analyze_multiple(
        self,
        datasets: List[pd.DataFrame],
        analysis_type: str = "full",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Analyze multiple datasets concurrently"""
        return await self.analyzer.analyze_multiple_datasets(
            datasets, analysis_type, **kwargs
        )
    
    async def visualize(
        self,
        data: Any,
        chart_type: str,
        **kwargs
    ) -> Any:
        """Create visualization asynchronously"""
        return await self.visualizer.create_visualization_async(
            data, chart_type, **kwargs
        )
    
    async def visualize_multiple(
        self,
        data_list: List[Any],
        chart_types: List[str],
        **kwargs
    ) -> List[Any]:
        """Create multiple visualizations concurrently"""
        return await self.visualizer.create_multiple_visualizations(
            data_list, chart_types, **kwargs
        )
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status"""
        return self.task_manager.get_task_status(task_id)
    
    async def get_all_tasks_status(self) -> Dict[str, Dict[str, Any]]:
        """Get all tasks status"""
        return self.task_manager.get_all_tasks_status()
    
    async def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """Wait for a specific task to complete"""
        return await self.task_manager.wait_for_task(task_id, timeout)
    
    async def wait_for_all_tasks(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Wait for all tasks to complete"""
        return await self.task_manager.wait_for_all_tasks(timeout)
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        return await self.task_manager.cancel_task(task_id)
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        await self.task_manager.cleanup()
        # Cleanup shared resources
        await self.data_loader.cleanup()
        await self.data_saver.cleanup()


# Global async instance
_async_quickinsights: Optional[AsyncQuickInsights] = None


def get_async_quickinsights() -> AsyncQuickInsights:
    """Get the global async QuickInsights instance"""
    global _async_quickinsights
    if _async_quickinsights is None:
        config = get_advanced_config_manager()
        max_tasks = config.get("performance.max_concurrent_tasks", 10)
        _async_quickinsights = AsyncQuickInsights(max_tasks)
    return _async_quickinsights


async def analyze_async(df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
    """Async analyze function"""
    return await get_async_quickinsights().analyze(df, **kwargs)


async def load_data_async(source: Union[str, Path], **kwargs) -> pd.DataFrame:
    """Async data loading function"""
    return await get_async_quickinsights().load_data(source, **kwargs)


async def save_data_async(
    df: pd.DataFrame,
    file_path: Union[str, Path],
    **kwargs
) -> None:
    """Async data saving function"""
    await get_async_quickinsights().save_data(df, file_path, **kwargs)
