#!/usr/bin/env python3
"""Quick test runner for the specific test you're working on."""

import subprocess
import sys

def run_test_with_coverage():
    """Run the specific test with coverage."""
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/test_utils.py::TestLoggerService::test_log_ai_request_decorator",
        "-v", 
        "--cov=src", 
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov"
    ]
    
    print("Running test with coverage...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    result = subprocess.run(cmd, cwd=".")
    
    if result.returncode == 0:
        print("\n✅ Test passed successfully!")
        print("📊 Coverage report generated in 'htmlcov/' directory")
    else:
        print("\n❌ Test failed!")
    
    return result.returncode

if __name__ == "__main__":
    exit(run_test_with_coverage())
