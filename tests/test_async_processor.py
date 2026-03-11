"""Tests for AsyncAIProcessor to ensure robust async handling and coverage."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from src.processors.ai_processor_async import AsyncAIProcessor, AIResponse

@pytest.mark.asyncio
class TestAsyncAIProcessor:
    """Tests for AsyncAIProcessor class."""

    async def test_initialization(self):
        """Test initialization of AsyncAIProcessor."""
        with patch('src.processors.ai_processor_async.openai.AsyncOpenAI') as mock_openai, \
             patch('src.processors.ai_processor_async.anthropic.AsyncAnthropic') as mock_anthropic, \
             patch('src.processors.ai_processor_async.validate_api_key'):
            
            processor = AsyncAIProcessor()
            assert processor.openai_client is not None
            assert processor.anthropic_client is not None

    async def test_context_manager(self):
        """Test async context manager."""
        with patch('src.processors.ai_processor_async.openai.AsyncOpenAI'), \
             patch('src.processors.ai_processor_async.anthropic.AsyncAnthropic'), \
             patch('src.processors.ai_processor_async.validate_api_key'):
            
            async with AsyncAIProcessor() as processor:
                assert processor.session is not None
                assert not processor.session.closed
            
            assert processor.session.closed

    async def test_extract_requirements_success(self):
        """Test successful requirement extraction."""
        with patch('src.processors.ai_processor_async.openai.AsyncOpenAI') as mock_openai, \
             patch('src.processors.ai_processor_async.anthropic.AsyncAnthropic') as mock_anthropic, \
             patch('src.processors.ai_processor_async.validate_api_key'), \
             patch('src.processors.ai_processor_async.config') as mock_config:
            
            # Setup config to use OpenAI
            mock_config.default_ai_service = "openai"
            mock_config.openai_api_key = "test_key"
            
            # Setup OpenAI mock response
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="Extracted requirements"))]
            mock_openai.return_value.chat.completions.create = AsyncMock(return_value=mock_response)
            
            processor = AsyncAIProcessor()
            result = await processor.extract_requirements("Test content")
            
            assert result.success
            assert result.content == "Extracted requirements"
            assert result.service_used == "openai"

    async def test_fallback_logic(self):
        """Test fallback from primary to secondary service."""
        with patch('src.processors.ai_processor_async.openai.AsyncOpenAI') as mock_openai, \
             patch('src.processors.ai_processor_async.anthropic.AsyncAnthropic') as mock_anthropic, \
             patch('src.processors.ai_processor_async.validate_api_key'), \
             patch('src.processors.ai_processor_async.config') as mock_config:
            
            # Setup config to prefer OpenAI
            mock_config.default_ai_service = "openai"
            mock_config.openai_api_key = "test_key"
            mock_config.anthropic_api_key = "test_key"

            # Fail OpenAI
            mock_openai.return_value.chat.completions.create = AsyncMock(side_effect=Exception("OpenAI Failed"))
            
            # Succeed Anthropic
            mock_anthropic_response = Mock(content=[Mock(text="Fallback success")])
            mock_anthropic.return_value.messages.create = AsyncMock(return_value=mock_anthropic_response)

            processor = AsyncAIProcessor()
            # Manually ensure both clients are set (mocking init logic if needed, but here mocks do it)
            
            result = await processor.extract_requirements("Test content")
            
            assert result.success
            assert result.content == "Fallback success"
            assert result.service_used == "anthropic"

    async def test_process_multiple_items_concurrently(self):
        """Test concurrent processing of multiple items."""
        with patch('src.processors.ai_processor_async.openai.AsyncOpenAI') as mock_openai, \
             patch('src.processors.ai_processor_async.anthropic.AsyncAnthropic'), \
             patch('src.processors.ai_processor_async.validate_api_key'), \
             patch('src.processors.ai_processor_async.config') as mock_config:
            
            mock_config.default_ai_service = "openai"
            
            # Mock successful response
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="Processed"))]
            mock_openai.return_value.chat.completions.create = AsyncMock(return_value=mock_response)
            
            processor = AsyncAIProcessor()
            items = [{"content": "item1"}, {"content": "item2"}, {"content": "item3"}]
            
            results = await processor.process_multiple_items_concurrently(items, "extract_requirements")
            
            assert len(results) == 3
            assert all(r.success for r in results)
            assert all(r.content == "Processed" for r in results)

    async def test_all_services_fail(self):
        """Test behavior when all services fail."""
        with patch('src.processors.ai_processor_async.openai.AsyncOpenAI') as mock_openai, \
             patch('src.processors.ai_processor_async.anthropic.AsyncAnthropic') as mock_anthropic, \
             patch('src.processors.ai_processor_async.validate_api_key'), \
             patch('src.processors.ai_processor_async.config') as mock_config:
            
            mock_config.default_ai_service = "openai"
            
            # Fail both
            mock_openai.return_value.chat.completions.create = AsyncMock(side_effect=Exception("OpenAI Failed"))
            mock_anthropic.return_value.messages.create = AsyncMock(side_effect=Exception("Anthropic Failed"))
            
            processor = AsyncAIProcessor()
            result = await processor.extract_requirements("Test content")
            
            assert not result.success
            assert "All AI services failed" in str(result.error_message) if result.error_message else False

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
