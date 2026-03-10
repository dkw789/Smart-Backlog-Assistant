#!/usr/bin/env python3
"""Test script to verify Claude (Anthropic) configuration."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv

def test_env_loading():
    """Test that .env file is loaded correctly."""
    print("🔧 Testing .env file loading...")
    
    load_dotenv()
    
    default_service = os.getenv('DEFAULT_AI_SERVICE', 'not_found')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY', 'not_found')
    
    print(f"✅ DEFAULT_AI_SERVICE: {default_service}")
    print(f"✅ ANTHROPIC_API_KEY: {'***configured***' if anthropic_key != 'not_found' else 'not_found'}")
    
    return default_service == 'anthropic'


def test_ai_processor_config():
    """Test AI processor configuration."""
    print("\n🤖 Testing AI Processor configuration...")
    
    try:
        from processors.ai_processor import AIProcessor
        
        processor = AIProcessor()
        
        # Check which clients are available
        has_anthropic = processor.anthropic_client is not None
        has_openai = processor.openai_client is not None
        
        print(f"✅ Anthropic client: {'Available' if has_anthropic else 'Not configured'}")
        print(f"✅ OpenAI client: {'Available' if has_openai else 'Not configured'}")
        
        return has_anthropic or has_openai
        
    except Exception as e:
        print(f"❌ AI Processor error: {e}")
        return False


def test_pydantic_ai_agents():
    """Test pydantic-ai agents configuration."""
    print("\n🎯 Testing pydantic-ai agents configuration...")
    
    try:
        # Test importing agents (they should configure with Claude by default)
        from agents.document_analyst import document_analyst
        from agents.coordinator import coordinator
        
        print(f"✅ Document Analyst agent: {document_analyst.model}")
        print(f"✅ Coordinator agent: {coordinator.model}")
        
        # Check if they're using Anthropic/Claude
        uses_claude = 'anthropic' in str(document_analyst.model).lower()
        
        return uses_claude
        
    except Exception as e:
        print(f"❌ Pydantic-AI agents error: {e}")
        return False


def main():
    """Run all configuration tests."""
    print("🚀 Claude (Anthropic) Configuration Test")
    print("=" * 50)
    
    tests = [
        ("Environment Loading", test_env_loading),
        ("AI Processor Config", test_ai_processor_config),
        ("Pydantic-AI Agents", test_pydantic_ai_agents)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results[test_name] = "✅ PASSED" if success else "⚠️ PARTIAL"
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results[test_name] = "❌ FAILED"
    
    # Summary
    print(f"\n{'='*50}")
    print("🎯 CONFIGURATION TEST RESULTS")
    print("=" * 50)
    
    for test_name, result in results.items():
        print(f"{test_name:.<30} {result}")
    
    passed = sum(1 for r in results.values() if "PASSED" in r)
    total = len(results)
    
    print(f"\n📊 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 Claude configuration is working correctly!")
        print("\n💡 To use the system with Claude:")
        print("  1. Set your Anthropic API key in .env:")
        print("     ANTHROPIC_API_KEY=your_actual_api_key_here")
        print("  2. Run the enhanced main:")
        print("     python3 src/enhanced_main.py --interactive")
        print("  3. Or use pydantic-ai framework:")
        print("     python3 src/agents/pydantic_ai_main.py meeting-notes sample_data/complex_meeting_notes.md")
    else:
        print("⚠️ Some configuration issues detected - check error messages above")


if __name__ == "__main__":
    main()
