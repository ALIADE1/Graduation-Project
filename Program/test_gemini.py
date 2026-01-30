import os
import asyncio
from google import genai
from dotenv import load_dotenv


async def test_gemini():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY not found in .env")
        return

    client = genai.Client(api_key=api_key)
    model_id = "gemini-flash-latest"

    print(f"Testing Gemini with model: {model_id}...")
    try:
        response = client.models.generate_content(
            model=model_id,
            contents="Hello! Can you confirm you are working? Reply with 'Yes, I am working!'",
        )
        print(f"✅ Success! Response: {response.text}")
    except Exception as e:
        print(f"❌ Gemini Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_gemini())
