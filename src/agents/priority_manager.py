"""Priority Manager Agent using pydantic-ai framework."""

import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from src.agents.context_models import PriorityManagerContext
from src.generators.priority_engine import PriorityEngine

load_dotenv()


class PriorityAssessmentResult(BaseModel):
    """Result from priority assessment tool."""

    assessments: List[Dict[str, Any]]
    total_assessed: int
    error_message: Optional[str] = None


class SprintRecommendationResult(BaseModel):
    """Result from sprint recommendation tool."""

    recommended_items: List[Dict[str, Any]]
    total_effort: int
    capacity_utilization: float
    reasoning: str


# Create Priority Manager Agent
# Get AI service from environment, default to Claude
default_service = os.getenv("DEFAULT_AI_SERVICE", "anthropic").lower()

# Define model configurations
model_configs = {
    "anthropic": "claude-3-haiku-20240307",
    "openai": "gpt-4",
    "qwen": "qwen3.5:cloud"
}

def get_model_provider():
    """Get model provider based on service."""
    model_name = model_configs.get(default_service, "claude-3-haiku-20240307")
    
    if default_service == "anthropic":
        return f"anthropic:{model_name}"
    elif default_service == "openai":
        return f"openai:{model_name}"
    elif default_service == "qwen":
        return f"openai:{model_configs['qwen']}"  # Qwen uses OpenAI-compatible API
    else:
        return f"anthropic:{model_configs['anthropic']}"  # Default fallback

model_provider = get_model_provider()

priority_manager = Agent(
    model_provider,
    system_prompt="""You are a Senior Engineering Manager specializing in backlog prioritization 
    and capacity planning. Your role is to:
    
    1. Assess priority levels based on business impact, technical complexity, and strategic alignment
    2. Categorize backlog items (Feature, Bug, Enhancement, Technical Debt, Research)
    3. Estimate effort and complexity for proper sprint planning
    4. Consider dependencies, blockers, and resource constraints
    5. Recommend sprint compositions based on team capacity and priorities
    6. Balance business value delivery with technical sustainability
    
    Use data-driven approaches while considering team dynamics and strategic objectives.""",
)


@priority_manager.tool
def assess_item_priority_tool(
    ctx: RunContext[PriorityManagerContext], item_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Tool wrapping single item priority assessment - CORE FUNCTIONALITY"""
    try:
        engine = PriorityEngine()
        assessment = engine.assess_item_priority(item_data)

        # Convert PriorityAssessment to dictionary
        assessment_dict = {
            "priority": (
                assessment.priority.value
                if hasattr(assessment.priority, "value")
                else str(assessment.priority)
            ),
            "category": (
                assessment.category.value
                if hasattr(assessment.category, "value")
                else str(assessment.category)
            ),
            "business_impact": (
                assessment.business_impact.value
                if hasattr(assessment.business_impact, "value")
                else str(assessment.business_impact)
            ),
            "technical_complexity": (
                assessment.technical_complexity.value
                if hasattr(assessment.technical_complexity, "value")
                else str(assessment.technical_complexity)
            ),
            "effort_estimate": (
                assessment.effort_estimate.value
                if hasattr(assessment.effort_estimate, "value")
                else str(assessment.effort_estimate)
            ),
            "dependencies": assessment.dependencies,
            "blockers": assessment.blockers,
            "reasoning": assessment.reasoning,
            "confidence_score": assessment.confidence_score,
            "assessed_by": assessment.assessed_by,
            "assessment_date": assessment.assessment_date.isoformat(),
        }

        # Update context
        if "business_impact" not in ctx.deps.assessment_criteria:
            ctx.deps.assessment_criteria.extend(
                [
                    "business_impact",
                    "technical_complexity",
                    "effort_estimate",
                    "dependencies",
                ]
            )

        return assessment_dict

    except Exception as e:
        return {
            "error": f"Priority assessment failed: {str(e)}",
            "priority": "medium",
            "category": "feature",
            "reasoning": "Assessment failed, using default values",
        }


@priority_manager.tool
def assess_multiple_items_tool(
    ctx: RunContext[PriorityManagerContext], items: List[Dict[str, Any]]
) -> PriorityAssessmentResult:
    """Tool wrapping multiple items priority assessment - REQUIRED FUNCTIONALITY"""
    try:
        engine = PriorityEngine()
        assessments = engine.assess_multiple_items(items)

        # Convert assessments to dictionaries
        assessment_dicts = []
        for assessment in assessments:
            assessment_dict = {
                "priority": (
                    assessment.priority.value
                    if hasattr(assessment.priority, "value")
                    else str(assessment.priority)
                ),
                "category": (
                    assessment.category.value
                    if hasattr(assessment.category, "value")
                    else str(assessment.category)
                ),
                "business_impact": (
                    assessment.business_impact.value
                    if hasattr(assessment.business_impact, "value")
                    else str(assessment.business_impact)
                ),
                "technical_complexity": (
                    assessment.technical_complexity.value
                    if hasattr(assessment.technical_complexity, "value")
                    else str(assessment.technical_complexity)
                ),
                "effort_estimate": (
                    assessment.effort_estimate.value
                    if hasattr(assessment.effort_estimate, "value")
                    else str(assessment.effort_estimate)
                ),
                "dependencies": assessment.dependencies,
                "blockers": assessment.blockers,
                "reasoning": assessment.reasoning,
                "confidence_score": assessment.confidence_score,
            }
            assessment_dicts.append(assessment_dict)

        return PriorityAssessmentResult(
            success=True, assessments=assessment_dicts, total_assessed=len(assessments)
        )

    except Exception as e:
        return PriorityAssessmentResult(
            success=False,
            assessments=[],
            total_assessed=0,
            error_message=f"Multiple assessment failed: {str(e)}",
        )


@priority_manager.tool
def recommend_sprint_items_tool(
    ctx: RunContext[PriorityManagerContext],
    backlog_items: List[Dict[str, Any]],
    sprint_capacity: int,
) -> SprintRecommendationResult:
    """Tool wrapping sprint item recommendations - REQUIRED FUNCTIONALITY"""
    try:
        engine = PriorityEngine()
        recommended_items = engine.recommend_sprint_items(
            backlog_items, sprint_capacity
        )

        # Calculate metrics
        total_effort = sum(item.get("effort_points", 0) for item in recommended_items)
        capacity_utilization = (
            (total_effort / sprint_capacity * 100) if sprint_capacity > 0 else 0
        )

        # Generate reasoning
        high_priority_count = sum(
            1
            for item in recommended_items
            if item.get("assessment", {}).get("priority") == "high"
        )

        reasoning = f"Selected {len(recommended_items)} items totaling {total_effort} story points. "
        reasoning += f"Capacity utilization: {capacity_utilization:.1f}%. "
        reasoning += f"Includes {high_priority_count} high-priority items. "
        reasoning += "Selection balanced business value with team capacity constraints."

        # Update context
        ctx.deps.capacity_info = {
            "sprint_capacity": sprint_capacity,
            "planned_effort": total_effort,
            "utilization": capacity_utilization,
        }

        return SprintRecommendationResult(
            recommended_items=recommended_items,
            total_effort=total_effort,
            capacity_utilization=capacity_utilization,
            reasoning=reasoning,
        )

    except Exception as e:
        return SprintRecommendationResult(
            recommended_items=[],
            total_effort=0,
            capacity_utilization=0.0,
            reasoning=f"Sprint recommendation failed: {str(e)}",
        )


@priority_manager.tool
def categorize_backlog_tool(
    ctx: RunContext[PriorityManagerContext], items: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """Tool for categorizing backlog items by type"""
    try:
        engine = PriorityEngine()
        categorized = engine.categorize_backlog(items)

        # Convert enum keys to strings and ensure serializable format
        result = {}
        for category, item_list in categorized.items():
            category_key = (
                category.value if hasattr(category, "value") else str(category)
            )
            result[category_key] = item_list

        return result

    except Exception as e:
        return {"error": [{"message": f"Categorization failed: {str(e)}"}]}


@priority_manager.tool
def analyze_priority_distribution_tool(
    ctx: RunContext[PriorityManagerContext], items: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Tool for analyzing priority distribution across backlog"""
    try:
        priority_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "not_set": 0,
        }

        total_items = len(items)

        for item in items:
            priority = item.get("priority", "").lower()
            if priority in priority_counts:
                priority_counts[priority] += 1
            else:
                priority_counts["not_set"] += 1

        # Calculate percentages
        priority_percentages = {}
        for priority, count in priority_counts.items():
            priority_percentages[priority] = (
                (count / total_items * 100) if total_items > 0 else 0
            )

        # Generate insights
        insights = []
        if priority_percentages["critical"] > 20:
            insights.append(
                "High number of critical items may indicate planning issues"
            )
        if priority_percentages["not_set"] > 10:
            insights.append("Many items lack priority assignment")
        if priority_percentages["low"] > 50:
            insights.append("Backlog may need more high-value items")

        analysis = {
            "total_items": total_items,
            "priority_counts": priority_counts,
            "priority_percentages": priority_percentages,
            "insights": insights,
            "recommendations": [],
        }

        # Add recommendations
        if priority_percentages["not_set"] > 5:
            analysis["recommendations"].append(
                "Prioritize items without assigned priorities"
            )
        if priority_percentages["critical"] > 15:
            analysis["recommendations"].append(
                "Review critical items for realistic prioritization"
            )

        return analysis

    except Exception as e:
        return {"error": f"Priority distribution analysis failed: {str(e)}"}


@priority_manager.tool
def estimate_delivery_timeline_tool(
    ctx: RunContext[PriorityManagerContext],
    items: List[Dict[str, Any]],
    team_velocity: int,
    sprint_length_weeks: int = 2,
) -> Dict[str, Any]:
    """Tool for estimating delivery timeline based on priorities and velocity"""
    try:
        # Sort items by priority (critical > high > medium > low)
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}

        sorted_items = sorted(
            items,
            key=lambda x: priority_order.get(x.get("priority", "medium").lower(), 2),
        )

        timeline = {
            "sprints": [],
            "total_sprints_needed": 0,
            "total_weeks": 0,
            "items_by_sprint": {},
            "completion_forecast": {},
        }

        current_sprint = 1
        current_capacity = team_velocity
        current_sprint_items = []

        for item in sorted_items:
            story_points = item.get("story_points", 3)

            if story_points <= current_capacity:
                # Item fits in current sprint
                current_sprint_items.append(item)
                current_capacity -= story_points
            else:
                # Start new sprint
                if current_sprint_items:
                    timeline["items_by_sprint"][
                        f"Sprint {current_sprint}"
                    ] = current_sprint_items
                    timeline["sprints"].append(
                        {
                            "sprint_number": current_sprint,
                            "items_count": len(current_sprint_items),
                            "total_points": team_velocity - current_capacity,
                        }
                    )

                current_sprint += 1
                current_capacity = team_velocity - story_points
                current_sprint_items = [item]

        # Add final sprint if has items
        if current_sprint_items:
            timeline["items_by_sprint"][
                f"Sprint {current_sprint}"
            ] = current_sprint_items
            timeline["sprints"].append(
                {
                    "sprint_number": current_sprint,
                    "items_count": len(current_sprint_items),
                    "total_points": team_velocity - current_capacity,
                }
            )

        timeline["total_sprints_needed"] = current_sprint
        timeline["total_weeks"] = current_sprint * sprint_length_weeks

        # Generate completion forecast
        priority_completion = {}
        for sprint_info in timeline["sprints"]:
            sprint_items = timeline["items_by_sprint"][
                f"Sprint {sprint_info['sprint_number']}"
            ]
            for item in sprint_items:
                priority = item.get("priority", "medium").lower()
                if priority not in priority_completion:
                    priority_completion[priority] = sprint_info["sprint_number"]

        timeline["completion_forecast"] = priority_completion

        return timeline

    except Exception as e:
        return {"error": f"Timeline estimation failed: {str(e)}"}
