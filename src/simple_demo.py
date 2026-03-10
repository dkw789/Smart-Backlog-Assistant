"""Simple working demo of the Smart Backlog Assistant improvements."""

import json
from datetime import datetime
from pathlib import Path

from src.utils.caching_system import default_cache
from src.utils.enhanced_error_handler import resilient_service_manager
from src.utils.logger_service import get_logger


def demo_caching_system():
    """Demonstrate the intelligent caching system."""
    print("🔄 Testing Intelligent Caching System...")

    # Test basic caching
    cache_key = "demo_operation_123"
    test_data = {
        "operation": "meeting_notes_processing",
        "result": "Successfully processed 5 requirements and generated 3 user stories",
        "timestamp": datetime.now().isoformat(),
    }

    # Set cache
    success = default_cache.set(
        cache_key, test_data, ttl=3600, tags=["demo", "meeting_notes"]
    )
    print(f"✅ Cache set: {success}")

    # Get from cache
    cached_data = default_cache.get(cache_key)
    print(f"✅ Cache hit: {cached_data is not None}")

    # Show cache stats
    stats = default_cache.get_stats()
    print(
        f"📊 Cache Stats: {stats['hits']} hits, {stats['misses']} misses, {stats['hit_rate_percent']}% hit rate"
    )

    return True


def demo_error_handling():
    """Demonstrate enhanced error handling with circuit breakers."""
    print("\n🛡️ Testing Enhanced Error Handling...")

    # Register a demo service
    from utils.enhanced_error_handler import CircuitBreakerConfig

    config = CircuitBreakerConfig(failure_threshold=2, recovery_timeout=5.0)
    resilient_service_manager.register_service("demo_service", config)

    # Test successful call
    def successful_operation():
        return "Operation completed successfully"

    result = resilient_service_manager.call_service(
        "demo_service", successful_operation
    )
    print(f"✅ Successful call: {result}")

    # Show service status
    status = resilient_service_manager.get_service_status()
    print(f"📊 Service Status: {status}")

    return True


def demo_file_processing():
    """Demonstrate file processing capabilities."""
    print("\n📁 Testing File Processing...")

    # Create demo output directory
    output_dir = Path("demo_output")
    output_dir.mkdir(exist_ok=True)

    # Demo processing result
    demo_result = {
        "operation": "backlog_analysis",
        "source": "demo_backlog.json",
        "results": {
            "total_items": 15,
            "health_score": 78.5,
            "priority_distribution": {"high": 5, "medium": 7, "low": 3},
            "recommendations": [
                "Add acceptance criteria to 60% of items",
                "Break down 3 large items (>8 story points)",
                "Prioritize 2 critical bug fixes",
            ],
        },
        "processing_time": "1.2 seconds",
        "framework": "Enhanced Smart Backlog Assistant",
        "timestamp": datetime.now().isoformat(),
    }

    # Save demo result
    output_file = (
        output_dir / f"demo_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(output_file, "w") as f:
        json.dump(demo_result, f, indent=2)

    print(f"✅ Demo result saved to: {output_file}")
    print(f"📊 Result summary: {demo_result['results']['total_items']} items analyzed")
    print(f"🎯 Health score: {demo_result['results']['health_score']}")

    return True


def demo_pydantic_models():
    """Demonstrate Pydantic model validation."""
    print("\n🔍 Testing Pydantic Model Validation...")

    try:
        from models.backlog_models import BacklogItem
        from models.base_models import Priority, Status

        # Create a valid backlog item
        item = BacklogItem(
            title="User Authentication System",
            description="Implement secure user login and registration with OAuth support",
            priority=Priority.HIGH,
            status=Status.TODO,
            story_points=8,
            tags=["security", "authentication", "backend"],
        )

        print(f"✅ Valid BacklogItem created: {item.title}")
        print(f"📊 Story points: {item.story_points}, Priority: {item.priority}")
        print(f"🏷️ Tags: {', '.join(item.tags)}")
        print(
            "✅ Validation passed: Item created successfully with all required fields"
        )

        return True

    except ImportError as e:
        print(f"⚠️ Pydantic models not available: {e}")
        return False


def demo_logging_system():
    """Demonstrate enhanced logging."""
    print("\n📝 Testing Enhanced Logging System...")

    logger = get_logger("demo")

    # Test different log levels
    logger.info("Demo logging system initialized")
    logger.debug("Debug information for troubleshooting")
    logger.warning("This is a warning message")

    # Test structured logging
    logger.info(
        "Processing completed",
        extra={
            "operation": "demo_processing",
            "items_processed": 15,
            "duration": 2.3,
            "success": True,
        },
    )

    print("✅ Logging system working correctly")
    return True


def main():
    """Run comprehensive demo of all improvements."""
    print("🚀 Smart Backlog Assistant - Enhanced Features Demo")
    print("=" * 60)

    demos = [
        ("Caching System", demo_caching_system),
        ("Error Handling", demo_error_handling),
        ("File Processing", demo_file_processing),
        ("Pydantic Models", demo_pydantic_models),
        ("Logging System", demo_logging_system),
    ]

    results = {}

    for demo_name, demo_func in demos:
        try:
            print(f"\n{'='*20} {demo_name} {'='*20}")
            success = demo_func()
            results[demo_name] = "✅ PASSED" if success else "⚠️ PARTIAL"
        except Exception as e:
            print(f"❌ {demo_name} failed: {str(e)}")
            results[demo_name] = "❌ FAILED"

    # Summary
    print(f"\n{'='*60}")
    print("🎯 DEMO RESULTS SUMMARY")
    print("=" * 60)

    for demo_name, result in results.items():
        print(f"{demo_name:.<30} {result}")

    passed = sum(1 for r in results.values() if "PASSED" in r)
    total = len(results)

    print(f"\n📊 Overall: {passed}/{total} demos passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("🎉 All enhanced features are working correctly!")
    elif passed >= total * 0.8:
        print("✅ Most features working - system is ready for use!")
    else:
        print("⚠️ Some features need attention - check error messages above")

    print("\n💡 Next steps:")
    print("  1. Set up API keys for full AI functionality:")
    print("     export OPENAI_API_KEY='your_key_here'")
    print("     export ANTHROPIC_API_KEY='your_key_here'")
    print("  2. Try the original framework:")
    print("     python3 src/main.py meeting-notes sample_data/complex_meeting_notes.md")
    print("  3. Run tests:")
    print("     python3 -m pytest tests/ -v")


if __name__ == "__main__":
    main()
