"""
Main entry point for YouTube Study Notes AI.
Provides CLI interface and server startup.
"""

import sys
import argparse
from pathlib import Path

# Import necessary modules for server and middleware
from src.utils.logger import setup_logger
from src.utils.config import settings

logger = setup_logger(__name__)


def run_server():
    """Start the FastAPI server with CORS enabled for Flutter Web."""
    import uvicorn
    from fastapi.middleware.cors import CORSMiddleware
    from src.api.main import app  # Import the app instance directly

    logger.info("Configuring CORS for Flutter Web...")

    # Add CORS Middleware to allow requests from Chrome/Flutter
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )

    logger.info("Starting YouTube Study Notes AI server...")
    logger.info(
        f"Server will be available at http://{settings.api_host}:{settings.api_port}"
    )
    logger.info(
        f"API Documentation: http://{settings.api_host}:{settings.api_port}/docs"
    )

    # Run the server using the app object directly
    # Note: reload is disabled here to ensure CORS settings are applied correctly from this script
    uvicorn.run(app, host=settings.api_host, port=settings.api_port, log_level="info")


def run_cli(youtube_url: str, output_file: str = None):
    """
    Run note generation from command line.

    Args:
        youtube_url: YouTube video URL
        output_file: Optional output file path
    """
    from src.audio.downloader import YouTubeDownloader
    from src.transcription.whisper_transcriber import WhisperTranscriber
    from src.summarization.note_generator import NoteGenerator

    logger.info("Starting CLI mode")
    logger.info(f"Processing URL: {youtube_url}")

    try:
        # Step 1: Download audio
        logger.info("Step 1/3: Downloading audio...")
        downloader = YouTubeDownloader()
        video_info = downloader.get_video_info(youtube_url)
        audio_file = downloader.download_audio(youtube_url)

        # Step 2: Transcribe
        logger.info("Step 2/3: Transcribing audio...")
        transcriber = WhisperTranscriber()
        transcript_data = transcriber.transcribe(audio_file)

        # Step 3: Generate notes
        logger.info("Step 3/3: Generating notes...")
        note_gen = NoteGenerator()
        notes = note_gen.generate_notes_from_full_transcript(
            transcript_data["text"], video_info["title"]
        )

        # Format and save
        final_notes = note_gen.format_final_notes(
            notes, video_info["title"], youtube_url, video_info["duration"]
        )

        if output_file:
            output_path = Path(output_file)
        else:
            output_path = settings.output_dir / f"{video_info['title'][:50]}_notes.md"

        output_path.write_text(final_notes, encoding="utf-8")

        logger.info(f"✅ Notes saved to: {output_path}")
        print(f"\n✅ Success! Notes saved to: {output_path}")

        # Cleanup
        downloader.cleanup(audio_file)

    except Exception as e:
        logger.error(f"Failed: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="YouTube Study Notes AI - Generate structured notes from educational videos"
    )

    parser.add_argument(
        "mode",
        choices=["server", "cli"],
        help="Run mode: server (API + web UI) or cli (direct processing)",
    )

    parser.add_argument(
        "--url", type=str, help="YouTube video URL (required for cli mode)"
    )

    parser.add_argument(
        "--output", type=str, help="Output file path (optional for cli mode)"
    )

    args = parser.parse_args()

    if args.mode == "server":
        run_server()
    elif args.mode == "cli":
        if not args.url:
            print("Error: --url is required for cli mode")
            sys.exit(1)
        run_cli(args.url, args.output)


if __name__ == "__main__":
    main()
