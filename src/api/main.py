"""FastAPI main application for Smart Backlog Assistant."""

import asyncio
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.main_unified import UnifiedSmartBacklogAssistant
from src.config import config
from src.utils.logger_service import get_logger
from src.api.models import (
    ProcessMeetingNotesRequest,
    ProcessMeetingNotesResponse,
    AnalyzeBacklogRequest,
    AnalyzeBacklogResponse,
    JobStatus,
    JobResult,
    SystemStatus,
    HealthCheck
)
from src.api.auth import verify_token, get_current_user
from src.api.jobs import JobManager


# Global job manager
job_manager = JobManager()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Security
security = HTTPBearer()

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Smart Backlog Assistant API")
    
    # Initialize services
    try:
        # Test database connection if configured
        logger.info("API startup completed successfully")
        yield
    except Exception as e:
        logger.error(f"Failed to start API: {e}")
        raise
    finally:
        logger.info("Shutting down Smart Backlog Assistant API")
        # Cleanup resources
        await job_manager.cleanup()


# FastAPI app
app = FastAPI(
    title="Smart Backlog Assistant API",
    description="AI-powered backlog management and analysis API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Dependency injection
async def get_assistant() -> UnifiedSmartBacklogAssistant:
    """Get configured UnifiedSmartBacklogAssistant instance."""
    return UnifiedSmartBacklogAssistant(
        use_async=True,
        enable_caching=True,
        use_rich_cli=False  # Disable CLI for API usage
    )


# Health check endpoints
@app.get("/health", response_model=HealthCheck, tags=["System"])
async def health_check():
    """Basic health check for load balancers."""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )


@app.get("/health/detailed", response_model=Dict[str, Any], tags=["System"])
async def detailed_health_check():
    """Detailed health check for monitoring systems."""
    try:
        # Test AI services
        assistant = await get_assistant()
        
        # Test basic functionality
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "version": "1.0.0",
            "services": {
                "ai_services": "healthy",
                "caching": "healthy" if assistant.enable_caching else "disabled",
                "database": "not_configured"  # Update when database is added
            },
            "system": {
                "python_version": "3.12",
                "async_mode": assistant.use_async,
                "cache_enabled": assistant.enable_caching
            }
        }
        
        return health_data
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.get("/api/v1/system/status", response_model=SystemStatus, tags=["System"])
@limiter.limit("10/minute")
async def get_system_status(request, current_user: str = Depends(get_current_user)):
    """Get comprehensive system status."""
    try:
        assistant = await get_assistant()
        
        return SystemStatus(
            status="operational",
            timestamp=datetime.utcnow(),
            version="1.0.0",
            processing_mode="async" if assistant.use_async else "sync",
            caching_enabled=assistant.enable_caching,
            active_jobs=len(job_manager.jobs),
            completed_jobs=job_manager.completed_count,
            failed_jobs=job_manager.failed_count
        )
        
    except Exception as e:
        logger.error(f"System status check failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system status")


# Core processing endpoints
@app.post("/api/v1/meeting-notes/process", response_model=ProcessMeetingNotesResponse, tags=["Processing"])
@limiter.limit("5/minute")
async def process_meeting_notes(
    request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
    assistant: UnifiedSmartBacklogAssistant = Depends(get_assistant)
):
    """Process meeting notes file and extract requirements."""
    try:
        # Validate file type
        allowed_types = [".txt", ".md", ".pdf", ".docx"]
        if not any(file.filename.endswith(ext) for ext in allowed_types):
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {allowed_types}"
            )
        
        # Create job
        job_id = str(uuid.uuid4())
        
        # Save uploaded file temporarily
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            temp_file_path = tmp_file.name
        
        # Start background processing
        background_tasks.add_task(
            job_manager.process_meeting_notes_job,
            job_id,
            temp_file_path,
            assistant,
            current_user
        )
        
        return ProcessMeetingNotesResponse(
            job_id=job_id,
            status="processing",
            message="Meeting notes processing started",
            filename=file.filename
        )
        
    except Exception as e:
        logger.error(f"Meeting notes processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/backlog/analyze", response_model=AnalyzeBacklogResponse, tags=["Processing"])
@limiter.limit("5/minute")
async def analyze_backlog(
    request,
    background_tasks: BackgroundTasks,
    request_data: AnalyzeBacklogRequest,
    current_user: str = Depends(get_current_user),
    assistant: UnifiedSmartBacklogAssistant = Depends(get_assistant)
):
    """Analyze backlog health and provide recommendations."""
    try:
        # Create job
        job_id = str(uuid.uuid4())
        
        # Start background processing
        background_tasks.add_task(
            job_manager.analyze_backlog_job,
            job_id,
            request_data.backlog_items,
            assistant,
            current_user
        )
        
        return AnalyzeBacklogResponse(
            job_id=job_id,
            status="processing",
            message="Backlog analysis started",
            item_count=len(request_data.backlog_items)
        )
        
    except Exception as e:
        logger.error(f"Backlog analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Job management endpoints
@app.get("/api/v1/jobs/{job_id}/status", response_model=JobStatus, tags=["Jobs"])
@limiter.limit("30/minute")
async def get_job_status(
    request,
    job_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get job processing status."""
    try:
        job = job_manager.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Check user access
        if job.get("user") != current_user:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return JobStatus(
            job_id=job_id,
            status=job["status"],
            created_at=job["created_at"],
            updated_at=job.get("updated_at", job["created_at"]),
            progress=job.get("progress", 0),
            message=job.get("message", "")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Job status check failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get job status")


@app.get("/api/v1/jobs/{job_id}/result", response_model=JobResult, tags=["Jobs"])
@limiter.limit("30/minute")
async def get_job_result(
    request,
    job_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get job result when completed."""
    try:
        job = job_manager.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Check user access
        if job.get("user") != current_user:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if job["status"] != "completed":
            raise HTTPException(
                status_code=400, 
                detail=f"Job not completed. Current status: {job['status']}"
            )
        
        return JobResult(
            job_id=job_id,
            status=job["status"],
            result=job.get("result", {}),
            completed_at=job.get("completed_at"),
            processing_time=job.get("processing_time", 0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Job result retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get job result")


@app.get("/api/v1/jobs", response_model=List[JobStatus], tags=["Jobs"])
@limiter.limit("10/minute")
async def list_user_jobs(
    request,
    current_user: str = Depends(get_current_user),
    limit: int = 50,
    status: Optional[str] = None
):
    """List user's jobs with optional status filter."""
    try:
        jobs = job_manager.get_user_jobs(current_user, limit=limit, status=status)
        
        return [
            JobStatus(
                job_id=job_id,
                status=job["status"],
                created_at=job["created_at"],
                updated_at=job.get("updated_at", job["created_at"]),
                progress=job.get("progress", 0),
                message=job.get("message", "")
            )
            for job_id, job in jobs.items()
        ]
        
    except Exception as e:
        logger.error(f"Job listing failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to list jobs")


def main():
    """Run the FastAPI application."""
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
