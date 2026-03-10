"""Tests for refactored AI processor - demonstrating simplified testing with providers."""

import pytest
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestAIProcessorRefactored:
    """Test refactored AI processor with easy dependency injection."""
    
    def test_processor_with_mock_provider(self):
        """Test processor with mock provider - no external dependencies."""
        from processors.ai_processor_refactored import AIProcessorRefactored
        from providers.openai_provider import MockAIProvider
        
        # Create mock provider with custom responses
        mock_responses = {
            "completion": "Processed text successfully",
            "structured": {
                "requirements": ["Login system", "User management"],
                "priority": "high",
                "complexity": "medium"
            }
        }
        mock_provider = MockAIProvider(mock_responses)
        
        # Create processor with injected mock
        processor = AIProcessorRefactored(ai_provider=mock_provider)
        
        # Test availability
        assert processor.is_available() == True
        
        # Test basic processing
        result = processor.process("Test input text")
        assert result["success"] == True
        assert result["result"] == "Processed text successfully"
        assert result["provider"] == "mock"
        assert result["input_length"] == 15
        
        # Test requirements analysis
        analysis = processor.analyze_requirements("Need user login and data export")
        assert analysis["success"] == True
        assert len(analysis["requirements"]) == 2
        assert "Login system" in analysis["requirements"]
        assert analysis["priority"] == "high"
        assert analysis["complexity"] == "medium"
        assert analysis["total_requirements"] == 2
        
        # Verify provider was called
        assert mock_provider.call_count == 2
    
    def test_processor_error_handling(self):
        """Test processor error handling with mock provider."""
        from processors.ai_processor_refactored import AIProcessorRefactored
        from providers.openai_provider import MockAIProvider
        
        # Create failing mock provider
        class FailingMockProvider(MockAIProvider):
            def generate_completion(self, prompt, **kwargs):
                raise Exception("Mock API failure")
            
            def generate_structured_response(self, prompt, schema=None):
                raise Exception("Mock structured API failure")
        
        failing_provider = FailingMockProvider()
        processor = AIProcessorRefactored(ai_provider=failing_provider)
        
        # Test error handling in process
        result = processor.process("Test input")
        assert result["success"] == False
        assert "Mock API failure" in result["error"]
        assert result["input_length"] == 10
        
        # Test error handling in analyze_requirements
        analysis = processor.analyze_requirements("Test requirements")
        assert analysis["success"] == False
        assert "Mock structured API failure" in analysis["error"]
        assert analysis["requirements"] == []
    
    def test_processor_edge_cases(self):
        """Test processor with edge cases."""
        from processors.ai_processor_refactored import AIProcessorRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_provider = MockAIProvider()
        processor = AIProcessorRefactored(ai_provider=mock_provider)
        
        # Test empty input
        result = processor.process("")
        assert result["success"] == False
        assert "Empty input text" in result["error"]
        
        # Test whitespace-only input
        result = processor.process("   ")
        assert result["success"] == False
        assert "Empty input text" in result["error"]
        
        # Test None input
        result = processor.process(None)
        assert result["success"] == False
        assert "Empty input text" in result["error"]
        
        # Test empty requirements analysis
        analysis = processor.analyze_requirements("")
        assert analysis["success"] == False
        assert "Empty input" in analysis["error"]
        assert analysis["requirements"] == []
    
    def test_entity_extraction(self):
        """Test entity extraction functionality."""
        from processors.ai_processor_refactored import AIProcessorRefactored
        from providers.openai_provider import MockAIProvider
        
        # Mock provider with entity response
        mock_responses = {
            "structured": {
                "entities": ["John Doe", "New York", "2024-01-01"],
                "categories": {
                    "people": ["John Doe"],
                    "locations": ["New York"],
                    "dates": ["2024-01-01"]
                }
            }
        }
        mock_provider = MockAIProvider(mock_responses)
        processor = AIProcessorRefactored(ai_provider=mock_provider)
        
        # Test entity extraction
        result = processor.extract_entities("John Doe visited New York on 2024-01-01")
        assert result["success"] == True
        assert len(result["entities"]) == 3
        assert "John Doe" in result["entities"]
        assert "New York" in result["entities"]
        assert result["total_entities"] == 3
        assert "people" in result["categories"]
        assert result["provider"] == "mock"
    
    def test_summarization(self):
        """Test text summarization functionality."""
        from processors.ai_processor_refactored import AIProcessorRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_responses = {
            "completion": "This is a concise summary of the input text."
        }
        mock_provider = MockAIProvider(mock_responses)
        processor = AIProcessorRefactored(ai_provider=mock_provider)
        
        # Test summarization
        long_text = "This is a very long text that needs to be summarized. " * 10
        result = processor.summarize(long_text, max_length=100)
        
        assert result["success"] == True
        assert result["summary"] == "This is a concise summary of the input text."
        assert result["original_length"] == len(long_text)
        assert result["summary_length"] == len("This is a concise summary of the input text.")
        assert result["compression_ratio"] > 0
        assert result["provider"] == "mock"
        
        # Test empty summarization
        empty_result = processor.summarize("")
        assert empty_result["success"] == False
        assert "Empty input" in empty_result["error"]
        assert empty_result["summary"] == ""
    
    def test_content_classification(self):
        """Test content classification functionality."""
        from processors.ai_processor_refactored import AIProcessorRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_responses = {
            "structured": {
                "category": "feature_request",
                "confidence": 0.85,
                "secondary_categories": ["requirement"]
            }
        }
        mock_provider = MockAIProvider(mock_responses)
        processor = AIProcessorRefactored(ai_provider=mock_provider)
        
        # Test classification with default categories
        result = processor.classify_content("I need a new login feature")
        assert result["success"] == True
        assert result["category"] == "feature_request"
        assert result["confidence"] == 0.85
        assert "requirement" in result["secondary_categories"]
        assert len(result["available_categories"]) == 5  # Default categories
        assert result["provider"] == "mock"
        
        # Test classification with custom categories
        custom_categories = ["urgent", "normal", "low"]
        result = processor.classify_content("This is urgent", categories=custom_categories)
        assert result["success"] == True
        assert result["available_categories"] == custom_categories
        
        # Test empty classification
        empty_result = processor.classify_content("")
        assert empty_result["success"] == False
        assert "Empty input" in empty_result["error"]
        assert empty_result["category"] == "unknown"
    
    def test_provider_status(self):
        """Test provider status functionality."""
        from processors.ai_processor_refactored import AIProcessorRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_provider = MockAIProvider()
        processor = AIProcessorRefactored(ai_provider=mock_provider)
        
        # Test status
        status = processor.get_provider_status()
        assert "provider_config" in status
        assert status["is_available"] == True
        assert status["processor_ready"] == True
        assert status["provider_config"]["provider"] == "mock"
    
    def test_processor_without_provider(self):
        """Test processor using default provider factory."""
        from processors.ai_processor_refactored import AIProcessorRefactored
        from providers.provider_factory import configure_providers
        
        # Configure factory to use mocks
        configure_providers(use_mocks=True)
        
        # Create processor without explicit provider (uses factory)
        processor = AIProcessorRefactored()
        
        # Should work with factory-provided mock
        assert processor.is_available() == True
        
        result = processor.process("Test with factory provider")
        assert result["success"] == True
        assert "Mock response" in result["result"]
    
    def test_comprehensive_workflow(self):
        """Test a comprehensive workflow using all processor methods."""
        from processors.ai_processor_refactored import AIProcessorRefactored
        from providers.openai_provider import MockAIProvider
        
        # Setup comprehensive mock responses
        mock_responses = {
            "completion": "Comprehensive analysis complete",
            "structured": {
                "requirements": ["User authentication", "Data validation", "Error handling"],
                "priority": "high",
                "complexity": "high",
                "entities": ["User", "Database", "API"],
                "categories": {"components": ["User", "Database", "API"]},
                "category": "requirement",
                "confidence": 0.9,
                "secondary_categories": ["feature_request"]
            }
        }
        mock_provider = MockAIProvider(mock_responses)
        processor = AIProcessorRefactored(ai_provider=mock_provider)
        
        test_text = "We need a user authentication system that validates data and handles errors properly."
        
        # Run comprehensive analysis
        process_result = processor.process(test_text)
        requirements = processor.analyze_requirements(test_text)
        entities = processor.extract_entities(test_text)
        summary = processor.summarize(test_text)
        classification = processor.classify_content(test_text)
        
        # Verify all operations succeeded
        assert process_result["success"] == True
        assert requirements["success"] == True
        assert entities["success"] == True
        assert summary["success"] == True
        assert classification["success"] == True
        
        # Verify comprehensive results
        assert len(requirements["requirements"]) == 3
        assert requirements["priority"] == "high"
        assert len(entities["entities"]) == 3
        assert classification["category"] == "requirement"
        assert classification["confidence"] == 0.9
        
        # Verify provider was called multiple times
        assert mock_provider.call_count == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
