"""Document Analyst Agent using pydantic-ai framework."""

import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from src.agents.context_models import DocumentAnalystContext
from src.processors.document_processor import DocumentProcessor
from src.utils.file_handler import FileHandler

load_dotenv()


class DocumentExtractionResult(BaseModel):
    """Result from document extraction tool."""

    success: bool
    content: str
    metadata: Dict[str, Any]
    error_message: Optional[str] = None


class MeetingNotesStructure(BaseModel):
    """Structured meeting notes extraction result."""

    attendees: List[str]
    action_items: List[str]
    decisions: List[str]
    requirements: List[str]
    next_steps: List[str]


# Create Document Analyst Agent
# Get AI service from environment, default to Claude
default_service = os.getenv("DEFAULT_AI_SERVICE", "anthropic").lower()
model_name = "claude-3-sonnet-20240229" if default_service == "anthropic" else "gpt-4"
model_provider = (
    f"{default_service}:{model_name}"
    if default_service == "anthropic"
    else f"openai:{model_name}"
)

document_analyst = Agent(
    model_provider,
    system_prompt="""You are a Senior Document Analyst specializing in extracting structured information 
    from engineering documents, meeting notes, and requirements specifications. Your role is to:
    
    1. Process various document formats (PDF, DOCX, TXT, MD)
    2. Extract key information like requirements, action items, decisions
    3. Structure unorganized content into actionable insights
    4. Identify stakeholders, priorities, and dependencies
    5. Provide metadata about document quality and completeness
    
    Always be thorough, accurate, and focus on actionable information extraction.""",
)


@document_analyst.tool
def extract_document_content_tool(
    ctx: RunContext[DocumentAnalystContext], file_path: str
) -> DocumentExtractionResult:
    """Tool wrapping document content extraction - CORE FUNCTIONALITY"""
    try:
        # Update context
        ctx.deps.current_document = file_path
        ctx.deps.document_type = FileHandler.get_file_type(file_path)

        # Process document
        processor = DocumentProcessor()
        result = processor.process_document(file_path)

        if result.processing_success:
            ctx.deps.processed_documents.append(file_path)
            return DocumentExtractionResult(
                success=True, content=result.content, metadata=result.metadata
            )
        else:
            return DocumentExtractionResult(
                success=False,
                content="",
                metadata={},
                error_message=result.error_message,
            )

    except Exception as e:
        return DocumentExtractionResult(
            success=False,
            content="",
            metadata={},
            error_message=f"Document extraction failed: {str(e)}",
        )


@document_analyst.tool
def extract_meeting_notes_structure_tool(
    ctx: RunContext[DocumentAnalystContext], content: str
) -> MeetingNotesStructure:
    """Tool wrapping meeting notes structure extraction - REQUIRED FUNCTIONALITY"""
    try:
        processor = DocumentProcessor()
        structure = processor.extract_meeting_notes_structure(content)

        return MeetingNotesStructure(
            attendees=structure.get("participants", []),
            action_items=structure.get("action_items", []),
            decisions=structure.get("decisions", []),
            requirements=structure.get("requirements", []),
            next_steps=structure.get("next_steps", []),
        )

    except Exception as e:
        return MeetingNotesStructure(
            attendees=[],
            action_items=[f"Error extracting structure: {str(e)}"],
            decisions=[],
            requirements=[],
            next_steps=[],
        )


@document_analyst.tool
def extract_requirements_from_text_tool(
    ctx: RunContext[DocumentAnalystContext], text_content: str
) -> List[Dict[str, Any]]:
    """Tool wrapping requirements extraction from text - REQUIRED FUNCTIONALITY"""
    try:
        processor = DocumentProcessor()
        requirements = processor.extract_requirements_from_text(text_content)

        # Update context with extracted requirements
        ctx.deps.project_context["extracted_requirements"] = requirements

        return requirements

    except Exception as e:
        return [{"error": f"Requirements extraction failed: {str(e)}"}]


@document_analyst.tool
def analyze_document_quality_tool(
    ctx: RunContext[DocumentAnalystContext], content: str, document_type: str
) -> Dict[str, Any]:
    """Tool for analyzing document quality and completeness"""
    try:
        quality_metrics = {
            "word_count": len(content.split()),
            "line_count": len(content.split("\n")),
            "has_structure": bool(
                any(
                    marker in content.lower()
                    for marker in ["#", "##", "1.", "2.", "-", "*"]
                )
            ),
            "completeness_score": 0.0,
            "quality_issues": [],
            "recommendations": [],
        }

        # Calculate completeness score
        score = 0.0
        if quality_metrics["word_count"] > 50:
            score += 25
        if quality_metrics["word_count"] > 200:
            score += 25
        if quality_metrics["has_structure"]:
            score += 25
        if any(
            keyword in content.lower()
            for keyword in ["requirement", "must", "should", "shall"]
        ):
            score += 25

        quality_metrics["completeness_score"] = score

        # Identify quality issues
        if quality_metrics["word_count"] < 50:
            quality_metrics["quality_issues"].append("Document is very brief")
            quality_metrics["recommendations"].append("Add more detailed descriptions")

        if not quality_metrics["has_structure"]:
            quality_metrics["quality_issues"].append("Document lacks clear structure")
            quality_metrics["recommendations"].append(
                "Add headings and bullet points for better organization"
            )

        return quality_metrics

    except Exception as e:
        return {"error": f"Quality analysis failed: {str(e)}"}


@document_analyst.tool
def identify_stakeholders_tool(
    ctx: RunContext[DocumentAnalystContext], content: str
) -> List[str]:
    """Tool for identifying stakeholders mentioned in documents"""
    try:
        stakeholders = []

        # Common patterns for stakeholder identification
        import re

        # Email patterns
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        emails = re.findall(email_pattern, content)
        stakeholders.extend(emails)

        # Name patterns (simple heuristic)
        name_patterns = [
            r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",  # First Last
            r"\b[A-Z]\. [A-Z][a-z]+\b",  # F. Last
        ]

        for pattern in name_patterns:
            names = re.findall(pattern, content)
            stakeholders.extend(names)

        # Remove duplicates and filter out common false positives
        stakeholders = list(set(stakeholders))
        filtered_stakeholders = [
            s
            for s in stakeholders
            if not any(word in s.lower() for word in ["test", "example", "sample"])
        ]

        return filtered_stakeholders[:10]  # Limit to top 10

    except Exception as e:
        return [f"Error identifying stakeholders: {str(e)}"]
