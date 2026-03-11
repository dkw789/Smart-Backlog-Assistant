"""Comprehensive tests for provider factory and implementations."""

import pytest
from unittest.mock import Mock, patch
from src.providers.provider_factory import (
    ProviderFactory,
    get_provider_factory,
    configure_providers,
    get_ai_provider,
    get_ui_provider,
    get_pydantic_provider
)
from src.providers.base_provider import AIProvider, UIProvider
from src.providers.openai_provider import OpenAIProvider, MockAIProvider
from src.providers.pydantic_provider import PydanticAIProvider, MockPydanticProvider
from src.providers.rich_provider import RichUIProvider, MockUIProvider

class TestProviderFactory:
    """Tests for ProviderFactory class."""

    def test_initialization(self):
        """Test factory initialization."""
        factory = ProviderFactory(use_mocks=True)
        assert factory.use_mocks is True
        assert factory._ai_provider is None
        assert factory._ui_provider is None

    def test_get_ai_provider_mock(self):
        """Test getting mock AI provider."""
        factory = ProviderFactory(use_mocks=True)
        provider = factory.get_ai_provider()
        assert isinstance(provider, MockAIProvider)

    @patch('src.providers.provider_factory.OpenAIProvider')
    def test_get_ai_provider_openai(self, mock_openai_provider):
        """Test getting OpenAI provider."""
        factory = ProviderFactory(use_mocks=False)
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
            provider = factory.get_ai_provider("openai")
            assert provider == mock_openai_provider.return_value
            # Should reuse instance
            assert factory.get_ai_provider("openai") == provider

    @patch('src.providers.provider_factory.PydanticAIProvider')
    def test_get_ai_provider_pydantic(self, mock_pydantic_provider):
        """Test getting Pydantic provider via get_ai_provider."""
        factory = ProviderFactory(use_mocks=False)
        provider = factory.get_ai_provider("pydantic")
        assert provider == mock_pydantic_provider.return_value

    def test_get_ai_provider_unknown(self):
        """Test getting unknown provider falls back to mock."""
        factory = ProviderFactory(use_mocks=False)
        provider = factory.get_ai_provider("unknown")
        assert isinstance(provider, MockAIProvider)

    def test_get_ui_provider_mock(self):
        """Test getting mock UI provider."""
        factory = ProviderFactory(use_mocks=True)
        provider = factory.get_ui_provider()
        assert isinstance(provider, MockUIProvider)

    @patch('src.providers.provider_factory.RichUIProvider')
    def test_get_ui_provider_rich(self, mock_rich_provider):
        """Test getting Rich UI provider."""
        factory = ProviderFactory(use_mocks=False)
        provider = factory.get_ui_provider("rich")
        assert provider == mock_rich_provider.return_value

    def test_get_ui_provider_unknown(self):
        """Test getting unknown UI provider falls back to mock."""
        factory = ProviderFactory(use_mocks=False)
        provider = factory.get_ui_provider("unknown")
        assert isinstance(provider, MockUIProvider)

    @patch('src.providers.provider_factory.PydanticAIProvider')
    def test_get_pydantic_provider(self, mock_pydantic_provider):
        """Test getting PydanticAI provider."""
        factory = ProviderFactory(use_mocks=False)
        provider = factory.get_pydantic_provider()
        assert provider == mock_pydantic_provider.return_value

    def test_get_pydantic_provider_mock(self):
        """Test getting mock PydanticAI provider."""
        factory = ProviderFactory(use_mocks=True)
        provider = factory.get_pydantic_provider()
        assert isinstance(provider, MockPydanticProvider)

    def test_get_all_providers_status(self):
        """Test getting status of all providers."""
        factory = ProviderFactory(use_mocks=True)
        status = factory.get_all_providers_status()
        assert "ai" in status
        assert "ui" in status
        assert "pydantic" in status

    def test_reset_providers(self):
        """Test resetting providers."""
        factory = ProviderFactory(use_mocks=True)
        # Initialize providers
        factory.get_ai_provider()
        factory.get_ui_provider()
        
        assert factory._ai_provider is not None
        assert factory._ui_provider is not None
        
        factory.reset_providers()
        
        assert factory._ai_provider is None
        assert factory._ui_provider is None

class TestGlobalFunctions:
    """Tests for global convenience functions."""

    def setup_method(self):
        configure_providers(use_mocks=True)

    def test_get_provider_factory(self):
        """Test getting global factory."""
        factory = get_provider_factory()
        assert isinstance(factory, ProviderFactory)
        assert factory.use_mocks is True

    def test_configure_providers(self):
        """Test configuring global factory."""
        configure_providers(use_mocks=False)
        factory = get_provider_factory()
        assert factory.use_mocks is False

    def test_convenience_functions(self):
        """Test get_*_provider convenience functions."""
        assert isinstance(get_ai_provider(), MockAIProvider)
        assert isinstance(get_ui_provider(), MockUIProvider)
        assert isinstance(get_pydantic_provider(), MockPydanticProvider)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
