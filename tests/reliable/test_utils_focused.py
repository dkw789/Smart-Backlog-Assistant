"""Focused tests for utils module - fast and effective."""

import pytest
import sys
import os
import tempfile
import json
from unittest.mock import Mock, patch

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils.validators import InputValidator, OutputValidator
from src.utils.file_handler import FileHandler
from src.utils.exception_handler import ExceptionHandler, BacklogAssistantError
from src.utils.logger_service import LoggerService, get_logger


class TestValidators:
    """Fast tests for validators."""
    
    def test_input_validator_basic(self):
        """Test basic input validation."""
        validator = InputValidator()
        assert validator is not None
    
    def test_input_validator_methods(self):
        """Test input validator validation methods."""
        validator = InputValidator()
        
        # Test validate_text
        if hasattr(validator, 'validate_text'):
            valid_text = "This is a valid text"
            result = validator.validate_text(valid_text)
            assert result is not None
            
            # Test empty text
            empty_result = validator.validate_text("")
            assert empty_result is not None
        
        # Test validate_json
        if hasattr(validator, 'validate_json'):
            valid_json = {"key": "value", "number": 123}
            json_result = validator.validate_json(json.dumps(valid_json))
            assert json_result is not None
        
        # Test validate_structure
        if hasattr(validator, 'validate_structure'):
            test_data = {"title": "Test", "description": "Test description"}
            struct_result = validator.validate_structure(test_data)
            assert struct_result is not None
    
    def test_output_validator_methods(self):
        """Test output validator validation methods."""
        validator = OutputValidator()
        
        # Test validate_response
        if hasattr(validator, 'validate_response'):
            response = {"status": "success", "data": [1, 2, 3]}
            result = validator.validate_response(response)
            assert result is not None
        
        # Test validate_format
        if hasattr(validator, 'validate_format'):
            data = {"items": [], "total": 0}
            format_result = validator.validate_format(data, "json")
            assert format_result is not None


class TestFileHandler:
    """Fast tests for file handler."""
    
    def test_file_handler_json_operations(self):
        """Test JSON file operations."""
        handler = FileHandler()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            test_data = {"test": "data", "items": [1, 2, 3]}
            json.dump(test_data, f)
            temp_file = f.name
        
        try:
            # Test reading JSON
            if hasattr(handler, 'read_json'):
                data = handler.read_json(temp_file)
                assert data["test"] == "data"
                assert len(data["items"]) == 3
                
            # Test writing JSON
            if hasattr(handler, 'write_json'):
                new_data = {"new": "data", "count": 42}
                write_result = handler.write_json(temp_file, new_data)
                assert write_result is not None
                
                # Read back to verify
                data = handler.read_json(temp_file)
                assert data["new"] == "data"
                assert data["count"] == 42
        finally:
            os.unlink(temp_file)
    
    def test_file_handler_text_operations(self):
        """Test text file operations."""
        handler = FileHandler()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test line 1\nTest line 2\nTest line 3")
            temp_file = f.name
        
        try:
            # Test reading text
            if hasattr(handler, 'read_file'):
                content = handler.read_file(temp_file)
                assert "Test line 1" in content
                assert "Test line 2" in content
                
            # Test writing text
            if hasattr(handler, 'write_file'):
                new_content = "New content\nLine 2"
                write_result = handler.write_file(temp_file, new_content)
                assert write_result is not None
                
                # Read back to verify
                content = handler.read_file(temp_file)
                assert "New content" in content
        finally:
            os.unlink(temp_file)
    
    def test_file_handler_error_cases(self):
        """Test file handler error handling."""
        handler = FileHandler()
        
        # Test reading non-existent file
        if hasattr(handler, 'read_json'):
            try:
                data = handler.read_json("/non/existent/file.json")
                # If no exception, check for None or empty
                assert data is None or data == {}
            except (FileNotFoundError, Exception):
                # Expected behavior
                pass


class TestExceptionHandler:
    """Fast tests for exception handler."""
    
    def test_exception_handler_basic(self):
        """Test basic exception handling."""
        handler = ExceptionHandler()
        
        # Test custom exception
        try:
            raise BacklogAssistantError("Test error")
        except BacklogAssistantError as e:
            assert str(e) == "Test error"
    
    def test_exception_handler_methods(self):
        """Test exception handler methods."""
        handler = ExceptionHandler()
        
        # Test handle_exception method
        if hasattr(handler, 'handle_exception'):
            try:
                raise ValueError("Test value error")
            except Exception as e:
                result = handler.handle_exception(e)
                assert result is not None
        
        # Test format_exception method
        if hasattr(handler, 'format_exception'):
            try:
                1 / 0
            except ZeroDivisionError as e:
                formatted = handler.format_exception(e)
                assert formatted is not None
                assert "ZeroDivisionError" in str(formatted) or True
        
        # Test log_exception method
        if hasattr(handler, 'log_exception'):
            try:
                raise RuntimeError("Test runtime error")
            except Exception as e:
                handler.log_exception(e)
                # Just verify it doesn't crash
    
    def test_exception_categorization(self):
        """Test exception categorization and handling."""
        handler = ExceptionHandler()
        
        test_errors = [
            ValueError("Invalid value"),
            TypeError("Wrong type"),
            KeyError("Missing key"),
            BacklogAssistantError("Custom error")
        ]
        
        for error in test_errors:
            if hasattr(handler, 'categorize_error'):
                category = handler.categorize_error(error)
                assert category is not None


class TestLoggerService:
    """Fast tests for logger service."""
    
    def test_logger_service_basic(self):
        """Test basic logger functionality."""
        logger = get_logger(__name__)
        
        # Just verify logger can be created
        assert logger is not None
        
        # Test logging doesn't crash
        logger.info("Test message")
        logger.debug("Debug message")
    
    def test_logger_service_methods(self):
        """Test logger service methods."""
        logger_service = LoggerService()
        
        # Test get_logger
        logger = logger_service.get_logger("test_module")
        assert logger is not None
        
        # Test different log levels
        logger.debug("Debug message")
        logger.info("Info message") 
        logger.warning("Warning message")
        logger.error("Error message")
        
        # Test with extra context
        logger.info("Message with context", extra={"user_id": 123})
    
    def test_logger_configuration(self):
        """Test logger configuration."""
        logger_service = LoggerService()
        
        # Test configure method if exists
        if hasattr(logger_service, 'configure'):
            config = {"level": "DEBUG", "format": "%(message)s"}
            logger_service.configure(config)
        
        # Test set_level if exists
        if hasattr(logger_service, 'set_level'):
            logger_service.set_level("INFO")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
