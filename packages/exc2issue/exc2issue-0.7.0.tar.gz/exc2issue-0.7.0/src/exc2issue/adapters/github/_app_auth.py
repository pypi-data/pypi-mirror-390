"""GitHub App authentication utilities.

This module provides utilities for authenticating with GitHub using a GitHub App,
including JWT generation and installation token acquisition.
"""

import time
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
import requests


def _installation_access_token_url(base_url: str, installation_id: str) -> str:
    """Return the URL for requesting an installation access token."""
    return f"{base_url.rstrip('/')}/app/installations/{installation_id}/access_tokens"


def _build_installation_headers(jwt_token: str) -> dict[str, str]:
    """Build request headers for GitHub App installation token requests."""
    return {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }


def _parse_expires_at(expires_at_str: str | None) -> datetime:
    """Parse the expires_at value returned by GitHub or provide a fallback."""
    if expires_at_str:
        return datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))

    # Fallback: assume 1 hour expiration when GitHub omits expires_at
    return datetime.now(timezone.utc) + timedelta(hours=1)


def generate_jwt(app_id: str, private_key: str, expiration_seconds: int = 600) -> str:
    """Generate a JWT for GitHub App authentication.

    Args:
        app_id: GitHub App ID
        private_key: GitHub App private key in PEM format
        expiration_seconds: JWT expiration time in seconds (default: 600, max: 600)

    Returns:
        JWT token string

    Raises:
        ValueError: If JWT generation fails or if private key is malformed
    """
    # GitHub Apps have a maximum JWT expiration of 10 minutes (600 seconds)
    expiration_seconds = min(expiration_seconds, 600)

    now = int(time.time())

    # Apply clock drift adjustment - backdate iat by 30s to account for clock skew
    # GitHub's spec caps the window at 60s, and recent implementations use 30s tolerance
    # This ensures the token is valid even with minor clock skew
    # We use min() to ensure we don't backdate more than half the expiration time
    clock_drift_buffer = min(30, expiration_seconds // 2)
    iat = now - clock_drift_buffer
    exp = now + expiration_seconds - clock_drift_buffer

    # Validate that iat is within GitHub's acceptable window (not more than 60s in the past)
    if now - iat > 60:
        raise ValueError(
            f"Clock drift buffer ({now - iat}s) exceeds GitHub's 60s maximum. "
            "This may indicate a system clock issue."
        )

    payload = {
        "iat": iat,  # Issued at time
        "exp": exp,  # Expiration time
        "iss": app_id,  # Issuer (GitHub App ID)
    }

    try:
        token = jwt.encode(payload, private_key, algorithm="RS256")
        return token
    except Exception as e:
        # Provide more helpful error message for common issues
        error_msg = str(e).lower()
        if "key" in error_msg or "pem" in error_msg or "format" in error_msg:
            raise ValueError(
                f"Failed to generate JWT - the private key appears to be malformed or invalid. "
                f"Ensure it's in valid PEM format. Original error: {e}"
            ) from e
        raise ValueError(f"Failed to generate JWT: {e}") from e


def get_installation_token(
    base_url: str,
    app_id: str,
    private_key: str,
    installation_id: str,
    timeout: int = 30
) -> tuple[str, datetime]:
    """Get an installation access token for a GitHub App.

    Args:
        base_url: GitHub API base URL
        app_id: GitHub App ID
        private_key: GitHub App private key in PEM format
        installation_id: GitHub App installation ID
        timeout: Request timeout in seconds (default: 30)

    Returns:
        Tuple of (installation access token, expiration datetime)

    Raises:
        ValueError: If token acquisition fails
        requests.HTTPError: If GitHub API returns an error
    """
    # Generate JWT for app authentication
    jwt_token = generate_jwt(app_id, private_key)

    # Request installation token
    url = _installation_access_token_url(base_url, installation_id)

    try:
        response = requests.post(
            url,
            headers=_build_installation_headers(jwt_token),
            json={},
            timeout=timeout,
        )
        response.raise_for_status()
        data: dict[str, Any] = response.json()

        # Validate token is present and not null
        token = data.get("token")
        if not token:
            raise ValueError("GitHub API returned null/empty token")

        # Parse expiration time from response
        expires_at = _parse_expires_at(data.get("expires_at"))

        return str(token), expires_at
    except requests.HTTPError as e:
        # Include response details for better troubleshooting
        error_msg = f"Failed to get installation token: HTTP {e.response.status_code if e.response else 'unknown'}"
        if e.response:
            error_msg += f" - {e.response.reason}"
        raise ValueError(error_msg) from e
    except (KeyError, ValueError) as e:
        raise ValueError(f"Invalid response from GitHub API: {e}") from e
