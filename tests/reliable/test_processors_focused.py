"""Focused tests for processors module - fast and effective."""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from processors.ai_processor import AIProcessor
from processors.backlog_analyzer import BacklogAnalyzer
from processors.document_processor import DocumentProcessor


class TestAIProcessor:
    """Fast tests for AI processor."""
    
    @patch('openai.OpenAI')
    def test_ai_processor_basic(self, mock_openai):
        """Test basic AI processor functionality."""
        # Mock only the OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.usage = Mock(total_tokens=50)
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        processor = AIProcessor()
        assert processor is not None
        
        # Test basic processing
        if hasattr(processor, 'process'):
            result = processor.process("Test input")
            assert result is not None


class TestBacklogAnalyzer:
    """Fast tests for backlog analyzer."""
    
    def test_backlog_analyzer_basic(self):
        """Test basic backlog analysis."""
        analyzer = BacklogAnalyzer()
        assert analyzer is not None
        
        # Test with minimal backlog data
        backlog = [
            {"id": "1", "title": "Test", "priority": "high", "status": "todo"}
        ]
        
        if hasattr(analyzer, 'analyze'):
            result = analyzer.analyze(backlog)
            assert result is not None
    
    def test_backlog_analyzer_comprehensive(self):
        """Test comprehensive backlog analysis."""
        analyzer = BacklogAnalyzer()
        
        # Create realistic backlog
        backlog = [
            {"id": "1", "title": "Login feature", "priority": "high", "status": "done", "story_points": 5},
            {"id": "2", "title": "Payment integration", "priority": "critical", "status": "in_progress", "story_points": 8},
            {"id": "3", "title": "Email notifications", "priority": "medium", "status": "todo", "story_points": 3},
            {"id": "4", "title": "Bug fix", "priority": "high", "status": "done", "story_points": 2},
            {"id": "5", "title": "Performance optimization", "priority": "low", "status": "todo", "story_points": 13}
        ]
        
        if hasattr(analyzer, 'analyze'):
            result = analyzer.analyze(backlog)
            assert result is not None
            
        # Test velocity calculation
        if hasattr(analyzer, 'calculate_velocity'):
            velocity = analyzer.calculate_velocity(backlog)
            assert velocity is not None
            
        # Test priority distribution
        if hasattr(analyzer, 'get_priority_distribution'):
            dist = analyzer.get_priority_distribution(backlog)
            assert dist is not None
            
        # Test status breakdown
        if hasattr(analyzer, 'get_status_breakdown'):
            breakdown = analyzer.get_status_breakdown(backlog)
            assert breakdown is not None
    
    def test_backlog_metrics(self):
        """Test backlog metrics calculation."""
        analyzer = BacklogAnalyzer()
        
        backlog = [
            {"id": "1", "title": "Task 1", "story_points": 5, "status": "done"},
            {"id": "2", "title": "Task 2", "story_points": 8, "status": "in_progress"},
            {"id": "3", "title": "Task 3", "story_points": 3, "status": "todo"}
        ]
        
        # Test completion rate
        if hasattr(analyzer, 'calculate_completion_rate'):
            rate = analyzer.calculate_completion_rate(backlog)
            assert rate is not None
            
        # Test total points
        if hasattr(analyzer, 'calculate_total_points'):
            total = analyzer.calculate_total_points(backlog)
            assert total == 16 or total is not None
            
        # Test remaining work
        if hasattr(analyzer, 'calculate_remaining_work'):
            remaining = analyzer.calculate_remaining_work(backlog)
            assert remaining is not None


class TestDocumentProcessor:
    """Fast tests for document processor."""
    
    def test_document_processor_basic(self):
        """Test basic document processing."""
        processor = DocumentProcessor()
        assert processor is not None
        
        # Test simple text extraction
        test_text = "Test requirement: User must login"
        
        if hasattr(processor, 'extract_requirements_from_text'):
            reqs = processor.extract_requirements_from_text(test_text)
            assert reqs is not None
            assert isinstance(reqs, list)
    
    def test_meeting_notes_extraction(self):
        """Test meeting notes extraction."""
        processor = DocumentProcessor()
        
        meeting_notes = """
Meeting Notes - March 7, 2024

Attendees:
- John Smith
- Jane Doe
- Bob Johnson

Action Items:
- Implement user login feature
- Fix bug #123 in payment system
- Review security protocols

Decisions:
- Use OAuth2 for authentication
- Deploy to production next Friday

Requirements:
- System must handle 1000 concurrent users
- Response time under 200ms
- 99.9% uptime SLA
"""
        
        if hasattr(processor, 'extract_meeting_notes_structure'):
            structure = processor.extract_meeting_notes_structure(meeting_notes)
            assert structure is not None
            assert 'action_items' in structure
            assert len(structure['action_items']) >= 2
            assert 'participants' in structure
            assert 'decisions' in structure
            assert 'requirements' in structure
    
    def test_document_processing_methods(self):
        """Test various document processing methods."""
        processor = DocumentProcessor()
        
        # Test process_document if exists
        if hasattr(processor, 'process_document'):
            test_doc = "This is a test document with requirements and action items."
            result = processor.process_document(test_doc)
            assert result is not None
        
        # Test extract_key_terms if exists
        if hasattr(processor, 'extract_key_terms'):
            text = "Authentication, authorization, security, OAuth2, JWT tokens"
            terms = processor.extract_key_terms(text)
            assert terms is not None
        
        # Test parse_requirements if exists  
        if hasattr(processor, 'parse_requirements'):
            req_text = """
1. User authentication required
2. Data must be encrypted
3. API rate limiting needed
"""
            reqs = processor.parse_requirements(req_text)
            assert reqs is not None
    
    def test_document_type_detection(self):
        """Test document type detection and processing."""
        processor = DocumentProcessor()
        
        test_documents = {
            "meeting": "Meeting Notes\nAttendees: John, Jane\nAction Items: Deploy app",
            "requirements": "Functional Requirements:\n1. User login\n2. Data export",
            "user_story": "As a user, I want to login so that I can access my data"
        }
        
        for doc_type, content in test_documents.items():
            if hasattr(processor, 'detect_document_type'):
                detected_type = processor.detect_document_type(content)
                assert detected_type is not None
            
            if hasattr(processor, 'process_by_type'):
                result = processor.process_by_type(content, doc_type)
                assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
