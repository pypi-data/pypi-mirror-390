"""
Inference Provider SDK
Python SDK for Inference Provider V2 API
"""

from inference_provider.client import InferenceProviderClient, AsyncInferenceProviderClient
from inference_provider.errors import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    InferenceProviderError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from inference_provider.types import (
    Agent,
    AgentInferenceRequest,
    AgentInferenceResponse,
    AIModel,
    AIProvider,
    CustomResponse,
    Document,
    DocumentCollection,
    MCPServer,
    ToolDefinition,
)

__version__ = "1.0.0"

__all__ = [
    # Client
    "InferenceProviderClient",
    "AsyncInferenceProviderClient",
    # Errors
    "InferenceProviderError",
    "AuthenticationError",
    "ValidationError",
    "NotFoundError",
    "RateLimitError",
    "APIError",
    "NetworkError",
    "ConfigurationError",
    # Types
    "Agent",
    "AgentInferenceRequest",
    "AgentInferenceResponse",
    "AIProvider",
    "AIModel",
    "ToolDefinition",
    "MCPServer",
    "DocumentCollection",
    "Document",
    "CustomResponse",
]
