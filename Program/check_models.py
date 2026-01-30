import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌Can't find the key.env")
else:
    genai.configure(api_key=api_key)
    print("🔍 Searching for available models...")
    try:
        found = False
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                print(f"✅ Available: {m.name}")
                found = True
        if not found:
            print("⚠️ No models found that support text generation.")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

input("\nPress Enter to exit...")
