"""
YouTube video downloader and audio extraction module.
Uses yt-dlp for robust YouTube video handling.
"""

import re
from pathlib import Path
from typing import Dict, Optional
import yt_dlp

from src.utils.logger import setup_logger
from src.utils.config import settings

logger = setup_logger(__name__)


class YouTubeDownloader:
    """Handles YouTube video downloading and audio extraction."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize the YouTube downloader.
        
        Args:
            output_dir: Directory to save downloaded audio files
        """
        self.output_dir = output_dir or settings.temp_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    @staticmethod
    def is_valid_youtube_url(url: str) -> bool:
        """
        Validate if the URL is a valid YouTube link.
        
        Args:
            url: YouTube URL to validate
            
        Returns:
            True if valid YouTube URL, False otherwise
        """
        youtube_regex = (
            r'(https?://)?(www\.)?'
            r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        
        match = re.match(youtube_regex, url)
        return bool(match)
    
    def get_video_info(self, url: str) -> Dict[str, any]:
        """
        Get video information without downloading.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Dictionary containing video metadata
            
        Raises:
            ValueError: If URL is invalid or video is unavailable
        """
        if not self.is_valid_youtube_url(url):
            raise ValueError(f"Invalid YouTube URL: {url}")
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'upload_date': info.get('upload_date', ''),
                }
        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            raise ValueError(f"Could not access video: {str(e)}")
    
    def download_audio(self, url: str, video_id: Optional[str] = None) -> Path:
        """
        Download YouTube video and extract audio.
        
        Args:
            url: YouTube video URL
            video_id: Optional custom identifier for the output file
            
        Returns:
            Path to the downloaded audio file
            
        Raises:
            ValueError: If URL is invalid or download fails
            RuntimeError: If video exceeds maximum duration
        """
        if not self.is_valid_youtube_url(url):
            raise ValueError(f"Invalid YouTube URL: {url}")
        
        # Get video info to check duration
        info = self.get_video_info(url)
        duration = info['duration']
        
        if duration > settings.max_video_duration:
            raise RuntimeError(
                f"Video duration ({duration}s) exceeds maximum allowed "
                f"({settings.max_video_duration}s)"
            )
        
        # Generate output filename
        if video_id:
            output_template = str(self.output_dir / f"{video_id}.%(ext)s")
        else:
            output_template = str(self.output_dir / "%(id)s.%(ext)s")
        
        # yt-dlp options for audio extraction
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'outtmpl': output_template,
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
        }
        
        try:
            logger.info(f"Downloading audio from: {url}")
            logger.info(f"Video title: {info['title']}")
            logger.info(f"Duration: {duration}s ({duration/60:.1f} minutes)")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(url, download=True)
                
                # Get the output filename
                if video_id:
                    audio_file = self.output_dir / f"{video_id}.wav"
                else:
                    audio_file = self.output_dir / f"{result['id']}.wav"
                
                if not audio_file.exists():
                    raise RuntimeError("Audio file was not created")
                
                logger.info(f"Audio downloaded successfully: {audio_file}")
                return audio_file
                
        except Exception as e:
            logger.error(f"Failed to download audio: {e}")
            raise ValueError(f"Download failed: {str(e)}")
    
    def cleanup(self, file_path: Path) -> None:
        """
        Remove downloaded audio file.
        
        Args:
            file_path: Path to the file to remove
        """
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Cleaned up file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup file {file_path}: {e}")
