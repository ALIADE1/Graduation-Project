from google import genai
from typing import Optional
from src.utils.logger import setup_logger
from src.utils.config import settings

logger = setup_logger(__name__)


class CategorizationService:
    """
    Service for automatically categorizing notes based on their content using Gemini AI.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.google_api_key
        # Use the newer google-genai client
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = "gemini-1.5-flash"

    async def categorize_text(self, text: str) -> str:
        """
        Categorize a piece of text into a single word or short phrase category.
        """
        if not text or len(text) < 10:
            return "Uncategorized"

        prompt = (
            "Analyze the following text and provide a single-word or short 2-word category that best describes its topic. "
            "Examples: Education, Technology, Health, Business, Personal, Cooking, Programming.\n\n"
            f"Text: {text[:2000]}\n\n"
            "Category:"
        )

        try:
            # Using the newer google-genai syntax
            response = self.client.models.generate_content(
                model=self.model_id, contents=prompt
            )

            category = response.text.strip().replace(".", "").title()
            # Basic validation/cleanup
            if len(category) > 30:
                category = category[:27] + "..."
            return category
        except Exception as e:
            logger.error(f"Categorization failed: {e}")
            return "Uncategorized"
