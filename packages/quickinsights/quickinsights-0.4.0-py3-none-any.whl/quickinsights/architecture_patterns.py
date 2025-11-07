"""
QuickInsights - Advanced Architecture Patterns

This module implements enterprise-grade architectural patterns including:
- Dependency Injection Container
- Command Pattern with undo/redo
- Observer Pattern for event handling
- Strategy Pattern for algorithms
- Singleton Pattern with thread safety
- Builder Pattern for complex object creation
- Adapter Pattern for external integrations
- Facade Pattern for simplified interfaces
"""

from __future__ import annotations
import threading
import logging
from typing import (
    Dict, List, Any, Optional, Callable, TypeVar, Generic,
    Protocol, runtime_checkable, Type, Set
)
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
import copy

# Configure logging
logger = logging.getLogger(__name__)

# Type variables
T = TypeVar('T')
R = TypeVar('R')


class EventType(Enum):
    """Event types for observer pattern"""
    DATA_PROCESSED = auto()
    ERROR_OCCURRED = auto()
    OPERATION_STARTED = auto()
    OPERATION_COMPLETED = auto()
    CONFIGURATION_CHANGED = auto()


@dataclass
class Event:
    """Event data structure"""
    event_type: EventType
    source: str
    data: Any
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


# Protocol definitions
@runtime_checkable
class Observer(Protocol):
    """Observer protocol for event handling"""

    def notify(self, event: Event) -> None:
        """Handle notification of an event"""
        ...


@runtime_checkable
class Command(Protocol):
    """Command protocol for command pattern"""

    def execute(self) -> Any:
        """Execute the command"""
        ...

    def undo(self) -> Any:
        """Undo the command"""
        ...


@runtime_checkable
class Strategy(Protocol):
    """Strategy protocol for algorithm selection"""

    def execute(self, data: Any) -> Any:
        """Execute the strategy"""
        ...


class DependencyInjectionContainer:
    """Thread-safe dependency injection container"""

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        self._lock = threading.RLock()

    def register_instance(self, name: str, instance: Any) -> None:
        """Register a service instance"""
        with self._lock:
            self._services[name] = instance
            logger.debug(f"Registered instance: {name}")

    def register_factory(self, name: str, factory: Callable) -> None:
        """Register a factory function"""
        with self._lock:
            self._factories[name] = factory
            logger.debug(f"Registered factory: {name}")

    def register_singleton(self, name: str, factory: Callable) -> None:
        """Register a singleton factory"""
        with self._lock:
            self._factories[name] = factory
            self._singletons[name] = None
            logger.debug(f"Registered singleton: {name}")

    def resolve(self, name: str) -> Any:
        """Resolve a service by name"""
        with self._lock:
            # Check instances first
            if name in self._services:
                return self._services[name]

            # Check singletons
            if name in self._singletons:
                if self._singletons[name] is None:
                    self._singletons[name] = self._factories[name]()
                return self._singletons[name]

            # Check factories
            if name in self._factories:
                return self._factories[name]()

            raise ValueError(f"Service '{name}' not found")

    def is_registered(self, name: str) -> bool:
        """Check if service is registered"""
        with self._lock:
            return (name in self._services or
                   name in self._factories or
                   name in self._singletons)


class EventBus:
    """Thread-safe event bus for observer pattern"""

    def __init__(self):
        self._observers: Dict[EventType, Set[Observer]] = {}
        self._lock = threading.RLock()
        self._event_history: List[Event] = []
        self._max_history = 1000

    def subscribe(self, event_type: EventType, observer: Observer) -> None:
        """Subscribe observer to event type"""
        with self._lock:
            if event_type not in self._observers:
                self._observers[event_type] = set()
            self._observers[event_type].add(observer)
            logger.debug(f"Observer subscribed to {event_type}")

    def unsubscribe(self, event_type: EventType, observer: Observer) -> None:
        """Unsubscribe observer from event type"""
        with self._lock:
            if event_type in self._observers:
                self._observers[event_type].discard(observer)
                logger.debug(f"Observer unsubscribed from {event_type}")

    def publish(self, event: Event) -> None:
        """Publish event to all subscribers"""
        with self._lock:
            # Add to history
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history = self._event_history[-self._max_history:]

            # Notify observers
            if event.event_type in self._observers:
                observers = self._observers[event.event_type].copy()
                for observer in observers:
                    try:
                        observer.notify(event)
                    except Exception as e:
                        logger.error(f"Error notifying observer: {e}")

    def get_event_history(self, event_type: Optional[EventType] = None) -> List[Event]:
        """Get event history, optionally filtered by type"""
        with self._lock:
            if event_type is None:
                return self._event_history.copy()
            return [e for e in self._event_history if e.event_type == event_type]


class CommandManager:
    """Command manager with undo/redo support"""

    def __init__(self, max_history: int = 100):
        self._history: List[Command] = []
        self._current_index = -1
        self._max_history = max_history
        self._lock = threading.Lock()

    def execute(self, command: Command) -> Any:
        """Execute command and add to history"""
        with self._lock:
            try:
                result = command.execute()

                # Remove any commands after current index
                self._history = self._history[:self._current_index + 1]

                # Add new command
                self._history.append(command)
                self._current_index += 1

                # Limit history size
                if len(self._history) > self._max_history:
                    self._history = self._history[-self._max_history:]
                    self._current_index = len(self._history) - 1

                logger.debug(f"Command executed: {type(command).__name__}")
                return result

            except Exception as e:
                logger.error(f"Command execution failed: {e}")
                raise

    def undo(self) -> bool:
        """Undo last command"""
        with self._lock:
            if self._current_index >= 0:
                try:
                    command = self._history[self._current_index]
                    command.undo()
                    self._current_index -= 1
                    logger.debug(f"Command undone: {type(command).__name__}")
                    return True
                except Exception as e:
                    logger.error(f"Command undo failed: {e}")
                    return False
            return False

    def redo(self) -> bool:
        """Redo next command"""
        with self._lock:
            if self._current_index < len(self._history) - 1:
                try:
                    self._current_index += 1
                    command = self._history[self._current_index]
                    command.execute()
                    logger.debug(f"Command redone: {type(command).__name__}")
                    return True
                except Exception as e:
                    logger.error(f"Command redo failed: {e}")
                    self._current_index -= 1
                    return False
            return False

    def can_undo(self) -> bool:
        """Check if undo is possible"""
        return self._current_index >= 0

    def can_redo(self) -> bool:
        """Check if redo is possible"""
        return self._current_index < len(self._history) - 1


class StrategyManager:
    """Strategy manager for algorithm selection"""

    def __init__(self):
        self._strategies: Dict[str, Strategy] = {}
        self._default_strategy: Optional[str] = None
        self._lock = threading.RLock()

    def register_strategy(self, name: str, strategy: Strategy, is_default: bool = False) -> None:
        """Register a strategy"""
        with self._lock:
            self._strategies[name] = strategy
            if is_default or self._default_strategy is None:
                self._default_strategy = name
            logger.debug(f"Strategy registered: {name}")

    def get_strategy(self, name: Optional[str] = None) -> Strategy:
        """Get strategy by name or default"""
        with self._lock:
            strategy_name = name or self._default_strategy
            if strategy_name is None:
                raise ValueError("No strategy specified and no default set")

            if strategy_name not in self._strategies:
                raise ValueError(f"Strategy '{strategy_name}' not found")

            return self._strategies[strategy_name]

    def execute_strategy(self, name: Optional[str], data: Any) -> Any:
        """Execute strategy with data"""
        strategy = self.get_strategy(name)
        return strategy.execute(data)

    def list_strategies(self) -> List[str]:
        """List all registered strategies"""
        with self._lock:
            return list(self._strategies.keys())


class ThreadSafeSingleton(type):
    """Thread-safe singleton metaclass"""

    _instances: Dict[Type, Any] = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class ServiceRegistry(metaclass=ThreadSafeSingleton):
    """Global service registry using singleton pattern"""

    def __init__(self):
        self._registry: Dict[str, Any] = {}
        self._aliases: Dict[str, str] = {}
        self._lock = threading.RLock()

    def register(self, name: str, service: Any, aliases: Optional[List[str]] = None) -> None:
        """Register a service with optional aliases"""
        with self._lock:
            self._registry[name] = service

            if aliases:
                for alias in aliases:
                    self._aliases[alias] = name

            logger.debug(f"Service registered: {name}")

    def get(self, name: str) -> Any:
        """Get service by name or alias"""
        with self._lock:
            # Check aliases first
            if name in self._aliases:
                name = self._aliases[name]

            if name not in self._registry:
                raise ValueError(f"Service '{name}' not found")

            return self._registry[name]

    def unregister(self, name: str) -> bool:
        """Unregister a service"""
        with self._lock:
            if name in self._registry:
                del self._registry[name]

                # Remove aliases
                aliases_to_remove = [alias for alias, target in self._aliases.items() if target == name]
                for alias in aliases_to_remove:
                    del self._aliases[alias]

                logger.debug(f"Service unregistered: {name}")
                return True
            return False


class ObjectBuilder(Generic[T]):
    """Builder pattern for complex object creation"""

    def __init__(self, object_class: Type[T]):
        self._object_class = object_class
        self._attributes: Dict[str, Any] = {}
        self._validators: List[Callable[[Dict[str, Any]], bool]] = []

    def set_attribute(self, name: str, value: Any) -> ObjectBuilder[T]:
        """Set an attribute value"""
        self._attributes[name] = value
        return self

    def add_validator(self, validator: Callable[[Dict[str, Any]], bool]) -> ObjectBuilder[T]:
        """Add a validation function"""
        self._validators.append(validator)
        return self

    def build(self) -> T:
        """Build the object with validation"""
        # Run validators
        for validator in self._validators:
            if not validator(self._attributes):
                raise ValueError("Object validation failed")

        try:
            # Try to create object with attributes
            return self._object_class(**self._attributes)
        except TypeError:
            # If direct instantiation fails, try setting attributes after creation
            obj = self._object_class()
            for name, value in self._attributes.items():
                setattr(obj, name, value)
            return obj


class AdapterRegistry:
    """Registry for adapter pattern implementations"""

    def __init__(self):
        self._adapters: Dict[str, Callable] = {}
        self._lock = threading.RLock()

    def register_adapter(self, source_type: str, target_type: str, adapter: Callable) -> None:
        """Register an adapter function"""
        key = f"{source_type}->{target_type}"
        with self._lock:
            self._adapters[key] = adapter
            logger.debug(f"Adapter registered: {key}")

    def adapt(self, data: Any, source_type: str, target_type: str) -> Any:
        """Adapt data from source type to target type"""
        key = f"{source_type}->{target_type}"
        with self._lock:
            if key not in self._adapters:
                raise ValueError(f"No adapter found for {key}")
            return self._adapters[key](data)

    def has_adapter(self, source_type: str, target_type: str) -> bool:
        """Check if adapter exists"""
        key = f"{source_type}->{target_type}"
        with self._lock:
            return key in self._adapters


class SimpleFacade:
    """Facade pattern for simplified interface to complex subsystems"""

    def __init__(self):
        self.container = DependencyInjectionContainer()
        self.event_bus = EventBus()
        self.command_manager = CommandManager()
        self.strategy_manager = StrategyManager()
        self.adapter_registry = AdapterRegistry()
        self.service_registry = ServiceRegistry()

    def initialize(self) -> None:
        """Initialize all subsystems"""
        logger.info("Initializing facade subsystems...")

        # Register core services
        self.container.register_instance("event_bus", self.event_bus)
        self.container.register_instance("command_manager", self.command_manager)
        self.container.register_instance("strategy_manager", self.strategy_manager)

        logger.info("Facade initialization completed")

    def process_with_strategy(self, strategy_name: str, data: Any) -> Any:
        """Process data using specified strategy"""
        try:
            result = self.strategy_manager.execute_strategy(strategy_name, data)

            # Publish success event
            event = Event(
                event_type=EventType.OPERATION_COMPLETED,
                source="facade",
                data={"strategy": strategy_name, "result_type": type(result).__name__}
            )
            self.event_bus.publish(event)

            return result
        except Exception as e:
            # Publish error event
            error_event = Event(
                event_type=EventType.ERROR_OCCURRED,
                source="facade",
                data={"strategy": strategy_name, "error": str(e)}
            )
            self.event_bus.publish(error_event)
            raise

    def execute_command_with_undo(self, command: Command) -> Any:
        """Execute command with undo support"""
        return self.command_manager.execute(command)

    def adapt_data(self, data: Any, source_type: str, target_type: str) -> Any:
        """Adapt data between types"""
        return self.adapter_registry.adapt(data, source_type, target_type)


# Example implementations
@dataclass
class ProcessingTask:
    """Example data class for builder pattern"""
    name: str
    priority: int = 1
    timeout: float = 30.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class LoggingObserver:
    """Example observer implementation"""

    def __init__(self, name: str):
        self.name = name

    def notify(self, event: Event) -> None:
        logger.info(f"Observer {self.name} received event: {event.event_type} from {event.source}")


class DataProcessingCommand:
    """Example command implementation"""

    def __init__(self, data: Any, processor: Callable):
        self.data = data
        self.processor = processor
        self.original_data = copy.deepcopy(data)
        self.result = None

    def execute(self) -> Any:
        self.result = self.processor(self.data)
        return self.result

    def undo(self) -> Any:
        # Restore original data
        self.data = copy.deepcopy(self.original_data)
        return self.data


class SortingStrategy:
    """Example strategy implementation"""

    def __init__(self, algorithm: str):
        self.algorithm = algorithm

    def execute(self, data: List) -> List:
        if self.algorithm == "quicksort":
            return self._quicksort(data.copy())
        elif self.algorithm == "bubblesort":
            return self._bubblesort(data.copy())
        else:
            return sorted(data)

    def _quicksort(self, arr: List) -> List:
        if len(arr) <= 1:
            return arr
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        return self._quicksort(left) + middle + self._quicksort(right)

    def _bubblesort(self, arr: List) -> List:
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr


# Convenience functions
def create_facade() -> SimpleFacade:
    """Create and initialize a facade"""
    facade = SimpleFacade()
    facade.initialize()
    return facade


def create_task_builder() -> ObjectBuilder[ProcessingTask]:
    """Create a builder for ProcessingTask"""
    def validate_priority(attrs: Dict[str, Any]) -> bool:
        return attrs.get('priority', 1) > 0

    return (ObjectBuilder(ProcessingTask)
            .add_validator(validate_priority))


if __name__ == "__main__":
    # Demonstration
    print("Architecture Patterns Demo")

    # Create facade
    facade = create_facade()

    # Register strategies
    facade.strategy_manager.register_strategy("quick", SortingStrategy("quicksort"), True)
    facade.strategy_manager.register_strategy("bubble", SortingStrategy("bubblesort"))

    # Add observer
    observer = LoggingObserver("demo_observer")
    facade.event_bus.subscribe(EventType.OPERATION_COMPLETED, observer)

    # Process data
    data = [64, 34, 25, 12, 22, 11, 90]
    result = facade.process_with_strategy("quick", data)
    print(f"Sorted result: {result}")

    # Use builder
    task = (create_task_builder()
            .set_attribute("name", "demo_task")
            .set_attribute("priority", 5)
            .build())
    print(f"Built task: {task}")

    print("Demo completed!")
