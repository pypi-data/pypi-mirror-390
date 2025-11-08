"""
Huitzo SDK - Developer SDK for Huitzo WebCLI Platform Tools.

This package provides a Python SDK for interacting with Huitzo Developer Tools:
- CRON Scheduling Service: Schedule and manage recurring command executions
- Email Service: Send emails and manage templates
- LLM Completions Service: Generate text completions using various LLM providers
- Static Site Hosting Service: Deploy temporary static sites from .zip archives

Usage:
    ```python
    from huitzo_sdk import HuitzoTools

    async with HuitzoTools(api_token="your_token") as sdk:
        # Schedule a CRON job
        job = await sdk.cron.schedule(
            name="daily_report",
            command="finance.report.generate",
            schedule="0 9 * * *",
            timezone="UTC"
        )

        # Send an email
        await sdk.email.send(
            recipient_user_id="user-uuid",
            subject="Report Ready",
            html_body="<p>Your report is ready!</p>"
        )

        # Generate LLM completion
        result = await sdk.llm.complete(
            prompt="Explain quantum computing in 2 sentences",
            model="gpt-4o-mini"
        )

        # Deploy a static site
        site = await sdk.sites.deploy(
            zip_file_path="./dist.zip",
            project_name="my-portfolio",
            expiration_minutes=2880
        )
    ```

Main Classes:
    - HuitzoTools: Main SDK client with async context manager support
    - CronClient: CRON Scheduling Service client
    - EmailClient: Email Service client
    - LLMClient: LLM Completions Service client
    - SitesClient: Static Site Hosting Service client

Exceptions:
    - HuitzoAPIError: Base exception for all API errors
    - AuthenticationError: 401/403 authentication failures
    - NotFoundError: 404 resource not found
    - RateLimitError: 429 rate limit exceeded
    - ValidationError: 400 validation errors
    - QuotaExceededError: 403 quota limits exceeded
"""

__version__ = "1.0.0"

from .client import HuitzoTools
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

__all__ = [
    # Main client
    "HuitzoTools",
    # Service clients
    "CronClient",
    "EmailClient",
    "LLMClient",
    "SitesClient",
    # Exceptions
    "HuitzoAPIError",
    "AuthenticationError",
    "NotFoundError",
    "QuotaExceededError",
    "RateLimitError",
    "ValidationError",
    # Version
    "__version__",
]
