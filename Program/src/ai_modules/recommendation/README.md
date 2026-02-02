# Recommendation Module 🎯

## Responsibility
This module handles **suggesting new educational videos** based on user interests.

## Functionality
1. Analyze user's saved notes.
2. Extract topics and categories.
3. Search **YouTube** for related videos.
4. Return a list of suggested educational videos.

## Files

### 1. `recommender.py`
- **Purpose:** Suggest educational videos from YouTube.
- **Main Class:** `RecommendationService`
- **Key Methods:**
  - `get_recommendations_for_user(user_id)` - Get general recommendations for user.
  - `get_youtube_recommendations(query)` - Search YouTube based on keywords.
  - `get_similar_notes(note_id)` - Get similar notes from the same category.

## How It Works
1. **Fetch Notes:** Read the user's last 5 saved notes.
2. **Extract Topics:** Use categories or titles.
3. **Enhance Search:** Add keywords like "educational", "tutorial", "lecture".
4. **Filter Results:** Select only embeddable videos.

## Proposed Enhancements
- [ ] Add caching for recommendations to reduce YouTube API calls.
- [ ] Use Machine Learning to improve recommendation accuracy.
- [ ] Add filter for video duration (avoid very long videos).
- [ ] Prioritize well-known educational channels.

## Testing
```python
from src.ai_modules.recommendation.recommender import RecommendationService
from src.db.database import get_session

recommender = RecommendationService()

# Get recommendations for user
async def test_recommendations():
    async with get_session() as session:
        recs = await recommender.get_recommendations_for_user(session, user_id=1)
        for video in recs:
            print(f"{video['title']} - {video['url']}")
```

## Libraries Used
- `google-api-python-client` - Search YouTube.
- `google-genai` - Analyze topics (future use).

## Important Notes
- YouTube API has a **daily quota limit**, use caching to reduce requests.
- Enhanced search adds "educational lecture tutorial" keywords for better educational results.
- System prioritizes videos from the same category.

## API Quota Management
It's recommended to cache results temporarily to avoid exhausting YouTube API quota:
```python
# Simple cache example
cache = {}

def get_cached_recommendations(query):
    if query in cache:
        return cache[query]
    
    results = youtube_search(query)
    cache[query] = results
    return results
```
