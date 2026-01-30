# YouTube Study Notes AI 🎓🎥

An AI-powered application that helps students and lifelong learners maximize their learning from YouTube videos. The app automatically generating concise notes, categorizes them, and provides personalized video recommendations.

## ✨ Key Features

- **AI Note Generation**: Converts YouTube videos into structured study notes.
- **Smart Categorization**: Automatically categorizes notes (e.g., Programming, History, Science) using Google Gemini AI.
- **Personalized Recommendations**: Suggests relevant YouTube videos based on your recent study history and interests.
- **Enhanced User Profiles**: Collects user-specific data (Age, Gender) to provide more accurate and personalized experiences.
- **User-Friendly Dashboard**: Easily access and manage your collection of AI-generated notes.

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLModel (Supabase/PostgreSQL)
- **AI/ML**: Google Gemini (generativeai), YouTube Data API v3
- **Authentication**: JWT-based auth

### Frontend
- **Framework**: Flutter
- **State Management**: Provider/setState
- **Networking**: Dio

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Flutter SDK
- Google API Key (with Gemini and YouTube Data API access)

### Backend Setup
1. Navigate to the `Program` directory:
   ```bash
   cd Program
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables (create a `.env` file):
   ```env
   DATABASE_URL=your_supabase_url
   GOOGLE_API_KEY=your_google_api_key
   SECRET_KEY=your_jwt_secret
   ```
4. Run the server:
   ```bash
   python run.py server
   ```

### Frontend Setup
1. Navigate to the `app` directory:
   ```bash
   cd app
   ```
2. Install Flutter packages:
   ```bash
   flutter pub get
   ```
3. Run the application:
   ```bash
   flutter run
   ```

## 📝 License

This project is part of a Graduation Project. All rights reserved.
