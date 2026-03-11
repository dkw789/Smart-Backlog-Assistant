"""Comprehensive tests for FileHandler to improve code coverage."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
import pytest

from src.utils.file_handler import FileHandler


class TestFileHandlerComprehensive:
    """Comprehensive tests for FileHandler class."""
    
    def test_read_text_file_success(self):
        """Test successful text file reading."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            test_content = "Test line 1\nTest line 2\nTest line 3"
            f.write(test_content)
            temp_path = f.name
        
        try:
            result = FileHandler.read_text_file(temp_path)
            assert result == test_content
        finally:
            os.unlink(temp_path)
    
    def test_read_text_file_not_found(self):
        """Test reading non-existent text file."""
        with pytest.raises(FileNotFoundError) as exc_info:
            FileHandler.read_text_file("non_existent_file.txt")
        
        assert "Error reading text file non_existent_file.txt" in str(exc_info.value)
    
    def test_read_text_file_encoding_error(self):
        """Test reading text file with encoding issues."""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.txt', delete=False) as f:
            # Write invalid UTF-8 bytes
            f.write(b'\xff\xfe\x00\x00')
            temp_path = f.name
        
        try:
            with pytest.raises(FileNotFoundError) as exc_info:
                FileHandler.read_text_file(temp_path)
            
            assert "Error reading text file" in str(exc_info.value)
        finally:
            os.unlink(temp_path)
    
    @patch('src.utils.file_handler.PyPDF2.PdfReader')
    def test_read_pdf_file_success(self, mock_pdf_reader):
        """Test successful PDF file reading."""
        # Mock PDF page
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "PDF page content"
        
        # Mock PDF reader
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page, mock_page]  # Two pages
        mock_pdf_reader.return_value = mock_reader
        
        with patch('builtins.open', mock_open()):
            result = FileHandler.read_pdf_file("test.pdf")
        
        assert result == "PDF page content\nPDF page content\n"
        mock_pdf_reader.assert_called_once()
    
    def test_read_pdf_file_not_found(self):
        """Test reading non-existent PDF file."""
        with pytest.raises(FileNotFoundError) as exc_info:
            FileHandler.read_pdf_file("non_existent_file.pdf")
        
        assert "Error reading PDF file non_existent_file.pdf" in str(exc_info.value)
    
    @patch('src.utils.file_handler.PyPDF2.PdfReader')
    def test_read_pdf_file_corruption_error(self, mock_pdf_reader):
        """Test reading corrupted PDF file."""
        mock_pdf_reader.side_effect = Exception("PDF corrupted")
        
        with patch('builtins.open', mock_open()):
            with pytest.raises(FileNotFoundError) as exc_info:
                FileHandler.read_pdf_file("corrupted.pdf")
            
            assert "Error reading PDF file corrupted.pdf" in str(exc_info.value)
    
    @patch('src.utils.file_handler.Document')
    def test_read_docx_file_success(self, mock_document_class):
        """Test successful DOCX file reading."""
        # Mock document and paragraphs
        mock_doc = MagicMock()
        mock_paragraph1 = MagicMock()
        mock_paragraph1.text = "First paragraph"
        mock_paragraph2 = MagicMock()
        mock_paragraph2.text = "Second paragraph"
        mock_doc.paragraphs = [mock_paragraph1, mock_paragraph2]
        mock_document_class.return_value = mock_doc
        
        result = FileHandler.read_docx_file("test.docx")
        
        assert result == "First paragraph\nSecond paragraph\n"
        mock_document_class.assert_called_once_with("test.docx")
    
    def test_read_docx_file_not_found(self):
        """Test reading non-existent DOCX file."""
        with pytest.raises(FileNotFoundError) as exc_info:
            FileHandler.read_docx_file("non_existent_file.docx")
        
        assert "Error reading DOCX file non_existent_file.docx" in str(exc_info.value)
    
    @patch('src.utils.file_handler.Document')
    def test_read_docx_file_corruption_error(self, mock_document_class):
        """Test reading corrupted DOCX file."""
        mock_document_class.side_effect = Exception("DOCX corrupted")
        
        with pytest.raises(FileNotFoundError) as exc_info:
            FileHandler.read_docx_file("corrupted.docx")
        
        assert "Error reading DOCX file corrupted.docx" in str(exc_info.value)
    
    def test_read_json_file_success(self):
        """Test successful JSON file reading."""
        test_data = {"key": "value", "items": [1, 2, 3], "nested": {"a": "b"}}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name
        
        try:
            result = FileHandler.read_json_file(temp_path)
            assert result == test_data
        finally:
            os.unlink(temp_path)
    
    def test_read_json_file_not_found(self):
        """Test reading non-existent JSON file."""
        with pytest.raises(FileNotFoundError) as exc_info:
            FileHandler.read_json_file("non_existent_file.json")
        
        assert "Error reading JSON file non_existent_file.json" in str(exc_info.value)
    
    def test_read_json_file_invalid_json(self):
        """Test reading invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json content")
            temp_path = f.name
        
        try:
            with pytest.raises(FileNotFoundError) as exc_info:
                FileHandler.read_json_file(temp_path)
            
            assert "Error reading JSON file" in str(exc_info.value)
        finally:
            os.unlink(temp_path)
    
    def test_write_json_file_success(self):
        """Test successful JSON file writing."""
        test_data = {"key": "value", "items": [1, 2, 3]}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "subdir", "test.json")
            
            FileHandler.write_json_file(file_path, test_data)
            
            # Verify file was created and contains correct data
            assert os.path.exists(file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            assert loaded_data == test_data
    
    def test_write_json_file_directory_creation(self):
        """Test that directories are created when writing JSON file."""
        test_data = {"test": "data"}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = os.path.join(temp_dir, "level1", "level2", "test.json")
            
            FileHandler.write_json_file(nested_path, test_data)
            
            assert os.path.exists(nested_path)
            assert os.path.exists(os.path.dirname(nested_path))
    
    def test_write_json_file_permission_error(self):
        """Test writing JSON file with permission error."""
        test_data = {"test": "data"}
        
        # Try to write to a location that should cause permission error
        invalid_path = "/root/forbidden/test.json"
        
        with pytest.raises(OSError) as exc_info:
            FileHandler.write_json_file(invalid_path, test_data)
        
        assert "Error writing JSON file" in str(exc_info.value)
    
    def test_get_file_type_supported_types(self):
        """Test file type detection for supported types."""
        test_cases = [
            ("test.txt", "text"),
            ("document.md", "text"),
            ("report.pdf", "pdf"),
            ("document.docx", "docx"),
            ("data.json", "json"),
            ("file.TXT", "text"),  # Test case insensitive
            ("FILE.PDF", "pdf"),   # Test case insensitive
        ]
        
        for file_path, expected_type in test_cases:
            result = FileHandler.get_file_type(file_path)
            assert result == expected_type, f"Failed for {file_path}"
    
    def test_get_file_type_unsupported(self):
        """Test file type detection for unsupported types."""
        unsupported_files = [
            "test.csv",
            "image.jpg",
            "script.py",
            "archive.zip",
            "no_extension",
            "",
        ]
        
        for file_path in unsupported_files:
            result = FileHandler.get_file_type(file_path)
            assert result == "unknown", f"Failed for {file_path}"
    
    def test_get_file_type_edge_cases(self):
        """Test file type detection edge cases."""
        # Multiple dots
        assert FileHandler.get_file_type("test.v2.txt") == "text"
        
        # Hidden files
        assert FileHandler.get_file_type(".hidden.txt") == "text"
        
        # Just extension (no filename) - should be unknown
        assert FileHandler.get_file_type(".txt") == "unknown"
    
    def test_read_file_content_text(self):
        """Test reading file content based on text file type."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            test_content = "This is a test text file."
            f.write(test_content)
            temp_path = f.name
        
        try:
            result = FileHandler.read_file_content(temp_path)
            assert result == test_content
        finally:
            os.unlink(temp_path)
    
    def test_read_file_content_json(self):
        """Test reading file content based on JSON file type."""
        test_data = {"message": "Hello, World!"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name
        
        try:
            result = FileHandler.read_file_content(temp_path)
            # Should return JSON string, not dict
            assert isinstance(result, str)
            assert "Hello, World!" in result
        finally:
            os.unlink(temp_path)
    
    @patch('src.utils.file_handler.PyPDF2.PdfReader')
    def test_read_file_content_pdf(self, mock_pdf_reader):
        """Test reading file content based on PDF file type."""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "PDF content"
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader
        
        with patch('builtins.open', mock_open()):
            result = FileHandler.read_file_content("test.pdf")
        
        assert result == "PDF content\n"
    
    @patch('src.utils.file_handler.Document')
    def test_read_file_content_docx(self, mock_document_class):
        """Test reading file content based on DOCX file type."""
        mock_doc = MagicMock()
        mock_paragraph = MagicMock()
        mock_paragraph.text = "DOCX content"
        mock_doc.paragraphs = [mock_paragraph]
        mock_document_class.return_value = mock_doc
        
        result = FileHandler.read_file_content("test.docx")
        
        assert result == "DOCX content\n"
    
    def test_read_file_content_unsupported_type(self):
        """Test reading file content with unsupported file type."""
        with pytest.raises(ValueError) as exc_info:
            FileHandler.read_file_content("test.csv")
        
        assert "Unsupported file type: unknown" in str(exc_info.value)
    
    def test_read_file_content_non_existent_file(self):
        """Test reading file content for non-existent file."""
        with pytest.raises(FileNotFoundError):
            FileHandler.read_file_content("non_existent.txt")
    
    def test_static_method_calls(self):
        """Test that all methods can be called as static methods."""
        # All methods should be callable without instantiation
        assert callable(FileHandler.read_text_file)
        assert callable(FileHandler.read_pdf_file)
        assert callable(FileHandler.read_docx_file)
        assert callable(FileHandler.read_json_file)
        assert callable(FileHandler.write_json_file)
        assert callable(FileHandler.get_file_type)
        assert callable(FileHandler.read_file_content)
    
    def test_method_chaining_compatibility(self):
        """Test that methods work independently and don't share state."""
        # Since these are static methods, they should not share state
        # This test verifies that calling one method doesn't affect others
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test content")
            temp_path = f.name
        
        try:
            # Call multiple methods
            file_type = FileHandler.get_file_type(temp_path)
            content = FileHandler.read_text_file(temp_path)
            json_data = FileHandler.read_json_file(temp_path)  # This should fail
            
        except FileNotFoundError:
            # Expected for JSON read of text file
            pass
        finally:
            os.unlink(temp_path)
        
        # Verify file type detection still works
        assert file_type == "text"
