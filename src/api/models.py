"""Pydantic models for FastAPI endpoints."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ProcessMeetingNotesRequest(BaseModel):
    """Request model for processing meeting notes."""
    filename: str = Field(..., description="Name of the uploaded file")
    extract_user_stories: bool = Field(default=True, description="Whether to extract user stories")
    priority_analysis: bool = Field(default=True, description="Whether to perform priority analysis")


class ProcessMeetingNotesResponse(BaseModel):
    """Response model for meeting notes processing."""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Processing status")
    message: str = Field(..., description="Status message")
    filename: str = Field(..., description="Original filename")


class BacklogItem(BaseModel):
    """Model for a backlog item."""
    title: str = Field(..., description="Item title")
    description: str = Field(..., description="Item description")
    priority: Optional[str] = Field(None, description="Priority level")
    status: Optional[str] = Field(None, description="Current status")
    tags: List[str] = Field(default_factory=list, description="Item tags")
    estimated_effort: Optional[str] = Field(None, description="Effort estimate")


class AnalyzeBacklogRequest(BaseModel):
    """Request model for backlog analysis."""
    backlog_items: List[BacklogItem] = Field(..., description="List of backlog items to analyze")
    analysis_type: str = Field(default="comprehensive", description="Type of analysis to perform")
    include_recommendations: bool = Field(default=True, description="Include improvement recommendations")


class AnalyzeBacklogResponse(BaseModel):
    """Response model for backlog analysis."""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Processing status")
    message: str = Field(..., description="Status message")
    item_count: int = Field(..., description="Number of items being analyzed")


class JobStatus(BaseModel):
    """Model for job status information."""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status (pending, processing, completed, failed)")
    created_at: datetime = Field(..., description="Job creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    progress: int = Field(default=0, description="Progress percentage (0-100)")
    message: str = Field(default="", description="Status message")


class JobResult(BaseModel):
    """Model for job result data."""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status")
    result: Dict[str, Any] = Field(..., description="Job result data")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    processing_time: float = Field(default=0.0, description="Processing time in seconds")


class SystemStatus(BaseModel):
    """Model for system status information."""
    status: str = Field(..., description="Overall system status")
    timestamp: datetime = Field(..., description="Status check timestamp")
    version: str = Field(..., description="API version")
    processing_mode: str = Field(..., description="Processing mode (async/sync)")
    caching_enabled: bool = Field(..., description="Whether caching is enabled")
    active_jobs: int = Field(..., description="Number of active jobs")
    completed_jobs: int = Field(..., description="Number of completed jobs")
    failed_jobs: int = Field(..., description="Number of failed jobs")


class HealthCheck(BaseModel):
    """Model for basic health check."""
    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(..., description="Check timestamp")
    version: str = Field(..., description="API version")


class UserStory(BaseModel):
    """Model for a user story."""
    title: str = Field(..., description="Story title")
    user_type: str = Field(..., description="Type of user")
    functionality: str = Field(..., description="Desired functionality")
    benefit: str = Field(..., description="Expected benefit")
    acceptance_criteria: List[str] = Field(default_factory=list, description="Acceptance criteria")
    priority: Optional[str] = Field(None, description="Story priority")
    estimated_effort: Optional[str] = Field(None, description="Effort estimate")
    tags: List[str] = Field(default_factory=list, description="Story tags")


class MeetingNotesResult(BaseModel):
    """Model for meeting notes processing result."""
    source_file: str = Field(..., description="Source file path")
    processing_timestamp: datetime = Field(..., description="Processing timestamp")
    extracted_requirements: str = Field(..., description="Extracted requirements text")
    user_stories: List[UserStory] = Field(default_factory=list, description="Generated user stories")
    ai_service_used: str = Field(..., description="AI service used for processing")
    processing_time: float = Field(..., description="Processing time in seconds")


class BacklogAnalysisResult(BaseModel):
    """Model for backlog analysis result."""
    total_items: int = Field(..., description="Total number of items analyzed")
    health_score: float = Field(..., description="Overall backlog health score")
    items_by_priority: Dict[str, int] = Field(..., description="Items grouped by priority")
    items_by_status: Dict[str, int] = Field(..., description="Items grouped by status")
    missing_information: List[str] = Field(..., description="Types of missing information")
    recommendations: List[str] = Field(..., description="Improvement recommendations")
    ai_insights: str = Field(..., description="AI-generated insights")
    processing_time: float = Field(..., description="Processing time in seconds")


class ErrorResponse(BaseModel):
    """Model for error responses."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class AuthToken(BaseModel):
    """Model for authentication token."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class UserInfo(BaseModel):
    """Model for user information."""
    user_id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Username")
    email: Optional[str] = Field(None, description="User email")
    roles: List[str] = Field(default_factory=list, description="User roles")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
