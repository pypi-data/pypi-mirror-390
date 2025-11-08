"""
Type definitions for Inference Provider SDK
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field


# ============================================================================
# Enums
# ============================================================================


class ProviderType(str, Enum):
    """AI provider types"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    TOGETHERAI = "togetherai"
    GROQ = "groq"


class ModelType(str, Enum):
    """Model types"""

    COMPLETION = "completion"
    EMBEDDING = "embedding"


class VariableType(str, Enum):
    """Variable types"""

    TEXT = "text"
    RAG_FILE = "rag_file"


class ToolType(str, Enum):
    """Tool types"""

    REST_API = "rest_api"
    JAVASCRIPT_FUNCTION = "javascript_function"
    MCP = "mcp"


class HttpMethod(str, Enum):
    """HTTP methods"""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class AuthType(str, Enum):
    """Authentication types"""

    NONE = "none"
    API_KEY = "api_key"
    BEARER = "bearer"
    OAUTH2 = "oauth2"
    BASIC = "basic"


class MCPServerType(str, Enum):
    """MCP server types"""

    STDIO = "stdio"
    SSE = "sse"
    HTTP = "http"


# ============================================================================
# Provider & Model Types
# ============================================================================


class AIProvider(BaseModel):
    """AI provider configuration"""

    id: str
    user_id: str
    name: str
    provider_type: ProviderType
    api_endpoint: str
    is_active: bool
    created_at: str
    updated_at: str


class AIModel(BaseModel):
    """AI model configuration"""

    id: str
    provider_id: str
    user_id: str
    name: str
    display_name: str
    description: Optional[str] = None
    context_window: int
    max_output_tokens: int
    input_cost_per_1k_tokens: float
    output_cost_per_1k_tokens: float
    supports_streaming: bool
    supports_function_calling: bool
    is_active: bool
    model_type: ModelType
    embedding_dimensions: Optional[int] = None
    supports_embeddings: bool
    created_at: str
    updated_at: str


# ============================================================================
# Agent Types
# ============================================================================


class Variable(BaseModel):
    """Agent variable definition"""

    name: str
    type: VariableType
    description: Optional[str] = None
    default_value: Optional[str] = None
    embedding_model_id: Optional[str] = None


class Agent(BaseModel):
    """Agent configuration"""

    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    system_prompt: str
    variables: List[Variable] = Field(default_factory=list)
    custom_response_id: Optional[str] = None
    provider_id: Optional[str] = None
    model_name: str
    temperature: float = 0.7
    max_tokens: int = 2000
    tags: List[str] = Field(default_factory=list)
    is_active: bool
    default_embedding_model_id: Optional[str] = None
    created_at: str
    updated_at: str


class MessageContent(BaseModel):
    """Message content (for multimodal messages)"""

    type: Literal["text", "image_url"]
    text: Optional[str] = None
    image_url: Optional[Dict[str, str]] = None


class ConversationMessage(BaseModel):
    """Conversation message"""

    role: Literal["user", "assistant", "system"]
    content: Union[str, List[MessageContent]]


class ImageInput(BaseModel):
    """Image input for vision models"""

    type: str
    image_url: Dict[str, str]


# ============================================================================
# Tool Types
# ============================================================================


class RetryConfig(BaseModel):
    """Retry configuration"""

    max_retries: int
    initial_delay_ms: int
    max_delay_ms: int
    backoff_multiplier: float


class AuthConfig(BaseModel):
    """Authentication configuration"""

    api_key: Optional[str] = None
    api_key_header: Optional[str] = None
    bearer_token: Optional[str] = None
    oauth_token_url: Optional[str] = None
    oauth_client_id: Optional[str] = None
    oauth_client_secret: Optional[str] = None
    basic_username: Optional[str] = None
    basic_password: Optional[str] = None


class RestApiConfig(BaseModel):
    """REST API tool configuration"""

    endpoint_url: str
    http_method: HttpMethod
    headers: Dict[str, str] = Field(default_factory=dict)
    body_template: Dict[str, Any] = Field(default_factory=dict)
    query_params: Dict[str, Any] = Field(default_factory=dict)
    auth_type: AuthType
    auth_config: AuthConfig
    timeout_ms: int
    retry_config: RetryConfig


class JavaScriptFunctionConfig(BaseModel):
    """JavaScript function tool configuration"""

    function_code: str
    runtime: Literal["deno", "node"]
    timeout_ms: int


class JSONSchema(BaseModel):
    """JSON Schema definition"""

    type: str
    properties: Optional[Dict[str, Any]] = None
    required: Optional[List[str]] = None

    class Config:
        extra = "allow"


class ToolDefinition(BaseModel):
    """Tool definition"""

    id: str
    user_id: str
    tool_name: str
    display_name: str
    description: str
    tool_type: ToolType
    version: str
    is_active: bool
    is_public: bool
    config: Dict[str, Any]
    input_schema: JSONSchema
    output_schema: JSONSchema
    tags: List[str] = Field(default_factory=list)
    created_at: str
    updated_at: str


# ============================================================================
# MCP Types
# ============================================================================


class MCPServer(BaseModel):
    """MCP server configuration"""

    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    server_type: MCPServerType
    connection_config: Any
    auth_type: AuthType
    auth_config: Optional[Any] = None
    is_active: bool
    last_sync_at: Optional[str] = None
    last_sync_status: Optional[str] = None
    metadata: Optional[Any] = None
    created_at: str
    updated_at: str


class MCPServerTool(BaseModel):
    """MCP server tool"""

    id: str
    mcp_server_id: str
    tool_name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    input_schema: JSONSchema
    output_schema: Optional[JSONSchema] = None
    metadata: Optional[Any] = None
    synced_at: str


class MCPServerResource(BaseModel):
    """MCP server resource"""

    id: str
    mcp_server_id: str
    resource_uri: str
    resource_name: str
    description: Optional[str] = None
    mime_type: Optional[str] = None
    metadata: Optional[Any] = None
    synced_at: str


# ============================================================================
# RAG Types
# ============================================================================


class DocumentCollection(BaseModel):
    """Document collection for RAG"""

    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    embedding_model: str
    embedding_dimensions: int
    metadata: Optional[Any] = None
    created_at: str
    updated_at: str


class Document(BaseModel):
    """Document in collection"""

    id: str
    collection_id: str
    user_id: str
    title: str
    content: str
    metadata: Optional[Any] = None
    created_at: str
    updated_at: str


class DocumentChunk(BaseModel):
    """Document chunk with embedding"""

    id: str
    document_id: str
    collection_id: str
    content: str
    chunk_index: int
    embedding: Optional[List[float]] = None
    metadata: Optional[Any] = None
    created_at: str


class SimilaritySearchResult(BaseModel):
    """Similarity search result"""

    chunk_id: str
    document_id: str
    content: str
    similarity: float
    metadata: Optional[Any] = None


# ============================================================================
# Custom Response Types
# ============================================================================


class CustomResponse(BaseModel):
    """Custom response template"""

    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    response_structure: Any
    tags: List[str] = Field(default_factory=list)
    created_at: str
    updated_at: str


# ============================================================================
# Request/Response Types
# ============================================================================


class AgentInferenceRequest(BaseModel):
    """Agent inference request"""

    agent_id: str
    user_message: str
    rag_collection_id: Optional[str] = None
    rag_match_threshold: Optional[float] = None
    rag_match_count: Optional[int] = None
    embedding_model_id: Optional[str] = None
    variables: Optional[Dict[str, str]] = None
    response_structure: Optional[Any] = None
    conversation_history: Optional[List[ConversationMessage]] = None
    images: Optional[List[ImageInput]] = None


class UsageStatistics(BaseModel):
    """Token usage statistics"""

    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost: float
    latency_ms: int


class RAGResult(BaseModel):
    """RAG search results"""

    collection_id: str
    results_count: int
    results: List[SimilaritySearchResult]


class AgentInfo(BaseModel):
    """Agent information in response"""

    id: str
    name: str
    model: str


class AgentInferenceResponse(BaseModel):
    """Agent inference response"""

    success: bool
    response: str
    agent: AgentInfo
    rag: Optional[RAGResult] = None
    usage: UsageStatistics
    session_id: Optional[str] = None


# ============================================================================
# Configuration Types
# ============================================================================


class ClientConfig(BaseModel):
    """Client configuration"""

    api_key: str
    api_secret: str
    base_url: str = "https://jurqxbgcbagakcikzhpe.supabase.co"
    timeout: Optional[int] = None
    max_retries: Optional[int] = None
    debug: bool = False

    class Config:
        arbitrary_types_allowed = True
