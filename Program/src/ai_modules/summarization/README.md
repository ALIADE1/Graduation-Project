# Summarization Module 📝

## Responsibility
This module handles **text summarization and conversion to study notes**.

## Functionality
1. Receive transcribed text from videos.
2. Use **Google Gemini** to analyze text and convert it to organized notes.
3. Create a Markdown file containing:
   - General summary
   - Key concepts
   - Timeline
   - Action items

## Files

### 1. `note_generator.py`
- **Purpose:** Generate notes using Gemini AI.
- **Main Class:** `NoteGenerator`
- **Key Methods:**
  - `generate_notes_json(transcript, title)` - Generates structured JSON.
  - `format_notes_to_markdown(json_notes)` - Converts JSON to Markdown.

### 2. `schemas.py`
- **Purpose:** Define data structure (Schema) for notes.
- **Main Class:** `StudyNoteSchema`
- **Fields:**
  - `summary` - General summary.
  - `key_concepts` - List of concepts and definitions.
  - `timestamps` - Timeline of topics.
  - `action_items` - Suggested tasks or exercises.

### 3. `segmenter.py`
- **Purpose:** Split long texts into smaller segments.
- **Main Class:** `TranscriptSegmenter`
- **Key Methods:**
  - `segment_by_time()` - Split by time (e.g., every 5 minutes).
  - `clean_text()` - Remove filler words (um, uh, like).

## Proposed Enhancements
- [ ] Add support for diagrams and illustrations.
- [ ] Improve prompts for more detailed summaries.
- [ ] Add translation feature to Arabic.

## Testing
```python
from src.ai_modules.summarization.note_generator import NoteGenerator

generator = NoteGenerator()
transcript = "Here is the complete video transcript..."
title = "Introduction to Python"

# Generate notes
notes_json = generator.generate_notes_json(transcript, title)
notes_md = generator.format_notes_to_markdown(notes_json)

print(notes_md)
```

## Libraries Used
- `google-genai` - Communicate with Google Gemini.
- `pydantic` - Data validation.

## Important Notes
- Currently using `gemini-flash-latest` model.
- Summary quality can be improved by modifying the `SYSTEM_PROMPT`.
- The Schema ensures the output is always in valid JSON format.
