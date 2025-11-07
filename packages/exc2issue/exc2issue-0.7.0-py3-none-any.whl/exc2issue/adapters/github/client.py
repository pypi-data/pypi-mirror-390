"""Main GitHub client for exc2issue.

This module provides the main GitHubClient class for interacting with the GitHub
API to create issues automatically when errors are detected.
"""

import logging
from typing import TYPE_CHECKING, Any, Callable

from pydantic import HttpUrl, SecretStr, TypeAdapter

from exc2issue.config import GitHubConfig
from exc2issue.core.models import ErrorRecord, GitHubIssue
from exc2issue.types import IssueCreationOptions

from ._auth_manager import AuthenticationManager
from ._issue_creation import IssueCreationRequest, create_issue_with_retry
from ._issue_formatting import convert_error_collection_to_issue, convert_error_to_issue
from ._search import (
    GitHubSearchParams,
    has_existing_open_issue,
    search_existing_issues,
)

if TYPE_CHECKING:
    from exc2issue.core.error_collection import ErrorCollection

logger = logging.getLogger(__name__)


class GitHubClient:
    """Client for interacting with the GitHub API.

    This client is a thin coordinator that delegates to specialized helpers:
    - Authentication management via AuthenticationManager
    - Issue creation with retry via create_issue_with_retry
    - Issue formatting via convert_error_to_issue / convert_error_collection_to_issue
    - Issue search via search_existing_issues / has_existing_open_issue

    Supports both Personal Access Token (PAT) and GitHub App authentication.
    GitHub App authentication is preferred when both are configured.

    Attributes:
        config: GitHub configuration settings
        base_url: Base URL for GitHub API (supports GitHub Enterprise)
    """

    def __init__(
        self,
        token: str | None = None,
        base_url: str = "https://api.github.com",
        *,
        config: GitHubConfig | None = None,
        installation_token_fetcher: Callable | None = None,
    ):
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token. If None, will try to read from
                  GITHUB_TOKEN environment variable or use GitHub App credentials.
            base_url: Base URL for GitHub API. Defaults to public GitHub.
            config: GitHub configuration settings (keyword-only, advanced usage).
            installation_token_fetcher: Optional override for token fetching (for testing).

        Raises:
            ValueError: If no authentication method is provided or configured.
        """
        # Priority order: config > parameters > env vars
        if config is not None:
            self.config = config
        elif token is not None:
            # Create config from parameters (PAT-based)
            base_url_value = TypeAdapter(HttpUrl).validate_python(base_url)
            self.config = GitHubConfig(
                token=SecretStr(token), base_url=base_url_value
            )
        else:
            # Use GitHubConfig to load from environment variables (including .env file)
            base_url_value = TypeAdapter(HttpUrl).validate_python(base_url)
            self.config = GitHubConfig(base_url=base_url_value)

        self.base_url = self.config.base_url

        # Delegate authentication management to AuthenticationManager
        self._auth_manager = AuthenticationManager(
            self.config, installation_token_fetcher
        )

    @property
    def auth_manager(self) -> AuthenticationManager:
        """Return the authentication manager in a controlled, public way."""
        return self._auth_manager

    def _build_search_params(self) -> GitHubSearchParams:
        """Create search parameters reflecting the current authentication state."""
        token, use_bearer = self._auth_manager.get_current_token()
        return GitHubSearchParams(
            base_url=str(self.base_url),
            token=token,
            use_bearer=use_bearer,
            allow_private_hosts=self.config.allow_private_hosts,
        )

    @classmethod
    def from_config(cls, config: GitHubConfig) -> "GitHubClient":
        """Create GitHubClient from GitHubConfig.

        Args:
            config: GitHub configuration settings

        Returns:
            GitHubClient: Configured client instance
        """
        return cls(config=config)

    def create_issue(
        self, repository: str, issue: GitHubIssue, max_retries: int = 3
    ) -> dict[str, Any]:
        """Create a GitHub issue with retry mechanism.

        Delegates to create_issue_with_retry helper for the actual HTTP request.

        Args:
            repository: Repository in format "owner/repo"
            issue: GitHubIssue object with issue details
            max_retries: Maximum number of retry attempts for transient failures

        Returns:
            Dictionary containing GitHub API response with issue details

        Raises:
            ValueError: If repository format is invalid
            HTTPError: If all retry attempts fail or client error (4xx) occurs
            RequestException: If network request fails after all retries
        """
        token, use_bearer = self._auth_manager.get_current_token()

        request = IssueCreationRequest(
            base_url=str(self.base_url),
            repository=repository,
            token=token,
            use_bearer=use_bearer,
            timeout=self.config.timeout,
            allow_private_hosts=self.config.allow_private_hosts,
        )

        return create_issue_with_retry(
            request=request,
            issue=issue,
            max_retries=max_retries,
        )

    def convert_error_to_issue(
        self,
        error_record: ErrorRecord,
        labels: list[str],
        assignees: list[str] | None = None,
    ) -> GitHubIssue:
        """Convert ErrorRecord to GitHubIssue.

        Args:
            error_record: ErrorRecord containing error details
            labels: List of labels to apply to the issue
            assignees: List of GitHub usernames to assign the issue to

        Returns:
            GitHubIssue object ready for creation
        """
        return convert_error_to_issue(error_record, labels, assignees)

    def search_existing_issues(
        self, repository: str, title: str, max_results: int = 10
    ) -> list[dict[str, Any]]:
        """Search for existing open issues with the specified title.

        Delegates to search_existing_issues helper for the actual search logic.

        Args:
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
        return search_existing_issues(
            self._build_search_params(), repository, title, max_results
        )

    def has_existing_open_issue(self, repository: str, title: str) -> bool:
        """Check if an open issue with the specified title already exists.

        Delegates to has_existing_open_issue helper for the actual check.

        Args:
            repository: Repository in format "owner/repo"
            title: Issue title to search for

        Returns:
            True if at least one open issue with the exact title exists, False otherwise

        Note:
            Returns False on any search error to ensure issue creation can proceed
            as a fallback behavior.
        """
        return has_existing_open_issue(
            self._build_search_params(), repository, title
        )

    def create_consolidated_issue(
        self,
        repository: str,
        error_collection: "ErrorCollection",
        options: IssueCreationOptions,
    ) -> dict[str, Any]:
        """Create a consolidated GitHub issue from an error collection.

        Args:
            repository: Repository in format "owner/repo"
            error_collection: Collection of errors from a single function execution
            options: Issue creation options (labels, assignees, Gemini description)

        Returns:
            Dictionary containing GitHub API response with issue details

        Raises:
            ValueError: If repository format is invalid or no errors in collection
            HTTPError: If GitHub API returns an error
            RequestException: If network request fails
        """

        if not error_collection.has_errors():
            raise ValueError("Cannot create issue from empty error collection")

        # Generate consolidated issue
        consolidated_issue = convert_error_collection_to_issue(
            error_collection=error_collection,
            labels=options.labels,
            assignees=options.assignees,
            gemini_description=options.gemini_description,
        )

        # Create the issue using existing logic
        return self.create_issue(repository, consolidated_issue)
