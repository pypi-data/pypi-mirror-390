"""
Plugin System for QuickInsights

Provides a flexible plugin architecture for extending functionality.
"""

import os
import sys
import importlib
import importlib.util
import inspect
import threading
import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, Callable, Union, Awaitable
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PluginType(Enum):
    """Plugin types"""
    ANALYZER = "analyzer"
    VISUALIZER = "visualizer"
    CLEANER = "cleaner"
    OPTIMIZER = "optimizer"
    EXPORTER = "exporter"
    CUSTOM = "custom"


class PluginPriority(Enum):
    """Plugin priority levels"""
    LOW = 1
    NORMAL = 5
    HIGH = 10
    CRITICAL = 20


@dataclass
class PluginInfo:
    """Plugin information"""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    priority: PluginPriority
    dependencies: List[str]
    entry_point: str
    enabled: bool = True
    loaded: bool = False


class PluginInterface(ABC):
    """Base interface for all plugins"""
    
    @abstractmethod
    def get_info(self) -> PluginInfo:
        """Get plugin information"""
        pass
    
    @abstractmethod
    def initialize(self, context: Dict[str, Any]) -> None:
        """Initialize the plugin"""
        pass
    
    @abstractmethod
    def execute(self, data: Any, **kwargs) -> Any:
        """Execute the plugin"""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup plugin resources"""
        pass
    
    def validate_dependencies(self) -> bool:
        """Validate plugin dependencies"""
        return True


class AnalyzerPlugin(PluginInterface):
    """Base class for analyzer plugins"""
    
    @abstractmethod
    def analyze(self, data: Any, **kwargs) -> Dict[str, Any]:
        """Analyze data"""
        pass
    
    def execute(self, data: Any, **kwargs) -> Any:
        """Execute analysis"""
        return self.analyze(data, **kwargs)


class VisualizerPlugin(PluginInterface):
    """Base class for visualizer plugins"""
    
    @abstractmethod
    def visualize(self, data: Any, **kwargs) -> Any:
        """Create visualization"""
        pass
    
    def execute(self, data: Any, **kwargs) -> Any:
        """Execute visualization"""
        return self.visualize(data, **kwargs)


class CleanerPlugin(PluginInterface):
    """Base class for data cleaner plugins"""
    
    @abstractmethod
    def clean(self, data: Any, **kwargs) -> Any:
        """Clean data"""
        pass
    
    def execute(self, data: Any, **kwargs) -> Any:
        """Execute cleaning"""
        return self.clean(data, **kwargs)


class PluginManager:
    """Manages plugin loading, registration, and execution"""
    
    def __init__(self):
        self._plugins: Dict[str, PluginInterface] = {}
        self._plugin_info: Dict[str, PluginInfo] = {}
        self._plugin_directories: List[str] = []
        self._context: Dict[str, Any] = {}
        self._lock = threading.RLock()
        
        # Register default plugin directories
        self._plugin_directories = [
            os.path.join(os.path.dirname(__file__), "plugins"),
            os.path.join(os.getcwd(), "plugins"),
            os.path.expanduser("~/.quickinsights/plugins")
        ]
    
    def add_plugin_directory(self, directory: str) -> None:
        """Add a plugin directory"""
        with self._lock:
            if directory not in self._plugin_directories:
                self._plugin_directories.append(directory)
                logger.info(f"Added plugin directory: {directory}")
    
    def load_plugin_from_file(self, file_path: str) -> Optional[PluginInterface]:
        """Load plugin from a Python file"""
        try:
            spec = importlib.util.spec_from_file_location("plugin", file_path)
            if spec is None or spec.loader is None:
                logger.error(f"Could not load plugin from {file_path}")
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin class
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, PluginInterface) and 
                    obj != PluginInterface):
                    plugin_class = obj
                    break
            
            if plugin_class is None:
                logger.error(f"No plugin class found in {file_path}")
                return None
            
            # Create plugin instance
            plugin = plugin_class()
            return plugin
            
        except Exception as e:
            logger.error(f"Error loading plugin from {file_path}: {e}")
            return None
    
    def load_plugin_from_module(self, module_name: str) -> Optional[PluginInterface]:
        """Load plugin from a module"""
        try:
            module = importlib.import_module(module_name)
            
            # Find plugin class
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, PluginInterface) and 
                    obj != PluginInterface):
                    plugin_class = obj
                    break
            
            if plugin_class is None:
                logger.error(f"No plugin class found in {module_name}")
                return None
            
            # Create plugin instance
            plugin = plugin_class()
            return plugin
            
        except Exception as e:
            logger.error(f"Error loading plugin from {module_name}: {e}")
            return None
    
    def discover_plugins(self) -> List[PluginInterface]:
        """Discover and load plugins from all directories"""
        discovered_plugins = []
        
        with self._lock:
            for directory in self._plugin_directories:
                if not os.path.exists(directory):
                    continue
                
                for file_path in Path(directory).rglob("*.py"):
                    if file_path.name.startswith("__"):
                        continue
                    
                    plugin = self.load_plugin_from_file(str(file_path))
                    if plugin is not None:
                        discovered_plugins.append(plugin)
        
        return discovered_plugins
    
    def register_plugin(self, plugin: PluginInterface) -> bool:
        """Register a plugin"""
        try:
            with self._lock:
                info = plugin.get_info()
                
                # Validate dependencies
                if not plugin.validate_dependencies():
                    logger.error(f"Plugin {info.name} failed dependency validation")
                    return False
                
                # Check for conflicts
                if info.name in self._plugins:
                    logger.warning(f"Plugin {info.name} already registered, replacing")
                
                # Initialize plugin
                plugin.initialize(self._context)
                
                # Register plugin
                self._plugins[info.name] = plugin
                self._plugin_info[info.name] = info
                info.loaded = True
                
                logger.info(f"Plugin registered: {info.name} v{info.version}")
                return True
                
        except Exception as e:
            logger.error(f"Error registering plugin: {e}")
            return False
    
    def unregister_plugin(self, name: str) -> bool:
        """Unregister a plugin"""
        with self._lock:
            if name in self._plugins:
                plugin = self._plugins[name]
                plugin.cleanup()
                del self._plugins[name]
                del self._plugin_info[name]
                logger.info(f"Plugin unregistered: {name}")
                return True
            return False
    
    def get_plugin(self, name: str) -> Optional[PluginInterface]:
        """Get a plugin by name"""
        with self._lock:
            return self._plugins.get(name)
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[PluginInterface]:
        """Get plugins by type"""
        with self._lock:
            return [
                plugin for plugin in self._plugins.values()
                if plugin.get_info().plugin_type == plugin_type
            ]
    
    def get_plugins_by_priority(self, plugin_type: Optional[PluginType] = None) -> List[PluginInterface]:
        """Get plugins sorted by priority"""
        with self._lock:
            plugins = list(self._plugins.values())
            
            if plugin_type is not None:
                plugins = [p for p in plugins if p.get_info().plugin_type == plugin_type]
            
            return sorted(plugins, key=lambda p: p.get_info().priority.value, reverse=True)
    
    def execute_plugin(self, name: str, data: Any, **kwargs) -> Any:
        """Execute a plugin (synchronous)"""
        with self._lock:
            plugin = self._plugins.get(name)
            if plugin is None:
                raise ValueError(f"Plugin '{name}' not found")
            
            plugin_info = self._plugin_info.get(name)
            if plugin_info is None or not plugin_info.enabled:
                raise ValueError(f"Plugin '{name}' is disabled")
        
        # Execute outside lock to prevent deadlock
        # If plugin.execute is async, it will be handled by async wrapper
        return plugin.execute(data, **kwargs)
    
    async def execute_plugin_async(self, name: str, data: Any, **kwargs) -> Any:
        """Execute a plugin asynchronously (async-safe)"""
        # Get plugin info with lock
        with self._lock:
            plugin = self._plugins.get(name)
            if plugin is None:
                raise ValueError(f"Plugin '{name}' not found")
            
            plugin_info = self._plugin_info.get(name)
            if plugin_info is None or not plugin_info.enabled:
                raise ValueError(f"Plugin '{name}' is disabled")
        
        # Check if plugin has async execute method
        if asyncio.iscoroutinefunction(plugin.execute):
            # Plugin is async, await directly
            return await plugin.execute(data, **kwargs)
        else:
            # Plugin is sync, run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                lambda: plugin.execute(data, **kwargs)
            )
    
    def execute_plugins_by_type(self, plugin_type: PluginType, data: Any, **kwargs) -> List[Any]:
        """Execute all plugins of a specific type (synchronous)"""
        results = []
        
        # Get plugins without holding lock during execution
        with self._lock:
            plugins = list(self._plugins.values())
            if plugin_type is not None:
                plugins = [p for p in plugins if p.get_info().plugin_type == plugin_type]
            plugins = sorted(plugins, key=lambda p: p.get_info().priority.value, reverse=True)
        
        # Execute plugins without holding lock to prevent deadlock
        for plugin in plugins:
            if plugin.get_info().enabled:
                try:
                    result = plugin.execute(data, **kwargs)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error executing plugin {plugin.get_info().name}: {e}")
        
        return results
    
    async def execute_plugins_by_type_async(self, plugin_type: PluginType, data: Any, **kwargs) -> List[Any]:
        """Execute all plugins of a specific type asynchronously (async-safe)"""
        # Get plugins with lock
        with self._lock:
            plugins = list(self._plugins.values())
            if plugin_type is not None:
                plugins = [p for p in plugins if p.get_info().plugin_type == plugin_type]
            plugins = sorted(plugins, key=lambda p: p.get_info().priority.value, reverse=True)
        
        # Execute plugins concurrently if async, sequentially if sync
        # Use asyncio.gather for concurrent execution of async plugins
        async_tasks = []
        sync_plugins = []
        
        for plugin in plugins:
            if plugin.get_info().enabled:
                if asyncio.iscoroutinefunction(plugin.execute):
                    # Create task for async plugin
                    async_tasks.append(
                        self._execute_async_plugin_safe(plugin, data, **kwargs)
                    )
                else:
                    sync_plugins.append(plugin)
        
        # Execute async plugins concurrently
        async_results = []
        if async_tasks:
            async_results = await asyncio.gather(*async_tasks, return_exceptions=True)
        
        # Filter out exceptions from async results
        for i, result in enumerate(async_results):
            if isinstance(result, Exception):
                logger.error(f"Error executing async plugin: {result}")
            else:
                async_results[i] = result
        
        # Execute sync plugins sequentially
        sync_results = []
        for plugin in sync_plugins:
            try:
                loop = asyncio.get_event_loop()
                # Fix lambda closure issue - capture plugin in closure
                result = await loop.run_in_executor(
                    None,
                    lambda p=plugin, d=data, k=kwargs: p.execute(d, **k)
                )
                sync_results.append(result)
            except Exception as e:
                logger.error(f"Error executing plugin {plugin.get_info().name}: {e}")
        
        # Combine results (async first, then sync, maintaining priority order)
        results = [r for r in async_results if not isinstance(r, Exception)] + sync_results
        return results
    
    async def _execute_async_plugin_safe(self, plugin: PluginInterface, data: Any, **kwargs) -> Any:
        """Safely execute an async plugin with error handling"""
        try:
            return await plugin.execute(data, **kwargs)
        except Exception as e:
            logger.error(f"Error executing async plugin {plugin.get_info().name}: {e}")
            raise
    
    def set_context(self, context: Dict[str, Any]) -> None:
        """Set plugin context"""
        with self._lock:
            self._context.update(context)
    
    def get_plugin_info(self, name: str) -> Optional[PluginInfo]:
        """Get plugin information"""
        with self._lock:
            return self._plugin_info.get(name)
    
    def list_plugins(self) -> List[PluginInfo]:
        """List all registered plugins"""
        with self._lock:
            return list(self._plugin_info.values())
    
    def enable_plugin(self, name: str) -> bool:
        """Enable a plugin"""
        with self._lock:
            if name in self._plugin_info:
                self._plugin_info[name].enabled = True
                logger.info(f"Plugin enabled: {name}")
                return True
            return False
    
    def disable_plugin(self, name: str) -> bool:
        """Disable a plugin"""
        with self._lock:
            if name in self._plugin_info:
                self._plugin_info[name].enabled = False
                logger.info(f"Plugin disabled: {name}")
                return True
            return False
    
    def cleanup(self) -> None:
        """Cleanup all plugins"""
        with self._lock:
            for plugin in self._plugins.values():
                try:
                    plugin.cleanup()
                except Exception as e:
                    logger.error(f"Error cleaning up plugin: {e}")
            
            self._plugins.clear()
            self._plugin_info.clear()


# Global plugin manager instance
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager instance"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager


def register_plugin(plugin: PluginInterface) -> bool:
    """Register a plugin with the global manager"""
    return get_plugin_manager().register_plugin(plugin)


def unregister_plugin(name: str) -> bool:
    """Unregister a plugin from the global manager"""
    return get_plugin_manager().unregister_plugin(name)


def execute_plugin(name: str, data: Any, **kwargs) -> Any:
    """Execute a plugin (synchronous)"""
    return get_plugin_manager().execute_plugin(name, data, **kwargs)


async def execute_plugin_async(name: str, data: Any, **kwargs) -> Any:
    """Execute a plugin asynchronously (async-safe)"""
    return await get_plugin_manager().execute_plugin_async(name, data, **kwargs)


def execute_plugins_by_type(plugin_type: PluginType, data: Any, **kwargs) -> List[Any]:
    """Execute all plugins of a specific type (synchronous)"""
    return get_plugin_manager().execute_plugins_by_type(plugin_type, data, **kwargs)


async def execute_plugins_by_type_async(plugin_type: PluginType, data: Any, **kwargs) -> List[Any]:
    """Execute all plugins of a specific type asynchronously (async-safe)"""
    return await get_plugin_manager().execute_plugins_by_type_async(plugin_type, data, **kwargs)


def discover_and_register_plugins() -> int:
    """Discover and register all available plugins"""
    manager = get_plugin_manager()
    plugins = manager.discover_plugins()
    
    registered_count = 0
    for plugin in plugins:
        if manager.register_plugin(plugin):
            registered_count += 1
    
    logger.info(f"Discovered and registered {registered_count} plugins")
    return registered_count
