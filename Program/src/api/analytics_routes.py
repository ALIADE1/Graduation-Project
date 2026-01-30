"""
Analytics API endpoints for user statistics.
"""

from typing import Dict, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlmodel import Session, select, func
from datetime import datetime

from src.db.database import get_session
from src.db.models import User, Note
from src.auth.dependencies import get_current_user
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# Response Models
class AnalyticsResponse(BaseModel):
    """Response model for user analytics."""
    total_videos_processed: int = Field(..., description="Total number of videos processed")
    total_study_time_seconds: int = Field(..., description="Total study time in seconds")
    total_study_time_formatted: str = Field(..., description="Total study time formatted (HH:MM:SS)")
    total_notes: int = Field(..., description="Total number of notes generated")
    average_video_duration: float = Field(..., description="Average video duration in seconds")
    languages_used: List[str] = Field(..., description="List of languages used")
    recent_activity: List[Dict] = Field(..., description="Recent notes (last 5)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_videos_processed": 15,
                "total_study_time_seconds": 18000,
                "total_study_time_formatted": "5:00:00",
                "total_notes": 15,
                "average_video_duration": 1200.0,
                "languages_used": ["en", "es"],
                "recent_activity": [
                    {
                        "video_title": "Python Basics",
                        "created_at": "2024-01-27T05:00:00",
                        "duration": 1800
                    }
                ]
            }
        }


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to HH:MM:SS format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds is None or seconds == 0:
        return "0:00:00"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    return f"{hours}:{minutes:02d}:{secs:02d}"


@router.get("", response_model=AnalyticsResponse)
async def get_analytics(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get user statistics and analytics.
    
    **Protected Route**: Requires authentication
    
    Returns comprehensive statistics including:
    - Total videos processed
    - Total study time (sum of video durations)
    - Average video duration
    - Languages used
    - Recent activity
    """
    # Get all notes for the user
    statement = select(Note).where(Note.user_id == current_user.id)
    notes = session.exec(statement).all()
    
    total_notes = len(notes)
    
    # Calculate total study time (sum of video durations)
    total_study_time = 0
    durations = []
    for note in notes:
        if note.video_duration:
            total_study_time += note.video_duration
            durations.append(note.video_duration)
    
    # Calculate average duration
    average_duration = sum(durations) / len(durations) if durations else 0
    
    # Get unique languages
    languages = list(set(note.language for note in notes if note.language))
    
    # Get recent activity (last 5 notes)
    recent_statement = (
        select(Note)
        .where(Note.user_id == current_user.id)
        .order_by(Note.created_at.desc())
        .limit(5)
    )
    recent_notes = session.exec(recent_statement).all()
    
    recent_activity = [
        {
            "video_title": note.video_title,
            "video_url": note.video_url,
            "created_at": str(note.created_at),
            "duration": note.video_duration,
            "duration_formatted": format_duration(note.video_duration) if note.video_duration else "N/A"
        }
        for note in recent_notes
    ]
    
    logger.info(f"Analytics retrieved for user {current_user.email}")
    
    return AnalyticsResponse(
        total_videos_processed=total_notes,
        total_study_time_seconds=total_study_time,
        total_study_time_formatted=format_duration(total_study_time),
        total_notes=total_notes,
        average_video_duration=round(average_duration, 2),
        languages_used=languages,
        recent_activity=recent_activity
    )
