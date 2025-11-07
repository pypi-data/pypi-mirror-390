"""GitHub authentication lifecycle management.

This module manages the complete lifecycle of GitHub authentication including:
- GitHub App authentication with installation tokens
- Personal Access Token (PAT) fallback
- Token refresh and expiration handling
- Retry logic for transient auth failures
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Callable

import requests

from exc2issue.config import GitHubConfig

from ._app_auth import get_installation_token

logger = logging.getLogger(__name__)


class AuthenticationManager:
    """Manages GitHub authentication lifecycle.

    Handles both GitHub App authentication (with automatic token refresh)
    and Personal Access Token authentication with intelligent fallback logic.

    Attributes:
        config: GitHub configuration settings
        token: Current authentication token (App installation token or PAT)
        use_bearer_auth: Whether to use Bearer authentication (App) vs token (PAT)
        token_expires_at: Expiration datetime for App tokens (None for PAT)
    """

    APP_AUTH_RETRY_COOLDOWN = timedelta(minutes=5)

    def __init__(
        self,
        config: GitHubConfig,
        installation_token_fetcher: Callable[[str, str, str, str, int], tuple[str, datetime]] | None = None,
    ):
        """Initialize authentication manager.

        Args:
            config: GitHub configuration settings
            installation_token_fetcher: Optional override for token fetching (for testing)

        Raises:
            ValueError: If no authentication method is configured
        """
        self.config = config
        self._installation_token_fetcher = installation_token_fetcher

        # Authentication state
        self.token: str
        self.use_bearer_auth: bool
        self.token_expires_at: datetime | None = None
        self._app_auth_failed_at: datetime | None = None

        # Initialize authentication
        self._initialize_authentication()

    @property
    def app_auth_failure_time(self) -> datetime | None:
        """Return the timestamp of the most recent App authentication failure."""
        return self._app_auth_failed_at

    def set_app_auth_failure_time(self, timestamp: datetime | None) -> None:
        """Manually adjust the stored App authentication failure timestamp."""
        self._app_auth_failed_at = timestamp

    def _initialize_authentication(self) -> None:
        """Initialize authentication using available credentials.

        Prefers GitHub App authentication if configured, falls back to PAT.

        Raises:
            ValueError: If no valid authentication method is available
        """
        # Prefer GitHub App authentication if configured
        if self._has_app_config():
            try:
                self.token, self.token_expires_at = self._get_app_installation_token()
                self.use_bearer_auth = True
                logger.info("GitHub App authentication initialized successfully")
            except (requests.RequestException, ValueError) as exc:
                # If App auth fails and PAT is available, fall back to PAT
                if self.config.token is not None and self.config.allow_pat_fallback:
                    logger.warning(
                        "GitHub App authentication failed, falling back to PAT: %s",
                        exc
                    )
                    self.token = self.config.token.get_secret_value()
                    self.use_bearer_auth = False
                    self.token_expires_at = None
                    self._app_auth_failed_at = datetime.now(timezone.utc)
                elif self.config.token is not None and not self.config.allow_pat_fallback:
                    raise ValueError(
                        "GitHub App authentication failed and PAT fallback is disabled. "
                        f"Enable allow_pat_fallback or fix App configuration. Error: {exc}"
                    ) from exc
                else:
                    raise ValueError(
                        "GitHub App authentication failed and no PAT available: "
                        f"{exc}"
                    ) from exc
        elif self.config.token is not None:
            # Use PAT authentication
            self.token = self.config.token.get_secret_value()
            self.use_bearer_auth = False
            self.token_expires_at = None
            logger.info("PAT authentication initialized")
        else:
            raise ValueError(
                "GitHub authentication required. Provide either a token "
                "(GITHUB_TOKEN) or GitHub App credentials (GITHUB_APP_ID, "
                "GITHUB_APP_PRIVATE_KEY, GITHUB_APP_INSTALLATION_ID)."
            )

    def _has_app_config(self) -> bool:
        """Check if GitHub App configuration is present.

        Returns:
            True if all required App config fields are present
        """
        return bool(
            self.config.app_id
            and self.config.app_private_key
            and self.config.app_installation_id
        )

    def _get_app_installation_token(self) -> tuple[str, datetime]:
        """Get installation token using GitHub App credentials.

        Returns:
            Tuple of (installation access token, expiration datetime)

        Raises:
            ValueError: If token acquisition fails
        """
        app_id = self.config.app_id
        private_key = self.config.app_private_key
        installation_id = self.config.app_installation_id

        if (
            app_id is None
            or private_key is None
            or installation_id is None
        ):
            raise ValueError("GitHub App configuration is incomplete")

        fetch_installation_token = self._installation_token_fetcher or get_installation_token
        return fetch_installation_token(
            str(self.config.base_url),
            str(app_id),
            private_key.get_secret_value(),
            str(installation_id),
            self.config.timeout,
        )

    def _is_token_expired(self) -> bool:
        """Check if the current token is expired or will expire soon.

        Returns:
            True if token is expired or will expire within 5 minutes
        """
        if self.token_expires_at is None:
            # PAT tokens don't expire
            return False

        # Consider token expired if it expires within 5 minutes
        buffer = timedelta(minutes=5)
        return datetime.now(timezone.utc) >= (self.token_expires_at - buffer)

    def _should_retry_app_auth(self) -> bool:
        """Check if we should retry App authentication after a previous failure.

        Returns:
            True if cooldown period has passed and retry should be attempted
        """
        if self._app_auth_failed_at is None:
            return False

        time_since_failure = datetime.now(timezone.utc) - self._app_auth_failed_at
        return time_since_failure >= self.APP_AUTH_RETRY_COOLDOWN

    def refresh_if_needed(self) -> None:
        """Refresh the installation token if it's expired or about to expire.

        Also retries App authentication after cooldown period if previously failed.
        Falls back to PAT if refresh fails and PAT is configured.
        """
        # If using PAT and we should retry App auth, attempt it
        if not self.use_bearer_auth and self._should_retry_app_auth() and self._has_app_config():
            try:
                logger.info("Retrying GitHub App authentication after cooldown period")
                self.token, self.token_expires_at = self._get_app_installation_token()
                self.use_bearer_auth = True
                self._app_auth_failed_at = None  # Clear failure timestamp
                logger.info("GitHub App authentication retry successful")
                return
            except (requests.RequestException, ValueError) as exc:
                logger.debug("GitHub App authentication retry failed: %s", exc)
                # Update failure timestamp and continue with PAT
                self._app_auth_failed_at = datetime.now(timezone.utc)

        # If not using bearer auth, nothing to refresh
        if not self.use_bearer_auth or not self._is_token_expired():
            return

        # Token is expired or about to expire, try to refresh
        if self._has_app_config():
            try:
                logger.debug("Refreshing expired GitHub App installation token")
                self.token, self.token_expires_at = self._get_app_installation_token()
                self.use_bearer_auth = True
                self._app_auth_failed_at = None  # Clear any previous failure
                logger.info("GitHub App token refreshed successfully")
            except (requests.RequestException, ValueError) as exc:
                # Refresh failed, fall back to PAT if available and allowed
                if self.config.token is not None and self.config.allow_pat_fallback:
                    logger.warning(
                        "GitHub App token refresh failed, falling back to PAT: %s",
                        exc
                    )
                    self.token = self.config.token.get_secret_value()
                    self.use_bearer_auth = False
                    self.token_expires_at = None
                    self._app_auth_failed_at = datetime.now(timezone.utc)
                elif self.config.token is not None and not self.config.allow_pat_fallback:
                    logger.error("GitHub App token refresh failed and PAT fallback is disabled")
                    raise ValueError(
                        "GitHub App token refresh failed and PAT fallback is disabled. "
                        f"Error: {exc}"
                    ) from exc
                else:
                    # No fallback available, re-raise the exception
                    logger.error("GitHub App token refresh failed and no PAT available")
                    raise

    def get_current_token(self) -> tuple[str, bool]:
        """Get the current authentication token and auth type.

        Automatically refreshes token if needed before returning.

        Returns:
            Tuple of (token, use_bearer_auth)
        """
        self.refresh_if_needed()
        return self.token, self.use_bearer_auth
