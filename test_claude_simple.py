#!/usr/bin/env python3
"""Simple Claude configuration test without complex dependencies."""

import os
from dotenv import load_dotenv

def test_environment_configuration():
    """Test basic environment configuration."""
    print("🔧 Testing Environment Configuration...")
    
    # Load environment variables
    load_dotenv()
    
    # Check key configuration values
    default_service = os.getenv('DEFAULT_AI_SERVICE', 'not_found')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY', 'not_found')
    openai_key = os.getenv('OPENAI_API_KEY', 'not_found')
    
    print(f"✅ DEFAULT_AI_SERVICE: {default_service}")
    print(f"✅ ANTHROPIC_API_KEY: {'***configured***' if anthropic_key != 'not_found' and anthropic_key != 'your_anthropic_api_key_here' else 'not configured'}")
    print(f"✅ OPENAI_API_KEY: {'***configured***' if openai_key != 'not_found' and openai_key != 'your_openai_api_key_here' else 'not configured'}")
    
    # Check if Claude is properly set as default
    claude_configured = (
        default_service == 'anthropic' and 
        anthropic_key != 'not_found' and 
        anthropic_key != 'your_anthropic_api_key_here'
    )
    
    return claude_configured

def test_basic_imports():
    """Test that basic system components can be imported."""
    print("\n🔍 Testing Basic System Imports...")
    
    imports_working = 0
    total_imports = 0
    
    # Test basic utilities
    test_imports = [
        ("dotenv", "python-dotenv"),
        ("pydantic", "pydantic"),
        ("rich", "rich CLI"),
        ("anthropic", "anthropic client"),
        ("openai", "openai client")
    ]
    
    for module_name, description in test_imports:
        total_imports += 1
        try:
            __import__(module_name)
            print(f"✅ {description}: Available")
            imports_working += 1
        except ImportError:
            print(f"⚠️ {description}: Not available")
    
    return imports_working, total_imports

def test_file_structure():
    """Test that key project files exist."""
    print("\n📁 Testing Project File Structure...")
    
    key_files = [
        (".env", "Environment configuration"),
        (".env.example", "Environment template"),
        ("CLAUDE_SETUP.md", "Claude setup guide"),
        ("RUN_COMMANDS.md", "Run commands documentation"),
        ("requirements.txt", "Python dependencies"),
        ("src/enhanced_main.py", "Enhanced main application"),
        ("src/agents/pydantic_ai_main.py", "Pydantic-AI main application"),
        (".gitignore", "Git ignore file"),
        (".dockerignore", "Docker ignore file")
    ]
    
    files_found = 0
    total_files = len(key_files)
    
    for file_path, description in key_files:
        if os.path.exists(file_path):
            print(f"✅ {description}: Found")
            files_found += 1
        else:
            print(f"❌ {description}: Missing")
    
    return files_found, total_files

def test_enhanced_features():
    """Test enhanced features without complex imports."""
    print("\n🚀 Testing Enhanced Features...")
    
    features_working = 0
    total_features = 0
    
    # Test caching system
    total_features += 1
    try:
        from src.utils.caching_system import default_cache
        test_key = "simple_test"
        test_data = {"test": "data"}
        
        success = default_cache.set(test_key, test_data, ttl=60)
        cached_data = default_cache.get(test_key)
        
        if success and cached_data == test_data:
            print("✅ Caching System: Working")
            features_working += 1
        else:
            print("⚠️ Caching System: Partial")
    except Exception as e:
        print(f"❌ Caching System: Error - {e}")
    
    # Test logging system
    total_features += 1
    try:
        from src.utils.logger_service import get_logger
        logger = get_logger("test")
        logger.info("Test log message")
        print("✅ Logging System: Working")
        features_working += 1
    except Exception as e:
        print(f"❌ Logging System: Error - {e}")
    
    # Test error handling
    total_features += 1
    try:
        from src.utils.enhanced_error_handler import CircuitBreakerConfig
        config = CircuitBreakerConfig(failure_threshold=2, recovery_timeout=5.0)
        print("✅ Error Handling: Working")
        features_working += 1
    except Exception as e:
        print(f"❌ Error Handling: Error - {e}")
    
    return features_working, total_features

def main():
    """Run simplified Claude configuration test."""
    print("🚀 Smart Backlog Assistant - Claude Configuration Test (Simplified)")
    print("=" * 70)
    
    # Run tests
    claude_configured = test_environment_configuration()
    imports_working, total_imports = test_basic_imports()
    files_found, total_files = test_file_structure()
    features_working, total_features = test_enhanced_features()
    
    # Summary
    print(f"\n{'='*70}")
    print("🎯 CONFIGURATION TEST RESULTS")
    print("=" * 70)
    
    print(f"Claude Configuration.......... {'✅ CONFIGURED' if claude_configured else '⚠️ NEEDS SETUP'}")
    print(f"Python Dependencies........... {imports_working}/{total_imports} available ({imports_working/total_imports*100:.1f}%)")
    print(f"Project Files................. {files_found}/{total_files} found ({files_found/total_files*100:.1f}%)")
    print(f"Enhanced Features............. {features_working}/{total_features} working ({features_working/total_features*100:.1f}%)")
    
    # Overall assessment
    total_score = (
        (1 if claude_configured else 0) +
        (imports_working / total_imports) +
        (files_found / total_files) +
        (features_working / total_features)
    ) / 4 * 100
    
    print(f"\n📊 Overall System Health: {total_score:.1f}%")
    
    if total_score >= 90:
        print("🎉 Excellent! Your Smart Backlog Assistant is ready to use with Claude!")
    elif total_score >= 70:
        print("✅ Good! Most features are working. Minor issues detected.")
    elif total_score >= 50:
        print("⚠️ Partial setup. Some components need attention.")
    else:
        print("❌ Setup incomplete. Please review the issues above.")
    
    # Next steps
    print(f"\n💡 Next steps:")
    if not claude_configured:
        print("  1. Set your Anthropic API key in .env:")
        print("     ANTHROPIC_API_KEY=your_actual_api_key_here")
    
    print("  2. Try the enhanced demo:")
    print("     python3 src/simple_demo.py")
    
    print("  3. Use the system:")
    print("     python3 src/enhanced_main.py --interactive")
    
    if claude_configured:
        print("  4. Test with Claude:")
        print("     python3 src/agents/pydantic_ai_main.py meeting-notes sample_data/complex_meeting_notes.md")

if __name__ == "__main__":
    main()
