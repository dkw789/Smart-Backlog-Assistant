"""Centralized logging service for the Smart Backlog Assistant."""

import json
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Dict, Optional


class LoggerService:
    """Centralized logging service with structured logging capabilities."""

    _instance = None
    _initialized = False

    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the logger service."""
        if not self._initialized:
            self.setup_logging()
            LoggerService._initialized = True

    def setup_logging(self):
        """Setup logging configuration."""
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Get log level from environment
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()

        # Create formatters
        detailed_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        )

        simple_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level))

        # Clear existing handlers
        root_logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level))
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)

        # File handler for all logs
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "backlog_assistant.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)

        # Error file handler
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / "errors.log", maxBytes=5 * 1024 * 1024, backupCount=3  # 5MB
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)

        # Performance log handler
        perf_handler = logging.FileHandler(log_dir / "performance.log")
        perf_handler.setLevel(logging.INFO)
        perf_handler.setFormatter(
            logging.Formatter("%(asctime)s - PERFORMANCE - %(message)s")
        )

        # Create performance logger
        perf_logger = logging.getLogger("performance")
        perf_logger.addHandler(perf_handler)
        perf_logger.setLevel(logging.INFO)
        perf_logger.propagate = False

        self.logger = logging.getLogger(__name__)
        self.perf_logger = perf_logger

        self.logger.info("Logging system initialized")

    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger instance for a specific module."""
        return logging.getLogger(name)

    def log_performance(
        self, operation: str, duration: float, metadata: Optional[Dict[str, Any]] = None
    ):
        """Log performance metrics."""
        perf_data = {
            "operation": operation,
            "duration_seconds": round(duration, 4),
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
        self.perf_logger.info(json.dumps(perf_data))

    def log_ai_request(
        self,
        service: str,
        operation: str,
        tokens_used: Optional[int] = None,
        cost: Optional[float] = None,
        success: bool = True,
    ):
        """Log AI service requests for monitoring."""
        ai_data = {
            "service": service,
            "operation": operation,
            "tokens_used": tokens_used,
            "cost": cost,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger = self.get_logger("ai_requests")
        if success:
            logger.info(f"AI Request: {json.dumps(ai_data)}")
        else:
            logger.error(f"AI Request Failed: {json.dumps(ai_data)}")

    def log_user_action(
        self,
        action: str,
        input_file: str,
        output_file: Optional[str] = None,
        success: bool = True,
        error: Optional[str] = None,
    ):
        """Log user actions for audit trail."""
        action_data = {
            "action": action,
            "input_file": input_file,
            "output_file": output_file,
            "success": success,
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger = self.get_logger("user_actions")
        if success:
            logger.info(f"User Action: {json.dumps(action_data)}")
        else:
            logger.error(f"User Action Failed: {json.dumps(action_data)}")


def get_logger(name: str) -> logging.Logger:
    """Convenience function to get a logger instance."""
    service = LoggerService()
    return service.get_logger(name)


def log_performance(operation: str):
    """Decorator to automatically log performance metrics."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time

            start_time = time.time()
            logger_service = LoggerService()
            logger = logger_service.get_logger(func.__module__)

            try:
                logger.debug(f"Starting {operation}")
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # Extract metadata from function arguments
                metadata = {
                    "function": func.__name__,
                    "module": func.__module__,
                    "args_count": len(args),
                    "kwargs_count": len(kwargs),
                }

                logger_service.log_performance(operation, duration, metadata)
                logger.debug(f"Completed {operation} in {duration:.4f}s")

                return result

            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Failed {operation} after {duration:.4f}s: {str(e)}")
                raise

        return wrapper

    return decorator


def log_ai_request(service: str, operation: str):
    """Decorator to log AI service requests."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger_service = LoggerService()

            try:
                result = func(*args, **kwargs)

                # Try to extract token usage from result if available
                tokens_used = None
                if hasattr(result, "usage") and hasattr(result.usage, "total_tokens"):
                    tokens_used = result.usage.total_tokens

                logger_service.log_ai_request(
                    service, operation, tokens_used, success=True
                )
                return result

            except Exception:
                logger_service.log_ai_request(service, operation, success=False)
                raise

        return wrapper

    return decorator
