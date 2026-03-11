"""Comprehensive tests for mock providers to improve code coverage."""

import pytest
from typing import Dict, List, Any

from src.providers.mock_providers import (
    MockAIResponse, 
    MockAIProvider, 
    MockConsoleProvider, 
    MockFailingAIProvider
)
from src.processors.ai_processor import AIResponse


class TestMockAIResponse:
    """Tests for MockAIResponse dataclass."""
    
    def test_mock_ai_response_creation_defaults(self):
        """Test MockAIResponse creation with default values."""
        response = MockAIResponse(content="test content")
        
        assert response.content == "test content"
        assert response.service_used == "mock"
        assert response.processing_time == 0.1
        assert response.success is True
        assert response.error_message is None
    
    def test_mock_ai_response_creation_custom(self):
        """Test MockAIResponse creation with custom values."""
        response = MockAIResponse(
            content="custom content",
            service_used="custom_mock",
            processing_time=0.5,
            success=False,
            error_message="Custom error"
        )
        
        assert response.content == "custom content"
        assert response.service_used == "custom_mock"
        assert response.processing_time == 0.5
        assert response.success is False
        assert response.error_message == "Custom error"
    
    def test_mock_ai_response_attributes_mutable(self):
        """Test that MockAIResponse attributes can be modified."""
        response = MockAIResponse(content="initial")
        
        response.content = "modified"
        response.success = False
        response.error_message = "Error occurred"
        
        assert response.content == "modified"
        assert response.success is False
        assert response.error_message == "Error occurred"


class TestMockAIProvider:
    """Tests for MockAIProvider class."""
    
    def test_mock_ai_provider_default_initialization(self):
        """Test MockAIProvider initialization with default responses."""
        provider = MockAIProvider()
        
        assert provider.call_count == 0
        assert "assess_priority" in provider.responses
        assert "generate_user_stories" in provider.responses
        assert "analyze_backlog_items" in provider.responses
        
        # Check default response content
        assert "Priority: High" in provider.responses["assess_priority"]
        assert "Story 1" in provider.responses["generate_user_stories"]
        assert "health score" in provider.responses["analyze_backlog_items"]
    
    def test_mock_ai_provider_custom_responses(self):
        """Test MockAIProvider initialization with custom responses."""
        custom_responses = {
            "assess_priority": "Custom priority response",
            "generate_user_stories": "Custom story response",
            "analyze_backlog_items": "Custom analysis response"
        }
        
        provider = MockAIProvider(responses=custom_responses)
        
        assert provider.responses == custom_responses
        assert provider.call_count == 0
    
    def test_assess_priority_method(self):
        """Test assess_priority method functionality."""
        provider = MockAIProvider()
        
        result = provider.assess_priority("Test item description")
        
        assert isinstance(result, AIResponse)
        assert result.content == provider.responses["assess_priority"]
        assert result.service_used == "mock"
        assert result.processing_time == 0.1
        assert result.success is True
        assert provider.call_count == 1
    
    def test_assess_priority_custom_response(self):
        """Test assess_priority with custom response."""
        custom_response = "Custom priority assessment result"
        provider = MockAIProvider(responses={"assess_priority": custom_response})
        
        result = provider.assess_priority("Test description")
        
        assert result.content == custom_response
        assert provider.call_count == 1
    
    def test_assess_priority_missing_response(self):
        """Test assess_priority when response key is missing."""
        provider = MockAIProvider(responses={})
        
        result = provider.assess_priority("Test description")
        
        # When key is missing, it uses the default from the constructor
        assert "Priority: High" in result.content
        assert provider.call_count == 1
    
    def test_generate_user_stories_method(self):
        """Test generate_user_stories method functionality."""
        provider = MockAIProvider()
        
        result = provider.generate_user_stories("Test requirements")
        
        assert isinstance(result, AIResponse)
        assert result.content == provider.responses["generate_user_stories"]
        assert result.service_used == "mock"
        assert result.processing_time == 0.1
        assert result.success is True
        assert provider.call_count == 1
    
    def test_generate_user_stories_custom_response(self):
        """Test generate_user_stories with custom response."""
        custom_response = "Custom user story generation result"
        provider = MockAIProvider(responses={"generate_user_stories": custom_response})
        
        result = provider.generate_user_stories("Test requirements")
        
        assert result.content == custom_response
        assert provider.call_count == 1
    
    def test_generate_user_stories_missing_response(self):
        """Test generate_user_stories when response key is missing."""
        provider = MockAIProvider(responses={})
        
        result = provider.generate_user_stories("Test requirements")
        
        # When key is missing, it uses the default from the constructor
        assert "Story 1" in result.content
        assert provider.call_count == 1
    
    def test_analyze_backlog_items_method(self):
        """Test analyze_backlog_items method functionality."""
        provider = MockAIProvider()
        backlog_data = [
            {"title": "Task 1", "description": "First task"},
            {"title": "Task 2", "description": "Second task"}
        ]
        
        result = provider.analyze_backlog_items(backlog_data)
        
        assert isinstance(result, AIResponse)
        assert result.content == provider.responses["analyze_backlog_items"]
        assert result.service_used == "mock"
        assert result.processing_time == 0.1
        assert result.success is True
        assert provider.call_count == 1
    
    def test_analyze_backlog_items_custom_response(self):
        """Test analyze_backlog_items with custom response."""
        custom_response = "Custom backlog analysis result"
        provider = MockAIProvider(responses={"analyze_backlog_items": custom_response})
        
        result = provider.analyze_backlog_items([])
        
        assert result.content == custom_response
        assert provider.call_count == 1
    
    def test_analyze_backlog_items_missing_response(self):
        """Test analyze_backlog_items when response key is missing."""
        provider = MockAIProvider(responses={})
        
        result = provider.analyze_backlog_items([])
        
        # When key is missing, it uses the default from the constructor
        assert "health score" in result.content
        assert provider.call_count == 1
    
    def test_call_count_tracking(self):
        """Test that call count is properly tracked across methods."""
        provider = MockAIProvider()
        
        assert provider.call_count == 0
        
        provider.assess_priority("test")
        assert provider.call_count == 1
        
        provider.generate_user_stories("test")
        assert provider.call_count == 2
        
        provider.analyze_backlog_items([])
        assert provider.call_count == 3
        
        # Multiple calls to same method
        provider.assess_priority("test2")
        assert provider.call_count == 4
    
    def test_multiple_providers_independent(self):
        """Test that multiple provider instances are independent."""
        provider1 = MockAIProvider()
        provider2 = MockAIProvider()
        
        provider1.assess_priority("test1")
        provider2.generate_user_stories("test2")
        
        assert provider1.call_count == 1
        assert provider2.call_count == 1


class TestMockConsoleProvider:
    """Tests for MockConsoleProvider class."""
    
    def test_mock_console_provider_initialization(self):
        """Test MockConsoleProvider initialization."""
        provider = MockConsoleProvider()
        
        assert provider.printed_messages == []
        assert provider.input_responses == []
        assert provider.input_index == 0
    
    def test_print_method_single_argument(self):
        """Test print method with single argument."""
        provider = MockConsoleProvider()
        
        provider.print("Hello, World!")
        
        assert len(provider.printed_messages) == 1
        assert provider.printed_messages[0] == "Hello, World!"
    
    def test_print_method_multiple_arguments(self):
        """Test print method with multiple arguments."""
        provider = MockConsoleProvider()
        
        provider.print("Hello", "World", 123, True)
        
        assert len(provider.printed_messages) == 1
        assert provider.printed_messages[0] == "Hello World 123 True"
    
    def test_print_method_multiple_calls(self):
        """Test multiple calls to print method."""
        provider = MockConsoleProvider()
        
        provider.print("First message")
        provider.print("Second message")
        provider.print("Third", "message")
        
        assert len(provider.printed_messages) == 3
        assert provider.printed_messages[0] == "First message"
        assert provider.printed_messages[1] == "Second message"
        assert provider.printed_messages[2] == "Third message"
    
    def test_print_method_empty_arguments(self):
        """Test print method with no arguments."""
        provider = MockConsoleProvider()
        
        provider.print()
        
        assert len(provider.printed_messages) == 1
        assert provider.printed_messages[0] == ""
    
    def test_input_method_no_responses(self):
        """Test input method when no responses are set."""
        provider = MockConsoleProvider()
        
        result = provider.input("Enter something: ")
        
        assert result == "mock_input"
    
    def test_input_method_with_responses(self):
        """Test input method with predefined responses."""
        provider = MockConsoleProvider()
        responses = ["first", "second", "third"]
        provider.set_input_responses(responses)
        
        result1 = provider.input("First prompt: ")
        result2 = provider.input("Second prompt: ")
        result3 = provider.input("Third prompt: ")
        
        assert result1 == "first"
        assert result2 == "second"
        assert result3 == "third"
        assert provider.input_index == 3
    
    def test_input_method_exhausted_responses(self):
        """Test input method when responses are exhausted."""
        provider = MockConsoleProvider()
        provider.set_input_responses(["only_response"])
        
        result1 = provider.input("First: ")
        result2 = provider.input("Second: ")
        
        assert result1 == "only_response"
        assert result2 == "mock_input"  # Falls back to default
    
    def test_set_input_responses_method(self):
        """Test set_input_responses method functionality."""
        provider = MockConsoleProvider()
        
        # Set initial responses
        responses1 = ["a", "b", "c"]
        provider.set_input_responses(responses1)
        
        assert provider.input_responses == responses1
        assert provider.input_index == 0
        
        # Use some responses
        provider.input("test")
        provider.input("test")
        assert provider.input_index == 2
        
        # Reset with new responses
        responses2 = ["x", "y"]
        provider.set_input_responses(responses2)
        
        assert provider.input_responses == responses2
        assert provider.input_index == 0  # Reset to 0
    
    def test_combined_print_and_input(self):
        """Test combined usage of print and input methods."""
        provider = MockConsoleProvider()
        provider.set_input_responses(["user_response"])
        
        provider.print("Welcome to the system")
        user_input = provider.input("Enter your name: ")
        provider.print("Hello", user_input)
        
        assert len(provider.printed_messages) == 2
        assert provider.printed_messages[0] == "Welcome to the system"
        assert provider.printed_messages[1] == "Hello user_response"
        assert user_input == "user_response"


class TestMockFailingAIProvider:
    """Tests for MockFailingAIProvider class."""
    
    def test_mock_failing_ai_provider_initialization(self):
        """Test MockFailingAIProvider initialization."""
        provider = MockFailingAIProvider()
        
        assert provider.failure_rate == 1.0
        assert provider.call_count == 0
    
    def test_mock_failing_ai_provider_custom_failure_rate(self):
        """Test MockFailingAIProvider with custom failure rate."""
        provider = MockFailingAIProvider(failure_rate=0.5)
        
        assert provider.failure_rate == 0.5
        assert provider.call_count == 0
    
    def test_assess_priority_failure(self):
        """Test assess_priority method returns failure response."""
        provider = MockFailingAIProvider()
        
        result = provider.assess_priority("Test item")
        
        assert isinstance(result, AIResponse)
        assert result.content == ""
        assert result.service_used == "mock_failing"
        assert result.processing_time == 0.1
        assert result.success is False
        assert result.error_message == "Mock AI service failure"
        assert provider.call_count == 1
    
    def test_generate_user_stories_failure(self):
        """Test generate_user_stories method returns failure response."""
        provider = MockFailingAIProvider()
        
        result = provider.generate_user_stories("Test requirements")
        
        assert isinstance(result, AIResponse)
        assert result.content == ""
        assert result.service_used == "mock_failing"
        assert result.processing_time == 0.1
        assert result.success is False
        assert result.error_message == "Mock AI service failure"
        assert provider.call_count == 1
    
    def test_analyze_backlog_items_failure(self):
        """Test analyze_backlog_items method returns failure response."""
        provider = MockFailingAIProvider()
        
        result = provider.analyze_backlog_items([{"title": "test"}])
        
        assert isinstance(result, AIResponse)
        assert result.content == ""
        assert result.service_used == "mock_failing"
        assert result.processing_time == 0.1
        assert result.success is False
        assert result.error_message == "Mock AI service failure"
        assert provider.call_count == 1
    
    def test_failing_provider_call_count(self):
        """Test call count tracking in failing provider."""
        provider = MockFailingAIProvider()
        
        assert provider.call_count == 0
        
        provider.assess_priority("test")
        assert provider.call_count == 1
        
        provider.generate_user_stories("test")
        assert provider.call_count == 2
        
        provider.analyze_backlog_items([])
        assert provider.call_count == 3


class TestMockProvidersIntegration:
    """Integration tests for mock providers."""
    
    def test_successful_and_failing_providers_comparison(self):
        """Test comparison between successful and failing providers."""
        success_provider = MockAIProvider()
        failing_provider = MockFailingAIProvider()
        
        # Test same method on both providers
        success_result = success_provider.assess_priority("test")
        failing_result = failing_provider.assess_priority("test")
        
        assert success_result.success is True
        assert failing_result.success is False
        
        assert success_result.content != ""
        assert failing_result.content == ""
        
        assert success_result.error_message is None
        assert failing_result.error_message is not None
    
    def test_console_provider_with_ai_provider_simulation(self):
        """Test console provider simulating interaction with AI provider."""
        console = MockConsoleProvider()
        ai_provider = MockAIProvider()
        
        # Simulate user interaction
        console.set_input_responses(["Create user login feature"])
        
        console.print("Welcome to the Backlog Assistant")
        user_input = console.input("Enter a feature description: ")
        
        # Process with AI provider
        result = ai_provider.generate_user_stories(user_input)
        
        console.print("Generated stories:", result.content[:50] + "...")
        
        # Verify interaction
        assert len(console.printed_messages) == 2
        assert "Welcome" in console.printed_messages[0]
        assert "Generated stories" in console.printed_messages[1]
        assert user_input == "Create user login feature"
        assert result.success is True
    
    def test_all_mock_providers_instantiable(self):
        """Test that all mock provider classes can be instantiated."""
        ai_provider = MockAIProvider()
        console_provider = MockConsoleProvider()
        failing_provider = MockFailingAIProvider()
        
        assert ai_provider is not None
        assert console_provider is not None
        assert failing_provider is not None
        
        # Test they have expected attributes
        assert hasattr(ai_provider, 'call_count')
        assert hasattr(console_provider, 'printed_messages')
        assert hasattr(failing_provider, 'failure_rate')
    
    def test_mock_ai_response_compatibility(self):
        """Test MockAIResponse compatibility with AIResponse."""
        mock_response = MockAIResponse(content="test")
        
        # Should have same attributes as AIResponse
        assert hasattr(mock_response, 'content')
        assert hasattr(mock_response, 'service_used')
        assert hasattr(mock_response, 'processing_time')
        assert hasattr(mock_response, 'success')
        assert hasattr(mock_response, 'error_message')
