# Transcription Module 🎤

## Responsibility
This module handles **Speech-to-Text conversion** from YouTube videos.

## Functionality
1. Download audio from YouTube videos.
2. Convert audio files to text using **OpenAI Whisper**.

## Files

### 1. `audio_downloader.py`
- **Purpose:** Download audio from YouTube using `yt-dlp`.
- **Main Class:** `YouTubeDownloader`
- **Key Method:** `download_audio(url)` - Downloads audio and returns file path.

### 2. `whisper_transcriber.py`
- **Purpose:** Convert audio to text using Whisper.
- **Main Class:** `WhisperTranscriber`
- **Key Method:** `transcribe(audio_path)` - Returns full text + timestamps.

### 3. `audio_processor.py`
- **Purpose:** Validate and process audio files.
- **Key Methods:**
  - `validate_audio_file()` - Verify file integrity.
  - `get_audio_duration()` - Calculate video duration.

## Proposed Enhancements
- [ ] Add support for multiple languages (Arabic, French, Spanish).
- [ ] Improve download speed using multi-threading.
- [ ] Add caching for audio files to avoid re-downloading.

## Testing
```python
from src.ai_modules.transcription.audio_downloader import YouTubeDownloader
from src.ai_modules.transcription.whisper_transcriber import WhisperTranscriber

# Download audio
downloader = YouTubeDownloader()
audio_path = downloader.download_audio("https://www.youtube.com/watch?v=...")

# Transcribe to text
transcriber = WhisperTranscriber()
result = transcriber.transcribe(audio_path)
print(result['text'])
```

## Libraries Used
- `yt-dlp` - Download videos from YouTube.
- `openai-whisper` - Convert audio to text.
- `torch` - Leverage GPU for transcription.

## Important Notes
- Default model is `base` but can be changed to `medium` or `large` for higher accuracy.
- Using GPU significantly speeds up the process (if available on the machine).
