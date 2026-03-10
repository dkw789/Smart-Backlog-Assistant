"""Coordinator Agent using pydantic-ai framework."""

import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from src.agents.context_models import CoordinatorContext

load_dotenv()


class WorkflowExecutionResult(BaseModel):
    """Result from workflow execution."""

    workflow_id: str
    completed_agents: List[str]
    results: Dict[str, Any]
    execution_time: float
    error_message: Optional[str] = None


class AgentCoordinationResult(BaseModel):
    """Result from agent coordination."""

    coordination_strategy: str
    agent_sequence: List[str]
    estimated_duration: float
    dependencies: Dict[str, List[str]]


# Create Coordinator Agent
# Get AI service from environment, default to Claude
default_service = os.getenv("DEFAULT_AI_SERVICE", "anthropic").lower()
model_name = "claude-3-sonnet-20240229" if default_service == "anthropic" else "gpt-4"
model_provider = (
    f"{default_service}:{model_name}"
    if default_service == "anthropic"
    else f"openai:{model_name}"
)

coordinator = Agent(
    model_provider,
    system_prompt="""You are the Master Coordinator for the Smart Backlog Assistant multi-agent system. 
    Your role is to:
    
    1. Orchestrate workflows across specialized agents (Document Analyst, Story Writer, Priority Manager, Backlog Coach)
    2. Manage agent dependencies and execution sequences
    3. Aggregate and synthesize results from multiple agents
    4. Handle error recovery and fallback strategies
    5. Optimize workflow efficiency and resource utilization
    6. Provide comprehensive reporting and insights
    
    You have access to all agent capabilities and coordinate their execution to deliver complete solutions.""",
)


@coordinator.tool
def execute_document_analysis_workflow_tool(
    ctx: RunContext[CoordinatorContext], file_path: str
) -> Dict[str, Any]:
    """Tool wrapping complete document analysis workflow - CORE FUNCTIONALITY"""
    try:
        from .context_models import DocumentAnalystContext
        from .document_analyst import document_analyst

        # Create context for document analyst
        doc_context = DocumentAnalystContext(
            session_id=ctx.deps.session_id, current_document=file_path
        )

        workflow_results = {
            "workflow_type": "document_analysis",
            "file_path": file_path,
            "steps_completed": [],
            "results": {},
            "success": True,
        }

        # Step 1: Extract document content
        extraction_result = document_analyst.run_sync(
            "Extract and analyze the document content", deps=doc_context
        )
        workflow_results["steps_completed"].append("content_extraction")
        workflow_results["results"]["content_extraction"] = str(extraction_result)

        # Step 2: Extract structured information
        if "meeting" in file_path.lower() or "notes" in file_path.lower():
            structure_result = document_analyst.run_sync(
                "Extract meeting notes structure from the content", deps=doc_context
            )
            workflow_results["steps_completed"].append("structure_extraction")
            workflow_results["results"]["structure_extraction"] = str(structure_result)

        # Step 3: Extract requirements
        requirements_result = document_analyst.run_sync(
            "Extract requirements from the document text", deps=doc_context
        )
        workflow_results["steps_completed"].append("requirements_extraction")
        workflow_results["results"]["requirements_extraction"] = str(
            requirements_result
        )

        # Update coordinator context
        ctx.deps.active_agents.append(AgentRole.BUSINESS_ANALYST)
        ctx.deps.workflow_state["document_analysis"] = "completed"

        return workflow_results

    except Exception as e:
        return {
            "workflow_type": "document_analysis",
            "success": False,
            "error": f"Document analysis workflow failed: {str(e)}",
            "steps_completed": [],
            "results": {},
        }


@coordinator.tool
def execute_story_generation_workflow_tool(
    ctx: RunContext[CoordinatorContext], requirements_text: str
) -> Dict[str, Any]:
    """Tool wrapping complete story generation workflow - REQUIRED FUNCTIONALITY"""
    try:
        from .context_models import StoryWriterContext
        from .story_writer import story_writer

        # Create context for story writer
        story_context = StoryWriterContext(
            session_id=ctx.deps.session_id, story_format="standard"
        )

        workflow_results = {
            "workflow_type": "story_generation",
            "input_requirements": (
                requirements_text[:200] + "..."
                if len(requirements_text) > 200
                else requirements_text
            ),
            "steps_completed": [],
            "results": {},
            "success": True,
        }

        # Step 1: Generate user stories
        generation_result = story_writer.run_sync(
            f"Generate user stories from these requirements: {requirements_text}",
            deps=story_context,
        )
        workflow_results["steps_completed"].append("story_generation")
        workflow_results["results"]["story_generation"] = str(generation_result)

        # Step 2: Enhance story quality
        enhancement_result = story_writer.run_sync(
            "Enhance the quality and completeness of the generated stories",
            deps=story_context,
        )
        workflow_results["steps_completed"].append("story_enhancement")
        workflow_results["results"]["story_enhancement"] = str(enhancement_result)

        # Step 3: Validate story structure
        validation_result = story_writer.run_sync(
            "Validate the structure and format of all generated stories",
            deps=story_context,
        )
        workflow_results["steps_completed"].append("story_validation")
        workflow_results["results"]["story_validation"] = str(validation_result)

        # Update coordinator context
        ctx.deps.active_agents.append(AgentRole.PRODUCT_OWNER)
        ctx.deps.workflow_state["story_generation"] = "completed"

        return workflow_results

    except Exception as e:
        return {
            "workflow_type": "story_generation",
            "success": False,
            "error": f"Story generation workflow failed: {str(e)}",
            "steps_completed": [],
            "results": {},
        }


@coordinator.tool
def execute_priority_assessment_workflow_tool(
    ctx: RunContext[CoordinatorContext], backlog_items: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Tool wrapping complete priority assessment workflow - REQUIRED FUNCTIONALITY"""
    try:
        from .context_models import PriorityManagerContext
        from .priority_manager import priority_manager

        # Create context for priority manager
        priority_context = PriorityManagerContext(
            session_id=ctx.deps.session_id,
            assessment_criteria=[
                "business_impact",
                "technical_complexity",
                "effort_estimate",
            ],
        )

        workflow_results = {
            "workflow_type": "priority_assessment",
            "items_count": len(backlog_items),
            "steps_completed": [],
            "results": {},
            "success": True,
        }

        # Step 1: Assess multiple items
        assessment_result = priority_manager.run_sync(
            f"Assess priorities for {len(backlog_items)} backlog items",
            deps=priority_context,
        )
        workflow_results["steps_completed"].append("priority_assessment")
        workflow_results["results"]["priority_assessment"] = str(assessment_result)

        # Step 2: Categorize backlog
        categorization_result = priority_manager.run_sync(
            "Categorize the backlog items by type and priority", deps=priority_context
        )
        workflow_results["steps_completed"].append("backlog_categorization")
        workflow_results["results"]["backlog_categorization"] = str(
            categorization_result
        )

        # Step 3: Analyze priority distribution
        distribution_result = priority_manager.run_sync(
            "Analyze the priority distribution across the backlog",
            deps=priority_context,
        )
        workflow_results["steps_completed"].append("priority_distribution")
        workflow_results["results"]["priority_distribution"] = str(distribution_result)

        # Update coordinator context
        ctx.deps.active_agents.append(AgentRole.ENGINEERING_MANAGER)
        ctx.deps.workflow_state["priority_assessment"] = "completed"

        return workflow_results

    except Exception as e:
        return {
            "workflow_type": "priority_assessment",
            "success": False,
            "error": f"Priority assessment workflow failed: {str(e)}",
            "steps_completed": [],
            "results": {},
        }


@coordinator.tool
def execute_backlog_coaching_workflow_tool(
    ctx: RunContext[CoordinatorContext], backlog_items: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Tool wrapping complete backlog coaching workflow - REQUIRED FUNCTIONALITY"""
    try:
        from .backlog_coach import backlog_coach
        from .context_models import BacklogCoachContext

        # Create context for backlog coach
        coach_context = BacklogCoachContext(
            session_id=ctx.deps.session_id, coaching_focus="health"
        )

        workflow_results = {
            "workflow_type": "backlog_coaching",
            "items_count": len(backlog_items),
            "steps_completed": [],
            "results": {},
            "success": True,
        }

        # Step 1: Analyze backlog health
        health_result = backlog_coach.run_sync(
            f"Analyze the health of {len(backlog_items)} backlog items",
            deps=coach_context,
        )
        workflow_results["steps_completed"].append("health_analysis")
        workflow_results["results"]["health_analysis"] = str(health_result)

        # Step 2: Generate improvement recommendations
        recommendations_result = backlog_coach.run_sync(
            "Generate targeted improvement recommendations based on the health analysis",
            deps=coach_context,
        )
        workflow_results["steps_completed"].append("improvement_recommendations")
        workflow_results["results"]["improvement_recommendations"] = str(
            recommendations_result
        )

        # Step 3: Create improvement plan
        plan_result = backlog_coach.run_sync(
            "Create a structured improvement plan with actionable items",
            deps=coach_context,
        )
        workflow_results["steps_completed"].append("improvement_plan")
        workflow_results["results"]["improvement_plan"] = str(plan_result)

        # Update coordinator context
        ctx.deps.active_agents.append(AgentRole.AGILE_COACH)
        ctx.deps.workflow_state["backlog_coaching"] = "completed"

        return workflow_results

    except Exception as e:
        return {
            "workflow_type": "backlog_coaching",
            "success": False,
            "error": f"Backlog coaching workflow failed: {str(e)}",
            "steps_completed": [],
            "results": {},
        }


@coordinator.tool
def execute_comprehensive_analysis_workflow_tool(
    ctx: RunContext[CoordinatorContext], input_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Tool wrapping comprehensive multi-agent analysis workflow - MASTER FUNCTIONALITY"""
    try:
        workflow_start = datetime.utcnow()

        comprehensive_results = {
            "workflow_type": "comprehensive_analysis",
            "input_summary": {
                "has_document": "file_path" in input_data,
                "has_backlog": "backlog_items" in input_data,
                "has_requirements": "requirements_text" in input_data,
            },
            "agent_results": {},
            "synthesis": {},
            "success": True,
            "execution_order": [],
        }

        # Step 1: Document Analysis (if document provided)
        if "file_path" in input_data:
            doc_result = coordinator.run_sync(
                f"Execute document analysis workflow for {input_data['file_path']}",
                deps=ctx.deps,
            )
            comprehensive_results["agent_results"]["document_analyst"] = doc_result
            comprehensive_results["execution_order"].append("document_analyst")

        # Step 2: Story Generation (if requirements available)
        requirements_text = input_data.get("requirements_text", "")
        if requirements_text:
            story_result = coordinator.run_sync(
                "Execute story generation workflow for requirements", deps=ctx.deps
            )
            comprehensive_results["agent_results"]["story_writer"] = story_result
            comprehensive_results["execution_order"].append("story_writer")

        # Step 3: Priority Assessment (if backlog items available)
        backlog_items = input_data.get("backlog_items", [])
        if backlog_items:
            priority_result = coordinator.run_sync(
                f"Execute priority assessment workflow for {len(backlog_items)} items",
                deps=ctx.deps,
            )
            comprehensive_results["agent_results"]["priority_manager"] = priority_result
            comprehensive_results["execution_order"].append("priority_manager")

            # Step 4: Backlog Coaching (follows priority assessment)
            coaching_result = coordinator.run_sync(
                f"Execute backlog coaching workflow for {len(backlog_items)} items",
                deps=ctx.deps,
            )
            comprehensive_results["agent_results"]["backlog_coach"] = coaching_result
            comprehensive_results["execution_order"].append("backlog_coach")

        # Synthesize results
        workflow_end = datetime.utcnow()
        execution_time = (workflow_end - workflow_start).total_seconds()

        comprehensive_results["synthesis"] = {
            "total_agents_executed": len(comprehensive_results["execution_order"]),
            "execution_time_seconds": execution_time,
            "workflow_completion": "success",
            "key_insights": [
                f"Executed {len(comprehensive_results['execution_order'])} specialized agents",
                f"Processed document analysis: {'Yes' if 'document_analyst' in comprehensive_results['execution_order'] else 'No'}",
                f"Generated user stories: {'Yes' if 'story_writer' in comprehensive_results['execution_order'] else 'No'}",
                f"Assessed priorities: {'Yes' if 'priority_manager' in comprehensive_results['execution_order'] else 'No'}",
                f"Provided coaching: {'Yes' if 'backlog_coach' in comprehensive_results['execution_order'] else 'No'}",
            ],
        }

        # Update coordinator context
        ctx.deps.coordination_strategy = "comprehensive"
        ctx.deps.results_aggregation = comprehensive_results["synthesis"]

        return comprehensive_results

    except Exception as e:
        return {
            "workflow_type": "comprehensive_analysis",
            "success": False,
            "error": f"Comprehensive analysis workflow failed: {str(e)}",
            "agent_results": {},
            "synthesis": {},
            "execution_order": [],
        }


@coordinator.tool
def generate_final_report_tool(
    ctx: RunContext[CoordinatorContext], workflow_results: Dict[str, Any]
) -> Dict[str, Any]:
    """Tool for generating comprehensive final report"""
    try:
        report = {
            "report_type": "comprehensive_analysis",
            "generated_at": datetime.utcnow().isoformat(),
            "session_id": ctx.deps.session_id,
            "executive_summary": {},
            "detailed_findings": {},
            "recommendations": [],
            "next_steps": [],
            "metrics": {},
        }

        # Generate executive summary
        agents_executed = len(ctx.deps.active_agents)
        workflows_completed = len(
            [k for k, v in ctx.deps.workflow_state.items() if v == "completed"]
        )

        report["executive_summary"] = {
            "agents_utilized": agents_executed,
            "workflows_completed": workflows_completed,
            "coordination_strategy": ctx.deps.coordination_strategy,
            "overall_success": workflow_results.get("success", False),
        }

        # Extract key findings from each agent
        agent_results = workflow_results.get("agent_results", {})

        if "document_analyst" in agent_results:
            report["detailed_findings"]["document_analysis"] = {
                "status": "completed",
                "key_outputs": "Requirements extracted and structured",
                "quality_assessment": "Document processed successfully",
            }

        if "story_writer" in agent_results:
            report["detailed_findings"]["story_generation"] = {
                "status": "completed",
                "key_outputs": "User stories generated with acceptance criteria",
                "quality_assessment": "Stories follow standard format",
            }

        if "priority_manager" in agent_results:
            report["detailed_findings"]["priority_assessment"] = {
                "status": "completed",
                "key_outputs": "Priorities assigned and categorized",
                "quality_assessment": "Assessment based on business value",
            }

        if "backlog_coach" in agent_results:
            report["detailed_findings"]["backlog_coaching"] = {
                "status": "completed",
                "key_outputs": "Health analysis and improvement recommendations",
                "quality_assessment": "Coaching insights provided",
            }

        # Generate recommendations
        report["recommendations"] = [
            "Review generated user stories with stakeholders",
            "Validate priority assessments with business owners",
            "Implement recommended backlog improvements",
            "Schedule regular backlog refinement sessions",
            "Monitor progress using provided metrics",
        ]

        # Define next steps
        report["next_steps"] = [
            "Share results with product team",
            "Plan implementation of recommendations",
            "Schedule follow-up analysis session",
            "Track improvement metrics over time",
        ]

        # Calculate metrics
        report["metrics"] = {
            "processing_efficiency": "high" if agents_executed >= 3 else "medium",
            "workflow_completeness": f"{workflows_completed}/{len(ctx.deps.workflow_state)}",
            "recommendation_count": len(report["recommendations"]),
            "coordination_success": ctx.deps.coordination_strategy != "failed",
        }

        return report

    except Exception as e:
        return {
            "report_type": "error_report",
            "error": f"Report generation failed: {str(e)}",
            "generated_at": datetime.utcnow().isoformat(),
        }
