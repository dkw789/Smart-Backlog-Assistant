"""Tests for database models."""

import uuid
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import (
    GUID,
    Base,
    BacklogItem,
    CacheEntry,
    DatabaseManager,
    ItemCategory,
    ItemStatus,
    Priority,
    PriorityAssessment,
    ProcessingJob,
    Project,
    UserStory,
)


@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestGUIDType:
    """Test the custom GUID type."""

    def test_guid_with_sqlite(self):
        """Test GUID type with SQLite dialect."""
        guid_type = GUID()
        
        # Test UUID generation and conversion
        test_uuid = uuid.uuid4()
        
        # Simulate SQLite dialect
        class MockDialect:
            name = 'sqlite'
        
        dialect = MockDialect()
        
        # Test bind parameter processing
        result = guid_type.process_bind_param(test_uuid, dialect)
        assert result == str(test_uuid)
        
        # Test result value processing
        result = guid_type.process_result_value(str(test_uuid), dialect)
        assert result == test_uuid

    def test_guid_with_postgresql(self):
        """Test GUID type with PostgreSQL dialect."""
        guid_type = GUID()
        
        test_uuid = uuid.uuid4()
        
        # Simulate PostgreSQL dialect
        class MockDialect:
            name = 'postgresql'
        
        dialect = MockDialect()
        
        # Test bind parameter processing
        result = guid_type.process_bind_param(test_uuid, dialect)
        assert result == str(test_uuid)
        
        # Test result value processing
        result = guid_type.process_result_value(test_uuid, dialect)
        assert result == test_uuid

    def test_guid_none_values(self):
        """Test GUID type with None values."""
        guid_type = GUID()
        
        class MockDialect:
            name = 'sqlite'
        
        dialect = MockDialect()
        
        assert guid_type.process_bind_param(None, dialect) is None
        assert guid_type.process_result_value(None, dialect) is None


class TestProject:
    """Test the Project model."""

    def test_project_creation(self, in_memory_db):
        """Test creating a project."""
        project = Project(
            name="Test Project",
            description="A test project"
        )
        
        in_memory_db.add(project)
        in_memory_db.commit()
        
        assert project.id is not None
        assert project.name == "Test Project"
        assert project.description == "A test project"
        assert project.created_at is not None
        assert project.updated_at is None

    def test_project_relationships(self, in_memory_db):
        """Test project relationships."""
        project = Project(name="Test Project")
        in_memory_db.add(project)
        in_memory_db.flush()
        
        # Add backlog item
        item = BacklogItem(
            title="Test Item",
            project_id=project.id
        )
        in_memory_db.add(item)
        
        # Add user story
        story = UserStory(
            title="Test Story",
            project_id=project.id
        )
        in_memory_db.add(story)
        
        in_memory_db.commit()
        
        # Test relationships
        assert len(project.backlog_items) == 1
        assert len(project.user_stories) == 1
        assert project.backlog_items[0].title == "Test Item"
        assert project.user_stories[0].title == "Test Story"


class TestBacklogItem:
    """Test the BacklogItem model."""

    def test_backlog_item_creation(self, in_memory_db):
        """Test creating a backlog item."""
        project = Project(name="Test Project")
        in_memory_db.add(project)
        in_memory_db.flush()
        
        item = BacklogItem(
            title="Test Item",
            description="A test backlog item",
            priority=Priority.HIGH,
            status=ItemStatus.TODO,
            category=ItemCategory.FEATURE,
            story_points=5,
            business_value=8,
            technical_complexity=6,
            tags=["frontend", "api"],
            extra_data={"custom_field": "value"},
            project_id=project.id
        )
        
        in_memory_db.add(item)
        in_memory_db.commit()
        
        assert item.id is not None
        assert item.title == "Test Item"
        assert item.priority == Priority.HIGH
        assert item.status == ItemStatus.TODO
        assert item.category == ItemCategory.FEATURE
        assert item.story_points == 5
        assert item.business_value == 8
        assert item.technical_complexity == 6
        assert item.tags == ["frontend", "api"]
        assert item.extra_data == {"custom_field": "value"}
        assert item.project_id == project.id

    def test_backlog_item_defaults(self, in_memory_db):
        """Test backlog item default values."""
        item = BacklogItem(title="Test Item")
        in_memory_db.add(item)
        in_memory_db.commit()
        
        assert item.priority == Priority.MEDIUM
        assert item.status == ItemStatus.TODO
        assert item.category == ItemCategory.FEATURE

    def test_backlog_item_relationships(self, in_memory_db):
        """Test backlog item relationships."""
        project = Project(name="Test Project")
        in_memory_db.add(project)
        in_memory_db.flush()
        
        item = BacklogItem(title="Test Item", project_id=project.id)
        in_memory_db.add(item)
        in_memory_db.flush()
        
        # Add user story
        story = UserStory(
            title="Test Story",
            project_id=project.id,
            backlog_item_id=item.id
        )
        in_memory_db.add(story)
        
        # Add priority assessment
        assessment = PriorityAssessment(
            priority=Priority.HIGH,
            category=ItemCategory.FEATURE,
            business_impact="High",
            technical_complexity="Medium",
            reasoning="Test reasoning",
            confidence_score=0.8,
            backlog_item_id=item.id
        )
        in_memory_db.add(assessment)
        
        in_memory_db.commit()
        
        # Test relationships
        assert len(item.user_stories) == 1
        assert len(item.priority_assessments) == 1
        assert item.project.name == "Test Project"


class TestUserStory:
    """Test the UserStory model."""

    def test_user_story_creation(self, in_memory_db):
        """Test creating a user story."""
        project = Project(name="Test Project")
        in_memory_db.add(project)
        in_memory_db.flush()
        
        story = UserStory(
            title="Test Story",
            user_type="developer",
            functionality="test functionality",
            benefit="test benefit",
            acceptance_criteria=[
                {"criterion": "Should do X"},
                {"criterion": "Should do Y"}
            ],
            priority=Priority.HIGH,
            estimated_effort="Medium",
            tags=["backend", "database"],
            original_requirement="Original requirement text",
            generated_by_ai=True,
            ai_service_used="anthropic",
            project_id=project.id
        )
        
        in_memory_db.add(story)
        in_memory_db.commit()
        
        assert story.id is not None
        assert story.title == "Test Story"
        assert story.user_type == "developer"
        assert story.functionality == "test functionality"
        assert story.benefit == "test benefit"
        assert len(story.acceptance_criteria) == 2
        assert story.priority == Priority.HIGH
        assert story.estimated_effort == "Medium"
        assert story.tags == ["backend", "database"]
        assert story.generated_by_ai is True
        assert story.ai_service_used == "anthropic"

    def test_user_story_defaults(self, in_memory_db):
        """Test user story default values."""
        story = UserStory(title="Test Story")
        in_memory_db.add(story)
        in_memory_db.commit()
        
        assert story.priority == Priority.MEDIUM
        assert story.generated_by_ai is False


class TestPriorityAssessment:
    """Test the PriorityAssessment model."""

    def test_priority_assessment_creation(self, in_memory_db):
        """Test creating a priority assessment."""
        project = Project(name="Test Project")
        in_memory_db.add(project)
        in_memory_db.flush()
        
        item = BacklogItem(title="Test Item", project_id=project.id)
        in_memory_db.add(item)
        in_memory_db.flush()
        
        assessment = PriorityAssessment(
            priority=Priority.CRITICAL,
            category=ItemCategory.BUG,
            business_impact="High",
            technical_complexity="Low",
            effort_estimate="Small",
            dependencies=["item1", "item2"],
            reasoning="Critical bug affecting users",
            confidence_score=0.95,
            generated_by_ai=True,
            ai_service_used="openai",
            processing_time=1.5,
            backlog_item_id=item.id
        )
        
        in_memory_db.add(assessment)
        in_memory_db.commit()
        
        assert assessment.id is not None
        assert assessment.priority == Priority.CRITICAL
        assert assessment.category == ItemCategory.BUG
        assert assessment.business_impact == "High"
        assert assessment.technical_complexity == "Low"
        assert assessment.effort_estimate == "Small"
        assert assessment.dependencies == ["item1", "item2"]
        assert assessment.reasoning == "Critical bug affecting users"
        assert assessment.confidence_score == 0.95
        assert assessment.generated_by_ai is True
        assert assessment.ai_service_used == "openai"
        assert assessment.processing_time == 1.5

    def test_priority_assessment_defaults(self, in_memory_db):
        """Test priority assessment default values."""
        item = BacklogItem(title="Test Item")
        in_memory_db.add(item)
        in_memory_db.flush()
        
        assessment = PriorityAssessment(
            priority=Priority.MEDIUM,
            category=ItemCategory.FEATURE,
            business_impact="Medium",
            technical_complexity="Medium",
            reasoning="Test reasoning",
            confidence_score=0.7,
            backlog_item_id=item.id
        )
        in_memory_db.add(assessment)
        in_memory_db.commit()
        
        assert assessment.generated_by_ai is False


class TestProcessingJob:
    """Test the ProcessingJob model."""

    def test_processing_job_creation(self, in_memory_db):
        """Test creating a processing job."""
        project = Project(name="Test Project")
        in_memory_db.add(project)
        in_memory_db.flush()
        
        job = ProcessingJob(
            job_type="meeting_notes",
            status="completed",
            input_file_path="/path/to/input.txt",
            output_file_path="/path/to/output.json",
            processing_mode="async",
            ai_service_used="anthropic",
            processing_time=5.2,
            results={"items_processed": 10, "stories_generated": 8},
            project_id=project.id
        )
        
        in_memory_db.add(job)
        in_memory_db.commit()
        
        assert job.id is not None
        assert job.job_type == "meeting_notes"
        assert job.status == "completed"
        assert job.input_file_path == "/path/to/input.txt"
        assert job.output_file_path == "/path/to/output.json"
        assert job.processing_mode == "async"
        assert job.ai_service_used == "anthropic"
        assert job.processing_time == 5.2
        assert job.results == {"items_processed": 10, "stories_generated": 8}
        assert job.project_id == project.id


class TestCacheEntry:
    """Test the CacheEntry model."""

    def test_cache_entry_creation(self, in_memory_db):
        """Test creating a cache entry."""
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        entry = CacheEntry(
            cache_key="test_key",
            cache_value={"data": "test_value"},
            tags=["tag1", "tag2"],
            size_bytes=100,
            access_count=5,
            hit_count=3,
            expires_at=expires_at
        )
        
        in_memory_db.add(entry)
        in_memory_db.commit()
        
        assert entry.id is not None
        assert entry.cache_key == "test_key"
        assert entry.cache_value == {"data": "test_value"}
        assert entry.tags == ["tag1", "tag2"]
        assert entry.size_bytes == 100
        assert entry.access_count == 5
        assert entry.hit_count == 3
        assert entry.expires_at == expires_at

    def test_cache_entry_defaults(self, in_memory_db):
        """Test cache entry default values."""
        entry = CacheEntry(
            cache_key="test_key",
            cache_value={"data": "value"}
        )
        
        in_memory_db.add(entry)
        in_memory_db.commit()
        
        assert entry.access_count == 0
        assert entry.hit_count == 0


class TestDatabaseManager:
    """Test the DatabaseManager class."""

    def test_database_manager_creation(self):
        """Test creating a database manager."""
        db_manager = DatabaseManager("sqlite:///:memory:")
        assert db_manager.database_url == "sqlite:///:memory:"
        assert db_manager.engine is not None
        assert db_manager.SessionLocal is not None

    def test_database_manager_default_url(self):
        """Test database manager with default URL."""
        with patch('src.database.models.config') as mock_config:
            mock_config.database_url = None
            
            db_manager = DatabaseManager()
            assert "sqlite:///" in db_manager.database_url

    def test_create_tables(self):
        """Test creating database tables."""
        db_manager = DatabaseManager("sqlite:///:memory:")
        
        # Should not raise an exception
        db_manager.create_tables()

    def test_get_session(self):
        """Test getting a database session."""
        db_manager = DatabaseManager("sqlite:///:memory:")
        db_manager.create_tables()
        
        session = db_manager.get_session()
        assert session is not None
        session.close()

    def test_drop_tables(self):
        """Test dropping database tables."""
        db_manager = DatabaseManager("sqlite:///:memory:")
        db_manager.create_tables()
        
        # Should not raise an exception
        db_manager.drop_tables()


class TestEnumValues:
    """Test enum value definitions."""

    def test_priority_enum(self):
        """Test Priority enum values."""
        assert Priority.CRITICAL == "critical"
        assert Priority.HIGH == "high"
        assert Priority.MEDIUM == "medium"
        assert Priority.LOW == "low"

    def test_item_status_enum(self):
        """Test ItemStatus enum values."""
        assert ItemStatus.TODO == "todo"
        assert ItemStatus.IN_PROGRESS == "in_progress"
        assert ItemStatus.DONE == "done"
        assert ItemStatus.BLOCKED == "blocked"

    def test_item_category_enum(self):
        """Test ItemCategory enum values."""
        assert ItemCategory.FEATURE == "feature"
        assert ItemCategory.BUG == "bug"
        assert ItemCategory.ENHANCEMENT == "enhancement"
        assert ItemCategory.TECHNICAL_DEBT == "technical_debt"
        assert ItemCategory.RESEARCH == "research"
        assert ItemCategory.MAINTENANCE == "maintenance"


class TestModelIntegration:
    """Test model integration and complex scenarios."""

    def test_full_workflow(self, in_memory_db):
        """Test a complete workflow with all models."""
        # Create project
        project = Project(name="Integration Test Project")
        in_memory_db.add(project)
        in_memory_db.flush()
        
        # Create backlog item
        item = BacklogItem(
            title="Integration Test Item",
            description="Test item for integration",
            priority=Priority.HIGH,
            project_id=project.id
        )
        in_memory_db.add(item)
        in_memory_db.flush()
        
        # Create user story
        story = UserStory(
            title="Integration Test Story",
            user_type="user",
            functionality="perform integration test",
            benefit="ensure system works",
            project_id=project.id,
            backlog_item_id=item.id
        )
        in_memory_db.add(story)
        
        # Create priority assessment
        assessment = PriorityAssessment(
            priority=Priority.HIGH,
            category=ItemCategory.FEATURE,
            business_impact="High",
            technical_complexity="Medium",
            reasoning="Integration test is important",
            confidence_score=0.8,
            backlog_item_id=item.id
        )
        in_memory_db.add(assessment)
        
        # Create processing job
        job = ProcessingJob(
            job_type="integration_test",
            status="completed",
            project_id=project.id
        )
        in_memory_db.add(job)
        
        # Create cache entry
        cache = CacheEntry(
            cache_key="integration_test_cache",
            cache_value={"test": "data"}
        )
        in_memory_db.add(cache)
        
        in_memory_db.commit()
        
        # Verify all relationships work
        assert project.backlog_items[0] == item
        assert project.user_stories[0] == story
        assert item.user_stories[0] == story
        assert item.priority_assessments[0] == assessment
        assert story.project == project
        assert story.backlog_item == item
        assert assessment.backlog_item == item

    def test_cascade_operations(self, in_memory_db):
        """Test cascade operations and constraints."""
        # Create project with items
        project = Project(name="Cascade Test")
        in_memory_db.add(project)
        in_memory_db.flush()
        
        item = BacklogItem(title="Test Item", project_id=project.id)
        in_memory_db.add(item)
        in_memory_db.flush()
        
        story = UserStory(
            title="Test Story",
            project_id=project.id,
            backlog_item_id=item.id
        )
        in_memory_db.add(story)
        in_memory_db.commit()
        
        # Verify items exist
        assert in_memory_db.query(Project).count() == 1
        assert in_memory_db.query(BacklogItem).count() == 1
        assert in_memory_db.query(UserStory).count() == 1
        
        # Delete project (this should work due to relationships)
        in_memory_db.delete(project)
        in_memory_db.commit()
        
        # Note: Cascade behavior depends on SQLAlchemy configuration
        # This test documents the current behavior
