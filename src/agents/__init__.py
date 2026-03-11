"""Agent module for Smart Backlog Assistant.

This module contains various AI agents for different tasks:
- backlog_coach: Provides backlog analysis and coaching
- coordinator: Coordinates multiple agents
- document_analyst: Analyzes documents for requirements
- priority_manager: Manages priority assessment
- story_writer: Generates user stories
- context_models: Context models for agents
- pydantic_ai_main: Pydantic AI integration
"""

# Import context models first (no circular dependencies)
from .context_models import (
    AgentContext,
    TaskContext,
    AgentResponse,
)

# Import agent classes (may have dependencies on models)
from .backlog_coach import BacklogCoach
from .coordinator import AgentCoordinator
from .document_analyst import DocumentAnalyst
from .priority_manager import PriorityManager
from .story_writer import StoryWriter

__all__ = [
    "AgentContext",
    "TaskContext",
    "AgentResponse",
    "BacklogCoach",
    "AgentCoordinator", 
    "DocumentAnalyst",
    "PriorityManager",
    "StoryWriter",
]