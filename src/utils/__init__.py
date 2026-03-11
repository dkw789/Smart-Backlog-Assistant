"""Utilities module for Smart Backlog Assistant.

This module provides various utility functions and services:
- caching_system: Intelligent caching with multiple backends
- exception_handler: Centralized exception handling
- enhanced_error_handler: Advanced error handling with retry logic
- file_handler: File operations and management
- logger_service: Logging configuration and utilities
- rich_cli: Rich command-line interface components
- validators: Input and output validation utilities
"""

from .caching_system import (
    IntelligentCache,
    AIResponseCache,
    CacheBackend,
    MemoryCacheBackend,
    FileCacheBackend,
)
from .exception_handler import (
    handle_exceptions,
    SmartBacklogError,
    ConfigurationError,
    ValidationError,
    ProcessingError,
)
from .enhanced_error_handler import (
    EnhancedRetryHandler,
    CircuitBreaker,
    RetryConfig,
)
from .file_handler import FileHandler
from .logger_service import get_logger, setup_logging
from .rich_cli import RichCLI, RichProgress
from .validators import (
    validate_api_key,
    validate_file_exists,
    validate_json_structure,
    sanitize_text,
)

__all__ = [
    "IntelligentCache",
    "AIResponseCache",
    "CacheBackend",
    "MemoryCacheBackend",
    "FileCacheBackend",
    "handle_exceptions",
    "SmartBacklogError",
    "ConfigurationError",
    "ValidationError",
    "ProcessingError",
    "EnhancedRetryHandler",
    "CircuitBreaker",
    "RetryConfig",
    "FileHandler",
    "get_logger",
    "setup_logging",
    "RichCLI",
    "RichProgress",
    "validate_api_key",
    "validate_file_exists",
    "validate_json_structure",
    "sanitize_text",
]