import uuid
from datetime import datetime
from typing import Dict
from enum import Enum
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

from src.audio.downloader import YouTubeDownloader
from src.transcription.whisper_transcriber import WhisperTranscriber
from src.summarization.note_generator import NoteGenerator
from src.utils.logger import setup_logger
from src.db.database import create_db_and_tables, async_engine
from src.db.models import Note, User
from src.auth.dependencies import get_current_user
from src.api.auth_routes import router as auth_router
from src.api.notes_routes import router as notes_router
from sqlmodel.ext.asyncio.session import AsyncSession

logger = setup_logger(__name__)


# --- Models ---
class TaskStatus(str, Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    TRANSCRIBING = "transcribing"
    GENERATING_NOTES = "generating_notes"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerateNotesRequest(BaseModel):
    youtube_url: HttpUrl
    language: str = "en"


class TaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    message: str


# Global task storage
tasks: Dict[str, Dict] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Lifespan: Initializing database tables...")
    await create_db_and_tables()
    yield


app = FastAPI(title="YouTube Study Notes AI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routes ---
app.include_router(auth_router)
app.include_router(notes_router)


@app.post("/generate", response_model=TaskResponse)
async def generate(
    request: GenerateNotesRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    task_id = str(uuid.uuid4())
    user_id = current_user.id

    tasks[task_id] = {
        "status": TaskStatus.PENDING,
        "message": "Initializing...",
        "youtube_url": str(request.youtube_url),
        "user_id": user_id,
        "created_at": datetime.now(),
    }

    background_tasks.add_task(
        process_video_and_save,
        task_id,
        str(request.youtube_url),
        request.language,
        user_id,
    )

    return TaskResponse(
        task_id=task_id,
        status=TaskStatus.PENDING,
        message="Generation started successfully.",
    )


async def process_video_and_save(
    task_id: str, youtube_url: str, language: str, user_id: int
):
    audio_file = None
    try:
        tasks[task_id]["status"] = TaskStatus.DOWNLOADING
        downloader = YouTubeDownloader()
        video_info = downloader.get_video_info(youtube_url)
        audio_file = downloader.download_audio(youtube_url, task_id)

        tasks[task_id]["status"] = TaskStatus.TRANSCRIBING
        transcriber = WhisperTranscriber()
        transcript_data = transcriber.transcribe(audio_file, language=language)

        tasks[task_id]["status"] = TaskStatus.GENERATING_NOTES
        note_gen = NoteGenerator()
        json_notes = note_gen.generate_notes_json(
            transcript_data["text"], video_info["title"]
        )
        final_notes = note_gen.format_final_notes(
            note_gen.format_notes_to_markdown(json_notes),
            video_info["title"],
            youtube_url,
            video_info["duration"],
        )

        async with AsyncSession(async_engine) as session:
            new_note = Note(
                user_id=user_id,
                video_url=youtube_url,
                video_title=video_info["title"],
                summary_content=final_notes,
            )
            session.add(new_note)
            await session.commit()
            await session.refresh(new_note)

        tasks[task_id]["status"] = TaskStatus.COMPLETED
    except Exception as e:
        logger.error(f"Task failed: {e}")
        tasks[task_id]["status"] = TaskStatus.FAILED
    finally:
        if audio_file and audio_file.exists():
            downloader.cleanup(audio_file)


@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]
