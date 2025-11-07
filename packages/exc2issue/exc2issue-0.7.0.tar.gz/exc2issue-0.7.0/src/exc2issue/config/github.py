"""GitHub API configuration.

This module provides GitHub-specific configuration management including
support for both Personal Access Token (PAT) and GitHub App authentication.
"""

from pathlib import Path

from pydantic import AliasChoices, Field, HttpUrl, SecretStr, field_validator
from pydantic_settings import BaseSettings

from exc2issue.adapters.github._url_validation import validate_url_against_ssrf
from exc2issue.config._base import build_default_settings_config


class GitHubConfig(BaseSettings):
    """GitHub API configuration.

    Environment Variables:
        GITHUB_TOKEN or BUG_HUNTER_GITHUB_TOKEN: GitHub personal access token
        GITHUB_URL or BUG_HUNTER_GITHUB_BASE_URL: GitHub API base URL (optional)
        GITHUB_APP_ID or BUG_HUNTER_GITHUB_APP_ID: GitHub App ID (optional)
        GITHUB_APP_PRIVATE_KEY or BUG_HUNTER_GITHUB_APP_PRIVATE_KEY: GitHub App private key (optional)
        GITHUB_APP_INSTALLATION_ID or BUG_HUNTER_GITHUB_APP_INSTALLATION_ID: GitHub App installation ID (optional)
    """

    model_config = build_default_settings_config()

    token: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices("token", "GITHUB_TOKEN", "BUG_HUNTER_GITHUB_TOKEN"),
        description="GitHub personal access token for API authentication",
    )

    @field_validator("token", mode="before")
    @classmethod
    def reject_empty_token(cls, v: str | SecretStr | None) -> SecretStr | None:
        """Reject empty string tokens while allowing None.

        Args:
            v: Token value from environment or config

        Returns:
            SecretStr containing the token, or None if input is None

        Raises:
            ValueError: If token is an empty string
        """
        if v is None:
            return None

        # Extract string value if SecretStr
        if isinstance(v, SecretStr):
            token_str = v.get_secret_value()
        else:
            token_str = str(v)

        # Reject empty or whitespace-only tokens
        if not token_str.strip():
            raise ValueError("GitHub token cannot be empty")

        return SecretStr(token_str) if isinstance(v, str) else v

    base_url: HttpUrl = Field(
        default=HttpUrl("https://api.github.com"),
        validation_alias=AliasChoices("GITHUB_URL", "BUG_HUNTER_GITHUB_BASE_URL"),
        description="GitHub API base URL (for GitHub Enterprise support)",
    )
    app_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("app_id", "GITHUB_APP_ID", "BUG_HUNTER_GITHUB_APP_ID"),
        description="GitHub App ID for GitHub App authentication",
    )
    app_private_key: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "app_private_key", "GITHUB_APP_PRIVATE_KEY", "BUG_HUNTER_GITHUB_APP_PRIVATE_KEY"
        ),
        description="GitHub App private key (PEM format) for authentication",
    )
    app_installation_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "app_installation_id", "GITHUB_APP_INSTALLATION_ID", "BUG_HUNTER_GITHUB_APP_INSTALLATION_ID"
        ),
        description="GitHub App installation ID for authentication",
    )
    allow_pat_fallback: bool = Field(
        default=True,
        validation_alias=AliasChoices(
            "allow_pat_fallback", "GITHUB_ALLOW_PAT_FALLBACK", "BUG_HUNTER_GITHUB_ALLOW_PAT_FALLBACK"
        ),
        description="Allow fallback to PAT if GitHub App authentication fails (default: True)",
    )
    timeout: int = Field(
        default=30,
        gt=0,
        validation_alias=AliasChoices(
            "timeout", "GITHUB_TIMEOUT", "BUG_HUNTER_GITHUB_TIMEOUT"
        ),
        description="API request timeout in seconds (default: 30)",
    )
    allow_private_hosts: bool = Field(
        default=False,
        validation_alias=AliasChoices(
            "allow_private_hosts", "GITHUB_ALLOW_PRIVATE_HOSTS", "BUG_HUNTER_GITHUB_ALLOW_PRIVATE_HOSTS"
        ),
        description="Allow GitHub Enterprise or custom GitHub hosts (default: False). "
                    "When False, only api.github.com and github.com are permitted (SSRF protection).",
    )

    @field_validator("base_url", mode="after")
    @classmethod
    def validate_base_url_ssrf(cls, v: HttpUrl, info) -> HttpUrl:
        """Validate base_url to prevent SSRF attacks.

        Args:
            v: Base URL value after HttpUrl validation
            info: Validation context containing other field values

        Returns:
            The validated HttpUrl

        Raises:
            SSRFProtectionError: If the URL fails SSRF validation
        """
        # Get allow_private_hosts from the current validation context
        # Default to False if not yet set
        allow_private_hosts = info.data.get("allow_private_hosts", False)

        # Validate against SSRF
        validate_url_against_ssrf(str(v), allow_private_hosts=allow_private_hosts)

        return v

    @field_validator("app_private_key", mode="before")
    @classmethod
    def load_private_key(cls, v: str | SecretStr | None) -> SecretStr | None:
        """Load private key from file path or return as-is if already PEM format.

        Supports three input formats:
        1. PEM string with literal \\n characters (e.g., "-----BEGIN...\\n...\\n-----END...")
        2. Multi-line PEM string (e.g., from environment with actual newlines)
        3. File path to a .pem file

        Args:
            v: Private key as string, SecretStr, or file path

        Returns:
            SecretStr containing the private key in PEM format, or None if input is None
        """
        if v is None:
            return None

        # Extract string value if SecretStr
        if isinstance(v, SecretStr):
            key_str = v.get_secret_value()
        else:
            key_str = str(v)

        # If it looks like PEM content (starts with header), convert literal \n to actual newlines
        if key_str.strip().startswith("-----BEGIN"):
            # Handle both literal \n (from CI/CD) and actual newlines
            key_str = key_str.replace('\\n', '\n')
            return SecretStr(key_str)

        # Try to load from file path (with ~ expansion)
        try:
            key_path = Path(key_str).expanduser()
            if key_path.exists() and key_path.is_file():
                return SecretStr(key_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            # Not a valid file path, could be malformed PEM
            pass

        # Return as-is and let the JWT library handle validation
        return SecretStr(key_str)
