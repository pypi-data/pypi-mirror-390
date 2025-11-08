"""
Main Inference Provider Client
"""

from typing import Optional

from inference_provider.auth import get_credentials_from_env, validate_credentials
from inference_provider.errors import ConfigurationError
from inference_provider.http_client import AsyncHttpClient, HttpClient
from inference_provider.resources.agents import Agents
from inference_provider.resources.custom_responses import CustomResponses
from inference_provider.resources.mcp_servers import MCPServers
from inference_provider.resources.providers import Providers
from inference_provider.resources.rag import RAG
from inference_provider.resources.tools import Tools

DEFAULT_BASE_URL = "https://jurqxbgcbagakcikzhpe.supabase.co"


class InferenceProviderClient:
    """
    Main client for Inference Provider API

    Example:
        ```python
        # Initialize client
        client = InferenceProviderClient(
            api_key="ip_xxxxxxxxxx",
            api_secret="xxxxxxxxxxxxxx"
        )

        # Run agent inference
        response = client.agents.run(
            agent_id="agent-id",
            user_message="Hello, world!"
        )

        print(response.response)
        ```
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        debug: bool = False,
    ):
        """
        Create a new Inference Provider client

        Args:
            api_key: API key (or set INFERENCE_API_KEY env var)
            api_secret: API secret (or set INFERENCE_API_SECRET env var)
            base_url: Base URL for API (default: production)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            debug: Enable debug logging

        Raises:
            ConfigurationError: If credentials are invalid or missing
        """
        # Try to get credentials from config or environment
        if api_key and api_secret:
            self.api_key = api_key
            self.api_secret = api_secret
        else:
            env_credentials = get_credentials_from_env()
            if not env_credentials:
                raise ConfigurationError(
                    "API credentials not provided. "
                    "Either pass api_key and api_secret to the constructor, "
                    "or set INFERENCE_API_KEY and INFERENCE_API_SECRET environment variables."
                )
            self.api_key, self.api_secret = env_credentials

        # Validate credentials
        validate_credentials(self.api_key, self.api_secret)

        # Store config
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.debug = debug

        # Create HTTP client
        self.http = HttpClient(
            base_url=self.base_url,
            api_key=self.api_key,
            api_secret=self.api_secret,
            timeout=self.timeout,
            max_retries=self.max_retries,
            debug=self.debug,
        )

        # Initialize resource clients
        self.agents = Agents(self.http, "/functions/v1/agent-management")
        self.providers = Providers(self.http, "/functions/v1/provider-management")
        self.tools = Tools(self.http, "/functions/v1/tool-management")
        self.mcp_servers = MCPServers(self.http, "/functions/v1/mcp-server-management")
        self.rag = RAG(self.http, "/functions/v1/rag-management")
        self.custom_responses = CustomResponses(self.http, "/functions/v1/custom-response-management")

    def __enter__(self) -> "InferenceProviderClient":
        """Context manager entry"""
        return self

    def __exit__(self, *args: any) -> None:
        """Context manager exit"""
        self.close()

    def close(self) -> None:
        """Close the client and cleanup resources"""
        self.http.close()

    def validate_credentials(self) -> bool:
        """
        Validate credentials with the API

        Returns:
            True if credentials are valid

        Raises:
            AuthenticationError: If credentials are invalid
        """
        # Try to list agents as a validation check
        self.agents.list()
        return True


class AsyncInferenceProviderClient:
    """
    Async client for Inference Provider API

    Example:
        ```python
        async with AsyncInferenceProviderClient(
            api_key="ip_xxxxxxxxxx",
            api_secret="xxxxxxxxxxxxxx"
        ) as client:
            response = await client.agents.run(
                agent_id="agent-id",
                user_message="Hello, world!"
            )
            print(response.response)
        ```
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        debug: bool = False,
    ):
        """
        Create a new async Inference Provider client

        Args:
            api_key: API key (or set INFERENCE_API_KEY env var)
            api_secret: API secret (or set INFERENCE_API_SECRET env var)
            base_url: Base URL for API (default: production)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            debug: Enable debug logging

        Raises:
            ConfigurationError: If credentials are invalid or missing
        """
        # Try to get credentials from config or environment
        if api_key and api_secret:
            self.api_key = api_key
            self.api_secret = api_secret
        else:
            env_credentials = get_credentials_from_env()
            if not env_credentials:
                raise ConfigurationError(
                    "API credentials not provided. "
                    "Either pass api_key and api_secret to the constructor, "
                    "or set INFERENCE_API_KEY and INFERENCE_API_SECRET environment variables."
                )
            self.api_key, self.api_secret = env_credentials

        # Validate credentials
        validate_credentials(self.api_key, self.api_secret)

        # Store config
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.debug = debug

        # Create async HTTP client
        self.http = AsyncHttpClient(
            base_url=self.base_url,
            api_key=self.api_key,
            api_secret=self.api_secret,
            timeout=self.timeout,
            max_retries=self.max_retries,
            debug=self.debug,
        )

        # Initialize resource clients
        # Note: These work with async HTTP client automatically
        self.agents = Agents(self.http, "/functions/v1/agent-management")
        self.providers = Providers(self.http, "/functions/v1/provider-management")
        self.tools = Tools(self.http, "/functions/v1/tool-management")
        self.mcp_servers = MCPServers(self.http, "/functions/v1/mcp-server-management")
        self.rag = RAG(self.http, "/functions/v1/rag-management")
        self.custom_responses = CustomResponses(self.http, "/functions/v1/custom-response-management")

    async def __aenter__(self) -> "AsyncInferenceProviderClient":
        """Async context manager entry"""
        return self

    async def __aexit__(self, *args: any) -> None:
        """Async context manager exit"""
        await self.close()

    async def close(self) -> None:
        """Close the client and cleanup resources"""
        await self.http.close()

    async def validate_credentials(self) -> bool:
        """
        Validate credentials with the API

        Returns:
            True if credentials are valid

        Raises:
            AuthenticationError: If credentials are invalid
        """
        # Try to list agents as a validation check
        await self.agents.list()
        return True
