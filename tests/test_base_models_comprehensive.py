"""Comprehensive tests for base models to improve code coverage."""

import pytest
from datetime import datetime
from src.models.base_models import (
    Priority,
    Status,
    Category,
    BusinessImpact,
    TechnicalComplexity,
    BaseEntity,
    HealthScore,
    EffortEstimate,
    ValidationResult,
    ProcessingMetadata,
    AIService,
    AgentRole
)


class TestEnums:
    """Test all enum classes."""
    
    def test_priority_enum(self):
        """Test Priority enum values."""
        assert Priority.CRITICAL.value == "critical"
        assert Priority.HIGH.value == "high"
        assert Priority.MEDIUM.value == "medium"
        assert Priority.LOW.value == "low"
        
        # Test enum iteration
        priorities = list(Priority)
        assert len(priorities) == 4
        assert Priority.CRITICAL in priorities
        
        # Test enum comparison
        assert Priority.HIGH == Priority.HIGH
        assert Priority.HIGH != Priority.LOW
    
    def test_status_enum(self):
        """Test Status enum values."""
        assert Status.TODO.value == "todo"
        assert Status.IN_PROGRESS.value == "in_progress"
        assert Status.DONE.value == "done"
        assert Status.BLOCKED.value == "blocked"
        
        statuses = list(Status)
        assert len(statuses) == 4
        assert Status.TODO in statuses
    
    def test_category_enum(self):
        """Test Category enum values."""
        assert Category.FEATURE.value == "feature"
        assert Category.BUG.value == "bug"
        assert Category.ENHANCEMENT.value == "enhancement"
        assert Category.TECHNICAL_DEBT.value == "technical_debt"
        assert Category.RESEARCH.value == "research"
        assert Category.MAINTENANCE.value == "maintenance"
        
        categories = list(Category)
        assert len(categories) == 6
        assert Category.FEATURE in categories
    
    def test_business_impact_enum(self):
        """Test BusinessImpact enum values."""
        assert BusinessImpact.HIGH.value == "high"
        assert BusinessImpact.MEDIUM.value == "medium"
        assert BusinessImpact.LOW.value == "low"
        
        impacts = list(BusinessImpact)
        assert len(impacts) == 3
    
    def test_technical_complexity_enum(self):
        """Test TechnicalComplexity enum values."""
        assert TechnicalComplexity.HIGH.value == "high"
        assert TechnicalComplexity.MEDIUM.value == "medium"
        assert TechnicalComplexity.LOW.value == "low"
        
        complexities = list(TechnicalComplexity)
        assert len(complexities) == 3


class TestBaseEntity:
    """Test BaseEntity class."""
    
    def test_base_entity_creation(self):
        """Test BaseEntity creation with minimal data."""
        entity = BaseEntity()
        assert entity.id is not None
        assert isinstance(entity.id, str)
        assert entity.created_at is not None
        assert isinstance(entity.created_at, datetime)
        assert entity.updated_at is None  # Default is None
    
    def test_base_entity_with_data(self):
        """Test BaseEntity creation with custom data."""
        test_id = "test-123"
        entity = BaseEntity(id=test_id)
        assert entity.id == test_id
        assert entity.created_at is not None
        assert entity.updated_at is None
    
    def test_base_entity_timestamps(self):
        """Test that timestamps are properly set."""
        before_creation = datetime.utcnow()
        entity = BaseEntity()
        after_creation = datetime.utcnow()
        
        assert before_creation <= entity.created_at <= after_creation
        assert entity.updated_at is None
    
    def test_base_entity_update_timestamp(self):
        """Test update_timestamp method."""
        entity = BaseEntity()
        original_updated_at = entity.updated_at
        
        entity.update_timestamp()
        
        assert entity.updated_at is not None
        assert entity.updated_at != original_updated_at
        assert entity.updated_at >= entity.created_at


class TestHealthScore:
    """Test HealthScore model."""
    
    def test_health_score_creation(self):
        """Test HealthScore creation."""
        health = HealthScore(score=85)
        assert health.score == 85
        assert health.factors == {}  # Default empty dict
        assert health.recommendations == []  # Default empty list
        assert health.calculation_metadata == {}  # Default empty dict
    
    def test_health_score_with_data(self):
        """Test HealthScore with full data."""
        factors = {"performance": 0.8, "reliability": 0.9}
        recommendations = ["Optimize database queries", "Add caching"]
        metadata = {"version": "1.0", "algorithm": "weighted_average"}
        
        health = HealthScore(
            score=90,
            factors=factors,
            recommendations=recommendations,
            calculation_metadata=metadata
        )
        assert health.score == 90
        assert health.factors == factors
        assert health.recommendations == recommendations
        assert health.calculation_metadata == metadata
    
    def test_health_score_validation(self):
        """Test HealthScore validation."""
        # Test valid scores
        for score in [0, 50, 100, 85.5]:
            health = HealthScore(score=score)
            assert health.score == score
        
        # Test invalid scores
        with pytest.raises(ValueError):
            HealthScore(score=-1)
        
        with pytest.raises(ValueError):
            HealthScore(score=101)
    
    def test_health_score_rounding(self):
        """Test score rounding validation."""
        # Test that scores are rounded to 2 decimal places
        health = HealthScore(score=85.6789)
        assert health.score == 85.68
        
        health = HealthScore(score=85.6749)
        assert health.score == 85.67


class TestEffortEstimate:
    """Test EffortEstimate enum."""
    
    def test_effort_estimate_enum_values(self):
        """Test EffortEstimate enum values."""
        assert EffortEstimate.SMALL.value == "small"
        assert EffortEstimate.MEDIUM.value == "medium"
        assert EffortEstimate.LARGE.value == "large"
        assert EffortEstimate.XL.value == "xl"
        
        # Test enum iteration
        estimates = list(EffortEstimate)
        assert len(estimates) == 4
        assert EffortEstimate.SMALL in estimates
        
        # Test enum comparison
        assert EffortEstimate.MEDIUM == EffortEstimate.MEDIUM
        assert EffortEstimate.SMALL != EffortEstimate.LARGE


class TestValidationResult:
    """Test ValidationResult model."""
    
    def test_validation_result_valid(self):
        """Test ValidationResult for valid case."""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []
        assert result.metadata == {}
    
    def test_validation_result_invalid(self):
        """Test ValidationResult for invalid case."""
        errors = ["Field X is required", "Field Y is invalid"]
        warnings = ["Deprecated field used"]
        result = ValidationResult(
            is_valid=False,
            errors=errors,
            warnings=warnings,
            metadata={"test": "data"}
        )
        assert result.is_valid is False
        assert result.errors == errors
        assert result.warnings == warnings
        assert result.metadata == {"test": "data"}
    
    def test_validation_result_partial(self):
        """Test ValidationResult with warnings only."""
        warnings = ["Minor issue detected"]
        result = ValidationResult(
            is_valid=True,
            warnings=warnings
        )
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == warnings
    
    def test_validation_result_add_error(self):
        """Test adding error to ValidationResult."""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert result.errors == []
        
        result.add_error("Test error")
        assert result.is_valid is False
        assert result.errors == ["Test error"]
    
    def test_validation_result_add_warning(self):
        """Test adding warning to ValidationResult."""
        result = ValidationResult(is_valid=True)
        assert result.warnings == []
        
        result.add_warning("Test warning")
        assert result.warnings == ["Test warning"]
        assert result.is_valid is True  # Warnings don't affect validity


class TestProcessingMetadata:
    """Test ProcessingMetadata model."""
    
    def test_processing_metadata_creation(self):
        """Test ProcessingMetadata creation with default values."""
        metadata = ProcessingMetadata()
        
        assert metadata.operation_id is not None
        assert isinstance(metadata.operation_id, str)
        assert metadata.start_time is not None
        assert metadata.end_time is None
        assert metadata.duration_seconds is None
        assert metadata.success is True
        assert metadata.error_message is None
        assert metadata.ai_service_used is None
        assert metadata.agent_role is None
        assert metadata.tokens_used is None
        assert metadata.cost_estimate is None
    
    def test_processing_metadata_full(self):
        """Test ProcessingMetadata with all fields."""
        metadata = ProcessingMetadata(
            operation_id="test-op-123",
            start_time=datetime(2023, 1, 1, 10, 0, 0),
            end_time=datetime(2023, 1, 1, 10, 5, 0),
            duration_seconds=300.0,
            success=False,
            error_message="Test error",
            ai_service_used=AIService.OPENAI,
            agent_role=AgentRole.BUSINESS_ANALYST,
            tokens_used=1000,
            cost_estimate=0.05,
            extra_field="extra_value"  # Should be allowed due to extra='allow'
        )
        
        assert metadata.operation_id == "test-op-123"
        assert metadata.success is False
        assert metadata.error_message == "Test error"
        assert metadata.ai_service_used == AIService.OPENAI
        assert metadata.agent_role == AgentRole.BUSINESS_ANALYST
        assert metadata.tokens_used == 1000
        assert metadata.cost_estimate == 0.05
        assert hasattr(metadata, 'extra_field')  # Extra field should be allowed
    
    def test_processing_metadata_mark_completed(self):
        """Test marking processing as completed."""
        metadata = ProcessingMetadata()
        original_start_time = metadata.start_time
        
        # Mark as completed successfully
        import time
        time.sleep(0.01)  # Small delay to ensure different timestamp
        
        metadata.mark_completed(success=True)
        
        assert metadata.success is True
        assert metadata.end_time is not None
        assert metadata.end_time > original_start_time
        assert metadata.duration_seconds is not None
        assert metadata.duration_seconds > 0
    
    def test_processing_metadata_mark_completed_with_error(self):
        """Test marking processing as completed with error."""
        metadata = ProcessingMetadata()
        
        metadata.mark_completed(success=False, error_message="Processing failed")
        
        assert metadata.success is False
        assert metadata.error_message == "Processing failed"
        assert metadata.end_time is not None
        assert metadata.duration_seconds is not None
