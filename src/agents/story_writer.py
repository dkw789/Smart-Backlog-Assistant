"""Story Writer Agent using pydantic-ai framework."""

import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from src.agents.context_models import StoryWriterContext
from src.generators.user_story_generator import UserStoryGenerator

load_dotenv()


class StoryGenerationResult(BaseModel):
    """Result from story generation tool."""

    stories: List[Dict[str, Any]]
    total_generated: int
    error_message: Optional[str] = None


class StoryEnhancementResult(BaseModel):
    """Result from story enhancement tool."""

    enhanced_story: Dict[str, Any]
    improvements_made: List[str]
    quality_score: float


# Create Story Writer Agent
# Get AI service from environment, default to Claude
default_service = os.getenv("DEFAULT_AI_SERVICE", "anthropic").lower()
model_name = "claude-3-sonnet-20240229" if default_service == "anthropic" else "gpt-4"
model_provider = (
    f"{default_service}:{model_name}"
    if default_service == "anthropic"
    else f"openai:{model_name}"
)

story_writer = Agent(
    model_provider,
    system_prompt="""You are a Senior Product Owner and Story Writer specializing in creating 
    well-structured user stories with clear acceptance criteria. Your role is to:
    
    1. Transform requirements into proper user story format: "As a [user], I want [functionality] so that [benefit]"
    2. Create comprehensive acceptance criteria using Given-When-Then format when appropriate
    3. Ensure stories are testable, valuable, and appropriately sized
    4. Add relevant tags and categorization
    5. Estimate effort and complexity
    6. Validate story quality and completeness
    
    Focus on creating stories that are independent, negotiable, valuable, estimable, small, and testable (INVEST principles).""",
)


@story_writer.tool
def generate_stories_from_requirements_tool(
    ctx: RunContext[StoryWriterContext], requirements: str
) -> StoryGenerationResult:
    """Tool wrapping user story generation from requirements - CORE FUNCTIONALITY"""
    try:
        generator = UserStoryGenerator()
        stories = generator.generate_stories_from_requirements(requirements)

        # Convert UserStory objects to dictionaries for serialization
        story_dicts = []
        for story in stories:
            story_dict = {
                "id": story.id,
                "title": story.title,
                "user_type": story.user_type,
                "functionality": story.functionality,
                "benefit": story.benefit,
                "narrative": story.to_narrative(),
                "acceptance_criteria": [
                    {
                        "id": ac.id,
                        "description": ac.description,
                        "is_completed": ac.is_completed,
                    }
                    for ac in story.acceptance_criteria
                ],
                "priority": (
                    story.priority.value
                    if hasattr(story.priority, "value")
                    else str(story.priority)
                ),
                "estimated_effort": (
                    story.estimated_effort.value
                    if hasattr(story.estimated_effort, "value")
                    else str(story.estimated_effort)
                ),
                "story_points": story.story_points,
                "tags": story.tags,
                "created_at": story.created_at.isoformat(),
            }
            story_dicts.append(story_dict)

        # Update context
        ctx.deps.generated_stories.extend(stories)

        return StoryGenerationResult(
            success=True, stories=story_dicts, total_generated=len(stories)
        )

    except Exception as e:
        return StoryGenerationResult(
            success=False,
            stories=[],
            total_generated=0,
            error_message=f"Story generation failed: {str(e)}",
        )


@story_writer.tool
def generate_stories_from_backlog_items_tool(
    ctx: RunContext[StoryWriterContext], backlog_items: List[Dict[str, Any]]
) -> StoryGenerationResult:
    """Tool wrapping user story generation from backlog items - REQUIRED FUNCTIONALITY"""
    try:
        generator = UserStoryGenerator()
        stories = generator.generate_stories_from_backlog_items(backlog_items)

        # Convert to dictionaries
        story_dicts = []
        for story in stories:
            story_dict = {
                "id": story.id,
                "title": story.title,
                "user_type": story.user_type,
                "functionality": story.functionality,
                "benefit": story.benefit,
                "narrative": story.to_narrative(),
                "acceptance_criteria": [
                    {
                        "id": ac.id,
                        "description": ac.description,
                        "is_completed": ac.is_completed,
                    }
                    for ac in story.acceptance_criteria
                ],
                "priority": (
                    story.priority.value
                    if hasattr(story.priority, "value")
                    else str(story.priority)
                ),
                "estimated_effort": (
                    story.estimated_effort.value
                    if hasattr(story.estimated_effort, "value")
                    else str(story.estimated_effort)
                ),
                "story_points": story.story_points,
                "tags": story.tags,
                "backlog_item_id": story.backlog_item_id,
            }
            story_dicts.append(story_dict)

        return StoryGenerationResult(
            success=True, stories=story_dicts, total_generated=len(stories)
        )

    except Exception as e:
        return StoryGenerationResult(
            success=False,
            stories=[],
            total_generated=0,
            error_message=f"Backlog story generation failed: {str(e)}",
        )


@story_writer.tool
def enhance_story_quality_tool(
    ctx: RunContext[StoryWriterContext], story_data: Dict[str, Any]
) -> StoryEnhancementResult:
    """Tool for enhancing story quality and completeness"""
    try:
        improvements_made = []
        enhanced_story = story_data.copy()
        quality_score = 0.0

        # Check and improve title
        if not story_data.get("title") or len(story_data.get("title", "")) < 5:
            enhanced_story["title"] = (
                f"User Story: {story_data.get('functionality', 'Feature')}"
            )
            improvements_made.append("Generated descriptive title")

        # Ensure proper user story format
        if not story_data.get("user_type"):
            enhanced_story["user_type"] = "user"
            improvements_made.append("Added default user type")

        if not story_data.get("functionality"):
            enhanced_story["functionality"] = "access system functionality"
            improvements_made.append("Added default functionality")

        if not story_data.get("benefit"):
            enhanced_story["benefit"] = "achieve my goals efficiently"
            improvements_made.append("Added default benefit")

        # Enhance acceptance criteria
        if (
            not story_data.get("acceptance_criteria")
            or len(story_data.get("acceptance_criteria", [])) == 0
        ):
            default_criteria = [
                {
                    "id": "AC-001",
                    "description": "User can access the functionality",
                    "is_completed": False,
                },
                {
                    "id": "AC-002",
                    "description": "System provides appropriate feedback",
                    "is_completed": False,
                },
                {
                    "id": "AC-003",
                    "description": "Error handling works correctly",
                    "is_completed": False,
                },
            ]
            enhanced_story["acceptance_criteria"] = default_criteria
            improvements_made.append("Added default acceptance criteria")

        # Add tags if missing
        if not story_data.get("tags"):
            functionality = story_data.get("functionality", "").lower()
            tags = []
            if "login" in functionality or "auth" in functionality:
                tags.append("authentication")
            if "ui" in functionality or "interface" in functionality:
                tags.append("frontend")
            if "data" in functionality or "database" in functionality:
                tags.append("backend")
            if not tags:
                tags.append("feature")
            enhanced_story["tags"] = tags
            improvements_made.append("Added relevant tags")

        # Set priority if missing
        if not story_data.get("priority"):
            enhanced_story["priority"] = "medium"
            improvements_made.append("Set default priority")

        # Set effort estimate if missing
        if not story_data.get("estimated_effort"):
            enhanced_story["estimated_effort"] = "medium"
            improvements_made.append("Set default effort estimate")

        # Calculate quality score
        score_factors = {
            "has_title": bool(enhanced_story.get("title")),
            "has_user_type": bool(enhanced_story.get("user_type")),
            "has_functionality": bool(enhanced_story.get("functionality")),
            "has_benefit": bool(enhanced_story.get("benefit")),
            "has_acceptance_criteria": len(
                enhanced_story.get("acceptance_criteria", [])
            )
            >= 3,
            "has_priority": bool(enhanced_story.get("priority")),
            "has_tags": len(enhanced_story.get("tags", [])) > 0,
            "title_length_good": len(enhanced_story.get("title", "")) >= 10,
        }

        quality_score = (sum(score_factors.values()) / len(score_factors)) * 100

        return StoryEnhancementResult(
            enhanced_story=enhanced_story,
            improvements_made=improvements_made,
            quality_score=quality_score,
        )

    except Exception as e:
        return StoryEnhancementResult(
            enhanced_story=story_data,
            improvements_made=[f"Enhancement failed: {str(e)}"],
            quality_score=0.0,
        )


@story_writer.tool
def validate_story_structure_tool(
    ctx: RunContext[StoryWriterContext], story_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Tool for validating user story structure and format"""
    try:
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "score": 0.0,
            "suggestions": [],
        }

        # Required fields validation
        required_fields = ["title", "user_type", "functionality", "benefit"]
        for field in required_fields:
            if not story_data.get(field):
                validation_result["errors"].append(f"Missing required field: {field}")
                validation_result["is_valid"] = False

        # Content quality checks
        if story_data.get("title") and len(story_data["title"]) < 5:
            validation_result["warnings"].append("Title is very short")
            validation_result["suggestions"].append("Consider a more descriptive title")

        if story_data.get("functionality") and len(story_data["functionality"]) < 10:
            validation_result["warnings"].append("Functionality description is brief")
            validation_result["suggestions"].append(
                "Add more detail about what the user wants to do"
            )

        if story_data.get("benefit") and len(story_data["benefit"]) < 10:
            validation_result["warnings"].append("Benefit description is brief")
            validation_result["suggestions"].append(
                "Explain the value this provides to the user"
            )

        # Acceptance criteria validation
        acceptance_criteria = story_data.get("acceptance_criteria", [])
        if len(acceptance_criteria) == 0:
            validation_result["errors"].append("No acceptance criteria defined")
            validation_result["is_valid"] = False
        elif len(acceptance_criteria) < 3:
            validation_result["warnings"].append(
                "Consider adding more acceptance criteria"
            )

        # Calculate validation score
        score = 100.0
        score -= len(validation_result["errors"]) * 20
        score -= len(validation_result["warnings"]) * 5
        validation_result["score"] = max(0.0, score)

        return validation_result

    except Exception as e:
        return {
            "is_valid": False,
            "errors": [f"Validation failed: {str(e)}"],
            "warnings": [],
            "score": 0.0,
            "suggestions": [],
        }


@story_writer.tool
def generate_acceptance_criteria_tool(
    ctx: RunContext[StoryWriterContext],
    story_title: str,
    functionality: str,
    format_style: str = "gherkin",
) -> List[Dict[str, Any]]:
    """Tool for generating comprehensive acceptance criteria"""
    try:
        criteria = []

        if format_style.lower() == "gherkin":
            # Generate Given-When-Then format criteria
            base_scenarios = [
                {
                    "id": "AC-001",
                    "description": f"Given a user wants to {functionality}, When they access the feature, Then they should be able to complete the action successfully",
                    "is_completed": False,
                },
                {
                    "id": "AC-002",
                    "description": f"Given the system is processing {functionality}, When an error occurs, Then appropriate error messages should be displayed",
                    "is_completed": False,
                },
                {
                    "id": "AC-003",
                    "description": f"Given a user has completed {functionality}, When they review the results, Then the outcome should meet their expectations",
                    "is_completed": False,
                },
            ]
        else:
            # Generate standard format criteria
            base_scenarios = [
                {
                    "id": "AC-001",
                    "description": f"User can successfully {functionality}",
                    "is_completed": False,
                },
                {
                    "id": "AC-002",
                    "description": "System provides clear feedback and status updates",
                    "is_completed": False,
                },
                {
                    "id": "AC-003",
                    "description": "Error handling works correctly with helpful messages",
                    "is_completed": False,
                },
                {
                    "id": "AC-004",
                    "description": "Performance meets acceptable standards",
                    "is_completed": False,
                },
            ]

        # Add specific criteria based on functionality keywords
        functionality_lower = functionality.lower()
        if "login" in functionality_lower or "auth" in functionality_lower:
            criteria.append(
                {
                    "id": f"AC-{len(base_scenarios) + 1:03d}",
                    "description": "Authentication credentials are validated securely",
                    "is_completed": False,
                }
            )

        if "data" in functionality_lower or "save" in functionality_lower:
            criteria.append(
                {
                    "id": f"AC-{len(base_scenarios) + 1:03d}",
                    "description": "Data is persisted correctly and can be retrieved",
                    "is_completed": False,
                }
            )

        if "ui" in functionality_lower or "interface" in functionality_lower:
            criteria.append(
                {
                    "id": f"AC-{len(base_scenarios) + 1:03d}",
                    "description": "User interface is intuitive and accessible",
                    "is_completed": False,
                }
            )

        criteria.extend(base_scenarios)
        return criteria

    except Exception as e:
        return [
            {
                "id": "AC-001",
                "description": f"Error generating criteria: {str(e)}",
                "is_completed": False,
            }
        ]
