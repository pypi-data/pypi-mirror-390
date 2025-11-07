"""Logging configuration.

This module provides logging configuration for the exc2issue library.
"""

from typing import Literal

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings

from exc2issue.config._base import build_default_settings_config


class LoggingConfig(BaseSettings):
    """Logging configuration.

    Environment Variables:
        LOG_LEVEL or BUG_HUNTER_LOGGING_LEVEL: Log level (optional)
        LOG_FORMAT or BUG_HUNTER_LOGGING_FORMAT: Log format string (optional)
    """

    model_config = build_default_settings_config()

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="WARNING",
        validation_alias=AliasChoices("LOG_LEVEL", "BUG_HUNTER_LOGGING_LEVEL"),
        description="Log level for exc2issue internal logging",
    )
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        validation_alias=AliasChoices("LOG_FORMAT", "BUG_HUNTER_LOGGING_FORMAT"),
        description="Log message format string",
    )
