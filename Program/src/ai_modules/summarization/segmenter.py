"""
Transcript segmentation module.
Splits long transcripts into logical sections for better processing.
"""

import re
from typing import List, Dict

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class TranscriptSegmenter:
    """Handles intelligent segmentation of transcripts."""
    
    # Common filler words to remove
    FILLER_WORDS = {
        'um', 'uh', 'like', 'you know', 'i mean', 'sort of', 'kind of',
        'basically', 'actually', 'literally', 'right', 'okay', 'so yeah'
    }
    
    def __init__(self, max_segment_words: int = 500):
        """
        Initialize the segmenter.
        
        Args:
            max_segment_words: Maximum words per segment
        """
        self.max_segment_words = max_segment_words
    
    def clean_text(self, text: str) -> str:
        """
        Clean transcript by removing filler words and normalizing.
        
        Args:
            text: Raw transcript text
            
        Returns:
            Cleaned text
        """
        # Convert to lowercase for processing
        cleaned = text.lower()
        
        # Remove filler words
        for filler in self.FILLER_WORDS:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(filler) + r'\b'
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Remove multiple spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remove leading/trailing whitespace
        cleaned = cleaned.strip()
        
        # Capitalize first letter of sentences
        cleaned = '. '.join(s.capitalize() for s in cleaned.split('. '))
        
        logger.debug(f"Cleaned text: reduced from {len(text)} to {len(cleaned)} characters")
        
        return cleaned
    
    def segment_by_time(
        self,
        segments: List[Dict],
        interval_seconds: int = 300
    ) -> List[Dict]:
        """
        Segment transcript by time intervals.
        
        Args:
            segments: List of timestamped segments from Whisper
            interval_seconds: Time interval for each segment (default: 5 minutes)
            
        Returns:
            List of combined segments grouped by time
        """
        if not segments:
            return []
        
        time_segments = []
        current_segment = {
            'start': segments[0]['start'],
            'text': ''
        }
        
        for seg in segments:
            # Check if we should start a new time segment
            if seg['start'] - current_segment['start'] >= interval_seconds:
                # Save current segment
                current_segment['end'] = seg['start']
                time_segments.append(current_segment)
                
                # Start new segment
                current_segment = {
                    'start': seg['start'],
                    'text': seg['text']
                }
            else:
                # Add to current segment
                current_segment['text'] += ' ' + seg['text']
        
        # Add the last segment
        if current_segment['text']:
            current_segment['end'] = segments[-1]['end']
            time_segments.append(current_segment)
        
        logger.info(f"Segmented transcript into {len(time_segments)} time-based segments")
        
        return time_segments
    
    def segment_by_topic(self, text: str) -> List[str]:
        """
        Segment text by detecting topic transitions.
        Simple heuristic: Split on paragraph breaks and large sentences.
        
        Args:
            text: Full transcript text
            
        Returns:
            List of text segments
        """
        # Split by double newlines (paragraphs)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        segments = []
        current_segment = []
        current_word_count = 0
        
        for para in paragraphs:
            words = para.split()
            word_count = len(words)
            
            # If adding this paragraph exceeds max words, start new segment
            if current_word_count + word_count > self.max_segment_words and current_segment:
                segments.append(' '.join(current_segment))
                current_segment = [para]
                current_word_count = word_count
            else:
                current_segment.append(para)
                current_word_count += word_count
        
        # Add the last segment
        if current_segment:
            segments.append(' '.join(current_segment))
        
        logger.info(f"Segmented text into {len(segments)} topic-based segments")
        
        return segments
    
    def segment_transcript(
        self,
        transcript_data: Dict,
        method: str = "time"
    ) -> List[Dict]:
        """
        Segment transcript using specified method.
        
        Args:
            transcript_data: Full transcript data with text and segments
            method: Segmentation method ("time" or "topic")
            
        Returns:
            List of segmented chunks
        """
        if method == "time" and 'segments' in transcript_data:
            # Use timestamped segments
            return self.segment_by_time(transcript_data['segments'])
        else:
            # Use topic-based segmentation on full text
            text_segments = self.segment_by_topic(transcript_data['text'])
            return [{'text': seg} for seg in text_segments]
