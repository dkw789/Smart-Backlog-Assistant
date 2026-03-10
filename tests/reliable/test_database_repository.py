"""Tests for database repository layer."""

import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import (
    Base,
    BacklogItem,
    CacheEntry,
    ItemCategory,
    ItemStatus,
    Priority,
    PriorityAssessment,
    ProcessingJob,
    Project,
    UserStory,
)
from src.database.repository import (
    BacklogItemRepository,
    CacheRepository,
    PriorityAssessmentRepository,
    ProcessingJobRepository,
    ProjectRepository,
    RepositoryManager,
    UserStoryRepository,
    get_repository_manager,
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


@pytest.fixture
def sample_project(in_memory_db):
    """Create a sample project for testing."""
    project = Project(name="Test Project", description="A test project")
    in_memory_db.add(project)
    in_memory_db.commit()
    return project


class TestProjectRepository:
    """Test the ProjectRepository class."""

    def test_create_project(self, in_memory_db):
        """Test creating a project."""
        repo = ProjectRepository(in_memory_db)
        
        project = repo.create_project("New Project", "Project description")
        
        assert project.id is not None
        assert project.name == "New Project"
        assert project.description == "Project description"
        assert project.created_at is not None

    def test_get_project(self, in_memory_db, sample_project):
        """Test getting a project by ID."""
        repo = ProjectRepository(in_memory_db)
        
        retrieved = repo.get_project(sample_project.id)
        
        assert retrieved is not None
        assert retrieved.id == sample_project.id
        assert retrieved.name == sample_project.name

    def test_get_project_nonexistent(self, in_memory_db):
        """Test getting a non-existent project."""
        repo = ProjectRepository(in_memory_db)
        
        retrieved = repo.get_project(uuid.uuid4())
        
        assert retrieved is None

    def test_get_project_by_name(self, in_memory_db, sample_project):
        """Test getting a project by name."""
        repo = ProjectRepository(in_memory_db)
        
        retrieved = repo.get_project_by_name("Test Project")
        
        assert retrieved is not None
        assert retrieved.id == sample_project.id

    def test_get_project_by_name_nonexistent(self, in_memory_db):
        """Test getting a non-existent project by name."""
        repo = ProjectRepository(in_memory_db)
        
        retrieved = repo.get_project_by_name("Non-existent Project")
        
        assert retrieved is None

    def test_list_projects(self, in_memory_db):
        """Test listing projects."""
        repo = ProjectRepository(in_memory_db)
        
        # Create multiple projects
        project1 = repo.create_project("Project 1")
        project2 = repo.create_project("Project 2")
        project3 = repo.create_project("Project 3")
        
        projects = repo.list_projects()
        
        assert len(projects) == 3
        # Should be ordered by created_at desc
        assert projects[0].name == "Project 3"

    def test_list_projects_with_limit(self, in_memory_db):
        """Test listing projects with limit."""
        repo = ProjectRepository(in_memory_db)
        
        # Create multiple projects
        for i in range(5):
            repo.create_project(f"Project {i}")
        
        projects = repo.list_projects(limit=3)
        
        assert len(projects) == 3

    def test_update_project(self, in_memory_db, sample_project):
        """Test updating a project."""
        repo = ProjectRepository(in_memory_db)
        
        updated = repo.update_project(
            sample_project.id,
            name="Updated Project",
            description="Updated description"
        )
        
        assert updated is not None
        assert updated.name == "Updated Project"
        assert updated.description == "Updated description"
        assert updated.updated_at is not None

    def test_update_project_nonexistent(self, in_memory_db):
        """Test updating a non-existent project."""
        repo = ProjectRepository(in_memory_db)
        
        updated = repo.update_project(uuid.uuid4(), name="Updated")
        
        assert updated is None

    def test_delete_project(self, in_memory_db, sample_project):
        """Test deleting a project."""
        repo = ProjectRepository(in_memory_db)
        
        result = repo.delete_project(sample_project.id)
        
        assert result is True
        assert repo.get_project(sample_project.id) is None

    def test_delete_project_nonexistent(self, in_memory_db):
        """Test deleting a non-existent project."""
        repo = ProjectRepository(in_memory_db)
        
        result = repo.delete_project(uuid.uuid4())
        
        assert result is False


class TestBacklogItemRepository:
    """Test the BacklogItemRepository class."""

    def test_create_backlog_item(self, in_memory_db, sample_project):
        """Test creating a backlog item."""
        repo = BacklogItemRepository(in_memory_db)
        
        item = repo.create_backlog_item(
            title="Test Item",
            description="Test description",
            project_id=sample_project.id,
            priority=Priority.HIGH,
            status=ItemStatus.IN_PROGRESS,
            category=ItemCategory.BUG,
            story_points=5
        )
        
        assert item.id is not None
        assert item.title == "Test Item"
        assert item.description == "Test description"
        assert item.project_id == sample_project.id
        assert item.priority == Priority.HIGH
        assert item.status == ItemStatus.IN_PROGRESS
        assert item.category == ItemCategory.BUG
        assert item.story_points == 5

    def test_create_backlog_item_with_defaults(self, in_memory_db):
        """Test creating a backlog item with default values."""
        repo = BacklogItemRepository(in_memory_db)
        
        item = repo.create_backlog_item("Test Item")
        
        assert item.priority == Priority.MEDIUM
        assert item.status == ItemStatus.TODO
        assert item.category == ItemCategory.FEATURE

    def test_get_backlog_item(self, in_memory_db, sample_project):
        """Test getting a backlog item."""
        repo = BacklogItemRepository(in_memory_db)
        
        item = repo.create_backlog_item("Test Item", project_id=sample_project.id)
        retrieved = repo.get_backlog_item(item.id)
        
        assert retrieved is not None
        assert retrieved.id == item.id

    def test_list_backlog_items(self, in_memory_db, sample_project):
        """Test listing backlog items."""
        repo = BacklogItemRepository(in_memory_db)
        
        # Create items with different attributes
        item1 = repo.create_backlog_item(
            "Item 1", project_id=sample_project.id, priority=Priority.HIGH
        )
        item2 = repo.create_backlog_item(
            "Item 2", project_id=sample_project.id, status=ItemStatus.DONE
        )
        item3 = repo.create_backlog_item(
            "Item 3", project_id=sample_project.id, category=ItemCategory.BUG
        )
        
        # Test listing all items
        all_items = repo.list_backlog_items(project_id=sample_project.id)
        assert len(all_items) == 3
        
        # Test filtering by priority
        high_priority = repo.list_backlog_items(priority=Priority.HIGH)
        assert len(high_priority) == 1
        assert high_priority[0].id == item1.id
        
        # Test filtering by status
        done_items = repo.list_backlog_items(status=ItemStatus.DONE)
        assert len(done_items) == 1
        assert done_items[0].id == item2.id
        
        # Test filtering by category
        bug_items = repo.list_backlog_items(category=ItemCategory.BUG)
        assert len(bug_items) == 1
        assert bug_items[0].id == item3.id

    def test_update_backlog_item(self, in_memory_db, sample_project):
        """Test updating a backlog item."""
        repo = BacklogItemRepository(in_memory_db)
        
        item = repo.create_backlog_item("Test Item", project_id=sample_project.id)
        
        updated = repo.update_backlog_item(
            item.id,
            title="Updated Item",
            priority=Priority.CRITICAL,
            story_points=8
        )
        
        assert updated is not None
        assert updated.title == "Updated Item"
        assert updated.priority == Priority.CRITICAL
        assert updated.story_points == 8
        assert updated.updated_at is not None

    def test_delete_backlog_item(self, in_memory_db, sample_project):
        """Test deleting a backlog item."""
        repo = BacklogItemRepository(in_memory_db)
        
        item = repo.create_backlog_item("Test Item", project_id=sample_project.id)
        
        result = repo.delete_backlog_item(item.id)
        
        assert result is True
        assert repo.get_backlog_item(item.id) is None

    def test_get_backlog_health_metrics(self, in_memory_db, sample_project):
        """Test getting backlog health metrics."""
        repo = BacklogItemRepository(in_memory_db)
        
        # Create items with different attributes
        repo.create_backlog_item(
            "Item 1", project_id=sample_project.id, priority=Priority.HIGH
        )
        repo.create_backlog_item(
            "Item 2", project_id=sample_project.id, priority=Priority.LOW,
            status=ItemStatus.DONE, category=ItemCategory.BUG
        )
        repo.create_backlog_item(
            "Item 3", project_id=sample_project.id, category=ItemCategory.ENHANCEMENT
        )
        
        metrics = repo.get_backlog_health_metrics(sample_project.id)
        
        assert metrics["total_items"] == 3
        assert "Priority.HIGH" in metrics["priority_distribution"]
        assert "Priority.LOW" in metrics["priority_distribution"]
        assert "Priority.MEDIUM" in metrics["priority_distribution"]
        assert "ItemStatus.TODO" in metrics["status_distribution"]
        assert "ItemStatus.DONE" in metrics["status_distribution"]
        assert "ItemCategory.FEATURE" in metrics["category_distribution"]
        assert "ItemCategory.BUG" in metrics["category_distribution"]
        assert "ItemCategory.ENHANCEMENT" in metrics["category_distribution"]


class TestUserStoryRepository:
    """Test the UserStoryRepository class."""

    def test_create_user_story(self, in_memory_db, sample_project):
        """Test creating a user story."""
        repo = UserStoryRepository(in_memory_db)
        
        story = repo.create_user_story(
            title="Test Story",
            user_type="developer",
            functionality="test functionality",
            benefit="test benefit",
            project_id=sample_project.id,
            acceptance_criteria=[{"criterion": "Should work"}],
            tags=["backend"]
        )
        
        assert story.id is not None
        assert story.title == "Test Story"
        assert story.user_type == "developer"
        assert story.functionality == "test functionality"
        assert story.benefit == "test benefit"
        assert story.project_id == sample_project.id
        assert story.acceptance_criteria == [{"criterion": "Should work"}]
        assert story.tags == ["backend"]

    def test_get_user_story(self, in_memory_db, sample_project):
        """Test getting a user story."""
        repo = UserStoryRepository(in_memory_db)
        
        story = repo.create_user_story("Test Story", project_id=sample_project.id)
        retrieved = repo.get_user_story(story.id)
        
        assert retrieved is not None
        assert retrieved.id == story.id

    def test_list_user_stories(self, in_memory_db, sample_project):
        """Test listing user stories."""
        repo = UserStoryRepository(in_memory_db)
        item_repo = BacklogItemRepository(in_memory_db)
        
        # Create backlog item
        item = item_repo.create_backlog_item("Test Item", project_id=sample_project.id)
        
        # Create stories
        story1 = repo.create_user_story("Story 1", project_id=sample_project.id)
        story2 = repo.create_user_story(
            "Story 2", project_id=sample_project.id, backlog_item_id=item.id
        )
        
        # Test listing by project
        project_stories = repo.list_user_stories(project_id=sample_project.id)
        assert len(project_stories) == 2
        
        # Test listing by backlog item
        item_stories = repo.list_user_stories(backlog_item_id=item.id)
        assert len(item_stories) == 1
        assert item_stories[0].id == story2.id

    def test_update_user_story(self, in_memory_db, sample_project):
        """Test updating a user story."""
        repo = UserStoryRepository(in_memory_db)
        
        story = repo.create_user_story("Test Story", project_id=sample_project.id)
        
        updated = repo.update_user_story(
            story.id,
            title="Updated Story",
            priority=Priority.HIGH
        )
        
        assert updated is not None
        assert updated.title == "Updated Story"
        assert updated.priority == Priority.HIGH

    def test_delete_user_story(self, in_memory_db, sample_project):
        """Test deleting a user story."""
        repo = UserStoryRepository(in_memory_db)
        
        story = repo.create_user_story("Test Story", project_id=sample_project.id)
        
        result = repo.delete_user_story(story.id)
        
        assert result is True
        assert repo.get_user_story(story.id) is None


class TestPriorityAssessmentRepository:
    """Test the PriorityAssessmentRepository class."""

    def test_create_priority_assessment(self, in_memory_db, sample_project):
        """Test creating a priority assessment."""
        item_repo = BacklogItemRepository(in_memory_db)
        repo = PriorityAssessmentRepository(in_memory_db)
        
        item = item_repo.create_backlog_item("Test Item", project_id=sample_project.id)
        
        assessment = repo.create_priority_assessment(
            backlog_item_id=item.id,
            priority=Priority.HIGH,
            category=ItemCategory.FEATURE,
            business_impact="High",
            technical_complexity="Medium",
            reasoning="Important feature",
            confidence_score=0.8,
            generated_by_ai=True,
            ai_service_used="anthropic"
        )
        
        assert assessment.id is not None
        assert assessment.backlog_item_id == item.id
        assert assessment.priority == Priority.HIGH
        assert assessment.category == ItemCategory.FEATURE
        assert assessment.business_impact == "High"
        assert assessment.technical_complexity == "Medium"
        assert assessment.reasoning == "Important feature"
        assert assessment.confidence_score == 0.8
        assert assessment.generated_by_ai is True
        assert assessment.ai_service_used == "anthropic"

    def test_get_latest_assessment(self, in_memory_db, sample_project):
        """Test getting the latest priority assessment."""
        item_repo = BacklogItemRepository(in_memory_db)
        repo = PriorityAssessmentRepository(in_memory_db)
        
        item = item_repo.create_backlog_item("Test Item", project_id=sample_project.id)
        
        # Create multiple assessments
        assessment1 = repo.create_priority_assessment(
            backlog_item_id=item.id,
            priority=Priority.LOW,
            category=ItemCategory.FEATURE,
            business_impact="Low",
            technical_complexity="Low",
            reasoning="First assessment",
            confidence_score=0.6
        )
        
        assessment2 = repo.create_priority_assessment(
            backlog_item_id=item.id,
            priority=Priority.HIGH,
            category=ItemCategory.FEATURE,
            business_impact="High",
            technical_complexity="Medium",
            reasoning="Updated assessment",
            confidence_score=0.9
        )
        
        latest = repo.get_latest_assessment(item.id)
        
        assert latest is not None
        assert latest.id == assessment2.id
        assert latest.reasoning == "Updated assessment"

    def test_list_assessments(self, in_memory_db, sample_project):
        """Test listing priority assessments."""
        item_repo = BacklogItemRepository(in_memory_db)
        repo = PriorityAssessmentRepository(in_memory_db)
        
        item1 = item_repo.create_backlog_item("Item 1", project_id=sample_project.id)
        item2 = item_repo.create_backlog_item("Item 2", project_id=sample_project.id)
        
        # Create assessments for different items
        assessment1 = repo.create_priority_assessment(
            backlog_item_id=item1.id,
            priority=Priority.HIGH,
            category=ItemCategory.FEATURE,
            business_impact="High",
            technical_complexity="Low",
            reasoning="Assessment 1",
            confidence_score=0.8
        )
        
        assessment2 = repo.create_priority_assessment(
            backlog_item_id=item2.id,
            priority=Priority.MEDIUM,
            category=ItemCategory.BUG,
            business_impact="Medium",
            technical_complexity="High",
            reasoning="Assessment 2",
            confidence_score=0.7
        )
        
        # Test listing all assessments
        all_assessments = repo.list_assessments()
        assert len(all_assessments) == 2
        
        # Test listing assessments for specific item
        item1_assessments = repo.list_assessments(backlog_item_id=item1.id)
        assert len(item1_assessments) == 1
        assert item1_assessments[0].id == assessment1.id


class TestProcessingJobRepository:
    """Test the ProcessingJobRepository class."""

    def test_create_processing_job(self, in_memory_db, sample_project):
        """Test creating a processing job."""
        repo = ProcessingJobRepository(in_memory_db)
        
        job = repo.create_processing_job(
            job_type="meeting_notes",
            status="pending",
            project_id=sample_project.id,
            input_file_path="/path/to/input.txt",
            processing_mode="async"
        )
        
        assert job.id is not None
        assert job.job_type == "meeting_notes"
        assert job.status == "pending"
        assert job.project_id == sample_project.id
        assert job.input_file_path == "/path/to/input.txt"
        assert job.processing_mode == "async"

    def test_update_job_status(self, in_memory_db):
        """Test updating job status."""
        repo = ProcessingJobRepository(in_memory_db)
        
        job = repo.create_processing_job("test_job", "pending")
        
        # Update to running
        updated = repo.update_job_status(job.id, "running")
        assert updated.status == "running"
        assert updated.started_at is not None
        
        # Update to completed
        updated = repo.update_job_status(
            job.id, "completed", 
            processing_time=5.2,
            results={"items": 10}
        )
        assert updated.status == "completed"
        assert updated.completed_at is not None
        assert updated.processing_time == 5.2
        assert updated.results == {"items": 10}

    def test_list_processing_jobs(self, in_memory_db, sample_project):
        """Test listing processing jobs."""
        repo = ProcessingJobRepository(in_memory_db)
        
        # Create jobs with different attributes
        job1 = repo.create_processing_job(
            "meeting_notes", "completed", project_id=sample_project.id
        )
        job2 = repo.create_processing_job(
            "backlog_analysis", "running", project_id=sample_project.id
        )
        job3 = repo.create_processing_job("other_job", "pending")
        
        # Test listing by project
        project_jobs = repo.list_processing_jobs(project_id=sample_project.id)
        assert len(project_jobs) == 2
        
        # Test listing by job type
        meeting_jobs = repo.list_processing_jobs(job_type="meeting_notes")
        assert len(meeting_jobs) == 1
        assert meeting_jobs[0].id == job1.id
        
        # Test listing by status
        running_jobs = repo.list_processing_jobs(status="running")
        assert len(running_jobs) == 1
        assert running_jobs[0].id == job2.id


class TestCacheRepository:
    """Test the CacheRepository class."""

    def test_set_cache(self, in_memory_db):
        """Test setting a cache entry."""
        repo = CacheRepository(in_memory_db)
        
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        entry = repo.set_cache(
            cache_key="test_key",
            cache_value={"data": "test_value"},
            expires_at=expires_at,
            tags=["tag1", "tag2"],
            size_bytes=100
        )
        
        assert entry.id is not None
        assert entry.cache_key == "test_key"
        assert entry.cache_value == {"data": "test_value"}
        assert entry.expires_at == expires_at
        assert entry.tags == ["tag1", "tag2"]
        assert entry.size_bytes == 100

    def test_set_cache_replaces_existing(self, in_memory_db):
        """Test that setting cache replaces existing entry."""
        repo = CacheRepository(in_memory_db)
        
        # Set initial entry
        entry1 = repo.set_cache("test_key", {"data": "value1"})
        
        # Set new entry with same key
        entry2 = repo.set_cache("test_key", {"data": "value2"})
        
        # Should be different entries
        assert entry1.id != entry2.id
        
        # Should only have one entry in database
        retrieved = repo.get_cache("test_key")
        assert retrieved.cache_value == {"data": "value2"}

    def test_get_cache(self, in_memory_db):
        """Test getting a cache entry."""
        repo = CacheRepository(in_memory_db)
        
        # Set cache entry
        original = repo.set_cache("test_key", {"data": "value"})
        
        # Get cache entry
        retrieved = repo.get_cache("test_key")
        
        assert retrieved is not None
        assert retrieved.cache_key == "test_key"
        assert retrieved.cache_value == {"data": "value"}
        assert retrieved.access_count == 1
        assert retrieved.hit_count == 1
        assert retrieved.last_accessed is not None

    def test_get_cache_nonexistent(self, in_memory_db):
        """Test getting a non-existent cache entry."""
        repo = CacheRepository(in_memory_db)
        
        retrieved = repo.get_cache("nonexistent_key")
        
        assert retrieved is None

    def test_get_cache_expired(self, in_memory_db):
        """Test getting an expired cache entry."""
        repo = CacheRepository(in_memory_db)
        
        # Set cache entry that expires in the past
        expires_at = datetime.utcnow() - timedelta(hours=1)
        repo.set_cache("expired_key", {"data": "value"}, expires_at=expires_at)
        
        # Should return None and delete the entry
        retrieved = repo.get_cache("expired_key")
        
        assert retrieved is None

    def test_delete_cache(self, in_memory_db):
        """Test deleting a cache entry."""
        repo = CacheRepository(in_memory_db)
        
        repo.set_cache("test_key", {"data": "value"})
        
        result = repo.delete_cache("test_key")
        
        assert result is True
        assert repo.get_cache("test_key") is None

    def test_delete_cache_nonexistent(self, in_memory_db):
        """Test deleting a non-existent cache entry."""
        repo = CacheRepository(in_memory_db)
        
        result = repo.delete_cache("nonexistent_key")
        
        assert result is False

    def test_invalidate_by_tags(self, in_memory_db):
        """Test invalidating cache entries by tags."""
        repo = CacheRepository(in_memory_db)
        
        # Set entries with different tags
        repo.set_cache("key1", {"data": "value1"}, tags=["tag1", "tag2"])
        repo.set_cache("key2", {"data": "value2"}, tags=["tag2", "tag3"])
        repo.set_cache("key3", {"data": "value3"}, tags=["tag3"])
        
        # Invalidate by tag2
        count = repo.invalidate_by_tags(["tag2"])
        
        assert count == 2  # key1 and key2 should be invalidated
        assert repo.get_cache("key1") is None
        assert repo.get_cache("key2") is None
        assert repo.get_cache("key3") is not None

    def test_cleanup_expired(self, in_memory_db):
        """Test cleaning up expired cache entries."""
        repo = CacheRepository(in_memory_db)
        
        # Set entries with different expiration times
        past_time = datetime.utcnow() - timedelta(hours=1)
        future_time = datetime.utcnow() + timedelta(hours=1)
        
        repo.set_cache("expired1", {"data": "value1"}, expires_at=past_time)
        repo.set_cache("expired2", {"data": "value2"}, expires_at=past_time)
        repo.set_cache("valid", {"data": "value3"}, expires_at=future_time)
        
        # Clean up expired entries
        count = repo.cleanup_expired()
        
        assert count == 2
        assert repo.get_cache("expired1") is None
        assert repo.get_cache("expired2") is None
        assert repo.get_cache("valid") is not None

    def test_get_cache_stats(self, in_memory_db):
        """Test getting cache statistics."""
        repo = CacheRepository(in_memory_db)
        
        # Set some cache entries
        repo.set_cache("key1", {"data": "value1"}, size_bytes=100)
        repo.set_cache("key2", {"data": "value2"}, size_bytes=200)
        
        # Access one entry multiple times
        repo.get_cache("key1")
        repo.get_cache("key1")
        
        stats = repo.get_cache_stats()
        
        assert stats["total_entries"] == 2
        assert stats["total_size_bytes"] == 300
        assert stats["total_hits"] == 2
        assert stats["total_accesses"] == 2
        assert stats["hit_rate_percent"] == 100.0


class TestRepositoryManager:
    """Test the RepositoryManager class."""

    def test_repository_manager_creation(self, in_memory_db):
        """Test creating a repository manager."""
        manager = RepositoryManager(in_memory_db)
        
        assert manager.session == in_memory_db
        assert isinstance(manager.projects, ProjectRepository)
        assert isinstance(manager.backlog_items, BacklogItemRepository)
        assert isinstance(manager.user_stories, UserStoryRepository)
        assert isinstance(manager.priority_assessments, PriorityAssessmentRepository)
        assert isinstance(manager.processing_jobs, ProcessingJobRepository)
        assert isinstance(manager.cache, CacheRepository)

    def test_repository_manager_context_manager(self):
        """Test repository manager as context manager."""
        with patch('src.database.models.db_manager') as mock_db_manager:
            mock_session = Mock()
            mock_db_manager.get_session.return_value = mock_session
            
            with RepositoryManager() as manager:
                assert manager.session == mock_session
            
            # Should commit on successful exit
            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()

    def test_repository_manager_context_manager_with_exception(self):
        """Test repository manager context manager with exception."""
        with patch('src.database.models.db_manager') as mock_db_manager:
            mock_session = Mock()
            mock_db_manager.get_session.return_value = mock_session
            
            try:
                with RepositoryManager() as manager:
                    raise ValueError("Test exception")
            except ValueError:
                pass
            
            # Should rollback on exception
            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()

    def test_get_repository_manager(self):
        """Test the get_repository_manager convenience function."""
        with patch('src.database.repository.RepositoryManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            
            result = get_repository_manager()
            
            assert result == mock_manager
            mock_manager_class.assert_called_once_with()

    def test_repository_manager_commit_rollback(self, in_memory_db):
        """Test manual commit and rollback operations."""
        manager = RepositoryManager(in_memory_db)
        
        # Create a project
        project = manager.projects.create_project("Test Project")
        
        # Manual rollback
        manager.rollback()
        
        # Project should not exist after rollback
        retrieved = manager.projects.get_project(project.id)
        assert retrieved is None
        
        # Create project again and commit
        project = manager.projects.create_project("Test Project")
        manager.commit()
        
        # Project should exist after commit
        retrieved = manager.projects.get_project(project.id)
        assert retrieved is not None


class TestRepositoryIntegration:
    """Test repository integration scenarios."""

    def test_full_workflow_with_repositories(self, in_memory_db):
        """Test a complete workflow using repositories."""
        manager = RepositoryManager(in_memory_db)
        
        # Create project
        project = manager.projects.create_project("Integration Test")
        
        # Create backlog item
        item = manager.backlog_items.create_backlog_item(
            "Test Feature",
            "Implement test feature",
            project_id=project.id,
            priority=Priority.HIGH
        )
        
        # Create user story
        story = manager.user_stories.create_user_story(
            "User Story",
            user_type="user",
            functionality="use test feature",
            benefit="get value",
            project_id=project.id,
            backlog_item_id=item.id
        )
        
        # Create priority assessment
        assessment = manager.priority_assessments.create_priority_assessment(
            backlog_item_id=item.id,
            priority=Priority.HIGH,
            category=ItemCategory.FEATURE,
            business_impact="High",
            technical_complexity="Medium",
            reasoning="Important feature",
            confidence_score=0.9
        )
        
        # Create processing job
        job = manager.processing_jobs.create_processing_job(
            "integration_test",
            "completed",
            project_id=project.id
        )
        
        # Set cache entry
        cache_entry = manager.cache.set_cache(
            "integration_cache",
            {"project_id": str(project.id)},
            tags=["integration"]
        )
        
        manager.commit()
        
        # Verify all entities are created and related correctly
        assert project.id is not None
        assert item.project_id == project.id
        assert story.project_id == project.id
        assert story.backlog_item_id == item.id
        assert assessment.backlog_item_id == item.id
        assert job.project_id == project.id
        assert cache_entry.cache_key == "integration_cache"
        
        # Test health metrics
        metrics = manager.backlog_items.get_backlog_health_metrics(project.id)
        assert metrics["total_items"] == 1
        assert "Priority.HIGH" in metrics["priority_distribution"]

    def test_repository_error_handling(self, in_memory_db):
        """Test repository error handling."""
        manager = RepositoryManager(in_memory_db)
        
        # Test operations on non-existent entities
        assert manager.projects.get_project(uuid.uuid4()) is None
        assert manager.projects.update_project(uuid.uuid4(), name="Test") is None
        assert manager.projects.delete_project(uuid.uuid4()) is False
        
        assert manager.backlog_items.get_backlog_item(uuid.uuid4()) is None
        assert manager.user_stories.get_user_story(uuid.uuid4()) is None
        assert manager.cache.get_cache("nonexistent") is None
        assert manager.cache.delete_cache("nonexistent") is False
