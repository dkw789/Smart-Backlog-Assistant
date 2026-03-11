#!/usr/bin/env python3
"""Simple API server for testing Smart Backlog Assistant endpoints."""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.environ['PYTHONPATH'] = str(project_root)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn

app = FastAPI(
    title="Smart Backlog Assistant API",
    description="AI-powered backlog management and analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class MeetingNotesRequest(BaseModel):
    content: str
    output_format: str = "json"

class BacklogAnalysisRequest(BaseModel):
    items: List[Dict[str, Any]]

class APIResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str = ""

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Smart Backlog Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Smart Backlog Assistant API",
        "timestamp": "2024-03-11T12:00:00Z"
    }

@app.post("/api/v1/meeting-notes", response_model=APIResponse)
async def process_meeting_notes(request: MeetingNotesRequest):
    """Process meeting notes and extract requirements."""
    try:
        # Mock response for testing
        mock_result = {
            "requirements": [
                "User authentication system",
                "Data validation framework",
                "Session management"
            ],
            "user_stories": [
                "As a user, I want to login securely so that I can access my account",
                "As a user, I want my data to be validated so that errors are prevented"
            ],
            "processing_time": 2.5,
            "service_used": "mock"
        }
        
        return APIResponse(
            success=True,
            data=mock_result,
            message="Meeting notes processed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/analyze-backlog", response_model=APIResponse)
async def analyze_backlog(request: BacklogAnalysisRequest):
    """Analyze backlog items and provide insights."""
    try:
        # Mock response for testing
        mock_result = {
            "health_score": 85,
            "total_items": len(request.items),
            "priority_distribution": {
                "high": 3,
                "medium": 5,
                "low": 2
            },
            "recommendations": [
                "Consider breaking down large items",
                "Add more acceptance criteria",
                "Balance priority distribution"
            ],
            "processing_time": 1.8,
            "service_used": "mock"
        }
        
        return APIResponse(
            success=True,
            data=mock_result,
            message="Backlog analysis completed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/sprint-plan")
async def generate_sprint_plan(capacity: int = 40):
    """Generate sprint plan based on capacity."""
    try:
        mock_result = {
            "sprint_capacity": capacity,
            "selected_items": [
                {"title": "User Authentication", "story_points": 8},
                {"title": "Data Validation", "story_points": 5},
                {"title": "UI Components", "story_points": 13}
            ],
            "total_story_points": 26,
            "remaining_capacity": 14,
            "recommendations": [
                "Sprint is well-balanced",
                "Consider adding smaller items to fill remaining capacity"
            ]
        }
        
        return APIResponse(
            success=True,
            data=mock_result,
            message="Sprint plan generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting Smart Backlog Assistant API...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Alternative Docs: http://localhost:8000/redoc")
    print("❤️  Health Check: http://localhost:8000/health")
    print("")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
