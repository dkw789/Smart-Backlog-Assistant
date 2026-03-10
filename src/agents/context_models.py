"""Context models for pydantic-ai agents in the Smart Backlog Assistant."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from src.models.backlog_models import UserStory
from src.models.base_models import AgentRole


class BaseAgentContext(BaseModel):
    """Base context for all agents."""

    session_id: str = Field(description="Unique session identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = Field(default=None, description="User identifier")
    project_context: Dict[str, Any] = Field(default_factory=dict)


class DocumentAnalystContext(BaseAgentContext):
    """Context for Document Analyst Agent."""

    current_document: Optional[str] = Field(
        default=None, description="Currently processing document"
    )
    document_type: Optional[str] = Field(
        default=None, description="Type of document being processed"
    )
    extraction_mode: str = Field(default="comprehensive", description="Extraction mode")
    processed_documents: List[str] = Field(default_factory=list)


class RequirementsAnalystContext(BaseAgentContext):
    """Context for Requirements Analyst Agent."""

    requirements_source: Optional[str] = Field(
        default=None, description="Source of requirements"
    )
    analysis_depth: str = Field(default="detailed", description="Analysis depth level")
    extracted_requirements: List[Dict[str, Any]] = Field(default_factory=list)
    stakeholders: List[str] = Field(default_factory=list)


class StoryWriterContext(BaseAgentContext):
    """Context for Story Writer Agent."""

    story_format: str = Field(default="standard", description="User story format")
    acceptance_criteria_style: str = Field(default="gherkin", description="AC style")
    generated_stories: List[UserStory] = Field(default_factory=list)
    story_templates: Dict[str, str] = Field(default_factory=dict)


class PriorityManagerContext(BaseAgentContext):
    """Context for Priority Manager Agent."""

    assessment_criteria: List[str] = Field(default_factory=list)
    business_priorities: List[str] = Field(default_factory=list)
    technical_constraints: List[str] = Field(default_factory=list)
    capacity_info: Optional[Dict[str, Any]] = Field(default=None)


class BacklogCoachContext(BaseAgentContext):
    """Context for Backlog Coach Agent."""

    coaching_focus: str = Field(default="health", description="Focus area for coaching")
    team_maturity: str = Field(
        default="intermediate", description="Team maturity level"
    )
    improvement_areas: List[str] = Field(default_factory=list)
    metrics_tracking: Dict[str, Any] = Field(default_factory=dict)


class CoordinatorContext(BaseAgentContext):
    """Context for Coordinator Agent."""

    active_agents: List[AgentRole] = Field(default_factory=list)
    workflow_state: Dict[str, Any] = Field(default_factory=dict)
    coordination_strategy: str = Field(
        default="sequential", description="Agent coordination strategy"
    )
    results_aggregation: Dict[str, Any] = Field(default_factory=dict)
