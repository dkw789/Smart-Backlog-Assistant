"""Repository pattern implementation for database operations."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session

from src.database.models import (
    BacklogItem,
    CacheEntry,
    ItemCategory,
    ItemStatus,
    Priority,
    PriorityAssessment,
    ProcessingJob,
    Project,
    UserStory,
    get_db,
)


class BaseRepository:
    """Base repository with common database operations."""

    def __init__(self, session: Session):
        self.session = session

    def commit(self):
        """Commit the current transaction."""
        self.session.commit()

    def rollback(self):
        """Rollback the current transaction."""
        self.session.rollback()

    def refresh(self, obj):
        """Refresh an object from the database."""
        self.session.refresh(obj)


class ProjectRepository(BaseRepository):
    """Repository for project operations."""

    def create_project(self, name: str, description: Optional[str] = None) -> Project:
        """Create a new project."""
        project = Project(name=name, description=description)
        self.session.add(project)
        self.session.flush()
        return project

    def get_project(self, project_id: UUID) -> Optional[Project]:
        """Get a project by ID."""
        return self.session.query(Project).filter(Project.id == project_id).first()

    def get_project_by_name(self, name: str) -> Optional[Project]:
        """Get a project by name."""
        return self.session.query(Project).filter(Project.name == name).first()

    def list_projects(self, limit: int = 100) -> List[Project]:
        """List all projects."""
        return self.session.query(Project).order_by(desc(Project.created_at)).limit(limit).all()

    def update_project(self, project_id: UUID, **kwargs) -> Optional[Project]:
        """Update a project."""
        project = self.get_project(project_id)
        if project:
            for key, value in kwargs.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            project.updated_at = datetime.utcnow()
            self.session.flush()
        return project

    def delete_project(self, project_id: UUID) -> bool:
        """Delete a project."""
        project = self.get_project(project_id)
        if project:
            self.session.delete(project)
            return True
        return False


class BacklogItemRepository(BaseRepository):
    """Repository for backlog item operations."""

    def create_backlog_item(
        self,
        title: str,
        description: Optional[str] = None,
        project_id: Optional[UUID] = None,
        priority: Priority = Priority.MEDIUM,
        status: ItemStatus = ItemStatus.TODO,
        category: ItemCategory = ItemCategory.FEATURE,
        **kwargs
    ) -> BacklogItem:
        """Create a new backlog item."""
        item = BacklogItem(
            title=title,
            description=description,
            project_id=project_id,
            priority=priority,
            status=status,
            category=category,
            **kwargs
        )
        self.session.add(item)
        self.session.flush()
        return item

    def get_backlog_item(self, item_id: UUID) -> Optional[BacklogItem]:
        """Get a backlog item by ID."""
        return self.session.query(BacklogItem).filter(BacklogItem.id == item_id).first()

    def list_backlog_items(
        self,
        project_id: Optional[UUID] = None,
        status: Optional[ItemStatus] = None,
        priority: Optional[Priority] = None,
        category: Optional[ItemCategory] = None,
        limit: int = 100,
    ) -> List[BacklogItem]:
        """List backlog items with optional filters."""
        query = self.session.query(BacklogItem)

        if project_id:
            query = query.filter(BacklogItem.project_id == project_id)
        if status:
            query = query.filter(BacklogItem.status == status)
        if priority:
            query = query.filter(BacklogItem.priority == priority)
        if category:
            query = query.filter(BacklogItem.category == category)

        return query.order_by(desc(BacklogItem.created_at)).limit(limit).all()

    def update_backlog_item(self, item_id: UUID, **kwargs) -> Optional[BacklogItem]:
        """Update a backlog item."""
        item = self.get_backlog_item(item_id)
        if item:
            for key, value in kwargs.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            item.updated_at = datetime.utcnow()
            self.session.flush()
        return item

    def delete_backlog_item(self, item_id: UUID) -> bool:
        """Delete a backlog item."""
        item = self.get_backlog_item(item_id)
        if item:
            self.session.delete(item)
            return True
        return False

    def get_backlog_health_metrics(self, project_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Get backlog health metrics."""
        query = self.session.query(BacklogItem)
        if project_id:
            query = query.filter(BacklogItem.project_id == project_id)

        total_items = query.count()
        
        # Priority distribution
        priority_dist = (
            query.with_entities(BacklogItem.priority, func.count(BacklogItem.id))
            .group_by(BacklogItem.priority)
            .all()
        )
        
        # Status distribution
        status_dist = (
            query.with_entities(BacklogItem.status, func.count(BacklogItem.id))
            .group_by(BacklogItem.status)
            .all()
        )
        
        # Category distribution
        category_dist = (
            query.with_entities(BacklogItem.category, func.count(BacklogItem.id))
            .group_by(BacklogItem.category)
            .all()
        )

        return {
            "total_items": total_items,
            "priority_distribution": {str(p): c for p, c in priority_dist},
            "status_distribution": {str(s): c for s, c in status_dist},
            "category_distribution": {str(cat): c for cat, c in category_dist},
        }


class UserStoryRepository(BaseRepository):
    """Repository for user story operations."""

    def create_user_story(
        self,
        title: str,
        user_type: Optional[str] = None,
        functionality: Optional[str] = None,
        benefit: Optional[str] = None,
        project_id: Optional[UUID] = None,
        backlog_item_id: Optional[UUID] = None,
        **kwargs
    ) -> UserStory:
        """Create a new user story."""
        story = UserStory(
            title=title,
            user_type=user_type,
            functionality=functionality,
            benefit=benefit,
            project_id=project_id,
            backlog_item_id=backlog_item_id,
            **kwargs
        )
        self.session.add(story)
        self.session.flush()
        return story

    def get_user_story(self, story_id: UUID) -> Optional[UserStory]:
        """Get a user story by ID."""
        return self.session.query(UserStory).filter(UserStory.id == story_id).first()

    def list_user_stories(
        self,
        project_id: Optional[UUID] = None,
        backlog_item_id: Optional[UUID] = None,
        limit: int = 100,
    ) -> List[UserStory]:
        """List user stories with optional filters."""
        query = self.session.query(UserStory)

        if project_id:
            query = query.filter(UserStory.project_id == project_id)
        if backlog_item_id:
            query = query.filter(UserStory.backlog_item_id == backlog_item_id)

        return query.order_by(desc(UserStory.created_at)).limit(limit).all()

    def update_user_story(self, story_id: UUID, **kwargs) -> Optional[UserStory]:
        """Update a user story."""
        story = self.get_user_story(story_id)
        if story:
            for key, value in kwargs.items():
                if hasattr(story, key):
                    setattr(story, key, value)
            story.updated_at = datetime.utcnow()
            self.session.flush()
        return story

    def delete_user_story(self, story_id: UUID) -> bool:
        """Delete a user story."""
        story = self.get_user_story(story_id)
        if story:
            self.session.delete(story)
            return True
        return False


class PriorityAssessmentRepository(BaseRepository):
    """Repository for priority assessment operations."""

    def create_priority_assessment(
        self,
        backlog_item_id: UUID,
        priority: Priority,
        category: ItemCategory,
        business_impact: str,
        technical_complexity: str,
        reasoning: str,
        confidence_score: float,
        **kwargs
    ) -> PriorityAssessment:
        """Create a new priority assessment."""
        assessment = PriorityAssessment(
            backlog_item_id=backlog_item_id,
            priority=priority,
            category=category,
            business_impact=business_impact,
            technical_complexity=technical_complexity,
            reasoning=reasoning,
            confidence_score=confidence_score,
            **kwargs
        )
        self.session.add(assessment)
        self.session.flush()
        return assessment

    def get_latest_assessment(self, backlog_item_id: UUID) -> Optional[PriorityAssessment]:
        """Get the latest priority assessment for a backlog item."""
        return (
            self.session.query(PriorityAssessment)
            .filter(PriorityAssessment.backlog_item_id == backlog_item_id)
            .order_by(desc(PriorityAssessment.created_at))
            .first()
        )

    def list_assessments(
        self, backlog_item_id: Optional[UUID] = None, limit: int = 100
    ) -> List[PriorityAssessment]:
        """List priority assessments."""
        query = self.session.query(PriorityAssessment)

        if backlog_item_id:
            query = query.filter(PriorityAssessment.backlog_item_id == backlog_item_id)

        return query.order_by(desc(PriorityAssessment.created_at)).limit(limit).all()


class ProcessingJobRepository(BaseRepository):
    """Repository for processing job operations."""

    def create_processing_job(
        self,
        job_type: str,
        status: str = "pending",
        project_id: Optional[UUID] = None,
        **kwargs
    ) -> ProcessingJob:
        """Create a new processing job."""
        job = ProcessingJob(
            job_type=job_type,
            status=status,
            project_id=project_id,
            **kwargs
        )
        self.session.add(job)
        self.session.flush()
        return job

    def get_processing_job(self, job_id: UUID) -> Optional[ProcessingJob]:
        """Get a processing job by ID."""
        return self.session.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()

    def update_job_status(
        self, job_id: UUID, status: str, **kwargs
    ) -> Optional[ProcessingJob]:
        """Update processing job status."""
        job = self.get_processing_job(job_id)
        if job:
            job.status = status
            if status == "running" and not job.started_at:
                job.started_at = datetime.utcnow()
            elif status in ["completed", "failed"]:
                job.completed_at = datetime.utcnow()
            
            for key, value in kwargs.items():
                if hasattr(job, key):
                    setattr(job, key, value)
            
            self.session.flush()
        return job

    def list_processing_jobs(
        self,
        project_id: Optional[UUID] = None,
        job_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[ProcessingJob]:
        """List processing jobs with optional filters."""
        query = self.session.query(ProcessingJob)

        if project_id:
            query = query.filter(ProcessingJob.project_id == project_id)
        if job_type:
            query = query.filter(ProcessingJob.job_type == job_type)
        if status:
            query = query.filter(ProcessingJob.status == status)

        return query.order_by(desc(ProcessingJob.created_at)).limit(limit).all()


class CacheRepository(BaseRepository):
    """Repository for cache operations."""

    def set_cache(
        self,
        cache_key: str,
        cache_value: Any,
        expires_at: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        size_bytes: Optional[int] = None,
    ) -> CacheEntry:
        """Set a cache entry."""
        # Delete existing entry if it exists
        existing = (
            self.session.query(CacheEntry)
            .filter(CacheEntry.cache_key == cache_key)
            .first()
        )
        if existing:
            self.session.delete(existing)
            self.session.flush()

        entry = CacheEntry(
            cache_key=cache_key,
            cache_value=cache_value,
            expires_at=expires_at,
            tags=tags or [],
            size_bytes=size_bytes or 0,
        )
        self.session.add(entry)
        self.session.flush()
        return entry

    def get_cache(self, cache_key: str) -> Optional[CacheEntry]:
        """Get a cache entry by key."""
        entry = (
            self.session.query(CacheEntry)
            .filter(CacheEntry.cache_key == cache_key)
            .first()
        )

        if entry:
            # Check if expired
            if entry.expires_at and entry.expires_at < datetime.utcnow():
                self.session.delete(entry)
                self.session.flush()
                return None

            # Update access statistics
            entry.access_count += 1
            entry.hit_count += 1
            entry.last_accessed = datetime.utcnow()
            self.session.flush()

        return entry

    def delete_cache(self, cache_key: str) -> bool:
        """Delete a cache entry."""
        entry = (
            self.session.query(CacheEntry)
            .filter(CacheEntry.cache_key == cache_key)
            .first()
        )
        if entry:
            self.session.delete(entry)
            return True
        return False

    def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate cache entries by tags."""
        count = 0
        for tag in tags:
            # For SQLite, we need to use a different approach for JSON array contains
            entries = self.session.query(CacheEntry).all()
            for entry in entries:
                if entry.tags and tag in entry.tags:
                    self.session.delete(entry)
                    count += 1
        self.session.flush()
        return count

    def cleanup_expired(self) -> int:
        """Clean up expired cache entries."""
        expired_entries = (
            self.session.query(CacheEntry)
            .filter(CacheEntry.expires_at < datetime.utcnow())
            .all()
        )
        count = len(expired_entries)
        for entry in expired_entries:
            self.session.delete(entry)
        self.session.flush()
        return count

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_entries = self.session.query(CacheEntry).count()
        total_size = (
            self.session.query(func.sum(CacheEntry.size_bytes)).scalar() or 0
        )
        total_hits = (
            self.session.query(func.sum(CacheEntry.hit_count)).scalar() or 0
        )
        total_accesses = (
            self.session.query(func.sum(CacheEntry.access_count)).scalar() or 0
        )

        hit_rate = (total_hits / total_accesses * 100) if total_accesses > 0 else 0

        return {
            "total_entries": total_entries,
            "total_size_bytes": total_size,
            "total_hits": total_hits,
            "total_accesses": total_accesses,
            "hit_rate_percent": round(hit_rate, 2),
        }


class RepositoryManager:
    """Manager for all repositories with database session handling."""

    def __init__(self, session: Optional[Session] = None):
        self.session = session
        self._own_session = session is None

        if self._own_session:
            from src.database.models import db_manager
            self.session = db_manager.get_session()

        # Initialize repositories
        self.projects = ProjectRepository(self.session)
        self.backlog_items = BacklogItemRepository(self.session)
        self.user_stories = UserStoryRepository(self.session)
        self.priority_assessments = PriorityAssessmentRepository(self.session)
        self.processing_jobs = ProcessingJobRepository(self.session)
        self.cache = CacheRepository(self.session)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()

        if self._own_session:
            self.session.close()

    def commit(self):
        """Commit all changes."""
        self.session.commit()

    def rollback(self):
        """Rollback all changes."""
        self.session.rollback()


# Convenience function for getting repository manager
def get_repository_manager() -> RepositoryManager:
    """Get a repository manager instance."""
    return RepositoryManager()
