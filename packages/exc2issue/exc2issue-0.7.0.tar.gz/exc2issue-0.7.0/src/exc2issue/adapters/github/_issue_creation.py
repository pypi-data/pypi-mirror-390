"""GitHub issue creation with retry logic.

This module handles the actual HTTP requests to create GitHub issues,
including intelligent retry logic with exponential backoff for transient failures.
"""

from dataclasses import dataclass
import logging
import time
from typing import Any

import requests
from requests.exceptions import HTTPError

from exc2issue.core.models import GitHubIssue

from ._api_utils import get_headers
from ._sanitization import sanitize_issue_data
from ._url_validation import validate_url_against_ssrf
from ._validation import validate_repository_format

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IssueCreationRequest:
    """Bundle API details required to create a GitHub issue."""

    base_url: str
    repository: str
    token: str
    use_bearer: bool
    timeout: int = 30
    allow_private_hosts: bool = False

    def issue_endpoint(self) -> str:
        """Return the fully qualified issues endpoint URL.

        Raises:
            SSRFProtectionError: If the base_url fails SSRF validation
        """
        # Validate URL to prevent SSRF (defense in depth)
        validate_url_against_ssrf(self.base_url, allow_private_hosts=self.allow_private_hosts)

        base = self.base_url.rstrip("/")
        return f"{base}/repos/{self.repository}/issues"


def create_issue_with_retry(
    request: IssueCreationRequest,
    issue: GitHubIssue,
    max_retries: int = 3,
) -> dict[str, Any]:
    """Create a GitHub issue with retry mechanism.

    Automatically retries on transient failures (5xx errors, network issues)
    with exponential backoff. Does not retry on client errors (4xx).

    Args:
        request: Issue creation request metadata
        issue: GitHubIssue object with issue details
        max_retries: Maximum number of retry attempts for transient failures

    Returns:
        Dictionary containing GitHub API response with issue details

    Raises:
        ValueError: If repository format is invalid
        HTTPError: If all retry attempts fail or client error (4xx) occurs
        RequestException: If network request fails after all retries
    """
    validate_repository_format(request.repository)

    # Sanitize and prepare issue data
    issue_data = sanitize_issue_data(issue)

    url = request.issue_endpoint()
    headers = get_headers(request.token, use_bearer=request.use_bearer)

    for attempt in range(max_retries):
        try:
            response = requests.post(
                url, headers=headers, json=issue_data, timeout=request.timeout
            )
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]
        except HTTPError as e:
            # Don't retry for client errors (4xx)
            if e.response and 400 <= e.response.status_code < 500:
                raise

            if attempt == max_retries - 1:
                raise

            # Exponential backoff for server errors (5xx) and other transient issues
            wait_time = 2**attempt
            logger.debug(
                "HTTP error on attempt %d/%d, retrying in %ds: %s",
                attempt + 1, max_retries, wait_time, e
            )
            time.sleep(wait_time)
        except (requests.RequestException, ValueError, OSError, ConnectionError) as e:
            # For non-HTTP exceptions (network issues, timeouts, etc.)
            if attempt == max_retries - 1:
                raise

            # Exponential backoff
            wait_time = 2**attempt
            logger.debug(
                "Request error on attempt %d/%d, retrying in %ds: %s",
                attempt + 1, max_retries, wait_time, e
            )
            time.sleep(wait_time)

    # This should never be reached, but just in case
    raise HTTPError("All retry attempts failed")
