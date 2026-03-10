"""Tests for refactored priority engine - demonstrating simplified testing with providers."""

import pytest
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestPriorityEngineRefactored:
    """Test refactored priority engine with easy dependency injection."""
    
    def test_engine_with_mock_provider(self):
        """Test priority engine with mock provider - no external dependencies."""
        from generators.priority_engine_refactored import PriorityEngineRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_provider = MockAIProvider()
        engine = PriorityEngineRefactored(ai_provider=mock_provider)
        
        # Test availability
        assert engine.is_available() == True
        
        # Test basic priority calculation
        test_item = {
            'id': '1',
            'title': 'Critical user authentication feature',
            'priority': 'high',
            'business_value': 9,
            'urgency': 8,
            'effort': 5,
            'risk': 3,
            'dependencies': ['auth_service']
        }
        
        result = engine.calculate_priority_score(test_item)
        assert result['success'] == True
        assert result['item_id'] == '1'
        assert result['priority_score'] > 0
        assert result['priority_level'] in ['critical', 'high', 'medium', 'low', 'very_low']
        assert 'metrics' in result
        assert 'weights_used' in result
        assert 'calculated_at' in result
        
        # Verify metrics
        metrics = result['metrics']
        assert metrics['business_value'] == 9
        assert metrics['urgency'] == 8
        assert metrics['effort'] == 5
        assert metrics['risk'] == 3
        assert metrics['dependencies'] == 1  # One dependency
    
    def test_priority_score_calculation(self):
        """Test priority score calculation with various scenarios."""
        from generators.priority_engine_refactored import PriorityEngineRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_provider = MockAIProvider()
        engine = PriorityEngineRefactored(ai_provider=mock_provider)
        
        # High priority item
        high_priority_item = {
            'id': 'high1',
            'title': 'Critical revenue feature',
            'business_value': 10,
            'urgency': 9,
            'effort': 3,  # Low effort
            'risk': 2,    # Low risk
            'dependencies': []  # No dependencies
        }
        
        result = engine.calculate_priority_score(high_priority_item)
        assert result['success'] == True
        assert result['priority_level'] in ['critical', 'high']
        assert result['priority_score'] > 7.0
        
        # Low priority item
        low_priority_item = {
            'id': 'low1',
            'title': 'Minor UI tweak',
            'business_value': 2,
            'urgency': 2,
            'effort': 8,  # High effort
            'risk': 7,    # High risk
            'dependencies': ['ui_framework', 'design_system', 'testing']
        }
        
        result = engine.calculate_priority_score(low_priority_item)
        assert result['success'] == True
        assert result['priority_level'] in ['low', 'very_low']
        assert result['priority_score'] < 5.0
    
    def test_backlog_prioritization(self):
        """Test prioritizing an entire backlog."""
        from generators.priority_engine_refactored import PriorityEngineRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_provider = MockAIProvider()
        engine = PriorityEngineRefactored(ai_provider=mock_provider)
        
        # Test backlog
        backlog = [
            {
                'id': '1',
                'title': 'User authentication',
                'priority': 'high',
                'business_value': 9,
                'urgency': 8
            },
            {
                'id': '2',
                'title': 'Data export feature',
                'priority': 'medium',
                'business_value': 6,
                'urgency': 5
            },
            {
                'id': '3',
                'title': 'UI polish',
                'priority': 'low',
                'business_value': 3,
                'urgency': 2
            }
        ]
        
        result = engine.prioritize_backlog(backlog)
        assert result['success'] == True
        assert result['total_items'] == 3
        assert len(result['prioritized_items']) == 3
        
        # Items should be sorted by priority score (highest first)
        items = result['prioritized_items']
        assert items[0]['calculated_priority_score'] >= items[1]['calculated_priority_score']
        assert items[1]['calculated_priority_score'] >= items[2]['calculated_priority_score']
        
        # Check rankings
        assert items[0]['priority_rank'] == 1
        assert items[1]['priority_rank'] == 2
        assert items[2]['priority_rank'] == 3
        
        # Check priority distribution
        assert 'priority_distribution' in result
        distribution = result['priority_distribution']
        assert sum(distribution.values()) == 3
    
    def test_ai_enhanced_prioritization(self):
        """Test AI-enhanced prioritization."""
        from generators.priority_engine_refactored import PriorityEngineRefactored
        from providers.openai_provider import MockAIProvider
        
        # Mock AI responses for enhancement
        mock_responses = {
            "structured": {
                "strategic_insights": ["Focus on user retention", "Market expansion priority"],
                "market_factors": ["Competitive pressure", "Customer demand"],
                "technical_considerations": ["Scalability concerns", "Technical debt"],
                "priority_adjustments": {
                    "1": {"adjustment": 1.5, "reasoning": "Critical for market position"},
                    "2": {"adjustment": -0.5, "reasoning": "Can be delayed"}
                }
            }
        }
        
        mock_provider = MockAIProvider(mock_responses)
        engine = PriorityEngineRefactored(ai_provider=mock_provider)
        
        backlog = [
            {'id': '1', 'title': 'Feature A', 'business_value': 7},
            {'id': '2', 'title': 'Feature B', 'business_value': 6}
        ]
        
        result = engine.ai_enhanced_prioritization(backlog)
        assert result['success'] == True
        assert result['ai_enhanced'] == True
        assert 'ai_insights' in result
        
        # Check AI insights
        insights = result['ai_insights']
        assert len(insights['strategic_insights']) == 2
        assert len(insights['market_factors']) == 2
        assert len(insights['technical_considerations']) == 2
        
        # Check AI adjustments
        items = result['prioritized_items']
        item1 = next(item for item in items if item['id'] == '1')
        item2 = next(item for item in items if item['id'] == '2')
        
        assert 'ai_priority_adjustment' in item1
        assert 'ai_reasoning' in item1
        assert 'ai_adjusted_score' in item1
        assert item1['ai_priority_adjustment'] == 1.5
        assert item2['ai_priority_adjustment'] == -0.5
    
    def test_empty_backlog(self):
        """Test handling of empty backlog."""
        from generators.priority_engine_refactored import PriorityEngineRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_provider = MockAIProvider()
        engine = PriorityEngineRefactored(ai_provider=mock_provider)
        
        result = engine.prioritize_backlog([])
        assert result['success'] == False
        assert 'No items provided' in result['error']
        assert result['prioritized_items'] == []
    
    def test_priority_level_inference(self):
        """Test priority level inference from various fields."""
        from generators.priority_engine_refactored import PriorityEngineRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_provider = MockAIProvider()
        engine = PriorityEngineRefactored(ai_provider=mock_provider)
        
        # Test inference from title keywords
        test_cases = [
            {
                'item': {'id': '1', 'title': 'Critical revenue bug'},
                'expected_min_score': 6.0
            },
            {
                'item': {'id': '2', 'title': 'User experience improvement'},
                'expected_min_score': 4.0
            },
            {
                'item': {'id': '3', 'title': 'Minor documentation update'},
                'expected_min_score': 2.0
            }
        ]
        
        for case in test_cases:
            result = engine.calculate_priority_score(case['item'])
            assert result['success'] == True
            assert result['priority_score'] >= case['expected_min_score']
    
    def test_story_points_conversion(self):
        """Test conversion of story points to effort assessment."""
        from generators.priority_engine_refactored import PriorityEngineRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_provider = MockAIProvider()
        engine = PriorityEngineRefactored(ai_provider=mock_provider)
        
        # Test various story point values
        story_point_cases = [
            {'story_points': 1, 'expected_effort': 1.0},
            {'story_points': 5, 'expected_effort': 5.0},
            {'story_points': 13, 'expected_effort': 10.0},  # Capped at 10
        ]
        
        for case in story_point_cases:
            item = {'id': '1', 'title': 'Test', 'story_points': case['story_points']}
            result = engine.calculate_priority_score(item)
            assert result['success'] == True
            assert result['metrics']['effort'] == case['expected_effort']
    
    def test_risk_assessment(self):
        """Test risk assessment from various inputs."""
        from generators.priority_engine_refactored import PriorityEngineRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_provider = MockAIProvider()
        engine = PriorityEngineRefactored(ai_provider=mock_provider)
        
        # Test explicit risk values
        risk_cases = [
            {'risk': 'high', 'expected': 7.0},
            {'risk': 'medium', 'expected': 5.0},
            {'risk': 'low', 'expected': 3.0},
            {'risk': 8, 'expected': 8.0},
        ]
        
        for case in risk_cases:
            item = {'id': '1', 'title': 'Test', 'risk': case['risk']}
            result = engine.calculate_priority_score(item)
            assert result['success'] == True
            assert result['metrics']['risk'] == case['expected']
        
        # Test risk inference from keywords
        high_risk_item = {'id': '1', 'title': 'New experimental architecture migration'}
        result = engine.calculate_priority_score(high_risk_item)
        assert result['success'] == True
        assert result['metrics']['risk'] >= 5.0  # Should be higher due to keywords
    
    def test_dependency_assessment(self):
        """Test dependency complexity assessment."""
        from generators.priority_engine_refactored import PriorityEngineRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_provider = MockAIProvider()
        engine = PriorityEngineRefactored(ai_provider=mock_provider)
        
        # Test list dependencies
        item_with_deps = {
            'id': '1',
            'title': 'Feature with dependencies',
            'dependencies': ['service_a', 'service_b', 'database_migration']
        }
        result = engine.calculate_priority_score(item_with_deps)
        assert result['success'] == True
        assert result['metrics']['dependencies'] == 3
        
        # Test string dependencies
        item_with_string_deps = {
            'id': '2',
            'title': 'Feature with string deps',
            'dependencies': 'auth_service, payment_service'
        }
        result = engine.calculate_priority_score(item_with_string_deps)
        assert result['success'] == True
        assert result['metrics']['dependencies'] == 2
        
        # Test blocked status
        blocked_item = {'id': '3', 'title': 'Blocked feature', 'status': 'blocked'}
        result = engine.calculate_priority_score(blocked_item)
        assert result['success'] == True
        assert result['metrics']['dependencies'] == 8.0  # High due to blocked status
    
    def test_error_handling(self):
        """Test error handling in priority calculations."""
        from generators.priority_engine_refactored import PriorityEngineRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_provider = MockAIProvider()
        engine = PriorityEngineRefactored(ai_provider=mock_provider)
        
        # Test with invalid item (should handle gracefully)
        invalid_item = None
        result = engine.calculate_priority_score(invalid_item)
        assert result['success'] == False
        assert 'error' in result
        
        # Test backlog with mix of valid and invalid items
        mixed_backlog = [
            {'id': '1', 'title': 'Valid item'},
            None,  # Invalid item
            {'id': '2', 'title': 'Another valid item'}
        ]
        
        # Should handle the None item gracefully
        try:
            result = engine.prioritize_backlog(mixed_backlog)
            # Should either succeed with error handling or fail gracefully
            assert 'success' in result
        except Exception:
            # If it throws, that's also acceptable for this edge case
            pass
    
    def test_ai_fallback(self):
        """Test fallback when AI is not available."""
        from generators.priority_engine_refactored import PriorityEngineRefactored
        from providers.openai_provider import MockAIProvider
        
        # Create unavailable AI provider
        class UnavailableAIProvider(MockAIProvider):
            def is_available(self):
                return False
        
        unavailable_provider = UnavailableAIProvider()
        engine = PriorityEngineRefactored(ai_provider=unavailable_provider)
        
        backlog = [{'id': '1', 'title': 'Test item'}]
        
        # Should fallback to basic prioritization
        result = engine.ai_enhanced_prioritization(backlog)
        assert result['success'] == True
        assert 'ai_enhanced' not in result or result['ai_enhanced'] != True
    
    def test_provider_status(self):
        """Test provider status functionality."""
        from generators.priority_engine_refactored import PriorityEngineRefactored
        from providers.openai_provider import MockAIProvider
        
        mock_provider = MockAIProvider()
        engine = PriorityEngineRefactored(ai_provider=mock_provider)
        
        status = engine.get_provider_status()
        assert "provider_config" in status
        assert status["is_available"] == True
        assert status["engine_ready"] == True
        assert "priority_weights" in status
        assert status["provider_config"]["provider"] == "mock"
    
    def test_comprehensive_workflow(self):
        """Test a comprehensive priority engine workflow."""
        from generators.priority_engine_refactored import PriorityEngineRefactored
        from providers.openai_provider import MockAIProvider
        
        # Setup comprehensive mock responses
        mock_responses = {
            "structured": {
                "strategic_insights": [
                    "Focus on customer retention features",
                    "Prioritize scalability improvements"
                ],
                "market_factors": [
                    "Competitive pressure in authentication space",
                    "Growing demand for real-time features"
                ],
                "technical_considerations": [
                    "Legacy system constraints",
                    "Performance bottlenecks in data layer"
                ],
                "priority_adjustments": {
                    "1": {"adjustment": 2.0, "reasoning": "Critical for customer retention"},
                    "2": {"adjustment": 0.5, "reasoning": "Aligns with market trends"},
                    "3": {"adjustment": -1.0, "reasoning": "Technical debt can wait"}
                }
            }
        }
        
        mock_provider = MockAIProvider(mock_responses)
        engine = PriorityEngineRefactored(ai_provider=mock_provider)
        
        # Comprehensive test backlog
        comprehensive_backlog = [
            {
                'id': '1',
                'title': 'User authentication system',
                'description': 'Implement secure user login and registration',
                'priority': 'high',
                'business_value': 9,
                'urgency': 8,
                'story_points': 8,
                'risk': 'medium',
                'dependencies': ['database', 'encryption_service'],
                'status': 'todo'
            },
            {
                'id': '2',
                'title': 'Real-time notifications',
                'description': 'Push notifications for user activities',
                'priority': 'medium',
                'business_value': 7,
                'urgency': 6,
                'story_points': 5,
                'risk': 'low',
                'dependencies': ['notification_service'],
                'status': 'todo'
            },
            {
                'id': '3',
                'title': 'Code refactoring',
                'description': 'Clean up legacy code in payment module',
                'priority': 'low',
                'business_value': 4,
                'urgency': 3,
                'story_points': 13,
                'risk': 'high',
                'dependencies': ['payment_service', 'testing_framework', 'deployment'],
                'status': 'todo'
            }
        ]
        
        # Run comprehensive analysis
        basic_result = engine.prioritize_backlog(comprehensive_backlog)
        ai_result = engine.ai_enhanced_prioritization(comprehensive_backlog)
        
        # Verify basic prioritization
        assert basic_result['success'] == True
        assert basic_result['total_items'] == 3
        assert len(basic_result['prioritized_items']) == 3
        
        # Verify AI enhancement
        assert ai_result['success'] == True
        assert ai_result['ai_enhanced'] == True
        assert len(ai_result['ai_insights']['strategic_insights']) == 2
        assert len(ai_result['ai_insights']['market_factors']) == 2
        assert len(ai_result['ai_insights']['technical_considerations']) == 2
        
        # Verify AI adjustments were applied
        ai_items = ai_result['prioritized_items']
        item1 = next(item for item in ai_items if item['id'] == '1')
        item2 = next(item for item in ai_items if item['id'] == '2')
        item3 = next(item for item in ai_items if item['id'] == '3')
        
        assert item1['ai_priority_adjustment'] == 2.0
        assert item2['ai_priority_adjustment'] == 0.5
        assert item3['ai_priority_adjustment'] == -1.0
        
        # Verify AI provider was used
        assert mock_provider.call_count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
