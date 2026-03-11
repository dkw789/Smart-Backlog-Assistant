"""Integration tests for main_unified.py to improve coverage."""

import pytest
import tempfile
import json
import os
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

from src.main_unified import UnifiedSmartBacklogAssistant
from src.processors.backlog_analyzer import BacklogAnalysis


class TestUnifiedSmartBacklogAssistantIntegration:
    """Integration tests for UnifiedSmartBacklogAssistant."""
    
    @pytest.fixture
    def temp_files(self):
        """Create temporary files for testing."""
        temp_dir = tempfile.mkdtemp()
        
        # Create test meeting notes file
        meeting_notes_file = os.path.join(temp_dir, "meeting_notes.txt")
        with open(meeting_notes_file, 'w') as f:
            f.write("We need to implement user authentication and data validation features.")
        
        # Create test backlog file
        backlog_data = [
            {
                "title": "User Authentication",
                "description": "Implement login system",
                "priority": "high",
                "story_points": 8
            },
            {
                "title": "Data Validation",
                "description": "Add input validation",
                "priority": "medium", 
                "story_points": 5
            }
        ]
        backlog_file = os.path.join(temp_dir, "backlog.json")
        with open(backlog_file, 'w') as f:
            json.dump(backlog_data, f)
        
        # Create requirements file
        requirements_file = os.path.join(temp_dir, "requirements.md")
        with open(requirements_file, 'w') as f:
            f.write("# Requirements\n\n1. User login functionality\n2. Password validation\n3. Session management")
        
        yield {
            "dir": temp_dir,
            "meeting_notes": meeting_notes_file,
            "backlog": backlog_file,
            "requirements": requirements_file
        }
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
    
    def test_assistant_initialization(self):
        """Test UnifiedSmartBacklogAssistant initialization."""
        assistant = UnifiedSmartBacklogAssistant()
        
        # Check that all components are initialized
        assert assistant.document_processor is not None
        assert assistant.backlog_analyzer is not None
        assert assistant.ai_processor is not None
        assert assistant.user_story_generator is not None
        assert assistant.priority_engine is not None
        assert assistant.file_handler is not None
        assert assistant.cli_interface is not None
        assert assistant.logger is not None
    
    def test_assistant_initialization_with_options(self):
        """Test UnifiedSmartBacklogAssistant initialization with options."""
        assistant = UnifiedSmartBacklogAssistant(
            enable_caching=False,
            use_rich_cli=False
        )
        
        assert assistant.enable_caching is False
        assert assistant.use_rich_cli is False
    
    @patch('src.main_unified.AIProcessor')
    @patch('src.main_unified.UserStoryGenerator')
    def test_process_meeting_notes_sync_success(self, mock_story_gen, mock_ai_proc, temp_files):
        """Test synchronous meeting notes processing."""
        # Mock AI processor
        mock_ai_instance = Mock()
        mock_ai_instance.extract_requirements.return_value = Mock(
            content=json.dumps(["User authentication", "Data validation"]),
            success=True
        )
        mock_ai_proc.return_value = mock_ai_instance
        
        # Mock story generator
        mock_story_instance = Mock()
        mock_story_instance.generate_stories_from_requirements.return_value = [
            Mock(title="User Login Story")
        ]
        mock_story_gen.return_value = mock_story_instance
        
        assistant = UnifiedSmartBacklogAssistant()
        
        result = assistant.process_meeting_notes_sync(
            temp_files["meeting_notes"],
            output_path=None
        )
        
        assert result is not None
        assert "structured_requirements" in result
        assert "user_stories" in result
        assert "summary" in result
    
    @patch('src.main_unified.BacklogAnalyzer')
    def test_analyze_backlog_sync_success(self, mock_analyzer, temp_files):
        """Test synchronous backlog analysis."""
        # Mock backlog analyzer
        mock_analyzer_instance = Mock()
        mock_analysis = BacklogAnalysis(
            analysis_success=True,
            total_items=2,
            health_score=85.0,
            items_by_priority={"high": 1, "medium": 1},
            items_by_status={"todo": 2},
            missing_information=[],
            recommendations=["Add more detailed acceptance criteria"]
        )
        mock_analyzer_instance.analyze_backlog_data.return_value = mock_analysis
        mock_analyzer.return_value = mock_analyzer_instance
        
        assistant = UnifiedSmartBacklogAssistant()
        
        result = assistant.analyze_backlog_sync(
            temp_files["backlog"],
            output_path=None
        )
        
        assert result is not None
        assert "analysis_summary" in result
        assert result["analysis_summary"]["health_score"] == 85.0
        assert "recommendations" in result

    @patch('src.main_unified.PriorityEngine')
    @patch('src.main_unified.BacklogAnalyzer')
    def test_generate_sprint_plan_sync_success(self, mock_analyzer, mock_priority, temp_files):
        """Test synchronous sprint plan generation."""
        # Mock backlog analyzer
        mock_analyzer_instance = Mock()
        mock_analysis = BacklogAnalysis(
            analysis_success=True,
            total_items=2,
            health_score=85.0,
            items_by_priority={"high": 1, "medium": 1},
            items_by_status={"todo": 2},
            missing_information=[],
            recommendations=["Test recommendation"]
        )
        mock_analyzer_instance.analyze_backlog_data.return_value = mock_analysis
        mock_analyzer.return_value = mock_analyzer_instance
        
        # Mock priority engine
        mock_priority_instance = Mock()
        mock_priority_instance.recommend_sprint_items.return_value = [
            {
                "item": {"title": "User Authentication", "priority": "high", "story_points": 8},
                "assessment": Mock(),
                "effort_points": 8
            }
        ]
        mock_priority.return_value = mock_priority_instance
        
        assistant = UnifiedSmartBacklogAssistant()
        
        result = assistant.generate_sprint_plan_sync(
            temp_files["backlog"],
            capacity=40,
            output_path=None
        )
        
        assert result is not None
        assert "selected_items" in result
        assert "sprint_capacity" in result
        assert result["sprint_capacity"] == 40
        assert "total_effort_planned" in result
    
    @patch('src.main_unified.AIProcessor')
    @patch('src.main_unified.UserStoryGenerator')
    def test_process_requirements_sync_success(self, mock_story_gen, mock_ai_proc, temp_files):
        """Test synchronous requirements processing."""
        # Mock AI processor
        mock_ai_instance = Mock()
        mock_ai_instance.extract_requirements.return_value = Mock(
            content=json.dumps(["Login functionality", "Password validation", "Session management"]),
            success=True
        )
        mock_ai_proc.return_value = mock_ai_instance
        
        # Mock story generator
        mock_story_instance = Mock()
        mock_story_instance.generate_stories_from_requirements.return_value = [
            Mock(title="User Login Story"),
            Mock(title="Password Validation Story")
        ]
        mock_story_gen.return_value = mock_story_instance
        
        assistant = UnifiedSmartBacklogAssistant()
        
        result = assistant.process_requirements_sync(
            temp_files["requirements"],
            output_path=None
        )
        
        assert result is not None
        assert "structured_requirements" in result
        assert "user_stories" in result
        assert "source_file" in result
        assert "summary" in result
    
    def test_load_backlog_data_success(self, temp_files):
        """Test loading backlog data from file."""
        assistant = UnifiedSmartBacklogAssistant()
        
        backlog_data = assistant._load_backlog_data(temp_files["backlog"])
        
        assert backlog_data is not None
        assert isinstance(backlog_data, list)
        assert len(backlog_data) == 2
        assert backlog_data[0]["title"] == "User Authentication"
        assert backlog_data[1]["title"] == "Data Validation"
    
    def test_load_backlog_data_file_not_found(self):
        """Test loading backlog data from non-existent file."""
        assistant = UnifiedSmartBacklogAssistant()
        
        with pytest.raises(FileNotFoundError):
            assistant._load_backlog_data("/nonexistent/file.json")
    
    def test_load_backlog_data_invalid_json(self, temp_files):
        """Test loading invalid JSON backlog data."""
        # Create invalid JSON file
        invalid_json_file = os.path.join(temp_files["dir"], "invalid.json")
        with open(invalid_json_file, 'w') as f:
            f.write("invalid json content")
        
        assistant = UnifiedSmartBacklogAssistant()
        
        with pytest.raises(json.JSONDecodeError):
            assistant._load_backlog_data(invalid_json_file)
    
    @patch('src.main_unified.RichCLI')
    def test_run_interactive_mode_sync_meeting_notes(self, mock_cli, temp_files):
        """Test synchronous interactive mode for meeting notes."""
        # Mock CLI interface
        mock_cli_instance = mock_cli.return_value
        mock_cli_instance.display_main_menu.return_value = "1"
        mock_cli_instance.get_file_path.return_value = temp_files["meeting_notes"]
        mock_cli_instance.get_output_path.return_value = None
        mock_cli_instance.get_confirmation.return_value = True
        
        assistant = UnifiedSmartBacklogAssistant(use_rich_cli=True)
        
        # Mock the processing method
        with patch.object(assistant, 'process_meeting_notes_sync') as mock_process:
            mock_process.return_value = {
                "requirements": ["Test requirement"],
                "user_stories": ["Test story"],
                "success": True
            }
            
            with pytest.raises(SystemExit):
                assistant.run_interactive_mode_sync()

            mock_cli_instance.display_main_menu.assert_called_once()
            mock_process.assert_called_once()
    
    @patch('src.main_unified.RichCLI')
    def test_run_interactive_mode_sync_backlog_analysis(self, mock_cli, temp_files):
        """Test synchronous interactive mode for backlog analysis."""
        # Mock CLI interface
        mock_cli_instance = mock_cli.return_value
        mock_cli_instance.display_main_menu.return_value = "2"
        mock_cli_instance.get_file_path.return_value = temp_files["backlog"]
        mock_cli_instance.get_output_path.return_value = None
        mock_cli_instance.get_confirmation.return_value = True
        
        assistant = UnifiedSmartBacklogAssistant(use_rich_cli=True)
        
        # Mock the processing method
        with patch.object(assistant, 'analyze_backlog_sync') as mock_analyze:
            mock_analyze.return_value = {
                "health_score": 85,
                "recommendations": ["Test recommendation"],
                "success": True
            }
            
            with pytest.raises(SystemExit):
                assistant.run_interactive_mode_sync()

            mock_cli_instance.display_main_menu.assert_called_once()
            mock_analyze.assert_called_once()
    
    def test_caching_integration(self, temp_files):
        """Test caching integration."""
        assistant = UnifiedSmartBacklogAssistant(enable_caching=True)
        
        assert assistant.enable_caching is True
        
        with patch.object(assistant, 'process_meeting_notes_sync', wraps=assistant.process_meeting_notes_sync) as wrapped_process:
            with patch.object(assistant.document_processor, 'process_document') as mock_process_doc:
                mock_process_doc.return_value = Mock(processing_success=True, content="Test content")

                assistant.process_meeting_notes_sync(temp_files["meeting_notes"])
                assistant.process_meeting_notes_sync(temp_files["meeting_notes"])

                assert wrapped_process.call_count == 2
                # The underlying expensive operation should be called once
                assert mock_process_doc.call_count == 1
    
    def test_error_handling_file_not_found(self):
        """Test error handling for file not found."""
        assistant = UnifiedSmartBacklogAssistant()
        
        with pytest.raises(FileNotFoundError):
            assistant.process_meeting_notes_sync("/nonexistent/file.txt")
    
    def test_error_handling_invalid_file_format(self, temp_files):
        """Test error handling for invalid file formats."""
        # Create a binary file
        binary_file = os.path.join(temp_files["dir"], "binary.bin")
        with open(binary_file, 'wb') as f:
            f.write(b'\x00\x01\x02\x03')
        
        assistant = UnifiedSmartBacklogAssistant()
        
        with pytest.raises(ValueError, match="Unsupported file type"):
            assistant.process_meeting_notes_sync(binary_file)
    
    def test_output_file_creation(self, temp_files):
        """Test output file creation."""
        output_file = os.path.join(temp_files["dir"], "output.json")
        
        assistant = UnifiedSmartBacklogAssistant()
        
        with patch.object(assistant, '_load_backlog_data') as mock_load:
            mock_load.return_value = [{"title": "Test item"}]
            
            with patch.object(assistant.backlog_analyzer, 'analyze_backlog_data') as mock_analyze:
                mock_analyze.return_value = BacklogAnalysis(
                    analysis_success=True, total_items=1, health_score=85.0,
                    items_by_priority={}, items_by_status={}, missing_information=[],
                    recommendations=["Test"]
                )
                
                assistant.analyze_backlog_sync(
                    temp_files["backlog"],
                    output_path=output_file
                )
                
                assert os.path.exists(output_file)
                
                with open(output_file, 'r') as f:
                    saved_data = json.load(f)
                    assert "analysis_summary" in saved_data
                    assert saved_data["analysis_summary"]["health_score"] == 85.0
    
    def test_configuration_validation(self):
        """Test configuration validation."""
        assistant = UnifiedSmartBacklogAssistant()
        
        assert hasattr(assistant, 'config')
        assert assistant.logger is not None
        assert assistant.enable_caching in [True, False]
        assert assistant.use_rich_cli in [True, False]
    
    @pytest.mark.asyncio
    async def test_async_context_manager_integration(self):
        """Test async context manager integration."""
        from src.processors.ai_processor import AIProcessor
        
        with patch('src.processors.ai_processor.openai.AsyncOpenAI'):
            async with AIProcessor() as async_ai:
                assert async_ai is not None
                assert hasattr(async_ai, 'extract_requirements')
    
    def test_logging_integration(self, caplog):
        """Test logging integration."""
        import logging
        caplog.set_level(logging.INFO)
        
        assistant = UnifiedSmartBacklogAssistant()
        assistant.logger.info("Test log message")

        assert "Test log message" in caplog.text
    
    def test_performance_monitoring(self, temp_files):
        """Test performance monitoring capabilities."""
        assistant = UnifiedSmartBacklogAssistant()
        
        import time
        start_time = time.time()
        
        with patch.object(assistant, '_load_backlog_data') as mock_load:
            mock_load.return_value = [{"title": "Test"}]
            
            with patch.object(assistant.backlog_analyzer, 'analyze_backlog_data') as mock_analyze:
                mock_analyze.return_value = BacklogAnalysis(
                    analysis_success=True, total_items=1, health_score=85.0,
                    items_by_priority={}, items_by_status={}, missing_information=[],
                    recommendations=[]
                )
                
                assistant.analyze_backlog_sync(temp_files["backlog"])
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                assert processing_time < 1.0

    def test_concurrent_processing_capability(self):
        """Test that the assistant can handle concurrent processing setup."""
        assistant = UnifiedSmartBacklogAssistant()
        
        assert hasattr(assistant, 'process_meeting_notes_async')
        assert hasattr(assistant, 'analyze_backlog_async')
        assert hasattr(assistant, 'process_meeting_notes_sync')
        assert hasattr(assistant, 'analyze_backlog_sync')
    
    def test_feature_flag_combinations(self):
        """Test different feature flag combinations."""
        assistant1 = UnifiedSmartBacklogAssistant(enable_caching=True, use_rich_cli=False)
        assert assistant1.enable_caching is True
        assert assistant1.use_rich_cli is False
        
        assistant2 = UnifiedSmartBacklogAssistant(enable_caching=False, use_rich_cli=True)
        assert assistant2.enable_caching is False
        assert assistant2.use_rich_cli is True
        
        assistant3 = UnifiedSmartBacklogAssistant(enable_caching=False, use_rich_cli=False)
        assert assistant3.enable_caching is False
        assert assistant3.use_rich_cli is False
