"""
Authentication utilities for Inference Provider SDK
"""

import os
from typing import Dict, Literal, Optional, Tuple

from inference_provider.errors import ConfigurationError


def validate_credentials(api_key: str, api_secret: str) -> None:
    """
    Validate API credentials

    Args:
        api_key: API key (starts with 'ip_' for user keys or 'ak_' for agent keys)
        api_secret: API secret

    Raises:
        ConfigurationError: If credentials are invalid
    """
    if not api_key or not isinstance(api_key, str):
        raise ConfigurationError("API key is required and must be a string")

    if not api_secret or not isinstance(api_secret, str):
        raise ConfigurationError("API secret is required and must be a string")

    # Validate API key format
    if not api_key.startswith("ip_") and not api_key.startswith("ak_"):
        raise ConfigurationError(
            'Invalid API key format. Key must start with "ip_" (user key) or "ak_" (agent key)'
        )

    # Basic length validation
    if len(api_key) < 10:
        raise ConfigurationError("API key is too short")

    if len(api_secret) < 20:
        raise ConfigurationError("API secret is too short")


def get_credentials_from_env() -> Optional[Tuple[str, str]]:
    """
    Get credentials from environment variables

    Returns:
        Tuple of (api_key, api_secret) or None if not found
    """
    api_key = os.environ.get("INFERENCE_API_KEY")
    api_secret = os.environ.get("INFERENCE_API_SECRET")

    if not api_key or not api_secret:
        return None

    return (api_key, api_secret)


def get_key_type(api_key: str) -> Literal["user", "agent"]:
    """
    Determine if API key is a user key or agent key

    Args:
        api_key: API key to check

    Returns:
        'user' or 'agent'
    """
    return "user" if api_key.startswith("ip_") else "agent"


def create_auth_headers(api_key: str, api_secret: str) -> Dict[str, str]:
    """
    Create authentication headers for API requests

    Args:
        api_key: API key
        api_secret: API secret

    Returns:
        Headers dictionary
    """
    return {
        "X-API-Key": api_key,
        "X-API-Secret": api_secret,
    }
