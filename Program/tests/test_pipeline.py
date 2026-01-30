"""
End-to-end pipeline test for YouTube study notes generation.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.audio.downloader import YouTubeDownloader
from src.audio.processor import AudioProcessor
from src.transcription.whisper_transcriber import WhisperTranscriber
from src.summarization.segmenter import TranscriptSegmenter
from src.summarization.note_generator import NoteGenerator
from src.utils.logger import setup_logger
from src.utils.config import settings

logger = setup_logger(__name__)


def test_pipeline(youtube_url: str):
    """
    Test the complete pipeline from YouTube URL to study notes.
    
    Args:
        youtube_url: YouTube video URL to process
    """
    logger.info("=" * 60)
    logger.info("STARTING PIPELINE TEST")
    logger.info("=" * 60)
    
    audio_file = None
    
    try:
        # Step 1: Download audio
        logger.info("\n[1/5] Downloading audio from YouTube...")
        downloader = YouTubeDownloader()
        
        if not downloader.is_valid_youtube_url(youtube_url):
            raise ValueError("Invalid YouTube URL")
        
        video_info = downloader.get_video_info(youtube_url)
        logger.info(f"Video: {video_info['title']}")
        logger.info(f"Duration: {video_info['duration']}s")
        
        audio_file = downloader.download_audio(youtube_url, "test_video")
        logger.info(f"✅ Audio downloaded: {audio_file}")
        
        # Step 2: Validate audio
        logger.info("\n[2/5] Validating audio file...")
        processor = AudioProcessor()
        
        if not processor.validate_audio_file(audio_file):
            raise ValueError("Audio validation failed")
        
        audio_info = processor.get_audio_info(audio_file)
        logger.info(f"✅ Audio validated: {audio_info['duration']:.2f}s, {audio_info['framerate']}Hz")
        
        # Step 3: Transcribe
        logger.info("\n[3/5] Transcribing audio with Whisper...")
        transcriber = WhisperTranscriber()
        transcript_data = transcriber.transcribe(audio_file, language="en", verbose=True)
        
        logger.info(f"✅ Transcription complete:")
        logger.info(f"   - Text length: {len(transcript_data['text'])} characters")
        logger.info(f"   - Segments: {len(transcript_data['segments'])}")
        logger.info(f"   - Language: {transcript_data['language']}")
        
        # Step 4: Segment transcript
        logger.info("\n[4/5] Segmenting transcript...")
        segmenter = TranscriptSegmenter()
        
        # Clean text
        cleaned_text = segmenter.clean_text(transcript_data['text'])
        logger.info(f"Text cleaned: {len(transcript_data['text'])} → {len(cleaned_text)} chars")
        
        # Segment
        segments = segmenter.segment_transcript(transcript_data, method="time")
        logger.info(f"✅ Created {len(segments)} segments")
        
        # Step 5: Generate notes
        logger.info("\n[5/5] Generating study notes with Gemini...")
        note_gen = NoteGenerator()
        
        if len(transcript_data['text'].split()) < 2000:
            notes = note_gen.generate_notes_from_full_transcript(
                transcript_data['text'],
                video_info['title']
            )
        else:
            notes = note_gen.generate_notes_from_segments(segments)
        
        logger.info(f"✅ Notes generated: {len(notes)} characters")
        
        # Format final notes
        final_notes = note_gen.format_final_notes(
            notes,
            video_info['title'],
            youtube_url,
            video_info['duration']
        )
        
        # Save notes
        output_file = settings.output_dir / "test_output_notes.md"
        output_file.write_text(final_notes, encoding='utf-8')
        
        logger.info(f"\n✅ SUCCESS! Notes saved to: {output_file}")
        
        # Show preview
        logger.info("\n" + "=" * 60)
        logger.info("NOTES PREVIEW (first 500 chars)")
        logger.info("=" * 60)
        logger.info(final_notes[:500] + "...")
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        if audio_file and audio_file.exists():
            logger.info("\nCleaning up temporary files...")
            downloader.cleanup(audio_file)


if __name__ == "__main__":
    # Test with a short educational video
    # Replace with an actual YouTube URL
    TEST_URL = "https://www.youtube.com/watch?v=aircAruvnKk"  # Example: 3Blue1Brown
    
    if len(sys.argv) > 1:
        TEST_URL = sys.argv[1]
    
    logger.info(f"Test URL: {TEST_URL}")
    
    success = test_pipeline(TEST_URL)
    
    sys.exit(0 if success else 1)
