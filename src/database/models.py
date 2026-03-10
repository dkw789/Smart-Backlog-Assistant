"""Database models for Smart Backlog Assistant."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    create_engine,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func

from src.config import config

Base = declarative_base()


class GUID(TypeDecorator):
    """Cross-database UUID type that works with SQLite and PostgreSQL."""
    
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            return value


class Priority(str, Enum):
    """Priority levels for backlog items."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ItemStatus(str, Enum):
    """Status values for backlog items."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


class ItemCategory(str, Enum):
    """Categories for backlog items."""
    FEATURE = "feature"
    BUG = "bug"
    ENHANCEMENT = "enhancement"
    TECHNICAL_DEBT = "technical_debt"
    RESEARCH = "research"
    MAINTENANCE = "maintenance"


class Project(Base):
    """Project model."""
    __tablename__ = "projects"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    backlog_items = relationship("BacklogItem", back_populates="project")
    user_stories = relationship("UserStory", back_populates="project")


class BacklogItem(Base):
    """Backlog item model."""
    __tablename__ = "backlog_items"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    priority = Column(SQLEnum(Priority), default=Priority.MEDIUM)
    status = Column(SQLEnum(ItemStatus), default=ItemStatus.TODO)
    category = Column(SQLEnum(ItemCategory), default=ItemCategory.FEATURE)
    story_points = Column(Integer)
    business_value = Column(Integer)
    technical_complexity = Column(Integer)
    
    # Metadata
    tags = Column(JSON)  # List of strings
    extra_data = Column(JSON)  # Additional flexible data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign keys
    project_id = Column(GUID(), ForeignKey("projects.id"))
    
    # Relationships
    project = relationship("Project", back_populates="backlog_items")
    user_stories = relationship("UserStory", back_populates="backlog_item")
    priority_assessments = relationship("PriorityAssessment", back_populates="backlog_item")


class UserStory(Base):
    """User story model."""
    __tablename__ = "user_stories"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    user_type = Column(String(100))
    functionality = Column(Text)
    benefit = Column(Text)
    acceptance_criteria = Column(JSON)  # List of criteria
    priority = Column(SQLEnum(Priority), default=Priority.MEDIUM)
    estimated_effort = Column(String(50))
    tags = Column(JSON)  # List of strings
    
    # Source information
    original_requirement = Column(Text)
    generated_by_ai = Column(Boolean, default=False)
    ai_service_used = Column(String(50))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign keys
    project_id = Column(GUID(), ForeignKey("projects.id"))
    backlog_item_id = Column(GUID(), ForeignKey("backlog_items.id"), nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="user_stories")
    backlog_item = relationship("BacklogItem", back_populates="user_stories")


class PriorityAssessment(Base):
    """Priority assessment model."""
    __tablename__ = "priority_assessments"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    priority = Column(SQLEnum(Priority), nullable=False)
    category = Column(SQLEnum(ItemCategory), nullable=False)
    business_impact = Column(String(20))  # High/Medium/Low
    technical_complexity = Column(String(20))  # High/Medium/Low
    effort_estimate = Column(String(50))
    dependencies = Column(JSON)  # List of dependencies
    reasoning = Column(Text)
    confidence_score = Column(Float)
    
    # AI processing metadata
    generated_by_ai = Column(Boolean, default=False)
    ai_service_used = Column(String(50))
    processing_time = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign keys
    backlog_item_id = Column(GUID(), ForeignKey("backlog_items.id"))
    
    # Relationships
    backlog_item = relationship("BacklogItem", back_populates="priority_assessments")


class ProcessingJob(Base):
    """Processing job tracking model."""
    __tablename__ = "processing_jobs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    job_type = Column(String(100), nullable=False)  # meeting_notes, backlog_analysis, etc.
    status = Column(String(20), nullable=False)  # pending, running, completed, failed
    input_file_path = Column(String(1000))
    output_file_path = Column(String(1000))
    
    # Processing metadata
    processing_mode = Column(String(20))  # sync, async
    ai_service_used = Column(String(50))
    processing_time = Column(Float)
    error_message = Column(Text)
    
    # Results
    results = Column(JSON)  # Flexible results storage
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Foreign keys
    project_id = Column(GUID(), ForeignKey("projects.id"), nullable=True)
    
    # Relationships
    project = relationship("Project")


class CacheEntry(Base):
    """Cache entry model for persistent caching."""
    __tablename__ = "cache_entries"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    cache_key = Column(String(500), nullable=False, unique=True)
    cache_value = Column(JSON, nullable=False)
    tags = Column(JSON)  # List of tags for cache invalidation
    
    # Cache metadata
    size_bytes = Column(Integer)
    access_count = Column(Integer, default=0)
    hit_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))


# Database configuration and session management
class DatabaseManager:
    """Database manager for handling connections and sessions."""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or self._get_database_url()
        self.engine = create_engine(
            self.database_url,
            echo=config.debug_mode,
            pool_pre_ping=True,
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def _get_database_url(self) -> str:
        """Get database URL from config or default to SQLite."""
        # Check for PostgreSQL config first
        if hasattr(config, 'database_url') and config.database_url:
            return config.database_url
        
        # Default to SQLite for development
        return "sqlite:///./smart_backlog_assistant.db"
    
    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get a database session."""
        return self.SessionLocal()
    
    def drop_tables(self):
        """Drop all database tables (use with caution)."""
        Base.metadata.drop_all(bind=self.engine)


# Global database manager instance
db_manager = DatabaseManager()


def get_db():
    """Dependency to get database session."""
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()
