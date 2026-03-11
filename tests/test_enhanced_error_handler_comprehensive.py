"""Comprehensive tests for enhanced error handler to improve code coverage."""

import pytest
import time
from unittest.mock import patch, MagicMock
from dataclasses import dataclass
from typing import Any, Dict

from src.utils.enhanced_error_handler import (
    CircuitState,
    RetryConfig,
    CircuitBreakerConfig,
    CircuitBreaker,
    EnhancedRetryHandler,
    ResilientServiceManager,
    resilient_service_manager,
    resilient_call,
    async_resilient_call
)
from src.utils.exception_handler import BacklogAssistantError


class TestCircuitState:
    """Tests for CircuitState enum."""
    
    def test_circuit_state_values(self):
        """Test CircuitState enum values."""
        assert CircuitState.CLOSED.value == "closed"
        assert CircuitState.OPEN.value == "open"
        assert CircuitState.HALF_OPEN.value == "half_open"
    
    def test_circuit_state_comparison(self):
        """Test CircuitState enum comparison."""
        assert CircuitState.CLOSED == CircuitState.CLOSED
        assert CircuitState.CLOSED != CircuitState.OPEN
        assert CircuitState.OPEN != CircuitState.HALF_OPEN


class TestRetryConfig:
    """Tests for RetryConfig dataclass."""
    
    def test_retry_config_defaults(self):
        """Test RetryConfig default values."""
        config = RetryConfig()
        
        assert config.max_attempts == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0
        assert config.jitter is True
    
    def test_retry_config_custom_values(self):
        """Test RetryConfig with custom values."""
        config = RetryConfig(
            max_attempts=5,
            base_delay=0.5,
            max_delay=30.0,
            exponential_base=1.5,
            jitter=False
        )
        
        assert config.max_attempts == 5
        assert config.base_delay == 0.5
        assert config.max_delay == 30.0
        assert config.exponential_base == 1.5
        assert config.jitter is False
    
    def test_retry_config_modification(self):
        """Test that RetryConfig attributes can be modified."""
        config = RetryConfig()
        
        config.max_attempts = 10
        config.base_delay = 2.0
        
        assert config.max_attempts == 10
        assert config.base_delay == 2.0


class TestCircuitBreakerConfig:
    """Tests for CircuitBreakerConfig dataclass."""
    
    def test_circuit_breaker_config_defaults(self):
        """Test CircuitBreakerConfig default values."""
        config = CircuitBreakerConfig()
        
        assert config.failure_threshold == 5
        assert config.recovery_timeout == 60.0
        assert config.success_threshold == 3
    
    def test_circuit_breaker_config_custom_values(self):
        """Test CircuitBreakerConfig with custom values."""
        config = CircuitBreakerConfig(
            failure_threshold=10,
            recovery_timeout=120.0,
            success_threshold=5
        )
        
        assert config.failure_threshold == 10
        assert config.recovery_timeout == 120.0
        assert config.success_threshold == 5
    
    def test_circuit_breaker_config_modification(self):
        """Test that CircuitBreakerConfig attributes can be modified."""
        config = CircuitBreakerConfig()
        
        config.failure_threshold = 8
        config.recovery_timeout = 90.0
        
        assert config.failure_threshold == 8
        assert config.recovery_timeout == 90.0


class TestCircuitBreaker:
    """Tests for CircuitBreaker class."""
    
    def test_circuit_breaker_initialization(self):
        """Test CircuitBreaker initialization."""
        config = CircuitBreakerConfig(failure_threshold=3, recovery_timeout=30.0)
        breaker = CircuitBreaker("test_service", config)
        
        assert breaker.name == "test_service"
        assert breaker.config == config
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0
        assert breaker.success_count == 0
        assert breaker.last_failure_time is None
    
    def test_circuit_breaker_record_success_closed_state(self):
        """Test recording success in closed state."""
        config = CircuitBreakerConfig()
        breaker = CircuitBreaker("test", config)
        
        breaker.record_success()
        
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0
        assert breaker.success_count == 1
    
    def test_circuit_breaker_record_failure_closed_state(self):
        """Test recording failure in closed state."""
        config = CircuitBreakerConfig(failure_threshold=2)
        breaker = CircuitBreaker("test", config)
        
        # First failure - should stay closed
        breaker.record_failure()
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 1
        
        # Second failure - should open circuit
        breaker.record_failure()
        assert breaker.state == CircuitState.OPEN
        assert breaker.failure_count == 2
        assert breaker.last_failure_time is not None
    
    @patch('src.utils.enhanced_error_handler.time.time')
    def test_circuit_breaker_can_execute_closed(self, mock_time):
        """Test can_execute in closed state."""
        config = CircuitBreakerConfig()
        breaker = CircuitBreaker("test", config)
        
        assert breaker.can_execute() is True
    
    @patch('src.utils.enhanced_error_handler.time.time')
    def test_circuit_breaker_can_execute_open_within_timeout(self, mock_time):
        """Test can_execute in open state within timeout."""
        mock_time.return_value = 1000.0
        
        config = CircuitBreakerConfig(failure_threshold=1, recovery_timeout=60.0)
        breaker = CircuitBreaker("test", config)
        
        # Force circuit to open
        breaker.record_failure()
        assert breaker.state == CircuitState.OPEN
        
        # Still within timeout
        mock_time.return_value = 1030.0  # 30 seconds later
        assert breaker.can_execute() is False
    
    @patch('src.utils.enhanced_error_handler.time.time')
    def test_circuit_breaker_can_execute_open_after_timeout(self, mock_time):
        """Test can_execute in open state after timeout."""
        mock_time.return_value = 1000.0
        
        config = CircuitBreakerConfig(failure_threshold=1, recovery_timeout=60.0)
        breaker = CircuitBreaker("test", config)
        
        # Force circuit to open
        breaker.record_failure()
        assert breaker.state == CircuitState.OPEN
        
        # After timeout - should transition to half-open
        mock_time.return_value = 1070.0  # 70 seconds later
        assert breaker.can_execute() is True
        assert breaker.state == CircuitState.HALF_OPEN
    
    def test_circuit_breaker_can_execute_half_open(self):
        """Test can_execute in half-open state."""
        config = CircuitBreakerConfig()
        breaker = CircuitBreaker("test", config)
        breaker.state = CircuitState.HALF_OPEN
        
        assert breaker.can_execute() is True
    
    def test_circuit_breaker_record_success_half_open(self):
        """Test recording success in half-open state."""
        config = CircuitBreakerConfig(success_threshold=2)
        breaker = CircuitBreaker("test", config)
        breaker.state = CircuitState.HALF_OPEN
        
        # First success - should stay half-open
        breaker.record_success()
        assert breaker.state == CircuitState.HALF_OPEN
        assert breaker.success_count == 1
        
        # Second success - should close circuit
        breaker.record_success()
        assert breaker.state == CircuitState.CLOSED
        assert breaker.success_count == 0  # Reset
        assert breaker.failure_count == 0  # Reset
    
    def test_circuit_breaker_record_failure_half_open(self):
        """Test recording failure in half-open state."""
        config = CircuitBreakerConfig()
        breaker = CircuitBreaker("test", config)
        breaker.state = CircuitState.HALF_OPEN
        
        breaker.record_failure()
        
        assert breaker.state == CircuitState.OPEN
        assert breaker.failure_count == 1
        assert breaker.last_failure_time is not None
    
    def test_circuit_breaker_get_stats(self):
        """Test getting circuit breaker statistics."""
        config = CircuitBreakerConfig()
        breaker = CircuitBreaker("test_service", config)
        
        breaker.failure_count = 3
        breaker.success_count = 7
        
        stats = breaker.get_stats()
        
        assert stats["name"] == "test_service"
        assert stats["state"] == CircuitState.CLOSED.value
        assert stats["failure_count"] == 3
        assert stats["success_count"] == 7
        assert "last_failure_time" in stats


class TestResilientServiceManager:
    """Tests for ResilientServiceManager class."""
    
    def test_resilient_service_manager_initialization(self):
        """Test ResilientServiceManager initialization."""
        manager = ResilientServiceManager()
        
        assert manager.circuit_breakers == {}
        assert manager.logger is not None
    
    def test_register_service(self):
        """Test registering a service with circuit breaker."""
        manager = ResilientServiceManager()
        config = CircuitBreakerConfig(failure_threshold=3)
        
        manager.register_service("test_service", config)
        
        assert "test_service" in manager.circuit_breakers
        breaker = manager.circuit_breakers["test_service"]
        assert breaker.name == "test_service"
        assert breaker.config == config
    
    def test_register_service_duplicate(self):
        """Test registering duplicate service."""
        manager = ResilientServiceManager()
        config1 = CircuitBreakerConfig(failure_threshold=3)
        config2 = CircuitBreakerConfig(failure_threshold=5)
        
        manager.register_service("test_service", config1)
        manager.register_service("test_service", config2)  # Should update
        
        breaker = manager.circuit_breakers["test_service"]
        assert breaker.config.failure_threshold == 5
    
    def test_get_circuit_breaker_existing(self):
        """Test getting existing circuit breaker."""
        manager = ResilientServiceManager()
        config = CircuitBreakerConfig()
        manager.register_service("test_service", config)
        
        breaker = manager.get_circuit_breaker("test_service")
        
        assert breaker is not None
        assert breaker.name == "test_service"
    
    def test_get_circuit_breaker_non_existing(self):
        """Test getting non-existing circuit breaker."""
        manager = ResilientServiceManager()
        
        breaker = manager.get_circuit_breaker("non_existing")
        
        assert breaker is None
    
    def test_record_success(self):
        """Test recording success for a service."""
        manager = ResilientServiceManager()
        config = CircuitBreakerConfig()
        manager.register_service("test_service", config)
        
        manager.record_success("test_service")
        
        breaker = manager.circuit_breakers["test_service"]
        assert breaker.success_count == 1
    
    def test_record_success_non_existing_service(self):
        """Test recording success for non-existing service."""
        manager = ResilientServiceManager()
        
        # Should not raise exception
        manager.record_success("non_existing")
    
    def test_record_failure(self):
        """Test recording failure for a service."""
        manager = ResilientServiceManager()
        config = CircuitBreakerConfig()
        manager.register_service("test_service", config)
        
        manager.record_failure("test_service")
        
        breaker = manager.circuit_breakers["test_service"]
        assert breaker.failure_count == 1
    
    def test_record_failure_non_existing_service(self):
        """Test recording failure for non-existing service."""
        manager = ResilientServiceManager()
        
        # Should not raise exception
        manager.record_failure("non_existing")
    
    def test_can_execute_service(self):
        """Test checking if service can execute."""
        manager = ResilientServiceManager()
        config = CircuitBreakerConfig()
        manager.register_service("test_service", config)
        
        result = manager.can_execute("test_service")
        
        assert result is True
    
    def test_can_execute_non_existing_service(self):
        """Test checking execution for non-existing service."""
        manager = ResilientServiceManager()
        
        result = manager.can_execute("non_existing")
        
        assert result is True  # Default to allowing execution
    
    def test_get_all_stats(self):
        """Test getting statistics for all services."""
        manager = ResilientServiceManager()
        config1 = CircuitBreakerConfig()
        config2 = CircuitBreakerConfig()
        
        manager.register_service("service1", config1)
        manager.register_service("service2", config2)
        
        stats = manager.get_all_stats()
        
        assert len(stats) == 2
        assert any(stat["name"] == "service1" for stat in stats)
        assert any(stat["name"] == "service2" for stat in stats)


class TestRetryWithBackoff:
    """Tests for retry_with_backoff decorator."""
    
    @patch('src.utils.enhanced_error_handler.time.sleep')
    def test_retry_success_first_attempt(self, mock_sleep):
        """Test retry decorator with success on first attempt."""
        @retry_with_backoff(RetryConfig(max_attempts=3))
        def successful_function():
            return "success"
        
        result = successful_function()
        
        assert result == "success"
        mock_sleep.assert_not_called()
    
    @patch('src.utils.enhanced_error_handler.time.sleep')
    def test_retry_success_after_failures(self, mock_sleep):
        """Test retry decorator with success after failures."""
        call_count = 0
        
        @retry_with_backoff(RetryConfig(max_attempts=3, base_delay=0.1))
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        result = flaky_function()
        
        assert result == "success"
        assert call_count == 3
        assert mock_sleep.call_count == 2  # Two retries
    
    @patch('src.utils.enhanced_error_handler.time.sleep')
    def test_retry_all_attempts_fail(self, mock_sleep):
        """Test retry decorator when all attempts fail."""
        @retry_with_backoff(RetryConfig(max_attempts=2, base_delay=0.1))
        def failing_function():
            raise ValueError("Persistent failure")
        
        with pytest.raises(ValueError, match="Persistent failure"):
            failing_function()
        
        assert mock_sleep.call_count == 1  # One retry
    
    @patch('src.utils.enhanced_error_handler.time.sleep')
    def test_retry_exponential_backoff(self, mock_sleep):
        """Test that retry uses exponential backoff."""
        call_count = 0
        
        @retry_with_backoff(RetryConfig(max_attempts=4, base_delay=1.0, exponential_base=2.0, jitter=False))
        def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            always_failing_function()
        
        # Should have called sleep with increasing delays: 1.0, 2.0, 4.0
        expected_delays = [1.0, 2.0, 4.0]
        actual_delays = [call[0][0] for call in mock_sleep.call_args_list]
        assert actual_delays == expected_delays


class TestCircuitBreakerDecorator:
    """Tests for circuit_breaker decorator."""
    
    def test_circuit_breaker_success(self):
        """Test circuit breaker decorator with successful function."""
        manager = ResilientServiceManager()
        config = CircuitBreakerConfig()
        manager.register_service("test_service", config)
        
        @circuit_breaker("test_service", manager)
        def successful_function():
            return "success"
        
        result = successful_function()
        
        assert result == "success"
        breaker = manager.get_circuit_breaker("test_service")
        assert breaker.success_count == 1
        assert breaker.failure_count == 0
    
    def test_circuit_breaker_failure(self):
        """Test circuit breaker decorator with failing function."""
        manager = ResilientServiceManager()
        config = CircuitBreakerConfig()
        manager.register_service("test_service", config)
        
        @circuit_breaker("test_service", manager)
        def failing_function():
            raise ValueError("Function failed")
        
        with pytest.raises(ValueError, match="Function failed"):
            failing_function()
        
        breaker = manager.get_circuit_breaker("test_service")
        assert breaker.success_count == 0
        assert breaker.failure_count == 1
    
    def test_circuit_breaker_open_circuit(self):
        """Test circuit breaker decorator with open circuit."""
        manager = ResilientServiceManager()
        config = CircuitBreakerConfig(failure_threshold=1)
        manager.register_service("test_service", config)
        
        @circuit_breaker("test_service", manager)
        def function_to_test():
            raise ValueError("Function failed")
        
        # First call should fail and open circuit
        with pytest.raises(ValueError):
            function_to_test()
        
        # Second call should be blocked by open circuit
        with pytest.raises(BacklogAssistantError, match="Circuit breaker is open"):
            function_to_test()


class TestGlobalResilientServiceManager:
    """Tests for global resilient service manager instance."""
    
    def test_global_manager_exists(self):
        """Test that global manager instance exists."""
        assert resilient_service_manager is not None
        assert isinstance(resilient_service_manager, ResilientServiceManager)
    
    def test_global_manager_register_service(self):
        """Test registering service with global manager."""
        config = CircuitBreakerConfig(failure_threshold=2)
        
        resilient_service_manager.register_service("global_test", config)
        
        breaker = resilient_service_manager.get_circuit_breaker("global_test")
        assert breaker is not None
        assert breaker.name == "global_test"
        assert breaker.config.failure_threshold == 2
    
    def test_global_manager_operations(self):
        """Test basic operations with global manager."""
        config = CircuitBreakerConfig()
        service_name = "global_ops_test"
        
        # Register service
        resilient_service_manager.register_service(service_name, config)
        
        # Test can execute
        assert resilient_service_manager.can_execute(service_name) is True
        
        # Record success
        resilient_service_manager.record_success(service_name)
        breaker = resilient_service_manager.get_circuit_breaker(service_name)
        assert breaker.success_count == 1
        
        # Record failure
        resilient_service_manager.record_failure(service_name)
        assert breaker.failure_count == 1
