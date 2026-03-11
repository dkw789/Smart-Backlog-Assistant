"""Comprehensive tests to boost coverage."""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch
from src.processors.document_processor import DocumentProcessor, ProcessedDocument
from src.processors.backlog_analyzer import BacklogAnalyzer
from src.generators.priority_engine import PriorityEngine
from src.generators.user_story_generator import UserStoryGenerator
from src.utils.file_handler import FileHandler
from src.utils.logger_service import get_logger


class TestDocumentProcessor:
    """Test DocumentProcessor."""
    
    def test_init(self):
        """Test initialization."""
        processor = DocumentProcessor()
        assert processor is not None
    
    def test_process_text_file(self):
        """Test processing text file."""
        processor = DocumentProcessor()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content")
            temp_file = f.name
        
        try:
            result = processor.process_document(temp_file)
            assert result.processing_success is True
            assert "Test content" in result.content
        finally:
            os.unlink(temp_file)


class TestBacklogAnalyzer:
    """Test BacklogAnalyzer."""
    
    def test_init(self):
        """Test initialization."""
        analyzer = BacklogAnalyzer()
        assert analyzer is not None
    
    def test_analyze_empty_backlog(self):
        """Test analyzing empty backlog."""
        analyzer = BacklogAnalyzer()
        result = analyzer.analyze_backlog_data([])
        assert result.total_items == 0
    
    def test_analyze_backlog_with_items(self):
        """Test analyzing backlog with items."""
        analyzer = BacklogAnalyzer()
        items = [
            {"title": "Item 1", "description": "Desc 1", "priority": "high", "status": "todo"},
            {"title": "Item 2", "description": "Desc 2", "priority": "medium", "status": "in_progress"}
        ]
        result = analyzer.analyze_backlog_data(items)
        assert result.total_items == 2
        assert result.health_score > 0


class TestPriorityEngine:
    """Test PriorityEngine."""
    
    def test_init(self):
        """Test initialization."""
        engine = PriorityEngine()
        assert engine is not None
    
    def test_calculate_priority_score(self):
        """Test priority score calculation."""
        engine = PriorityEngine()
        item = {"title": "Test", "description": "Test desc", "priority": "high"}
        score = engine._calculate_priority_score(item)
        assert score > 0


class TestUserStoryGenerator:
    """Test UserStoryGenerator."""
    
    def test_init(self):
        """Test initialization."""
        generator = UserStoryGenerator()
        assert generator is not None


class TestFileHandler:
    """Test FileHandler."""
    
    def test_read_write_json(self):
        """Test JSON read/write."""
        handler = FileHandler()
        
        data = {"test": "data", "number": 123}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            handler.write_json_file(temp_file, data)
            result = handler.read_json_file(temp_file)
            assert result["test"] == "data"
            assert result["number"] == 123
        finally:
            os.unlink(temp_file)
    
    def test_read_file_content(self):
        """Test reading file content."""
        handler = FileHandler()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content line 1\nTest content line 2")
            temp_file = f.name
        
        try:
            content = handler.read_file_content(temp_file)
            assert "Test content line 1" in content
            assert "Test content line 2" in content
        finally:
            os.unlink(temp_file)


class TestLogger:
    """Test logger service."""
    
    def test_get_logger(self):
        """Test getting logger."""
        logger = get_logger(__name__)
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'debug')



class TestProcessedDocument:
    """Test ProcessedDocument model."""
    
    def test_create_processed_document(self):
        """Test creating ProcessedDocument."""
        doc = ProcessedDocument(
            content="Test content",
            file_type="text",
            metadata={"pages": 1},
            processing_success=True
        )
        assert doc.content == "Test content"
        assert doc.file_type == "text"
        assert doc.processing_success is True
        assert doc.metadata["pages"] == 1
    
    def test_processed_document_with_error(self):
        """Test ProcessedDocument with error."""
        doc = ProcessedDocument(
            content="",
            file_type="text",
            metadata={},
            processing_success=False,
            error_message="Processing failed"
        )
        assert doc.processing_success is False
        assert doc.error_message == "Processing failed"


class TestCachingSystem:
    """Test caching system."""
    
    def test_cache_import(self):
        """Test cache imports."""
        from src.utils.caching_system import default_cache, ai_response_cache
        assert default_cache is not None
        assert ai_response_cache is not None
    
    def test_cache_operations(self):
        """Test basic cache operations."""
        from src.utils.caching_system import default_cache
        
        # Set and get
        default_cache.set("test_key", "test_value", ttl=60)
        result = default_cache.get("test_key")
        assert result == "test_value"
        
        # Clear
        default_cache.clear()
        result = default_cache.get("test_key")
        assert result is None


class TestEnhancedErrorHandler:
    """Test enhanced error handler."""
    
    def test_resilient_service_manager_import(self):
        """Test importing resilient service manager."""
        from src.utils.enhanced_error_handler import resilient_service_manager
        assert resilient_service_manager is not None
    
    def test_circuit_breaker_config(self):
        """Test CircuitBreakerConfig."""
        from src.utils.enhanced_error_handler import CircuitBreakerConfig
        
        config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=60.0,
            success_threshold=2
        )
        assert config.failure_threshold == 3
        assert config.recovery_timeout == 60.0
        assert config.success_threshold == 2


class TestExceptionHandler:
    """Test exception handler."""
    
    def test_backlog_assistant_error(self):
        """Test BacklogAssistantError."""
        from src.utils.exception_handler import BacklogAssistantError
        
        error = BacklogAssistantError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)
    
    def test_ai_processing_error(self):
        """Test AIProcessingError."""
        from src.utils.exception_handler import AIProcessingError
        
        error = AIProcessingError("AI processing failed")
        assert str(error) == "AI processing failed"
    
    def test_document_processing_error(self):
        """Test DocumentProcessingError."""
        from src.utils.exception_handler import DocumentProcessingError
        
        error = DocumentProcessingError("Document processing failed")
        assert str(error) == "Document processing failed"
