"""FastAPI web API for Smart Backlog Assistant.

This module provides REST API endpoints for the Smart Backlog Assistant:
- Authentication and authorization
- Job management and status tracking
- Meeting notes processing
- Backlog analysis and management
- User story generation
- System health and monitoring
"""

__all__ = [
    "authenticate_user",
    "create_access_token", 
    "get_current_user",
    "verify_token",
    "JobManager",
    "create_job",
    "get_job_status",
    "update_job_status",
]
