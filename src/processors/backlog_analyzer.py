"""Backlog analysis module for the Smart Backlog Assistant."""

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from abc import ABC, abstractmethod
from typing import Protocol
from src.utils.validators import InputValidator
from src.processors.ai_processor import AIProcessor


@dataclass
class BacklogAnalysis:
    """Results from backlog analysis."""

    total_items: int
    items_by_priority: Dict[str, int]
    items_by_status: Dict[str, int]
    missing_information: List[str]
    recommendations: List[str]
    health_score: float
    analysis_success: bool
    error_message: Optional[str] = None


class AIProviderProtocol(Protocol):
    """Protocol for AI processing providers."""
    
    def analyze_backlog_items(self, backlog_data: List[Dict[str, Any]]) -> Any:
        """Analyze backlog items for improvements."""
        ...


class BacklogAnalyzer:
    """Analyzes backlog health and provides improvement recommendations with provider injection."""

    def __init__(self, ai_provider: AIProviderProtocol = None):
        self.logger = logging.getLogger(__name__)
        self.ai_provider = ai_provider or AIProcessor()
        self.logger.info(f"BacklogAnalyzer initialized with provider: {type(self.ai_provider).__name__}")

    def analyze_backlog_data(
        self, backlog_data: List[Dict[str, Any]]
    ) -> BacklogAnalysis:
        """Analyze backlog items and provide recommendations."""
        try:
            if not backlog_data:
                return BacklogAnalysis(
                    total_items=0,
                    items_by_priority={},
                    items_by_status={},
                    missing_information=["No backlog items provided"],
                    recommendations=["Add backlog items to analyze"],
                    health_score=0.0,
                    analysis_success=False,
                    error_message="Empty backlog data",
                )

            # Validate backlog items
            valid_items = []
            invalid_items = []

            for item in backlog_data:
                if InputValidator.validate_backlog_item(item):
                    valid_items.append(item)
                else:
                    invalid_items.append(item)

            # Analyze distribution
            priority_distribution = self._analyze_priority_distribution(valid_items)
            status_distribution = self._analyze_status_distribution(valid_items)

            # Identify missing information
            missing_info = self._identify_missing_information(valid_items)

            # Generate recommendations
            recommendations = self._generate_recommendations(
                valid_items, priority_distribution, status_distribution, missing_info
            )

            # Calculate health score
            health_score = self._calculate_health_score(
                valid_items, invalid_items, missing_info
            )

            return BacklogAnalysis(
                total_items=len(backlog_data),
                items_by_priority=priority_distribution,
                items_by_status=status_distribution,
                missing_information=missing_info,
                recommendations=recommendations,
                health_score=health_score,
                analysis_success=True,
            )

        except Exception as e:
            self.logger.error(f"Error analyzing backlog: {str(e)}")
            return BacklogAnalysis(
                total_items=0,
                items_by_priority={},
                items_by_status={},
                missing_information=[],
                recommendations=[],
                health_score=0.0,
                analysis_success=False,
                error_message=str(e),
            )

    def extract_backlog_from_json(self, json_content: str) -> List[Dict[str, Any]]:
        """Extract backlog items from JSON content."""
        try:
            data = json.loads(json_content)

            # Handle different JSON structures
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Look for common backlog keys
                for key in ["items", "backlog", "tasks", "stories", "issues"]:
                    if key in data and isinstance(data[key], list):
                        return data[key]
                # If no standard key found, treat the dict as a single item
                return [data]
            else:
                return []

        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON content: {str(e)}")
            return []

    def enhance_backlog_items(
        self, items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Enhance backlog items with additional structure and information."""
        enhanced_items = []

        for item in items:
            enhanced_item = item.copy()

            # Add missing fields with defaults
            if "priority" not in enhanced_item:
                enhanced_item["priority"] = self._infer_priority(enhanced_item)

            if "status" not in enhanced_item:
                enhanced_item["status"] = "todo"

            if "tags" not in enhanced_item:
                enhanced_item["tags"] = self._generate_tags(enhanced_item)

            if "story_points" not in enhanced_item:
                enhanced_item["story_points"] = self._estimate_story_points(
                    enhanced_item
                )

            if "acceptance_criteria" not in enhanced_item:
                enhanced_item["acceptance_criteria"] = (
                    self._generate_basic_acceptance_criteria(enhanced_item)
                )

            # Enhance description if too brief
            if len(enhanced_item.get("description", "")) < 50:
                enhanced_item["description"] = self._enhance_description(enhanced_item)

            enhanced_items.append(enhanced_item)

        return enhanced_items

    def _analyze_priority_distribution(
        self, items: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Analyze the distribution of priorities in backlog items."""
        distribution = {"high": 0, "medium": 0, "low": 0, "not_set": 0}

        for item in items:
            priority = item.get("priority", "").lower()
            if priority in distribution:
                distribution[priority] += 1
            else:
                distribution["not_set"] += 1

        return distribution

    def _analyze_status_distribution(
        self, items: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Analyze the distribution of statuses in backlog items."""
        distribution = {
            "todo": 0,
            "in_progress": 0,
            "done": 0,
            "blocked": 0,
            "not_set": 0,
        }

        for item in items:
            status = item.get("status", "").lower()
            if status in distribution:
                distribution[status] += 1
            else:
                distribution["not_set"] += 1

        return distribution

    def _identify_missing_information(self, items: List[Dict[str, Any]]) -> List[str]:
        """Identify what information is missing from backlog items."""
        missing_info = []

        # Check for common missing fields
        fields_to_check = {
            "acceptance_criteria": "Acceptance criteria",
            "story_points": "Story point estimates",
            "assignee": "Assignee information",
            "tags": "Tags for categorization",
            "due_date": "Due dates",
            "dependencies": "Dependencies",
        }

        for field, description in fields_to_check.items():
            missing_count = sum(
                1 for item in items if field not in item or not item[field]
            )
            if missing_count > len(items) * 0.5:  # More than 50% missing
                missing_info.append(
                    f"{description} missing from {missing_count}/{len(items)} items"
                )

        # Check for brief descriptions
        brief_descriptions = sum(
            1 for item in items if len(item.get("description", "")) < 50
        )
        if brief_descriptions > 0:
            missing_info.append(
                f"Brief descriptions in {brief_descriptions}/{len(items)} items"
            )

        return missing_info

    def _generate_recommendations(
        self,
        items: List[Dict[str, Any]],
        priority_dist: Dict[str, int],
        status_dist: Dict[str, int],
        missing_info: List[str],
    ) -> List[str]:
        """Generate recommendations for backlog improvement."""
        recommendations = []

        # Priority distribution recommendations
        total_items = len(items)
        if total_items > 0:
            high_priority_ratio = priority_dist.get("high", 0) / total_items
            if high_priority_ratio > 0.5:
                recommendations.append(
                    "Too many high-priority items. Consider re-prioritizing some items to medium or low."
                )
            elif high_priority_ratio < 0.1:
                recommendations.append(
                    "Very few high-priority items. Ensure critical work is properly prioritized."
                )

        # Status distribution recommendations
        if status_dist.get("in_progress", 0) > 5:
            recommendations.append(
                "Many items in progress. Consider limiting WIP to improve focus."
            )

        if status_dist.get("blocked", 0) > 0:
            recommendations.append(
                "Blocked items found. Review and resolve blockers to maintain flow."
            )

        # Missing information recommendations
        if missing_info:
            recommendations.append(
                "Add missing information to improve backlog quality:"
            )
            recommendations.extend([f"  - {info}" for info in missing_info[:3]])

        # General recommendations
        if total_items < 5:
            recommendations.append(
                "Consider adding more items to maintain a healthy backlog size."
            )
        elif total_items > 50:
            recommendations.append(
                "Large backlog detected. Consider archiving or removing low-priority items."
            )

        return recommendations

    def _calculate_health_score(
        self,
        valid_items: List[Dict[str, Any]],
        invalid_items: List[Dict[str, Any]],
        missing_info: List[str],
    ) -> float:
        """Calculate a health score for the backlog (0-100)."""
        if not valid_items and not invalid_items:
            return 0.0

        total_items = len(valid_items) + len(invalid_items)

        # Base score from valid items ratio
        validity_score = (len(valid_items) / total_items) * 40

        # Score from completeness (fewer missing info = higher score)
        completeness_score = max(0, 30 - len(missing_info) * 5)

        # Score from having reasonable distribution
        priority_balance_score = 15
        if valid_items:
            high_ratio = sum(
                1 for item in valid_items if item.get("priority") == "high"
            ) / len(valid_items)
            if 0.1 <= high_ratio <= 0.3:  # Good balance
                priority_balance_score = 15
            else:
                priority_balance_score = 5

        # Score from having descriptions
        description_score = 15
        if valid_items:
            good_descriptions = sum(
                1 for item in valid_items if len(item.get("description", "")) >= 50
            )
            description_score = (good_descriptions / len(valid_items)) * 15

        total_score = (
            validity_score
            + completeness_score
            + priority_balance_score
            + description_score
        )
        return min(100, max(0, total_score))

    def _infer_priority(self, item: Dict[str, Any]) -> str:
        """Infer priority from item content."""
        text = f"{item.get('title', '')} {item.get('description', '')}".lower()

        if any(
            keyword in text for keyword in ["critical", "urgent", "blocker", "security"]
        ):
            return "high"
        elif any(keyword in text for keyword in ["important", "needed", "required"]):
            return "medium"
        else:
            return "low"

    def _generate_tags(self, item: Dict[str, Any]) -> List[str]:
        """Generate tags based on item content."""
        text = f"{item.get('title', '')} {item.get('description', '')}".lower()
        tags = []

        tag_keywords = {
            "frontend": ["ui", "frontend", "interface", "react", "vue", "angular"],
            "backend": ["api", "backend", "server", "database", "service"],
            "bug": ["bug", "fix", "error", "issue"],
            "feature": ["feature", "new", "add", "implement"],
            "performance": ["performance", "optimize", "speed", "slow"],
            "security": ["security", "auth", "permission", "vulnerability"],
        }

        for tag, keywords in tag_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(tag)

        return tags[:3]  # Limit to 3 tags

    def _estimate_story_points(self, item: Dict[str, Any]) -> int:
        """Estimate story points based on description length and complexity."""
        description = item.get("description", "")
        title = item.get("title", "")

        # Simple heuristic based on content
        content_length = len(description) + len(title)

        if content_length < 100:
            return 1
        elif content_length < 300:
            return 3
        elif content_length < 500:
            return 5
        else:
            return 8

    def _generate_basic_acceptance_criteria(self, item: Dict[str, Any]) -> List[str]:
        """Generate basic acceptance criteria for an item."""
        criteria = []

        # Generic criteria based on item type
        if "bug" in item.get("tags", []):
            criteria = [
                "Issue is reproduced and root cause identified",
                "Fix is implemented and tested",
                "No regression in existing functionality",
            ]
        elif "feature" in item.get("tags", []):
            criteria = [
                "Feature requirements are clearly defined",
                "Implementation meets design specifications",
                "Feature is tested and working as expected",
            ]
        else:
            criteria = [
                "Requirements are clearly understood",
                "Implementation is complete and tested",
                "Stakeholder acceptance is obtained",
            ]

        return criteria

    def _enhance_description(self, item: Dict[str, Any]) -> str:
        """Enhance a brief description with more detail."""
        original = item.get("description", "")
        title = item.get("title", "")

        if len(original) < 50:
            enhanced = f"{original}\n\nAdditional context needed:\n"
            enhanced += "- What is the specific problem or need?\n"
            enhanced += "- What should the solution accomplish?\n"
            enhanced += "- Are there any constraints or requirements?"
            return enhanced

        return original
