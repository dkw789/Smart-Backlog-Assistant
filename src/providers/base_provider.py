"""Base provider interface for external services."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseProvider(ABC):
    """Abstract base class for all external service providers."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and configured."""
        pass

    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """Get provider configuration."""
        pass


class AIProvider(BaseProvider):
    """Abstract base class for AI service providers."""

    @abstractmethod
    def generate_completion(self, prompt: str, **kwargs) -> str:
        """Generate a completion from the AI service."""
        pass

    @abstractmethod
    def generate_structured_response(
        self, prompt: str, schema: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate a structured response from the AI service."""
        pass


class UIProvider(BaseProvider):
    """Abstract base class for UI/CLI providers."""

    @abstractmethod
    def print_message(self, message: str, style: Optional[str] = None) -> None:
        """Print a message with optional styling."""
        pass

    @abstractmethod
    def create_progress_tracker(self) -> Any:
        """Create a progress tracker instance."""
        pass

    @abstractmethod
    def format_table(self, data: list, title: Optional[str] = None) -> Any:
        """Format data as a table."""
        pass
