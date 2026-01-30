from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.database import get_session
from src.db.models import User
from src.auth.dependencies import get_current_user
from src.services.recommender import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])
recommender = RecommendationService()

@router.get("", response_model=List[Dict])
async def get_general_recommendations(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get general recommendations for the user based on their note history.
    """
    return await recommender.get_recommendations_for_user(session, current_user.id)

@router.get("/{note_id}", response_model=List[Dict])
async def get_note_recommendations(
    note_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get recommendations similar to a specific note.
    """
    similar_notes = await recommender.get_similar_notes(session, note_id)
    return [{"id": n.id, "title": n.video_title, "type": "note"} for n in similar_notes]
