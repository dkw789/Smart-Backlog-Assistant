"""Comprehensive tests for document processor to improve code coverage."""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from typing import Dict, Any, List

from src.processors.document_processor import DocumentProcessor, ProcessedDocument
from src.utils.file_handler import FileHandler
from src.utils.validators import InputValidator


class TestProcessedDocument:
    """Tests for ProcessedDocument dataclass."""
    
    def test_processed_document_creation_success(self):
        """Test ProcessedDocument creation with successful processing."""
        doc = ProcessedDocument(
            file_path="/path/to/file.txt",
            file_type="text",
            content="Sample content",
            metadata={"word_count": 2},
            processing_success=True
        )
        
        assert doc.file_path == "/path/to/file.txt"
        assert doc.file_type == "text"
        assert doc.content == "Sample content"
        assert doc.metadata == {"word_count": 2}
        assert doc.processing_success is True
        assert doc.error_message is None
    
    def test_processed_document_creation_failure(self):
        """Test ProcessedDocument creation with failed processing."""
        doc = ProcessedDocument(
            file_path="/path/to/file.txt",
            file_type="unknown",
            content="",
            metadata={},
            processing_success=False,
            error_message="File not found"
        )
        
        assert doc.file_path == "/path/to/file.txt"
        assert doc.file_type == "unknown"
        assert doc.content == ""
        assert doc.metadata == {}
        assert doc.processing_success is False
        assert doc.error_message == "File not found"


class TestDocumentProcessor:
    """Tests for DocumentProcessor class."""
    
    def test_document_processor_initialization(self):
        """Test DocumentProcessor initialization."""
        processor = DocumentProcessor()
        
        assert processor.logger is not None
        assert isinstance(processor.file_handler, FileHandler)
    
    @patch('src.processors.document_processor.InputValidator.validate_file_exists')
    def test_process_document_file_not_found(self, mock_validate):
        """Test processing non-existent file."""
        mock_validate.return_value = False
        
        processor = DocumentProcessor()
        result = processor.process_document("non_existent.txt")
        
        assert isinstance(result, ProcessedDocument)
        assert result.file_path == "non_existent.txt"
        assert result.file_type == "unknown"
        assert result.content == ""
        assert result.processing_success is False
        assert "File not found or not readable" in result.error_message
        mock_validate.assert_called_once_with("non_existent.txt")
    
    @patch('src.processors.document_processor.InputValidator.validate_file_exists')
    @patch('src.processors.document_processor.FileHandler.get_file_type')
    def test_process_document_unsupported_type(self, mock_get_type, mock_validate):
        """Test processing unsupported file type."""
        mock_validate.return_value = True
        mock_get_type.return_value = "unknown"
        
        processor = DocumentProcessor()
        result = processor.process_document("test.xyz")
        
        assert result.file_path == "test.xyz"
        assert result.file_type == "unknown"
        assert result.processing_success is False
        assert "Unsupported file type" in result.error_message
    
    @patch('src.processors.document_processor.InputValidator.validate_file_exists')
    @patch('src.processors.document_processor.FileHandler.get_file_type')
    @patch('src.processors.document_processor.FileHandler.read_file_content')
    @patch('src.processors.document_processor.InputValidator.sanitize_text_input')
    @patch.object(DocumentProcessor, '_extract_metadata')
    def test_process_document_success(self, mock_extract_metadata, mock_sanitize, 
                                    mock_read_content, mock_get_type, mock_validate):
        """Test successful document processing."""
        mock_validate.return_value = True
        mock_get_type.return_value = "text"
        mock_read_content.return_value = "Raw file content"
        mock_sanitize.return_value = "Sanitized content"
        mock_extract_metadata.return_value = {"word_count": 2, "line_count": 1}
        
        processor = DocumentProcessor()
        result = processor.process_document("test.txt")
        
        assert result.file_path == "test.txt"
        assert result.file_type == "text"
        assert result.content == "Sanitized content"
        assert result.metadata == {"word_count": 2, "line_count": 1}
        assert result.processing_success is True
        assert result.error_message is None
        
        mock_validate.assert_called_once_with("test.txt")
        mock_get_type.assert_called_once_with("test.txt")
        mock_read_content.assert_called_once_with("test.txt")
        mock_sanitize.assert_called_once_with("Raw file content")
        mock_extract_metadata.assert_called_once_with("test.txt", "text", "Sanitized content")
    
    @patch('src.processors.document_processor.InputValidator.validate_file_exists')
    @patch('src.processors.document_processor.FileHandler.get_file_type')
    @patch('src.processors.document_processor.FileHandler.read_file_content')
    def test_process_document_exception_handling(self, mock_read_content, mock_get_type, mock_validate):
        """Test exception handling during document processing."""
        mock_validate.return_value = True
        mock_get_type.return_value = "text"
        mock_read_content.side_effect = Exception("Read error")
        
        processor = DocumentProcessor()
        result = processor.process_document("test.txt")
        
        assert result.file_path == "test.txt"
        assert result.file_type == "unknown"
        assert result.content == ""
        assert result.processing_success is False
        assert result.error_message == "Read error"
    
    @patch.object(DocumentProcessor, 'process_document')
    def test_process_multiple_documents_success(self, mock_process_single):
        """Test processing multiple documents successfully."""
        # Mock successful processing for all files
        mock_process_single.side_effect = [
            ProcessedDocument("file1.txt", "text", "content1", {}, True),
            ProcessedDocument("file2.txt", "text", "content2", {}, True),
            ProcessedDocument("file3.txt", "text", "content3", {}, True)
        ]
        
        processor = DocumentProcessor()
        file_paths = ["file1.txt", "file2.txt", "file3.txt"]
        results = processor.process_multiple_documents(file_paths)
        
        assert len(results) == 3
        assert all(result.processing_success for result in results)
        assert results[0].content == "content1"
        assert results[1].content == "content2"
        assert results[2].content == "content3"
        
        # Verify process_document was called for each file
        assert mock_process_single.call_count == 3
    
    @patch.object(DocumentProcessor, 'process_document')
    def test_process_multiple_documents_mixed_results(self, mock_process_single):
        """Test processing multiple documents with mixed success/failure."""
        mock_process_single.side_effect = [
            ProcessedDocument("file1.txt", "text", "content1", {}, True),
            ProcessedDocument("file2.txt", "unknown", "", {}, False, "Error"),
            ProcessedDocument("file3.txt", "text", "content3", {}, True)
        ]
        
        processor = DocumentProcessor()
        file_paths = ["file1.txt", "file2.txt", "file3.txt"]
        results = processor.process_multiple_documents(file_paths)
        
        assert len(results) == 3
        assert results[0].processing_success is True
        assert results[1].processing_success is False
        assert results[2].processing_success is True
        assert results[1].error_message == "Error"
    
    @patch.object(DocumentProcessor, 'process_document')
    def test_process_multiple_documents_empty_list(self, mock_process_single):
        """Test processing empty list of documents."""
        processor = DocumentProcessor()
        results = processor.process_multiple_documents([])
        
        assert len(results) == 0
        mock_process_single.assert_not_called()
    
    def test_extract_meeting_notes_structure_empty_content(self):
        """Test extracting structure from empty meeting notes."""
        processor = DocumentProcessor()
        result = processor.extract_meeting_notes_structure("")
        
        expected_structure = {
            "action_items": [],
            "decisions": [],
            "requirements": [],
            "participants": [],
            "date": None,
            "topics": [],
        }
        
        assert result == expected_structure
    
    def test_extract_meeting_notes_structure_basic_content(self):
        """Test extracting structure from basic meeting notes."""
        content = """
        # Meeting Topic 1
        ## Subtopic
        
        Action Items:
        - Complete user authentication
        - Review API documentation
        
        Decisions:
        - Use React for frontend
        - Deploy on AWS
        
        Requirements:
        - Must support 1000 users
        - Response time under 200ms
        
        Participants:
        - John Doe
        - Jane Smith
        """
        
        processor = DocumentProcessor()
        result = processor.extract_meeting_notes_structure(content)
        
        assert len(result["action_items"]) == 2
        assert "Complete user authentication" in result["action_items"]
        assert "Review API documentation" in result["action_items"]
        
        assert len(result["decisions"]) == 2
        assert "Use React for frontend" in result["decisions"]
        assert "Deploy on AWS" in result["decisions"]
        
        assert len(result["requirements"]) == 2
        assert "Must support 1000 users" in result["requirements"]
        assert "Response time under 200ms" in result["requirements"]
        
        assert len(result["participants"]) == 2
        assert "John Doe" in result["participants"]
        assert "Jane Smith" in result["participants"]
        
        assert len(result["topics"]) == 2
        assert "# Meeting Topic 1" in result["topics"]
        assert "## Subtopic" in result["topics"]
    
    def test_extract_meeting_notes_structure_case_insensitive(self):
        """Test that section detection is case insensitive."""
        content = """ACTION ITEMS:
- Task 1

DECISIONS:
- Decision 1

REQUIREMENTS:
- Requirement 1

ATTENDEES:
- Person 1"""
        
        processor = DocumentProcessor()
        result = processor.extract_meeting_notes_structure(content)
        
        assert len(result["action_items"]) == 1
        assert len(result["decisions"]) == 1
        assert len(result["requirements"]) == 1
        assert len(result["participants"]) == 1
    
    def test_extract_meeting_notes_structure_various_keywords(self):
        """Test extraction with various keyword variations."""
        content = """Action Item:
- Single action item

Decision made:
- Single decision

Requirement identified:
- Single requirement

Present at meeting:
- Single participant"""
        
        processor = DocumentProcessor()
        result = processor.extract_meeting_notes_structure(content)
        
        assert len(result["action_items"]) == 1
        assert len(result["decisions"]) == 1
        assert len(result["requirements"]) == 1
        assert len(result["participants"]) == 1
    
    def test_extract_meeting_notes_structure_mixed_content(self):
        """Test extraction with mixed content and no clear sections."""
        content = """
        This is a general meeting note.
        
        # Main Topic
        
        Some discussion happened here.
        
        - Random bullet point not in section
        
        ## Another topic
        
        More discussion.
        """
        
        processor = DocumentProcessor()
        result = processor.extract_meeting_notes_structure(content)
        
        # Should capture topics but not random bullet points
        assert len(result["topics"]) == 2
        assert "# Main Topic" in result["topics"]
        assert "## Another topic" in result["topics"]
        
        # Other sections should be empty
        assert len(result["action_items"]) == 0
        assert len(result["decisions"]) == 0
        assert len(result["requirements"]) == 0
        assert len(result["participants"]) == 0
    
    def test_extract_meeting_notes_structure_whitespace_handling(self):
        """Test that whitespace is properly handled."""
        content = """Action Items:
-    Task with extra spaces    

Decisions:
-Clean decision"""
        
        processor = DocumentProcessor()
        result = processor.extract_meeting_notes_structure(content)
        
        assert len(result["action_items"]) == 1
        assert result["action_items"][0] == "Task with extra spaces"
        
        assert len(result["decisions"]) == 1
        assert result["decisions"][0] == "Clean decision"


class TestDocumentProcessorIntegration:
    """Integration tests for DocumentProcessor."""
    
    def test_document_processor_with_real_file(self):
        """Test document processor with actual temporary file."""
        content = "This is a test document with some content."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            processor = DocumentProcessor()
            result = processor.process_document(temp_path)
            
            assert result.processing_success is True
            assert result.file_type == "text"
            assert result.content == content  # Should be same after sanitization
            assert result.error_message is None
            assert "word_count" in result.metadata or "line_count" in result.metadata
        finally:
            os.unlink(temp_path)
    
    def test_document_processor_end_to_end_meeting_notes(self):
        """Test end-to-end processing of meeting notes."""
        meeting_content = """
        # Weekly Team Meeting
        
        Action Items:
        - Update documentation
        - Fix critical bug
        
        Decisions:
        - Use new framework
        
        Participants:
        - Alice
        - Bob
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(meeting_content)
            temp_path = f.name
        
        try:
            processor = DocumentProcessor()
            
            # Process the document
            result = processor.process_document(temp_path)
            assert result.processing_success is True
            
            # Extract meeting structure
            structure = processor.extract_meeting_notes_structure(result.content)
            
            assert len(structure["action_items"]) == 2
            assert len(structure["decisions"]) == 1
            assert len(structure["participants"]) == 2
            assert len(structure["topics"]) == 1
            
        finally:
            os.unlink(temp_path)
    
    def test_multiple_document_processing_integration(self):
        """Test processing multiple real documents."""
        documents = [
            ("doc1.txt", "First document content"),
            ("doc2.txt", "Second document content"),
            ("doc3.txt", "Third document content")
        ]
        
        temp_paths = []
        
        # Create temporary files
        for filename, content in documents:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(content)
                temp_paths.append(f.name)
        
        try:
            processor = DocumentProcessor()
            results = processor.process_multiple_documents(temp_paths)
            
            assert len(results) == 3
            assert all(result.processing_success for result in results)
            assert results[0].content == "First document content"
            assert results[1].content == "Second document content"
            assert results[2].content == "Third document content"
            
        finally:
            for path in temp_paths:
                os.unlink(path)
