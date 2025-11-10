"""Configuration management using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Settings
    app_name: str = Field(default="Conversational Chatbot", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")

    # LLM Provider Configuration
    llm_provider: Literal["openai", "anthropic", "gemini", "ollama"] = Field(
        default="openai", description="LLM provider to use"
    )
    llm_model: str = Field(default="gpt-4", description="LLM model name")
    llm_temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="LLM temperature")
    llm_max_tokens: int = Field(default=2000, gt=0, description="Maximum tokens for LLM response")

    # API Keys
    openai_api_key: str | None = Field(default=None, description="OpenAI API key")
    anthropic_api_key: str | None = Field(default=None, description="Anthropic API key")
    google_api_key: str | None = Field(default=None, description="Google Gemini API key")

    # Ollama Settings
    ollama_base_url: str = Field(
        default="http://localhost:11434", description="Ollama base URL"
    )
    ollama_model: str = Field(default="llama2", description="Ollama model name")

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./chatbot.db", description="Database connection URL"
    )

    # Memory Settings
    short_term_memory_window: int = Field(
        default=10, gt=0, description="Number of recent messages to keep in short-term memory"
    )
    long_term_memory_summary_threshold: int = Field(
        default=50, gt=0, description="Number of messages before summarization"
    )

    # Session Settings
    session_timeout_minutes: int = Field(
        default=30, gt=0, description="Session timeout in minutes"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("openai_api_key")
    @classmethod
    def validate_openai_key(cls, v: str | None, info) -> str | None:
        """Validate OpenAI API key is present when using OpenAI provider."""
        # Get provider from validation context
        if info.data.get("llm_provider") == "openai" and not v:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
        return v

    @field_validator("anthropic_api_key")
    @classmethod
    def validate_anthropic_key(cls, v: str | None, info) -> str | None:
        """Validate Anthropic API key is present when using Anthropic provider."""
        if info.data.get("llm_provider") == "anthropic" and not v:
            raise ValueError("ANTHROPIC_API_KEY is required when using Anthropic provider")
        return v

    @field_validator("google_api_key")
    @classmethod
    def validate_google_key(cls, v: str | None, info) -> str | None:
        """Validate Google API key is present when using Gemini provider."""
        if info.data.get("llm_provider") == "gemini" and not v:
            raise ValueError("GOOGLE_API_KEY is required when using Gemini provider")
        return v


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Uses @lru_cache to ensure Settings is instantiated only once,
    implementing the singleton pattern for configuration.

    Returns:
        Settings: Cached settings instance
    """
    return Settings()



