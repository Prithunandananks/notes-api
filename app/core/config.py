import os
from typing import List, Any, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings class using Pydantic Settings.
    Loads and validates environment variables from the .env file.
    Provides sensible defaults for local development.
    """
    # Core Application Settings
    APP_NAME: str = Field(default="Notes API")
    API_V1_PREFIX: str = Field(default="/api/v1")
    
    # Database Settings
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./notes.db")
    
    # JWT Authentication Security Settings
    JWT_SECRET_KEY: str = Field(default="super-secret-key-change-in-production-1234567890")
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    
    # File Upload Settings
    UPLOAD_DIR: str = Field(default="uploads")
    MAX_UPLOAD_SIZE_MB: int = Field(default=5)  # Default max upload size of 5 Megabytes
    ALLOWED_FILE_TYPES: List[str] = Field(default=["jpg", "jpeg", "png", "pdf", "txt"])

    # CORS Settings (Required by app/main.py middleware stack)
    BACKEND_CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:8000"])

    # Private attribute to support dynamic test monkeypatch overrides
    _max_file_size_override: Optional[int] = None

    # Parser validator to handle comma-separated lists or JSON string arrays from .env
    @field_validator("ALLOWED_FILE_TYPES", mode="before")
    @classmethod
    def parse_allowed_file_types(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    import json
                    return json.loads(v)
                except Exception:
                    pass
            return [item.strip().lower() for item in v.split(",") if item.strip()]
        return v

    # Compatibility properties for existing codebase integrations
    @property
    def PROJECT_NAME(self) -> str:
        return self.APP_NAME

    @property
    def API_V1_STR(self) -> str:
        return self.API_V1_PREFIX

    @property
    def SECRET_KEY(self) -> str:
        return self.JWT_SECRET_KEY

    @property
    def ALGORITHM(self) -> str:
        return self.JWT_ALGORITHM

    @property
    def MAX_FILE_SIZE(self) -> int:
        if self._max_file_size_override is not None:
            return self._max_file_size_override
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @MAX_FILE_SIZE.setter
    def MAX_FILE_SIZE(self, value: int) -> None:
        self._max_file_size_override = value

    @property
    def ALLOWED_EXTENSIONS(self) -> List[str]:
        return self.ALLOWED_FILE_TYPES

    @property
    def ALLOWED_MIME_TYPES(self) -> List[str]:
        # Maps allowed extensions to standard browser MIME types
        mime_mapping = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "pdf": "application/pdf",
            "txt": "text/plain"
        }
        return [mime_mapping[ext] for ext in self.ALLOWED_FILE_TYPES if ext in mime_mapping]

    # Configuration binding settings source
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()

# Ensure that the configured upload folder exists on system initialization
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
