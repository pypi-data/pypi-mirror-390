"""
QuickInsights - Modern Python Features Implementation

This module showcases and implements modern Python 3.11+ features including:
- Dataclasses with advanced features
- Pattern matching (match/case)
- Protocol classes and structural subtyping
- Enhanced type hints and Generic types
- Modern context managers
- Exception groups and error handling
- Performance optimizations with new features
"""

from __future__ import annotations
from typing import (
    TypeVar, Generic, Protocol, runtime_checkable,
    Union, Optional, Any, Dict, List, Set,
    Literal, Final, Callable
)

# Python 3.9 compatibility
try:
    from typing import TypeAlias, TypeGuard
except ImportError:
    # Fallback for Python 3.9
    TypeAlias = Any
    TypeGuard = Any
from dataclasses import dataclass, field

# Python 3.9 compatibility
try:
    from dataclasses import KW_ONLY
except ImportError:
    # KW_ONLY not available in Python 3.9
    KW_ONLY = None
from contextlib import asynccontextmanager, contextmanager

import logging
from datetime import datetime
from pathlib import Path

from enum import Enum, auto
import weakref

# Configure logging
logger = logging.getLogger(__name__)

# Type aliases for better readability (Python 3.9 compatible)
ConfigValue = Union[str, int, float, bool, List[Any], Dict[str, Any]]
ProcessingResult = Dict[str, Union[str, float, List[Any]]]

# Generic type variables
T = TypeVar('T')
R = TypeVar('R')
P = TypeVar('P', bound='Processor')

class ProcessingStatus(Enum):
    """Processing status enumeration using auto()"""
    PENDING = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()

@runtime_checkable
class Processor(Protocol):
    """Protocol for processing operations - structural subtyping"""
    
    def process(self, data: Any) -> Dict[str, Any]:
        """Process data and return results"""
        ...
    
    def validate(self, data: Any) -> bool:
        """Validate input data"""
        ...
    
    @property
    def name(self) -> str:
        """Processor name"""
        ...

@runtime_checkable
class AsyncProcessor(Protocol):
    """Protocol for async processing operations"""
    
    async def process_async(self, data: Any) -> Dict[str, Any]:
        """Async process data and return results"""
        ...
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        ...

@dataclass(frozen=True)  # Remove slots for Python 3.9 compatibility
class ProcessingConfig:
    """Modern dataclass with frozen for immutability"""
    
    # Required fields
    processor_name: str
    batch_size: int
    
    # Optional fields (KW_ONLY not available in Python 3.9)
    timeout: float = 30.0
    max_retries: int = 3
    enable_parallel: bool = True
    debug_mode: bool = False
    
    # Advanced field with factory
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        """Validation after initialization"""
        if self.batch_size <= 0:
            raise ValueError("Batch size must be positive")
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")

@dataclass
class ProcessingResultData:
    """Result of processing operation"""
    
    status: ProcessingStatus
    data: Any
    processing_time: float
    processor_name: str
    timestamp: datetime = field(default_factory=datetime.now)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_successful(self) -> bool:
        """Check if processing was successful"""
        return self.status == ProcessingStatus.COMPLETED and not self.errors
    
    def add_error(self, error: str) -> None:
        """Add error to result"""
        self.errors.append(error)
        if self.status == ProcessingStatus.PROCESSING:
            self.status = ProcessingStatus.FAILED

class PatternMatcher:
    """Demonstrates modern pattern matching with match/case"""
    
    def process_data_type(self, data: Any) -> str:
        """Process different data types using pattern matching (Python 3.9 compatible)"""
        
        # None check
        if data is None:
            return "null_data"
        
        # Boolean check
        if isinstance(data, bool):
            return f"boolean: {data}"
        
        # Integer patterns
        if isinstance(data, int):
            if data < 0:
                return f"negative_integer: {data}"
            elif data == 0:
                return "zero"
            else:
                return f"positive_integer: {data}"
        
        # String patterns
        if isinstance(data, str):
            if len(data) == 0:
                return "empty_string"
            elif data.startswith("http"):
                return f"url: {data}"
            else:
                return f"string: {data[:50]}..."
        
        # List patterns
        if isinstance(data, list):
            if len(data) == 0:
                return "empty_list"
            elif len(data) == 1:
                return f"single_item_list: {type(data[0]).__name__}"
            elif len(data) > 11:  # first + 10+ rest
                return f"long_list: first={data[0]}, count={len(data)}"
            else:
                return f"multi_item_list: first={data[0]}, second={data[1] if len(data) > 1 else 'None'}, rest_count={len(data) - 2 if len(data) > 2 else 0}"
        
        # Dictionary patterns
        if isinstance(data, dict):
            if len(data) == 0:
                return "empty_dict"
            elif data.get("type") == "config" and "value" in data:
                return f"config_dict: {data['value']}"
            elif "name" in data and "age" in data and isinstance(data["age"], int):
                age = data["age"]
                name = data["name"]
                if age >= 18:
                    return f"adult_person: {name}, {age}"
                else:
                    return f"minor_person: {name}, {age}"
            elif "error" in data:
                return f"error_dict: {data.get('error')}"
        
        # ProcessingResult patterns
        if isinstance(data, ProcessingResultData):
            if data.status == ProcessingStatus.COMPLETED:
                return f"completed_result: {type(data.data).__name__}"
            elif data.status == ProcessingStatus.FAILED:
                return f"failed_result: {len(data.errors)} errors"
        
        # Default case
        return f"unknown_type: {type(data).__name__}"
    
    def route_processing_request(self, request: Dict[str, Any]) -> str:
        """Route processing requests using pattern matching (Python 3.9 compatible)"""
        
        # High priority check first
        if request.get("priority") == "high":
            action = request.get("action", "unknown")
            return f"high_priority_handler:{action}"
        
        action = request.get("action")
        
        # Process actions
        if action == "process":
            request_type = request.get("type")
            if request_type == "batch" and "data" in request:
                data = request["data"]
                if isinstance(data, list):
                    if len(data) > 1000:
                        return "large_batch_processor"
                    else:
                        return "standard_batch_processor"
            elif request_type == "stream" and "source" in request:
                source = request["source"]
                return f"stream_processor:{source}"
        
        # Analyze actions
        elif action == "analyze":
            algorithm = request.get("algorithm")
            if algorithm == "ml" and "model" in request:
                model = request["model"]
                return f"ml_analyzer:{model}"
            elif algorithm == "stats":
                return "statistical_analyzer"
        
        # Export actions
        elif action == "export":
            fmt = request.get("format")
            if fmt in ["json", "csv", "xml"]:
                return f"export_handler:{fmt}"
        
        # Import actions
        elif action == "import" and "source" in request:
            source = request["source"]
            if isinstance(source, dict):
                source_type = source.get("type")
                if source_type == "database" and "connection" in source:
                    conn = source["connection"]
                    return f"db_importer:{conn}"
                elif source_type == "file" and "path" in source:
                    path = source["path"]
                    return f"file_importer:{Path(path).suffix}"
        
        # Default handler
        return "default_handler"

class GenericProcessor(Generic[T, R]):
    """Generic processor with type parameters"""
    
    def __init__(self, processor_func: Callable[[T], R], name: str) -> None:
        self.processor_func = processor_func
        self.name = name
        self._cache: weakref.WeakValueDictionary[str, Any] = weakref.WeakValueDictionary()
    
    def process(self, data: T) -> R:
        """Process data with generic types"""
        try:
            return self.processor_func(data)
        except Exception as e:
            logger.error(f"Processing failed in {self.name}: {e}")
            raise
    
    def process_batch(self, items: List[T]) -> List[R]:
        """Process multiple items"""
        results = []
        for item in items:
            try:
                result = self.process(item)
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to process item in batch: {e}")
                continue
        return results

def is_valid_processor(obj: Any) -> bool:
    """Type guard to check if object implements Processor protocol"""
    return (
        hasattr(obj, 'process') and callable(obj.process) and
        hasattr(obj, 'validate') and callable(obj.validate) and
        hasattr(obj, 'name') and isinstance(obj.name, str)
    )

class ModernContextManager:
    """Modern context manager with advanced features"""
    
    def __init__(self, name: str, auto_cleanup: bool = True):
        self.name = name
        self.auto_cleanup = auto_cleanup
        self.resources: List[Any] = []
        self.start_time: Optional[datetime] = None
    
    def __enter__(self) -> ModernContextManager:
        """Enter context"""
        self.start_time = datetime.now()
        logger.info(f"Entering context: {self.name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> Optional[bool]:
        """Exit context with exception handling"""
        duration = datetime.now() - self.start_time if self.start_time else None
        
        if exc_type is not None:
            logger.error(f"Exception in context {self.name}: {exc_val}")
            if self.auto_cleanup:
                self.cleanup()
            return False  # Don't suppress exception
        
        logger.info(f"Exiting context: {self.name}, duration: {duration}")
        if self.auto_cleanup:
            self.cleanup()
        return None
    
    def add_resource(self, resource: Any) -> None:
        """Add resource for cleanup"""
        self.resources.append(resource)
    
    def cleanup(self) -> None:
        """Clean up resources"""
        for resource in self.resources:
            try:
                if hasattr(resource, 'close'):
                    resource.close()
                elif hasattr(resource, 'cleanup'):
                    resource.cleanup()
            except Exception as e:
                logger.warning(f"Failed to cleanup resource: {e}")
        self.resources.clear()

@asynccontextmanager
async def async_processing_context(config: ProcessingConfig):
    """Async context manager for processing operations"""
    logger.info(f"Starting async processing: {config.processor_name}")
    start_time = datetime.now()
    
    try:
        # Setup
        if config.debug_mode:
            logger.setLevel(logging.DEBUG)
        
        yield config
        
    except Exception as e:
        logger.error(f"Error in async processing: {e}")
        raise
    finally:
        # Cleanup
        duration = datetime.now() - start_time
        logger.info(f"Async processing completed in {duration}")

@contextmanager
def processing_session(processor_name: str, **kwargs):
    """Context manager for processing sessions"""
    session_id = f"{processor_name}_{datetime.now().isoformat()}"
    logger.info(f"Starting session: {session_id}")
    
    try:
        yield session_id
    except Exception as e:
        logger.error(f"Session {session_id} failed: {e}")
        raise
    finally:
        logger.info(f"Session {session_id} ended")

class ExceptionGroupHandler:
    """Handler for exception groups (Python 3.11+)"""
    
    @staticmethod
    def handle_processing_errors(errors: List[Exception]) -> None:
        """Handle multiple processing errors"""
        if not errors:
            return
        
        # Group exceptions by type
        error_groups = {}
        for error in errors:
            error_type = type(error).__name__
            if error_type not in error_groups:
                error_groups[error_type] = []
            error_groups[error_type].append(error)
        
        # Log grouped errors
        for error_type, error_list in error_groups.items():
            logger.error(f"{error_type}: {len(error_list)} occurrences")
            for i, error in enumerate(error_list[:3]):  # Log first 3
                logger.error(f"  {i+1}: {error}")
            if len(error_list) > 3:
                logger.error(f"  ... and {len(error_list) - 3} more")

class PerformanceOptimizer:
    """Performance optimizations using modern Python features"""
    
    # __slots__ removed for Python 3.9 compatibility with frozen dataclass
    
    def __init__(self, config: ProcessingConfig):
        self._cache: Dict[str, Any] = {}
        self._stats: Dict[str, int] = {'hits': 0, 'misses': 0}
        self._config: Final[ProcessingConfig] = config
    
    def cached_operation(self, key: str, operation: Callable) -> Any:
        """Cached operation with performance tracking"""
        if key in self._cache:
            self._stats['hits'] += 1
            return self._cache[key]
        
        self._stats['misses'] += 1
        result = operation()
        self._cache[key] = result
        return result
    
    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self._stats['hits'] + self._stats['misses']
        return self._stats['hits'] / total if total > 0 else 0.0

# Factory functions for common patterns
def create_processor(processor_type: Literal["batch", "stream", "ml"]) -> Processor:
    """Factory function with literal types (Python 3.9 compatible)"""
    
    if processor_type == "batch":
        return BatchProcessor()
    elif processor_type == "stream":
        return StreamProcessor()
    elif processor_type == "ml":
        return MLProcessor()
    else:
        raise ValueError(f"Unknown processor type: {processor_type}")

# Concrete processor implementations
class BatchProcessor:
    """Batch processor implementation"""
    
    @property
    def name(self) -> str:
        return "batch_processor"
    
    def process(self, data: Any) -> Dict[str, Any]:
        return {"type": "batch", "result": f"Processed {len(data) if hasattr(data, '__len__') else 1} items"}
    
    def validate(self, data: Any) -> bool:
        return data is not None

class StreamProcessor:
    """Stream processor implementation"""
    
    @property
    def name(self) -> str:
        return "stream_processor"
    
    def process(self, data: Any) -> Dict[str, Any]:
        return {"type": "stream", "result": f"Streamed data: {type(data).__name__}"}
    
    def validate(self, data: Any) -> bool:
        return hasattr(data, '__iter__')

class MLProcessor:
    """ML processor implementation"""
    
    @property
    def name(self) -> str:
        return "ml_processor"
    
    def process(self, data: Any) -> Dict[str, Any]:
        return {"type": "ml", "result": f"ML analysis of {type(data).__name__}"}
    
    def validate(self, data: Any) -> bool:
        return hasattr(data, '__len__') and len(data) > 0

# Example usage functions
def demonstrate_modern_features():
    """Demonstrate modern Python features"""
    
    # Pattern matching
    matcher = PatternMatcher()
    
    test_data = [
        None, True, -5, 0, 42, "", "https://example.com", "hello",
        [], [1], [1, 2, 3, 4, 5], {"type": "config", "value": 100},
        {"name": "Alice", "age": 25}, {"error": "Something went wrong"}
    ]
    
    print("=== Pattern Matching Demo ===")
    for data in test_data:
        result = matcher.process_data_type(data)
        print(f"{repr(data)} -> {result}")
    
    # Protocol and type guards
    print("\n=== Protocol Demo ===")
    processors = [BatchProcessor(), StreamProcessor(), MLProcessor()]
    
    for proc in processors:
        if is_valid_processor(proc):
            print(f"Valid processor: {proc.name}")
            result = proc.process([1, 2, 3])
            print(f"  Result: {result}")
    
    # Context managers
    print("\n=== Context Manager Demo ===")
    with ModernContextManager("demo_context") as ctx:
        ctx.add_resource({"type": "demo_resource"})
        print("Working in context...")
    
    print("Modern features demonstration completed!")

if __name__ == "__main__":
    demonstrate_modern_features()
