"""
Main Huitzo SDK client.

This module provides the HuitzoTools class, the main entry point for the SDK.
It manages the HTTP session and provides access to CRON and Email service clients.

Usage:
    ```python
    from huitzo_sdk import HuitzoTools

    async with HuitzoTools(api_token="your_token") as sdk:
        # Use CRON service
        job = await sdk.cron.schedule(...)

        # Use Email service
        result = await sdk.email.send(...)
    ```
"""

from __future__ import annotations

import logging
from types import TracebackType
from typing import Any, Type

import aiohttp

from .cron import CronClient
from .email import EmailClient
from .llm import LLMClient
from .sites import SitesClient
from .exceptions import (
    AuthenticationError,
    HuitzoAPIError,
    NotFoundError,
    QuotaExceededError,
    RateLimitError,
    ValidationError,
)

logger = logging.getLogger(__name__)


class HuitzoTools:
    """
    Main SDK client for Huitzo Developer Tools platform.

    This class provides access to all Huitzo services through a unified interface.
    It manages HTTP sessions and authentication automatically.

    Attributes:
        cron: CronClient for CRON Scheduling Service
        email: EmailClient for Email Service
        llm: LLMClient for LLM Completions Service
        sites: SitesClient for Static Site Hosting Service
        base_url: Base URL for API requests
        api_token: API token for authentication

    Example:
        ```python
        async with HuitzoTools(api_token="your_token") as sdk:
            # Schedule a job
            job = await sdk.cron.schedule(
                name="daily_report",
                command="finance.report.generate",
                schedule="0 9 * * *",
                timezone="UTC"
            )

            # Send email
            await sdk.email.send(
                recipient_user_id="user-uuid",
                subject="Daily Report Ready",
                html_body="<p>Your report is ready!</p>"
            )
        ```
    """

    def __init__(
        self,
        api_token: str,
        base_url: str = "http://localhost:8010",
        timeout: int = 30,
    ):
        """
        Initialize HuitzoTools SDK client.

        Args:
            api_token: API token for authentication (required)
            base_url: Base URL for API requests (default: http://localhost:8010)
            timeout: Request timeout in seconds (default: 30)

        Raises:
            ValueError: If api_token is not provided
        """
        if not api_token:
            raise ValueError("api_token is required")

        self.api_token = api_token
        self.base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session: aiohttp.ClientSession | None = None

        # Initialize service clients (they will use the session from __aenter__)
        self.cron = CronClient(self)
        self.email = EmailClient(self)
        self.llm = LLMClient(self)
        self.sites = SitesClient(self)

    async def __aenter__(self) -> "HuitzoTools":
        """
        Enter async context manager.

        Creates the aiohttp ClientSession for making HTTP requests.

        Returns:
            Self for use in async with statement
        """
        # Create aiohttp session with timeout
        timeout = aiohttp.ClientTimeout(total=self._timeout)
        self._session = aiohttp.ClientSession(timeout=timeout)

        logger.debug(f"HuitzoTools session initialized (base_url={self.base_url})")
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        Exit async context manager.

        Properly closes the aiohttp ClientSession to clean up resources.

        Args:
            exc_type: Exception type (if exception occurred)
            exc_val: Exception value (if exception occurred)
            exc_tb: Exception traceback (if exception occurred)
        """
        if self._session:
            await self._session.close()
            self._session = None
            logger.debug("HuitzoTools session closed")

    def _get_headers(self) -> dict[str, str]:
        """
        Get HTTP headers for API requests.

        Returns:
            Dictionary of HTTP headers including authentication

        Raises:
            RuntimeError: If called outside async context manager
        """
        if not self._session:
            raise RuntimeError(
                "HuitzoTools must be used within async context manager: "
                "async with HuitzoTools(...) as sdk:"
            )

        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "User-Agent": "huitzo-sdk/1.0.0",
        }

    async def _handle_response(
        self,
        response: aiohttp.ClientResponse,
        expected_status: int = 200,
    ) -> Any:
        """
        Handle API response and raise appropriate exceptions.

        Args:
            response: aiohttp ClientResponse object
            expected_status: Expected HTTP status code (default: 200)

        Returns:
            Parsed JSON response (if applicable)

        Raises:
            AuthenticationError: 401/403 authentication failures
            NotFoundError: 404 resource not found
            RateLimitError: 429 rate limit exceeded
            ValidationError: 400 validation errors
            HuitzoAPIError: Other API errors
        """
        status = response.status

        # Handle successful responses
        if status == expected_status:
            # 204 No Content has no response body
            if status == 204:
                return None

            # Parse JSON response
            try:
                return await response.json()
            except Exception as e:
                logger.error(f"Failed to parse JSON response: {e}")
                raise HuitzoAPIError(
                    f"Invalid JSON response from API",
                    status_code=status,
                )

        # Handle error responses
        try:
            error_data = await response.json()
            error_message = error_data.get("detail", f"HTTP {status}")
        except Exception:
            # If JSON parsing fails, use text response
            try:
                error_message = await response.text()
            except Exception:
                error_message = f"HTTP {status}"
            error_data = {}

        # Map status codes to exceptions
        if status in (401, 403):
            raise AuthenticationError(
                message=error_message,
                status_code=status,
                response_data=error_data,
            )
        elif status == 404:
            raise NotFoundError(
                message=error_message,
                response_data=error_data,
            )
        elif status == 429:
            raise RateLimitError(
                message=error_message,
                response_data=error_data,
            )
        elif status == 400:
            raise ValidationError(
                message=error_message,
                response_data=error_data,
            )
        else:
            # Generic API error for other status codes
            raise HuitzoAPIError(
                message=error_message,
                status_code=status,
                response_data=error_data,
            )

    async def close(self) -> None:
        """
        Explicitly close the HTTP session.

        This method is provided for cases where the context manager
        cannot be used. Prefer using the async context manager when possible.

        Example:
            ```python
            sdk = HuitzoTools(api_token="your_token")
            await sdk.__aenter__()
            try:
                job = await sdk.cron.list()
            finally:
                await sdk.close()
            ```
        """
        if self._session:
            await self._session.close()
            self._session = None
            logger.debug("HuitzoTools session closed (explicit)")
