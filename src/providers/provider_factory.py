"""Provider factory for managing external service providers."""

import logging
import os
from typing import Any, Dict

from .base_provider import AIProvider, UIProvider
from .openai_provider import MockAIProvider, OpenAIProvider
from .pydantic_provider import MockPydanticProvider, PydanticAIProvider
from .rich_provider import MockUIProvider, RichUIProvider


class ProviderFactory:
    """Factory for creating and managing service providers."""

    def __init__(self, use_mocks: bool = False):
        self.logger = logging.getLogger(__name__)
        self.use_mocks = use_mocks
        self._ai_provider = None
        self._ui_provider = None
        self._pydantic_provider = None

    def get_ai_provider(self, provider_type: str = "openai") -> AIProvider:
        """Get AI provider instance."""
        if self.use_mocks:
            return MockAIProvider()

        if self._ai_provider is None:
            if provider_type == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                self._ai_provider = OpenAIProvider(api_key=api_key)
            elif provider_type == "pydantic":
                self._ai_provider = PydanticAIProvider()
            else:
                self.logger.warning(
                    f"Unknown AI provider type: {provider_type}, using mock"
                )
                self._ai_provider = MockAIProvider()

        return self._ai_provider

    def get_ui_provider(self, provider_type: str = "rich") -> UIProvider:
        """Get UI provider instance."""
        if self.use_mocks:
            return MockUIProvider()

        if self._ui_provider is None:
            if provider_type == "rich":
                self._ui_provider = RichUIProvider()
            else:
                self.logger.warning(
                    f"Unknown UI provider type: {provider_type}, using mock"
                )
                self._ui_provider = MockUIProvider()

        return self._ui_provider

    def get_pydantic_provider(self) -> PydanticAIProvider:
        """Get PydanticAI provider instance."""
        if self.use_mocks:
            return MockPydanticProvider()

        if self._pydantic_provider is None:
            self._pydantic_provider = PydanticAIProvider()

        return self._pydantic_provider

    def get_all_providers_status(self) -> Dict[str, Any]:
        """Get status of all providers."""
        status = {}

        try:
            ai_provider = self.get_ai_provider()
            status["ai"] = ai_provider.get_config()
        except Exception as e:
            status["ai"] = {"error": str(e)}

        try:
            ui_provider = self.get_ui_provider()
            status["ui"] = ui_provider.get_config()
        except Exception as e:
            status["ui"] = {"error": str(e)}

        try:
            pydantic_provider = self.get_pydantic_provider()
            status["pydantic"] = pydantic_provider.get_config()
        except Exception as e:
            status["pydantic"] = {"error": str(e)}

        return status

    def reset_providers(self) -> None:
        """Reset all provider instances."""
        self._ai_provider = None
        self._ui_provider = None
        self._pydantic_provider = None


# Global factory instance
_factory = None


def get_provider_factory(use_mocks: bool = False) -> ProviderFactory:
    """Get the global provider factory instance."""
    global _factory
    if _factory is None:
        _factory = ProviderFactory(use_mocks=use_mocks)
    return _factory


def configure_providers(use_mocks: bool = False, **kwargs) -> None:
    """Configure the global provider factory."""
    global _factory
    _factory = ProviderFactory(use_mocks=use_mocks)


# Convenience functions
def get_ai_provider(provider_type: str = "openai") -> AIProvider:
    """Get AI provider instance."""
    return get_provider_factory().get_ai_provider(provider_type)


def get_ui_provider(provider_type: str = "rich") -> UIProvider:
    """Get UI provider instance."""
    return get_provider_factory().get_ui_provider(provider_type)


def get_pydantic_provider() -> PydanticAIProvider:
    """Get PydanticAI provider instance."""
    return get_provider_factory().get_pydantic_provider()
