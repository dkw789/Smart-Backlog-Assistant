"""Comprehensive tests for AI processor to improve code coverage."""

import pytest
import os
from unittest.mock import patch, MagicMock, Mock
from typing import Dict, Any, Optional

from src.processors.ai_processor import AIProcessor, AIResponse
from src.utils.exception_handler import ConfigurationError


class TestAIResponse:
    """Tests for AIResponse dataclass."""
    
    def test_ai_response_creation_success(self):
        """Test AIResponse creation with successful response."""
        response = AIResponse(
            content="Test AI response content",
            service_used="openai",
            processing_time=1.5,
            success=True
        )
        
        assert response.content == "Test AI response content"
        assert response.service_used == "openai"
        assert response.processing_time == 1.5
        assert response.success is True
        assert response.error_message is None
    
    def test_ai_response_creation_failure(self):
        """Test AIResponse creation with failed response."""
        response = AIResponse(
            content="",
            service_used="anthropic",
            processing_time=0.5,
            success=False,
            error_message="API rate limit exceeded"
        )
        
        assert response.content == ""
        assert response.service_used == "anthropic"
        assert response.processing_time == 0.5
        assert response.success is False
        assert response.error_message == "API rate limit exceeded"
    
    def test_ai_response_attributes_mutable(self):
        """Test that AIResponse attributes can be modified."""
        response = AIResponse("initial", "openai", 1.0, True)
        
        response.content = "modified content"
        response.success = False
        response.error_message = "Modified error"
        
        assert response.content == "modified content"
        assert response.success is False
        assert response.error_message == "Modified error"


class TestAIProcessor:
    """Tests for AIProcessor class."""
    
    @patch('src.processors.ai_processor.get_logger')
    @patch.object(AIProcessor, '_initialize_clients')
    def test_ai_processor_initialization(self, mock_init_clients, mock_get_logger):
        """Test AIProcessor initialization."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        processor = AIProcessor()
        
        assert processor.openai_client is None
        assert processor.anthropic_client is None
        assert processor.qwen_client is None
        assert processor.max_retries == 3  # Default from config
        assert processor.timeout == 30  # Default from config
        assert processor.logger == mock_logger
        mock_init_clients.assert_called_once()
    
    @patch('src.processors.ai_processor.openai.OpenAI')
    @patch('src.processors.ai_processor.anthropic.Anthropic')
    @patch('src.processors.ai_processor.openai.OpenAI')
    @patch('src.processors.ai_processor.os.getenv')
    @patch.object(AIProcessor, '__init__', lambda x: None)
    def test_initialize_clients_all_available(self, mock_getenv, mock_openai_class, mock_anthropic_class, mock_qwen_class):
        """Test client initialization when all API keys are available."""
        # Mock environment variables
        def mock_env_side_effect(key, default=None):
            env_vars = {
                'OPENAI_API_KEY': 'test_openai_key',
                'ANTHROPIC_API_KEY': 'test_anthropic_key',
                'QWEN_BASE_URL': 'http://test-qwen-url',
                'QWEN_API_KEY': 'test_qwen_key'
            }
            return env_vars.get(key, default)
        
        mock_getenv.side_effect = mock_env_side_effect
        
        # Mock client instances
        mock_openai_instance = MagicMock()
        mock_anthropic_instance = MagicMock()
        mock_qwen_instance = MagicMock()
        
        mock_openai_class.return_value = mock_openai_instance
        mock_anthropic_class.return_value = mock_anthropic_instance
        mock_qwen_class.return_value = mock_qwen_instance
        
        processor = AIProcessor.__new__(AIProcessor)
        processor.logger = MagicMock()
        processor._initialize_clients()
        
        assert processor.openai_client == mock_openai_instance
        assert processor.anthropic_client == mock_anthropic_instance
        assert processor.qwen_client == mock_qwen_instance
    
    @patch('src.processors.ai_processor.os.getenv')
    @patch.object(AIProcessor, '__init__', lambda x: None)
    def test_initialize_clients_no_keys(self, mock_getenv):
        """Test client initialization when no API keys are available."""
        mock_getenv.return_value = None
        
        processor = AIProcessor.__new__(AIProcessor)
        processor.logger = MagicMock()
        processor._initialize_clients()
        
        assert processor.openai_client is None
        assert processor.anthropic_client is None
        assert processor.qwen_client is None
    
    @patch.object(AIProcessor, '_call_openai')
    @patch.object(AIProcessor, '__init__', lambda x: None)
    def test_extract_requirements_success(self, mock_call_openai):
        """Test successful requirements extraction."""
        mock_response = AIResponse(
            content='["Requirement 1", "Requirement 2"]',
            service_used="openai",
            processing_time=1.0,
            success=True
        )
        mock_call_openai.return_value = mock_response
        
        processor = AIProcessor.__new__(AIProcessor)
        processor.openai_client = MagicMock()
        processor.anthropic_client = None
        processor.qwen_client = None
        processor.logger = MagicMock()
        
        result = processor.extract_requirements("Test meeting notes content")
        
        assert result.success is True
        assert result.content == '["Requirement 1", "Requirement 2"]'
        assert result.service_used == "openai"
        mock_call_openai.assert_called_once()
    
    @patch.object(AIProcessor, '_call_openai')
    @patch.object(AIProcessor, '_call_anthropic')
    @patch.object(AIProcessor, '__init__', lambda x: None)
    def test_extract_requirements_fallback(self, mock_call_anthropic, mock_call_openai):
        """Test requirements extraction with fallback to Anthropic."""
        # OpenAI fails
        mock_openai_response = AIResponse("", "openai", 0.5, False, "API Error")
        mock_call_openai.return_value = mock_openai_response
        
        # Anthropic succeeds
        mock_anthropic_response = AIResponse(
            content='["Fallback requirement"]',
            service_used="anthropic",
            processing_time=1.2,
            success=True
        )
        mock_call_anthropic.return_value = mock_anthropic_response
        
        processor = AIProcessor.__new__(AIProcessor)
        processor.openai_client = MagicMock()
        processor.anthropic_client = MagicMock()
        processor.qwen_client = None
        processor.logger = MagicMock()
        
        result = processor.extract_requirements("Test content")
        
        assert result.success is True
        assert result.content == '["Fallback requirement"]'
        assert result.service_used == "anthropic"
        mock_call_openai.assert_called_once()
        mock_call_anthropic.assert_called_once()
    
    @patch.object(AIProcessor, '_call_openai')
    @patch.object(AIProcessor, '__init__', lambda x: None)
    def test_assess_priority_success(self, mock_call_openai):
        """Test successful priority assessment."""
        mock_response = AIResponse(
            content="Priority: High\nReasoning: Critical feature",
            service_used="openai",
            processing_time=0.8,
            success=True
        )
        mock_call_openai.return_value = mock_response
        
        processor = AIProcessor.__new__(AIProcessor)
        processor.openai_client = MagicMock()
        processor.anthropic_client = None
        processor.qwen_client = None
        processor.logger = MagicMock()
        
        result = processor.assess_priority("User authentication feature")
        
        assert result.success is True
        assert "Priority: High" in result.content
        assert result.service_used == "openai"
        mock_call_openai.assert_called_once()
    
    @patch.object(AIProcessor, '_call_openai')
    @patch.object(AIProcessor, '__init__', lambda x: None)
    def test_generate_user_stories_success(self, mock_call_openai):
        """Test successful user story generation."""
        mock_response = AIResponse(
            content="As a user, I want to login so that I can access my account",
            service_used="openai",
            processing_time=2.1,
            success=True
        )
        mock_call_openai.return_value = mock_response
        
        processor = AIProcessor.__new__(AIProcessor)
        processor.openai_client = MagicMock()
        processor.anthropic_client = None
        processor.qwen_client = None
        processor.logger = MagicMock()
        
        result = processor.generate_user_stories(["User authentication", "Password reset"])
        
        assert result.success is True
        assert "As a user" in result.content
        assert result.service_used == "openai"
        mock_call_openai.assert_called_once()
    
    @patch.object(AIProcessor, '_call_openai')
    @patch.object(AIProcessor, '__init__', lambda x: None)
    def test_analyze_backlog_items_success(self, mock_call_openai):
        """Test successful backlog analysis."""
        mock_response = AIResponse(
            content="Health Score: 85%\nRecommendations: Add acceptance criteria",
            service_used="openai",
            processing_time=1.5,
            success=True
        )
        mock_call_openai.return_value = mock_response
        
        processor = AIProcessor.__new__(AIProcessor)
        processor.openai_client = MagicMock()
        processor.anthropic_client = None
        processor.qwen_client = None
        processor.logger = MagicMock()
        
        backlog_items = [
            {"title": "Feature 1", "description": "First feature"},
            {"title": "Feature 2", "description": "Second feature"}
        ]
        
        result = processor.analyze_backlog_items(backlog_items)
        
        assert result.success is True
        assert "Health Score" in result.content
        assert result.service_used == "openai"
        mock_call_openai.assert_called_once()
    
    @patch('src.processors.ai_processor.time.time')
    @patch.object(AIProcessor, '__init__', lambda x: None)
    def test_call_openai_success(self, mock_time):
        """Test successful OpenAI API call."""
        mock_time.side_effect = [1000.0, 1001.5]  # Start and end times
        
        # Mock OpenAI client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "OpenAI response content"
        mock_client.chat.completions.create.return_value = mock_response
        
        processor = AIProcessor.__new__(AIProcessor)
        processor.openai_client = mock_client
        processor.timeout = 30
        processor.logger = MagicMock()
        
        result = processor._call_openai("Test prompt")
        
        assert result.success is True
        assert result.content == "OpenAI response content"
        assert result.service_used == "openai"
        assert result.processing_time == 1.5
        mock_client.chat.completions.create.assert_called_once()
    
    @patch.object(AIProcessor, '__init__', lambda x: None)
    def test_call_openai_no_client(self):
        """Test OpenAI call when client is not available."""
        processor = AIProcessor.__new__(AIProcessor)
        processor.openai_client = None
        processor.logger = MagicMock()
        
        result = processor._call_openai("Test prompt")
        
        assert result.success is False
        assert result.content == ""
        assert result.service_used == "openai"
        assert "OpenAI client not available" in result.error_message
    
    @patch('src.processors.ai_processor.time.time')
    @patch.object(AIProcessor, '__init__', lambda x: None)
    def test_call_anthropic_success(self, mock_time):
        """Test successful Anthropic API call."""
        mock_time.side_effect = [2000.0, 2002.0]  # Start and end times
        
        # Mock Anthropic client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = "Anthropic response content"
        mock_client.messages.create.return_value = mock_response
        
        processor = AIProcessor.__new__(AIProcessor)
        processor.anthropic_client = mock_client
        processor.timeout = 30
        processor.logger = MagicMock()
        
        result = processor._call_anthropic("Test prompt")
        
        assert result.success is True
        assert result.content == "Anthropic response content"
        assert result.service_used == "anthropic"
        assert result.processing_time == 2.0
        mock_client.messages.create.assert_called_once()
    
    @patch.object(AIProcessor, '__init__', lambda x: None)
    def test_call_anthropic_no_client(self):
        """Test Anthropic call when client is not available."""
        processor = AIProcessor.__new__(AIProcessor)
        processor.anthropic_client = None
        processor.logger = MagicMock()
        
        result = processor._call_anthropic("Test prompt")
        
        assert result.success is False
        assert result.content == ""
        assert result.service_used == "anthropic"
        assert "Anthropic client not available" in result.error_message
    
    @patch('src.processors.ai_processor.time.time')
    @patch.object(AIProcessor, '__init__', lambda x: None)
    def test_call_qwen_success(self, mock_time):
        """Test successful Qwen API call."""
        mock_time.side_effect = [3000.0, 3001.0]  # Start and end times
        
        # Mock Qwen client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Qwen response content"
        mock_client.chat.completions.create.return_value = mock_response
        
        processor = AIProcessor.__new__(AIProcessor)
        processor.qwen_client = mock_client
        processor.timeout = 30
        processor.logger = MagicMock()
        
        result = processor._call_qwen("Test prompt")
        
        assert result.success is True
        assert result.content == "Qwen response content"
        assert result.service_used == "qwen"
        assert result.processing_time == 1.0
        mock_client.chat.completions.create.assert_called_once()
    
    @patch.object(AIProcessor, '__init__', lambda x: None)
    def test_call_qwen_no_client(self):
        """Test Qwen call when client is not available."""
        processor = AIProcessor.__new__(AIProcessor)
        processor.qwen_client = None
        processor.logger = MagicMock()
        
        result = processor._call_qwen("Test prompt")
        
        assert result.success is False
        assert result.content == ""
        assert result.service_used == "qwen"
        assert "Qwen client not available" in result.error_message
    
    @patch.object(AIProcessor, '_call_openai')
    @patch.object(AIProcessor, '_call_anthropic')
    @patch.object(AIProcessor, '_call_qwen')
    @patch.object(AIProcessor, '__init__', lambda x: None)
    def test_all_services_fail(self, mock_call_qwen, mock_call_anthropic, mock_call_openai):
        """Test behavior when all AI services fail."""
        # All services fail
        failed_response = AIResponse("", "service", 0.1, False, "Service unavailable")
        mock_call_openai.return_value = failed_response
        mock_call_anthropic.return_value = failed_response
        mock_call_qwen.return_value = failed_response
        
        processor = AIProcessor.__new__(AIProcessor)
        processor.openai_client = MagicMock()
        processor.anthropic_client = MagicMock()
        processor.qwen_client = MagicMock()
        processor.logger = MagicMock()
        
        result = processor.extract_requirements("Test content")
        
        assert result.success is False
        assert result.content == ""
        assert "All AI services failed" in result.error_message
        
        # All three services should have been attempted
        mock_call_openai.assert_called_once()
        mock_call_anthropic.assert_called_once()
        mock_call_qwen.assert_called_once()
    
    @patch.object(AIProcessor, '__init__', lambda x: None)
    def test_no_clients_available(self):
        """Test behavior when no AI clients are available."""
        processor = AIProcessor.__new__(AIProcessor)
        processor.openai_client = None
        processor.anthropic_client = None
        processor.qwen_client = None
        processor.logger = MagicMock()
        
        result = processor.extract_requirements("Test content")
        
        assert result.success is False
        assert result.content == ""
        assert "All AI services failed" in result.error_message
    
    @patch('src.processors.ai_processor.time.time')
    @patch.object(AIProcessor, '__init__', lambda x: None)
    def test_api_call_exception_handling(self, mock_time):
        """Test exception handling during API calls."""
        mock_time.side_effect = [4000.0, 4000.5]
        
        # Mock client that raises exception
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Network error")
        
        processor = AIProcessor.__new__(AIProcessor)
        processor.openai_client = mock_client
        processor.timeout = 30
        processor.logger = MagicMock()
        
        result = processor._call_openai("Test prompt")
        
        assert result.success is False
        assert result.content == ""
        assert result.service_used == "openai"
        assert "Network error" in result.error_message
        assert result.processing_time == 0.5


class TestAIProcessorIntegration:
    """Integration tests for AIProcessor."""
    
    @patch('src.processors.ai_processor.os.getenv')
    @patch('src.processors.ai_processor.openai.OpenAI')
    def test_processor_with_mocked_openai_integration(self, mock_openai_class, mock_getenv):
        """Test AI processor integration with mocked OpenAI."""
        # Mock environment
        mock_getenv.side_effect = lambda key, default=None: {
            'OPENAI_API_KEY': 'test_key'
        }.get(key, default)
        
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Mocked AI response"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        with patch('src.processors.ai_processor.time.time', side_effect=[1000.0, 1001.0]):
            processor = AIProcessor()
            result = processor.extract_requirements("Test meeting notes")
        
        assert result.success is True
        assert result.content == "Mocked AI response"
        assert result.service_used == "openai"
        assert result.processing_time == 1.0
    
    def test_ai_response_serialization(self):
        """Test that AIResponse can be converted to dict-like structure."""
        response = AIResponse(
            content="Test content",
            service_used="openai",
            processing_time=1.5,
            success=True,
            error_message=None
        )
        
        # Test that all attributes are accessible
        assert hasattr(response, 'content')
        assert hasattr(response, 'service_used')
        assert hasattr(response, 'processing_time')
        assert hasattr(response, 'success')
        assert hasattr(response, 'error_message')
        
        # Test attribute values
        assert response.content == "Test content"
        assert response.service_used == "openai"
        assert response.processing_time == 1.5
        assert response.success is True
        assert response.error_message is None
