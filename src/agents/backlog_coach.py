"""Backlog Coach Agent using pydantic-ai framework."""

import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from src.agents.context_models import BacklogCoachContext
from src.processors.backlog_analyzer import BacklogAnalyzer

load_dotenv()


class BacklogHealthResult(BaseModel):
    """Result from backlog health analysis tool."""

    health_score: float
    analysis_summary: Dict[str, Any]
    recommendations: List[str]
    missing_information: List[str]


class ImprovementPlanResult(BaseModel):
    """Result from improvement plan generation tool."""

    improvement_areas: List[str]
    action_items: List[Dict[str, Any]]
    timeline: Dict[str, str]
    success_metrics: List[str]


# Create Backlog Coach Agent
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

backlog_coach = Agent(
    model_provider,
    system_prompt="""You are a Senior Agile Coach specializing in backlog management and team improvement. 
    Your role is to:
    
    1. Analyze backlog health and maturity using established metrics
    2. Identify gaps, inconsistencies, and improvement opportunities
    3. Provide actionable recommendations for backlog optimization
    4. Coach teams on best practices for user story writing and prioritization
    5. Track progress and suggest continuous improvement strategies
    6. Balance process improvement with practical team constraints
    
    Focus on sustainable improvements that enhance team productivity and product quality.""",
)


@backlog_coach.tool
def analyze_backlog_health_tool(
    ctx: RunContext[BacklogCoachContext], backlog_items: List[Dict[str, Any]]
) -> BacklogHealthResult:
    """Tool wrapping backlog health analysis - CORE FUNCTIONALITY"""
    try:
        analyzer = BacklogAnalyzer()
        analysis = analyzer.analyze_backlog_data(backlog_items)

        # Convert analysis to structured result
        analysis_summary = {
            "total_items": analysis.total_items,
            "items_by_priority": analysis.items_by_priority,
            "items_by_status": analysis.items_by_status,
            "health_score": analysis.health_score,
            "completion_rate": getattr(analysis, "completion_rate", None),
            "average_story_points": getattr(analysis, "average_story_points", None),
        }

        # Update context
        ctx.deps.metrics_tracking.update(
            {
                "last_health_score": analysis.health_score,
                "total_items_analyzed": analysis.total_items,
                "analysis_date": analysis.analysis_date.isoformat(),
            }
        )

        return BacklogHealthResult(
            health_score=analysis.health_score,
            analysis_summary=analysis_summary,
            recommendations=analysis.recommendations,
            missing_information=analysis.missing_information,
        )

    except Exception as e:
        return BacklogHealthResult(
            health_score=0.0,
            analysis_summary={"error": f"Analysis failed: {str(e)}"},
            recommendations=[f"Unable to analyze backlog: {str(e)}"],
            missing_information=["Analysis data unavailable due to error"],
        )


@backlog_coach.tool
def generate_improvement_recommendations_tool(
    ctx: RunContext[BacklogCoachContext],
    health_score: float,
    missing_information: List[str],
) -> List[str]:
    """Tool for generating targeted improvement recommendations"""
    try:
        recommendations = []

        # Score-based recommendations
        if health_score < 30:
            recommendations.extend(
                [
                    "🚨 URGENT: Backlog requires immediate attention",
                    "Schedule dedicated backlog refinement sessions",
                    "Focus on adding detailed descriptions to all items",
                    "Establish clear acceptance criteria for each story",
                    "Prioritize items based on business value",
                ]
            )
        elif health_score < 50:
            recommendations.extend(
                [
                    "⚠️ Backlog needs significant improvement",
                    "Implement regular backlog grooming sessions",
                    "Add missing story points to unestimated items",
                    "Review and update item priorities",
                    "Enhance user story formats",
                ]
            )
        elif health_score < 70:
            recommendations.extend(
                [
                    "📈 Good progress, focus on optimization",
                    "Refine acceptance criteria quality",
                    "Balance priority distribution",
                    "Add more detailed descriptions where needed",
                    "Consider breaking down large items",
                ]
            )
        else:
            recommendations.extend(
                [
                    "✅ Excellent backlog health!",
                    "Maintain current quality standards",
                    "Continue regular refinement practices",
                    "Monitor for any quality degradation",
                    "Share best practices with other teams",
                ]
            )

        # Missing information specific recommendations
        if "acceptance criteria" in str(missing_information).lower():
            recommendations.append(
                "🎯 Add comprehensive acceptance criteria to stories"
            )

        if "priority" in str(missing_information).lower():
            recommendations.append("🔢 Assign priorities to all backlog items")

        if "story points" in str(missing_information).lower():
            recommendations.append(
                "📊 Estimate story points for better sprint planning"
            )

        if "description" in str(missing_information).lower():
            recommendations.append("📝 Enhance item descriptions with more detail")

        # Update context
        ctx.deps.improvement_areas = [
            rec.split(":")[1].strip() if ":" in rec else rec for rec in recommendations
        ]

        return recommendations

    except Exception as e:
        return [f"Error generating recommendations: {str(e)}"]


@backlog_coach.tool
def create_improvement_plan_tool(
    ctx: RunContext[BacklogCoachContext],
    recommendations: List[str],
    team_capacity: str = "medium",
) -> ImprovementPlanResult:
    """Tool for creating structured improvement plan"""
    try:
        # Extract improvement areas from recommendations
        improvement_areas = []
        action_items = []

        for i, rec in enumerate(recommendations[:6]):  # Limit to top 6 recommendations
            # Clean recommendation text
            clean_rec = rec.split(":", 1)[-1].strip() if ":" in rec else rec
            improvement_areas.append(clean_rec)

            # Create action items based on recommendation type
            if "acceptance criteria" in rec.lower():
                action_items.append(
                    {
                        "id": f"AI-{i+1:03d}",
                        "title": "Improve Acceptance Criteria",
                        "description": "Review and enhance acceptance criteria for all user stories",
                        "priority": "high",
                        "effort": "2-3 sprints",
                        "owner": "Product Owner + Team",
                    }
                )
            elif "priority" in rec.lower():
                action_items.append(
                    {
                        "id": f"AI-{i+1:03d}",
                        "title": "Prioritize Backlog Items",
                        "description": "Assign business value-based priorities to all items",
                        "priority": "high",
                        "effort": "1 sprint",
                        "owner": "Product Owner",
                    }
                )
            elif "story points" in rec.lower():
                action_items.append(
                    {
                        "id": f"AI-{i+1:03d}",
                        "title": "Estimate Story Points",
                        "description": "Conduct estimation sessions for unestimated items",
                        "priority": "medium",
                        "effort": "1-2 sprints",
                        "owner": "Development Team",
                    }
                )
            elif "description" in rec.lower():
                action_items.append(
                    {
                        "id": f"AI-{i+1:03d}",
                        "title": "Enhance Descriptions",
                        "description": "Add detailed descriptions to brief backlog items",
                        "priority": "medium",
                        "effort": "2 sprints",
                        "owner": "Product Owner + BA",
                    }
                )
            else:
                action_items.append(
                    {
                        "id": f"AI-{i+1:03d}",
                        "title": "General Improvement",
                        "description": clean_rec,
                        "priority": "medium",
                        "effort": "1-2 sprints",
                        "owner": "Team",
                    }
                )

        # Create timeline based on team capacity
        if team_capacity.lower() == "high":
            timeline = {
                "phase_1": "Weeks 1-2: High priority items",
                "phase_2": "Weeks 3-4: Medium priority items",
                "phase_3": "Weeks 5-6: Optimization and monitoring",
            }
        elif team_capacity.lower() == "low":
            timeline = {
                "phase_1": "Weeks 1-4: Critical improvements only",
                "phase_2": "Weeks 5-8: Gradual implementation",
                "phase_3": "Weeks 9-12: Monitoring and adjustment",
            }
        else:  # medium
            timeline = {
                "phase_1": "Weeks 1-3: High priority improvements",
                "phase_2": "Weeks 4-6: Medium priority items",
                "phase_3": "Weeks 7-8: Review and optimization",
            }

        # Define success metrics
        success_metrics = [
            "Backlog health score improvement of 15+ points",
            "90%+ items have acceptance criteria",
            "95%+ items have assigned priorities",
            "80%+ items have story point estimates",
            "Team velocity stabilization",
            "Reduced time spent in backlog refinement",
        ]

        return ImprovementPlanResult(
            improvement_areas=improvement_areas,
            action_items=action_items,
            timeline=timeline,
            success_metrics=success_metrics,
        )

    except Exception as e:
        return ImprovementPlanResult(
            improvement_areas=[f"Error creating plan: {str(e)}"],
            action_items=[],
            timeline={"error": "Plan creation failed"},
            success_metrics=[],
        )


@backlog_coach.tool
def assess_team_maturity_tool(
    ctx: RunContext[BacklogCoachContext],
    backlog_quality_score: float,
    team_practices: Dict[str, Any],
) -> Dict[str, Any]:
    """Tool for assessing agile team maturity level"""
    try:
        maturity_score = 0
        maturity_factors = {}

        # Backlog quality factor (40% weight)
        backlog_factor = min(backlog_quality_score / 100, 1.0) * 40
        maturity_factors["backlog_quality"] = backlog_factor
        maturity_score += backlog_factor

        # Team practices factors (60% weight)
        practices = team_practices or {}

        # Regular refinement sessions (15% weight)
        if practices.get("regular_refinement", False):
            refinement_factor = 15
        else:
            refinement_factor = 0
        maturity_factors["refinement_practices"] = refinement_factor
        maturity_score += refinement_factor

        # Sprint planning quality (15% weight)
        planning_quality = practices.get("planning_quality", "basic")
        if planning_quality == "advanced":
            planning_factor = 15
        elif planning_quality == "intermediate":
            planning_factor = 10
        else:
            planning_factor = 5
        maturity_factors["planning_quality"] = planning_factor
        maturity_score += planning_factor

        # Retrospective implementation (15% weight)
        if practices.get("implements_retrospectives", False):
            retro_factor = 15
        else:
            retro_factor = 0
        maturity_factors["retrospective_practices"] = retro_factor
        maturity_score += retro_factor

        # Definition of Done clarity (15% weight)
        dod_clarity = practices.get("definition_of_done", "unclear")
        if dod_clarity == "clear":
            dod_factor = 15
        elif dod_clarity == "partial":
            dod_factor = 8
        else:
            dod_factor = 0
        maturity_factors["definition_of_done"] = dod_factor
        maturity_score += dod_factor

        # Determine maturity level
        if maturity_score >= 80:
            maturity_level = "Advanced"
            next_steps = [
                "Mentor other teams",
                "Experiment with advanced practices",
                "Focus on continuous optimization",
            ]
        elif maturity_score >= 60:
            maturity_level = "Intermediate"
            next_steps = [
                "Strengthen weak areas",
                "Implement advanced planning techniques",
                "Improve retrospective outcomes",
            ]
        elif maturity_score >= 40:
            maturity_level = "Developing"
            next_steps = [
                "Establish consistent practices",
                "Focus on backlog quality",
                "Implement regular ceremonies",
            ]
        else:
            maturity_level = "Beginning"
            next_steps = [
                "Start with basic agile practices",
                "Focus on backlog fundamentals",
                "Establish team ceremonies",
            ]

        # Update context
        ctx.deps.team_maturity = maturity_level.lower()

        assessment = {
            "maturity_level": maturity_level,
            "maturity_score": round(maturity_score, 1),
            "maturity_factors": maturity_factors,
            "strengths": [],
            "improvement_areas": [],
            "next_steps": next_steps,
        }

        # Identify strengths and improvement areas
        for factor, score in maturity_factors.items():
            if factor == "backlog_quality" and score >= 30:
                assessment["strengths"].append("Strong backlog management")
            elif factor == "refinement_practices" and score >= 12:
                assessment["strengths"].append("Good refinement practices")
            elif factor == "planning_quality" and score >= 12:
                assessment["strengths"].append("Effective sprint planning")
            elif factor == "retrospective_practices" and score >= 12:
                assessment["strengths"].append("Active retrospective implementation")
            elif factor == "definition_of_done" and score >= 12:
                assessment["strengths"].append("Clear definition of done")
            else:
                # Convert factor name to readable improvement area
                readable_factor = factor.replace("_", " ").title()
                assessment["improvement_areas"].append(readable_factor)

        return assessment

    except Exception as e:
        return {"error": f"Maturity assessment failed: {str(e)}"}


@backlog_coach.tool
def track_improvement_progress_tool(
    ctx: RunContext[BacklogCoachContext],
    current_metrics: Dict[str, Any],
    baseline_metrics: Dict[str, Any],
) -> Dict[str, Any]:
    """Tool for tracking backlog improvement progress over time"""
    try:
        progress_report = {
            "overall_progress": "unknown",
            "metric_changes": {},
            "achievements": [],
            "areas_needing_attention": [],
            "trend_analysis": {},
        }

        # Compare key metrics
        current_health = current_metrics.get("health_score", 0)
        baseline_health = baseline_metrics.get("health_score", 0)
        health_change = current_health - baseline_health

        progress_report["metric_changes"]["health_score"] = {
            "current": current_health,
            "baseline": baseline_health,
            "change": health_change,
            "change_percentage": (
                (health_change / baseline_health * 100) if baseline_health > 0 else 0
            ),
        }

        # Overall progress assessment
        if health_change >= 15:
            progress_report["overall_progress"] = "excellent"
            progress_report["achievements"].append(
                "Significant health score improvement"
            )
        elif health_change >= 5:
            progress_report["overall_progress"] = "good"
            progress_report["achievements"].append("Positive health score trend")
        elif health_change >= -5:
            progress_report["overall_progress"] = "stable"
        else:
            progress_report["overall_progress"] = "declining"
            progress_report["areas_needing_attention"].append("Health score declining")

        # Compare other metrics if available
        for metric in ["total_items", "completion_rate", "average_story_points"]:
            if metric in current_metrics and metric in baseline_metrics:
                current_val = current_metrics[metric]
                baseline_val = baseline_metrics[metric]

                if current_val is not None and baseline_val is not None:
                    change = current_val - baseline_val
                    change_pct = (
                        (change / baseline_val * 100) if baseline_val != 0 else 0
                    )

                    progress_report["metric_changes"][metric] = {
                        "current": current_val,
                        "baseline": baseline_val,
                        "change": change,
                        "change_percentage": change_pct,
                    }

        # Generate recommendations based on progress
        recommendations = []
        if progress_report["overall_progress"] == "excellent":
            recommendations.append("Maintain current improvement momentum")
            recommendations.append("Consider sharing best practices with other teams")
        elif progress_report["overall_progress"] == "declining":
            recommendations.append("Review and adjust improvement plan")
            recommendations.append("Identify and address root causes of decline")
            recommendations.append("Consider additional coaching support")

        progress_report["recommendations"] = recommendations

        # Update context tracking
        ctx.deps.metrics_tracking.update(
            {
                "progress_trend": progress_report["overall_progress"],
                "last_comparison_date": current_metrics.get("analysis_date", "unknown"),
            }
        )

        return progress_report

    except Exception as e:
        return {"error": f"Progress tracking failed: {str(e)}"}
