"""Priority assessment and categorization engine for the Smart Backlog Assistant."""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Tuple

from abc import ABC, abstractmethod
from typing import Protocol
from src.processors.ai_processor import AIProcessor


class Priority(Enum):
    """Priority levels for backlog items."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Category(Enum):
    """Categories for backlog items."""

    FEATURE = "feature"
    BUG = "bug"
    ENHANCEMENT = "enhancement"
    TECHNICAL_DEBT = "technical_debt"
    RESEARCH = "research"
    MAINTENANCE = "maintenance"


@dataclass
class PriorityAssessment:
    """Results from priority assessment."""

    priority: Priority
    category: Category
    business_impact: str
    technical_complexity: str
    effort_estimate: str
    dependencies: List[str]
    reasoning: str
    confidence_score: float


class AIProviderProtocol(Protocol):
    """Protocol for AI processing providers."""
    
    def assess_priority(self, item_description: str) -> Any:
        """Assess priority for a backlog item."""
        ...


class PriorityEngine:
    """Assesses priority and categorization for backlog items with provider injection."""

    def __init__(self, ai_provider: AIProviderProtocol = None):
        self.logger = logging.getLogger(__name__)
        self.ai_provider = ai_provider or AIProcessor()
        self.logger.info(f"PriorityEngine initialized with provider: {type(self.ai_provider).__name__}")

    def assess_item_priority(self, item: Dict[str, Any]) -> PriorityAssessment:
        """Assess priority for a single backlog item."""
        try:
            # Prepare item description for AI analysis
            item_description = self._format_item_for_analysis(item)

            # Get AI assessment
            ai_response = self.ai_provider.assess_priority(item_description)

            if ai_response.success:
                # Parse AI response
                assessment = self._parse_ai_priority_response(ai_response.content)

                # Apply rule-based validation and adjustments
                validated_assessment = self._validate_and_adjust_assessment(
                    assessment, item
                )

                return validated_assessment
            else:
                # Fallback to rule-based assessment
                return self._rule_based_priority_assessment(item)

        except Exception as e:
            self.logger.error(f"Error assessing item priority: {str(e)}")
            return self._default_priority_assessment(item)

    def assess_multiple_items(
        self, items: List[Dict[str, Any]]
    ) -> List[PriorityAssessment]:
        """Assess priority for multiple backlog items."""
        assessments = []

        for item in items:
            assessment = self.assess_item_priority(item)
            assessments.append(assessment)

        # Apply relative prioritization
        assessments = self._apply_relative_prioritization(assessments, items)

        return assessments

    def categorize_backlog(
        self, items: List[Dict[str, Any]]
    ) -> Dict[Category, List[Dict[str, Any]]]:
        """Categorize backlog items by type."""
        categorized = {category: [] for category in Category}

        for item in items:
            category = self._determine_category(item)
            categorized[category].append(item)

        return categorized

    def recommend_sprint_items(
        self, items: List[Dict[str, Any]], sprint_capacity: int = 40
    ) -> List[Dict[str, Any]]:
        """Recommend items for next sprint based on priority and capacity."""
        # Assess all items
        assessments = self.assess_multiple_items(items)

        # Sort by priority and business impact
        sorted_items = self._sort_by_priority_and_impact(items, assessments)

        # Select items that fit within sprint capacity
        selected_items = []
        total_effort = 0

        for item, assessment in sorted_items:
            effort = self._estimate_effort_points(assessment.effort_estimate)

            if total_effort + effort <= sprint_capacity:
                selected_items.append(
                    {"item": item, "assessment": assessment, "effort_points": effort}
                )
                total_effort += effort
            else:
                # Check if we can fit smaller items
                continue

        return selected_items

    def _format_item_for_analysis(self, item: Dict[str, Any]) -> str:
        """Format backlog item for AI analysis."""
        title = item.get("title", "No title")
        description = item.get("description", "No description")
        existing_priority = item.get("priority", "Not set")
        tags = item.get("tags", [])

        formatted = f"""
        Title: {title}
        Description: {description}
        Current Priority: {existing_priority}
        Tags: {', '.join(tags) if tags else 'None'}
        """

        return formatted.strip()

    def _parse_ai_priority_response(self, ai_content: str) -> PriorityAssessment:
        """Parse AI response into PriorityAssessment object."""
        lines = ai_content.split("\n")

        # Default values
        priority = Priority.MEDIUM
        category = Category.FEATURE
        business_impact = "medium"
        technical_complexity = "medium"
        effort_estimate = "medium"
        dependencies = []
        reasoning = ""

        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Parse different sections
            if "priority level" in line.lower():
                priority_text = self._extract_value_after_colon(line).lower()
                priority = self._text_to_priority(priority_text)

            elif "category" in line.lower():
                category_text = self._extract_value_after_colon(line).lower()
                category = self._text_to_category(category_text)

            elif "business impact" in line.lower():
                business_impact = self._extract_value_after_colon(line).lower()

            elif "technical complexity" in line.lower():
                technical_complexity = self._extract_value_after_colon(line).lower()

            elif "effort estimate" in line.lower():
                effort_estimate = self._extract_value_after_colon(line).lower()

            elif "dependencies" in line.lower():
                current_section = "dependencies"
                deps_text = self._extract_value_after_colon(line)
                if deps_text and deps_text.lower() != "none":
                    dependencies.extend([dep.strip() for dep in deps_text.split(",")])

            elif "reasoning" in line.lower():
                current_section = "reasoning"
                reasoning = self._extract_value_after_colon(line)

            elif current_section == "dependencies" and line.startswith("-"):
                dependencies.append(line[1:].strip())

            elif current_section == "reasoning":
                reasoning += " " + line

        return PriorityAssessment(
            priority=priority,
            category=category,
            business_impact=business_impact,
            technical_complexity=technical_complexity,
            effort_estimate=effort_estimate,
            dependencies=dependencies,
            reasoning=reasoning.strip(),
            confidence_score=0.8,  # AI-based assessment confidence
        )

    def _validate_and_adjust_assessment(
        self, assessment: PriorityAssessment, item: Dict[str, Any]
    ) -> PriorityAssessment:
        """Validate and adjust AI assessment using rules."""
        # Apply business rules
        adjusted_assessment = assessment

        # Security-related items should be high priority
        if self._is_security_related(item):
            if assessment.priority in [Priority.LOW, Priority.MEDIUM]:
                adjusted_assessment.priority = Priority.HIGH
                adjusted_assessment.reasoning += (
                    " [Adjusted: Security-related items prioritized]"
                )

        # Bug fixes should generally be higher priority than features
        if assessment.category == Category.BUG:
            if assessment.priority == Priority.LOW:
                adjusted_assessment.priority = Priority.MEDIUM
                adjusted_assessment.reasoning += " [Adjusted: Bug fixes prioritized]"

        # Critical path items should be high priority
        if self._is_critical_path(item):
            adjusted_assessment.priority = Priority.HIGH
            adjusted_assessment.reasoning += " [Adjusted: Critical path item]"

        return adjusted_assessment

    def _rule_based_priority_assessment(
        self, item: Dict[str, Any]
    ) -> PriorityAssessment:
        """Fallback rule-based priority assessment."""
        title = item.get("title", "").lower()
        description = item.get("description", "").lower()
        tags = [tag.lower() for tag in item.get("tags", [])]

        text = f"{title} {description}"

        # Determine priority
        priority = Priority.MEDIUM
        if any(
            keyword in text for keyword in ["critical", "urgent", "blocker", "security"]
        ):
            priority = Priority.HIGH
        elif any(keyword in text for keyword in ["bug", "fix", "error", "issue"]):
            priority = Priority.MEDIUM
        elif any(
            keyword in text for keyword in ["nice to have", "enhancement", "future"]
        ):
            priority = Priority.LOW

        # Determine category
        category = Category.FEATURE
        if "bug" in tags or any(keyword in text for keyword in ["bug", "fix", "error"]):
            category = Category.BUG
        elif any(keyword in text for keyword in ["enhance", "improve", "optimize"]):
            category = Category.ENHANCEMENT
        elif any(keyword in text for keyword in ["research", "investigate", "explore"]):
            category = Category.RESEARCH
        elif any(keyword in text for keyword in ["refactor", "cleanup", "debt"]):
            category = Category.TECHNICAL_DEBT

        # Estimate effort
        content_length = len(text)
        if content_length < 100:
            effort_estimate = "small"
        elif content_length < 300:
            effort_estimate = "medium"
        else:
            effort_estimate = "large"

        return PriorityAssessment(
            priority=priority,
            category=category,
            business_impact="medium",
            technical_complexity="medium",
            effort_estimate=effort_estimate,
            dependencies=[],
            reasoning="Rule-based assessment due to AI unavailability",
            confidence_score=0.6,
        )

    def _default_priority_assessment(self, item: Dict[str, Any]) -> PriorityAssessment:
        """Default assessment when all else fails."""
        return PriorityAssessment(
            priority=Priority.MEDIUM,
            category=Category.FEATURE,
            business_impact="medium",
            technical_complexity="medium",
            effort_estimate="medium",
            dependencies=[],
            reasoning="Default assessment due to processing error",
            confidence_score=0.3,
        )

    def _apply_relative_prioritization(
        self, assessments: List[PriorityAssessment], items: List[Dict[str, Any]]
    ) -> List[PriorityAssessment]:
        """Apply relative prioritization across all items."""
        # Count items by priority using string values to avoid enum identity issues
        priority_counts = {p.value: 0 for p in Priority}
        for assessment in assessments:
            priority_counts[assessment.priority.value] += 1

        total_items = len(assessments)

        # If too many high priority items, demote some to medium
        if priority_counts[Priority.HIGH.value] > total_items * 0.3:
            high_priority_assessments = [
                a for a in assessments if a.priority.value == Priority.HIGH.value
            ]
            # Sort by confidence and business impact, keep top 30%
            sorted_high = sorted(
                high_priority_assessments,
                key=lambda a: (a.confidence_score, a.business_impact == "high"),
                reverse=True,
            )

            keep_high = int(total_items * 0.3)
            for assessment in sorted_high[keep_high:]:
                assessment.priority = Priority.MEDIUM
                assessment.reasoning += " [Adjusted: Relative prioritization]"

        return assessments

    def _determine_category(self, item: Dict[str, Any]) -> Category:
        """Determine category for a backlog item."""
        title = item.get("title", "").lower()
        description = item.get("description", "").lower()
        tags = [tag.lower() for tag in item.get("tags", [])]

        text = f"{title} {description}"

        if "bug" in tags or any(
            keyword in text for keyword in ["bug", "fix", "error", "defect"]
        ):
            return Category.BUG
        elif any(
            keyword in text for keyword in ["enhance", "improve", "optimize", "upgrade"]
        ):
            return Category.ENHANCEMENT
        elif any(
            keyword in text
            for keyword in ["research", "investigate", "explore", "spike"]
        ):
            return Category.RESEARCH
        elif any(
            keyword in text
            for keyword in ["refactor", "cleanup", "debt", "technical debt"]
        ):
            return Category.TECHNICAL_DEBT
        elif any(keyword in text for keyword in ["maintain", "update", "patch"]):
            return Category.MAINTENANCE
        else:
            return Category.FEATURE

    def _sort_by_priority_and_impact(
        self, items: List[Dict[str, Any]], assessments: List[PriorityAssessment]
    ) -> List[Tuple[Dict[str, Any], PriorityAssessment]]:
        """Sort items by priority and business impact."""
        combined = list(zip(items, assessments))

        # Define priority order
        priority_order = {
            Priority.CRITICAL: 4,
            Priority.HIGH: 3,
            Priority.MEDIUM: 2,
            Priority.LOW: 1,
        }

        impact_order = {"high": 3, "medium": 2, "low": 1}

        return sorted(
            combined,
            key=lambda x: (
                priority_order.get(x[1].priority, 0),
                impact_order.get(x[1].business_impact, 0),
                x[1].confidence_score,
            ),
            reverse=True,
        )

    def _estimate_effort_points(self, effort_estimate: str) -> int:
        """Convert effort estimate to story points."""
        effort_mapping = {"small": 2, "medium": 5, "large": 8, "xl": 13}
        return effort_mapping.get(effort_estimate.lower(), 5)

    def _extract_value_after_colon(self, line: str) -> str:
        """Extract value after colon in a line."""
        if ":" in line:
            return line.split(":", 1)[1].strip()
        return line.strip()

    def _text_to_priority(self, text: str) -> Priority:
        """Convert text to Priority enum."""
        text = text.lower().strip()
        if "critical" in text:
            return Priority.CRITICAL
        elif "high" in text:
            return Priority.HIGH
        elif "low" in text:
            return Priority.LOW
        else:
            return Priority.MEDIUM

    def _text_to_category(self, text: str) -> Category:
        """Convert text to Category enum."""
        text = text.lower().strip()
        if "bug" in text:
            return Category.BUG
        elif "enhancement" in text:
            return Category.ENHANCEMENT
        elif "research" in text:
            return Category.RESEARCH
        elif "technical" in text or "debt" in text:
            return Category.TECHNICAL_DEBT
        elif "maintenance" in text:
            return Category.MAINTENANCE
        else:
            return Category.FEATURE

    def _is_security_related(self, item: Dict[str, Any]) -> bool:
        """Check if item is security-related."""
        text = f"{item.get('title', '')} {item.get('description', '')}".lower()
        security_keywords = [
            "security",
            "auth",
            "authentication",
            "authorization",
            "vulnerability",
            "encryption",
            "ssl",
            "https",
        ]
        return any(keyword in text for keyword in security_keywords)

    def _is_critical_path(self, item: Dict[str, Any]) -> bool:
        """Check if item is on critical path."""
        text = f"{item.get('title', '')} {item.get('description', '')}".lower()
        critical_keywords = ["critical", "blocker", "blocking", "urgent", "deadline"]
        return any(keyword in text for keyword in critical_keywords)
