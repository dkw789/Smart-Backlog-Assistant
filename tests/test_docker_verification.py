"""Simple tests to verify Docker environment is working correctly."""

import sys
import os
from pathlib import Path

def test_python_version():
    """Test that we're running the expected Python version."""
    assert sys.version_info.major == 3
    assert sys.version_info.minor >= 10  # Should be 3.10, 3.11, or 3.12

def test_working_directory():
    """Test that we're in the correct working directory."""
    cwd = Path.cwd()
    assert cwd.name == "app" or "windsurf-project-3" in str(cwd)

def test_src_directory_exists():
    """Test that src directory exists and contains expected modules."""
    src_path = Path("src")
    assert src_path.exists()
    assert src_path.is_dir()
    
    # Check key modules exist
    expected_modules = [
        "src/config.py",
        "src/models",
        "src/utils", 
        "src/processors",
        "src/generators",
        "src/agents",
        "src/api"
    ]
    
    for module_path in expected_modules:
        path = Path(module_path)
        assert path.exists(), f"Expected module {module_path} not found"

def test_basic_module_imports():
    """Test that basic modules can be imported without errors."""
    try:
        import src.config
        import src.models.base_models
        import src.utils.validators
        success = True
    except ImportError as e:
        success = False
        print(f"Import error: {e}")
    
    assert success, "Basic module imports should work"

def test_environment_setup():
    """Test that the environment is set up correctly."""
    # Test that we can access the source code
    import src
    assert hasattr(src, '__version__')
    
    # Test that pytest is available
    import pytest
    assert pytest is not None

def test_test_directory_structure():
    """Test that test directory has expected structure."""
    tests_path = Path("tests")
    assert tests_path.exists()
    
    # Check for key test directories/files
    expected_items = [
        "tests/conftest.py",
        "tests/reliable"
    ]
    
    for item_path in expected_items:
        path = Path(item_path)
        assert path.exists(), f"Expected test item {item_path} not found"

def test_package_installation():
    """Test that the package is properly installed."""
    try:
        # Try importing the main package
        import src
        from src.config import config
        from src.models.base_models import Priority
        
        # Basic functionality test
        assert Priority.HIGH.value == "HIGH"
        assert config.log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]
        
        success = True
    except Exception as e:
        success = False
        print(f"Package installation test failed: {e}")
    
    assert success, "Package should be properly installed and importable"
