"""
Configuration management for the YouTube Notes AI application.
Uses Pydantic Settings for type-safe environment variable loading.
"""

import os
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables."""
    
    # Google Gemini API Configuration
    google_api_key: str = Field(
        ..., 
        description="Google Gemini API key for note generation"
    )
    
    # Whisper Model Configuration
    whisper_model_size: Literal["tiny", "base", "small", "medium", "large"] = Field(
        default="base",
        description="Whisper model size (larger = more accurate but slower)"
    )
    
    # Processing Limits
    max_video_duration: int = Field(
        default=7200,
        description="Maximum video duration in seconds (2 hours default)"
    )
    
    # Output Configuration
    output_format: Literal["markdown", "json"] = Field(
        default="markdown",
        description="Output format for generated notes"
    )
    output_dir: Path = Field(
        default=Path("outputs"),
        description="Directory for saving generated notes"
    )
    
    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    log_file: str = Field(
        default="app.log",
        description="Log file path"
    )
    
    # API Configuration
    api_host: str = Field(
        default="0.0.0.0",
        description="FastAPI host address"
    )
    api_port: int = Field(
        default=8000,
        description="FastAPI port number"
    )
    
    # Database Configuration
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/studynotes",
        description="PostgreSQL database connection URL (use asyncpg driver)"
    )
    
    # Authentication Configuration
    secret_key: str = Field(
        default="your-secret-key-change-this-in-production-min-32-chars",
        description="JWT secret key for token signing (MUST be changed in production)"
    )
    access_token_expire_minutes: int = Field(
        default=60,
        description="JWT token expiration time in minutes"
    )
    algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )
    
    # Temporary Files
    temp_dir: Path = Field(
        default=Path("temp"),
        description="Directory for temporary files (audio, video)"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    def __init__(self, **kwargs):
        """Initialize settings and create necessary directories."""
        super().__init__(**kwargs)
        
        # Create directories if they don't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
