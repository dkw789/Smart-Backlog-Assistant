"""Tests for refactored Rich CLI - demonstrating simplified testing with providers."""

import pytest
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestRichCLIRefactored:
    """Test refactored Rich CLI with easy dependency injection."""
    
    def test_cli_with_mock_provider(self):
        """Test CLI with mock provider - no external dependencies."""
        from src.utils.rich_cli import RichCLIInterface
        from src.providers.mock_providers import MockConsoleProvider
        
        mock_provider = MockConsoleProvider()
        cli = RichCLIInterface(console_provider=mock_provider)
        
        # Test availability
        assert cli.is_available() == True
        
        # Test basic message printing
        cli.print_message("Test message", style="blue")
        assert len(mock_provider.messages) == 1
        assert mock_provider.messages[0]["message"] == "Test message"
        assert mock_provider.messages[0]["style"] == "blue"
        
        # Test styled messages
        cli.print_success("Success message")
        cli.print_error("Error message")
        cli.print_warning("Warning message")
        cli.print_info("Info message")
        
        assert len(mock_provider.messages) == 5
        assert "✅ Success message" in mock_provider.messages[1]["message"]
        assert "❌ Error message" in mock_provider.messages[2]["message"]
        assert "⚠️ Warning message" in mock_provider.messages[3]["message"]
        assert "ℹ️ Info message" in mock_provider.messages[4]["message"]
    
    def test_table_display(self):
        """Test table display functionality."""
        from utils.rich_cli_refactored import RichCLIRefactored
        from providers.rich_provider import MockUIProvider
        
        mock_provider = MockUIProvider()
        cli = RichCLIRefactored(ui_provider=mock_provider)
        
        # Test table display
        data = [
            ["Name", "Age", "City"],
            ["John", "30", "New York"],
            ["Jane", "25", "London"]
        ]
        
        table = cli.display_table(data, title="People")
        assert len(mock_provider.tables) == 1
        assert mock_provider.tables[0]["title"] == "People"
        assert mock_provider.tables[0]["data"] == data
        
        # Test empty table
        cli.display_table([], title="Empty")
        # Should print warning about no data
        warning_messages = [msg for msg in mock_provider.messages if "No data" in msg["message"]]
        assert len(warning_messages) > 0
    
    def test_progress_tracking(self):
        """Test progress tracking functionality."""
        from utils.rich_cli_refactored import RichCLIRefactored
        from providers.rich_provider import MockUIProvider
        
        mock_provider = MockUIProvider()
        cli = RichCLIRefactored(ui_provider=mock_provider)
        
        # Test progress workflow
        tracker = cli.start_progress()
        assert tracker is not None
        assert cli.progress_tracker is not None
        
        # Add tasks
        task1 = cli.add_progress_task("Download files", total=100)
        task2 = cli.add_progress_task("Process data", total=50)
        
        assert task1 is not None
        assert task2 is not None
        assert len(tracker.tasks) == 2
        
        # Update progress
        cli.update_progress(task1, advance=25)
        cli.update_progress(task2, completed=30)
        
        assert tracker.tasks[task1]["completed"] == 25
        assert tracker.tasks[task2]["completed"] == 30
        
        # Complete tasks
        cli.complete_progress_task(task1)
        cli.complete_progress_task(task2)
        
        assert tracker.tasks[task1]["completed"] == 100
        assert tracker.tasks[task2]["completed"] == 50
        
        # Stop progress
        cli.stop_progress()
        assert cli.progress_tracker is None
    
    def test_progress_without_tracker(self):
        """Test progress operations without active tracker."""
        from utils.rich_cli_refactored import RichCLIRefactored
        from providers.rich_provider import MockUIProvider
        
        mock_provider = MockUIProvider()
        cli = RichCLIRefactored(ui_provider=mock_provider)
        
        # Try to add task without starting progress
        task_id = cli.add_progress_task("Test task")
        assert task_id is None
        
        # Should have warning message
        warning_messages = [msg for msg in mock_provider.messages if "No active progress" in msg["message"]]
        assert len(warning_messages) > 0
        
        # Update and complete should not crash
        cli.update_progress("fake_id", advance=10)
        cli.complete_progress_task("fake_id")
    
    def test_panel_display(self):
        """Test panel display functionality."""
        from utils.rich_cli_refactored import RichCLIRefactored
        from providers.rich_provider import MockUIProvider
        
        mock_provider = MockUIProvider()
        cli = RichCLIRefactored(ui_provider=mock_provider)
        
        # Test panel display
        cli.display_panel("Test content", title="Test Panel", border_style="blue")
        
        # Should have printed title and content
        title_messages = [msg for msg in mock_provider.messages if "Test Panel" in msg["message"]]
        content_messages = [msg for msg in mock_provider.messages if "Test content" in msg["message"]]
        
        assert len(title_messages) > 0
        assert len(content_messages) > 0
    
    def test_backlog_analysis_display(self):
        """Test backlog analysis results display."""
        from utils.rich_cli_refactored import RichCLIRefactored
        from providers.rich_provider import MockUIProvider
        
        mock_provider = MockUIProvider()
        cli = RichCLIRefactored(ui_provider=mock_provider)
        
        # Test comprehensive analysis display
        analysis_result = {
            'total_items': 10,
            'health_score': 75.5,
            'analysis_success': True,
            'items_by_priority': {'high': 3, 'medium': 4, 'low': 3},
            'items_by_status': {'todo': 4, 'in_progress': 3, 'done': 3},
            'recommendations': [
                'Focus on completing in-progress items',
                'Review high-priority backlog'
            ],
            'risk_factors': [
                'Some items lack estimates',
                'Blocked items may delay delivery'
            ]
        }
        
        cli.display_backlog_analysis(analysis_result)
        
        # Should have multiple tables and messages
        assert len(mock_provider.tables) >= 2  # Summary, priority, status tables
        
        # Should have recommendation and risk messages
        messages_text = ' '.join([msg["message"] for msg in mock_provider.messages])
        assert "Recommendations" in messages_text
        assert "Risk Factors" in messages_text
        assert "Focus on completing" in messages_text
        assert "Some items lack" in messages_text
    
    def test_processing_results_display(self):
        """Test AI processing results display."""
        from utils.rich_cli_refactored import RichCLIRefactored
        from providers.rich_provider import MockUIProvider
        
        mock_provider = MockUIProvider()
        cli = RichCLIRefactored(ui_provider=mock_provider)
        
        # Test successful processing results
        success_results = {
            'success': True,
            'result': 'Analysis completed successfully',
            'input_length': 150,
            'provider': 'openai',
            'requirements': ['User authentication', 'Data validation'],
            'entities': ['User', 'Database', 'API']
        }
        
        cli.display_processing_results(success_results)
        
        # Should have tables and requirement/entity lists
        assert len(mock_provider.tables) >= 1  # Metadata table
        
        messages_text = ' '.join([msg["message"] for msg in mock_provider.messages])
        assert "Processing Complete" in messages_text
        assert "Requirements" in messages_text
        assert "Entities" in messages_text
        assert "User authentication" in messages_text
        
        # Test failed processing results
        mock_provider.messages.clear()
        mock_provider.tables.clear()
        
        failure_results = {
            'success': False,
            'error': 'API connection failed'
        }
        
        cli.display_processing_results(failure_results)
        
        messages_text = ' '.join([msg["message"] for msg in mock_provider.messages])
        assert "Processing Failed" in messages_text
        assert "API connection failed" in messages_text
    
    def test_user_prompt(self):
        """Test user prompting functionality."""
        from utils.rich_cli_refactored import RichCLIRefactored
        from providers.rich_provider import MockUIProvider
        
        mock_provider = MockUIProvider()
        cli = RichCLIRefactored(ui_provider=mock_provider)
        
        # Test prompt with choices
        choices = ["Option 1", "Option 2", "Option 3"]
        result = cli.prompt_user("Select an option:", choices)
        
        # Should return first choice as default
        assert result == "Option 1"
        
        # Should have printed prompt and choices
        messages_text = ' '.join([msg["message"] for msg in mock_provider.messages])
        assert "Select an option" in messages_text
        assert "Option 1" in messages_text
        assert "Option 2" in messages_text
        
        # Test prompt without choices
        mock_provider.messages.clear()
        result = cli.prompt_user("Enter something:")
        assert result == "default"
    
    def test_error_handling(self):
        """Test error handling in CLI operations."""
        from utils.rich_cli_refactored import RichCLIRefactored
        from providers.rich_provider import MockUIProvider
        
        # Create failing mock provider
        class FailingMockProvider(MockUIProvider):
            def print_message(self, message, style=None):
                raise Exception("Mock UI failure")
            
            def format_table(self, data, title=None):
                raise Exception("Mock table failure")
        
        failing_provider = FailingMockProvider()
        cli = RichCLIRefactored(ui_provider=failing_provider)
        
        # Should handle print failures gracefully
        cli.print_message("Test message")  # Should not crash
        
        # Should handle table failures gracefully
        data = [["Header"], ["Data"]]
        cli.display_table(data, title="Test")  # Should not crash
    
    def test_status_display(self):
        """Test status display functionality."""
        from utils.rich_cli_refactored import RichCLIRefactored
        from providers.rich_provider import MockUIProvider
        
        mock_provider = MockUIProvider()
        cli = RichCLIRefactored(ui_provider=mock_provider)
        
        # Test status display
        status = cli.display_status("Processing...", spinner="dots")
        
        # Should have printed info message as fallback
        info_messages = [msg for msg in mock_provider.messages if "Status: Processing" in msg["message"]]
        assert len(info_messages) > 0
    
    def test_provider_status(self):
        """Test provider status functionality."""
        from utils.rich_cli_refactored import RichCLIRefactored
        from providers.rich_provider import MockUIProvider
        
        mock_provider = MockUIProvider()
        cli = RichCLIRefactored(ui_provider=mock_provider)
        
        # Test status
        status = cli.get_provider_status()
        assert "provider_config" in status
        assert status["is_available"] == True
        assert status["cli_ready"] == True
        assert status["progress_active"] == False
        assert status["provider_config"]["provider"] == "mock"
        
        # Test with active progress
        cli.start_progress()
        status = cli.get_provider_status()
        assert status["progress_active"] == True
    
    def test_comprehensive_workflow(self):
        """Test a comprehensive CLI workflow."""
        from utils.rich_cli_refactored import RichCLIRefactored
        from providers.rich_provider import MockUIProvider
        
        mock_provider = MockUIProvider()
        cli = RichCLIRefactored(ui_provider=mock_provider)
        
        # Simulate a complete workflow
        cli.print_info("Starting analysis workflow...")
        
        # Start progress
        tracker = cli.start_progress()
        task1 = cli.add_progress_task("Loading data", total=100)
        task2 = cli.add_progress_task("Processing", total=50)
        
        # Simulate progress
        cli.update_progress(task1, advance=50)
        cli.update_progress(task2, advance=25)
        
        # Display some results
        data = [["Item", "Status"], ["Task 1", "Complete"], ["Task 2", "In Progress"]]
        cli.display_table(data, title="Current Status")
        
        # Complete tasks
        cli.complete_progress_task(task1)
        cli.complete_progress_task(task2)
        cli.stop_progress()
        
        # Display final results
        cli.print_success("Workflow completed successfully!")
        
        # Verify workflow executed
        assert len(mock_provider.messages) >= 2  # At least start and success messages
        assert len(mock_provider.tables) >= 1
        assert tracker.tasks[task1]["completed"] == 100
        assert tracker.tasks[task2]["completed"] == 50
        
        success_messages = [msg for msg in mock_provider.messages if "successfully" in msg["message"]]
        assert len(success_messages) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
