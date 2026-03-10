"""Background job management for FastAPI endpoints."""

import asyncio
import os
import tempfile
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

from src.utils.logger_service import get_logger

logger = get_logger(__name__)


class JobManager:
    """Manages background jobs for API processing."""
    
    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.completed_count = 0
        self.failed_count = 0
        self.max_jobs = 1000  # Prevent memory issues
    
    def create_job(self, job_id: str, job_type: str, user: str) -> Dict[str, Any]:
        """Create a new job entry."""
        job = {
            "id": job_id,
            "type": job_type,
            "user": user,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "progress": 0,
            "message": "Job created",
            "result": None,
            "error": None
        }
        
        # Clean up old jobs if needed
        if len(self.jobs) >= self.max_jobs:
            self._cleanup_old_jobs()
        
        self.jobs[job_id] = job
        logger.info(f"Created job {job_id} of type {job_type} for user {user}")
        return job
    
    def update_job(self, job_id: str, **updates) -> Optional[Dict[str, Any]]:
        """Update job with new information."""
        if job_id not in self.jobs:
            return None
        
        job = self.jobs[job_id]
        job.update(updates)
        job["updated_at"] = datetime.utcnow()
        
        logger.debug(f"Updated job {job_id}: {updates}")
        return job
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID."""
        return self.jobs.get(job_id)
    
    def get_user_jobs(self, user: str, limit: int = 50, status: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """Get jobs for a specific user."""
        user_jobs = {
            job_id: job for job_id, job in self.jobs.items() 
            if job["user"] == user and (status is None or job["status"] == status)
        }
        
        # Sort by creation time (newest first) and limit
        sorted_jobs = dict(sorted(
            user_jobs.items(), 
            key=lambda x: x[1]["created_at"], 
            reverse=True
        )[:limit])
        
        return sorted_jobs
    
    def _cleanup_old_jobs(self):
        """Remove old completed/failed jobs to prevent memory issues."""
        # Keep only the 100 most recent jobs
        sorted_jobs = sorted(
            self.jobs.items(),
            key=lambda x: x[1]["created_at"],
            reverse=True
        )
        
        # Keep the 100 most recent
        self.jobs = dict(sorted_jobs[:100])
        logger.info("Cleaned up old jobs")
    
    async def process_meeting_notes_job(
        self, 
        job_id: str, 
        file_path: str, 
        assistant, 
        user: str
    ):
        """Process meeting notes in background."""
        try:
            # Create job entry
            self.create_job(job_id, "meeting_notes", user)
            
            # Update status
            self.update_job(job_id, status="processing", message="Processing meeting notes", progress=10)
            
            # Process the file
            start_time = time.time()
            result = await assistant.process_meeting_notes_async(file_path)
            processing_time = time.time() - start_time
            
            # Update with result
            self.update_job(
                job_id,
                status="completed",
                message="Meeting notes processed successfully",
                progress=100,
                result=result,
                completed_at=datetime.utcnow(),
                processing_time=processing_time
            )
            
            self.completed_count += 1
            logger.info(f"Completed meeting notes job {job_id} in {processing_time:.2f}s")
            
        except Exception as e:
            # Update with error
            self.update_job(
                job_id,
                status="failed",
                message=f"Processing failed: {str(e)}",
                progress=0,
                error=str(e),
                completed_at=datetime.utcnow()
            )
            
            self.failed_count += 1
            logger.error(f"Meeting notes job {job_id} failed: {e}")
            
        finally:
            # Clean up temporary file
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temp file {file_path}: {e}")
    
    async def analyze_backlog_job(
        self,
        job_id: str,
        backlog_items: List[Dict[str, Any]],
        assistant,
        user: str
    ):
        """Analyze backlog in background."""
        try:
            # Create job entry
            self.create_job(job_id, "backlog_analysis", user)
            
            # Update status
            self.update_job(
                job_id, 
                status="processing", 
                message=f"Analyzing {len(backlog_items)} backlog items", 
                progress=10
            )
            
            # Convert backlog items to the format expected by the analyzer
            items_data = []
            for item in backlog_items:
                item_dict = {
                    "title": item.get("title", ""),
                    "description": item.get("description", ""),
                    "priority": item.get("priority"),
                    "status": item.get("status"),
                    "tags": item.get("tags", []),
                    "estimated_effort": item.get("estimated_effort")
                }
                items_data.append(item_dict)
            
            # Create temporary file for backlog data
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
                import json
                json.dump({"items": items_data}, tmp_file)
                temp_file_path = tmp_file.name
            
            try:
                # Process the backlog
                start_time = time.time()
                result = await assistant.analyze_backlog_async(temp_file_path)
                processing_time = time.time() - start_time
                
                # Update with result
                self.update_job(
                    job_id,
                    status="completed",
                    message="Backlog analysis completed successfully",
                    progress=100,
                    result=result,
                    completed_at=datetime.utcnow(),
                    processing_time=processing_time
                )
                
                self.completed_count += 1
                logger.info(f"Completed backlog analysis job {job_id} in {processing_time:.2f}s")
                
            finally:
                # Clean up temporary file
                try:
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                except Exception as e:
                    logger.warning(f"Failed to clean up temp file {temp_file_path}: {e}")
            
        except Exception as e:
            # Update with error
            self.update_job(
                job_id,
                status="failed",
                message=f"Analysis failed: {str(e)}",
                progress=0,
                error=str(e),
                completed_at=datetime.utcnow()
            )
            
            self.failed_count += 1
            logger.error(f"Backlog analysis job {job_id} failed: {e}")
    
    async def cleanup(self):
        """Cleanup resources when shutting down."""
        logger.info("Cleaning up job manager resources")
        # Cancel any running background tasks if needed
        # Clean up temporary files
        self.jobs.clear()
