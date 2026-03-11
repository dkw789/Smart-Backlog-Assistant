"""Final tests to reach 50% coverage."""

import pytest
from src.models.ai_models import AIRequest, AIResponse
from src.models.backlog_models import BacklogItem, BacklogAnalysis
from src.models.base_models import Priority, Status, UserStory, AcceptanceCriterion
from src.utils.caching_system import IntelligentCache, AIResponseCache
from src.utils.enhanced_error_handler import CircuitBreaker, CircuitBreakerState


class TestAIModels:
    """Test AI models."""
    
    def test_ai_request(self):
        """Test AIRequest model."""
        request = AIRequest(
            prompt="Test prompt",
            model="gpt-4",
            temperature=0.7,
            max_tokens=1000
        )
        assert request.prompt == "Test prompt"
        assert request.model == "gpt-4"
    
    def test_ai_response(self):
        """Test AIResponse model."""
        response = AIResponse(
            content="Test response",
            success=True,
            service_used="openai",
            processing_time=1.5
        )
        assert response.content == "Test response"
        assert response.success is True
        assert response.service_used == "openai"


class TestBacklogModels:
    """Test backlog models."""
    
    def test_backlog_item(self):
        """Test BacklogItem model."""
        item = BacklogItem(
            title="Test Item",
            description="Test description",
            priority="high",
            status="todo",
            story_points=5
        )
        assert item.title == "Test Item"
        assert item.priority == "high"
        assert item.story_points == 5
    
    def test_backlog_analysis(self):
        """Test BacklogAnalysis model."""
        analysis = BacklogAnalysis(
            analysis_success=True,
            total_items=10,
            health_score=85.0,
            items_by_priority={"high": 3, "medium": 5, "low": 2},
            items_by_status={"todo": 7, "in_progress": 2, "done": 1},
            missing_information=[],
            recommendations=["Add more details"]
        )
        assert analysis.total_items == 10
        assert analysis.health_score == 85.0


class TestBaseModels:
    """Test base models."""
    
    def test_priority_enum(self):
        """Test Priority enum."""
        assert Priority.CRITICAL.value == "critical"
        assert Priority.HIGH.value == "high"
        assert Priority.MEDIUM.value == "medium"
        assert Priority.LOW.value == "low"
    
    def test_status_enum(self):
        """Test Status enum."""
        assert Status.TODO.value == "todo"
        assert Status.IN_PROGRESS.value == "in_progress"
        assert Status.DONE.value == "done"
        assert Status.BLOCKED.value == "blocked"
    
    def test_acceptance_criterion(self):
        """Test AcceptanceCriterion model."""
        criterion = AcceptanceCriterion(
            given="User is logged in",
            when="User clicks logout",
            then="User is logged out"
        )
        assert criterion.given == "User is logged in"
        assert criterion.when == "User clicks logout"
        assert criterion.then == "User is logged out"
    
    def test_user_story(self):
        """Test UserStory model."""
        story = UserStory(
            title="User Login",
            user_type="user",
            functionality="login to the system",
            benefit="access my account",
            acceptance_criteria=[
                AcceptanceCriterion(
                    given="User has valid credentials",
                    when="User submits login form",
                    then="User is authenticated"
                )
            ],
            priority=Priority.HIGH,
            estimated_effort="5 days"
        )
        assert story.title == "User Login"
        assert story.priority == Priority.HIGH
        assert len(story.acceptance_criteria) == 1


class TestIntelligentCache:
    """Test IntelligentCache."""
    
    def test_cache_set_get(self):
        """Test cache set and get."""
        cache = IntelligentCache(max_size=100, default_ttl=60)
        
        cache.set("key1", "value1")
        result = cache.get("key1")
        assert result == "value1"
    
    def test_cache_clear(self):
        """Test cache clear."""
        cache = IntelligentCache(max_size=100, default_ttl=60)
        
        cache.set("key1", "value1")
        cache.clear()
        result = cache.get("key1")
        assert result is None
    
    def test_cache_stats(self):
        """Test cache statistics."""
        cache = IntelligentCache(max_size=100, default_ttl=60)
        
        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss
        
        stats = cache.get_stats()
        assert "hits" in stats
        assert "misses" in stats
        assert stats["hits"] == 1
        assert stats["misses"] == 1


class TestCircuitBreaker:
    """Test CircuitBreaker."""
    
    def test_circuit_breaker_init(self):
        """Test CircuitBreaker initialization."""
        cb = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60.0,
            success_threshold=2
        )
        assert cb.failure_threshold == 3
        assert cb.recovery_timeout == 60.0
        assert cb.success_threshold == 2
    
    def test_circuit_breaker_state(self):
        """Test CircuitBreaker state."""
        cb = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60.0,
            success_threshold=2
        )
        assert cb.state == CircuitBreakerState.CLOSED
    
    def test_circuit_breaker_record_success(self):
        """Test recording success."""
        cb = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60.0,
            success_threshold=2
        )
        cb.record_success()
        assert cb.consecutive_successes == 1
    
    def test_circuit_breaker_record_failure(self):
        """Test recording failure."""
        cb = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60.0,
            success_threshold=2
        )
        cb.record_failure()
        assert cb.failure_count == 1


class TestAIResponseCache:
    """Test AIResponseCache."""
    
    def test_ai_response_cache_init(self):
        """Test AIResponseCache initialization."""
        cache = AIResponseCache(max_size=50, default_ttl=300)
        assert cache is not None
    
    def test_ai_response_cache_operations(self):
        """Test AIResponseCache operations."""
        cache = AIResponseCache(max_size=50, default_ttl=300)
        
        # Cache AI response
        cache.cache_response("test_prompt", "test_response", "openai")
        
        # Retrieve cached response
        result = cache.get_cached_response("test_prompt", "openai")
        assert result == "test_response"
