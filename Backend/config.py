"""
config.py — All settings in one place, loaded from environment variables / .env.

Why: secrets (API keys) must never be hard-coded. pydantic-settings reads the
.env file, validates the types, and gives us a typed `settings` object.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- LLM (any OpenAI-compatible API: OpenAI, Groq, OpenRouter, Ollama, LM Studio...) ---
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4.1-mini"

    # --- Database ---
    database_url: str = "sqlite:///./tasks.db"

    # --- Web ---
    frontend_origin: str = "http://localhost:5173"
    log_level: str = "INFO"


settings = Settings()
