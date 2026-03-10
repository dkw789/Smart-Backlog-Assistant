"""Enhanced error handling with circuit breaker and retry patterns."""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, Optional

from src.utils.exception_handler import BacklogAssistantError


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class RetryConfig:
    """Configuration for retry logic."""

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    success_threshold: int = 3


class CircuitBreaker:
    """Circuit breaker implementation for resilient service calls."""

    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.logger = logging.getLogger(f"circuit_breaker.{name}")

    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.logger.info(f"Circuit breaker {self.name} moving to HALF_OPEN")
            else:
                raise BacklogAssistantError(
                    f"Circuit breaker {self.name} is OPEN",
                    error_code="CIRCUIT_BREAKER_OPEN",
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset."""
        if self.last_failure_time is None:
            return True

        time_since_failure = datetime.utcnow() - self.last_failure_time
        return time_since_failure.total_seconds() >= self.config.recovery_timeout

    def _on_success(self):
        """Handle successful operation."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                self.logger.info(f"Circuit breaker {self.name} reset to CLOSED")
        else:
            self.failure_count = 0

    def _on_failure(self):
        """Handle failed operation."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            self.success_count = 0
            self.logger.warning(f"Circuit breaker {self.name} opened due to failures")


class EnhancedRetryHandler:
    """Enhanced retry handler with exponential backoff and jitter."""

    def __init__(self, config: RetryConfig):
        self.config = config
        self.logger = logging.getLogger("retry_handler")

    def retry(self, func: Callable, *args, **kwargs):
        """Execute function with retry logic."""
        last_exception = None

        for attempt in range(self.config.max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e

                if attempt == self.config.max_attempts - 1:
                    self.logger.error(f"All retry attempts failed: {str(e)}")
                    break

                delay = self._calculate_delay(attempt)
                self.logger.warning(
                    f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay:.2f}s"
                )
                time.sleep(delay)

        raise last_exception

    async def async_retry(self, func: Callable, *args, **kwargs):
        """Execute async function with retry logic."""
        last_exception = None

        for attempt in range(self.config.max_attempts):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e

                if attempt == self.config.max_attempts - 1:
                    self.logger.error(f"All async retry attempts failed: {str(e)}")
                    break

                delay = self._calculate_delay(attempt)
                self.logger.warning(
                    f"Async attempt {attempt + 1} failed: {str(e)}. Retrying in {delay:.2f}s"
                )
                await asyncio.sleep(delay)

        raise last_exception

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and jitter."""
        delay = min(
            self.config.base_delay * (self.config.exponential_base**attempt),
            self.config.max_delay,
        )

        if self.config.jitter:
            import random

            delay *= 0.5 + random.random() * 0.5  # Add 0-50% jitter

        return delay


class ResilientServiceManager:
    """Manager for resilient service calls with circuit breakers and retries."""

    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_handler = EnhancedRetryHandler(RetryConfig())
        self.logger = logging.getLogger("resilient_service_manager")

    def register_service(
        self, name: str, circuit_config: Optional[CircuitBreakerConfig] = None
    ):
        """Register a service with circuit breaker."""
        config = circuit_config or CircuitBreakerConfig()
        self.circuit_breakers[name] = CircuitBreaker(name, config)
        self.logger.info(f"Registered service {name} with circuit breaker")

    def call_service(self, service_name: str, func: Callable, *args, **kwargs):
        """Call service with circuit breaker and retry protection."""
        if service_name not in self.circuit_breakers:
            self.register_service(service_name)

        circuit_breaker = self.circuit_breakers[service_name]

        def protected_call():
            return circuit_breaker.call(func, *args, **kwargs)

        return self.retry_handler.retry(protected_call)

    async def async_call_service(
        self, service_name: str, func: Callable, *args, **kwargs
    ):
        """Call async service with circuit breaker and retry protection."""
        if service_name not in self.circuit_breakers:
            self.register_service(service_name)

        circuit_breaker = self.circuit_breakers[service_name]

        async def protected_call():
            return circuit_breaker.call(func, *args, **kwargs)

        return await self.retry_handler.async_retry(protected_call)

    def get_service_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all registered services."""
        status = {}
        for name, breaker in self.circuit_breakers.items():
            status[name] = {
                "state": breaker.state.value,
                "failure_count": breaker.failure_count,
                "success_count": breaker.success_count,
                "last_failure": (
                    breaker.last_failure_time.isoformat()
                    if breaker.last_failure_time
                    else None
                ),
            }
        return status


# Global instance
resilient_service_manager = ResilientServiceManager()


def resilient_call(
    service_name: str, circuit_config: Optional[CircuitBreakerConfig] = None
):
    """Decorator for resilient service calls."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if (
                service_name not in resilient_service_manager.circuit_breakers
                and circuit_config
            ):
                resilient_service_manager.register_service(service_name, circuit_config)

            return resilient_service_manager.call_service(
                service_name, func, *args, **kwargs
            )

        return wrapper

    return decorator


def async_resilient_call(
    service_name: str, circuit_config: Optional[CircuitBreakerConfig] = None
):
    """Decorator for resilient async service calls."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if (
                service_name not in resilient_service_manager.circuit_breakers
                and circuit_config
            ):
                resilient_service_manager.register_service(service_name, circuit_config)

            return await resilient_service_manager.async_call_service(
                service_name, func, *args, **kwargs
            )

        return wrapper

    return decorator
