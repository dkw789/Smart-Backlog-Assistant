"""Tests for the UnifiedSmartBacklogAssistant."""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.main_unified import UnifiedSmartBacklogAssistant


class TestUnifiedSmartBacklogAssistant:
    """Test the UnifiedSmartBacklogAssistant class."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        with patch('src.main_unified.config') as mock_config:
            mock_config.openai_api_key = "test-openai-key"
            mock_config.anthropic_api_key = "test-anthropic-key"
            mock_config.enable_caching = True
            mock_config.debug_mode = False
            yield mock_config

    @pytest.fixture
    def temp_files(self):
        """Create temporary files for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test input file
            input_file = temp_path / "test_input.txt"
            input_file.write_text("Test meeting notes content")
            
            # Create test output file path
            output_file = temp_path / "test_output.json"
            
            yield {
                "input": str(input_file),
                "output": str(output_file),
                "dir": temp_dir
            }

    def test_assistant_initialization_sync(self, mock_config):
        """Test assistant initialization in sync mode."""
        with patch('src.main_unified.SmartBacklogAssistant') as mock_sync_assistant:
            mock_instance = Mock()
            mock_sync_assistant.return_value = mock_instance
            
            assistant = UnifiedSmartBacklogAssistant(use_async=False)
            
            assert assistant.use_async is False
            assert assistant.sync_assistant == mock_instance
            assert assistant.async_processor is None
            mock_sync_assistant.assert_called_once()

    def test_assistant_initialization_async(self, mock_config):
        """Test assistant initialization in async mode."""
        with patch('src.main_unified.AsyncAIProcessor') as mock_async_processor, \
             patch('src.main_unified.SmartBacklogAssistant'):
            
            mock_processor = Mock()
            mock_async_processor.return_value = mock_processor
            
            assistant = UnifiedSmartBacklogAssistant(use_async=True)
            
            assert assistant.use_async is True
            assert assistant.async_processor == mock_processor
            mock_async_processor.assert_called_once()

    def test_assistant_initialization_with_options(self, mock_config):
        """Test assistant initialization with various options."""
        with patch('src.main_unified.SmartBacklogAssistant'), \
             patch('src.main_unified.AsyncAIProcessor'), \
             patch('src.main_unified.CacheManager') as mock_cache, \
             patch('src.main_unified.CircuitBreaker') as mock_circuit:
            
            assistant = UnifiedSmartBacklogAssistant(
                use_async=True,
                enable_caching=True,
                enable_circuit_breaker=True,
                use_rich_cli=True
            )
            
            assert assistant.use_async is True
            assert assistant.enable_caching is True
            assert assistant.enable_circuit_breaker is True
            assert assistant.use_rich_cli is True

    def test_process_meeting_notes_sync(self, mock_config, temp_files):
        """Test processing meeting notes in sync mode."""
        with patch('src.main_unified.SmartBacklogAssistant') as mock_sync_assistant:
            mock_instance = Mock()
            mock_result = {"requirements": ["req1", "req2"], "user_stories": []}
            mock_instance.process_meeting_notes.return_value = mock_result
            mock_sync_assistant.return_value = mock_instance
            
            assistant = UnifiedSmartBacklogAssistant(use_async=False)
            
            result = assistant.process_meeting_notes(
                temp_files["input"], 
                temp_files["output"]
            )
            
            assert result == mock_result
            mock_instance.process_meeting_notes.assert_called_once_with(
                temp_files["input"], 
                temp_files["output"]
            )

    @pytest.mark.asyncio
    async def test_process_meeting_notes_async(self, mock_config, temp_files):
        """Test processing meeting notes in async mode."""
        with patch('src.main_unified.AsyncAIProcessor') as mock_async_processor, \
             patch('src.main_unified.SmartBacklogAssistant'), \
             patch('src.main_unified.DocumentProcessor') as mock_doc_processor, \
             patch('src.main_unified.UserStoryGenerator') as mock_story_gen, \
             patch('builtins.open', create=True) as mock_open:
            
            # Mock file operations
            mock_open.return_value.__enter__.return_value.read.return_value = "test content"
            
            # Mock processors
            mock_processor = AsyncMock()
            mock_processor.extract_requirements.return_value = Mock(
                success=True, content="extracted requirements"
            )
            mock_processor.generate_user_stories.return_value = Mock(
                success=True, content="generated stories"
            )
            mock_async_processor.return_value = mock_processor
            
            mock_doc = Mock()
            mock_doc.extract_text.return_value = "document text"
            mock_doc_processor.return_value = mock_doc
            
            mock_generator = Mock()
            mock_generator.parse_stories_from_text.return_value = [
                {"title": "Story 1", "description": "Test story"}
            ]
            mock_story_gen.return_value = mock_generator
            
            assistant = UnifiedSmartBacklogAssistant(use_async=True)
            
            result = await assistant.process_meeting_notes_async(
                temp_files["input"],
                temp_files["output"]
            )
            
            assert result is not None
            assert "requirements" in result
            assert "user_stories" in result
            mock_processor.extract_requirements.assert_called_once()
            mock_processor.generate_user_stories.assert_called_once()

    def test_analyze_backlog_sync(self, mock_config, temp_files):
        """Test backlog analysis in sync mode."""
        # Create test backlog file
        backlog_file = Path(temp_files["dir"]) / "backlog.json"
        backlog_file.write_text('{"items": [{"title": "Test Item"}]}')
        
        with patch('src.main_unified.SmartBacklogAssistant') as mock_sync_assistant:
            mock_instance = Mock()
            mock_result = {"analysis": "test analysis", "health_score": 85}
            mock_instance.analyze_backlog.return_value = mock_result
            mock_sync_assistant.return_value = mock_instance
            
            assistant = UnifiedSmartBacklogAssistant(use_async=False)
            
            result = assistant.analyze_backlog(
                str(backlog_file),
                temp_files["output"]
            )
            
            assert result == mock_result
            mock_instance.analyze_backlog.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_backlog_async(self, mock_config, temp_files):
        """Test backlog analysis in async mode."""
        # Create test backlog file
        backlog_file = Path(temp_files["dir"]) / "backlog.json"
        backlog_file.write_text('{"items": [{"title": "Test Item", "description": "Test"}]}')
        
        with patch('src.main_unified.AsyncAIProcessor') as mock_async_processor, \
             patch('src.main_unified.SmartBacklogAssistant'), \
             patch('src.main_unified.BacklogAnalyzer') as mock_analyzer, \
             patch('builtins.open', create=True) as mock_open:
            
            # Mock file operations
            mock_open.return_value.__enter__.return_value.read.return_value = '{"items": []}'
            
            # Mock async processor
            mock_processor = AsyncMock()
            mock_processor.analyze_backlog_items.return_value = Mock(
                success=True, content="analysis results"
            )
            mock_async_processor.return_value = mock_processor
            
            # Mock backlog analyzer
            mock_analyzer_instance = Mock()
            mock_analyzer_instance.extract_backlog_from_json.return_value = [
                {"title": "Test Item", "description": "Test"}
            ]
            mock_analyzer_instance.analyze_backlog_data.return_value = Mock(
                health_score=85,
                total_items=1,
                recommendations=["test recommendation"]
            )
            mock_analyzer.return_value = mock_analyzer_instance
            
            assistant = UnifiedSmartBacklogAssistant(use_async=True)
            
            result = await assistant.analyze_backlog_async(
                str(backlog_file),
                temp_files["output"]
            )
            
            assert result is not None
            assert "analysis" in result
            mock_processor.analyze_backlog_items.assert_called_once()

    def test_generate_sprint_plan_sync(self, mock_config, temp_files):
        """Test sprint plan generation in sync mode."""
        # Create test backlog file
        backlog_file = Path(temp_files["dir"]) / "backlog.json"
        backlog_file.write_text('{"items": [{"title": "Test Item", "priority": "high"}]}')
        
        with patch('src.main_unified.SmartBacklogAssistant') as mock_sync_assistant:
            mock_instance = Mock()
            mock_result = {"sprint_plan": "test plan", "capacity": 40}
            mock_instance.generate_sprint_plan.return_value = mock_result
            mock_sync_assistant.return_value = mock_instance
            
            assistant = UnifiedSmartBacklogAssistant(use_async=False)
            
            result = assistant.generate_sprint_plan(
                str(backlog_file),
                capacity=40,
                output_path=temp_files["output"]
            )
            
            assert result == mock_result
            mock_instance.generate_sprint_plan.assert_called_once_with(
                str(backlog_file),
                40,
                temp_files["output"]
            )

    def test_process_requirements_document_sync(self, mock_config, temp_files):
        """Test requirements document processing in sync mode."""
        with patch('src.main_unified.SmartBacklogAssistant') as mock_sync_assistant:
            mock_instance = Mock()
            mock_result = {"requirements": ["req1"], "backlog_items": []}
            mock_instance.process_requirements_document.return_value = mock_result
            mock_sync_assistant.return_value = mock_instance
            
            assistant = UnifiedSmartBacklogAssistant(use_async=False)
            
            result = assistant.process_requirements_document(
                temp_files["input"],
                temp_files["output"]
            )
            
            assert result == mock_result
            mock_instance.process_requirements_document.assert_called_once()

    def test_run_interactive_mode_sync(self, mock_config):
        """Test interactive mode in sync mode."""
        with patch('src.main_unified.SmartBacklogAssistant') as mock_sync_assistant, \
             patch('src.main_unified.RichCLI') as mock_rich_cli:
            
            mock_instance = Mock()
            mock_sync_assistant.return_value = mock_instance
            
            mock_cli = Mock()
            mock_rich_cli.return_value = mock_cli
            
            assistant = UnifiedSmartBacklogAssistant(use_async=False, use_rich_cli=True)
            
            # Mock user input to exit immediately
            with patch('builtins.input', side_effect=['4']):  # Exit option
                assistant.run_interactive_mode()
            
            mock_rich_cli.assert_called_once()

    def test_run_interactive_mode_no_cli(self, mock_config):
        """Test interactive mode without rich CLI."""
        with patch('src.main_unified.SmartBacklogAssistant') as mock_sync_assistant:
            mock_instance = Mock()
            mock_sync_assistant.return_value = mock_instance
            
            assistant = UnifiedSmartBacklogAssistant(use_async=False, use_rich_cli=False)
            
            # Mock user input to exit immediately
            with patch('builtins.input', side_effect=['4']):  # Exit option
                assistant.run_interactive_mode()

    @pytest.mark.asyncio
    async def test_run_interactive_mode_async(self, mock_config):
        """Test interactive mode in async mode."""
        with patch('src.main_unified.AsyncAIProcessor') as mock_async_processor, \
             patch('src.main_unified.SmartBacklogAssistant'), \
             patch('src.main_unified.RichCLI') as mock_rich_cli:
            
            mock_processor = AsyncMock()
            mock_async_processor.return_value = mock_processor
            
            mock_cli = Mock()
            mock_rich_cli.return_value = mock_cli
            
            assistant = UnifiedSmartBacklogAssistant(use_async=True, use_rich_cli=True)
            
            # Mock user input to exit immediately
            with patch('builtins.input', side_effect=['4']):  # Exit option
                await assistant.run_interactive_mode_async()

    def test_caching_integration(self, mock_config):
        """Test caching integration."""
        with patch('src.main_unified.SmartBacklogAssistant'), \
             patch('src.main_unified.CacheManager') as mock_cache_manager:
            
            mock_cache = Mock()
            mock_cache_manager.return_value = mock_cache
            
            assistant = UnifiedSmartBacklogAssistant(
                use_async=False,
                enable_caching=True
            )
            
            assert assistant.enable_caching is True
            mock_cache_manager.assert_called_once()

    def test_circuit_breaker_integration(self, mock_config):
        """Test circuit breaker integration."""
        with patch('src.main_unified.SmartBacklogAssistant'), \
             patch('src.main_unified.CircuitBreaker') as mock_circuit_breaker:
            
            mock_circuit = Mock()
            mock_circuit_breaker.return_value = mock_circuit
            
            assistant = UnifiedSmartBacklogAssistant(
                use_async=False,
                enable_circuit_breaker=True
            )
            
            assert assistant.enable_circuit_breaker is True
            mock_circuit_breaker.assert_called_once()

    def test_error_handling_sync(self, mock_config, temp_files):
        """Test error handling in sync mode."""
        with patch('src.main_unified.SmartBacklogAssistant') as mock_sync_assistant:
            mock_instance = Mock()
            mock_instance.process_meeting_notes.side_effect = Exception("Test error")
            mock_sync_assistant.return_value = mock_instance
            
            assistant = UnifiedSmartBacklogAssistant(use_async=False)
            
            with pytest.raises(Exception, match="Test error"):
                assistant.process_meeting_notes(
                    temp_files["input"],
                    temp_files["output"]
                )

    @pytest.mark.asyncio
    async def test_error_handling_async(self, mock_config, temp_files):
        """Test error handling in async mode."""
        with patch('src.main_unified.AsyncAIProcessor') as mock_async_processor, \
             patch('src.main_unified.SmartBacklogAssistant'), \
             patch('src.main_unified.DocumentProcessor') as mock_doc_processor:
            
            # Mock document processor to raise an error
            mock_doc_processor.side_effect = Exception("Document processing error")
            
            assistant = UnifiedSmartBacklogAssistant(use_async=True)
            
            with pytest.raises(Exception, match="Document processing error"):
                await assistant.process_meeting_notes_async(
                    temp_files["input"],
                    temp_files["output"]
                )

    def test_file_operations(self, mock_config, temp_files):
        """Test file operations and validation."""
        with patch('src.main_unified.SmartBacklogAssistant') as mock_sync_assistant:
            mock_instance = Mock()
            mock_sync_assistant.return_value = mock_instance
            
            assistant = UnifiedSmartBacklogAssistant(use_async=False)
            
            # Test with non-existent file
            with pytest.raises(FileNotFoundError):
                assistant.process_meeting_notes(
                    "/non/existent/file.txt",
                    temp_files["output"]
                )

    def test_output_file_creation(self, mock_config, temp_files):
        """Test output file creation."""
        with patch('src.main_unified.SmartBacklogAssistant') as mock_sync_assistant, \
             patch('builtins.open', create=True) as mock_open, \
             patch('json.dump') as mock_json_dump:
            
            mock_instance = Mock()
            mock_result = {"test": "result"}
            mock_instance.process_meeting_notes.return_value = mock_result
            mock_sync_assistant.return_value = mock_instance
            
            assistant = UnifiedSmartBacklogAssistant(use_async=False)
            
            result = assistant.process_meeting_notes(
                temp_files["input"],
                temp_files["output"]
            )
            
            assert result == mock_result

    def test_configuration_validation(self):
        """Test configuration validation."""
        with patch('src.main_unified.config') as mock_config:
            mock_config.openai_api_key = None
            mock_config.anthropic_api_key = None
            
            # Should still initialize but may have limited functionality
            with patch('src.main_unified.SmartBacklogAssistant'):
                assistant = UnifiedSmartBacklogAssistant(use_async=False)
                assert assistant is not None

    def test_async_context_manager_integration(self, mock_config):
        """Test async context manager integration."""
        with patch('src.main_unified.AsyncAIProcessor') as mock_async_processor, \
             patch('src.main_unified.SmartBacklogAssistant'):
            
            mock_processor = AsyncMock()
            mock_async_processor.return_value = mock_processor
            
            assistant = UnifiedSmartBacklogAssistant(use_async=True)
            
            # Verify async processor is available
            assert assistant.async_processor == mock_processor

    def test_logging_integration(self, mock_config):
        """Test logging integration."""
        with patch('src.main_unified.SmartBacklogAssistant'), \
             patch('src.main_unified.get_logger') as mock_get_logger:
            
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            assistant = UnifiedSmartBacklogAssistant(use_async=False)
            
            # Logger should be initialized
            mock_get_logger.assert_called()

    def test_performance_monitoring(self, mock_config, temp_files):
        """Test performance monitoring capabilities."""
        with patch('src.main_unified.SmartBacklogAssistant') as mock_sync_assistant, \
             patch('time.time', side_effect=[0, 1.5]):  # Mock timing
            
            mock_instance = Mock()
            mock_result = {"test": "result"}
            mock_instance.process_meeting_notes.return_value = mock_result
            mock_sync_assistant.return_value = mock_instance
            
            assistant = UnifiedSmartBacklogAssistant(use_async=False)
            
            result = assistant.process_meeting_notes(
                temp_files["input"],
                temp_files["output"]
            )
            
            # Should complete successfully with timing
            assert result == mock_result

    @pytest.mark.asyncio
    async def test_concurrent_processing_capability(self, mock_config):
        """Test concurrent processing capabilities."""
        with patch('src.main_unified.AsyncAIProcessor') as mock_async_processor, \
             patch('src.main_unified.SmartBacklogAssistant'):
            
            mock_processor = AsyncMock()
            mock_processor.process_multiple_items_concurrently.return_value = [
                Mock(success=True, content="result1"),
                Mock(success=True, content="result2")
            ]
            mock_async_processor.return_value = mock_processor
            
            assistant = UnifiedSmartBacklogAssistant(use_async=True)
            
            # Test that concurrent processing is available
            async with assistant.async_processor as processor:
                results = await processor.process_multiple_items_concurrently(
                    [{"description": "item1"}, {"description": "item2"}],
                    "assess_priority"
                )
                
                assert len(results) == 2
                assert all(result.success for result in results)

    def test_feature_flag_combinations(self, mock_config):
        """Test different combinations of feature flags."""
        with patch('src.main_unified.SmartBacklogAssistant'), \
             patch('src.main_unified.AsyncAIProcessor'), \
             patch('src.main_unified.CacheManager'), \
             patch('src.main_unified.CircuitBreaker'), \
             patch('src.main_unified.RichCLI'):
            
            # Test all features enabled
            assistant1 = UnifiedSmartBacklogAssistant(
                use_async=True,
                enable_caching=True,
                enable_circuit_breaker=True,
                use_rich_cli=True
            )
            
            assert assistant1.use_async is True
            assert assistant1.enable_caching is True
            assert assistant1.enable_circuit_breaker is True
            assert assistant1.use_rich_cli is True
            
            # Test minimal configuration
            assistant2 = UnifiedSmartBacklogAssistant(
                use_async=False,
                enable_caching=False,
                enable_circuit_breaker=False,
                use_rich_cli=False
            )
            
            assert assistant2.use_async is False
            assert assistant2.enable_caching is False
            assert assistant2.enable_circuit_breaker is False
            assert assistant2.use_rich_cli is False
