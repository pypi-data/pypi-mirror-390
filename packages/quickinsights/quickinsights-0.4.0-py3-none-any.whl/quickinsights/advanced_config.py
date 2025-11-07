"""
Advanced Configuration Management System for QuickInsights

Provides enhanced configuration management with validation, hot-reloading,
environment-specific configs, and plugin integration.
"""

import os
import json
import yaml
import toml
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Callable, Type
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
import threading
import time
from datetime import datetime
import hashlib
import copy

from .error_handling import ConfigurationError

logger = logging.getLogger(__name__)


class ConfigFormat(Enum):
    """Supported configuration formats"""
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    ENV = "env"


class ConfigSource(Enum):
    """Configuration sources"""
    DEFAULT = "default"
    FILE = "file"
    ENVIRONMENT = "environment"
    RUNTIME = "runtime"
    PLUGIN = "plugin"


@dataclass
class ConfigMetadata:
    """Configuration metadata"""
    source: ConfigSource
    timestamp: datetime
    version: str = "1.0.0"
    checksum: Optional[str] = None
    description: Optional[str] = None


@dataclass
class ConfigValidationRule:
    """Configuration validation rule"""
    field_path: str
    validator: Callable[[Any], bool]
    error_message: str
    required: bool = True


class ConfigValidator:
    """Advanced configuration validator"""
    
    def __init__(self):
        self.rules: List[ConfigValidationRule] = []
        self.custom_validators: Dict[str, Callable] = {}
    
    def add_rule(self, rule: ConfigValidationRule) -> None:
        """Add a validation rule"""
        self.rules.append(rule)
    
    def add_custom_validator(self, name: str, validator: Callable) -> None:
        """Add a custom validator"""
        self.custom_validators[name] = validator
    
    def validate(self, config: Dict[str, Any]) -> List[str]:
        """Validate configuration against all rules"""
        errors = []
        
        for rule in self.rules:
            try:
                value = self._get_nested_value(config, rule.field_path)
                
                if value is None and rule.required:
                    errors.append(f"Required field '{rule.field_path}' is missing")
                    continue
                
                if value is not None and not rule.validator(value):
                    errors.append(f"Field '{rule.field_path}': {rule.error_message}")
                    
            except Exception as e:
                errors.append(f"Validation error for '{rule.field_path}': {e}")
        
        return errors
    
    def _get_nested_value(self, config: Dict[str, Any], path: str) -> Any:
        """Get nested value from configuration"""
        keys = path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value


class ConfigWatcher:
    """File system watcher for configuration changes"""
    
    def __init__(self, config_manager: 'AdvancedConfigManager'):
        self.config_manager = config_manager
        self.watched_files: Dict[str, float] = {}
        self.watch_thread: Optional[threading.Thread] = None
        self.stop_watching = threading.Event()
        self.callbacks: List[Callable] = []
    
    def add_callback(self, callback: Callable) -> None:
        """Add a callback for configuration changes"""
        self.callbacks.append(callback)
    
    def watch_file(self, file_path: str) -> None:
        """Start watching a configuration file"""
        if os.path.exists(file_path):
            self.watched_files[file_path] = os.path.getmtime(file_path)
    
    def start_watching(self) -> None:
        """Start the file watcher thread"""
        if self.watch_thread is None or not self.watch_thread.is_alive():
            self.watch_thread = threading.Thread(target=self._watch_loop, daemon=True)
            self.watch_thread.start()
    
    def stop(self) -> None:
        """Stop watching"""
        self.stop_watching.set()
        if self.watch_thread:
            self.watch_thread.join(timeout=1.0)
    
    def _watch_loop(self) -> None:
        """Main watching loop"""
        while not self.stop_watching.is_set():
            try:
                for file_path, last_mtime in self.watched_files.items():
                    if os.path.exists(file_path):
                        current_mtime = os.path.getmtime(file_path)
                        if current_mtime > last_mtime:
                            self.watched_files[file_path] = current_mtime
                            self._notify_change(file_path)
                
                time.sleep(1.0)  # Check every second
                
            except Exception as e:
                logger.error(f"Error in config watcher: {e}")
    
    def _notify_change(self, file_path: str) -> None:
        """Notify about configuration changes"""
        logger.info(f"Configuration file changed: {file_path}")
        
        try:
            # Reload configuration
            self.config_manager.reload_from_file(file_path)
            
            # Notify callbacks
            for callback in self.callbacks:
                try:
                    callback(file_path)
                except Exception as e:
                    logger.error(f"Error in config change callback: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to reload configuration from {file_path}: {e}")


class ConfigTemplate:
    """Configuration template for generating default configs"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.sections: Dict[str, Dict[str, Any]] = {}
        self.validators: ConfigValidator = ConfigValidator()
    
    def add_section(self, name: str, config: Dict[str, Any]) -> 'ConfigTemplate':
        """Add a configuration section"""
        self.sections[name] = config
        return self
    
    def add_validation_rule(self, rule: ConfigValidationRule) -> 'ConfigTemplate':
        """Add a validation rule"""
        self.validators.add_rule(rule)
        return self
    
    def generate_config(self) -> Dict[str, Any]:
        """Generate configuration from template"""
        return copy.deepcopy(self.sections)
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate configuration against template"""
        return self.validators.validate(config)


class AdvancedConfigManager:
    """Advanced configuration manager with hot-reloading and validation"""
    
    def __init__(self, config_file: Optional[Union[str, Path]] = None):
        self.config_file = Path(config_file) if config_file else None
        self.config: Dict[str, Any] = {}
        self.metadata: Dict[str, ConfigMetadata] = {}
        self.templates: Dict[str, ConfigTemplate] = {}
        self.validators: Dict[str, ConfigValidator] = {}
        self.watcher = ConfigWatcher(self)
        self.lock = threading.RLock()
        
        # Environment-specific configs
        self.environment = os.getenv('QUICKINSIGHTS_ENV', 'development')
        self.environment_configs: Dict[str, Dict[str, Any]] = {}
        
        # Plugin configurations
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}
        
        # Initialize with default configuration
        self._load_default_config()
        
        # Load from file if provided
        if self.config_file and self.config_file.exists():
            self._load_from_file(self.config_file)
        
        # Load environment-specific config
        self._load_environment_config()
        
        # Start file watcher if config file exists
        if self.config_file:
            self.watcher.watch_file(str(self.config_file))
            self.watcher.start_watching()
    
    def _load_default_config(self) -> None:
        """Load default configuration"""
        default_config = {
            "performance": {
                "max_memory_gb": 8.0,
                "parallel_workers": 4,
                "chunk_size": 10000,
                "cache_enabled": True,
                "cache_size_mb": 1000,
                "gpu_enabled": False,
                "gpu_memory_fraction": 0.8
            },
            "visualization": {
                "default_style": "seaborn",
                "figure_size": [12, 8],
                "dpi": 300,
                "save_format": "png",
                "show_plots": True,
                "interactive": False
            },
            "ml": {
                "random_seed": 42,
                "cross_validation_folds": 5,
                "test_size": 0.2,
                "auto_tuning": True,
                "max_iterations": 1000
            },
            "data": {
                "max_rows_display": 1000,
                "precision": 4,
                "missing_value_strategy": "auto",
                "outlier_detection": True,
                "duplicate_handling": "remove"
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file_enabled": True,
                "console_enabled": True,
                "max_file_size_mb": 10,
                "backup_count": 5
            },
            "plugins": {
                "auto_discovery": True,
                "plugin_directories": [],
                "enabled_plugins": [],
                "disabled_plugins": []
            }
        }
        
        self._merge_config(default_config, ConfigSource.DEFAULT)
    
    def _load_from_file(self, file_path: Union[str, Path]) -> None:
        """Load configuration from file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise ConfigurationError(f"Configuration file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() == '.json':
                    config_data = json.load(f)
                elif file_path.suffix.lower() in ['.yml', '.yaml']:
                    config_data = yaml.safe_load(f)
                elif file_path.suffix.lower() == '.toml':
                    config_data = toml.load(f)
                else:
                    raise ConfigurationError(f"Unsupported configuration format: {file_path.suffix}")
            
            self._merge_config(config_data, ConfigSource.FILE, str(file_path))
            logger.info(f"Configuration loaded from {file_path}")
            
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration from {file_path}: {e}")
    
    def _load_environment_config(self) -> None:
        """Load environment-specific configuration"""
        env_config_file = None
        
        # Look for environment-specific config files
        if self.config_file:
            env_config_file = self.config_file.parent / f"{self.config_file.stem}.{self.environment}{self.config_file.suffix}"
        
        if env_config_file and env_config_file.exists():
            self._load_from_file(env_config_file)
        
        # Load from environment variables
        env_config = {}
        for key, value in os.environ.items():
            if key.startswith('QUICKINSIGHTS_'):
                config_key = key[13:].lower()  # Skip 'QUICKINSIGHTS_' (13 chars)
                # Convert to nested structure: PERFORMANCE_MAX_MEMORY_GB -> performance.max_memory_gb
                parts = config_key.split('_')
                if len(parts) > 1:
                    config_key = parts[0] + '.' + '_'.join(parts[1:])
                self._set_nested_value(env_config, config_key, self._parse_env_value(value))
        
        if env_config:
            self._merge_config(env_config, ConfigSource.ENVIRONMENT)
    
    def _parse_env_value(self, value: str) -> Any:
        """Parse environment variable value"""
        # Try to parse as JSON first
        try:
            return json.loads(value)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Try to parse as boolean
        if value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        
        # Try to parse as number
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def _merge_config(self, new_config: Dict[str, Any], source: ConfigSource, file_path: Optional[str] = None) -> None:
        """Merge new configuration with existing"""
        with self.lock:
            # Deep merge configuration
            self._deep_merge(self.config, new_config)
            
            # Update metadata
            metadata = ConfigMetadata(
                source=source,
                timestamp=datetime.now(),
                checksum=self._calculate_checksum(new_config)
            )
            
            if file_path:
                self.metadata[file_path] = metadata
            else:
                self.metadata[source.value] = metadata
    
    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> None:
        """Deep merge two dictionaries"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _set_nested_value(self, config: Dict[str, Any], key_path: str, value: Any) -> None:
        """Set nested value in configuration dictionary"""
        keys = key_path.split('.')
        current = config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def _calculate_checksum(self, config: Dict[str, Any]) -> str:
        """Calculate checksum for configuration"""
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        with self.lock:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
    
    def set(self, key: str, value: Any, source: ConfigSource = ConfigSource.RUNTIME) -> None:
        """Set configuration value"""
        with self.lock:
            keys = key.split('.')
            config = self.config
            
            # Navigate to the parent of the target key
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # Set the value
            config[keys[-1]] = value
            
            # Update metadata
            metadata = ConfigMetadata(
                source=source,
                timestamp=datetime.now()
            )
            self.metadata[key] = metadata
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self.get(section, {})
    
    def set_section(self, section: str, config: Dict[str, Any], source: ConfigSource = ConfigSource.RUNTIME) -> None:
        """Set entire configuration section"""
        with self.lock:
            self.config[section] = copy.deepcopy(config)
            
            metadata = ConfigMetadata(
                source=source,
                timestamp=datetime.now()
            )
            self.metadata[section] = metadata
    
    def save_to_file(self, file_path: Union[str, Path], format: ConfigFormat = ConfigFormat.JSON) -> None:
        """Save configuration to file"""
        file_path = Path(file_path)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if format == ConfigFormat.JSON:
                    json.dump(self.config, f, indent=2, default=str)
                elif format == ConfigFormat.YAML:
                    yaml.dump(self.config, f, default_flow_style=False)
                elif format == ConfigFormat.TOML:
                    toml.dump(self.config, f)
                else:
                    raise ConfigurationError(f"Unsupported format: {format}")
            
            logger.info(f"Configuration saved to {file_path}")
            
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration to {file_path}: {e}")
    
    def reload_from_file(self, file_path: Union[str, Path]) -> None:
        """Reload configuration from file"""
        try:
            self._load_from_file(file_path)
            logger.info(f"Configuration reloaded from {file_path}")
        except Exception as e:
            logger.error(f"Failed to reload configuration from {file_path}: {e}")
            raise ConfigurationError(f"Failed to reload configuration: {e}")
    
    def validate_config(self, config: Optional[Dict[str, Any]] = None) -> List[str]:
        """Validate configuration"""
        config_to_validate = config or self.config
        errors = []
        
        # Run all registered validators
        for validator_name, validator in self.validators.items():
            try:
                validator_errors = validator.validate(config_to_validate)
                errors.extend(validator_errors)
            except Exception as e:
                errors.append(f"Validator '{validator_name}' failed: {e}")
        
        return errors
    
    def add_validator(self, name: str, validator: ConfigValidator) -> None:
        """Add a configuration validator"""
        self.validators[name] = validator
    
    def add_template(self, name: str, template: ConfigTemplate) -> None:
        """Add a configuration template"""
        self.templates[name] = template
    
    def generate_from_template(self, template_name: str) -> Dict[str, Any]:
        """Generate configuration from template"""
        if template_name not in self.templates:
            raise ConfigurationError(f"Template '{template_name}' not found")
        
        return self.templates[template_name].generate_config()
    
    def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """Get plugin-specific configuration"""
        return self.plugin_configs.get(plugin_name, {})
    
    def set_plugin_config(self, plugin_name: str, config: Dict[str, Any]) -> None:
        """Set plugin-specific configuration"""
        self.plugin_configs[plugin_name] = copy.deepcopy(config)
    
    def get_environment_config(self, environment: str) -> Dict[str, Any]:
        """Get environment-specific configuration"""
        return self.environment_configs.get(environment, {})
    
    def set_environment_config(self, environment: str, config: Dict[str, Any]) -> None:
        """Set environment-specific configuration"""
        self.environment_configs[environment] = copy.deepcopy(config)
    
    def add_change_callback(self, callback: Callable) -> None:
        """Add callback for configuration changes"""
        self.watcher.add_callback(callback)
    
    def get_metadata(self, key: Optional[str] = None) -> Union[Dict[str, ConfigMetadata], ConfigMetadata]:
        """Get configuration metadata"""
        if key:
            return self.metadata.get(key)
        return self.metadata
    
    def cleanup(self) -> None:
        """Cleanup resources"""
        self.watcher.stop()


# Global advanced config manager instance
_advanced_config_manager: Optional[AdvancedConfigManager] = None


def get_advanced_config_manager() -> AdvancedConfigManager:
    """Get the global advanced config manager instance"""
    global _advanced_config_manager
    if _advanced_config_manager is None:
        _advanced_config_manager = AdvancedConfigManager()
    return _advanced_config_manager


def get_config_value(key: str, default: Any = None) -> Any:
    """Get configuration value"""
    return get_advanced_config_manager().get(key, default)


def set_config_value(key: str, value: Any) -> None:
    """Set configuration value"""
    get_advanced_config_manager().set(key, value)


def get_config_section(section: str) -> Dict[str, Any]:
    """Get configuration section"""
    return get_advanced_config_manager().get_section(section)


def set_config_section(section: str, config: Dict[str, Any]) -> None:
    """Set configuration section"""
    get_advanced_config_manager().set_section(section, config)
