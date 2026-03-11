"""Comprehensive tests for Backlog Analyzer to improve code coverage."""

import pytest
from unittest.mock import MagicMock, patch
from typing import List, Dict, Any

from src.processors.backlog_analyzer import (
    BacklogAnalysis,
    AIProviderProtocol,
    BacklogAnalyzer
)


class TestBacklogAnalysis:
    """Test BacklogAnalysis dataclass."""
    
    def test_backlog_analysis_creation(self):
        """Test BacklogAnalysis creation with all fields."""
        analysis = BacklogAnalysis(
            total_items=10,
            items_by_priority={"high": 3, "medium": 5, "low": 2},
            items_by_status={"todo": 6, "in_progress": 3, "done": 1},
            missing_information=["acceptance_criteria", "effort_estimates"],
            recommendations=["Add more details", "Prioritize critical items"],
            health_score=0.75,
            analysis_success=True,
            error_message=None
        )
        
        assert analysis.total_items == 10
        assert analysis.items_by_priority["high"] == 3
        assert analysis.items_by_status["todo"] == 6
        assert len(analysis.missing_information) == 2
        assert len(analysis.recommendations) == 2
        assert analysis.health_score == 0.75
        assert analysis.analysis_success is True
        assert analysis.error_message is None
    
    def test_backlog_analysis_with_error(self):
        """Test BacklogAnalysis creation with error."""
        analysis = BacklogAnalysis(
            total_items=0,
            items_by_priority={},
            items_by_status={},
            missing_information=[],
            recommendations=[],
            health_score=0.0,
            analysis_success=False,
            error_message="Analysis failed"
        )
        
        assert analysis.analysis_success is False
        assert analysis.error_message == "Analysis failed"
        assert analysis.health_score == 0.0


class TestAIProviderProtocol:
    """Test AIProviderProtocol."""
    
    def test_ai_provider_protocol_interface(self):
        """Test that AIProviderProtocol defines the expected interface."""
        class MockAIProvider:
            def analyze_backlog_items(self, backlog_data: List[Dict[str, Any]]):
                return MagicMock(success=True, content="Mock analysis")
        
        provider = MockAIProvider()
        result = provider.analyze_backlog_items([{"title": "test"}])
        
        assert result.success is True
        assert result.content == "Mock analysis"


class TestBacklogAnalyzer:
    """Test BacklogAnalyzer class."""
    
    @patch('src.processors.backlog_analyzer.AIProcessor')
    def test_backlog_analyzer_init_default(self, mock_ai_processor):
        """Test BacklogAnalyzer initialization with default provider."""
        mock_processor = MagicMock()
        mock_ai_processor.return_value = mock_processor
        
        analyzer = BacklogAnalyzer()
        
        assert analyzer.ai_provider is not None
        assert hasattr(analyzer, 'logger')
        mock_ai_processor.assert_called_once()
    
    def test_backlog_analyzer_init_custom_provider(self):
        """Test BacklogAnalyzer initialization with custom provider."""
        mock_provider = MagicMock()
        
        analyzer = BacklogAnalyzer(ai_provider=mock_provider)
        
        assert analyzer.ai_provider is mock_provider
    
    def test_analyze_backlog_data_empty(self):
        """Test analysis with empty backlog data."""
        analyzer = BacklogAnalyzer()
        
        result = analyzer.analyze_backlog_data([])
        
        assert isinstance(result, BacklogAnalysis)
        assert result.total_items == 0
        assert result.analysis_success is False
        assert "Empty backlog" in result.error_message
        assert result.health_score == 0.0
    
    def test_analyze_backlog_data_success(self):
        """Test successful backlog analysis."""
        mock_provider = MagicMock()
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.content = """
        {
            "health_score": 0.8,
            "recommendations": [
                "Add acceptance criteria to 3 items",
                "Prioritize security-related items",
                "Break down large items"
            ],
            "missing_information": ["effort_estimates", "dependencies"],
            "insights": "Backlog is well-structured with clear priorities"
        }
        """
        mock_provider.analyze_backlog_items.return_value = mock_response
        
        analyzer = BacklogAnalyzer(ai_provider=mock_provider)
        backlog_data = [
            {"title": "User Login", "priority": "high", "status": "todo"},
            {"title": "Dashboard", "priority": "medium", "status": "in_progress"},
            {"title": "Bug Fix", "priority": "low", "status": "done"}
        ]
        
        result = analyzer.analyze_backlog_data(backlog_data)
        
        assert isinstance(result, BacklogAnalysis)
        assert result.analysis_success is True
        assert result.total_items == 3
        assert result.health_score == 0.8
        assert len(result.recommendations) == 3
        assert "Add acceptance criteria" in result.recommendations[0]
        assert len(result.missing_information) == 2
        assert "effort_estimates" in result.missing_information
    
    def test_analyze_backlog_data_ai_failure(self):
        """Test backlog analysis when AI fails."""
        mock_provider = MagicMock()
        mock_response = MagicMock()
        mock_response.success = False
        mock_response.error_message = "AI service unavailable"
        mock_provider.analyze_backlog_items.return_value = mock_response
        
        analyzer = BacklogAnalyzer(ai_provider=mock_provider)
        backlog_data = [
            {"title": "Test Item", "priority": "medium", "status": "todo"}
        ]
        
        result = analyzer.analyze_backlog_data(backlog_data)
        
        assert isinstance(result, BacklogAnalysis)
        assert result.analysis_success is True  # Should fallback to rule-based
        assert result.total_items == 1
        assert result.health_score > 0  # Rule-based should provide some score
        assert len(result.recommendations) > 0
    
    def test_analyze_backlog_data_exception(self):
        """Test backlog analysis when exception occurs."""
        mock_provider = MagicMock()
        mock_provider.analyze_backlog_items.side_effect = Exception("Network error")
        
        analyzer = BacklogAnalyzer(ai_provider=mock_provider)
        backlog_data = [
            {"title": "Test Item", "priority": "medium", "status": "todo"}
        ]
        
        result = analyzer.analyze_backlog_data(backlog_data)
        
        assert isinstance(result, BacklogAnalysis)
        assert result.analysis_success is True  # Should fallback to rule-based
        assert result.total_items == 1
    
    def test_calculate_basic_metrics(self):
        """Test basic metrics calculation."""
        analyzer = BacklogAnalyzer()
        
        backlog_data = [
            {"title": "Item 1", "priority": "high", "status": "todo"},
            {"title": "Item 2", "priority": "high", "status": "in_progress"},
            {"title": "Item 3", "priority": "medium", "status": "todo"},
            {"title": "Item 4", "priority": "low", "status": "done"}
        ]
        
        metrics = analyzer._calculate_basic_metrics(backlog_data)
        
        assert metrics["total_items"] == 4
        assert metrics["items_by_priority"]["high"] == 2
        assert metrics["items_by_priority"]["medium"] == 1
        assert metrics["items_by_priority"]["low"] == 1
        assert metrics["items_by_status"]["todo"] == 2
        assert metrics["items_by_status"]["in_progress"] == 1
        assert metrics["items_by_status"]["done"] == 1
    
    def test_parse_ai_analysis_response(self):
        """Test AI response parsing."""
        analyzer = BacklogAnalyzer()
        
        ai_content = """
        {
            "health_score": 0.75,
            "recommendations": [
                "Add acceptance criteria to incomplete items",
                "Balance priority distribution",
                "Improve item descriptions"
            ],
            "missing_information": ["effort_estimates", "dependencies", "acceptance_criteria"],
            "insights": "Good overall structure but needs more detail"
        }
        """
        
        parsed = analyzer._parse_ai_analysis_response(ai_content)
        
        assert parsed["health_score"] == 0.75
        assert len(parsed["recommendations"]) == 3
        assert "Add acceptance criteria" in parsed["recommendations"][0]
        assert len(parsed["missing_information"]) == 3
        assert "effort_estimates" in parsed["missing_information"]
        assert parsed["insights"] == "Good overall structure but needs more detail"
    
    def test_parse_ai_analysis_response_invalid_json(self):
        """Test AI response parsing with invalid JSON."""
        analyzer = BacklogAnalyzer()
        
        invalid_content = "This is not valid JSON content"
        
        parsed = analyzer._parse_ai_analysis_response(invalid_content)
        
        # Should return default structure
        assert "health_score" in parsed
        assert "recommendations" in parsed
        assert "missing_information" in parsed
        assert isinstance(parsed["recommendations"], list)
    
    def test_rule_based_analysis(self):
        """Test rule-based analysis fallback."""
        analyzer = BacklogAnalyzer()
        
        backlog_data = [
            {"title": "User Authentication", "priority": "high", "status": "todo", "description": "Implement OAuth2"},
            {"title": "Bug Fix", "priority": "medium", "status": "in_progress"},
            {"title": "UI Enhancement", "priority": "low", "status": "done", "acceptance_criteria": ["Criterion 1"]}
        ]
        
        analysis = analyzer._rule_based_analysis(backlog_data)
        
        assert isinstance(analysis, BacklogAnalysis)
        assert analysis.analysis_success is True
        assert analysis.total_items == 3
        assert analysis.health_score > 0
        assert len(analysis.recommendations) > 0
        assert len(analysis.missing_information) > 0
    
    def test_calculate_health_score(self):
        """Test health score calculation."""
        analyzer = BacklogAnalyzer()
        
        # High quality backlog
        high_quality_data = [
            {
                "title": "Complete Feature",
                "description": "Detailed description",
                "priority": "high",
                "status": "todo",
                "acceptance_criteria": ["Criterion 1", "Criterion 2"],
                "effort_estimate": "5 points"
            }
        ]
        
        high_score = analyzer._calculate_health_score(high_quality_data)
        assert high_score > 0.7
        
        # Low quality backlog
        low_quality_data = [
            {"title": "Item", "status": "todo"}  # Missing many fields
        ]
        
        low_score = analyzer._calculate_health_score(low_quality_data)
        assert low_score < 0.5
    
    def test_identify_missing_information(self):
        """Test missing information identification."""
        analyzer = BacklogAnalyzer()
        
        incomplete_data = [
            {"title": "Item 1", "status": "todo"},  # Missing priority, description, etc.
            {"title": "Item 2", "priority": "high"},  # Missing status, description, etc.
            {"title": "Item 3", "priority": "medium", "status": "todo", "description": "Complete"}  # Missing acceptance_criteria, effort_estimate
        ]
        
        missing_info = analyzer._identify_missing_information(incomplete_data)
        
        assert isinstance(missing_info, list)
        assert "priority" in missing_info
        assert "description" in missing_info
        assert "acceptance_criteria" in missing_info
        assert "effort_estimate" in missing_info
    
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        analyzer = BacklogAnalyzer()
        
        backlog_data = [
            {"title": "Security Fix", "priority": "low", "status": "todo"},  # Security should be high priority
            {"title": "Large Feature", "description": "Very complex feature with many components", "status": "todo"},  # Should be broken down
            {"title": "Item", "status": "todo"}  # Missing information
        ]
        
        recommendations = analyzer._generate_recommendations(backlog_data)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        # Should contain various types of recommendations
        rec_text = " ".join(recommendations).lower()
        assert any(keyword in rec_text for keyword in ["priority", "information", "detail"])
    
    def test_format_backlog_for_ai(self):
        """Test backlog formatting for AI analysis."""
        analyzer = BacklogAnalyzer()
        
        backlog_data = [
            {"title": "User Login", "priority": "high", "status": "todo", "description": "OAuth2 implementation"},
            {"title": "Dashboard", "priority": "medium", "status": "in_progress"}
        ]
        
        formatted = analyzer._format_backlog_for_ai(backlog_data)
        
        assert isinstance(formatted, str)
        assert "User Login" in formatted
        assert "OAuth2 implementation" in formatted
        assert "Dashboard" in formatted
        assert "high" in formatted
        assert "medium" in formatted
    
    def test_validate_backlog_item(self):
        """Test backlog item validation."""
        analyzer = BacklogAnalyzer()
        
        # Complete item
        complete_item = {
            "title": "Complete Feature",
            "description": "Detailed description",
            "priority": "high",
            "status": "todo",
            "acceptance_criteria": ["Criterion 1"],
            "effort_estimate": "3 points"
        }
        
        complete_score = analyzer._validate_backlog_item(complete_item)
        assert complete_score > 0.8
        
        # Incomplete item
        incomplete_item = {"title": "Incomplete"}
        
        incomplete_score = analyzer._validate_backlog_item(incomplete_item)
        assert incomplete_score < 0.5
    
    def test_is_security_related(self):
        """Test security-related item detection."""
        analyzer = BacklogAnalyzer()
        
        security_item = {
            "title": "Authentication Fix",
            "description": "Fix security vulnerability in login"
        }
        
        assert analyzer._is_security_related(security_item) is True
        
        normal_item = {
            "title": "UI Update",
            "description": "Change button color"
        }
        
        assert analyzer._is_security_related(normal_item) is False
    
    def test_needs_breakdown(self):
        """Test item breakdown detection."""
        analyzer = BacklogAnalyzer()
        
        large_item = {
            "title": "Complete System Overhaul",
            "description": "Redesign entire application architecture, update all components, migrate database, implement new features, and update documentation"
        }
        
        assert analyzer._needs_breakdown(large_item) is True
        
        small_item = {
            "title": "Fix Button",
            "description": "Change button color to blue"
        }
        
        assert analyzer._needs_breakdown(small_item) is False
    
    def test_has_sufficient_detail(self):
        """Test detail sufficiency check."""
        analyzer = BacklogAnalyzer()
        
        detailed_item = {
            "title": "User Registration",
            "description": "Implement user registration with email verification",
            "acceptance_criteria": ["User can enter email", "Verification email sent"],
            "effort_estimate": "5 points"
        }
        
        assert analyzer._has_sufficient_detail(detailed_item) is True
        
        minimal_item = {"title": "Fix bug"}
        
        assert analyzer._has_sufficient_detail(minimal_item) is False


class TestBacklogAnalyzerIntegration:
    """Integration tests for BacklogAnalyzer."""
    
    def test_end_to_end_analysis(self):
        """Test complete analysis workflow."""
        mock_provider = MagicMock()
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.content = """
        {
            "health_score": 0.85,
            "recommendations": [
                "Excellent backlog structure",
                "Consider adding more acceptance criteria",
                "Balance priority distribution"
            ],
            "missing_information": ["effort_estimates"],
            "insights": "Well-maintained backlog with clear priorities"
        }
        """
        mock_provider.analyze_backlog_items.return_value = mock_response
        
        analyzer = BacklogAnalyzer(ai_provider=mock_provider)
        
        backlog_data = [
            {
                "title": "User Authentication",
                "description": "Implement OAuth2 authentication system",
                "priority": "high",
                "status": "todo",
                "acceptance_criteria": ["OAuth2 integration", "Security validation"]
            },
            {
                "title": "Dashboard Analytics",
                "description": "Create analytics dashboard for users",
                "priority": "medium",
                "status": "in_progress",
                "effort_estimate": "8 points"
            },
            {
                "title": "Bug Fix - Login",
                "description": "Fix login redirect issue",
                "priority": "high",
                "status": "done"
            }
        ]
        
        result = analyzer.analyze_backlog_data(backlog_data)
        
        # Verify complete analysis structure
        assert result.analysis_success is True
        assert result.total_items == 3
        assert result.health_score == 0.85
        assert len(result.recommendations) == 3
        assert "Excellent backlog structure" in result.recommendations[0]
        assert len(result.missing_information) == 1
        assert "effort_estimates" in result.missing_information
        assert result.items_by_priority["high"] == 2
        assert result.items_by_priority["medium"] == 1
        assert result.items_by_status["todo"] == 1
        assert result.items_by_status["in_progress"] == 1
        assert result.items_by_status["done"] == 1
    
    def test_fallback_analysis_workflow(self):
        """Test analysis workflow with AI failure and rule-based fallback."""
        mock_provider = MagicMock()
        mock_provider.analyze_backlog_items.side_effect = Exception("AI service down")
        
        analyzer = BacklogAnalyzer(ai_provider=mock_provider)
        
        backlog_data = [
            {"title": "Security Update", "priority": "low", "status": "todo"},  # Should trigger security recommendation
            {"title": "Feature", "status": "todo"},  # Missing information
            {"title": "Complete Item", "description": "Detailed", "priority": "high", "status": "done", "acceptance_criteria": ["Done"]}
        ]
        
        result = analyzer.analyze_backlog_data(backlog_data)
        
        # Should successfully complete with rule-based analysis
        assert result.analysis_success is True
        assert result.total_items == 3
        assert result.health_score > 0
        assert len(result.recommendations) > 0
        assert len(result.missing_information) > 0
        
        # Should identify security priority issue
        rec_text = " ".join(result.recommendations).lower()
        assert "security" in rec_text or "priority" in rec_text
    
    def test_various_backlog_scenarios(self):
        """Test analyzer with various backlog scenarios."""
        analyzer = BacklogAnalyzer()
        
        scenarios = [
            # Empty backlog
            [],
            # Single item
            [{"title": "Single Item", "priority": "medium", "status": "todo"}],
            # Well-structured backlog
            [
                {"title": "Item 1", "description": "Detailed", "priority": "high", "status": "todo", "acceptance_criteria": ["AC1"]},
                {"title": "Item 2", "description": "Detailed", "priority": "medium", "status": "in_progress", "effort_estimate": "3"}
            ],
            # Poorly structured backlog
            [
                {"title": "Item"},
                {"status": "todo"},
                {"priority": "high"}
            ]
        ]
        
        for i, scenario in enumerate(scenarios):
            result = analyzer.analyze_backlog_data(scenario)
            
            assert isinstance(result, BacklogAnalysis)
            assert result.total_items == len(scenario)
            
            if len(scenario) == 0:
                assert result.analysis_success is False
                assert "Empty backlog" in result.error_message
            else:
                # Non-empty scenarios should have some analysis
                assert isinstance(result.items_by_priority, dict)
                assert isinstance(result.items_by_status, dict)
                assert isinstance(result.recommendations, list)
                assert isinstance(result.missing_information, list)
                assert 0 <= result.health_score <= 1
