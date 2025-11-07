"""Search utilities for the GitHub client.

This module contains functions for searching existing GitHub issues
to prevent duplicates.
"""

import logging
from dataclasses import dataclass
from typing import Any

import requests
from requests.exceptions import HTTPError, RequestException

from ._api_utils import get_headers
from ._url_validation import validate_url_against_ssrf
from ._validation import validate_repository_format


@dataclass(frozen=True)
class GitHubSearchParams:
    """Authentication and configuration parameters for GitHub issue search."""

    base_url: str
    token: str
    use_bearer: bool = False
    allow_private_hosts: bool = False

    def normalized_base_url(self) -> str:
        """Return the base URL without a trailing slash.

        Raises:
            SSRFProtectionError: If the base_url fails SSRF validation
        """
        # Validate URL to prevent SSRF (defense in depth)
        validate_url_against_ssrf(self.base_url, allow_private_hosts=self.allow_private_hosts)

        return self.base_url.rstrip("/")


def search_existing_issues(
    params: GitHubSearchParams,
    repository: str,
    title: str,
    max_results: int = 10,
) -> list[dict[str, Any]]:
    """Search for existing open issues with the specified title.

    Uses GitHub's search API to find issues by title. Only searches for open issues
    in the specified repository to prevent creation of duplicate issues.

    Args:
        params: GitHub search parameters including auth details
        repository: Repository in format "owner/repo"
        title: Issue title to search for (exact match)
        max_results: Maximum number of results to return (default: 10)

    Returns:
        List of issue dictionaries from GitHub API, empty if no matches found

    Raises:
        HTTPError: If GitHub API returns an error
        RequestException: If network request fails

    Note:
        This method is designed to be robust - search failures should not prevent
        issue creation, so calling code should handle exceptions gracefully.
    """
    validate_repository_format(repository)

    # Construct search query for exact title match in specific repository
    # Format: "exact title" repo:owner/repo state:open type:issue
    query = " ".join(
        [
            f'"{title}"',  # Exact title match with quotes
            f"repo:{repository}",  # Specific repository
            "state:open",  # Only open issues
            "type:issue",  # Issues only, not PRs
        ]
    )

    logger = logging.getLogger(__name__)
    logger.debug("Searching for existing issues with query: %s", query)

    try:
        response = requests.get(
            f"{params.normalized_base_url()}/search/issues",
            headers=get_headers(params.token, use_bearer=params.use_bearer),
            params={
                "q": query,
                "per_page": str(min(max_results, 100)),  # GitHub API max is 100
                "page": "1",
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])

        logger.debug(
            "Found %s existing issues matching title '%s' in %s",
            data.get("total_count", 0),
            title,
            repository,
        )

        if isinstance(items, list):
            issue_list: list[dict[str, Any]] = []
            for item in items:
                if isinstance(item, dict):
                    issue_list.append(item)
            return issue_list

        return []

    except HTTPError as e:
        logger.warning(
            "GitHub API error when searching for existing issues: %s - %s",
            e.response.status_code if e.response else "unknown",
            str(e),
        )
        # Return empty list to allow issue creation as fallback
        return []

    except RequestException as e:
        logger.warning("Network error when searching for existing issues: %s", str(e))
        # Return empty list to allow issue creation as fallback
        return []

    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        logger.warning(
            "Unexpected error when searching for existing issues: %s", str(exc)
        )
        # Return empty list to allow issue creation as fallback
        return []
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.warning(
            "Unexpected error when searching for existing issues: %s", str(exc)
        )
        # Return empty list to allow issue creation as fallback
        return []


def has_existing_open_issue(
    params: GitHubSearchParams, repository: str, title: str
) -> bool:
    """Check if an open issue with the specified title already exists.

    This is a convenience method that wraps search_existing_issues to provide
    a simple boolean response for duplicate detection.

    Args:
        params: GitHub search parameters including auth details
        repository: Repository in format "owner/repo"
        title: Issue title to search for

    Returns:
        True if at least one open issue with the exact title exists, False otherwise

    Note:
        Returns False on any search error to ensure issue creation can proceed
        as a fallback behavior.
    """
    try:
        existing_issues = search_existing_issues(
            params, repository, title, max_results=1
        )
        return len(existing_issues) > 0
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        logger = logging.getLogger(__name__)
        logger.warning(
            "Error checking for existing issues, assuming none exist: %s", exc
        )
        return False
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger = logging.getLogger(__name__)
        logger.warning(
            "Unexpected error checking for existing issues, assuming none exist: %s",
            exc,
        )
        return False
