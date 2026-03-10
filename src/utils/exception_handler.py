"""Centralized exception handling for the Smart Backlog Assistant."""

import json
import sys
import traceback
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, Optional

from .logger_service import LoggerService


class ErrorSeverity(Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BacklogAssistantError(Exception):
    """Base exception class for Smart Backlog Assistant."""

    def __init__(
        self,
        message: str,
        error_code: str = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.severity = severity
        self.context = context or {}
        self.timestamp = datetime.utcnow().isoformat()


class DocumentProcessingError(BacklogAssistantError):
    """Exception raised during document processing."""

    pass


class AIProcessingError(BacklogAssistantError):
    """Exception raised during AI processing."""

    pass


class ValidationError(BacklogAssistantError):
    """Exception raised during input validation."""

    pass


class ConfigurationError(BacklogAssistantError):
    """Exception raised for configuration issues."""

    pass


class FileHandlingError(BacklogAssistantError):
    """Exception raised during file operations."""

    pass


class ExceptionHandler:
    """Centralized exception handling service."""

    def __init__(self):
        self.logger_service = LoggerService()
        self.logger = self.logger_service.get_logger(__name__)
        self.error_counts = {}
        self.setup_global_exception_handler()

    def setup_global_exception_handler(self):
        """Setup global exception handler for uncaught exceptions."""

        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            self.logger.critical(
                "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
            )

            # Log structured error data
            error_data = {
                "type": exc_type.__name__,
                "message": str(exc_value),
                "traceback": traceback.format_exception(
                    exc_type, exc_value, exc_traceback
                ),
                "timestamp": datetime.utcnow().isoformat(),
            }

            self.logger.critical(
                f"Uncaught Exception Details: {json.dumps(error_data, indent=2)}"
            )

        sys.excepthook = handle_exception

    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        reraise: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """Handle and log an error with structured information."""

        # Increment error count
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

        # Prepare error information
        error_info = {
            "type": error_type,
            "message": str(error),
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat(),
            "count": self.error_counts[error_type],
        }

        # Add custom error information if available
        if isinstance(error, BacklogAssistantError):
            error_info.update(
                {
                    "error_code": error.error_code,
                    "severity": error.severity.value,
                    "custom_context": error.context,
                }
            )

        # Log based on severity
        if isinstance(error, BacklogAssistantError):
            if error.severity == ErrorSeverity.CRITICAL:
                self.logger.critical(
                    f"Critical Error: {json.dumps(error_info, indent=2)}"
                )
            elif error.severity == ErrorSeverity.HIGH:
                self.logger.error(
                    f"High Severity Error: {json.dumps(error_info, indent=2)}"
                )
            elif error.severity == ErrorSeverity.MEDIUM:
                self.logger.warning(
                    f"Medium Severity Error: {json.dumps(error_info, indent=2)}"
                )
            else:
                self.logger.info(
                    f"Low Severity Error: {json.dumps(error_info, indent=2)}"
                )
        else:
            self.logger.error(f"Unhandled Error: {json.dumps(error_info, indent=2)}")

        # Log full traceback for debugging
        self.logger.debug("Full traceback:", exc_info=True)

        if reraise:
            raise error

        return error_info

    def create_error_response(self, error: Exception, operation: str) -> Dict[str, Any]:
        """Create a standardized error response."""
        return {
            "success": False,
            "operation": operation,
            "error": {
                "type": type(error).__name__,
                "message": str(error),
                "code": getattr(error, "error_code", None),
                "severity": (
                    getattr(error, "severity", ErrorSeverity.MEDIUM).value
                    if hasattr(error, "severity")
                    else ErrorSeverity.MEDIUM.value
                ),
                "timestamp": datetime.utcnow().isoformat(),
            },
        }

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring."""
        return {
            "error_counts": self.error_counts.copy(),
            "total_errors": sum(self.error_counts.values()),
            "unique_error_types": len(self.error_counts),
            "timestamp": datetime.utcnow().isoformat(),
        }


# Global exception handler instance
_exception_handler = None


def get_exception_handler() -> ExceptionHandler:
    """Get the global exception handler instance."""
    global _exception_handler
    if _exception_handler is None:
        _exception_handler = ExceptionHandler()
    return _exception_handler


def handle_exceptions(
    operation: str = None, reraise: bool = True, return_error_response: bool = False
):
    """Decorator to handle exceptions in functions."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            handler = get_exception_handler()
            op_name = operation or f"{func.__module__}.{func.__name__}"

            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = {
                    "function": func.__name__,
                    "module": func.__module__,
                    "operation": op_name,
                    "args_count": len(args),
                    "kwargs_count": len(kwargs),
                }

                if return_error_response:
                    handler.handle_error(e, context, reraise=False)
                    return handler.create_error_response(e, op_name)
                else:
                    handler.handle_error(e, context, reraise=reraise)
                    if not reraise:
                        return None

        return wrapper

    return decorator


def safe_execute(
    func: Callable,
    *args,
    default_return=None,
    context: Optional[Dict[str, Any]] = None,
    **kwargs,
):
    """Safely execute a function with error handling."""
    handler = get_exception_handler()

    try:
        return func(*args, **kwargs)
    except Exception as e:
        handler.handle_error(e, context, reraise=False)
        return default_return


def validate_input(
    condition: bool,
    message: str,
    error_code: str = None,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    context: Optional[Dict[str, Any]] = None,
):
    """Validate input condition and raise ValidationError if false."""
    if not condition:
        raise ValidationError(message, error_code, severity, context)


def validate_file_exists(file_path: str, context: Optional[Dict[str, Any]] = None):
    """Validate that a file exists."""
    import os

    if not os.path.isfile(file_path):
        raise FileHandlingError(
            f"File not found: {file_path}",
            "FILE_NOT_FOUND",
            ErrorSeverity.HIGH,
            context,
        )


def validate_api_key(
    api_key: Optional[str], service_name: str, context: Optional[Dict[str, Any]] = None
):
    """Validate that an API key is present."""
    if not api_key or not api_key.strip():
        raise ConfigurationError(
            f"Missing API key for {service_name}",
            "MISSING_API_KEY",
            ErrorSeverity.HIGH,
            context,
        )


def create_processing_error(
    message: str,
    original_error: Exception = None,
    context: Optional[Dict[str, Any]] = None,
) -> DocumentProcessingError:
    """Create a document processing error with context."""
    if original_error:
        message = f"{message}: {str(original_error)}"
        if context is None:
            context = {}
        context["original_error"] = {
            "type": type(original_error).__name__,
            "message": str(original_error),
        }

    return DocumentProcessingError(
        message, "PROCESSING_ERROR", ErrorSeverity.MEDIUM, context
    )


def create_ai_error(
    message: str,
    service: str,
    operation: str,
    original_error: Exception = None,
    context: Optional[Dict[str, Any]] = None,
) -> AIProcessingError:
    """Create an AI processing error with context."""
    if context is None:
        context = {}

    context.update({"ai_service": service, "ai_operation": operation})

    if original_error:
        message = f"{message}: {str(original_error)}"
        context["original_error"] = {
            "type": type(original_error).__name__,
            "message": str(original_error),
        }

    return AIProcessingError(
        message, "AI_PROCESSING_ERROR", ErrorSeverity.HIGH, context
    )
