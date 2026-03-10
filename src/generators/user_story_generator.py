"""User story generation module for the Smart Backlog Assistant."""

import logging
from typing import Any, Dict, List, Optional

from src.models.backlog_models import AcceptanceCriterion, UserStory
from src.models.base_models import EffortEstimate, Priority
from abc import ABC, abstractmethod
from typing import Protocol
from src.processors.ai_processor import AIProcessor


class AIProviderProtocol(Protocol):
    """Protocol for AI processing providers."""
    
    def generate_user_stories(self, requirements: str) -> Any:
        """Generate user stories from requirements."""
        ...


class UserStoryGenerator:
    """Generates user stories from requirements and backlog items with provider injection."""

    def __init__(self, ai_provider: AIProviderProtocol = None):
        self.logger = logging.getLogger(__name__)
        self.ai_provider = ai_provider or AIProcessor()
        self.logger.info(f"UserStoryGenerator initialized with provider: {type(self.ai_provider).__name__}")

    def generate_stories_from_requirements(self, requirements: str) -> List[UserStory]:
        """Generate user stories from extracted requirements."""
        try:
            # Use AI to generate structured user stories
            ai_response = self.ai_provider.generate_user_stories(requirements)

            if not ai_response.success:
                self.logger.error(f"AI processing failed: {ai_response.error_message}")
                return self._generate_fallback_stories(requirements)

            # Parse AI response into structured user stories
            stories = self._parse_ai_response_to_stories(
                ai_response.content, requirements
            )

            # Validate and enhance stories
            validated_stories = []
            for story in stories:
                if self._validate_story_structure(story):
                    validated_stories.append(story)
                else:
                    # Try to fix common issues
                    fixed_story = self._fix_story_structure(story)
                    if fixed_story:
                        validated_stories.append(fixed_story)

            return validated_stories

        except Exception as e:
            self.logger.error(f"Error generating user stories: {str(e)}")
            return self._generate_fallback_stories(requirements)

    def generate_stories_from_backlog_items(
        self, backlog_items: List[Dict[str, Any]]
    ) -> List[UserStory]:
        """Generate or enhance user stories from existing backlog items."""
        stories = []

        for item in backlog_items:
            try:
                # Check if item already has good user story format
                if self._has_good_user_story_format(item):
                    story = self._convert_backlog_item_to_story(item)
                    stories.append(story)
                else:
                    # Generate new user story from backlog item
                    requirement_text = self._backlog_item_to_requirement_text(item)
                    generated_stories = self.generate_stories_from_requirements(
                        requirement_text
                    )
                    stories.extend(generated_stories)

            except Exception as e:
                self.logger.warning(f"Error processing backlog item: {str(e)}")
                continue

        return stories

    def enhance_existing_stories(
        self, stories: List[Dict[str, Any]]
    ) -> List[UserStory]:
        """Enhance existing user stories with better structure and details."""
        enhanced_stories = []

        for story_data in stories:
            try:
                # Convert to UserStory object and enhance
                story = self._dict_to_user_story(story_data)
                enhanced_story = self._enhance_story(story)
                enhanced_stories.append(enhanced_story)

            except Exception as e:
                self.logger.warning(f"Error enhancing story: {str(e)}")
                continue

        return enhanced_stories

    def _parse_ai_response_to_stories(
        self, ai_content: str, original_requirements: str
    ) -> List[UserStory]:
        """Parse AI response into structured UserStory objects."""
        stories = []

        # Split content by story markers
        story_sections = self._split_content_into_stories(ai_content)

        for section in story_sections:
            try:
                story = self._parse_story_section(section, original_requirements)
                if story:
                    stories.append(story)
            except Exception as e:
                self.logger.warning(f"Error parsing story section: {str(e)}")
                continue

        return stories

    def _split_content_into_stories(self, content: str) -> List[str]:
        """Split AI response content into individual story sections."""
        # Look for story markers - split on **Story Title** as that indicates a new story
        lines = content.split("\n")
        sections = []
        current_section = []

        for line in lines:
            line = line.strip()

            # Check if this line starts a new story
            if line.startswith("**Story Title"):
                # Save previous section if it exists
                if current_section:
                    sections.append("\n".join(current_section))
                # Start new section with this line
                current_section = [line]
            elif (
                current_section or line
            ):  # Only add non-empty lines or if we're in a section
                current_section.append(line)

        # Add the last section
        if current_section:
            sections.append("\n".join(current_section))

        return sections

    def _parse_story_section(
        self, section: str, original_requirements: str
    ) -> Optional[UserStory]:
        """Parse a single story section into a UserStory object."""
        lines = section.split("\n")

        story_data = {
            "title": "",
            "user_type": "user",
            "functionality": "",
            "benefit": "",
            "acceptance_criteria": [],
            "priority": "medium",
            "estimated_effort": "medium",
            "tags": [],
        }

        current_field = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Parse different fields
            if line.startswith("**Story Title"):
                story_data["title"] = (
                    line.replace("**Story Title**:", "")
                    .replace("**Story Title", "")
                    .strip()
                )
            elif line.startswith("**User Story"):
                user_story_text = (
                    line.replace("**User Story**:", "")
                    .replace("**User Story", "")
                    .strip()
                )
                parsed = self._parse_user_story_format(user_story_text)
                if parsed:
                    story_data.update(parsed)
            elif line.startswith("**Acceptance Criteria"):
                current_field = "acceptance_criteria"
            elif line.startswith("**Priority"):
                priority = (
                    line.replace("**Priority**:", "")
                    .replace("**Priority", "")
                    .strip()
                    .lower()
                )
                story_data["priority"] = (
                    priority
                    if priority in ["high", "medium", "low", "critical"]
                    else "medium"
                )
            elif line.startswith("**Estimated Effort"):
                effort = (
                    line.replace("**Estimated Effort**:", "")
                    .replace("**Estimated Effort", "")
                    .strip()
                    .lower()
                )
                story_data["estimated_effort"] = (
                    effort if effort in ["small", "medium", "large"] else "medium"
                )
            elif line.startswith("**Tags"):
                tags_text = line.replace("**Tags**:", "").replace("**Tags", "").strip()
                story_data["tags"] = [
                    tag.strip() for tag in tags_text.split(",") if tag.strip()
                ]
            elif current_field == "acceptance_criteria" and (
                line.startswith("- [ ]") or line.startswith("-")
            ):
                criteria = line.replace("- [ ]", "").replace("-", "").strip()
                if criteria:
                    story_data["acceptance_criteria"].append(criteria)

        # Validate required fields
        if not story_data["title"] or not story_data["functionality"]:
            return None

        # Convert string acceptance criteria to AcceptanceCriterion objects
        acceptance_criteria = []
        for i, criteria_text in enumerate(story_data["acceptance_criteria"]):
            acceptance_criteria.append(
                AcceptanceCriterion(id=f"ac_{i+1}", description=criteria_text)
            )

        # Ensure at least one acceptance criterion exists
        if not acceptance_criteria:
            acceptance_criteria.append(
                AcceptanceCriterion(id="ac_1", description="Feature works as expected")
            )

        # Convert string values to enum values
        from src.models.base_models import EffortEstimate, Priority

        priority_map = {
            "high": Priority.HIGH,
            "medium": Priority.MEDIUM,
            "low": Priority.LOW,
            "critical": Priority.CRITICAL,
        }
        effort_map = {
            "small": EffortEstimate.SMALL,
            "medium": EffortEstimate.MEDIUM,
            "large": EffortEstimate.LARGE,
        }

        return UserStory(
            title=story_data["title"],
            user_type=story_data["user_type"],
            functionality=story_data["functionality"],
            benefit=story_data["benefit"],
            acceptance_criteria=acceptance_criteria,
            priority=priority_map.get(story_data["priority"], Priority.MEDIUM),
            estimated_effort=effort_map.get(
                story_data["estimated_effort"], EffortEstimate.MEDIUM
            ),
            tags=story_data["tags"],
            original_requirement=(
                original_requirements[:200] if original_requirements else None
            ),
        )

    def _parse_user_story_format(
        self, user_story_text: str
    ) -> Optional[Dict[str, str]]:
        """Parse 'As a [user], I want [functionality] so that [benefit]' format."""
        import re

        # Try to match the standard user story format
        pattern = r"As an? (.*?), I want (.*?) so that (.*?)(?:\.|$)"
        match = re.search(pattern, user_story_text, re.IGNORECASE)

        if match:
            return {
                "user_type": match.group(1).strip(),
                "functionality": match.group(2).strip(),
                "benefit": match.group(3).strip(),
            }

        # Fallback: try to extract functionality at least
        if "I want" in user_story_text:
            parts = user_story_text.split("I want")
            if len(parts) > 1:
                functionality = parts[1].split("so that")[0].strip()
                benefit = (
                    parts[1].split("so that")[1].strip()
                    if "so that" in parts[1]
                    else ""
                )
                return {
                    "user_type": "user",
                    "functionality": functionality,
                    "benefit": benefit,
                }

        return None

    def _validate_story_structure(self, story: UserStory) -> bool:
        """Validate that a user story has proper structure."""
        valid_priorities = ["high", "medium", "low", "critical"]
        priority_value = (
            story.priority.value
            if hasattr(story.priority, "value")
            else str(story.priority)
        )
        return (
            bool(story.title)
            and bool(story.functionality)
            and len(story.acceptance_criteria) > 0
            and priority_value in valid_priorities
        )

    def _fix_story_structure(self, story: UserStory) -> Optional[UserStory]:
        """Try to fix common issues in story structure."""
        # Fix missing title
        if not story.title:
            story.title = (
                story.functionality[:50] + "..."
                if len(story.functionality) > 50
                else story.functionality
            )

        # Fix missing acceptance criteria
        if not story.acceptance_criteria:
            story.acceptance_criteria = self._generate_default_acceptance_criteria(
                story
            )

        # Fix invalid priority
        if story.priority not in ["high", "medium", "low", "critical"]:
            story.priority = "medium"

        # Validate again
        if self._validate_story_structure(story):
            return story

        return None

    def _generate_default_acceptance_criteria(self, story: UserStory) -> List[str]:
        """Generate default acceptance criteria for a story."""
        return [
            f"User can {story.functionality.lower()}",
            "Feature works as expected without errors",
            "User interface is intuitive and accessible",
        ]

    def _generate_fallback_stories(self, requirements: str) -> List[UserStory]:
        """Generate basic user stories when AI processing fails."""
        # Simple fallback: create one story per requirement line
        lines = [line.strip() for line in requirements.split("\n") if line.strip()]
        stories = []

        for i, line in enumerate(lines[:5]):  # Limit to 5 stories
            if len(line) > 20:  # Only process substantial lines
                story = UserStory(
                    title=f"Requirement {i+1}",
                    user_type="user",
                    functionality=line,
                    benefit="improve system functionality",
                    acceptance_criteria=[
                        AcceptanceCriterion(
                            id=f"ac_{i+1}_1",
                            description="Requirement is implemented correctly",
                        ),
                        AcceptanceCriterion(
                            id=f"ac_{i+1}_2", description="Feature works without errors"
                        ),
                        AcceptanceCriterion(
                            id=f"ac_{i+1}_3",
                            description="User can access the functionality",
                        ),
                    ],
                    priority=Priority.MEDIUM,
                    estimated_effort=EffortEstimate.MEDIUM,
                    tags=["generated"],
                    original_requirement=line,
                )
                stories.append(story)

        return stories

    def _has_good_user_story_format(self, item: Dict[str, Any]) -> bool:
        """Check if backlog item already has good user story format."""
        description = item.get("description", "").lower()
        return (
            "as a" in description
            and "i want" in description
            and item.get("acceptance_criteria")
            and len(item.get("acceptance_criteria", [])) > 0
        )

    def _convert_backlog_item_to_story(self, item: Dict[str, Any]) -> UserStory:
        """Convert a well-formatted backlog item to UserStory object."""
        return UserStory(
            title=item.get("title", "Untitled Story"),
            user_type=self._extract_user_type(item.get("description", "")),
            functionality=self._extract_functionality(item.get("description", "")),
            benefit=self._extract_benefit(item.get("description", "")),
            acceptance_criteria=item.get("acceptance_criteria", []),
            priority=item.get("priority", "medium").lower(),
            estimated_effort=self._map_story_points_to_effort(
                item.get("story_points", 3)
            ),
            tags=item.get("tags", []),
            original_requirement=item.get("description", ""),
        )

    def _backlog_item_to_requirement_text(self, item: Dict[str, Any]) -> str:
        """Convert backlog item to requirement text for AI processing."""
        title = item.get("title", "")
        description = item.get("description", "")
        return f"Title: {title}\nDescription: {description}"

    def _dict_to_user_story(self, story_data: Dict[str, Any]) -> UserStory:
        """Convert dictionary to UserStory object."""
        return UserStory(
            title=story_data.get("title", ""),
            user_type=story_data.get("user_type", "user"),
            functionality=story_data.get("functionality", ""),
            benefit=story_data.get("benefit", ""),
            acceptance_criteria=story_data.get("acceptance_criteria", []),
            priority=story_data.get("priority", "medium"),
            estimated_effort=story_data.get("estimated_effort", "medium"),
            tags=story_data.get("tags", []),
            original_requirement=story_data.get("original_requirement", ""),
        )

    def _enhance_story(self, story: UserStory) -> UserStory:
        """Enhance an existing story with better details."""
        # Enhance acceptance criteria if too few
        if len(story.acceptance_criteria) < 3:
            additional_criteria = self._generate_additional_acceptance_criteria(story)
            story.acceptance_criteria.extend(additional_criteria)

        # Add tags if missing
        if not story.tags:
            story.tags = self._generate_tags_from_story(story)

        return story

    def _generate_additional_acceptance_criteria(self, story: UserStory) -> List[str]:
        """Generate additional acceptance criteria for a story."""
        additional = []

        if "error handling" not in " ".join(story.acceptance_criteria).lower():
            additional.append("Error handling works correctly")

        if "validation" not in " ".join(story.acceptance_criteria).lower():
            additional.append("Input validation is implemented")

        if (
            "responsive" not in " ".join(story.acceptance_criteria).lower()
            and "ui" in story.functionality.lower()
        ):
            additional.append("Interface is responsive on different devices")

        return additional[:2]  # Limit to 2 additional criteria

    def _generate_tags_from_story(self, story: UserStory) -> List[str]:
        """Generate tags based on story content."""
        text = f"{story.title} {story.functionality} {story.benefit}".lower()
        tags = []

        tag_keywords = {
            "frontend": ["ui", "interface", "display", "view", "page"],
            "backend": ["api", "service", "database", "server"],
            "authentication": ["login", "auth", "user", "account"],
            "data": ["data", "information", "record", "store"],
            "integration": ["integrate", "connect", "sync", "import"],
        }

        for tag, keywords in tag_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(tag)

        return tags[:3]

    def _extract_user_type(self, description: str) -> str:
        """Extract user type from user story description."""
        import re

        match = re.search(r"as an? (.*?),", description, re.IGNORECASE)
        return match.group(1).strip() if match else "user"

    def _extract_functionality(self, description: str) -> str:
        """Extract functionality from user story description."""
        import re

        match = re.search(r"i want (.*?) so that", description, re.IGNORECASE)
        return match.group(1).strip() if match else description[:100]

    def _extract_benefit(self, description: str) -> str:
        """Extract benefit from user story description."""
        import re

        match = re.search(r"so that (.*?)(?:\.|$)", description, re.IGNORECASE)
        return match.group(1).strip() if match else "improve user experience"

    def _map_story_points_to_effort(self, story_points: int) -> str:
        """Map story points to effort estimation."""
        if story_points <= 2:
            return "small"
        elif story_points <= 5:
            return "medium"
        else:
            return "large"
