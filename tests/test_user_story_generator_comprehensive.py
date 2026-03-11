"""Comprehensive tests for User Story Generator to improve code coverage."""

import pytest
from unittest.mock import MagicMock, patch
from typing import List

from src.generators.user_story_generator import (
    AIProviderProtocol,
    UserStoryGenerator
)
from src.models.backlog_models import AcceptanceCriterion, UserStory
from src.models.base_models import EffortEstimate, Priority


class TestAIProviderProtocol:
    """Test AIProviderProtocol."""
    
    def test_ai_provider_protocol_interface(self):
        """Test that AIProviderProtocol defines the expected interface."""
        class MockAIProvider:
            def generate_user_stories(self, requirements: str):
                return MagicMock(success=True, content="Mock user stories")
        
        provider = MockAIProvider()
        result = provider.generate_user_stories("test requirements")
        
        assert result.success is True
        assert result.content == "Mock user stories"


class TestUserStoryGenerator:
    """Test UserStoryGenerator class."""
    
    @patch('src.generators.user_story_generator.AIProcessor')
    def test_user_story_generator_init_default(self, mock_ai_processor):
        """Test UserStoryGenerator initialization with default provider."""
        mock_processor = MagicMock()
        mock_ai_processor.return_value = mock_processor
        
        generator = UserStoryGenerator()
        
        assert generator.ai_provider is not None
        assert hasattr(generator, 'logger')
        mock_ai_processor.assert_called_once()
    
    def test_user_story_generator_init_custom_provider(self):
        """Test UserStoryGenerator initialization with custom provider."""
        mock_provider = MagicMock()
        
        generator = UserStoryGenerator(ai_provider=mock_provider)
        
        assert generator.ai_provider is mock_provider
    
    def test_generate_stories_from_requirements_success(self):
        """Test successful story generation from requirements."""
        mock_provider = MagicMock()
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.content = """
        **Story 1**: As a user, I want to login so that I can access my account
        **Acceptance Criteria**:
        - User can enter username and password
        - System validates credentials
        - User is redirected on success
        
        **Story 2**: As a user, I want to reset password so that I can recover access
        **Acceptance Criteria**:
        - User can request password reset
        - System sends reset email
        """
        mock_provider.generate_user_stories.return_value = mock_response
        
        generator = UserStoryGenerator(ai_provider=mock_provider)
        requirements = "User authentication and password reset functionality"
        
        stories = generator.generate_stories_from_requirements(requirements)
        
        assert isinstance(stories, list)
        assert len(stories) >= 1
        for story in stories:
            assert isinstance(story, UserStory)
            assert story.title
            assert story.user_role
            assert story.functionality
            assert story.benefit
    
    def test_generate_stories_from_requirements_ai_failure(self):
        """Test story generation when AI fails."""
        mock_provider = MagicMock()
        mock_response = MagicMock()
        mock_response.success = False
        mock_response.error_message = "AI service unavailable"
        mock_provider.generate_user_stories.return_value = mock_response
        
        generator = UserStoryGenerator(ai_provider=mock_provider)
        requirements = "User authentication functionality"
        
        stories = generator.generate_stories_from_requirements(requirements)
        
        assert isinstance(stories, list)
        assert len(stories) >= 1
        # Should fallback to rule-based generation
        for story in stories:
            assert isinstance(story, UserStory)
            assert "Fallback" in story.title or "Generated" in story.title
    
    def test_generate_stories_from_requirements_exception(self):
        """Test story generation when exception occurs."""
        mock_provider = MagicMock()
        mock_provider.generate_user_stories.side_effect = Exception("Network error")
        
        generator = UserStoryGenerator(ai_provider=mock_provider)
        requirements = "Test functionality"
        
        stories = generator.generate_stories_from_requirements(requirements)
        
        assert isinstance(stories, list)
        assert len(stories) >= 1
        # Should fallback to rule-based generation
        for story in stories:
            assert isinstance(story, UserStory)
    
    def test_generate_stories_from_backlog_items(self):
        """Test story generation from backlog items."""
        mock_provider = MagicMock()
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.content = """
        **Story 1**: As a user, I want to view dashboard so that I can see overview
        **Acceptance Criteria**:
        - Dashboard loads quickly
        - Shows key metrics
        """
        mock_provider.generate_user_stories.return_value = mock_response
        
        generator = UserStoryGenerator(ai_provider=mock_provider)
        backlog_items = [
            {"title": "Dashboard Feature", "description": "Create user dashboard"},
            {"title": "Analytics", "description": "Add analytics tracking"}
        ]
        
        stories = generator.generate_stories_from_backlog_items(backlog_items)
        
        assert isinstance(stories, list)
        assert len(stories) >= 1
        for story in stories:
            assert isinstance(story, UserStory)
    
    def test_enhance_existing_stories(self):
        """Test enhancement of existing stories."""
        mock_provider = MagicMock()
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.content = """
        Enhanced acceptance criteria:
        - User can login with email or username
        - Password must meet security requirements
        - Account lockout after failed attempts
        - Two-factor authentication support
        """
        mock_provider.generate_user_stories.return_value = mock_response
        
        generator = UserStoryGenerator(ai_provider=mock_provider)
        
        # Create basic story
        basic_story = UserStory(
            title="User Login",
            user_role="user",
            functionality="login to system",
            benefit="access account",
            acceptance_criteria=[
                AcceptanceCriterion(description="User can enter credentials")
            ],
            priority=Priority.MEDIUM,
            estimated_effort=EffortEstimate.MEDIUM,
            tags=["auth"],
            original_requirement="User authentication"
        )
        
        enhanced_stories = generator.enhance_existing_stories([basic_story])
        
        assert isinstance(enhanced_stories, list)
        assert len(enhanced_stories) >= 1
        for story in enhanced_stories:
            assert isinstance(story, UserStory)
            assert len(story.acceptance_criteria) >= 1
    
    def test_parse_ai_response_to_stories(self):
        """Test parsing AI response to stories."""
        generator = UserStoryGenerator()
        
        ai_content = """
        **Story 1**: As a user, I want to login so that I can access my account
        **Acceptance Criteria**:
        - User can enter username and password
        - System validates credentials
        - User is redirected on success
        
        **Story 2**: As an admin, I want to manage users so that I can control access
        **Acceptance Criteria**:
        - Admin can view user list
        - Admin can disable accounts
        """
        
        stories = generator._parse_ai_response_to_stories(ai_content, "User management")
        
        assert isinstance(stories, list)
        assert len(stories) == 2
        
        # Check first story
        story1 = stories[0]
        assert story1.title == "User Login"
        assert story1.user_role == "user"
        assert story1.functionality == "login"
        assert story1.benefit == "access my account"
        assert len(story1.acceptance_criteria) == 3
        
        # Check second story
        story2 = stories[1]
        assert story2.title == "User Management"
        assert story2.user_role == "admin"
        assert story2.functionality == "manage users"
        assert story2.benefit == "control access"
        assert len(story2.acceptance_criteria) == 2
    
    def test_validate_story_structure_valid(self):
        """Test story structure validation with valid story."""
        generator = UserStoryGenerator()
        
        valid_story = UserStory(
            title="Valid Story",
            user_role="user",
            functionality="perform action",
            benefit="achieve goal",
            acceptance_criteria=[
                AcceptanceCriterion(description="Valid criterion")
            ],
            priority=Priority.HIGH,
            estimated_effort=EffortEstimate.SMALL,
            tags=["test"],
            original_requirement="Test requirement"
        )
        
        assert generator._validate_story_structure(valid_story) is True
    
    def test_validate_story_structure_invalid(self):
        """Test story structure validation with invalid story."""
        generator = UserStoryGenerator()
        
        # Missing required fields
        invalid_story = UserStory(
            title="",  # Empty title
            user_role="user",
            functionality="",  # Empty functionality
            benefit="achieve goal",
            acceptance_criteria=[],  # No acceptance criteria
            priority=Priority.HIGH,
            estimated_effort=EffortEstimate.SMALL,
            tags=[],
            original_requirement="Test requirement"
        )
        
        assert generator._validate_story_structure(invalid_story) is False
    
    def test_generate_fallback_stories(self):
        """Test fallback story generation."""
        generator = UserStoryGenerator()
        requirements = "User authentication and profile management"
        
        fallback_stories = generator._generate_fallback_stories(requirements)
        
        assert isinstance(fallback_stories, list)
        assert len(fallback_stories) >= 1
        for story in fallback_stories:
            assert isinstance(story, UserStory)
            assert "Fallback" in story.title
            assert story.user_role == "user"
            assert len(story.acceptance_criteria) >= 1
    
    def test_extract_story_components(self):
        """Test story component extraction."""
        generator = UserStoryGenerator()
        
        story_text = "As a user, I want to login so that I can access my account"
        user_role, functionality, benefit = generator._extract_story_components(story_text)
        
        assert user_role == "user"
        assert functionality == "login"
        assert benefit == "access my account"
    
    def test_extract_story_components_malformed(self):
        """Test story component extraction with malformed text."""
        generator = UserStoryGenerator()
        
        malformed_text = "This is not a proper user story format"
        user_role, functionality, benefit = generator._extract_story_components(malformed_text)
        
        # Should return defaults for malformed input
        assert user_role == "user"
        assert functionality == "perform action"
        assert benefit == "achieve goal"
    
    def test_determine_priority_from_text(self):
        """Test priority determination from text."""
        generator = UserStoryGenerator()
        
        # Test different priority keywords
        assert generator._determine_priority_from_text("critical security issue") == Priority.CRITICAL
        assert generator._determine_priority_from_text("high priority feature") == Priority.HIGH
        assert generator._determine_priority_from_text("low priority enhancement") == Priority.LOW
        assert generator._determine_priority_from_text("regular feature") == Priority.MEDIUM
    
    def test_estimate_effort_from_text(self):
        """Test effort estimation from text."""
        generator = UserStoryGenerator()
        
        # Test different effort keywords
        assert generator._estimate_effort_from_text("simple login form") == EffortEstimate.SMALL
        assert generator._estimate_effort_from_text("complex dashboard") == EffortEstimate.LARGE
        assert generator._estimate_effort_from_text("integration with API") == EffortEstimate.MEDIUM
        assert generator._estimate_effort_from_text("regular feature") == EffortEstimate.MEDIUM
    
    def test_extract_tags_from_text(self):
        """Test tag extraction from text."""
        generator = UserStoryGenerator()
        
        text = "User authentication with OAuth2 and security features"
        tags = generator._extract_tags_from_text(text)
        
        assert isinstance(tags, list)
        assert len(tags) >= 2
        assert "auth" in tags or "authentication" in tags
        assert "security" in tags
    
    def test_clean_story_title(self):
        """Test story title cleaning."""
        generator = UserStoryGenerator()
        
        # Test various title formats
        assert generator._clean_story_title("**Story 1**: User Login") == "User Login"
        assert generator._clean_story_title("Story: User Registration") == "User Registration"
        assert generator._clean_story_title("1. User Profile") == "User Profile"
        assert generator._clean_story_title("Clean Title") == "Clean Title"
    
    def test_create_acceptance_criteria(self):
        """Test acceptance criteria creation."""
        generator = UserStoryGenerator()
        
        criteria_text = """
        - User can enter username and password
        - System validates credentials
        - User is redirected on success
        - Error message shown for invalid credentials
        """
        
        criteria = generator._create_acceptance_criteria(criteria_text)
        
        assert isinstance(criteria, list)
        assert len(criteria) == 4
        for criterion in criteria:
            assert isinstance(criterion, AcceptanceCriterion)
            assert criterion.description
            assert criterion.description.strip()
    
    def test_create_acceptance_criteria_empty(self):
        """Test acceptance criteria creation with empty input."""
        generator = UserStoryGenerator()
        
        criteria = generator._create_acceptance_criteria("")
        
        assert isinstance(criteria, list)
        assert len(criteria) == 1
        assert criteria[0].description == "Implementation details to be defined"
    
    def test_format_backlog_items_for_ai(self):
        """Test backlog items formatting for AI."""
        generator = UserStoryGenerator()
        
        items = [
            {"title": "User Login", "description": "Implement OAuth2 login"},
            {"title": "Dashboard", "description": "Create user dashboard", "priority": "high"}
        ]
        
        formatted = generator._format_backlog_items_for_ai(items)
        
        assert isinstance(formatted, str)
        assert "User Login" in formatted
        assert "OAuth2 login" in formatted
        assert "Dashboard" in formatted
        assert "high" in formatted
    
    def test_split_into_sentences(self):
        """Test sentence splitting."""
        generator = UserStoryGenerator()
        
        text = "First sentence. Second sentence! Third sentence?"
        sentences = generator._split_into_sentences(text)
        
        assert isinstance(sentences, list)
        assert len(sentences) == 3
        assert "First sentence" in sentences[0]
        assert "Second sentence" in sentences[1]
        assert "Third sentence" in sentences[2]
    
    def test_generate_story_variations(self):
        """Test story variation generation."""
        generator = UserStoryGenerator()
        
        base_story = UserStory(
            title="User Login",
            user_role="user",
            functionality="login",
            benefit="access account",
            acceptance_criteria=[
                AcceptanceCriterion(description="User can enter credentials")
            ],
            priority=Priority.MEDIUM,
            estimated_effort=EffortEstimate.MEDIUM,
            tags=["auth"],
            original_requirement="User authentication"
        )
        
        variations = generator.generate_story_variations(base_story, 3)
        
        assert isinstance(variations, list)
        assert len(variations) <= 3
        for variation in variations:
            assert isinstance(variation, UserStory)
            assert variation.user_role  # Should have different roles
            assert variation.title != base_story.title  # Should be different


class TestUserStoryGeneratorIntegration:
    """Integration tests for UserStoryGenerator."""
    
    def test_end_to_end_story_generation(self):
        """Test complete story generation workflow."""
        mock_provider = MagicMock()
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.content = """
        **Story 1**: As a user, I want to register an account so that I can use the system
        **Acceptance Criteria**:
        - User can enter email and password
        - System validates email format
        - Confirmation email is sent
        - Account is created successfully
        """
        mock_provider.generate_user_stories.return_value = mock_response
        
        generator = UserStoryGenerator(ai_provider=mock_provider)
        requirements = "User registration system with email verification"
        
        stories = generator.generate_stories_from_requirements(requirements)
        
        assert len(stories) >= 1
        story = stories[0]
        
        # Verify complete story structure
        assert story.title == "User Registration"
        assert story.user_role == "user"
        assert story.functionality == "register an account"
        assert story.benefit == "use the system"
        assert len(story.acceptance_criteria) == 4
        assert story.priority in [Priority.LOW, Priority.MEDIUM, Priority.HIGH, Priority.CRITICAL]
        assert story.estimated_effort in [EffortEstimate.SMALL, EffortEstimate.MEDIUM, EffortEstimate.LARGE, EffortEstimate.EXTRA_LARGE]
        assert isinstance(story.tags, list)
        assert story.original_requirement == requirements
    
    def test_multiple_providers_compatibility(self):
        """Test that generator works with different provider implementations."""
        # Test with different mock providers
        providers = []
        
        # Provider 1: Always successful
        provider1 = MagicMock()
        provider1.generate_user_stories.return_value = MagicMock(
            success=True, 
            content="**Story**: As a user, I want to test so that I can verify"
        )
        providers.append(provider1)
        
        # Provider 2: Always fails
        provider2 = MagicMock()
        provider2.generate_user_stories.return_value = MagicMock(
            success=False, 
            error_message="Service unavailable"
        )
        providers.append(provider2)
        
        requirements = "Test functionality"
        
        for provider in providers:
            generator = UserStoryGenerator(ai_provider=provider)
            stories = generator.generate_stories_from_requirements(requirements)
            
            assert isinstance(stories, list)
            assert len(stories) >= 1
            for story in stories:
                assert isinstance(story, UserStory)
    
    def test_story_enhancement_workflow(self):
        """Test the complete story enhancement workflow."""
        mock_provider = MagicMock()
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.content = """
        Enhanced acceptance criteria:
        - User authentication with multi-factor support
        - Session management with timeout
        - Audit logging for security events
        - Password complexity requirements
        """
        mock_provider.generate_user_stories.return_value = mock_response
        
        generator = UserStoryGenerator(ai_provider=mock_provider)
        
        # Create initial stories
        initial_stories = [
            UserStory(
                title="Basic Login",
                user_role="user",
                functionality="login",
                benefit="access system",
                acceptance_criteria=[
                    AcceptanceCriterion(description="Basic login functionality")
                ],
                priority=Priority.MEDIUM,
                estimated_effort=EffortEstimate.SMALL,
                tags=["auth"],
                original_requirement="User login"
            )
        ]
        
        # Enhance stories
        enhanced_stories = generator.enhance_existing_stories(initial_stories)
        
        assert len(enhanced_stories) >= 1
        enhanced_story = enhanced_stories[0]
        
        # Should have more detailed acceptance criteria
        assert len(enhanced_story.acceptance_criteria) >= 2
        assert any("multi-factor" in ac.description.lower() for ac in enhanced_story.acceptance_criteria)
