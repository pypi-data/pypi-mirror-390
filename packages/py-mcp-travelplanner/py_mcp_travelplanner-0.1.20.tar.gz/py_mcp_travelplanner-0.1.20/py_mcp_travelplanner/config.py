"""Runtime Configuration Manager for MCP Travel Planner.

This module provides centralized configuration management for the MCP Travel Planner
application. It supports loading configuration from multiple sources with the
following precedence (highest to lowest):

1. Environment variables
2. .env file (in project root or specified path)
3. runtime_config.yaml file
4. Default values

Configuration can be accessed via the global `config` instance or by calling
`get_config()` to ensure initialization.

Example Usage:
    from py_mcp_travelplanner.config import get_config
    
    config = get_config()
    api_key = config.get('SERPAPI_KEY')
    port = config.get('CONTROL_SERVER_PORT', default=8787)
    
Environment Variables:
    MCP_CONFIG_PATH: Path to runtime_config.yaml (default: ./runtime_config.yaml)
    MCP_ENV_FILE: Path to .env file (default: ./.env)
    MCP_LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
"""
from __future__ import annotations

import logging
import os
import pathlib
from typing import Any, Dict, Optional

LOG = logging.getLogger("py_mcp_travelplanner.config")

# Try to import optional dependencies
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    LOG.debug("PyYAML not available, YAML config files will not be supported")

try:
    from dotenv import dotenv_values
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    LOG.debug("python-dotenv not available, .env file support will be limited")


class RuntimeConfig:
    """Runtime configuration manager with multi-source support.
    
    This class manages configuration from multiple sources:
    - Environment variables (highest priority)
    - .env files
    - YAML configuration files
    - Default values (lowest priority)
    
    The configuration is loaded lazily on first access and can be reloaded
    at any time using the reload() method.
    """
    
    def __init__(self, config_path: Optional[str | pathlib.Path] = None,
                 env_file: Optional[str | pathlib.Path] = None,
                 auto_load: bool = True):
        """Initialize the runtime configuration manager.
        
        Args:
            config_path: Path to runtime_config.yaml file. If None, uses
                        MCP_CONFIG_PATH env var or ./runtime_config.yaml
            env_file: Path to .env file. If None, uses MCP_ENV_FILE env var
                     or ./.env
            auto_load: If True, load configuration immediately
        """
        self._config: Dict[str, Any] = {}
        self._loaded = False
        self._config_path = config_path
        self._env_file = env_file
        self._defaults = self._get_defaults()
        
        if auto_load:
            self.load()
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Return default configuration values.
        
        These are the fallback values used when no other configuration
        source provides a value.
        """
        return {
            # Server Configuration
            'CONTROL_SERVER_HOST': '127.0.0.1',
            'CONTROL_SERVER_PORT': 8787,
            'MCP_SERVER_NAME': 'py_mcp_travelplanner_unified',
            
            # Logging Configuration
            'LOG_LEVEL': 'INFO',
            'LOG_FORMAT': '%(levelname)s:%(name)s: %(message)s',
            
            # Server Process Management
            'SERVER_START_TIMEOUT': 30.0,
            'SERVER_STOP_TIMEOUT': 5.0,
            'HEALTH_CHECK_INTERVAL': 10.0,
            
            # API Keys (should be overridden by env vars or .env)
            'SERPAPI_KEY': None,  # Required for all services
            
            # Server Discovery
            'SERVERS_DIR': None,  # Auto-detected if None
            'ENABLE_AUTO_DISCOVERY': True,
            
            # Development/Debug
            'DRY_RUN': False,
            'VERBOSE': False,
            'DEBUG_MODE': False,
            
            # PID File Management
            'PID_FILE_DIR': '.mcp_pids',
            'ENABLE_PID_TRACKING': True,
        }
    
    def _resolve_path(self, path: Optional[str | pathlib.Path],
                     env_var: str, default: str) -> pathlib.Path:
        """Resolve a configuration file path from multiple sources.
        
        Args:
            path: Explicitly provided path
            env_var: Environment variable name to check
            default: Default filename to use
            
        Returns:
            Resolved pathlib.Path
        """
        if path:
            return pathlib.Path(path)
        
        # Check environment variable
        env_path = os.environ.get(env_var)
        if env_path:
            return pathlib.Path(env_path)
        
        # Use default (relative to project root)
        repo_root = pathlib.Path(__file__).resolve().parents[1]
        return repo_root / default
    
    def load(self) -> None:
        """Load configuration from all sources in priority order.
        
        Loading order (lowest to highest priority):
        1. Default values
        2. YAML configuration file
        3. .env file
        4. Environment variables
        """
        LOG.debug("Loading runtime configuration")
        
        # Start with defaults
        self._config = self._defaults.copy()
        
        # Load from YAML file
        self._load_from_yaml()
        
        # Load from .env file
        self._load_from_env_file()
        
        # Override with environment variables
        self._load_from_environment()
        
        # Apply log level
        self._configure_logging()
        
        self._loaded = True
        LOG.info("Runtime configuration loaded successfully")
    
    def _load_from_yaml(self) -> None:
        """Load configuration from YAML file."""
        if not YAML_AVAILABLE:
            LOG.debug("Skipping YAML config: PyYAML not installed")
            return
        
        config_path = self._resolve_path(
            self._config_path,
            'MCP_CONFIG_PATH',
            'runtime_config.yaml'
        )
        
        if not config_path.exists():
            LOG.debug("YAML config file not found: %s", config_path)
            return
        
        try:
            with open(config_path, 'r') as f:
                yaml_config = yaml.safe_load(f) or {}
            
            # Merge YAML config into self._config
            self._config.update(yaml_config)
            LOG.info("Loaded configuration from %s", config_path)
        except Exception as exc:
            LOG.warning("Failed to load YAML config from %s: %s", config_path, exc)
    
    def _load_from_env_file(self) -> None:
        """Load configuration from .env file."""
        env_path = self._resolve_path(
            self._env_file,
            'MCP_ENV_FILE',
            '.env'
        )
        
        if not env_path.exists():
            LOG.debug(".env file not found: %s", env_path)
            return
        
        try:
            if DOTENV_AVAILABLE:
                env_vars = dotenv_values(str(env_path))
            else:
                env_vars = self._parse_env_file_simple(env_path)
            
            # Update config with env vars, converting types where appropriate
            for key, value in env_vars.items():
                if value is not None:
                    self._config[key] = self._convert_type(key, value)
            
            LOG.info("Loaded configuration from %s", env_path)
        except Exception as exc:
            LOG.warning("Failed to load .env file from %s: %s", env_path, exc)
    
    def _parse_env_file_simple(self, path: pathlib.Path) -> Dict[str, str]:
        """Simple .env file parser (fallback when python-dotenv not available)."""
        env_vars = {}
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip().strip('"').strip("'")
                    env_vars[key.strip()] = value
        return env_vars
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables.
        
        This has the highest priority and will override values from
        YAML and .env files.
        """
        for key in self._defaults.keys():
            env_value = os.environ.get(key)
            if env_value is not None:
                self._config[key] = self._convert_type(key, env_value)
                LOG.debug("Loaded %s from environment", key)
    
    def _convert_type(self, key: str, value: Any) -> Any:
        """Convert string values to appropriate types based on defaults."""
        if value is None or value == '':
            return None
        
        default_value = self._defaults.get(key)
        
        # If we have a default, try to match its type
        if default_value is not None:
            if isinstance(default_value, bool):
                return str(value).lower() in ('true', '1', 'yes', 'on')
            elif isinstance(default_value, int):
                try:
                    return int(value)
                except ValueError:
                    LOG.warning("Cannot convert %s to int: %s", key, value)
                    return value
            elif isinstance(default_value, float):
                try:
                    return float(value)
                except ValueError:
                    LOG.warning("Cannot convert %s to float: %s", key, value)
                    return value
        
        # Return as-is if no type conversion needed
        return value
    
    def _configure_logging(self) -> None:
        """Configure logging based on configuration."""
        # Access _config directly to avoid recursion
        log_level_str = self._config.get('LOG_LEVEL', 'INFO')
        log_format = self._config.get('LOG_FORMAT', '%(levelname)s:%(name)s: %(message)s')

        try:
            log_level = getattr(logging, log_level_str.upper())
            logging.basicConfig(level=log_level, format=log_format)
            LOG.info("Logging configured: level=%s", log_level_str)
        except (AttributeError, ValueError) as exc:
            LOG.warning("Invalid log level '%s': %s", log_level_str, exc)
    
    def reload(self) -> None:
        """Reload configuration from all sources."""
        LOG.info("Reloading runtime configuration")
        self._loaded = False
        self.load()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key to retrieve
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if not self._loaded:
            self.load()
        
        return self._config.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values as a dictionary.
        
        Returns:
            Dictionary of all configuration values
        """
        if not self._loaded:
            self.load()
        
        return self._config.copy()
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value at runtime.
        
        Note: This only affects the in-memory configuration and will
        not persist across restarts.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        if not self._loaded:
            self.load()
        
        self._config[key] = value
        LOG.debug("Set configuration: %s=%s", key, value)
    
    def has(self, key: str) -> bool:
        """Check if a configuration key exists.
        
        Args:
            key: Configuration key to check
            
        Returns:
            True if key exists, False otherwise
        """
        if not self._loaded:
            self.load()
        
        return key in self._config
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Export configuration as a dictionary.
        
        Args:
            include_sensitive: If False, mask sensitive values (API keys, etc.)
            
        Returns:
            Dictionary of configuration values
        """
        if not self._loaded:
            self.load()
        
        config_copy = self._config.copy()
        
        if not include_sensitive:
            sensitive_keys = ['SERPAPI_KEY']
            for key in sensitive_keys:
                if key in config_copy and config_copy[key]:
                    config_copy[key] = '***REDACTED***'
        
        return config_copy


# Global configuration instance
_global_config: Optional[RuntimeConfig] = None


def get_config(reload: bool = False) -> RuntimeConfig:
    """Get the global configuration instance.
    
    Args:
        reload: If True, reload configuration from sources
        
    Returns:
        Global RuntimeConfig instance
    """
    global _global_config
    
    if _global_config is None:
        _global_config = RuntimeConfig(auto_load=True)
    elif reload:
        _global_config.reload()
    
    return _global_config


def reset_config() -> None:
    """Reset the global configuration instance.
    
    This is primarily useful for testing.
    """
    global _global_config
    _global_config = None


# Convenience function for common use case
def get_api_key(key_name: str) -> Optional[str]:
    """Get an API key from configuration.
    
    Args:
        key_name: Name of the API key (e.g., 'SERPAPI_KEY')
        
    Returns:
        API key value or None if not set
    """
    return get_config().get(key_name)

