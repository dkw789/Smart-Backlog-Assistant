"""Tests for legacy main modules to improve coverage."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.main import SmartBacklogAssistant


class TestSmartBacklogAssistant:
    """Test the original SmartBacklogAssistant class."""

    @pytest.fixture
    def temp_files(self):
        """Create temporary files for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test input file
            input_file = temp_path / "test_input.txt"
            input_file.write_text("Test meeting notes content")
            
            # Create test backlog file
            backlog_file = temp_path / "backlog.json"
            backlog_file.write_text('{"items": [{"title": "Test Item", "description": "Test"}]}')
            
            # Create test output file path
            output_file = temp_path / "test_output.json"
            
            yield {
                "input": str(input_file),
                "backlog": str(backlog_file),
                "output": str(output_file),
                "dir": temp_dir
            }

    def test_assistant_initialization(self):
        """Test SmartBacklogAssistant initialization."""
        with patch('src.main.DocumentProcessor') as mock_doc_proc, \
             patch('src.main.BacklogAnalyzer') as mock_analyzer, \
             patch('src.main.AIProcessor') as mock_ai_proc, \
             patch('src.main.UserStoryGenerator') as mock_story_gen, \
             patch('src.main.PriorityEngine') as mock_priority, \
             patch('src.main.FileHandler') as mock_file_handler:
            
            assistant = SmartBacklogAssistant()
            
            # Verify all components are initialized
            mock_doc_proc.assert_called_once()
            mock_analyzer.assert_called_once()
            mock_ai_proc.assert_called_once()
            mock_story_gen.assert_called_once()
            mock_priority.assert_called_once()
            mock_file_handler.assert_called_once()

    def test_process_meeting_notes_success(self, temp_files):
        """Test successful meeting notes processing."""
        with patch('src.main.DocumentProcessor') as mock_doc_proc, \
             patch('src.main.BacklogAnalyzer') as mock_analyzer, \
             patch('src.main.AIProcessor') as mock_ai_proc, \
             patch('src.main.UserStoryGenerator') as mock_story_gen, \
             patch('src.main.PriorityEngine') as mock_priority, \
             patch('src.main.FileHandler') as mock_file_handler:
            
            # Mock components
            mock_doc = Mock()
            mock_doc.extract_text.return_value = "extracted text"
            mock_doc_proc.return_value = mock_doc
            
            mock_ai = Mock()
            mock_ai.extract_requirements.return_value = Mock(
                success=True, content="requirements"
            )
            mock_ai_proc.return_value = mock_ai
            
            mock_generator = Mock()
            mock_generator.generate_stories_from_requirements.return_value = [
                {"title": "Story 1", "description": "Test story"}
            ]
            mock_story_gen.return_value = mock_generator
            
            mock_file = Mock()
            mock_file_handler.return_value = mock_file
            
            assistant = SmartBacklogAssistant()
            
            result = assistant.process_meeting_notes(
                temp_files["input"],
                temp_files["output"]
            )
            
            assert result is not None
            assert "requirements" in result
            assert "user_stories" in result
            mock_doc.extract_text.assert_called_once()
            mock_ai.extract_requirements.assert_called_once()

    def test_process_meeting_notes_ai_failure(self, temp_files):
        """Test meeting notes processing with AI failure."""
        with patch('src.main.DocumentProcessor') as mock_doc_proc, \
             patch('src.main.BacklogAnalyzer') as mock_analyzer, \
             patch('src.main.AIProcessor') as mock_ai_proc, \
             patch('src.main.UserStoryGenerator') as mock_story_gen, \
             patch('src.main.PriorityEngine') as mock_priority, \
             patch('src.main.FileHandler') as mock_file_handler:
            
            # Mock components with AI failure
            mock_doc = Mock()
            mock_doc.extract_text.return_value = "extracted text"
            mock_doc_proc.return_value = mock_doc
            
            mock_ai = Mock()
            mock_ai.extract_requirements.return_value = Mock(
                success=False, error_message="AI service unavailable"
            )
            mock_ai_proc.return_value = mock_ai
            
            assistant = SmartBacklogAssistant()
            
            result = assistant.process_meeting_notes(
                temp_files["input"],
                temp_files["output"]
            )
            
            # Should still return a result with error information
            assert result is not None
            assert "error" in result or "requirements" in result

    def test_analyze_backlog_success(self, temp_files):
        """Test successful backlog analysis."""
        with patch('src.main.DocumentProcessor') as mock_doc_proc, \
             patch('src.main.BacklogAnalyzer') as mock_analyzer, \
             patch('src.main.AIProcessor') as mock_ai_proc, \
             patch('src.main.UserStoryGenerator') as mock_story_gen, \
             patch('src.main.PriorityEngine') as mock_priority, \
             patch('src.main.FileHandler') as mock_file_handler:
            
            # Mock components
            mock_analyzer_instance = Mock()
            mock_analyzer_instance.extract_backlog_from_json.return_value = [
                {"title": "Item 1", "description": "Test item"}
            ]
            mock_analyzer_instance.analyze_backlog_data.return_value = Mock(
                health_score=85,
                total_items=1,
                recommendations=["Add more details"]
            )
            mock_analyzer.return_value = mock_analyzer_instance
            
            mock_ai = Mock()
            mock_ai.analyze_backlog_items.return_value = Mock(
                success=True, content="AI analysis"
            )
            mock_ai_proc.return_value = mock_ai
            
            mock_file = Mock()
            mock_file_handler.return_value = mock_file
            
            assistant = SmartBacklogAssistant()
            
            result = assistant.analyze_backlog(
                temp_files["backlog"],
                temp_files["output"]
            )
            
            assert result is not None
            assert "analysis" in result
            mock_analyzer_instance.extract_backlog_from_json.assert_called_once()
            mock_analyzer_instance.analyze_backlog_data.assert_called_once()

    def test_generate_sprint_plan_success(self, temp_files):
        """Test successful sprint plan generation."""
        with patch('src.main.DocumentProcessor') as mock_doc_proc, \
             patch('src.main.BacklogAnalyzer') as mock_analyzer, \
             patch('src.main.AIProcessor') as mock_ai_proc, \
             patch('src.main.UserStoryGenerator') as mock_story_gen, \
             patch('src.main.PriorityEngine') as mock_priority, \
             patch('src.main.FileHandler') as mock_file_handler:
            
            # Mock components
            mock_analyzer_instance = Mock()
            mock_analyzer_instance.extract_backlog_from_json.return_value = [
                {"title": "Item 1", "priority": "high", "story_points": 5},
                {"title": "Item 2", "priority": "medium", "story_points": 3}
            ]
            mock_analyzer.return_value = mock_analyzer_instance
            
            mock_priority_instance = Mock()
            mock_priority_instance.assess_multiple_items.return_value = [
                Mock(priority="high", business_value=8),
                Mock(priority="medium", business_value=5)
            ]
            mock_priority.return_value = mock_priority_instance
            
            mock_file = Mock()
            mock_file_handler.return_value = mock_file
            
            assistant = SmartBacklogAssistant()
            
            result = assistant.generate_sprint_plan(
                temp_files["backlog"],
                capacity=40,
                output_path=temp_files["output"]
            )
            
            assert result is not None
            assert "sprint_plan" in result
            assert "capacity" in result
            mock_analyzer_instance.extract_backlog_from_json.assert_called_once()

    def test_process_requirements_document_success(self, temp_files):
        """Test successful requirements document processing."""
        with patch('src.main.DocumentProcessor') as mock_doc_proc, \
             patch('src.main.BacklogAnalyzer') as mock_analyzer, \
             patch('src.main.AIProcessor') as mock_ai_proc, \
             patch('src.main.UserStoryGenerator') as mock_story_gen, \
             patch('src.main.PriorityEngine') as mock_priority, \
             patch('src.main.FileHandler') as mock_file_handler:
            
            # Mock components
            mock_doc = Mock()
            mock_doc.extract_text.return_value = "requirements document text"
            mock_doc_proc.return_value = mock_doc
            
            mock_ai = Mock()
            mock_ai.extract_requirements.return_value = Mock(
                success=True, content="extracted requirements"
            )
            mock_ai_proc.return_value = mock_ai
            
            mock_generator = Mock()
            mock_generator.generate_stories_from_requirements.return_value = [
                {"title": "Story 1", "description": "Generated story"}
            ]
            mock_story_gen.return_value = mock_generator
            
            mock_priority_instance = Mock()
            mock_priority_instance.assess_multiple_items.return_value = [
                Mock(priority="high", category="feature")
            ]
            mock_priority.return_value = mock_priority_instance
            
            mock_file = Mock()
            mock_file_handler.return_value = mock_file
            
            assistant = SmartBacklogAssistant()
            
            result = assistant.process_requirements_document(
                temp_files["input"],
                temp_files["output"]
            )
            
            assert result is not None
            assert "requirements" in result
            assert "user_stories" in result
            assert "backlog_items" in result
            mock_doc.extract_text.assert_called_once()
            mock_ai.extract_requirements.assert_called_once()

    def test_file_not_found_error(self):
        """Test handling of file not found errors."""
        with patch('src.main.DocumentProcessor') as mock_doc_proc, \
             patch('src.main.BacklogAnalyzer') as mock_analyzer, \
             patch('src.main.AIProcessor') as mock_ai_proc, \
             patch('src.main.UserStoryGenerator') as mock_story_gen, \
             patch('src.main.PriorityEngine') as mock_priority, \
             patch('src.main.FileHandler') as mock_file_handler:
            
            assistant = SmartBacklogAssistant()
            
            with pytest.raises(FileNotFoundError):
                assistant.process_meeting_notes(
                    "/non/existent/file.txt",
                    "/tmp/output.json"
                )

    def test_empty_file_handling(self, temp_files):
        """Test handling of empty files."""
        # Create empty file
        empty_file = Path(temp_files["dir"]) / "empty.txt"
        empty_file.write_text("")
        
        with patch('src.main.DocumentProcessor') as mock_doc_proc, \
             patch('src.main.BacklogAnalyzer') as mock_analyzer, \
             patch('src.main.AIProcessor') as mock_ai_proc, \
             patch('src.main.UserStoryGenerator') as mock_story_gen, \
             patch('src.main.PriorityEngine') as mock_priority, \
             patch('src.main.FileHandler') as mock_file_handler:
            
            # Mock components
            mock_doc = Mock()
            mock_doc.extract_text.return_value = ""
            mock_doc_proc.return_value = mock_doc
            
            mock_ai = Mock()
            mock_ai.extract_requirements.return_value = Mock(
                success=False, error_message="Empty content"
            )
            mock_ai_proc.return_value = mock_ai
            
            assistant = SmartBacklogAssistant()
            
            result = assistant.process_meeting_notes(
                str(empty_file),
                temp_files["output"]
            )
            
            # Should handle empty content gracefully
            assert result is not None

    def test_invalid_json_handling(self, temp_files):
        """Test handling of invalid JSON files."""
        # Create invalid JSON file
        invalid_json_file = Path(temp_files["dir"]) / "invalid.json"
        invalid_json_file.write_text("invalid json content")
        
        with patch('src.main.DocumentProcessor') as mock_doc_proc, \
             patch('src.main.BacklogAnalyzer') as mock_analyzer, \
             patch('src.main.AIProcessor') as mock_ai_proc, \
             patch('src.main.UserStoryGenerator') as mock_story_gen, \
             patch('src.main.PriorityEngine') as mock_priority, \
             patch('src.main.FileHandler') as mock_file_handler:
            
            # Mock components
            mock_analyzer_instance = Mock()
            mock_analyzer_instance.extract_backlog_from_json.side_effect = ValueError("Invalid JSON")
            mock_analyzer.return_value = mock_analyzer_instance
            
            assistant = SmartBacklogAssistant()
            
            with pytest.raises(ValueError):
                assistant.analyze_backlog(
                    str(invalid_json_file),
                    temp_files["output"]
                )

    def test_large_capacity_sprint_plan(self, temp_files):
        """Test sprint plan generation with large capacity."""
        with patch('src.main.DocumentProcessor') as mock_doc_proc, \
             patch('src.main.BacklogAnalyzer') as mock_analyzer, \
             patch('src.main.AIProcessor') as mock_ai_proc, \
             patch('src.main.UserStoryGenerator') as mock_story_gen, \
             patch('src.main.PriorityEngine') as mock_priority, \
             patch('src.main.FileHandler') as mock_file_handler:
            
            # Mock components
            mock_analyzer_instance = Mock()
            mock_analyzer_instance.extract_backlog_from_json.return_value = [
                {"title": f"Item {i}", "priority": "high", "story_points": 2}
                for i in range(50)  # Many items
            ]
            mock_analyzer.return_value = mock_analyzer_instance
            
            mock_priority_instance = Mock()
            mock_priority_instance.assess_multiple_items.return_value = [
                Mock(priority="high", business_value=8) for _ in range(50)
            ]
            mock_priority.return_value = mock_priority_instance
            
            mock_file = Mock()
            mock_file_handler.return_value = mock_file
            
            assistant = SmartBacklogAssistant()
            
            result = assistant.generate_sprint_plan(
                temp_files["backlog"],
                capacity=100,  # Large capacity
                output_path=temp_files["output"]
            )
            
            assert result is not None
            assert result["capacity"] == 100

    def test_zero_capacity_sprint_plan(self, temp_files):
        """Test sprint plan generation with zero capacity."""
        with patch('src.main.DocumentProcessor') as mock_doc_proc, \
             patch('src.main.BacklogAnalyzer') as mock_analyzer, \
             patch('src.main.AIProcessor') as mock_ai_proc, \
             patch('src.main.UserStoryGenerator') as mock_story_gen, \
             patch('src.main.PriorityEngine') as mock_priority, \
             patch('src.main.FileHandler') as mock_file_handler:
            
            # Mock components
            mock_analyzer_instance = Mock()
            mock_analyzer_instance.extract_backlog_from_json.return_value = []
            mock_analyzer.return_value = mock_analyzer_instance
            
            mock_file = Mock()
            mock_file_handler.return_value = mock_file
            
            assistant = SmartBacklogAssistant()
            
            result = assistant.generate_sprint_plan(
                temp_files["backlog"],
                capacity=0,
                output_path=temp_files["output"]
            )
            
            assert result is not None
            assert result["capacity"] == 0

    def test_component_integration(self):
        """Test that all components work together."""
        with patch('src.main.DocumentProcessor') as mock_doc_proc, \
             patch('src.main.BacklogAnalyzer') as mock_analyzer, \
             patch('src.main.AIProcessor') as mock_ai_proc, \
             patch('src.main.UserStoryGenerator') as mock_story_gen, \
             patch('src.main.PriorityEngine') as mock_priority, \
             patch('src.main.FileHandler') as mock_file_handler:
            
            assistant = SmartBacklogAssistant()
            
            # Verify all components are accessible
            assert assistant.document_processor is not None
            assert assistant.backlog_analyzer is not None
            assert assistant.ai_processor is not None
            assert assistant.user_story_generator is not None
            assert assistant.priority_engine is not None
            assert assistant.file_handler is not None

    def test_logging_integration(self):
        """Test logging integration."""
        with patch('src.main.DocumentProcessor') as mock_doc_proc, \
             patch('src.main.BacklogAnalyzer') as mock_analyzer, \
             patch('src.main.AIProcessor') as mock_ai_proc, \
             patch('src.main.UserStoryGenerator') as mock_story_gen, \
             patch('src.main.PriorityEngine') as mock_priority, \
             patch('src.main.FileHandler') as mock_file_handler, \
             patch('src.main.get_logger') as mock_get_logger:
            
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            assistant = SmartBacklogAssistant()
            
            # Logger should be initialized
            mock_get_logger.assert_called()

    def test_output_path_none(self, temp_files):
        """Test behavior when output_path is None."""
        with patch('src.main.DocumentProcessor') as mock_doc_proc, \
             patch('src.main.BacklogAnalyzer') as mock_analyzer, \
             patch('src.main.AIProcessor') as mock_ai_proc, \
             patch('src.main.UserStoryGenerator') as mock_story_gen, \
             patch('src.main.PriorityEngine') as mock_priority, \
             patch('src.main.FileHandler') as mock_file_handler:
            
            # Mock components
            mock_doc = Mock()
            mock_doc.extract_text.return_value = "test content"
            mock_doc_proc.return_value = mock_doc
            
            mock_ai = Mock()
            mock_ai.extract_requirements.return_value = Mock(
                success=True, content="requirements"
            )
            mock_ai_proc.return_value = mock_ai
            
            mock_generator = Mock()
            mock_generator.generate_stories_from_requirements.return_value = []
            mock_story_gen.return_value = mock_generator
            
            assistant = SmartBacklogAssistant()
            
            result = assistant.process_meeting_notes(
                temp_files["input"],
                output_path=None  # No output file
            )
            
            assert result is not None
