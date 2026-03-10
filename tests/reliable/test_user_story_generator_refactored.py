"""Tests for refactored user story generator - demonstrating simplified testing with providers."""

import pytest
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestUserStoryGeneratorRefactored:
    """Test refactored user story generator with easy dependency injection."""
    
    def test_generator_with_mock_provider(self):
        """Test user story generator with mock provider - no external dependencies."""
        from generators.user_story_generator_refactored import UserStoryGeneratorRefactored
        from providers.openai_provider import MockAIProvider
        
        # Setup mock responses
        mock_responses = {
            "structured": {
                "user_type": "customer",
                "functionality": "view order history",
                "benefit": "track previous purchases",
                "action": "access",
                "object": "order records",
                "outcome": "see purchase history",
                "additional_benefit": "make informed decisions",
                "acceptance_criteria": ["Can view last 10 orders", "Shows order details", "Filters by date"]
            }
        }
        
        mock_provider = MockAIProvider(mock_responses)
        generator = UserStoryGeneratorRefactored(ai_provider=mock_provider)
        
        # Test availability
        assert generator.is_available() == True
        
        # Test basic story generation
        requirements = "Users need to see their order history to track purchases"
        result = generator.generate_user_story(requirements)
        
        assert result['success'] == True
        assert result['story'] is not None
        assert 'As a customer' in result['story']
        assert 'view order history' in result['story']
        assert 'track previous purchases' in result['story']
        assert result['template_used'] == 'basic'
        assert len(result['acceptance_criteria']) == 3
        assert 'generated_at' in result
        
        # Verify components
        components = result['components']
        assert components['user_type'] == 'customer'
        assert components['functionality'] == 'view order history'
        assert components['benefit'] == 'track previous purchases'
    
    def test_different_templates(self):
        """Test story generation with different templates."""
        from generators.user_story_generator_refactored import UserStoryGeneratorRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_responses = {
            "structured": {
                "user_type": "admin",
                "functionality": "manage user accounts",
                "benefit": "maintain system security",
                "action": "modify",
                "object": "user permissions",
                "outcome": "control access",
                "additional_benefit": "ensure compliance",
                "acceptance_criteria": ["Can add users", "Can remove users", "Can modify roles"]
            }
        }
        
        mock_provider = MockAIProvider(mock_responses)
        generator = UserStoryGeneratorRefactored(ai_provider=mock_provider)
        
        requirements = "Admin needs to manage user accounts for security"
        
        # Test basic template
        basic_result = generator.generate_user_story(requirements, 'basic')
        assert basic_result['success'] == True
        assert basic_result['template_used'] == 'basic'
        assert 'As a admin, I want manage user accounts so that maintain system security' in basic_result['story']
        
        # Test detailed template
        detailed_result = generator.generate_user_story(requirements, 'detailed')
        assert detailed_result['success'] == True
        assert detailed_result['template_used'] == 'detailed'
        assert 'modify' in detailed_result['story']
        assert 'user permissions' in detailed_result['story']
        
        # Test acceptance template
        acceptance_result = generator.generate_user_story(requirements, 'acceptance')
        assert acceptance_result['success'] == True
        assert acceptance_result['template_used'] == 'acceptance'
        assert 'Acceptance Criteria:' in acceptance_result['story']
        assert '- Can add users' in acceptance_result['story']
    
    def test_story_suite_generation(self):
        """Test generating multiple stories from requirements list."""
        from generators.user_story_generator_refactored import UserStoryGeneratorRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_responses = {
            "structured": {
                "user_type": "user",
                "functionality": "perform action",
                "benefit": "achieve goal",
                "action": "execute",
                "object": "task",
                "outcome": "complete work",
                "additional_benefit": "save time",
                "acceptance_criteria": ["Action works", "Goal achieved"]
            }
        }
        
        mock_provider = MockAIProvider(mock_responses)
        generator = UserStoryGeneratorRefactored(ai_provider=mock_provider)
        
        requirements_list = [
            "User needs login functionality",
            "User wants to reset password",
            "User should see dashboard after login"
        ]
        
        result = generator.generate_story_suite(requirements_list)
        assert result['success'] == True
        assert result['total_requirements'] == 3
        assert result['successful_stories'] == 3
        assert result['failed_stories'] == 0
        assert len(result['stories']) == 3
        assert len(result['failures']) == 0
        
        # Check that different templates were used
        templates_used = [story['template_used'] for story in result['stories']]
        assert 'basic' in templates_used
        assert 'detailed' in templates_used
        assert 'acceptance' in templates_used
        
        # Check that original requirements are preserved
        for story in result['stories']:
            assert 'original_requirements' in story
            assert story['original_requirements'] in requirements_list
    
    def test_story_enhancement(self):
        """Test enhancing existing user stories."""
        from generators.user_story_generator_refactored import UserStoryGeneratorRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_responses = {
            "structured": {
                "enhanced_story": "As a customer, I want to securely log into my account using email and password so that I can access my personal dashboard and manage my profile.",
                "improvements": ["Added security aspect", "Specified login method", "Clarified outcome"],
                "acceptance_criteria": ["Email validation works", "Password meets requirements", "Dashboard loads correctly"],
                "edge_cases": ["Invalid credentials", "Account locked", "Network timeout"],
                "dependencies": ["Authentication service", "User database"],
                "effort_estimate": 5
            }
        }
        
        mock_provider = MockAIProvider(mock_responses)
        generator = UserStoryGeneratorRefactored(ai_provider=mock_provider)
        
        original_story = "As a customer, I want to login so that I can use the system."
        result = generator.enhance_existing_story(original_story)
        
        assert result['success'] == True
        assert result['original_story'] == original_story
        assert len(result['enhanced_story']) > len(original_story)
        assert len(result['improvements']) == 3
        assert len(result['acceptance_criteria']) == 3
        assert len(result['edge_cases']) == 3
        assert len(result['dependencies']) == 2
        assert result['effort_estimate'] == 5
        assert 'enhanced_at' in result
    
    def test_story_validation(self):
        """Test user story validation."""
        from generators.user_story_generator_refactored import UserStoryGeneratorRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_responses = {
            "structured": {
                "quality_score": 85,
                "clarity_score": 90,
                "completeness_score": 80,
                "suggestions": ["Add more specific acceptance criteria", "Consider edge cases"],
                "strengths": ["Clear user type", "Well-defined benefit"]
            }
        }
        
        mock_provider = MockAIProvider(mock_responses)
        generator = UserStoryGeneratorRefactored(ai_provider=mock_provider)
        
        # Test valid story
        valid_story = "As a customer, I want to view my order history so that I can track my purchases."
        result = generator.validate_story(valid_story)
        
        assert result['success'] == True
        assert result['story'] == valid_story
        assert result['validation_result']['is_valid'] == True
        assert result['validation_result']['overall_score'] > 70
        
        # Check basic validation
        basic_val = result['validation_result']['basic_validation']
        assert basic_val['is_valid'] == True
        assert basic_val['score'] == 100
        assert len(basic_val['issues']) == 0
        
        # Check AI validation
        ai_val = result['validation_result']['ai_validation']
        assert ai_val['is_valid'] == True
        assert ai_val['quality_score'] == 85
        assert ai_val['clarity_score'] == 90
        assert ai_val['completeness_score'] == 80
        assert len(ai_val['suggestions']) == 2
        assert len(ai_val['strengths']) == 2
    
    def test_invalid_story_validation(self):
        """Test validation of invalid stories."""
        from generators.user_story_generator_refactored import UserStoryGeneratorRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_provider = MockAIProvider()
        generator = UserStoryGeneratorRefactored(ai_provider=mock_provider)
        
        # Test story missing components
        invalid_story = "I want something to work."
        result = generator.validate_story(invalid_story)
        
        assert result['success'] == True
        basic_val = result['validation_result']['basic_validation']
        assert basic_val['is_valid'] == False
        assert len(basic_val['issues']) > 0
        assert basic_val['score'] < 100
        
        # Should have specific issues
        issues_text = ' '.join(basic_val['issues'])
        assert "Missing 'As a'" in issues_text
        assert "Missing 'so that'" in issues_text
        assert "vague term: 'something'" in issues_text
    
    def test_epic_breakdown(self):
        """Test breaking down epics into user stories."""
        from generators.user_story_generator_refactored import UserStoryGeneratorRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_responses = {
            "structured": {
                "epic_title": "User Authentication System",
                "user_stories": [
                    "User registration with email verification",
                    "User login with password",
                    "Password reset functionality",
                    "User profile management"
                ],
                "story_priorities": {
                    "0": "high",
                    "1": "high", 
                    "2": "medium",
                    "3": "low"
                },
                "dependencies": {
                    "1": ["0"],  # Login depends on registration
                    "2": ["1"]   # Password reset depends on login
                },
                "estimated_effort": 21
            }
        }
        
        mock_provider = MockAIProvider(mock_responses)
        generator = UserStoryGeneratorRefactored(ai_provider=mock_provider)
        
        epic_description = "Build a complete user authentication system with registration, login, and profile management"
        result = generator.generate_epic_breakdown(epic_description)
        
        assert result['success'] == True
        assert result['epic_title'] == "User Authentication System"
        assert result['epic_description'] == epic_description
        assert result['total_stories'] == 4
        assert len(result['stories']) == 4
        assert result['estimated_effort'] == 21
        
        # Check that stories have priorities
        priorities = [story['priority'] for story in result['stories']]
        assert 'high' in priorities
        assert 'medium' in priorities
        assert 'low' in priorities
        
        # Check dependencies
        assert '1' in result['dependencies']
        assert '2' in result['dependencies']
    
    def test_empty_inputs(self):
        """Test handling of empty inputs."""
        from generators.user_story_generator_refactored import UserStoryGeneratorRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_provider = MockAIProvider()
        generator = UserStoryGeneratorRefactored(ai_provider=mock_provider)
        
        # Test empty requirements
        result = generator.generate_user_story("")
        assert result['success'] == False
        assert 'empty' in result['error'].lower()
        
        # Test empty story suite
        result = generator.generate_story_suite([])
        assert result['success'] == False
        assert 'empty' in result['error'].lower()
        
        # Test empty story for enhancement
        result = generator.enhance_existing_story("")
        assert result['success'] == False
        assert 'empty' in result['error'].lower()
        
        # Test empty story for validation
        result = generator.validate_story("")
        assert result['success'] == False
        assert 'empty' in result['error'].lower()
        
        # Test empty epic
        result = generator.generate_epic_breakdown("")
        assert result['success'] == False
        assert 'empty' in result['error'].lower()
    
    def test_story_suite_with_failures(self):
        """Test story suite generation with some failures."""
        from generators.user_story_generator_refactored import UserStoryGeneratorRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_responses = {
            "structured": {
                "user_type": "user",
                "functionality": "perform action",
                "benefit": "achieve goal",
                "acceptance_criteria": ["Works correctly"]
            }
        }
        
        mock_provider = MockAIProvider(mock_responses)
        generator = UserStoryGeneratorRefactored(ai_provider=mock_provider)
        
        # Mix of valid and invalid requirements
        requirements_list = [
            "Valid requirement for user login",
            "",  # Empty requirement
            "Another valid requirement for dashboard",
            "   ",  # Whitespace only
            "Third valid requirement for logout"
        ]
        
        result = generator.generate_story_suite(requirements_list)
        assert result['success'] == True
        assert result['total_requirements'] == 5
        assert result['successful_stories'] == 3
        assert result['failed_stories'] == 2
        assert len(result['stories']) == 3
        assert len(result['failures']) == 2
        
        # Check failure details
        for failure in result['failures']:
            assert 'index' in failure
            assert 'error' in failure
            assert 'requirements' in failure
            assert failure['error'] == 'Empty requirements'
    
    def test_ai_unavailable_fallback(self):
        """Test behavior when AI is unavailable."""
        from generators.user_story_generator_refactored import UserStoryGeneratorRefactored
        from providers.openai_provider import MockAIProvider
        
        # Create unavailable AI provider
        class UnavailableAIProvider(MockAIProvider):
            def is_available(self):
                return False
        
        unavailable_provider = UnavailableAIProvider()
        generator = UserStoryGeneratorRefactored(ai_provider=unavailable_provider)
        
        assert generator.is_available() == False
        
        # Story validation should still work with basic validation only
        story = "As a user, I want to login so that I can access my account."
        result = generator.validate_story(story)
        
        assert result['success'] == True
        assert result['validation_result']['basic_validation']['is_valid'] == True
        assert result['validation_result']['ai_validation'] is None
    
    def test_error_handling(self):
        """Test error handling in story generation."""
        from generators.user_story_generator_refactored import UserStoryGeneratorRefactored
        from providers.openai_provider import MockAIProvider
        
        # Create failing AI provider
        class FailingAIProvider(MockAIProvider):
            def generate_structured_response(self, prompt, schema=None):
                raise Exception("AI service failure")
        
        failing_provider = FailingAIProvider()
        generator = UserStoryGeneratorRefactored(ai_provider=failing_provider)
        
        # Should handle AI failures gracefully
        result = generator.generate_user_story("Test requirements")
        assert result['success'] == False
        assert 'AI service failure' in result['error']
        
        result = generator.enhance_existing_story("Test story")
        assert result['success'] == False
        assert 'AI service failure' in result['error']
        
        result = generator.generate_epic_breakdown("Test epic")
        assert result['success'] == False
        assert 'AI service failure' in result['error']
    
    def test_template_formatting_edge_cases(self):
        """Test template formatting with edge cases."""
        from generators.user_story_generator_refactored import UserStoryGeneratorRefactored
        from providers.openai_provider import MockAIProvider
        
        # Mock responses with missing fields
        mock_responses = {
            "structured": {
                "user_type": "customer",
                # Missing other fields to test defaults
            }
        }
        
        mock_provider = MockAIProvider(mock_responses)
        generator = UserStoryGeneratorRefactored(ai_provider=mock_provider)
        
        result = generator.generate_user_story("Test requirements")
        assert result['success'] == True
        assert result['story'] is not None
        
        # Should use defaults for missing fields
        assert 'customer' in result['story']
        assert 'perform an action' in result['story']
        assert 'achieve a goal' in result['story']
    
    def test_provider_status(self):
        """Test provider status functionality."""
        from generators.user_story_generator_refactored import UserStoryGeneratorRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_provider = MockAIProvider()
        generator = UserStoryGeneratorRefactored(ai_provider=mock_provider)
        
        status = generator.get_provider_status()
        assert "provider_config" in status
        assert status["is_available"] == True
        assert status["generator_ready"] == True
        assert "available_templates" in status
        assert status["provider_config"]["provider"] == "mock"
        
        # Check available templates
        templates = status["available_templates"]
        assert 'basic' in templates
        assert 'detailed' in templates
        assert 'acceptance' in templates
    
    def test_comprehensive_workflow(self):
        """Test a comprehensive user story generation workflow."""
        from generators.user_story_generator_refactored import UserStoryGeneratorRefactored
        from providers.openai_provider import MockAIProvider
        
        # Setup comprehensive mock responses
        mock_responses = {
            "structured": {
                "user_type": "e-commerce customer",
                "functionality": "search for products by category and price",
                "benefit": "find relevant items quickly and efficiently",
                "action": "filter and browse",
                "object": "product catalog",
                "outcome": "discover suitable products",
                "additional_benefit": "save time and make informed purchases",
                "acceptance_criteria": [
                    "Can filter by category",
                    "Can set price range",
                    "Results update in real-time",
                    "Can sort by relevance"
                ],
                "enhanced_story": "As an e-commerce customer, I want to search for products using advanced filters including category, price range, brand, and ratings so that I can quickly find exactly what I'm looking for without browsing through irrelevant items.",
                "improvements": [
                    "Added specific filter types",
                    "Emphasized efficiency",
                    "Clarified user intent"
                ],
                "edge_cases": [
                    "No results found",
                    "Network connectivity issues",
                    "Invalid price range"
                ],
                "dependencies": [
                    "Product database",
                    "Search service",
                    "Filter API"
                ],
                "effort_estimate": 8,
                "quality_score": 92,
                "clarity_score": 88,
                "completeness_score": 95,
                "suggestions": [
                    "Consider mobile responsiveness",
                    "Add analytics tracking"
                ],
                "strengths": [
                    "Clear user persona",
                    "Specific functionality",
                    "Measurable benefit"
                ]
            }
        }
        
        mock_provider = MockAIProvider(mock_responses)
        generator = UserStoryGeneratorRefactored(ai_provider=mock_provider)
        
        # Step 1: Generate initial story
        requirements = "Customers need to search for products efficiently in an e-commerce platform"
        story_result = generator.generate_user_story(requirements, 'acceptance')
        
        assert story_result['success'] == True
        assert 'e-commerce customer' in story_result['story']
        assert len(story_result['acceptance_criteria']) == 4
        
        # Step 2: Enhance the story
        enhancement_result = generator.enhance_existing_story(story_result['story'])
        
        assert enhancement_result['success'] == True
        assert enhancement_result['enhanced_story'] is not None
        assert len(enhancement_result['improvements']) == 3
        assert len(enhancement_result['edge_cases']) == 3
        assert enhancement_result['effort_estimate'] == 8
        
        # Step 3: Validate the enhanced story
        validation_result = generator.validate_story(enhancement_result['enhanced_story'])
        
        assert validation_result['success'] == True
        assert validation_result['validation_result']['is_valid'] == True
        assert validation_result['validation_result']['overall_score'] > 85
        
        # Step 4: Generate a story suite
        related_requirements = [
            requirements,
            "Users want to save favorite products for later",
            "Customers need to compare products side by side"
        ]
        
        suite_result = generator.generate_story_suite(related_requirements)
        
        assert suite_result['success'] == True
        assert suite_result['total_requirements'] == 3
        assert suite_result['successful_stories'] == 3
        
        # Verify AI provider was used multiple times
        assert mock_provider.call_count >= 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
