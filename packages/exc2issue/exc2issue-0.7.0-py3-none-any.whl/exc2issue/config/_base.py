"""Shared configuration defaults for exc2issue settings models."""

from __future__ import annotations

from pydantic_settings import SettingsConfigDict


def build_default_settings_config() -> SettingsConfigDict:
    """Return the default settings configuration used across settings classes."""

    return SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


__all__ = ["build_default_settings_config"]
