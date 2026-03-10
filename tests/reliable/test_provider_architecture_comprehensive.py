"""Comprehensive test demonstrating the full provider architecture working together."""

import pytest
import sys
import os
import json

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestProviderArchitectureIntegration:
    """Test the complete provider architecture working together."""
    
    def test_full_workflow_integration(self):
        """Test a complete workflow using all refactored modules together."""
        from processors.ai_processor_refactored import AIProcessorRefactored
        from processors.backlog_analyzer_refactored import BacklogAnalyzerRefactored
        from utils.rich_cli_refactored import RichCLIRefactored
        from providers.openai_provider import MockAIProvider
        from providers.rich_provider import MockUIProvider
        
        # Setup coordinated mock responses
        ai_responses = {
            "completion": "Requirements analysis completed successfully",
            "structured": {
                "requirements": ["User authentication", "Data validation", "Error handling"],
                "priority": "high",
                "complexity": "medium",
                "priority_suggestion": "high",
                "effort_estimate": 8,
                "risk_level": "medium",
                "dependencies": ["database", "auth_service"],
                "acceptance_criteria": ["Login works", "Data validates", "Errors handled"]
            }
        }
        
        # Create providers
        ai_provider = MockAIProvider(ai_responses)
        ui_provider = MockUIProvider()
        
        # Create modules with injected providers
        ai_processor = AIProcessorRefactored(ai_provider=ai_provider)
        backlog_analyzer = BacklogAnalyzerRefactored(ai_provider=ai_provider)
        cli = RichCLIRefactored(ui_provider=ui_provider)
        
        # Simulate complete workflow
        cli.print_info("Starting comprehensive analysis workflow...")
        
        # Step 1: Process requirements document
        requirements_text = """
        We need a user authentication system that validates user data
        and handles errors gracefully. The system should support login,
        registration, and password reset functionality.
        """
        
        processing_result = ai_processor.analyze_requirements(requirements_text)
        assert processing_result["success"] == True
        assert len(processing_result["requirements"]) == 3
        
        # Step 2: Create backlog from requirements
        backlog_items = []
        for i, req in enumerate(processing_result["requirements"]):
            backlog_items.append({
                "id": str(i + 1),
                "title": req,
                "priority": "high" if i == 0 else "medium",
                "status": "todo",
                "description": f"Implement {req.lower()}"
            })
        
        # Step 3: Analyze backlog
        analysis_result = backlog_analyzer.analyze_backlog_data(backlog_items)
        assert analysis_result.analysis_success == True
        assert analysis_result.total_items == 3
        assert analysis_result.health_score > 0
        
        # Step 4: Enhance backlog items with AI
        enhanced_items = backlog_analyzer.enhance_backlog_items(backlog_items)
        assert len(enhanced_items) == 3
        assert all("ai_priority_suggestion" in item for item in enhanced_items)
        
        # Step 5: Display results through CLI
        cli.display_processing_results(processing_result)
        cli.display_backlog_analysis({
            'total_items': analysis_result.total_items,
            'health_score': analysis_result.health_score,
            'analysis_success': analysis_result.analysis_success,
            'items_by_priority': analysis_result.items_by_priority,
            'items_by_status': analysis_result.items_by_status,
            'recommendations': analysis_result.recommendations,
            'risk_factors': analysis_result.risk_factors
        })
        
        cli.print_success("Comprehensive workflow completed successfully!")
        
        # Verify all components worked together
        assert ai_provider.call_count >= 4  # Processing + enhancement calls
        assert len(ui_provider.messages) >= 3  # Info, success, and display messages
        assert len(ui_provider.tables) >= 2  # Analysis tables
        
        # Verify data flow
        assert processing_result["provider"] == "mock"
        assert analysis_result.items_by_priority["high"] >= 1
        assert all(item["ai_effort_estimate"] == 8 for item in enhanced_items)
    
    def test_error_resilience_across_modules(self):
        """Test that modules handle errors gracefully when providers fail."""
        from processors.ai_processor_refactored import AIProcessorRefactored
        from processors.backlog_analyzer_refactored import BacklogAnalyzerRefactored
        from utils.rich_cli_refactored import RichCLIRefactored
        from providers.openai_provider import MockAIProvider
        from providers.rich_provider import MockUIProvider
        
        # Create failing AI provider
        class FailingAIProvider(MockAIProvider):
            def generate_completion(self, prompt, **kwargs):
                raise Exception("AI service unavailable")
            
            def generate_structured_response(self, prompt, schema=None):
                raise Exception("AI structured service unavailable")
        
        # Create failing UI provider
        class FailingUIProvider(MockUIProvider):
            def print_message(self, message, style=None):
                raise Exception("UI service unavailable")
        
        failing_ai = FailingAIProvider()
        failing_ui = FailingUIProvider()
        
        # Create modules with failing providers
        ai_processor = AIProcessorRefactored(ai_provider=failing_ai)
        backlog_analyzer = BacklogAnalyzerRefactored(ai_provider=failing_ai)
        cli = RichCLIRefactored(ui_provider=failing_ui)
        
        # Test graceful failure handling
        processing_result = ai_processor.process("Test input")
        assert processing_result["success"] == False
        assert "AI service unavailable" in processing_result["error"]
        
        backlog_items = [{"id": "1", "title": "Test item"}]
        analysis_result = backlog_analyzer.analyze_backlog_data(backlog_items)
        # Analysis should still work for basic operations
        assert analysis_result.total_items == 1
        
        # Enhancement should fail gracefully
        enhanced = backlog_analyzer.enhance_backlog_items(backlog_items)
        assert enhanced == backlog_items  # Should return original items
        
        # CLI should not crash
        cli.print_message("Test message")  # Should not raise exception
    
    def test_provider_switching(self):
        """Test switching between different provider implementations."""
        from processors.ai_processor_refactored import AIProcessorRefactored
        from providers.openai_provider import MockAIProvider
        
        # Create processor with first provider
        provider1 = MockAIProvider({"completion": "Response from provider 1"})
        processor = AIProcessorRefactored(ai_provider=provider1)
        
        result1 = processor.process("Test input")
        assert result1["result"] == "Response from provider 1"
        assert result1["provider"] == "mock"
        
        # Switch to different provider
        provider2 = MockAIProvider({"completion": "Response from provider 2"})
        processor.ai_provider = provider2
        
        result2 = processor.process("Test input")
        assert result2["result"] == "Response from provider 2"
        assert result2["provider"] == "mock"
        
        # Verify providers are independent
        assert provider1.call_count == 1
        assert provider2.call_count == 1
    
    def test_provider_factory_integration(self):
        """Test integration with provider factory."""
        from processors.ai_processor_refactored import AIProcessorRefactored
        from utils.rich_cli_refactored import RichCLIRefactored
        from providers.provider_factory import configure_providers, get_ai_provider, get_ui_provider
        
        # Configure factory to use mocks
        configure_providers(use_mocks=True)
        
        # Create modules without explicit providers (should use factory)
        ai_processor = AIProcessorRefactored()
        cli = RichCLIRefactored()
        
        # Test that they work with factory-provided providers
        assert ai_processor.is_available() == True
        assert cli.is_available() == True
        
        result = ai_processor.process("Test with factory")
        assert result["success"] == True
        
        cli.print_info("Factory integration test")
        # Should not crash
    
    def test_complex_data_flow(self):
        """Test complex data transformations through the provider architecture."""
        from processors.ai_processor_refactored import AIProcessorRefactored
        from processors.backlog_analyzer_refactored import BacklogAnalyzerRefactored
        from providers.openai_provider import MockAIProvider
        
        # Setup complex mock responses
        complex_responses = {
            "completion": json.dumps({
                "summary": "Complex system requirements",
                "entities": ["User", "System", "Database", "API"],
                "complexity": "high"
            }),
            "structured": {
                "requirements": [
                    "Multi-factor authentication",
                    "Real-time data synchronization", 
                    "Advanced error recovery",
                    "Performance monitoring",
                    "Security audit logging"
                ],
                "priority": "critical",
                "complexity": "very_high",
                "entities": ["User", "System", "Database", "API", "Monitor"],
                "categories": {
                    "security": ["Multi-factor authentication", "Security audit logging"],
                    "performance": ["Real-time data synchronization", "Performance monitoring"],
                    "reliability": ["Advanced error recovery"]
                },
                "priority_suggestion": "critical",
                "effort_estimate": 13,
                "risk_level": "high",
                "dependencies": ["auth_service", "database", "monitoring", "logging"],
                "acceptance_criteria": [
                    "MFA works correctly",
                    "Data syncs in real-time",
                    "System recovers from errors",
                    "Performance is monitored",
                    "All actions are logged"
                ]
            }
        }
        
        ai_provider = MockAIProvider(complex_responses)
        ai_processor = AIProcessorRefactored(ai_provider=ai_provider)
        backlog_analyzer = BacklogAnalyzerRefactored(ai_provider=ai_provider)
        
        # Complex processing workflow
        complex_text = """
        Build a enterprise-grade authentication and data management system
        with real-time synchronization, advanced monitoring, and comprehensive
        security features including multi-factor authentication and audit logging.
        """
        
        # Step 1: Extract requirements
        requirements = ai_processor.analyze_requirements(complex_text)
        assert requirements["success"] == True
        assert len(requirements["requirements"]) == 5
        assert requirements["priority"] == "critical"
        
        # Step 2: Extract entities
        entities = ai_processor.extract_entities(complex_text)
        assert entities["success"] == True
        assert len(entities["entities"]) == 5
        assert "User" in entities["entities"]
        
        # Step 3: Classify content
        classification = ai_processor.classify_content(complex_text)
        assert classification["success"] == True
        
        # Step 4: Create complex backlog
        complex_backlog = []
        for i, req in enumerate(requirements["requirements"]):
            # Make sure we have at least 2 critical items
            priority = "critical" if ("security" in req.lower() or "authentication" in req.lower()) else "high"
            status = "todo" if i < 3 else "in_progress" if i < 4 else "done"
            
            complex_backlog.append({
                "id": str(i + 1),
                "title": req,
                "priority": priority,
                "status": status,
                "description": f"Implement {req}",
                "story_points": 8 + (i * 2),
                "tags": ["enterprise", "security"] if "security" in req.lower() else ["enterprise"]
            })
        
        # Step 5: Analyze complex backlog
        analysis = backlog_analyzer.analyze_backlog_data(complex_backlog)
        assert analysis.analysis_success == True
        assert analysis.total_items == 5
        assert analysis.items_by_priority["critical"] >= 2
        assert analysis.items_by_status["todo"] >= 1
        
        # Step 6: Enhance all items
        enhanced = backlog_analyzer.enhance_backlog_items(complex_backlog)
        assert len(enhanced) == 5
        assert all("ai_priority_suggestion" in item for item in enhanced)
        assert all(item["ai_effort_estimate"] == 13 for item in enhanced)
        assert all(len(item["ai_dependencies"]) == 4 for item in enhanced)
        
        # Verify complex data transformations
        total_story_points = sum(item.get("story_points", 0) for item in complex_backlog)
        assert total_story_points > 40  # Should be substantial
        
        # Verify AI provider was used extensively
        assert ai_provider.call_count >= 8  # Multiple analysis + enhancement calls


class TestProviderArchitectureBenefits:
    """Demonstrate the key benefits of the provider architecture."""
    
    def test_easy_mocking_and_testing(self):
        """Demonstrate how easy it is to create comprehensive tests."""
        from processors.ai_processor_refactored import AIProcessorRefactored
        from providers.openai_provider import MockAIProvider
        
        # Create custom mock responses for specific test scenarios
        test_scenarios = [
            {"name": "success", "responses": {"completion": "Success response"}},
            {"name": "structured", "responses": {"structured": {"result": "structured data"}}},
            {"name": "empty", "responses": {"completion": ""}},
            {"name": "unicode", "responses": {"completion": "Unicode: 世界 🌍 café"}}
        ]
        
        for scenario in test_scenarios:
            mock_provider = MockAIProvider(scenario["responses"])
            processor = AIProcessorRefactored(ai_provider=mock_provider)
            
            if scenario["name"] == "success":
                result = processor.process("test")
                assert result["success"] == True
                assert result["result"] == "Success response"
            
            elif scenario["name"] == "structured":
                result = processor.analyze_requirements("test")
                assert result["success"] == True
            
            elif scenario["name"] == "empty":
                result = processor.process("test")
                assert result["success"] == True
                assert result["result"] == ""
            
            elif scenario["name"] == "unicode":
                result = processor.process("test")
                assert result["success"] == True
                assert "世界" in result["result"]
    
    def test_no_external_dependencies(self):
        """Demonstrate that tests run without any external service dependencies."""
        from processors.ai_processor_refactored import AIProcessorRefactored
        from processors.backlog_analyzer_refactored import BacklogAnalyzerRefactored
        from utils.rich_cli_refactored import RichCLIRefactored
        from providers.openai_provider import MockAIProvider
        from providers.rich_provider import MockUIProvider
        
        # All these operations work without OpenAI, Rich, or any external service
        ai_provider = MockAIProvider()
        ui_provider = MockUIProvider()
        
        processor = AIProcessorRefactored(ai_provider=ai_provider)
        analyzer = BacklogAnalyzerRefactored(ai_provider=ai_provider)
        cli = RichCLIRefactored(ui_provider=ui_provider)
        
        # Complex operations that would normally require external services
        result = processor.analyze_requirements("Build a web application")
        assert result["success"] == True
        
        backlog = [{"id": "1", "title": "Web app", "priority": "high", "status": "todo"}]
        analysis = analyzer.analyze_backlog_data(backlog)
        assert analysis.analysis_success == True
        
        cli.display_backlog_analysis({
            'total_items': 1,
            'health_score': 80.0,
            'analysis_success': True,
            'items_by_priority': {'high': 1},
            'items_by_status': {'todo': 1},
            'recommendations': [],
            'risk_factors': []
        })
        
        # All operations completed successfully without external dependencies
        assert len(ui_provider.messages) > 0
        assert len(ui_provider.tables) > 0
    
    def test_fast_execution(self):
        """Demonstrate fast test execution with provider architecture."""
        import time
        from processors.ai_processor_refactored import AIProcessorRefactored
        from providers.openai_provider import MockAIProvider
        
        start_time = time.time()
        
        # Perform many operations that would be slow with real services
        mock_provider = MockAIProvider({"completion": "Fast response"})
        processor = AIProcessorRefactored(ai_provider=mock_provider)
        
        for i in range(50):  # 50 AI operations
            result = processor.process(f"Test input {i}")
            assert result["success"] == True
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete very quickly (under 1 second for 50 operations)
        assert execution_time < 1.0
        assert mock_provider.call_count == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
