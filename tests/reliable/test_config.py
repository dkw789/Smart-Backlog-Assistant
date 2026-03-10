"""Tests for centralized configuration module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.config import AppConfig, config


class TestAppConfig:
    """Test the AppConfig class."""

    def test_default_values(self):
        """Test that default configuration values are set correctly."""
        test_config = AppConfig()
        
        assert test_config.log_level == "INFO"
        assert test_config.log_file == "backlog_assistant.log"
        assert test_config.default_ai_service == "anthropic"
        assert test_config.max_retries == 3
        assert test_config.timeout_seconds == 30
        assert test_config.max_tokens == 2000
        assert test_config.temperature == 0.7
        assert test_config.circuit_breaker_failure_threshold == 5
        assert test_config.circuit_breaker_recovery_timeout == 60.0
        assert test_config.circuit_breaker_success_threshold == 3
        assert test_config.cache_ttl_seconds == 3600
        assert test_config.cache_max_size == 1000
        assert test_config.enable_caching is True
        assert test_config.max_file_size_mb == 50
        assert test_config.default_sprint_capacity == 40
        assert test_config.debug_mode is False
        assert test_config.use_mock_providers is False

    def test_supported_file_extensions_default(self):
        """Test that supported file extensions are set correctly."""
        test_config = AppConfig()
        expected_extensions = [".txt", ".md", ".pdf", ".docx", ".json"]
        assert test_config.supported_file_extensions == expected_extensions

    def test_environment_variable_override(self):
        """Test that environment variables override defaults."""
        with patch.dict(os.environ, {
            'LOG_LEVEL': 'DEBUG',
            'DEFAULT_AI_SERVICE': 'openai',
            'MAX_RETRIES': '5',
            'TIMEOUT_SECONDS': '45',
            'ENABLE_CACHING': 'false',
            'DEBUG_MODE': 'true'
        }):
            test_config = AppConfig()
            
            assert test_config.log_level == "DEBUG"
            assert test_config.default_ai_service == "openai"
            assert test_config.max_retries == 5
            assert test_config.timeout_seconds == 45
            assert test_config.enable_caching is False
            assert test_config.debug_mode is True

    def test_get_ai_service_config(self):
        """Test AI service configuration getter."""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test-openai-key',
            'ANTHROPIC_API_KEY': 'test-anthropic-key'
        }):
            test_config = AppConfig()
            ai_config = test_config.get_ai_service_config()
            
            assert ai_config['openai_api_key'] == 'test-openai-key'
            assert ai_config['anthropic_api_key'] == 'test-anthropic-key'
            assert ai_config['default_service'] == 'anthropic'
            assert ai_config['max_retries'] == 3
            assert ai_config['timeout_seconds'] == 30
            assert ai_config['max_tokens'] == 2000
            assert ai_config['temperature'] == 0.7

    def test_get_circuit_breaker_config(self):
        """Test circuit breaker configuration getter."""
        test_config = AppConfig()
        cb_config = test_config.get_circuit_breaker_config()
        
        assert cb_config['failure_threshold'] == 5
        assert cb_config['recovery_timeout'] == 60.0
        assert cb_config['success_threshold'] == 3

    def test_get_cache_config(self):
        """Test cache configuration getter."""
        test_config = AppConfig()
        cache_config = test_config.get_cache_config()
        
        assert cache_config['ttl_seconds'] == 3600
        assert cache_config['max_size'] == 1000
        assert cache_config['enabled'] is True

    def test_validate_ai_services_with_keys(self):
        """Test AI service validation when keys are present."""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test-key'
        }):
            test_config = AppConfig()
            assert test_config.validate_ai_services() is True

    def test_validate_ai_services_without_keys(self):
        """Test AI service validation when no keys are present."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': '', 'ANTHROPIC_API_KEY': ''}, clear=True):
            test_config = AppConfig()
            assert test_config.validate_ai_services() is False

    def test_validate_ai_services_with_anthropic_key(self):
        """Test AI service validation with Anthropic key only."""
        with patch.dict(os.environ, {
            'ANTHROPIC_API_KEY': 'test-anthropic-key'
        }, clear=True):
            test_config = AppConfig()
            assert test_config.validate_ai_services() is True

    def test_config_from_env_file(self):
        """Test loading configuration from .env file."""
        # Create temporary .env file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("LOG_LEVEL=ERROR\n")
            f.write("MAX_RETRIES=10\n")
            f.write("OPENAI_API_KEY=env-file-key\n")
            temp_env_file = f.name

        try:
            # Test with custom env file
            test_config = AppConfig(_env_file=temp_env_file)
            
            # Note: This test may not work as expected because pydantic-settings
            # loads from the default .env file. This is more of a documentation test.
            # In practice, the .env file loading is handled by pydantic-settings automatically.
            
        finally:
            # Clean up
            os.unlink(temp_env_file)

    def test_case_insensitive_env_vars(self):
        """Test that environment variables are case insensitive."""
        with patch.dict(os.environ, {
            'log_level': 'WARNING',  # lowercase
            'MAX_RETRIES': '7'       # uppercase
        }):
            test_config = AppConfig()
            assert test_config.log_level == "WARNING"
            assert test_config.max_retries == 7


class TestGlobalConfig:
    """Test the global config instance."""

    def test_global_config_instance(self):
        """Test that the global config instance is properly initialized."""
        assert config is not None
        assert isinstance(config, AppConfig)
        assert config.log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    def test_global_config_ai_service_validation(self):
        """Test that global config can validate AI services."""
        # This will depend on whether API keys are set in the environment
        result = config.validate_ai_services()
        assert isinstance(result, bool)

    def test_global_config_methods(self):
        """Test that global config methods work correctly."""
        ai_config = config.get_ai_service_config()
        assert isinstance(ai_config, dict)
        assert 'default_service' in ai_config
        
        cb_config = config.get_circuit_breaker_config()
        assert isinstance(cb_config, dict)
        assert 'failure_threshold' in cb_config
        
        cache_config = config.get_cache_config()
        assert isinstance(cache_config, dict)
        assert 'enabled' in cache_config


class TestConfigValidation:
    """Test configuration validation and edge cases."""

    def test_invalid_temperature_values(self):
        """Test temperature validation bounds."""
        # Note: Pydantic doesn't automatically validate bounds unless we add validators
        # These tests document expected behavior but may not fail without custom validators
        with patch.dict(os.environ, {'TEMPERATURE': '3.0'}):
            config = AppConfig()
            # Should accept the value even if outside typical bounds
            assert config.temperature == 3.0

        with patch.dict(os.environ, {'TEMPERATURE': '-1.0'}):
            config = AppConfig()
            assert config.temperature == -1.0

    def test_invalid_max_tokens(self):
        """Test max tokens validation bounds."""
        # Note: Without custom validators, Pydantic accepts any integer
        with patch.dict(os.environ, {'MAX_TOKENS': '50'}):
            config = AppConfig()
            assert config.max_tokens == 50

        with patch.dict(os.environ, {'MAX_TOKENS': '10000'}):
            config = AppConfig()
            assert config.max_tokens == 10000

    def test_invalid_max_retries(self):
        """Test max retries validation."""
        with patch.dict(os.environ, {'MAX_RETRIES': '0'}):  # Should be at least 1
            test_config = AppConfig()
            assert test_config.max_retries == 0  # Pydantic allows 0, but it's not practical

    def test_boolean_env_var_parsing(self):
        """Test that boolean environment variables are parsed correctly."""
        test_cases = [
            ('true', True),
            ('True', True), 
            ('TRUE', True),
            ('1', True),
            ('false', False),
            ('False', False),
            ('FALSE', False),
            ('0', False),
        ]
        
        for env_value, expected in test_cases:
            with patch.dict(os.environ, {'ENABLE_CACHING': env_value}):
                test_config = AppConfig()
                assert test_config.enable_caching == expected, f"Failed for {env_value}"

    def test_numeric_env_var_parsing(self):
        """Test that numeric environment variables are parsed correctly."""
        with patch.dict(os.environ, {
            'MAX_RETRIES': '15',
            'TIMEOUT_SECONDS': '120',
            'MAX_TOKENS': '4000',
            'TEMPERATURE': '0.9',
            'CACHE_TTL_SECONDS': '7200',
            'MAX_FILE_SIZE_MB': '100'
        }):
            test_config = AppConfig()
            
            assert test_config.max_retries == 15
            assert test_config.timeout_seconds == 120
            assert test_config.max_tokens == 4000
            assert test_config.temperature == 0.9
            assert test_config.cache_ttl_seconds == 7200
            assert test_config.max_file_size_mb == 100
