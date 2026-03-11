"""Comprehensive tests for validators module to improve code coverage."""

import os
import tempfile
from typing import Dict, Any
import pytest

from src.utils.validators import InputValidator, OutputValidator


class TestInputValidator:
    """Comprehensive tests for InputValidator class."""
    
    def test_validate_file_exists_valid_file(self):
        """Test file validation with existing readable file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_path = f.name
        
        try:
            result = InputValidator.validate_file_exists(temp_path)
            assert result is True
        finally:
            os.unlink(temp_path)
    
    def test_validate_file_exists_non_existent_file(self):
        """Test file validation with non-existent file."""
        result = InputValidator.validate_file_exists("non_existent_file.txt")
        assert result is False
    
    def test_validate_file_exists_directory(self):
        """Test file validation with directory path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = InputValidator.validate_file_exists(temp_dir)
            assert result is False  # Should be False for directories
    
    def test_validate_json_structure_valid(self):
        """Test JSON structure validation with valid data."""
        data = {"name": "test", "value": 123, "items": [1, 2, 3]}
        required_fields = ["name", "value"]
        
        result = InputValidator.validate_json_structure(data, required_fields)
        assert result is True
    
    def test_validate_json_structure_missing_fields(self):
        """Test JSON structure validation with missing required fields."""
        data = {"name": "test"}
        required_fields = ["name", "value", "description"]
        
        result = InputValidator.validate_json_structure(data, required_fields)
        assert result is False
    
    def test_validate_json_structure_empty_data(self):
        """Test JSON structure validation with empty data."""
        data = {}
        required_fields = ["name", "value"]
        
        result = InputValidator.validate_json_structure(data, required_fields)
        assert result is False
    
    def test_validate_json_structure_empty_requirements(self):
        """Test JSON structure validation with no required fields."""
        data = {"name": "test", "value": 123}
        required_fields = []
        
        result = InputValidator.validate_json_structure(data, required_fields)
        assert result is True
    
    def test_validate_backlog_item_valid_minimal(self):
        """Test backlog item validation with minimal valid item."""
        item = {
            "title": "Test Task",
            "description": "A test task description"
        }
        
        result = InputValidator.validate_backlog_item(item)
        assert result is True
    
    def test_validate_backlog_item_valid_complete(self):
        """Test backlog item validation with complete valid item."""
        item = {
            "title": "Complete Task",
            "description": "A complete task description",
            "priority": "high",
            "status": "todo",
            "assignee": "John Doe",
            "tags": ["frontend", "urgent"],
            "story_points": 8
        }
        
        result = InputValidator.validate_backlog_item(item)
        assert result is True
    
    def test_validate_backlog_item_missing_title(self):
        """Test backlog item validation with missing title."""
        item = {
            "description": "A task description"
        }
        
        result = InputValidator.validate_backlog_item(item)
        assert result is False
    
    def test_validate_backlog_item_missing_description(self):
        """Test backlog item validation with missing description."""
        item = {
            "title": "Test Task"
        }
        
        result = InputValidator.validate_backlog_item(item)
        assert result is False
    
    def test_validate_backlog_item_invalid_priority(self):
        """Test backlog item validation with invalid priority."""
        item = {
            "title": "Test Task",
            "description": "A test task description",
            "priority": "invalid_priority"
        }
        
        result = InputValidator.validate_backlog_item(item)
        assert result is False
    
    def test_validate_backlog_item_valid_priorities(self):
        """Test backlog item validation with all valid priorities."""
        valid_priorities = ["high", "medium", "low", "critical", "HIGH", "Medium", "LOW"]
        
        for priority in valid_priorities:
            item = {
                "title": "Test Task",
                "description": "A test task description",
                "priority": priority
            }
            
            result = InputValidator.validate_backlog_item(item)
            assert result is True, f"Failed for priority: {priority}"
    
    def test_validate_backlog_item_invalid_status(self):
        """Test backlog item validation with invalid status."""
        item = {
            "title": "Test Task",
            "description": "A test task description",
            "status": "invalid_status"
        }
        
        result = InputValidator.validate_backlog_item(item)
        assert result is False
    
    def test_validate_backlog_item_valid_statuses(self):
        """Test backlog item validation with all valid statuses."""
        valid_statuses = ["todo", "in_progress", "done", "blocked", "TODO", "In_Progress", "DONE"]
        
        for status in valid_statuses:
            item = {
                "title": "Test Task",
                "description": "A test task description",
                "status": status
            }
            
            result = InputValidator.validate_backlog_item(item)
            assert result is True, f"Failed for status: {status}"
    
    def test_validate_api_key_valid(self):
        """Test API key validation with valid keys."""
        valid_keys = [
            "sk-1234567890abcdef",
            "valid_api_key",
            "  key_with_spaces  ",  # Should be stripped
            "a" * 100  # Long key
        ]
        
        for key in valid_keys:
            result = InputValidator.validate_api_key(key)
            assert result is True, f"Failed for key: {key}"
    
    def test_validate_api_key_invalid(self):
        """Test API key validation with invalid keys."""
        invalid_keys = [
            None,
            "",
            "   ",  # Only whitespace
            "\t\n"  # Only whitespace characters
        ]
        
        for key in invalid_keys:
            result = InputValidator.validate_api_key(key)
            assert result is False, f"Should fail for key: {key}"
    
    def test_sanitize_text_input_normal_text(self):
        """Test text sanitization with normal text."""
        text = "This is a normal text input."
        result = InputValidator.sanitize_text_input(text)
        assert result == text
    
    def test_sanitize_text_input_with_null_bytes(self):
        """Test text sanitization with null bytes."""
        text = "Text with\x00null bytes"
        result = InputValidator.sanitize_text_input(text)
        assert result == "Text withnull bytes"
    
    def test_sanitize_text_input_with_line_endings(self):
        """Test text sanitization with different line endings."""
        text = "Line 1\r\nLine 2\nLine 3"
        result = InputValidator.sanitize_text_input(text)
        assert result == "Line 1\nLine 2\nLine 3"
    
    def test_sanitize_text_input_long_text(self):
        """Test text sanitization with text exceeding max length."""
        long_text = "a" * 60000  # Exceeds 50000 limit
        result = InputValidator.sanitize_text_input(long_text)
        
        assert len(result) == 50000 + len("... [truncated]")
        assert result.endswith("... [truncated]")
        assert result.startswith("a" * 100)  # First part should be preserved
    
    def test_sanitize_text_input_with_whitespace(self):
        """Test text sanitization with leading/trailing whitespace."""
        text = "  \t  Text with whitespace  \n  "
        result = InputValidator.sanitize_text_input(text)
        assert result == "Text with whitespace"
    
    def test_sanitize_text_input_non_string(self):
        """Test text sanitization with non-string input."""
        inputs = [123, None, [], {}, True]
        
        for input_val in inputs:
            result = InputValidator.sanitize_text_input(input_val)
            assert result == "", f"Failed for input: {input_val}"
    
    def test_sanitize_text_input_empty_string(self):
        """Test text sanitization with empty string."""
        result = InputValidator.sanitize_text_input("")
        assert result == ""
    
    def test_sanitize_text_input_edge_cases(self):
        """Test text sanitization with edge cases."""
        # Text at exactly max length
        text_at_limit = "a" * 50000
        result = InputValidator.sanitize_text_input(text_at_limit)
        assert result == text_at_limit
        
        # Text just over limit
        text_over_limit = "a" * 50001
        result = InputValidator.sanitize_text_input(text_over_limit)
        assert result.endswith("... [truncated]")


class TestOutputValidator:
    """Comprehensive tests for OutputValidator class."""
    
    def test_validate_user_story_valid_minimal(self):
        """Test user story validation with minimal valid story."""
        story = {
            "title": "User Login",
            "description": "As a user, I want to login",
            "acceptance_criteria": ["User can enter credentials"]
        }
        
        result = OutputValidator.validate_user_story(story)
        assert result is True
    
    def test_validate_user_story_valid_complete(self):
        """Test user story validation with complete valid story."""
        story = {
            "title": "User Login Feature",
            "description": "As a user, I want to login to access my account",
            "acceptance_criteria": [
                "User can enter username and password",
                "System validates credentials",
                "User is redirected to dashboard on success"
            ],
            "priority": "high",
            "story_points": 5
        }
        
        result = OutputValidator.validate_user_story(story)
        assert result is True
    
    def test_validate_user_story_missing_title(self):
        """Test user story validation with missing title."""
        story = {
            "description": "As a user, I want to login",
            "acceptance_criteria": ["User can enter credentials"]
        }
        
        result = OutputValidator.validate_user_story(story)
        assert result is False
    
    def test_validate_user_story_missing_description(self):
        """Test user story validation with missing description."""
        story = {
            "title": "User Login",
            "acceptance_criteria": ["User can enter credentials"]
        }
        
        result = OutputValidator.validate_user_story(story)
        assert result is False
    
    def test_validate_user_story_missing_acceptance_criteria(self):
        """Test user story validation with missing acceptance criteria."""
        story = {
            "title": "User Login",
            "description": "As a user, I want to login"
        }
        
        result = OutputValidator.validate_user_story(story)
        assert result is False
    
    def test_validate_user_story_invalid_acceptance_criteria_type(self):
        """Test user story validation with invalid acceptance criteria type."""
        story = {
            "title": "User Login",
            "description": "As a user, I want to login",
            "acceptance_criteria": "User can enter credentials"  # Should be list
        }
        
        result = OutputValidator.validate_user_story(story)
        assert result is False
    
    def test_validate_user_story_empty_acceptance_criteria(self):
        """Test user story validation with empty acceptance criteria."""
        story = {
            "title": "User Login",
            "description": "As a user, I want to login",
            "acceptance_criteria": []  # Empty list
        }
        
        result = OutputValidator.validate_user_story(story)
        assert result is False
    
    def test_validate_priority_assessment_valid(self):
        """Test priority assessment validation with valid assessment."""
        assessment = {
            "priority": "high",
            "reasoning": "Critical feature for user experience"
        }
        
        result = OutputValidator.validate_priority_assessment(assessment)
        assert result is True
    
    def test_validate_priority_assessment_valid_all_priorities(self):
        """Test priority assessment validation with all valid priorities."""
        valid_priorities = ["high", "medium", "low", "critical", "HIGH", "Medium", "LOW"]
        
        for priority in valid_priorities:
            assessment = {
                "priority": priority,
                "reasoning": f"Reasoning for {priority} priority"
            }
            
            result = OutputValidator.validate_priority_assessment(assessment)
            assert result is True, f"Failed for priority: {priority}"
    
    def test_validate_priority_assessment_missing_priority(self):
        """Test priority assessment validation with missing priority."""
        assessment = {
            "reasoning": "Some reasoning"
        }
        
        result = OutputValidator.validate_priority_assessment(assessment)
        assert result is False
    
    def test_validate_priority_assessment_missing_reasoning(self):
        """Test priority assessment validation with missing reasoning."""
        assessment = {
            "priority": "high"
        }
        
        result = OutputValidator.validate_priority_assessment(assessment)
        assert result is False
    
    def test_validate_priority_assessment_invalid_priority(self):
        """Test priority assessment validation with invalid priority."""
        assessment = {
            "priority": "invalid_priority",
            "reasoning": "Some reasoning"
        }
        
        result = OutputValidator.validate_priority_assessment(assessment)
        assert result is False
    
    def test_validate_priority_assessment_empty_data(self):
        """Test priority assessment validation with empty data."""
        assessment = {}
        
        result = OutputValidator.validate_priority_assessment(assessment)
        assert result is False


class TestValidatorIntegration:
    """Integration tests for validator classes."""
    
    def test_validator_classes_exist(self):
        """Test that validator classes can be instantiated."""
        input_validator = InputValidator()
        output_validator = OutputValidator()
        
        assert input_validator is not None
        assert output_validator is not None
    
    def test_static_methods_callable(self):
        """Test that all validator methods are callable as static methods."""
        # InputValidator methods
        assert callable(InputValidator.validate_file_exists)
        assert callable(InputValidator.validate_json_structure)
        assert callable(InputValidator.validate_backlog_item)
        assert callable(InputValidator.validate_api_key)
        assert callable(InputValidator.sanitize_text_input)
        
        # OutputValidator methods
        assert callable(OutputValidator.validate_user_story)
        assert callable(OutputValidator.validate_priority_assessment)
    
    def test_cross_validator_usage(self):
        """Test using both validators together."""
        # Create a backlog item
        backlog_item = {
            "title": "User Authentication",
            "description": "Implement user login system",
            "priority": "high",
            "status": "todo"
        }
        
        # Validate with InputValidator
        backlog_valid = InputValidator.validate_backlog_item(backlog_item)
        assert backlog_valid is True
        
        # Create corresponding user story
        user_story = {
            "title": "User Login Story",
            "description": "As a user, I want to authenticate",
            "acceptance_criteria": ["User can login", "System validates credentials"]
        }
        
        # Validate with OutputValidator
        story_valid = OutputValidator.validate_user_story(user_story)
        assert story_valid is True
        
        # Create priority assessment
        priority_assessment = {
            "priority": "high",
            "reasoning": "Critical for security"
        }
        
        # Validate priority assessment
        priority_valid = OutputValidator.validate_priority_assessment(priority_assessment)
        assert priority_valid is True
    
    def test_sanitization_with_validation(self):
        """Test text sanitization combined with validation."""
        # Sanitize text input
        raw_text = "  \x00Malicious\r\ninput  "
        sanitized = InputValidator.sanitize_text_input(raw_text)
        
        # Use sanitized text in backlog item
        backlog_item = {
            "title": sanitized,
            "description": "Clean description"
        }
        
        # Validate the item
        result = InputValidator.validate_backlog_item(backlog_item)
        assert result is True
        assert backlog_item["title"] == "Malicious\ninput"
