"""Tests for async AI processor."""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.processors.ai_processor_async import AIResponse, AsyncAIProcessor


class TestAIResponse:
    """Test the AIResponse dataclass."""

    def test_ai_response_creation(self):
        """Test creating an AIResponse."""
        response = AIResponse(
            content="Test response",
            service_used="anthropic",
            processing_time=1.5,
            success=True,
            error_message=None
        )
        
        assert response.content == "Test response"
        assert response.service_used == "anthropic"
        assert response.processing_time == 1.5
        assert response.success is True
        assert response.error_message is None

    def test_ai_response_with_error(self):
        """Test creating an AIResponse with error."""
        response = AIResponse(
            content="",
            service_used="none",
            processing_time=0.1,
            success=False,
            error_message="API key not found"
        )
        
        assert response.content == ""
        assert response.service_used == "none"
        assert response.processing_time == 0.1
        assert response.success is False
        assert response.error_message == "API key not found"


class TestAsyncAIProcessor:
    """Test the AsyncAIProcessor class."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        with patch('src.processors.ai_processor_async.config') as mock_config:
            mock_config.openai_api_key = "test-openai-key"
            mock_config.anthropic_api_key = "test-anthropic-key"
            mock_config.max_retries = 3
            mock_config.timeout_seconds = 30
            mock_config.max_tokens = 2000
            mock_config.temperature = 0.7
            mock_config.default_ai_service = "anthropic"
            yield mock_config

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI async client."""
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "OpenAI response"
        mock_client.chat.completions.create.return_value = mock_response
        return mock_client

    @pytest.fixture
    def mock_anthropic_client(self):
        """Mock Anthropic async client."""
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "Anthropic response"
        mock_client.messages.create.return_value = mock_response
        return mock_client

    def test_processor_initialization(self, mock_config):
        """Test processor initialization."""
        with patch('anthropic.AsyncAnthropic') as mock_anthropic, \
             patch('openai.AsyncOpenAI') as mock_openai:
            
            processor = AsyncAIProcessor()
            
            assert processor.max_retries == 3
            assert processor.timeout == 30
            assert processor.session is None
            mock_openai.assert_called_once()
            mock_anthropic.assert_called_once()

    def test_processor_initialization_no_keys(self):
        """Test processor initialization with no API keys."""
        with patch('src.processors.ai_processor_async.config') as mock_config:
            mock_config.openai_api_key = None
            mock_config.anthropic_api_key = None
            mock_config.max_retries = 3
            mock_config.timeout_seconds = 30
            
            # Without API keys, processor should still initialize but log warnings
            # The actual ConfigurationError is only raised if no services are available
            with patch('src.processors.ai_processor_async.validate_api_key') as mock_validate:
                mock_validate.side_effect = Exception("No API key")
                
                with pytest.raises(Exception):  # Should raise ConfigurationError
                    AsyncAIProcessor()

    @pytest.mark.asyncio
    async def test_context_manager(self, mock_config):
        """Test async context manager."""
        with patch('anthropic.AsyncAnthropic'), \
             patch('openai.AsyncOpenAI'), \
             patch('aiohttp.ClientSession') as mock_session_class:
            
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            async with AsyncAIProcessor() as processor:
                assert processor.session == mock_session
            
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_requirements(self, mock_config, mock_anthropic_client):
        """Test extracting requirements."""
        with patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client), \
             patch('openai.AsyncOpenAI'):
            
            processor = AsyncAIProcessor()
            
            response = await processor.extract_requirements("Test content")
            
            assert response.success is True
            assert response.content == "Anthropic response"
            assert response.service_used == "anthropic"
            assert response.processing_time > 0

    @pytest.mark.asyncio
    async def test_generate_user_stories(self, mock_config, mock_anthropic_client):
        """Test generating user stories."""
        with patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client), \
             patch('openai.AsyncOpenAI'):
            
            processor = AsyncAIProcessor()
            
            response = await processor.generate_user_stories("Test requirements")
            
            assert response.success is True
            assert response.content == "Anthropic response"
            assert response.service_used == "anthropic"
            mock_anthropic_client.messages.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_assess_priority(self, mock_config, mock_anthropic_client):
        """Test assessing priority."""
        with patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client), \
             patch('openai.AsyncOpenAI'):
            
            processor = AsyncAIProcessor()
            
            response = await processor.assess_priority("Test item description")
            
            assert response.success is True
            assert response.content == "Anthropic response"
            assert response.service_used == "anthropic"

    @pytest.mark.asyncio
    async def test_analyze_backlog_items(self, mock_config, mock_anthropic_client):
        """Test analyzing backlog items."""
        with patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client), \
             patch('openai.AsyncOpenAI'):
            
            processor = AsyncAIProcessor()
            
            backlog_data = [
                {"title": "Item 1", "description": "Description 1"},
                {"title": "Item 2", "description": "Description 2"}
            ]
            
            response = await processor.analyze_backlog_items(backlog_data)
            
            assert response.success is True
            assert response.content == "Anthropic response"
            assert response.service_used == "anthropic"

    @pytest.mark.asyncio
    async def test_process_multiple_items_concurrently(self, mock_config, mock_anthropic_client):
        """Test processing multiple items concurrently."""
        with patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client), \
             patch('openai.AsyncOpenAI'):
            
            processor = AsyncAIProcessor()
            
            items = [
                {"description": "Item 1 description"},
                {"description": "Item 2 description"},
                {"description": "Item 3 description"}
            ]
            
            results = await processor.process_multiple_items_concurrently(
                items, "assess_priority"
            )
            
            assert len(results) == 3
            for result in results:
                assert isinstance(result, AIResponse)
                assert result.success is True
                assert result.content == "Anthropic response"

    @pytest.mark.asyncio
    async def test_process_multiple_items_with_exception(self, mock_config):
        """Test processing multiple items with exceptions."""
        with patch('anthropic.AsyncAnthropic') as mock_anthropic, \
             patch('openai.AsyncOpenAI') as mock_openai:
            
            # Make both services fail for one item to test exception handling
            mock_anthropic_client = AsyncMock()
            mock_openai_client = AsyncMock()
            
            # First item succeeds, second fails, third succeeds
            mock_anthropic_client.messages.create.side_effect = [
                Mock(content=[Mock(text="Success 1")]),
                Exception("Anthropic API Error"),
                Mock(content=[Mock(text="Success 3")])
            ]
            
            mock_openai_client.chat.completions.create.side_effect = [
                Exception("OpenAI also fails"),  # Fallback also fails for item 2
            ]
            
            mock_anthropic.return_value = mock_anthropic_client
            mock_openai.return_value = mock_openai_client
            
            processor = AsyncAIProcessor()
            
            items = [
                {"description": "Item 1"},
                {"description": "Item 2"},  # This will fail
                {"description": "Item 3"}
            ]
            
            results = await processor.process_multiple_items_concurrently(
                items, "assess_priority"
            )
            
            assert len(results) == 3
            assert results[0].success is True
            assert results[1].success is False
            assert "All AI services failed" in results[1].error_message
            assert results[2].success is True

    @pytest.mark.asyncio
    async def test_fallback_to_openai(self, mock_config, mock_openai_client):
        """Test fallback from Anthropic to OpenAI."""
        with patch('anthropic.AsyncAnthropic') as mock_anthropic, \
             patch('openai.AsyncOpenAI', return_value=mock_openai_client):
            
            # Make Anthropic fail
            mock_anthropic_client = AsyncMock()
            mock_anthropic_client.messages.create.side_effect = Exception("Anthropic error")
            mock_anthropic.return_value = mock_anthropic_client
            
            processor = AsyncAIProcessor()
            
            response = await processor.extract_requirements("Test content")
            
            assert response.success is True
            assert response.content == "OpenAI response"
            assert response.service_used == "openai"

    @pytest.mark.asyncio
    async def test_all_services_fail(self, mock_config):
        """Test when all AI services fail."""
        with patch('anthropic.AsyncAnthropic') as mock_anthropic, \
             patch('openai.AsyncOpenAI') as mock_openai:
            
            # Make both services fail
            mock_anthropic_client = AsyncMock()
            mock_anthropic_client.messages.create.side_effect = Exception("Anthropic error")
            mock_anthropic.return_value = mock_anthropic_client
            
            mock_openai_client = AsyncMock()
            mock_openai_client.chat.completions.create.side_effect = Exception("OpenAI error")
            mock_openai.return_value = mock_openai_client
            
            processor = AsyncAIProcessor()
            
            response = await processor.extract_requirements("Test content")
            
            assert response.success is False
            assert response.service_used == "none"
            assert response.error_message == "All AI services failed"

    @pytest.mark.asyncio
    async def test_openai_as_default_service(self, mock_config, mock_openai_client):
        """Test using OpenAI as default service."""
        mock_config.default_ai_service = "openai"
        
        with patch('anthropic.AsyncAnthropic'), \
             patch('openai.AsyncOpenAI', return_value=mock_openai_client):
            
            processor = AsyncAIProcessor()
            
            response = await processor.extract_requirements("Test content")
            
            assert response.success is True
            assert response.content == "OpenAI response"
            assert response.service_used == "openai"

    def test_summarize_backlog(self, mock_config):
        """Test backlog summarization."""
        with patch('anthropic.AsyncAnthropic'), \
             patch('openai.AsyncOpenAI'):
            
            processor = AsyncAIProcessor()
            
            backlog_data = [
                {
                    "title": "Feature 1",
                    "description": "Implement user authentication system",
                    "priority": "high",
                    "status": "todo"
                },
                {
                    "title": "Bug Fix",
                    "description": "Fix login redirect issue",
                    "priority": "critical",
                    "status": "in_progress"
                }
            ]
            
            summary = processor._summarize_backlog(backlog_data)
            
            assert "Feature 1" in summary
            assert "Bug Fix" in summary
            assert "Implement user authentication" in summary
            assert "high" in summary
            assert "critical" in summary

    def test_summarize_backlog_long_list(self, mock_config):
        """Test backlog summarization with long list."""
        with patch('anthropic.AsyncAnthropic'), \
             patch('openai.AsyncOpenAI'):
            
            processor = AsyncAIProcessor()
            
            # Create 25 items (more than the 20 limit)
            backlog_data = []
            for i in range(25):
                backlog_data.append({
                    "title": f"Item {i}",
                    "description": f"Description for item {i}",
                    "priority": "medium",
                    "status": "todo"
                })
            
            summary = processor._summarize_backlog(backlog_data)
            
            # Should include first 20 items
            assert "Item 0" in summary
            assert "Item 19" in summary
            
            # Should not include items beyond 20
            assert "Item 20" not in summary
            assert "Item 24" not in summary
            
            # Should include summary line
            assert "and 5 more items" in summary

    @pytest.mark.asyncio
    async def test_anthropic_api_call(self, mock_config, mock_anthropic_client):
        """Test direct Anthropic API call."""
        with patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client), \
             patch('openai.AsyncOpenAI'):
            
            processor = AsyncAIProcessor()
            
            result = await processor._call_anthropic_async("Test prompt")
            
            assert result == "Anthropic response"
            mock_anthropic_client.messages.create.assert_called_once_with(
                model="claude-3-haiku-20240307",
                max_tokens=2000,
                messages=[{"role": "user", "content": "Test prompt"}]
            )

    @pytest.mark.asyncio
    async def test_openai_api_call(self, mock_config, mock_openai_client):
        """Test direct OpenAI API call."""
        with patch('anthropic.AsyncAnthropic'), \
             patch('openai.AsyncOpenAI', return_value=mock_openai_client):
            
            processor = AsyncAIProcessor()
            
            result = await processor._call_openai_async("Test prompt")
            
            assert result == "OpenAI response"
            mock_openai_client.chat.completions.create.assert_called_once_with(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert software engineering assistant.",
                    },
                    {"role": "user", "content": "Test prompt"},
                ],
                max_tokens=2000,
                temperature=0.7,
            )

    @pytest.mark.asyncio
    async def test_concurrent_request_limiting(self, mock_config, mock_anthropic_client):
        """Test that concurrent requests are limited by semaphore."""
        with patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client), \
             patch('openai.AsyncOpenAI'):
            
            processor = AsyncAIProcessor()
            
            # Create many items to test semaphore limiting
            items = [{"description": f"Item {i}"} for i in range(10)]
            
            # Mock the semaphore to track concurrent calls
            original_semaphore = asyncio.Semaphore(3)
            with patch('asyncio.Semaphore', return_value=original_semaphore) as mock_semaphore:
                results = await processor.process_multiple_items_concurrently(
                    items, "assess_priority"
                )
                
                # Should have created semaphore with limit 3
                mock_semaphore.assert_called_once_with(3)
                assert len(results) == 10

    def test_processor_without_context_manager(self, mock_config):
        """Test processor usage without context manager."""
        with patch('anthropic.AsyncAnthropic'), \
             patch('openai.AsyncOpenAI'):
            
            processor = AsyncAIProcessor()
            
            # Should work without context manager
            assert processor.session is None
            assert processor.openai_client is not None
            assert processor.anthropic_client is not None

    @pytest.mark.asyncio
    async def test_invalid_operation_type(self, mock_config, mock_anthropic_client):
        """Test processing with invalid operation type."""
        with patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client), \
             patch('openai.AsyncOpenAI'):
            
            processor = AsyncAIProcessor()
            
            items = [{"description": "Test item"}]
            
            results = await processor.process_multiple_items_concurrently(
                items, "invalid_operation"
            )
            
            # Should return empty list for invalid operation
            assert len(results) == 0

    @pytest.mark.asyncio
    async def test_empty_items_list(self, mock_config):
        """Test processing empty items list."""
        with patch('anthropic.AsyncAnthropic'), \
             patch('openai.AsyncOpenAI'):
            
            processor = AsyncAIProcessor()
            
            results = await processor.process_multiple_items_concurrently(
                [], "assess_priority"
            )
            
            assert len(results) == 0

    def test_processor_logger_initialization(self, mock_config):
        """Test that processor initializes logger correctly."""
        with patch('anthropic.AsyncAnthropic'), \
             patch('openai.AsyncOpenAI'), \
             patch('src.processors.ai_processor_async.get_logger') as mock_get_logger:
            
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            processor = AsyncAIProcessor()
            
            mock_get_logger.assert_called_once_with('src.processors.ai_processor_async')
            assert processor.logger == mock_logger
