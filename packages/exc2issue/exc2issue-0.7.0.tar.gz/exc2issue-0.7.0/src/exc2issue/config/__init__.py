"""Configuration management for exc2issue using Pydantic Settings.

This module provides simple configuration management for the exc2issue library.
Each component (GitHub, Google AI, Logging) has its own BaseSettings class with
proper environment variable prefixes and aliases for flexibility.
"""

from .github import GitHubConfig
from .google_ai import GeminiConfig, VertexAIConfig
from .logging import LoggingConfig

__all__ = ["GitHubConfig", "GeminiConfig", "VertexAIConfig", "LoggingConfig"]
