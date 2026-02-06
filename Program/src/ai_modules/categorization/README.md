# Categorization Module 🏷️

## Responsibility
This module handles **automatic categorization of notes**.

## Functionality
1. Receive summary text.
2. Use **Google Gemini** to analyze content.
3. Return a single category (e.g., Programming, Medicine, History).

## Files

### 1. `categorizer.py`
- **Purpose:** Categorize text using AI.
- **Main Class:** `CategorizationService`
- **Key Method:** `categorize_text(text)` - Returns category name.

## How It Works
1. **Receive Text:** Take first 2000 characters from summary.
2. **Send Prompt:** Ask Gemini to determine one or two-word category.
3. **Clean Result:** Remove periods and capitalize first letter.
4. **Validate:** If result is too long (>30 chars), truncate it.

## Category Examples
- **Programming** - Coding and development tutorials.
- **Medicine** - Health and medical content.
- **Business** - Business management and entrepreneurship.
- **Science** - Physics, chemistry, biology.
- **History** - Historical events and civilizations.
- **Personal Development** - Self-improvement content.
- **Uncategorized** - If categorization fails.

## Proposed Enhancements
- [ ] Add predefined list of allowed categories.
- [ ] Use embeddings to improve categorization accuracy.
- [ ] Add support for sub-categories.
- [ ] Store categorization results in database for future analysis.

## Testing
```python
from src.ai_modules.categorization.categorizer import CategorizationService

categorizer = CategorizationService()

# Categorize text
text = "This video explains how to build a REST API using FastAPI and Python..."
category = await categorizer.categorize_text(text)

print(f"Category: {category}")  # Output: Programming
```

## Libraries Used
- `google-genai` - Communicate with Google Gemini.

## Important Notes
- Currently using `gemini-1.5-flash` model.
- If text is too short (<10 chars), returns "Uncategorized".
- Accuracy can be improved by adding examples in the prompt.

## Improving the Prompt
To improve categorization accuracy, you can modify the prompt in the file:
```python
prompt = (
    "Analyze the following text and categorize it into ONE of these categories: "
    "Programming, Medicine, Business, Science, History, Personal Development, Education, Technology. "
    "Return ONLY the category name.\n\n"
    f"Text: {text[:2000]}\n\n"
    "Category:"
)
```
