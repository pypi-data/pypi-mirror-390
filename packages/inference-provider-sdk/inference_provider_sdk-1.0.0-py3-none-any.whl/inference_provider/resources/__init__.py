"""
Resource clients
"""

from inference_provider.resources.agents import Agents
from inference_provider.resources.base import BaseResource
from inference_provider.resources.custom_responses import CustomResponses
from inference_provider.resources.mcp_servers import MCPServers
from inference_provider.resources.providers import Providers
from inference_provider.resources.rag import RAG
from inference_provider.resources.tools import Tools

__all__ = [
    "BaseResource",
    "Agents",
    "Providers",
    "Tools",
    "MCPServers",
    "RAG",
    "CustomResponses",
]
