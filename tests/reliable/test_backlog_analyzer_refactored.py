"""Tests for refactored backlog analyzer - demonstrating simplified testing with providers."""

import pytest
import sys
import os
import json

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestBacklogAnalyzerRefactored:
    """Test refactored backlog analyzer with easy dependency injection."""
    
    def test_analyzer_with_mock_provider(self):
        """Test analyzer with mock provider - no external dependencies."""
        from processors.backlog_analyzer_refactored import BacklogAnalyzerRefactored
        from providers.openai_provider import MockAIProvider
        
        # Create mock provider with custom responses
        mock_responses = {
            "structured": {
                "priority_suggestion": "high",
                "effort_estimate": 8,
                "risk_level": "medium",
                "dependencies": ["authentication", "database"],
                "acceptance_criteria": ["User can login", "Session persists"]
            }
        }
        mock_provider = MockAIProvider(mock_responses)
        
        # Create analyzer with injected mock
        analyzer = BacklogAnalyzerRefactored(ai_provider=mock_provider)
        
        # Test availability
        assert analyzer.is_available() == True
        
        # Test basic analysis
        backlog_data = [
            {"id": "1", "title": "User login", "priority": "high", "status": "todo"},
            {"id": "2", "title": "Data export", "priority": "medium", "status": "in_progress"},
            {"id": "3", "title": "Bug fix", "priority": "high", "status": "done"}
        ]
        
        result = analyzer.analyze_backlog_data(backlog_data)
        assert result.analysis_success == True
        assert result.total_items == 3
        assert result.health_score > 0
        assert result.items_by_priority['high'] == 2
        assert result.items_by_status['todo'] == 1
        assert result.items_by_status['in_progress'] == 1
        assert result.items_by_status['done'] == 1
        assert len(result.recommendations) >= 0
    
    def test_empty_backlog_analysis(self):
        """Test analyzer with empty backlog."""
        from processors.backlog_analyzer_refactored import BacklogAnalyzerRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_provider = MockAIProvider()
        analyzer = BacklogAnalyzerRefactored(ai_provider=mock_provider)
        
        # Test empty list
        result = analyzer.analyze_backlog_data([])
        assert result.analysis_success == False
        assert result.total_items == 0
        assert result.health_score == 0.0
        
        # Test None input
        result = analyzer.analyze_backlog_data(None)
        assert result.analysis_success == False
        assert result.total_items == 0
    
    def test_invalid_backlog_items(self):
        """Test analyzer with invalid backlog items."""
        from processors.backlog_analyzer_refactored import BacklogAnalyzerRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_provider = MockAIProvider()
        analyzer = BacklogAnalyzerRefactored(ai_provider=mock_provider)
        
        # Test with invalid items (no id or title)
        invalid_data = [
            {"description": "No ID or title"},
            {},
            "not a dict",
            None
        ]
        
        result = analyzer.analyze_backlog_data(invalid_data)
        assert result.analysis_success == False
        assert result.total_items == len(invalid_data)
        assert result.health_score == 0.0
    
    def test_health_score_calculation(self):
        """Test health score calculation with different scenarios."""
        from processors.backlog_analyzer_refactored import BacklogAnalyzerRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_provider = MockAIProvider()
        analyzer = BacklogAnalyzerRefactored(ai_provider=mock_provider)
        
        # High health score scenario (many completed items)
        high_health_data = [
            {"id": f"{i}", "title": f"Task {i}", "status": "done"} for i in range(8)
        ] + [
            {"id": "9", "title": "Task 9", "status": "in_progress"},
            {"id": "10", "title": "Task 10", "status": "todo"}
        ]
        
        result = analyzer.analyze_backlog_data(high_health_data)
        assert result.analysis_success == True
        assert result.health_score > 70  # Should be high due to many completed items
        
        # Low health score scenario (many blocked items)
        low_health_data = [
            {"id": f"{i}", "title": f"Task {i}", "status": "blocked"} for i in range(7)
        ] + [
            {"id": "8", "title": "Task 8", "status": "todo"},
            {"id": "9", "title": "Task 9", "status": "todo"},
            {"id": "10", "title": "Task 10", "status": "todo"}
        ]
        
        result = analyzer.analyze_backlog_data(low_health_data)
        assert result.analysis_success == True
        assert result.health_score < 50  # Should be low due to many blocked items
    
    def test_json_extraction(self):
        """Test JSON backlog extraction."""
        from processors.backlog_analyzer_refactored import BacklogAnalyzerRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_provider = MockAIProvider()
        analyzer = BacklogAnalyzerRefactored(ai_provider=mock_provider)
        
        # Test list format
        list_json = json.dumps([
            {"id": "1", "title": "Task 1"},
            {"id": "2", "title": "Task 2"}
        ])
        result = analyzer.extract_backlog_from_json(list_json)
        assert len(result) == 2
        assert result[0]["id"] == "1"
        
        # Test object with items key
        object_json = json.dumps({
            "items": [
                {"id": "1", "title": "Task 1"},
                {"id": "2", "title": "Task 2"}
            ],
            "metadata": {"version": "1.0"}
        })
        result = analyzer.extract_backlog_from_json(object_json)
        assert len(result) == 2
        
        # Test single object
        single_json = json.dumps({"id": "1", "title": "Single Task"})
        result = analyzer.extract_backlog_from_json(single_json)
        assert len(result) == 1
        assert result[0]["id"] == "1"
        
        # Test invalid JSON
        result = analyzer.extract_backlog_from_json("invalid json")
        assert result == []
    
    def test_item_enhancement(self):
        """Test backlog item enhancement with AI."""
        from processors.backlog_analyzer_refactored import BacklogAnalyzerRefactored
        from providers.openai_provider import MockAIProvider
        
        # Mock provider with enhancement responses
        mock_responses = {
            "structured": {
                "priority_suggestion": "high",
                "effort_estimate": 5,
                "risk_level": "low",
                "dependencies": ["user_service"],
                "acceptance_criteria": ["User can register", "Email validation works"]
            }
        }
        mock_provider = MockAIProvider(mock_responses)
        analyzer = BacklogAnalyzerRefactored(ai_provider=mock_provider)
        
        # Test enhancement
        items = [
            {"id": "1", "title": "User registration", "description": "Allow users to create accounts"}
        ]
        
        enhanced = analyzer.enhance_backlog_items(items)
        assert len(enhanced) == 1
        assert enhanced[0]["ai_priority_suggestion"] == "high"
        assert enhanced[0]["ai_effort_estimate"] == 5
        assert enhanced[0]["ai_risk_level"] == "low"
        assert "user_service" in enhanced[0]["ai_dependencies"]
        assert len(enhanced[0]["ai_acceptance_criteria"]) == 2
        
        # Original fields should be preserved
        assert enhanced[0]["id"] == "1"
        assert enhanced[0]["title"] == "User registration"
    
    def test_enhancement_without_ai(self):
        """Test item enhancement when AI is not available."""
        from processors.backlog_analyzer_refactored import BacklogAnalyzerRefactored
        from providers.openai_provider import MockAIProvider
        
        # Create unavailable mock provider
        class UnavailableMockProvider(MockAIProvider):
            def is_available(self):
                return False
        
        unavailable_provider = UnavailableMockProvider()
        analyzer = BacklogAnalyzerRefactored(ai_provider=unavailable_provider)
        
        items = [{"id": "1", "title": "Test item"}]
        enhanced = analyzer.enhance_backlog_items(items)
        
        # Should return original items unchanged
        assert len(enhanced) == 1
        assert enhanced[0] == items[0]
        assert "ai_priority_suggestion" not in enhanced[0]
    
    def test_comprehensive_analysis(self):
        """Test comprehensive backlog analysis with various scenarios."""
        from processors.backlog_analyzer_refactored import BacklogAnalyzerRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_provider = MockAIProvider()
        analyzer = BacklogAnalyzerRefactored(ai_provider=mock_provider)
        
        # Comprehensive test data
        comprehensive_data = [
            {"id": "1", "title": "High priority task", "priority": "high", "status": "todo"},
            {"id": "2", "title": "Medium priority task", "priority": "medium", "status": "in_progress"},
            {"id": "3", "title": "Low priority task", "priority": "low", "status": "done"},
            {"id": "4", "title": "Blocked task", "priority": "high", "status": "blocked"},
            {"id": "5", "title": "Unknown priority", "status": "todo"},
            {"id": "6", "title": "Completed feature", "priority": "medium", "status": "done"},
            {"id": "7", "title": "Bug fix", "priority": "high", "status": "done"},
            {"id": "8", "title": "Enhancement", "priority": "low", "status": "in_progress"},
        ]
        
        result = analyzer.analyze_backlog_data(comprehensive_data)
        
        # Verify comprehensive analysis
        assert result.analysis_success == True
        assert result.total_items == 8
        assert result.health_score > 0
        
        # Check priority distribution
        assert result.items_by_priority['high'] == 3
        assert result.items_by_priority['medium'] == 2
        assert result.items_by_priority['low'] == 2
        assert result.items_by_priority['unknown'] == 1
        
        # Check status distribution
        assert result.items_by_status['todo'] == 2
        assert result.items_by_status['in_progress'] == 2
        assert result.items_by_status['done'] == 3
        assert result.items_by_status['blocked'] == 1
        
        # Should have recommendations due to blocked items
        assert len(result.recommendations) > 0
        assert any("blocked" in rec.lower() for rec in result.recommendations)
        
        # Should have risk factors
        assert len(result.risk_factors) > 0
        
        # Should have trends analysis
        assert 'velocity_estimate' in result.trends
        assert 'bottlenecks' in result.trends
        assert 'priority_distribution' in result.trends
        
        # Should have completion estimate
        assert result.completion_estimate in ['1-2 weeks', '1-2 months', '2-6 months', '6+ months', 'completed']
    
    def test_status_normalization(self):
        """Test status value normalization."""
        from processors.backlog_analyzer_refactored import BacklogAnalyzerRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_provider = MockAIProvider()
        analyzer = BacklogAnalyzerRefactored(ai_provider=mock_provider)
        
        # Test various status formats
        status_variants = [
            {"id": "1", "title": "Task 1", "status": "new"},
            {"id": "2", "title": "Task 2", "status": "open"},
            {"id": "3", "title": "Task 3", "status": "in-progress"},
            {"id": "4", "title": "Task 4", "status": "active"},
            {"id": "5", "title": "Task 5", "status": "completed"},
            {"id": "6", "title": "Task 6", "status": "closed"},
            {"id": "7", "title": "Task 7", "status": "on_hold"},
            {"id": "8", "title": "Task 8", "status": "waiting"},
        ]
        
        result = analyzer.analyze_backlog_data(status_variants)
        
        # Verify normalization
        assert result.items_by_status['todo'] == 2  # new, open
        assert result.items_by_status['in_progress'] == 2  # in-progress, active
        assert result.items_by_status['done'] == 2  # completed, closed
        assert result.items_by_status['blocked'] == 2  # on_hold, waiting
    
    def test_error_handling(self):
        """Test error handling in analysis."""
        from processors.backlog_analyzer_refactored import BacklogAnalyzerRefactored
        from providers.openai_provider import MockAIProvider
        
        # Create failing mock provider for enhancement
        class FailingMockProvider(MockAIProvider):
            def generate_structured_response(self, prompt, schema=None):
                raise Exception("Mock AI failure")
        
        failing_provider = FailingMockProvider()
        analyzer = BacklogAnalyzerRefactored(ai_provider=failing_provider)
        
        # Test that analysis still works even if AI enhancement fails
        items = [{"id": "1", "title": "Test item"}]
        enhanced = analyzer.enhance_backlog_items(items)
        
        # Should return original items when enhancement fails
        assert len(enhanced) == 1
        assert enhanced[0] == items[0]
    
    def test_provider_status(self):
        """Test provider status functionality."""
        from processors.backlog_analyzer_refactored import BacklogAnalyzerRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_provider = MockAIProvider()
        analyzer = BacklogAnalyzerRefactored(ai_provider=mock_provider)
        
        # Test status
        status = analyzer.get_provider_status()
        assert "provider_config" in status
        assert status["is_available"] == True
        assert status["analyzer_ready"] == True
        assert status["provider_config"]["provider"] == "mock"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
