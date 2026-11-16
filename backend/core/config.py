"""
core/config.py
--------------
Central application configuration loaded from environment variables.
Uses pydantic-settings so values can be overridden via a .env file.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application metadata
    APP_NAME: str = "Health Inequality Intelligence System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS – allow local dev server and deployed origins
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "*",
    ]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


# Single shared instance imported throughout the project
settings = Settings()
