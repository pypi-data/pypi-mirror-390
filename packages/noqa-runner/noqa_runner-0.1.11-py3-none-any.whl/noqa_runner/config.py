"""Runner settings"""

from __future__ import annotations

import sentry_sdk
from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration


class NoqaSettings(BaseSettings):
    """Base settings class with common configurations"""

    ENVIRONMENT: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")
    SENTRY_DSN: str | None = Field(default=None)

    model_config = ConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


class RunnerSettings(NoqaSettings):
    """Settings for remote runner"""

    # Agent API configuration
    AGENT_API_URL: str = Field(
        default="https://agent.noqa.ai", description="Base URL for the agent API"
    )
    DEFAULT_APPIUM_URL: str = Field(
        default="http://localhost:4723",
        description="Default Appium URL for the agent API",
    )


settings = RunnerSettings()


def sentry_init(
    dsn: str | None = None, environment: str = "development", enable_logs: bool = False
):
    """Initialize Sentry. Logging is automatically captured via stdlib logging."""
    if not dsn:
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        traces_sample_rate=0.1,
        enable_logs=enable_logs,
        integrations=[FastApiIntegration(), AsyncioIntegration()],
    )
