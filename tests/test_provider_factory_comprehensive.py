"""Comprehensive tests for ProviderFactory to improve code coverage."""

import pytest
from unittest.mock import patch, MagicMock
from src.providers.provider_factory import ProviderFactory
from src.providers.base_provider import AIProvider, UIProvider


class TestProviderFactory:
    """Test ProviderFactory class."""
    
    def test_provider_factory_init_default(self):
        """Test ProviderFactory initialization with default parameters."""
        factory = ProviderFactory()
        assert factory.use_mocks is False
        assert factory._ai_provider is None
        assert factory._ui_provider is None
        assert factory._pydantic_provider is None
    
    def test_provider_factory_init_with_mocks(self):
        """Test ProviderFactory initialization with mocks enabled."""
        factory = ProviderFactory(use_mocks=True)
        assert factory.use_mocks is True
        assert factory._ai_provider is None
        assert factory._ui_provider is None
        assert factory._pydantic_provider is None
    
    def test_get_ai_provider_with_mocks(self):
        """Test getting AI provider when mocks are enabled."""
        factory = ProviderFactory(use_mocks=True)
        provider = factory.get_ai_provider()
        
        assert provider is not None
        assert hasattr(provider, 'process_request')  # Mock provider interface
    
    def test_get_ai_provider_openai_type(self):
        """Test getting OpenAI provider."""
        factory = ProviderFactory(use_mocks=False)
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            provider = factory.get_ai_provider("openai")
            assert provider is not None
            assert factory._ai_provider is provider
    
    def test_get_ai_provider_openai_no_key(self):
        """Test getting OpenAI provider without API key."""
        factory = ProviderFactory(use_mocks=False)
        
        with patch.dict('os.environ', {}, clear=True):
            provider = factory.get_ai_provider("openai")
            assert provider is not None
            # Should create provider even without key (may fail later)
    
    def test_get_ai_provider_pydantic_type(self):
        """Test getting Pydantic AI provider."""
        factory = ProviderFactory(use_mocks=False)
        provider = factory.get_ai_provider("pydantic")
        
        assert provider is not None
        assert factory._ai_provider is provider
    
    def test_get_ai_provider_unknown_type(self):
        """Test getting AI provider with unknown type."""
        factory = ProviderFactory(use_mocks=False)
        
        with patch.object(factory.logger, 'warning') as mock_warning:
            provider = factory.get_ai_provider("unknown")
            
            assert provider is not None
            mock_warning.assert_called_once()
            assert "Unknown AI provider type: unknown" in str(mock_warning.call_args)
    
    def test_get_ai_provider_caching(self):
        """Test that AI provider is cached after first call."""
        factory = ProviderFactory(use_mocks=True)
        
        provider1 = factory.get_ai_provider()
        provider2 = factory.get_ai_provider()
        
        assert provider1 is provider2
        assert factory._ai_provider is provider1
    
    def test_get_ui_provider_with_mocks(self):
        """Test getting UI provider when mocks are enabled."""
        factory = ProviderFactory(use_mocks=True)
        provider = factory.get_ui_provider()
        
        assert provider is not None
        assert hasattr(provider, 'display_message')  # Mock UI interface
    
    def test_get_ui_provider_rich_type(self):
        """Test getting Rich UI provider."""
        factory = ProviderFactory(use_mocks=False)
        provider = factory.get_ui_provider("rich")
        
        assert provider is not None
        assert factory._ui_provider is provider
    
    def test_get_ui_provider_unknown_type(self):
        """Test getting UI provider with unknown type."""
        factory = ProviderFactory(use_mocks=False)
        
        with patch.object(factory.logger, 'warning') as mock_warning:
            provider = factory.get_ui_provider("unknown")
            
            assert provider is not None
            mock_warning.assert_called_once()
            assert "Unknown UI provider type: unknown" in str(mock_warning.call_args)
    
    def test_get_ui_provider_caching(self):
        """Test that UI provider is cached after first call."""
        factory = ProviderFactory(use_mocks=True)
        
        provider1 = factory.get_ui_provider()
        provider2 = factory.get_ui_provider()
        
        assert provider1 is provider2
        assert factory._ui_provider is provider1
    
    def test_get_pydantic_provider_with_mocks(self):
        """Test getting Pydantic provider when mocks are enabled."""
        factory = ProviderFactory(use_mocks=True)
        provider = factory.get_pydantic_provider()
        
        assert provider is not None
        # Mock provider should be returned directly, not cached
    
    def test_get_pydantic_provider_real(self):
        """Test getting real Pydantic provider."""
        factory = ProviderFactory(use_mocks=False)
        provider = factory.get_pydantic_provider()
        
        assert provider is not None
        assert factory._pydantic_provider is provider
    
    def test_get_pydantic_provider_caching(self):
        """Test that Pydantic provider is cached after first call."""
        factory = ProviderFactory(use_mocks=False)
        
        provider1 = factory.get_pydantic_provider()
        provider2 = factory.get_pydantic_provider()
        
        assert provider1 is provider2
        assert factory._pydantic_provider is provider1
    
    def test_provider_factory_different_types(self):
        """Test factory with different provider types simultaneously."""
        factory = ProviderFactory(use_mocks=False)
        
        # Get different types of providers
        ai_provider = factory.get_ai_provider("openai")
        ui_provider = factory.get_ui_provider("rich")
        pydantic_provider = factory.get_pydantic_provider()
        
        assert ai_provider is not None
        assert ui_provider is not None
        assert pydantic_provider is not None
        
        # Verify they're cached separately
        assert factory._ai_provider is ai_provider
        assert factory._ui_provider is ui_provider
        assert factory._pydantic_provider is pydantic_provider
    
    def test_provider_factory_mixed_mode(self):
        """Test factory behavior with mixed real/mock providers."""
        factory = ProviderFactory(use_mocks=False)
        
        # Get real providers
        real_ai = factory.get_ai_provider()
        real_ui = factory.get_ui_provider()
        
        # Create new factory with mocks
        mock_factory = ProviderFactory(use_mocks=True)
        mock_ai = mock_factory.get_ai_provider()
        mock_ui = mock_factory.get_ui_provider()
        
        # Verify they're different instances
        assert real_ai is not mock_ai
        assert real_ui is not mock_ui
        
        # Verify mock factory has no cached real providers
        assert mock_factory._ai_provider is None
        assert mock_factory._ui_provider is None
    
    @patch('src.providers.provider_factory.logging.getLogger')
    def test_logger_initialization(self, mock_get_logger):
        """Test that logger is properly initialized."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        factory = ProviderFactory()
        
        mock_get_logger.assert_called_once_with(__name__)
        assert factory.logger is mock_logger
