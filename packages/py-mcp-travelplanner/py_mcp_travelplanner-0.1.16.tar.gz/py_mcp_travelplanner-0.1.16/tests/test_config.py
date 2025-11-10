"""Tests for the runtime configuration module.

This module tests the multi-source configuration loading with proper
precedence handling (env vars > .env file > YAML > defaults).
"""
from __future__ import annotations

import os
import pathlib
import tempfile
from typing import Any

import pytest

from py_mcp_travelplanner.config import (
    RuntimeConfig,
    get_config,
    reset_config,
    get_api_key,
)


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary directory for config files."""
    return tmp_path


@pytest.fixture
def sample_yaml_config(temp_config_dir):
    """Create a sample YAML config file."""
    config_file = temp_config_dir / "test_config.yaml"
    config_content = """
# Test configuration
CONTROL_SERVER_HOST: "0.0.0.0"
CONTROL_SERVER_PORT: 9999
LOG_LEVEL: "DEBUG"
SERVER_START_TIMEOUT: 60.0
ENABLE_AUTO_DISCOVERY: false
SERPAPI_KEY: "yaml_test_key"
CUSTOM_YAML_VALUE: "from_yaml"

# Nested config for servers
FLIGHT_SERVER:
  MAX_RESULTS: 15
  CACHE_TTL: 7200
"""
    config_file.write_text(config_content)
    return config_file


@pytest.fixture
def sample_env_file(temp_config_dir):
    """Create a sample .env file."""
    env_file = temp_config_dir / ".env"
    env_content = """
# Test environment file
CONTROL_SERVER_PORT=8888
LOG_LEVEL=WARNING
SERPAPI_KEY=env_file_key
CUSTOM_ENV_VALUE=from_env_file
"""
    env_file.write_text(env_content)
    return env_file


@pytest.fixture
def clean_env(tmp_path):
    """Clean environment variables before and after test."""
    # Save original env vars
    original_env = os.environ.copy()
    
    # Remove config-related env vars
    keys_to_remove = [
        'CONTROL_SERVER_HOST', 'CONTROL_SERVER_PORT', 'LOG_LEVEL',
        'SERPAPI_KEY', 'MCP_CONFIG_PATH', 'MCP_ENV_FILE',
        'WEATHERSTACK_API_KEY', 'NOMINATIM_USER_AGENT',
        'CUSTOM_YAML_VALUE', 'CUSTOM_ENV_VALUE', 'CUSTOM_ENV_VAR'
    ]
    for key in keys_to_remove:
        os.environ.pop(key, None)
    
    # Point config paths to non-existent files in temp directory to avoid
    # loading from actual project runtime_config.yaml
    os.environ['MCP_CONFIG_PATH'] = str(tmp_path / 'nonexistent_config.yaml')
    os.environ['MCP_ENV_FILE'] = str(tmp_path / 'nonexistent.env')

    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)
    
    # Reset global config
    reset_config()


class TestRuntimeConfigDefaults:
    """Test default configuration values."""
    
    def test_default_values_loaded(self, clean_env):
        """Test that default values are properly set."""
        config = RuntimeConfig(auto_load=True)
        
        assert config.get('CONTROL_SERVER_HOST') == '127.0.0.1'
        assert config.get('CONTROL_SERVER_PORT') == 8787
        assert config.get('LOG_LEVEL') == 'INFO'
        assert config.get('SERVER_START_TIMEOUT') == 30.0
        assert config.get('ENABLE_AUTO_DISCOVERY') is True
        assert config.get('SERPAPI_KEY') is None
    
    def test_get_with_default(self, clean_env):
        """Test getting values with custom defaults."""
        config = RuntimeConfig(auto_load=True)
        
        assert config.get('NONEXISTENT_KEY', 'default_value') == 'default_value'
        assert config.get('CONTROL_SERVER_PORT', 9999) == 8787  # Returns actual value
    
    def test_has_method(self, clean_env):
        """Test the has() method for key existence."""
        config = RuntimeConfig(auto_load=True)
        
        assert config.has('CONTROL_SERVER_PORT') is True
        assert config.has('NONEXISTENT_KEY') is False


class TestRuntimeConfigYAML:
    """Test YAML configuration file loading."""
    
    def test_yaml_overrides_defaults(self, clean_env, sample_yaml_config):
        """Test that YAML values override defaults."""
        config = RuntimeConfig(config_path=sample_yaml_config, auto_load=True)
        
        assert config.get('CONTROL_SERVER_HOST') == '0.0.0.0'
        assert config.get('CONTROL_SERVER_PORT') == 9999
        assert config.get('LOG_LEVEL') == 'DEBUG'
        assert config.get('SERVER_START_TIMEOUT') == 60.0
        assert config.get('ENABLE_AUTO_DISCOVERY') is False
        assert config.get('SERPAPI_KEY') == 'yaml_test_key'
        assert config.get('CUSTOM_YAML_VALUE') == 'from_yaml'
    
    def test_yaml_nested_config(self, clean_env, sample_yaml_config):
        """Test that nested YAML structures are loaded."""
        config = RuntimeConfig(config_path=sample_yaml_config, auto_load=True)
        
        flight_config = config.get('FLIGHT_SERVER')
        assert flight_config is not None
        assert flight_config['MAX_RESULTS'] == 15
        assert flight_config['CACHE_TTL'] == 7200
    
    def test_missing_yaml_file(self, clean_env, temp_config_dir):
        """Test behavior when YAML file doesn't exist."""
        nonexistent = temp_config_dir / "nonexistent.yaml"
        config = RuntimeConfig(config_path=nonexistent, auto_load=True)
        
        # Should fall back to defaults
        assert config.get('CONTROL_SERVER_PORT') == 8787


class TestRuntimeConfigEnvFile:
    """Test .env file loading."""
    
    def test_env_file_overrides_yaml(self, clean_env, sample_yaml_config, sample_env_file):
        """Test that .env file overrides YAML config."""
        config = RuntimeConfig(
            config_path=sample_yaml_config,
            env_file=sample_env_file,
            auto_load=True
        )
        
        # YAML sets port to 9999, .env sets it to 8888
        assert config.get('CONTROL_SERVER_PORT') == 8888
        # .env overrides LOG_LEVEL
        assert config.get('LOG_LEVEL') == 'WARNING'
        # .env overrides SERPAPI_KEY
        assert config.get('SERPAPI_KEY') == 'env_file_key'
        # Custom value from .env
        assert config.get('CUSTOM_ENV_VALUE') == 'from_env_file'
        # YAML value not in .env should remain
        assert config.get('CUSTOM_YAML_VALUE') == 'from_yaml'
    
    def test_missing_env_file(self, clean_env, temp_config_dir):
        """Test behavior when .env file doesn't exist."""
        nonexistent = temp_config_dir / "nonexistent.env"
        config = RuntimeConfig(env_file=nonexistent, auto_load=True)
        
        # Should fall back to defaults
        assert config.get('CONTROL_SERVER_PORT') == 8787


class TestRuntimeConfigEnvironmentVars:
    """Test environment variable precedence."""
    
    def test_env_vars_override_all(self, clean_env, sample_yaml_config, sample_env_file):
        """Test that environment variables have highest priority."""
        # Set environment variables
        os.environ['CONTROL_SERVER_PORT'] = '7777'
        os.environ['LOG_LEVEL'] = 'ERROR'
        os.environ['SERPAPI_KEY'] = 'env_var_key'

        config = RuntimeConfig(
            config_path=sample_yaml_config,
            env_file=sample_env_file,
            auto_load=True
        )
        
        # Environment variables should override everything (for keys in defaults)
        assert config.get('CONTROL_SERVER_PORT') == 7777
        assert config.get('LOG_LEVEL') == 'ERROR'
        assert config.get('SERPAPI_KEY') == 'env_var_key'

        # Values not in env vars come from lower priority sources
        assert config.get('CUSTOM_ENV_VALUE') == 'from_env_file'
        assert config.get('CUSTOM_YAML_VALUE') == 'from_yaml'


class TestRuntimeConfigTypeConversion:
    """Test type conversion for configuration values."""
    
    def test_boolean_conversion(self, clean_env):
        """Test boolean value conversion from strings."""
        os.environ['ENABLE_AUTO_DISCOVERY'] = 'true'
        os.environ['DRY_RUN'] = 'false'
        
        config = RuntimeConfig(auto_load=True)
        
        assert config.get('ENABLE_AUTO_DISCOVERY') is True
        assert config.get('DRY_RUN') is False
        
        # Test various boolean representations
        os.environ['VERBOSE'] = '1'
        config.reload()
        assert config.get('VERBOSE') is True
        
        os.environ['VERBOSE'] = '0'
        config.reload()
        assert config.get('VERBOSE') is False
    
    def test_integer_conversion(self, clean_env):
        """Test integer value conversion from strings."""
        os.environ['CONTROL_SERVER_PORT'] = '9000'
        
        config = RuntimeConfig(auto_load=True)
        
        assert config.get('CONTROL_SERVER_PORT') == 9000
        assert isinstance(config.get('CONTROL_SERVER_PORT'), int)
    
    def test_float_conversion(self, clean_env):
        """Test float value conversion from strings."""
        os.environ['SERVER_START_TIMEOUT'] = '45.5'
        
        config = RuntimeConfig(auto_load=True)
        
        assert config.get('SERVER_START_TIMEOUT') == 45.5
        assert isinstance(config.get('SERVER_START_TIMEOUT'), float)


class TestRuntimeConfigMethods:
    """Test configuration methods and utilities."""
    
    def test_set_method(self, clean_env):
        """Test setting configuration values at runtime."""
        config = RuntimeConfig(auto_load=True)
        
        original_port = config.get('CONTROL_SERVER_PORT')
        config.set('CONTROL_SERVER_PORT', 9999)
        
        assert config.get('CONTROL_SERVER_PORT') == 9999
        assert config.get('CONTROL_SERVER_PORT') != original_port
    
    def test_get_all_method(self, clean_env):
        """Test getting all configuration as dictionary."""
        config = RuntimeConfig(auto_load=True)
        
        all_config = config.get_all()
        
        assert isinstance(all_config, dict)
        assert 'CONTROL_SERVER_PORT' in all_config
        assert 'LOG_LEVEL' in all_config
        
        # Modifying returned dict shouldn't affect config
        all_config['CONTROL_SERVER_PORT'] = 9999
        assert config.get('CONTROL_SERVER_PORT') == 8787
    
    def test_reload_method(self, clean_env, sample_yaml_config):
        """Test reloading configuration."""
        config = RuntimeConfig(config_path=sample_yaml_config, auto_load=True)
        
        assert config.get('CONTROL_SERVER_PORT') == 9999
        
        # Change environment variable
        os.environ['CONTROL_SERVER_PORT'] = '7777'
        
        # Before reload, should still be old value
        assert config.get('CONTROL_SERVER_PORT') == 9999
        
        # After reload, should pick up new env var
        config.reload()
        assert config.get('CONTROL_SERVER_PORT') == 7777
    
    def test_to_dict_method(self, clean_env):
        """Test exporting configuration as dictionary."""
        os.environ['SERPAPI_KEY'] = 'secret_key_12345'
        
        config = RuntimeConfig(auto_load=True)
        
        # Without sensitive data
        safe_dict = config.to_dict(include_sensitive=False)
        assert safe_dict['SERPAPI_KEY'] == '***REDACTED***'
        
        # With sensitive data
        full_dict = config.to_dict(include_sensitive=True)
        assert full_dict['SERPAPI_KEY'] == 'secret_key_12345'
    
    def test_to_dict_handles_none_values(self, clean_env):
        """Test to_dict handles None values for API keys."""
        config = RuntimeConfig(auto_load=True)
        
        # SERPAPI_KEY should be None by default
        safe_dict = config.to_dict(include_sensitive=False)
        # Should not crash, and None should stay None
        assert safe_dict['SERPAPI_KEY'] is None


class TestGlobalConfigFunctions:
    """Test global configuration functions."""
    
    def test_get_config_singleton(self, clean_env):
        """Test that get_config returns a singleton instance."""
        config1 = get_config()
        config2 = get_config()
        
        assert config1 is config2
        
        # Modifying one should affect the other
        config1.set('TEST_KEY', 'test_value')
        assert config2.get('TEST_KEY') == 'test_value'
    
    def test_reset_config(self, clean_env):
        """Test resetting the global configuration."""
        config1 = get_config()
        config1.set('TEST_KEY', 'test_value')
        
        reset_config()
        
        config2 = get_config()
        assert config1 is not config2
        assert config2.get('TEST_KEY') is None
    
    def test_get_config_reload(self, clean_env):
        """Test reloading global configuration."""
        config = get_config()
        original_port = config.get('CONTROL_SERVER_PORT')
        
        os.environ['CONTROL_SERVER_PORT'] = '9999'
        
        # Without reload
        config_no_reload = get_config()
        assert config_no_reload.get('CONTROL_SERVER_PORT') == original_port
        
        # With reload
        config_reloaded = get_config(reload=True)
        assert config_reloaded.get('CONTROL_SERVER_PORT') == 9999
    
    def test_get_api_key(self, clean_env):
        """Test get_api_key convenience function."""
        os.environ['SERPAPI_KEY'] = 'test_api_key_123'
        
        reset_config()  # Ensure fresh config
        
        api_key = get_api_key('SERPAPI_KEY')
        assert api_key == 'test_api_key_123'
        
        # Test non-existent key
        assert get_api_key('NONEXISTENT_KEY') is None


class TestRuntimeConfigEdgeCases:
    """Test edge cases and error handling."""
    
    def test_lazy_loading(self, clean_env):
        """Test that config is loaded lazily on first access."""
        config = RuntimeConfig(auto_load=False)
        
        # Config should not be loaded yet
        assert not config._loaded
        
        # First get() should trigger loading
        _ = config.get('CONTROL_SERVER_PORT')
        assert config._loaded
    
    def test_empty_string_values(self, clean_env):
        """Test handling of empty string values."""
        os.environ['SERPAPI_KEY'] = ''
        
        config = RuntimeConfig(auto_load=True)
        
        # Empty string should be converted to None
        assert config.get('SERPAPI_KEY') is None
    
    def test_invalid_type_conversion(self, clean_env):
        """Test handling of invalid type conversions."""
        # Set port to non-numeric value
        os.environ['CONTROL_SERVER_PORT'] = 'not_a_number'
        
        config = RuntimeConfig(auto_load=True)
        
        # Should return the string value (not crash)
        port = config.get('CONTROL_SERVER_PORT')
        assert port == 'not_a_number'
    
    def test_unicode_values(self, clean_env, temp_config_dir):
        """Test handling of unicode values in configuration."""
        yaml_file = temp_config_dir / "unicode.yaml"
        yaml_file.write_text("TEST_VALUE: '日本語テスト 🚀'\n", encoding='utf-8')
        
        config = RuntimeConfig(config_path=yaml_file, auto_load=True)
        
        assert config.get('TEST_VALUE') == '日本語テスト 🚀'


class TestRuntimeConfigIntegration:
    """Integration tests for real-world scenarios."""
    
    def test_complete_precedence_chain(self, clean_env, sample_yaml_config, sample_env_file):
        """Test complete precedence: env var > .env > yaml > defaults."""
        # Set up the chain
        os.environ['CONTROL_SERVER_PORT'] = '7777'  # Highest priority
        
        config = RuntimeConfig(
            config_path=sample_yaml_config,  # Port = 9999
            env_file=sample_env_file,         # Port = 8888
            auto_load=True
        )
        # Default would be 8787
        
        # Environment variable should win
        assert config.get('CONTROL_SERVER_PORT') == 7777
    
    def test_partial_override_scenario(self, clean_env, sample_yaml_config, sample_env_file):
        """Test realistic scenario with partial overrides at each level."""
        os.environ['LOG_LEVEL'] = 'CRITICAL'
        
        config = RuntimeConfig(
            config_path=sample_yaml_config,
            env_file=sample_env_file,
            auto_load=True
        )
        
        # From environment
        assert config.get('LOG_LEVEL') == 'CRITICAL'
        
        # From .env file (not overridden by env)
        assert config.get('CONTROL_SERVER_PORT') == 8888
        
        # From YAML (not in .env or environment)
        assert config.get('CUSTOM_YAML_VALUE') == 'from_yaml'
        
        # From defaults (not in any config source)
        assert config.get('HEALTH_CHECK_INTERVAL') == 10.0
    
    def test_server_specific_config(self, clean_env, sample_yaml_config):
        """Test loading server-specific nested configuration."""
        config = RuntimeConfig(config_path=sample_yaml_config, auto_load=True)
        
        flight_config = config.get('FLIGHT_SERVER')
        assert flight_config is not None
        assert flight_config.get('MAX_RESULTS') == 15
        assert flight_config.get('CACHE_TTL') == 7200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

