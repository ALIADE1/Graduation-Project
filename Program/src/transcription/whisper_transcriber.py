"""
Whisper-based speech-to-text transcription module.
Converts audio files to text using OpenAI's Whisper model.
"""

from pathlib import Path
from typing import Dict, List, Optional
import whisper
import torch

from src.utils.logger import setup_logger
from src.utils.config import settings

logger = setup_logger(__name__)


class WhisperTranscriber:
    """Handles audio transcription using Whisper ASR model."""
    
    def __init__(self, model_size: Optional[str] = None):
        """
        Initialize the Whisper transcriber.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
                       Defaults to config setting
        """
        self.model_size = model_size or settings.whisper_model_size
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"Initializing Whisper transcriber with model: {self.model_size}")
        logger.info(f"Using device: {self.device}")
    
    def load_model(self) -> None:
        """Load the Whisper model into memory."""
        if self.model is not None:
            logger.info("Model already loaded")
            return
        
        try:
            logger.info(f"Loading Whisper {self.model_size} model...")
            self.model = whisper.load_model(self.model_size, device=self.device)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise RuntimeError(f"Model loading failed: {str(e)}")
    
    def transcribe(
        self,
        audio_path: Path,
        language: str = "en",
        verbose: bool = True
    ) -> Dict[str, any]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to the audio file
            language: Language code (default: "en" for English)
            verbose: Whether to show progress during transcription
            
        Returns:
            Dictionary containing:
                - text: Full transcript
                - segments: List of timestamped segments
                - language: Detected/specified language
                
        Raises:
            FileNotFoundError: If audio file doesn't exist
            RuntimeError: If transcription fails
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Load model if not already loaded
        self.load_model()
        
        try:
            logger.info(f"Starting transcription of: {audio_path}")
            logger.info(f"Language: {language}")
            
            # Transcribe with Whisper
            result = self.model.transcribe(
                str(audio_path),
                language=language,
                verbose=verbose,
                task="transcribe",
                fp16=torch.cuda.is_available()  # Use FP16 on GPU for speed
            )
            
            # Extract relevant information
            transcript_data = {
                'text': result['text'].strip(),
                'segments': self._process_segments(result['segments']),
                'language': result['language'],
            }
            
            logger.info(f"Transcription complete. Length: {len(transcript_data['text'])} characters")
            logger.info(f"Number of segments: {len(transcript_data['segments'])}")
            
            return transcript_data
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise RuntimeError(f"Transcription error: {str(e)}")
    
    def _process_segments(self, raw_segments: List[Dict]) -> List[Dict]:
        """
        Process raw Whisper segments into a cleaner format.
        
        Args:
            raw_segments: Raw segment data from Whisper
            
        Returns:
            List of processed segments with timestamps and text
        """
        processed = []
        
        for segment in raw_segments:
            processed.append({
                'id': segment['id'],
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text'].strip(),
            })
        
        return processed
    
    def transcribe_with_timestamps(
        self,
        audio_path: Path,
        language: str = "en"
    ) -> str:
        """
        Transcribe audio and format with timestamps.
        
        Args:
            audio_path: Path to the audio file
            language: Language code
            
        Returns:
            Formatted transcript with timestamps
        """
        result = self.transcribe(audio_path, language, verbose=False)
        
        formatted_lines = []
        for segment in result['segments']:
            timestamp = self._format_timestamp(segment['start'])
            formatted_lines.append(f"[{timestamp}] {segment['text']}")
        
        return "\n".join(formatted_lines)
    
    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """
        Format seconds into MM:SS or HH:MM:SS.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted timestamp string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def get_plain_text(self, audio_path: Path, language: str = "en") -> str:
        """
        Get plain text transcript without timestamps.
        
        Args:
            audio_path: Path to the audio file
            language: Language code
            
        Returns:
            Plain text transcript
        """
        result = self.transcribe(audio_path, language, verbose=False)
        return result['text']
