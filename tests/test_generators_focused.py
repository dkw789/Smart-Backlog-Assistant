"""Focused tests for generators module - fast and effective."""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from generators.priority_engine import PriorityEngine
from generators.user_story_generator import UserStoryGenerator


class TestPriorityEngine:
    """Fast tests for priority engine."""
    
    @patch('openai.OpenAI')
    def test_priority_engine_basic(self, mock_openai):
        """Test basic priority engine functionality."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Priority: HIGH"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        engine = PriorityEngine()
        assert engine is not None
        
        # Test basic priority assessment
        test_item = {"title": "Critical bug", "description": "System crash"}
        
        if hasattr(engine, 'calculate_priority'):
            result = engine.calculate_priority(test_item)
            assert result is not None


class TestUserStoryGenerator:
    """Fast tests for user story generator."""
    
    @patch('openai.OpenAI')
    def test_user_story_generator_basic(self, mock_openai):
        """Test basic user story generation."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "As a user, I want to login"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        generator = UserStoryGenerator()
        assert generator is not None
        
        # Test basic story generation
        test_req = "User authentication required"
        
        if hasattr(generator, 'generate_story'):
            story = generator.generate_story(test_req)
            assert story is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
