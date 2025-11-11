"""Configuration management for AgentWorks SDK."""


from pydantic_settings import BaseSettings


class SDKConfig(BaseSettings):
    """SDK configuration."""

    # Ingest endpoint
    ingest_endpoint: str = "http://localhost:8080"
    ingest_format: str = "json"  # json or otlp

    # Authentication
    api_key: str | None = None
    org_id: str = "dev-org"
    project_id: str = "default"

    # PII detection
    redact_pii: bool = True
    pii_patterns: str = "email,phone,ssn,credit_card,api_key"

    # Sampling
    sample_rate: float = 1.0

    # Performance
    batch_size: int = 10
    flush_interval: float = 5.0

    # Debug
    debug: bool = False

    class Config:
        """Pydantic config."""
        env_prefix = "AGENTWORKS_"


# Global config instance
_config = SDKConfig()


def configure(**kwargs: str | float | bool | None) -> None:
    """
    Configure AgentWorks SDK.

    Args:
        **kwargs: Configuration parameters matching SDKConfig fields

    Example:
        configure(
            ingest_endpoint="https://api.agentworks.dev",
            api_key="aw_1234567890",
            org_id="my-org",
            project_id="my-project",
        )
    """
    global _config

    for key, value in kwargs.items():
        if hasattr(_config, key):
            setattr(_config, key, value)


def get_config() -> SDKConfig:
    """Get current SDK configuration."""
    return _config

