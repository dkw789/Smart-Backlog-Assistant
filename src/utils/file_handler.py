"""File handling utilities for the Smart Backlog Assistant."""

import json
import os
from pathlib import Path
from typing import Any, Dict

import PyPDF2
from docx import Document


class FileHandler:
    """Handles file operations for various input formats."""

    @staticmethod
    def read_text_file(file_path: str) -> str:
        """Read content from a text file."""
        try:
            with open(file_path, encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            raise FileNotFoundError(f"Error reading text file {file_path}: {str(e)}")

    @staticmethod
    def read_pdf_file(file_path: str) -> str:
        """Extract text content from a PDF file."""
        try:
            text = ""
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise FileNotFoundError(f"Error reading PDF file {file_path}: {str(e)}")

    @staticmethod
    def read_docx_file(file_path: str) -> str:
        """Extract text content from a Word document."""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise FileNotFoundError(f"Error reading DOCX file {file_path}: {str(e)}")

    @staticmethod
    def read_json_file(file_path: str) -> Dict[str, Any]:
        """Read and parse a JSON file."""
        try:
            with open(file_path, encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            raise FileNotFoundError(f"Error reading JSON file {file_path}: {str(e)}")

    @staticmethod
    def write_json_file(file_path: str, data: Dict[str, Any]) -> None:
        """Write data to a JSON file."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
        except Exception as e:
            raise OSError(f"Error writing JSON file {file_path}: {str(e)}")

    @staticmethod
    def get_file_type(file_path: str) -> str:
        """Determine the file type based on extension."""
        extension = Path(file_path).suffix.lower()
        type_mapping = {
            ".txt": "text",
            ".md": "text",
            ".pdf": "pdf",
            ".docx": "docx",
            ".json": "json",
        }
        return type_mapping.get(extension, "unknown")

    @staticmethod
    def read_file_content(file_path: str) -> str:
        """Read file content based on file type."""
        file_type = FileHandler.get_file_type(file_path)

        if file_type == "text":
            return FileHandler.read_text_file(file_path)
        elif file_type == "pdf":
            return FileHandler.read_pdf_file(file_path)
        elif file_type == "docx":
            return FileHandler.read_docx_file(file_path)
        elif file_type == "json":
            json_data = FileHandler.read_json_file(file_path)
            return json.dumps(json_data, indent=2)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
