import json
from typing import Dict, Optional
from google import genai
from pydantic import ValidationError

from src.utils.logger import setup_logger
from src.utils.config import settings
from src.ai_modules.summarization.schemas import StudyNoteSchema

logger = setup_logger(__name__)


class NoteGenerator:
    """Generates structured study notes using Google Gemini LLM."""

    SYSTEM_PROMPT = """You are an expert educational note-taker. Convert transcripts into a valid JSON object matching the provided schema.
    
    Guidelines:
    1. Extract the most important educational content.
    2. Be concise but comprehensive.
    3. Ensure keywords are relevant for categorization.
    4. Provide a chronological timeline of topics.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.google_api_key
        # Switch to the new google-genai client
        self.client = genai.Client(api_key=self.api_key)

        # Use a model name that was confirmed to be available
        self.model_id = "gemini-flash-latest"

        logger.info(
            f"Initialized NoteGenerator with {self.model_id} using google-genai"
        )

    def generate_notes_json(self, transcript_text: str, video_title: str) -> Dict:
        try:
            prompt = f"{self.SYSTEM_PROMPT}\nVideo Title: {video_title}\nTranscript: {transcript_text}"

            logger.info(f"Generating notes for: {video_title}")

            # Using the new google-genai syntax
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": StudyNoteSchema,
                },
            )

            try:
                # The response object has a parsed data field if schema is provided
                # but if we want to be safe with json.loads:
                content = response.text
                data = json.loads(content)
                validated_notes = StudyNoteSchema(**data)
                return validated_notes.model_dump()
            except (json.JSONDecodeError, ValidationError) as e:
                logger.error(f"Validation failed: {e}")
                return self._get_error_json(str(e))

        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            return self._get_error_json(str(e))

    def format_notes_to_markdown(self, json_notes: Dict) -> str:
        md = f"## Summary\n{json_notes.get('summary', '')}\n\n"
        md += "## Key Concepts\n"
        for concept in json_notes.get("key_concepts", []):
            md += f"- **{concept.get('term', '')}**: {concept.get('definition', '')}\n"
        md += "\n## Timeline\n"
        for item in json_notes.get("timestamps", []):
            md += f"- **{item.get('timestamp', '')}** - {item.get('topic', '')}: {item.get('summary', '')}\n"
        md += "\n## Action Items\n"
        for item in json_notes.get("action_items", []):
            md += f"- {item}\n"
        return md

    def format_final_notes(
        self, notes: str, video_title: str, video_url: str, duration: int
    ) -> str:
        duration_str = self._format_timestamp(duration)
        header = f"# {video_title}\n\n---\n**Source:** {video_url}\n**Duration:** {duration_str}\n---\n\n"
        return header + notes

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def _get_error_json(self, error_msg: str) -> Dict:
        return {
            "title": "Error",
            "summary": error_msg,
            "key_concepts": [],
            "action_items": [],
            "timestamps": [],
            "keywords": [],
        }
