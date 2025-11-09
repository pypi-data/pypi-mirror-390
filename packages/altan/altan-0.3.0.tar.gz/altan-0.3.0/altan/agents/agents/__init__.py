"""
Agents - Altan AI Python SDK

Official Python SDK for the Altan AI platform, providing access to:
- Stateless Responses API (OpenAI/Anthropic-compatible)
- Agent Activations API (event-driven agent execution)
"""

from .client import AgentClient
from .sync_client import SyncAgentClient, Client, AsyncClient
from .responses import ResponsesClient
from .activations import ActivationsClient
from .types import (
    # Responses API types
    ResponseMessage,
    SimpleMessage,
    RichMessage,
    ResponseCreateRequest,
    ResponseCreateResponse,
    TextConfig,
    ToolDefinition,
    MCPServerDefinition,
    
    # Activations API types
    ActivationRequest,
    ActivationResponse,
    CancellationResponse,
    BulkCancellationResponse,
    ThreadStatusResponse,
    ThreadActivationsResponse,
    ActivationStatsResponse,
    ActivationInfo,
    
    # SSE types
    SSEEvent,
    StreamEvent,
)
from .managed_types import (
    # Managed event types (high-level)
    ManagedEvent,
    TextChunk,
    ThinkingChunk,
    ToolRequest,
    ToolResult,
    ResponseComplete,
    ResponseStarted,
    ResponseError,
    Response,
)
from .history import MessageHistory
from .tools import ToolRegistry
from .hooks import (
    HookManager,
    RequestContext,
    ResponseContext,
    logging_request_hook,
    logging_response_hook,
    custom_header_hook,
)
from .rate_limiter import RateLimiter, NoopRateLimiter
from .usage_tracker import UsageTracker, UsageStats
from .beta_features import BetaFeatures, EXTENDED_THINKING, PROMPT_CACHING
from .validation import (
    validate_messages,
    validate_tools,
    validate_model,
    validate_temperature,
    validate_max_tokens,
    validate_request_params,
)
from .streaming_helpers import (
    stream_and_accumulate,
    stream_with_callback,
    stream_to_list,
    stream_text_only,
    stream_with_timeout,
    stream_with_progress,
)
from .errors import (
    AgentError,
    ValidationError,
    ServiceUnavailableError,
    TimeoutError,
    NotFoundError,
    RateLimitError,
    InternalServerError,
)

__version__ = "0.1.0"

__all__ = [
    # Main clients
    "AgentClient",
    "SyncAgentClient",
    "Client",  # Alias for SyncAgentClient
    "AsyncClient",  # Alias for AgentClient
    
    # Sub-clients
    "ResponsesClient",
    "ActivationsClient",
    
    # Utilities
    "MessageHistory",
    "ToolRegistry",
    
    # Hooks
    "HookManager",
    "RequestContext",
    "ResponseContext",
    "logging_request_hook",
    "logging_response_hook",
    "custom_header_hook",
    
    # Rate Limiting
    "RateLimiter",
    "NoopRateLimiter",
    
    # Usage Tracking
    "UsageTracker",
    "UsageStats",
    
    # Beta Features
    "BetaFeatures",
    "EXTENDED_THINKING",
    "PROMPT_CACHING",
    
    # Validation
    "validate_messages",
    "validate_tools",
    "validate_model",
    "validate_temperature",
    "validate_max_tokens",
    "validate_request_params",
    
    # Streaming Helpers
    "stream_and_accumulate",
    "stream_with_callback",
    "stream_to_list",
    "stream_text_only",
    "stream_with_timeout",
    "stream_with_progress",
    
    # Responses API types
    "ResponseMessage",
    "SimpleMessage",
    "RichMessage",
    "ResponseCreateRequest",
    "ResponseCreateResponse",
    "TextConfig",
    "ToolDefinition",
    "MCPServerDefinition",
    
    # Managed event types (high-level streaming)
    "ManagedEvent",
    "TextChunk",
    "ThinkingChunk",
    "ToolRequest",
    "ToolResult",
    "ResponseComplete",
    "ResponseStarted",
    "ResponseError",
    "Response",
    
    # Activations API types
    "ActivationRequest",
    "ActivationResponse",
    "CancellationResponse",
    "BulkCancellationResponse",
    "ThreadStatusResponse",
    "ThreadActivationsResponse",
    "ActivationStatsResponse",
    "ActivationInfo",
    
    # SSE types
    "SSEEvent",
    "StreamEvent",
    
    # Errors
    "AgentError",
    "ValidationError",
    "ServiceUnavailableError",
    "TimeoutError",
    "NotFoundError",
    "RateLimitError",
    "InternalServerError",
]

