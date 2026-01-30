"""
Notes management API endpoints.
"""

from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Optional
from pathlib import Path
import os

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, HttpUrl, Field
from sqlmodel import Session, select

from src.db.database import get_session
from src.db.models import User, Note
from src.auth.dependencies import get_current_user
from src.services.categorizer import CategorizationService
from src.utils.logger import setup_logger
from src.utils.config import settings

logger = setup_logger(__name__)
categorizer = CategorizationService()

router = APIRouter(prefix="/notes", tags=["Notes"])


# --- New Models for File-based Notes ---
class GeneratedNoteFile(BaseModel):
    filename: str
    title: str
    created_at: float
    size: int


# --- Existing Models ---
class CreateNoteRequest(BaseModel):
    video_url: HttpUrl = Field(..., description="YouTube video URL")
    video_title: str = Field(..., max_length=500, description="Video title")
    summary_text: str = Field(..., description="Generated study notes in markdown")
    video_duration: Optional[int] = Field(None, description="Video duration in seconds")
    language: str = Field(
        default="en", max_length=10, description="Video language code"
    )


class NoteResponse(BaseModel):
    id: int
    video_url: str
    video_title: str
    summary_text: str
    video_duration: Optional[int]
    language: str
    user_id: int
    category: Optional[str]
    created_at: str


# ==========================================
# ✅ NEW ENDPOINTS: Read from 'outputs' folder
# ==========================================


@router.get("/generated", response_model=List[GeneratedNoteFile])
async def list_generated_notes():
    """
    List all markdown files found in the 'outputs' directory.
    This bypasses the database to show files directly.
    """
    notes = []
    output_dir = settings.output_dir

    # Create directory if it doesn't exist
    if not output_dir.exists():
        return []

    # Scan for .md files
    # We look for files ending with _notes.md
    for file_path in output_dir.glob("*_notes.md"):
        try:
            # Try to read the first line to get a clean title
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")
            # Usually the first line is "# Title"
            title = lines[0].replace("#", "").strip() if lines else file_path.name

            stats = file_path.stat()

            notes.append(
                GeneratedNoteFile(
                    filename=file_path.name,
                    title=title if title else file_path.name,
                    created_at=stats.st_mtime,
                    size=stats.st_size,
                )
            )
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            continue

    # Sort by newest first
    notes.sort(key=lambda x: x.created_at, reverse=True)
    return notes


@router.get("/generated/{filename}")
async def get_generated_note_content(filename: str):
    """
    Get the full content of a specific markdown file.
    """
    # Security check: prevent directory traversal
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = settings.output_dir / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Note file not found")

    content = file_path.read_text(encoding="utf-8")
    return {"content": content, "filename": filename}


# ==========================================
# End of New Endpoints
# ==========================================

# ... (Database endpoints kept for compatibility if needed later) ...
# You can leave the rest of the file as is, or I can include it below just in case.
# For brevity, I'll include the standard DB create/get just to not break anything.


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific note by ID.
    """
    statement = select(Note).where(Note.id == note_id, Note.user_id == current_user.id)
    result = await session.exec(statement)
    note = result.first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    return NoteResponse(
        id=note.id,
        video_url=note.video_url,
        video_title=note.video_title,
        summary_text=note.summary_content,
        video_duration=None,
        language="en",
        user_id=note.user_id,
        category=note.category,
        created_at=str(note.created_at),
    )


@router.get("", response_model=List[NoteResponse])
async def list_user_notes(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    List all notes belonging to the current user.
    """
    statement = (
        select(Note)
        .where(Note.user_id == current_user.id)
        .order_by(Note.created_at.desc())
    )
    result = await session.exec(statement)
    notes = result.all()

    return [
        NoteResponse(
            id=n.id,
            video_url=n.video_url,
            video_title=n.video_title,
            summary_text=n.summary_content,
            video_duration=None,  # Update if stored
            language="en",  # Default
            user_id=n.user_id,
            category=n.category,
            created_at=str(n.created_at),
        )
        for n in notes
    ]


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_data: CreateNoteRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # Automatically categorize the note
    category = await categorizer.categorize_text(note_data.summary_text)

    new_note = Note(
        video_url=str(note_data.video_url),
        video_title=note_data.video_title,
        summary_content=note_data.summary_text,
        user_id=current_user.id,
        category=category,
    )
    session.add(new_note)
    await session.commit()
    await session.refresh(new_note)
    return NoteResponse(
        id=new_note.id,
        video_url=new_note.video_url,
        video_title=new_note.video_title,
        summary_text=new_note.summary_content,
        video_duration=None,
        language="en",
        user_id=new_note.user_id,
        category=new_note.category,
        created_at=str(new_note.created_at),
    )
