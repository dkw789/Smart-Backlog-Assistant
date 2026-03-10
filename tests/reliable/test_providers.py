"""Tests for provider modules - demonstrating simplified testing approach."""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestOpenAIProvider:
    """Test OpenAI provider with easy mocking."""
    
    def test_mock_ai_provider(self):
        """Test mock AI provider - no external dependencies."""
        from providers.openai_provider import MockAIProvider
        
        # Create provider with custom responses
        responses = {
            "completion": "Custom mock response",
            "structured": {"priority": "high", "confidence": 0.9}
        }
        provider = MockAIProvider(responses)
        
        # Test availability
        assert provider.is_available() == True
        
        # Test configuration
        config = provider.get_config()
        assert config["provider"] == "mock"
        assert config["available"] == True
        
        # Test completion
        result = provider.generate_completion("Test prompt")
        assert result == "Custom mock response"
        
        # Test structured response
        structured = provider.generate_structured_response("Analyze this")
        assert structured["priority"] == "high"
        assert structured["confidence"] == 0.9
        
        # Verify call counting
        assert provider.call_count == 2
    
    @patch('providers.openai_provider.openai')
    def test_openai_provider_with_mock(self, mock_openai):
        """Test real OpenAI provider with mocked openai library."""
        from providers.openai_provider import OpenAIProvider
        
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Mocked OpenAI response"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client
        
        # Create provider
        provider = OpenAIProvider(api_key="test-key")
        
        # Test completion
        result = provider.generate_completion("Test prompt")
        assert result == "Mocked OpenAI response"
        
        # Verify OpenAI was called correctly
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "gpt-3.5-turbo"
        assert call_args[1]["messages"][0]["content"] == "Test prompt"
    
    def test_openai_provider_without_api_key(self):
        """Test OpenAI provider behavior without API key."""
        from providers.openai_provider import OpenAIProvider
        
        provider = OpenAIProvider()  # No API key
        
        # Should not be available
        assert provider.is_available() == False
        
        # Should raise error when trying to use
        with pytest.raises(RuntimeError, match="OpenAI provider is not available"):
            provider.generate_completion("Test")


class TestRichProvider:
    """Test Rich UI provider with easy mocking."""
    
    def test_mock_ui_provider(self):
        """Test mock UI provider - no external dependencies."""
        from providers.rich_provider import MockUIProvider, MockProgressTracker
        
        provider = MockUIProvider()
        
        # Test availability
        assert provider.is_available() == True
        
        # Test print message
        provider.print_message("Test message", style="red")
        assert len(provider.messages) == 1
        assert provider.messages[0]["message"] == "Test message"
        assert provider.messages[0]["style"] == "red"
        
        # Test table formatting
        data = [["Name", "Age"], ["John", "30"]]
        table = provider.format_table(data, title="People")
        assert "Mock table: People" in table
        assert len(provider.tables) == 1
        
        # Test progress tracker
        tracker = provider.create_progress_tracker()
        assert isinstance(tracker, MockProgressTracker)
        
        tracker.start()
        task_id = tracker.add_task("Test task", total=100)
        tracker.update(task_id, advance=50)
        tracker.complete(task_id)
        
        assert tracker.started == True
        assert task_id in tracker.tasks
        assert tracker.tasks[task_id]["completed"] == 100
    
    @patch('providers.rich_provider.Console')
    def test_rich_provider_with_mock(self, mock_console_class):
        """Test real Rich provider with mocked Rich library."""
        from providers.rich_provider import RichUIProvider
        
        # Setup mock console
        mock_console = Mock()
        mock_console_class.return_value = mock_console
        
        provider = RichUIProvider()
        
        # Test print message
        provider.print_message("Test message", style="blue")
        mock_console.print.assert_called_once_with("Test message", style="blue")
        
        # Test fallback when Rich fails
        mock_console.print.side_effect = Exception("Rich error")
        with patch('builtins.print') as mock_print:
            provider.print_message("Fallback message")
            mock_print.assert_called_once_with("Fallback message")


class TestPydanticProvider:
    """Test PydanticAI provider with easy mocking."""
    
    def test_mock_pydantic_provider(self):
        """Test mock PydanticAI provider - no external dependencies."""
        from providers.pydantic_provider import MockPydanticProvider
        
        provider = MockPydanticProvider()
        
        # Test availability
        assert provider.is_available() == True
        
        # Test agent creation
        agent = provider.create_agent("test_agent", "You are a helpful assistant")
        assert agent.name == "test_agent"
        assert agent.system_prompt == "You are a helpful assistant"
        
        # Test agent retrieval
        retrieved_agent = provider.get_agent("test_agent")
        assert retrieved_agent == agent
        
        # Test completion
        result = provider.generate_completion("Test prompt", agent_name="test_agent")
        assert "Mock completion" in result
        
        # Test structured response
        structured = provider.generate_structured_response("Analyze this")
        assert structured["analysis"] == "Mock analysis"
        assert structured["priority"] == "medium"
        
        # Test custom mock responses
        provider.set_mock_response("completion", "Custom response")
        result = provider.generate_completion("Test")
        assert result == "Custom response"


class TestProviderFactory:
    """Test provider factory for dependency injection."""
    
    def test_factory_with_mocks(self):
        """Test factory configured to use mocks."""
        from providers.provider_factory import ProviderFactory
        
        factory = ProviderFactory(use_mocks=True)
        
        # Get providers
        ai_provider = factory.get_ai_provider()
        ui_provider = factory.get_ui_provider()
        pydantic_provider = factory.get_pydantic_provider()
        
        # All should be mock providers
        assert ai_provider.__class__.__name__ == "MockAIProvider"
        assert ui_provider.__class__.__name__ == "MockUIProvider"
        assert pydantic_provider.__class__.__name__ == "MockPydanticProvider"
        
        # Test status
        status = factory.get_all_providers_status()
        assert status["ai"]["provider"] == "mock"
        assert status["ui"]["provider"] == "mock"
        assert status["pydantic"]["provider"] == "mock_pydantic_ai"
    
    def test_factory_convenience_functions(self):
        """Test convenience functions for getting providers."""
        from providers.provider_factory import configure_providers, get_ai_provider, get_ui_provider
        
        # Configure to use mocks
        configure_providers(use_mocks=True)
        
        # Get providers through convenience functions
        ai_provider = get_ai_provider()
        ui_provider = get_ui_provider()
        
        assert ai_provider.is_available() == True
        assert ui_provider.is_available() == True


class TestProviderIntegration:
    """Test how providers integrate with existing modules."""
    
    def test_ai_processor_with_provider_injection(self):
        """Demonstrate how AIProcessor would use provider injection."""
        from providers.openai_provider import MockAIProvider
        
        # Mock AIProcessor that accepts provider
        class TestAIProcessor:
            def __init__(self, ai_provider=None):
                self.ai_provider = ai_provider or MockAIProvider()
            
            def process(self, text):
                return self.ai_provider.generate_completion(f"Process: {text}")
            
            def analyze(self, text):
                return self.ai_provider.generate_structured_response(f"Analyze: {text}")
        
        # Test with mock provider
        mock_responses = {
            "completion": "Processed successfully",
            "structured": {"result": "analysis complete", "confidence": 0.95}
        }
        mock_provider = MockAIProvider(mock_responses)
        processor = TestAIProcessor(mock_provider)
        
        # Test processing
        result = processor.process("test input")
        assert result == "Processed successfully"
        
        # Test analysis
        analysis = processor.analyze("test data")
        assert analysis["result"] == "analysis complete"
        assert analysis["confidence"] == 0.95
    
    def test_rich_cli_with_provider_injection(self):
        """Demonstrate how RichCLI would use provider injection."""
        from providers.rich_provider import MockUIProvider
        
        # Mock RichCLI that accepts provider
        class TestRichCLI:
            def __init__(self, ui_provider=None):
                self.ui_provider = ui_provider or MockUIProvider()
            
            def display_results(self, data):
                self.ui_provider.print_message("Results:", style="bold")
                table = self.ui_provider.format_table(data, title="Analysis Results")
                return table
            
            def show_progress(self, tasks):
                tracker = self.ui_provider.create_progress_tracker()
                tracker.start()
                
                for task_name, total in tasks:
                    task_id = tracker.add_task(task_name, total=total)
                    tracker.update(task_id, completed=total)
                    tracker.complete(task_id)
                
                tracker.stop()
                return tracker
        
        # Test with mock provider
        mock_provider = MockUIProvider()
        cli = TestRichCLI(mock_provider)
        
        # Test display
        data = [["Name", "Score"], ["Test", "95"]]
        table = cli.display_results(data)
        
        assert len(mock_provider.messages) == 1
        assert mock_provider.messages[0]["message"] == "Results:"
        assert len(mock_provider.tables) == 1
        
        # Test progress
        tasks = [("Task 1", 100), ("Task 2", 50)]
        tracker = cli.show_progress(tasks)
        
        assert len(tracker.tasks) == 2
        assert tracker.tasks["mock_task_0"]["completed"] == 100
        assert tracker.tasks["mock_task_1"]["completed"] == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
