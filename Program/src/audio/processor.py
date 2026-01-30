"""
Audio preprocessing utilities.
Handles noise reduction, normalization, and format validation.
"""

from pathlib import Path
from typing import Optional
import wave

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class AudioProcessor:
    """Handles audio preprocessing and validation."""
    
    @staticmethod
    def get_audio_duration(audio_path: Path) -> float:
        """
        Get the duration of an audio file in seconds.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Duration in seconds
        """
        try:
            with wave.open(str(audio_path), 'r') as audio_file:
                frames = audio_file.getnframes()
                rate = audio_file.getframerate()
                duration = frames / float(rate)
                return duration
        except Exception as e:
            logger.warning(f"Could not get audio duration: {e}")
            return 0.0
    
    @staticmethod
    def validate_audio_file(audio_path: Path) -> bool:
        """
        Validate that the audio file is readable and properly formatted.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            True if valid, False otherwise
        """
        if not audio_path.exists():
            logger.error(f"Audio file does not exist: {audio_path}")
            return False
        
        if audio_path.stat().st_size == 0:
            logger.error(f"Audio file is empty: {audio_path}")
            return False
        
        try:
            with wave.open(str(audio_path), 'r') as audio_file:
                # Check basic properties
                channels = audio_file.getnchannels()
                sample_width = audio_file.getsampwidth()
                framerate = audio_file.getframerate()
                
                logger.info(
                    f"Audio validation: {channels} channels, "
                    f"{sample_width} bytes/sample, {framerate} Hz"
                )
                
                return True
        except Exception as e:
            logger.error(f"Audio file validation failed: {e}")
            return False
    
    @staticmethod
    def get_audio_info(audio_path: Path) -> dict:
        """
        Get detailed information about an audio file.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dictionary with audio properties
        """
        try:
            with wave.open(str(audio_path), 'r') as audio_file:
                frames = audio_file.getnframes()
                rate = audio_file.getframerate()
                duration = frames / float(rate)
                
                return {
                    'channels': audio_file.getnchannels(),
                    'sample_width': audio_file.getsampwidth(),
                    'framerate': rate,
                    'frames': frames,
                    'duration': duration,
                    'file_size': audio_path.stat().st_size,
                }
        except Exception as e:
            logger.error(f"Failed to get audio info: {e}")
            return {}
