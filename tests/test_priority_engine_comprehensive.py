"""Comprehensive tests for Priority Engine to improve code coverage."""

import pytest
from unittest.mock import MagicMock, patch
from src.generators.priority_engine import (
    Priority,
    Category,
    PriorityAssessment,
    AIProviderProtocol,
    PriorityEngine
)


class TestPriorityEngineEnums:
    """Test enum classes in priority engine."""
    
    def test_priority_enum_values(self):
        """Test Priority enum values and behavior."""
        assert Priority.CRITICAL.value == "critical"
        assert Priority.HIGH.value == "high"
        assert Priority.MEDIUM.value == "medium"
        assert Priority.LOW.value == "low"
        
        # Test enum iteration
        priorities = list(Priority)
        assert len(priorities) == 4
        assert Priority.CRITICAL in priorities
        
        # Test enum comparison
        assert Priority.HIGH == Priority.HIGH
        assert Priority.HIGH != Priority.LOW
        
        # Test enum ordering (if implemented)
        priority_values = [p.value for p in Priority]
        assert "critical" in priority_values
        assert "low" in priority_values
    
    def test_category_enum_values(self):
        """Test Category enum values and behavior."""
        assert Category.FEATURE.value == "feature"
        assert Category.BUG.value == "bug"
        assert Category.ENHANCEMENT.value == "enhancement"
        assert Category.TECHNICAL_DEBT.value == "technical_debt"
        assert Category.RESEARCH.value == "research"
        assert Category.MAINTENANCE.value == "maintenance"
        
        categories = list(Category)
        assert len(categories) == 6
        assert Category.FEATURE in categories


class TestPriorityAssessment:
    """Test PriorityAssessment dataclass."""
    
    def test_priority_assessment_creation(self):
        """Test PriorityAssessment creation with all fields."""
        assessment = PriorityAssessment(
            priority=Priority.HIGH,
            category=Category.FEATURE,
            business_impact="High impact on user experience",
            technical_complexity="Medium complexity",
            effort_estimate="3-5 days",
            dependencies=["auth-service", "database"],
            reasoning="Critical feature for Q2 release",
            confidence_score=0.85
        )
        
        assert assessment.priority == Priority.HIGH
        assert assessment.category == Category.FEATURE
        assert assessment.business_impact == "High impact on user experience"
        assert assessment.technical_complexity == "Medium complexity"
        assert assessment.effort_estimate == "3-5 days"
        assert assessment.dependencies == ["auth-service", "database"]
        assert assessment.reasoning == "Critical feature for Q2 release"
        assert assessment.confidence_score == 0.85
    
    def test_priority_assessment_minimal(self):
        """Test PriorityAssessment creation with minimal data."""
        assessment = PriorityAssessment(
            priority=Priority.MEDIUM,
            category=Category.BUG,
            business_impact="Low impact",
            technical_complexity="Low complexity",
            effort_estimate="1-2 hours",
            dependencies=[],
            reasoning="Minor UI bug",
            confidence_score=0.95
        )
        
        assert assessment.dependencies == []
        assert assessment.confidence_score == 0.95
    
    def test_priority_assessment_confidence_validation(self):
        """Test confidence score validation."""
        # Valid confidence scores
        for score in [0.0, 0.5, 0.8, 1.0]:
            assessment = PriorityAssessment(
                priority=Priority.LOW,
                category=Category.MAINTENANCE,
                business_impact="test",
                technical_complexity="test",
                effort_estimate="test",
                dependencies=[],
                reasoning="test",
                confidence_score=score
            )
            assert assessment.confidence_score == score


class TestAIProviderProtocol:
    """Test AIProviderProtocol."""
    
    def test_ai_provider_protocol_interface(self):
        """Test that AIProviderProtocol defines the expected interface."""
        # This is a Protocol, so we test it by creating a mock that implements it
        class MockAIProvider:
            def assess_priority(self, item_description: str):
                return PriorityAssessment(
                    priority=Priority.HIGH,
                    category=Category.FEATURE,
                    business_impact="test",
                    technical_complexity="test",
                    effort_estimate="test",
                    dependencies=[],
                    reasoning="test",
                    confidence_score=0.8
                )
        
        provider = MockAIProvider()
        result = provider.assess_priority("test item")
        
        assert isinstance(result, PriorityAssessment)
        assert result.priority == Priority.HIGH


class TestPriorityEngine:
    """Test PriorityEngine class."""
    
    @patch('src.generators.priority_engine.AIProcessor')
    def test_priority_engine_init_default(self, mock_ai_processor):
        """Test PriorityEngine initialization with default provider."""
        mock_processor = MagicMock()
        mock_ai_processor.return_value = mock_processor
        
        engine = PriorityEngine()
        assert engine.ai_provider is not None
        assert hasattr(engine, 'logger')
    
    @patch('src.generators.priority_engine.AIProcessor')
    def test_priority_engine_init_custom_provider(self, mock_ai_processor):
        """Test PriorityEngine initialization with custom provider."""
        mock_provider = MagicMock()
        
        engine = PriorityEngine(ai_provider=mock_provider)
        assert engine.ai_provider is mock_provider
    
    @patch('src.generators.priority_engine.AIProcessor')
    def test_assess_item_priority_success(self, mock_ai_processor):
        """Test successful priority assessment for single item."""
        # Mock AI processor
        mock_processor = MagicMock()
        mock_ai_processor.return_value = mock_processor
        
        # Mock successful AI response
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.content = """
        Priority Level: High
        Category: Feature
        Business Impact: High
        Technical Complexity: Medium
        Effort Estimate: Medium
        Dependencies: None
        Reasoning: Important feature for user experience
        """
        mock_processor.assess_priority.return_value = mock_response
        
        engine = PriorityEngine()
        item = {
            "title": "User Authentication",
            "description": "Implement OAuth2 authentication",
            "tags": ["feature", "auth"]
        }
        
        assessment = engine.assess_item_priority(item)
        
        assert isinstance(assessment, PriorityAssessment)
        assert assessment.priority == Priority.HIGH
        assert assessment.category == Category.FEATURE
        assert assessment.business_impact == "high"
        assert assessment.technical_complexity == "medium"
        assert assessment.effort_estimate == "medium"
        assert assessment.dependencies == []
        assert "Important feature for user experience" in assessment.reasoning
    
    @patch('src.generators.priority_engine.AIProcessor')
    def test_assess_item_priority_ai_failure(self, mock_ai_processor):
        """Test priority assessment when AI fails."""
        mock_processor = MagicMock()
        mock_ai_processor.return_value = mock_processor
        
        # Mock AI failure
        mock_response = MagicMock()
        mock_response.success = False
        mock_processor.assess_priority.return_value = mock_response
        
        engine = PriorityEngine()
        item = {
            "title": "Bug Fix",
            "description": "Fix login issue",
            "tags": ["bug"]
        }
        
        assessment = engine.assess_item_priority(item)
        
        assert isinstance(assessment, PriorityAssessment)
        assert assessment.category == Category.BUG
        assert "Rule-based assessment" in assessment.reasoning
    
    @patch('src.generators.priority_engine.AIProcessor')
    def test_assess_item_priority_exception(self, mock_ai_processor):
        """Test priority assessment when exception occurs."""
        mock_processor = MagicMock()
        mock_ai_processor.return_value = mock_processor
        mock_processor.assess_priority.side_effect = Exception("AI service error")
        
        engine = PriorityEngine()
        item = {
            "title": "Test Item",
            "description": "Test description"
        }
        
        assessment = engine.assess_item_priority(item)
        
        assert isinstance(assessment, PriorityAssessment)
        assert assessment.priority == Priority.MEDIUM
        assert assessment.category == Category.FEATURE
        assert "Default assessment" in assessment.reasoning
        assert assessment.confidence_score == 0.3
    
    @patch('src.generators.priority_engine.AIProcessor')
    def test_assess_multiple_items(self, mock_ai_processor):
        """Test priority assessment for multiple items."""
        mock_processor = MagicMock()
        mock_ai_processor.return_value = mock_processor
        
        # Mock AI response
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.content = """
        Priority Level: Medium
        Category: Feature
        Business Impact: Medium
        Technical Complexity: Low
        Effort Estimate: Small
        Dependencies: None
        Reasoning: Standard feature implementation
        """
        mock_processor.assess_priority.return_value = mock_response
        
        engine = PriorityEngine()
        items = [
            {"title": "Feature 1", "description": "First feature"},
            {"title": "Feature 2", "description": "Second feature"}
        ]
        
        assessments = engine.assess_multiple_items(items)
        
        assert len(assessments) == 2
        for assessment in assessments:
            assert isinstance(assessment, PriorityAssessment)
            assert assessment.priority == Priority.MEDIUM
            assert assessment.category == Category.FEATURE
    
    @patch('src.generators.priority_engine.AIProcessor')
    def test_categorize_backlog(self, mock_ai_processor):
        """Test backlog categorization."""
        mock_processor = MagicMock()
        mock_ai_processor.return_value = mock_processor
        
        engine = PriorityEngine()
        items = [
            {"title": "Bug fix", "description": "Fix login bug", "tags": ["bug"]},
            {"title": "New feature", "description": "Add user profile"},
            {"title": "Research", "description": "Investigate new tech"},
            {"title": "Refactor", "description": "Clean up code", "tags": ["refactor"]},
            {"title": "Enhancement", "description": "Improve performance"},
            {"title": "Maintenance", "description": "Update dependencies"}
        ]
        
        categorized = engine.categorize_backlog(items)
        
        assert len(categorized) == len(Category)
        assert len(categorized[Category.BUG]) == 1
        assert len(categorized[Category.FEATURE]) == 1
        assert len(categorized[Category.RESEARCH]) == 1
        assert len(categorized[Category.TECHNICAL_DEBT]) == 1
        assert len(categorized[Category.ENHANCEMENT]) == 1
        assert len(categorized[Category.MAINTENANCE]) == 1
    
    @patch('src.generators.priority_engine.AIProcessor')
    def test_recommend_sprint_items(self, mock_ai_processor):
        """Test sprint item recommendations."""
        mock_processor = MagicMock()
        mock_ai_processor.return_value = mock_processor
        
        # Mock AI response
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.content = """
        Priority Level: High
        Category: Feature
        Business Impact: High
        Technical Complexity: Medium
        Effort Estimate: Small
        Dependencies: None
        Reasoning: Critical feature
        """
        mock_processor.assess_priority.return_value = mock_response
        
        engine = PriorityEngine()
        items = [
            {"title": "High Priority", "description": "Important feature"},
            {"title": "Medium Priority", "description": "Standard feature"},
            {"title": "Low Priority", "description": "Nice to have"}
        ]
        
        recommendations = engine.recommend_sprint_items(items, sprint_capacity=10)
        
        assert len(recommendations) > 0
        for rec in recommendations:
            assert "item" in rec
            assert "assessment" in rec
            assert "effort_points" in rec
            assert isinstance(rec["assessment"], PriorityAssessment)
    
    def test_format_item_for_analysis(self):
        """Test item formatting for AI analysis."""
        engine = PriorityEngine()
        item = {
            "title": "Test Feature",
            "description": "This is a test feature",
            "priority": "High",
            "tags": ["test", "feature"]
        }
        
        formatted = engine._format_item_for_analysis(item)
        
        assert "Test Feature" in formatted
        assert "This is a test feature" in formatted
        assert "High" in formatted
        assert "test, feature" in formatted
    
    def test_parse_ai_priority_response(self):
        """Test AI response parsing."""
        engine = PriorityEngine()
        ai_content = """
        Priority Level: Critical
        Category: Bug
        Business Impact: High
        Technical Complexity: Low
        Effort Estimate: Small
        Dependencies: auth-service, database
        Reasoning: Critical security vulnerability that needs immediate attention
        """
        
        assessment = engine._parse_ai_priority_response(ai_content)
        
        assert assessment.priority == Priority.CRITICAL
        assert assessment.category == Category.BUG
        assert assessment.business_impact == "high"
        assert assessment.technical_complexity == "low"
        assert assessment.effort_estimate == "small"
        assert assessment.dependencies == ["auth-service", "database"]
        assert "Critical security vulnerability" in assessment.reasoning
        assert assessment.confidence_score == 0.8
    
    def test_validate_and_adjust_assessment_security(self):
        """Test assessment adjustment for security items."""
        engine = PriorityEngine()
        assessment = PriorityAssessment(
            priority=Priority.LOW,
            category=Category.FEATURE,
            business_impact="low",
            technical_complexity="low",
            effort_estimate="small",
            dependencies=[],
            reasoning="Regular feature",
            confidence_score=0.8
        )
        
        item = {
            "title": "Security Fix",
            "description": "Fix authentication vulnerability"
        }
        
        adjusted = engine._validate_and_adjust_assessment(assessment, item)
        
        assert adjusted.priority == Priority.HIGH
        assert "Security-related items prioritized" in adjusted.reasoning
    
    def test_validate_and_adjust_assessment_bug(self):
        """Test assessment adjustment for bug items."""
        engine = PriorityEngine()
        assessment = PriorityAssessment(
            priority=Priority.LOW,
            category=Category.BUG,
            business_impact="low",
            technical_complexity="low",
            effort_estimate="small",
            dependencies=[],
            reasoning="Minor bug",
            confidence_score=0.8
        )
        
        item = {"title": "UI Bug", "description": "Fix button color"}
        
        adjusted = engine._validate_and_adjust_assessment(assessment, item)
        
        assert adjusted.priority == Priority.MEDIUM
        assert "Bug fixes prioritized" in adjusted.reasoning
    
    def test_rule_based_priority_assessment(self):
        """Test rule-based priority assessment."""
        engine = PriorityEngine()
        
        # Test critical item
        critical_item = {
            "title": "Critical Security Bug",
            "description": "Urgent security vulnerability",
            "tags": ["security", "critical"]
        }
        
        assessment = engine._rule_based_priority_assessment(critical_item)
        
        assert assessment.priority == Priority.HIGH
        assert assessment.category == Category.BUG
        assert "Rule-based assessment" in assessment.reasoning
        assert assessment.confidence_score == 0.6
    
    def test_default_priority_assessment(self):
        """Test default priority assessment."""
        engine = PriorityEngine()
        item = {"title": "Test", "description": "Test"}
        
        assessment = engine._default_priority_assessment(item)
        
        assert assessment.priority == Priority.MEDIUM
        assert assessment.category == Category.FEATURE
        assert assessment.business_impact == "medium"
        assert assessment.technical_complexity == "medium"
        assert assessment.effort_estimate == "medium"
        assert assessment.dependencies == []
        assert "Default assessment" in assessment.reasoning
        assert assessment.confidence_score == 0.3
    
    def test_determine_category(self):
        """Test category determination."""
        engine = PriorityEngine()
        
        # Test bug category
        bug_item = {"title": "Fix bug", "description": "Error in login", "tags": ["bug"]}
        assert engine._determine_category(bug_item) == Category.BUG
        
        # Test feature category
        feature_item = {"title": "New feature", "description": "Add user profile"}
        assert engine._determine_category(feature_item) == Category.FEATURE
        
        # Test research category
        research_item = {"title": "Investigate", "description": "Research new technology"}
        assert engine._determine_category(research_item) == Category.RESEARCH
    
    def test_text_to_priority(self):
        """Test text to priority conversion."""
        engine = PriorityEngine()
        
        assert engine._text_to_priority("critical") == Priority.CRITICAL
        assert engine._text_to_priority("high priority") == Priority.HIGH
        assert engine._text_to_priority("low priority") == Priority.LOW
        assert engine._text_to_priority("medium") == Priority.MEDIUM
        assert engine._text_to_priority("unknown") == Priority.MEDIUM
    
    def test_text_to_category(self):
        """Test text to category conversion."""
        engine = PriorityEngine()
        
        assert engine._text_to_category("bug fix") == Category.BUG
        assert engine._text_to_category("feature request") == Category.FEATURE
        assert engine._text_to_category("research task") == Category.RESEARCH
        assert engine._text_to_category("technical debt") == Category.TECHNICAL_DEBT
        assert engine._text_to_category("maintenance") == Category.MAINTENANCE
        assert engine._text_to_category("enhancement") == Category.ENHANCEMENT
    
    def test_is_security_related(self):
        """Test security-related item detection."""
        engine = PriorityEngine()
        
        security_item = {
            "title": "Authentication Fix",
            "description": "Fix SSL vulnerability"
        }
        assert engine._is_security_related(security_item) is True
        
        normal_item = {
            "title": "UI Feature",
            "description": "Add new button"
        }
        assert engine._is_security_related(normal_item) is False
    
    def test_is_critical_path(self):
        """Test critical path item detection."""
        engine = PriorityEngine()
        
        critical_item = {
            "title": "Blocker Issue",
            "description": "Critical for deadline"
        }
        assert engine._is_critical_path(critical_item) is True
        
        normal_item = {
            "title": "Regular Feature",
            "description": "Standard enhancement"
        }
        assert engine._is_critical_path(normal_item) is False
    
    def test_extract_value_after_colon(self):
        """Test value extraction after colon."""
        engine = PriorityEngine()
        
        assert engine._extract_value_after_colon("Priority: High") == "High"
        assert engine._extract_value_after_colon("No colon here") == "No colon here"
        assert engine._extract_value_after_colon("Multiple: colons: here") == "colons: here"
    
    def test_estimate_effort_points(self):
        """Test effort point estimation."""
        engine = PriorityEngine()
        
        assert engine._estimate_effort_points("small") == 2
        assert engine._estimate_effort_points("medium") == 5
        assert engine._estimate_effort_points("large") == 8
        assert engine._estimate_effort_points("xl") == 13
        assert engine._estimate_effort_points("unknown") == 5
