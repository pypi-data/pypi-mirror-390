"""URL validation to prevent SSRF attacks.

This module provides secure URL validation by checking against an allowlist
of permitted schemes and hosts to prevent Server-Side Request Forgery (SSRF).
"""

from urllib.parse import urlparse


class SSRFProtectionError(ValueError):
    """Raised when a URL fails SSRF protection validation."""


# Allowlist of permitted schemes
ALLOWED_SCHEMES = {"https", "http"}

# Allowlist of permitted hosts (GitHub API endpoints)
ALLOWED_HOSTS = {
    "api.github.com",  # GitHub.com API
    "github.com",  # GitHub.com (for redirects)
}


def validate_url_against_ssrf(url: str, allow_private_hosts: bool = False) -> None:
    """Validate URL to prevent SSRF attacks.

    This function validates URLs against an allowlist of schemes and hosts
    to prevent Server-Side Request Forgery (SSRF) attacks where user-controlled
    URLs could be used to access internal services or cloud metadata endpoints.

    Args:
        url: The URL to validate
        allow_private_hosts: If True, allows GitHub Enterprise domains.
                           If False (default), only allows public GitHub API.

    Raises:
        SSRFProtectionError: If the URL scheme or host is not in the allowlist

    Security considerations:
        - Only HTTPS and HTTP schemes are allowed
        - By default, only api.github.com and github.com are allowed
        - GitHub Enterprise support requires allow_private_hosts=True
        - This prevents access to:
          * Cloud metadata endpoints (169.254.169.254, etc.)
          * Internal network addresses
          * Localhost and loopback addresses
          * File:// and other dangerous schemes
    """
    parsed = urlparse(url)

    # Validate scheme
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise SSRFProtectionError(
            f"URL scheme '{parsed.scheme}' is not allowed. "
            f"Only {ALLOWED_SCHEMES} are permitted."
        )

    # Validate hostname
    hostname = parsed.hostname
    if not hostname:
        raise SSRFProtectionError("URL must have a valid hostname")

    # For public GitHub, enforce strict allowlist
    if not allow_private_hosts:
        if hostname not in ALLOWED_HOSTS:
            raise SSRFProtectionError(
                f"Host '{hostname}' is not in the allowlist. "
                f"Only {ALLOWED_HOSTS} are permitted. "
                "For GitHub Enterprise, set GITHUB_ALLOW_PRIVATE_HOSTS=true"
            )
        return

    # For GitHub Enterprise, perform additional security checks
    _validate_private_host_safety(hostname)


def _validate_private_host_safety(hostname: str) -> None:
    """Validate that a private host is not a dangerous internal address.

    Args:
        hostname: The hostname to validate

    Raises:
        SSRFProtectionError: If the hostname appears to be an internal or dangerous address
    """
    hostname_lower = hostname.lower()

    # Block localhost and loopback addresses
    if hostname_lower in {"localhost", "127.0.0.1", "::1", "0.0.0.0"}:
        raise SSRFProtectionError(
            f"Host '{hostname}' is not allowed (localhost/loopback)"
        )

    # Block link-local addresses (cloud metadata endpoints)
    if hostname_lower.startswith("169.254.") or hostname_lower.startswith("fe80:"):
        raise SSRFProtectionError(
            f"Host '{hostname}' is not allowed (link-local address)"
        )

    # Block private network ranges (RFC 1918)
    if (
        hostname_lower.startswith("10.")
        or hostname_lower.startswith("192.168.")
        or hostname_lower.startswith("172.")
    ):
        # For 172.x.x.x, we should check if it's in 172.16-31 range
        # but for simplicity, we'll warn about all 172.x addresses
        raise SSRFProtectionError(
            f"Host '{hostname}' appears to be a private network address"
        )

    # Block common metadata endpoints
    metadata_endpoints = {
        "metadata.google.internal",
        "169.254.169.254",
        "metadata.azure.com",
    }
    if hostname_lower in metadata_endpoints:
        raise SSRFProtectionError(
            f"Host '{hostname}' is not allowed (cloud metadata endpoint)"
        )
