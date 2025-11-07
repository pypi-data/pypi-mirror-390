"""Google AI configuration (Gemini and Vertex AI).

This module provides configuration management for Google's AI services:
- Gemini API (direct API access)
- Vertex AI (Google Cloud Platform integration)
"""

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings

from exc2issue.config._base import build_default_settings_config


class GeminiConfig(BaseSettings):
    """Gemini API configuration.

    Environment Variables:
        GEMINI_API_KEY or BUG_HUNTER_GEMINI_API_KEY: Google Gemini API key
        GEMINI_MODEL_NAME or BUG_HUNTER_GEMINI_MODEL_NAME: Model name (optional)
        GEMINI_TEMPERATURE or BUG_HUNTER_GEMINI_TEMPERATURE: Temperature (optional)
        GEMINI_MAX_OUTPUT_TOKENS or BUG_HUNTER_GEMINI_MAX_OUTPUT_TOKENS: Max tokens (optional)
        GEMINI_MAX_RETRIES or BUG_HUNTER_GEMINI_MAX_RETRIES: Max retries (optional)
        GEMINI_USE_FALLBACK or BUG_HUNTER_GEMINI_USE_FALLBACK: Use fallback (optional)
    """

    model_config = build_default_settings_config()

    api_key: SecretStr | None = Field(
        default=None,
        min_length=1,
        validation_alias=AliasChoices("GEMINI_API_KEY", "BUG_HUNTER_GEMINI_API_KEY"),
        description="Google Gemini API key for AI-powered issue descriptions",
    )
    model_name: str = Field(
        default="gemini-2.5-flash",
        validation_alias=AliasChoices(
            "GEMINI_MODEL_NAME", "BUG_HUNTER_GEMINI_MODEL_NAME"
        ),
        description="Gemini model name to use for generation",
    )
    temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        validation_alias=AliasChoices(
            "GEMINI_TEMPERATURE", "BUG_HUNTER_GEMINI_TEMPERATURE"
        ),
        description="Sampling temperature for response generation (0.0 to 1.0)",
    )
    max_output_tokens: int = Field(
        default=2048,
        gt=0,
        validation_alias=AliasChoices(
            "GEMINI_MAX_OUTPUT_TOKENS", "BUG_HUNTER_GEMINI_MAX_OUTPUT_TOKENS"
        ),
        description="Maximum tokens in generated output",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        validation_alias=AliasChoices(
            "GEMINI_MAX_RETRIES", "BUG_HUNTER_GEMINI_MAX_RETRIES"
        ),
        description="Maximum number of retry attempts for API calls",
    )
    use_fallback: bool = Field(
        default=True,
        validation_alias=AliasChoices(
            "GEMINI_USE_FALLBACK", "BUG_HUNTER_GEMINI_USE_FALLBACK"
        ),
        description="Whether to use fallback descriptions when AI generation fails",
    )


class VertexAIConfig(BaseSettings):
    """Vertex AI configuration.

    Environment Variables:
        VERTEXAI_PROJECT or BUG_HUNTER_VERTEXAI_PROJECT: GCP Project ID
        VERTEXAI_LOCATION or BUG_HUNTER_VERTEXAI_LOCATION: GCP Location/Region
        VERTEXAI_MODEL_NAME or BUG_HUNTER_VERTEXAI_MODEL_NAME: Model name (optional)
        VERTEXAI_TEMPERATURE or BUG_HUNTER_VERTEXAI_TEMPERATURE: Temperature (optional)
        VERTEXAI_MAX_OUTPUT_TOKENS or BUG_HUNTER_VERTEXAI_MAX_OUTPUT_TOKENS: Max tokens (optional)
        VERTEXAI_MAX_RETRIES or BUG_HUNTER_VERTEXAI_MAX_RETRIES: Max retries (optional)
        VERTEXAI_USE_FALLBACK or BUG_HUNTER_VERTEXAI_USE_FALLBACK: Use fallback (optional)
    """

    model_config = build_default_settings_config()

    project: str | None = Field(
        default=None,
        min_length=1,
        validation_alias=AliasChoices("VERTEXAI_PROJECT", "BUG_HUNTER_VERTEXAI_PROJECT"),
        description="Google Cloud Project ID for Vertex AI",
    )
    location: str = Field(
        default="us-central1",
        validation_alias=AliasChoices("VERTEXAI_LOCATION", "BUG_HUNTER_VERTEXAI_LOCATION"),
        description="Google Cloud location/region for Vertex AI",
    )
    model_name: str = Field(
        default="gemini-2.5-flash",
        validation_alias=AliasChoices(
            "VERTEXAI_MODEL_NAME", "BUG_HUNTER_VERTEXAI_MODEL_NAME"
        ),
        description="Vertex AI model name to use for generation",
    )
    temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        validation_alias=AliasChoices(
            "VERTEXAI_TEMPERATURE", "BUG_HUNTER_VERTEXAI_TEMPERATURE"
        ),
        description="Sampling temperature for response generation (0.0 to 1.0)",
    )
    max_output_tokens: int = Field(
        default=2048,
        gt=0,
        validation_alias=AliasChoices(
            "VERTEXAI_MAX_OUTPUT_TOKENS", "BUG_HUNTER_VERTEXAI_MAX_OUTPUT_TOKENS"
        ),
        description="Maximum tokens in generated output",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        validation_alias=AliasChoices(
            "VERTEXAI_MAX_RETRIES", "BUG_HUNTER_VERTEXAI_MAX_RETRIES"
        ),
        description="Maximum number of retry attempts for API calls",
    )
    use_fallback: bool = Field(
        default=True,
        validation_alias=AliasChoices(
            "VERTEXAI_USE_FALLBACK", "BUG_HUNTER_VERTEXAI_USE_FALLBACK"
        ),
        description="Whether to use fallback descriptions when AI generation fails",
    )
