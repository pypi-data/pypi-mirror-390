"""API utilities for the GitHub client.

This module contains helper functions for GitHub API interactions,
including header generation and request handling.
"""


def get_headers(token: str, use_bearer: bool = False) -> dict[str, str]:
    """Get HTTP headers for GitHub API requests.

    Args:
        token: GitHub access token (PAT or installation token)
        use_bearer: Whether to use Bearer auth format (required for GitHub App
                   installation tokens). PATs use "token" prefix.

    Returns:
        Dictionary of HTTP headers

    Note:
        GitHub App installation access tokens require the "Bearer" prefix
        for REST API calls. Personal Access Tokens (PATs) use the "token" prefix.
        See the GitHub docs for details:
        https://docs.github.com/en/apps/creating-github-apps/
        authenticating-with-a-github-app/authenticating-as-a-github-app-installation
    """
    # Use Bearer format for GitHub App installation tokens, token format for PATs
    auth_prefix = "Bearer" if use_bearer else "token"
    return {
        "Authorization": f"{auth_prefix} {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        "User-Agent": "exc2issue-client/1.0",
    }
