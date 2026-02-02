from typing import List, Optional
from pydantic import BaseModel, Field

class KeyConcept(BaseModel):
    term: str = Field(..., description="The concept or term being explained")
    definition: str = Field(..., description="Explanation or definition of the term")

class TimelineItem(BaseModel):
    timestamp: str = Field(..., description="Timestamp in format MM:SS or HH:MM:SS")
    topic: str = Field(..., description="Topic discussed at this timestamp")
    summary: str = Field(..., description="Brief summary of what was discussed")

class StudyNoteSchema(BaseModel):
    title: str = Field(..., description="Title of the study notes")
    summary: str = Field(..., description="A high-level summary of the video content")
    key_concepts: List[KeyConcept] = Field(..., description="List of important terms and their definitions")
    action_items: List[str] = Field(..., description="Actionable takeaways or tasks derived from the content")
    timestamps: List[TimelineItem] = Field(..., description="Chronological timeline of topics")
    keywords: List[str] = Field(..., description="List of keywords for categorization and recommendations")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Introduction to Python",
                "summary": "This video covers the basics of Python programming, including variables, data types, and control flow.",
                "key_concepts": [
                    {"term": "Variable", "definition": "A name that refers to a value stored in memory."}
                ],
                "action_items": [
                    "Install Python 3.12",
                    "Try writing a hello world script"
                ],
                "timestamps": [
                    {"timestamp": "02:15", "topic": "Setting up the environment", "summary": "How to download and install Python."}
                ],
                "keywords": ["python", "programming", "tutorial", "coding"]
            }
        }
