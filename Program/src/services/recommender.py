import asyncio
from typing import List, Dict, Optional
import google.generativeai as genai
from googleapiclient.discovery import build
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import Note
from src.utils.logger import setup_logger
from src.utils.config import settings

logger = setup_logger(__name__)


class RecommendationService:
    """
    Service for suggesting videos and categories based on user's saved notes.
    Uses keyword overlap and YouTube Search API for new recommendations.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.google_api_key
        genai.configure(api_key=self.api_key)
        self.youtube = build("youtube", "v3", developerKey=self.api_key)

    async def get_recommendations_for_user(
        self, session: AsyncSession, user_id: int, limit: int = 5
    ) -> List[Dict]:
        """
        Get general recommendations (Categories & YouTube Videos) for a user based on their history.
        """
        # 1. Fetch user's saved notes
        statement = (
            select(Note).where(Note.user_id == user_id).order_by(Note.created_at.desc())
        )
        result = await session.exec(statement)
        notes = result.all()

        if not notes:
            return await self.get_youtube_recommendations(
                "educational tutorials", limit
            )

        # 2. Extract topics from categories of recent notes
        topics = [
            n.category
            for n in notes[:5]
            if n.category and n.category != "Uncategorized"
        ]

        # If no categories, use titles
        if not topics:
            topics = [n.video_title for n in notes[:3]]

        search_query = " ".join(topics[:3])

        # 3. Get YouTube recommendations
        youtube_recs = await self.get_youtube_recommendations(search_query, limit)

        return youtube_recs

    async def get_youtube_recommendations(
        self, query: str, limit: int = 5
    ) -> List[Dict]:
        """
        Search YouTube for new videos based on a query.
        """
        try:
            # Run in thread pool since google-api-python-client is synchronous
            loop = asyncio.get_event_loop()
            search_response = await loop.run_in_executor(
                None,
                lambda: self.youtube.search()
                .list(
                    q=query,
                    part="snippet",
                    maxResults=limit,
                    type="video",
                    relevanceLanguage="en",
                )
                .execute(),
            )

            videos = []
            for item in search_response.get("items", []):
                videos.append(
                    {
                        "id": item["id"]["videoId"],
                        "title": item["snippet"]["title"],
                        "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                        "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                        "type": "youtube_video",
                    }
                )
            return videos
        except Exception as e:
            logger.error(f"YouTube search failed: {e}")
            return []

    async def get_similar_notes(
        self, session: AsyncSession, note_id: int, limit: int = 3
    ) -> List[Note]:
        """
        Find notes similar to a specific note based on category.
        """
        # Fetch the target note
        target_note = await session.get(Note, note_id)
        if not target_note:
            return []

        # Fetch other notes in the same category
        statement = (
            select(Note)
            .where(
                Note.id != note_id,
                Note.category == target_note.category,
                Note.user_id == target_note.user_id,
            )
            .limit(limit)
        )

        result = await session.exec(statement)
        return result.all()
