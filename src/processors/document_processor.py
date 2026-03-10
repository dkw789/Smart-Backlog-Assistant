"""Document processing module for the Smart Backlog Assistant."""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.utils.file_handler import FileHandler
from src.utils.validators import InputValidator


@dataclass
class ProcessedDocument:
    """Represents a processed document with extracted content."""

    file_path: str
    file_type: str
    content: str
    metadata: Dict[str, Any]
    processing_success: bool
    error_message: Optional[str] = None


class DocumentProcessor:
    """Processes various document types for content extraction."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.file_handler = FileHandler()

    def process_document(self, file_path: str) -> ProcessedDocument:
        """Process a single document and extract its content."""
        try:
            # Validate file exists
            if not InputValidator.validate_file_exists(file_path):
                return ProcessedDocument(
                    file_path=file_path,
                    file_type="unknown",
                    content="",
                    metadata={},
                    processing_success=False,
                    error_message=f"File not found or not readable: {file_path}",
                )

            # Determine file type
            file_type = self.file_handler.get_file_type(file_path)

            # Extract content based on file type
            if file_type == "unknown":
                return ProcessedDocument(
                    file_path=file_path,
                    file_type=file_type,
                    content="",
                    metadata={},
                    processing_success=False,
                    error_message=f"Unsupported file type: {file_path}",
                )

            # Read and sanitize content
            raw_content = self.file_handler.read_file_content(file_path)
            sanitized_content = InputValidator.sanitize_text_input(raw_content)

            # Extract metadata
            metadata = self._extract_metadata(file_path, file_type, sanitized_content)

            return ProcessedDocument(
                file_path=file_path,
                file_type=file_type,
                content=sanitized_content,
                metadata=metadata,
                processing_success=True,
            )

        except Exception as e:
            self.logger.error(f"Error processing document {file_path}: {str(e)}")
            return ProcessedDocument(
                file_path=file_path,
                file_type="unknown",
                content="",
                metadata={},
                processing_success=False,
                error_message=str(e),
            )

    def process_multiple_documents(
        self, file_paths: List[str]
    ) -> List[ProcessedDocument]:
        """Process multiple documents and return results."""
        results = []
        for file_path in file_paths:
            result = self.process_document(file_path)
            results.append(result)

            if result.processing_success:
                self.logger.info(f"Successfully processed: {file_path}")
            else:
                self.logger.warning(
                    f"Failed to process: {file_path} - {result.error_message}"
                )

        return results

    def extract_meeting_notes_structure(self, content: str) -> Dict[str, Any]:
        """Extract structured information from meeting notes."""
        structure = {
            "action_items": [],
            "decisions": [],
            "requirements": [],
            "participants": [],
            "date": None,
            "topics": [],
        }

        lines = content.split("\n")
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect common meeting note patterns
            lower_line = line.lower()

            # Section headers
            if any(
                keyword in lower_line for keyword in ["action item", "action items"]
            ):
                current_section = "action_items"
            elif any(keyword in lower_line for keyword in ["decision", "decisions"]):
                current_section = "decisions"
            elif any(
                keyword in lower_line for keyword in ["requirement", "requirements"]
            ):
                current_section = "requirements"
            elif any(
                keyword in lower_line
                for keyword in ["attendees", "participants", "present"]
            ):
                current_section = "participants"
            # Topics/agenda items
            elif line.startswith("#") or line.startswith("##"):
                structure["topics"].append(line)
            # Bullet points within sections
            elif line.startswith("-") and current_section:
                item_text = line[1:].strip()
                if item_text and current_section in structure:
                    structure[current_section].append(item_text)
            # Non-bullet items within sections
            elif (
                current_section
                and not line.startswith("-")
                and not any(
                    keyword in lower_line
                    for keyword in [
                        "action item",
                        "decision",
                        "requirement",
                        "attendee",
                    ]
                )
            ):
                if current_section in structure:
                    structure[current_section].append(line)
            # Standalone lines with keywords (fallback)
            elif any(
                keyword in lower_line
                for keyword in ["action item", "todo", "follow up", "- [ ]"]
            ):
                if not line.startswith("-"):
                    structure["action_items"].append(line)
            elif any(
                keyword in lower_line for keyword in ["decision", "agreed", "decided"]
            ):
                if not line.startswith("-"):
                    structure["decisions"].append(line)
            elif any(
                keyword in lower_line
                for keyword in ["requirement", "need to", "must", "should"]
            ):
                if not line.startswith("-"):
                    structure["requirements"].append(line)

        return structure

    def extract_requirements_from_text(self, content: str) -> List[Dict[str, Any]]:
        """Extract requirements from unstructured text."""
        requirements = []
        lines = content.split("\n")

        current_requirement = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for requirement indicators
            lower_line = line.lower()

            if any(
                keyword in lower_line
                for keyword in [
                    "requirement",
                    "user story",
                    "feature",
                    "functionality",
                    "the system shall",
                    "the user should",
                    "must be able to",
                ]
            ):
                # Save previous requirement if exists
                if current_requirement:
                    requirements.append(current_requirement)

                # Start new requirement
                current_requirement = {
                    "title": line[:100],  # First 100 chars as title
                    "description": line,
                    "type": self._classify_requirement_type(line),
                    "priority": self._estimate_priority(line),
                    "source_line": line,
                }

            elif current_requirement and line.startswith("-"):
                # Add details to current requirement
                if "details" not in current_requirement:
                    current_requirement["details"] = []
                current_requirement["details"].append(line[1:].strip())

        # Add last requirement
        if current_requirement:
            requirements.append(current_requirement)

        return requirements

    def _extract_metadata(
        self, file_path: str, file_type: str, content: str
    ) -> Dict[str, Any]:
        """Extract metadata from document content."""
        import os
        from pathlib import Path

        metadata = {
            "file_size": os.path.getsize(file_path),
            "file_name": Path(file_path).name,
            "content_length": len(content),
            "word_count": len(content.split()) if content else 0,
            "line_count": len(content.split("\n")) if content else 0,
        }

        # Add file-type specific metadata
        if file_type == "json":
            try:
                import json

                json_data = json.loads(content)
                metadata["json_keys"] = (
                    list(json_data.keys()) if isinstance(json_data, dict) else []
                )
                metadata["json_items_count"] = (
                    len(json_data) if isinstance(json_data, (list, dict)) else 0
                )
            except:
                pass

        return metadata

    def _classify_requirement_type(self, text: str) -> str:
        """Classify the type of requirement based on text content."""
        lower_text = text.lower()

        if any(keyword in lower_text for keyword in ["bug", "fix", "error", "issue"]):
            return "bug"
        elif any(
            keyword in lower_text
            for keyword in ["performance", "optimize", "speed", "memory"]
        ):
            return "performance"
        elif any(
            keyword in lower_text
            for keyword in ["security", "authentication", "authorization"]
        ):
            return "security"
        elif any(
            keyword in lower_text for keyword in ["ui", "ux", "interface", "design"]
        ):
            return "ui_ux"
        elif any(
            keyword in lower_text for keyword in ["api", "integration", "service"]
        ):
            return "integration"
        else:
            return "feature"

    def _estimate_priority(self, text: str) -> str:
        """Estimate priority based on text content."""
        lower_text = text.lower()

        if any(
            keyword in lower_text
            for keyword in ["critical", "urgent", "asap", "immediately"]
        ):
            return "high"
        elif any(
            keyword in lower_text for keyword in ["important", "priority", "soon"]
        ):
            return "medium"
        elif any(
            keyword in lower_text
            for keyword in ["nice to have", "eventually", "future"]
        ):
            return "low"
        else:
            return "medium"
