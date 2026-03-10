"""Validation utilities for the Smart Backlog Assistant."""

import os
from typing import Any, Dict, List, Optional


class InputValidator:
    """Validates input data and configurations."""

    @staticmethod
    def validate_file_exists(file_path: str) -> bool:
        """Check if a file exists and is readable."""
        return os.path.isfile(file_path) and os.access(file_path, os.R_OK)

    @staticmethod
    def validate_json_structure(
        data: Dict[str, Any], required_fields: List[str]
    ) -> bool:
        """Validate that JSON data contains required fields."""
        return all(field in data for field in required_fields)

    @staticmethod
    def validate_backlog_item(item: Dict[str, Any]) -> bool:
        """Validate a backlog item structure."""
        required_fields = ["title", "description"]
        optional_fields = ["priority", "status", "assignee", "tags", "story_points"]

        # Check required fields
        if not InputValidator.validate_json_structure(item, required_fields):
            return False

        # Validate priority if present
        if "priority" in item:
            valid_priorities = ["high", "medium", "low", "critical"]
            if item["priority"].lower() not in valid_priorities:
                return False

        # Validate status if present
        if "status" in item:
            valid_statuses = ["todo", "in_progress", "done", "blocked"]
            if item["status"].lower() not in valid_statuses:
                return False

        return True

    @staticmethod
    def validate_api_key(api_key: Optional[str]) -> bool:
        """Validate that an API key is present and non-empty."""
        return api_key is not None and len(api_key.strip()) > 0

    @staticmethod
    def sanitize_text_input(text: str) -> str:
        """Sanitize text input to prevent issues."""
        if not isinstance(text, str):
            return ""

        # Remove null bytes and control characters
        sanitized = text.replace("\x00", "").replace("\r\n", "\n")

        # Limit length to prevent excessive processing
        max_length = 50000
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "... [truncated]"

        return sanitized.strip()


class OutputValidator:
    """Validates output data structures."""

    @staticmethod
    def validate_user_story(story: Dict[str, Any]) -> bool:
        """Validate a generated user story structure."""
        required_fields = ["title", "description", "acceptance_criteria"]

        if not InputValidator.validate_json_structure(story, required_fields):
            return False

        # Validate acceptance criteria is a list
        if not isinstance(story["acceptance_criteria"], list):
            return False

        # Check that acceptance criteria are non-empty
        if len(story["acceptance_criteria"]) == 0:
            return False

        return True

    @staticmethod
    def validate_priority_assessment(assessment: Dict[str, Any]) -> bool:
        """Validate a priority assessment structure."""
        required_fields = ["priority", "reasoning"]

        if not InputValidator.validate_json_structure(assessment, required_fields):
            return False

        # Validate priority value
        valid_priorities = ["high", "medium", "low", "critical"]
        if assessment["priority"].lower() not in valid_priorities:
            return False

        return True
