"""
Type definitions for Agent Evolution SDK
"""

from typing import Any, Dict, List, Literal, Optional, Union
from typing_extensions import TypedDict


# ============================================================================
# Web Search Types
# ============================================================================

class ApproximateLocation(TypedDict, total=False):
    """Approximate user location for web search context."""
    type: Literal["approximate"]
    city: Optional[str]
    region: Optional[str]
    country: Optional[str]  # ISO-3166-1 alpha-2, e.g. "US"
    timezone: Optional[str]  # IANA TZ, e.g. "America/Los_Angeles"


class WebSearchFilters(TypedDict, total=False):
    """
    Domain filtering for web search results.
    
    Note: Anthropic's API only allows ONE of allowed_domains OR blocked_domains, not both.
    The SDK will raise a ValueError if both are provided.
    """
    allowed_domains: Optional[List[str]]  # Whitelist: Only search these domains
    blocked_domains: Optional[List[str]]  # Blacklist: Exclude these domains


class WebSearchConfig(TypedDict, total=False):
    """
    Web search configuration.
    
    Unified configuration that works across OpenAI and Anthropic providers.
    Provider-specific fields are automatically handled by the backend.
    
    Example (OpenAI):
        {
            "enabled": True,
            "type": "web_search_2025_08_26",
            "filters": {"allowed_domains": ["techcrunch.com", "nytimes.com"]},
            "search_context_size": "high",
            "include_sources": True
        }
    
    Example (Anthropic):
        {
            "enabled": True,
            "max_searches": 3,
            "filters": {"allowed_domains": ["nasa.gov"]}  # Note: Use either allowed_domains OR blocked_domains, not both
        }
    """
    enabled: bool  # Required: Enable web search
    
    # OpenAI-specific
    type: Optional[Literal["web_search", "web_search_2025_08_26"]]
    search_context_size: Optional[Literal["low", "medium", "high"]]
    
    # Anthropic-specific
    max_searches: Optional[int]  # Maps to max_uses
    
    # Common fields
    filters: Optional[WebSearchFilters]
    user_location: Optional[ApproximateLocation]
    include_sources: Optional[bool]
    include_actions: Optional[bool]


class WebSearchCitation(TypedDict, total=False):
    """URL citation from web search results."""
    type: Literal["url_citation"]
    url: str
    title: Optional[str]
    location: Optional[str]  # Character range or encrypted index
    start_index: Optional[int]
    end_index: Optional[int]


class WebSearchSource(TypedDict, total=False):
    """Source URL from web search action."""
    url: str
    title: Optional[str]
    type: Optional[str]
    page_age: Optional[str]  # Anthropic only


class WebSearchActionSearch(TypedDict, total=False):
    """Web search action - search."""
    type: Literal["search"]
    query: Optional[str]
    sources: Optional[List[str]]  # List of URLs
    status: Optional[Literal["in_progress", "searching", "completed", "error"]]


class WebSearchActionOpenPage(TypedDict, total=False):
    """Web search action - open page."""
    type: Literal["open_page"]
    url: Optional[str]
    status: Optional[Literal["in_progress", "searching", "completed", "error"]]


class WebSearchActionFindInPage(TypedDict, total=False):
    """Web search action - find in page."""
    type: Literal["find_in_page"]
    url: Optional[str]
    pattern: Optional[str]
    status: Optional[Literal["in_progress", "searching", "completed", "error"]]


WebSearchAction = Union[WebSearchActionSearch, WebSearchActionOpenPage, WebSearchActionFindInPage]


# ============================================================================
# Responses API Types
# ============================================================================

# ============================================================================
# Message Part Types (for rich format)
# ============================================================================

class TextPartInput(TypedDict, total=False):
    """Text part for rich message format."""
    id: str  # Optional, auto-generated if not provided
    type: Literal["text"]
    text: str
    order: int  # Optional, auto-assigned from position
    block_order: int  # Optional, auto-assigned
    provider: str  # Optional LLM provider tracking
    provider_id: str
    provider_item_type: str
    created_at: str  # ISO format, optional
    finished_at: str
    annotations: List[Dict[str, Any]] # Optional, annotations for the text part


class MediaPartInput(TypedDict, total=False):
    """Media part for rich message format."""
    id: str
    type: Literal["media"]
    url: str
    mime_type: str
    file_name: str
    file_size: int
    order: int
    block_order: int
    meta_data: Dict[str, Any]
    created_at: str
    finished_at: str


class ToolPartInput(TypedDict, total=False):
    """Tool part for rich message format."""
    id: str
    type: Literal["tool"]
    tool_call_id: str
    tool_id: str
    name: str
    input: Dict[str, Any]
    arguments: Dict[str, Any]
    result: Union[Dict[str, Any], str]
    error: Union[Dict[str, Any], str]
    order: int
    block_order: int
    # Synthetic UX parameters
    act_now: str
    act_done: str
    intent: str
    use_intent: bool
    # Provider tracking
    provider: str
    provider_id: str
    provider_item_type: str
    # MCP fields
    server_label: str
    approval_request_id: str
    # Web search specific fields
    citations: List[WebSearchCitation]
    sources: List[WebSearchSource]
    actions: List[WebSearchAction]
    created_at: str
    finished_at: str


class ThinkingPartInput(TypedDict, total=False):
    """Thinking/reasoning part for rich message format."""
    id: str
    type: Literal["thinking"]
    text: str
    status: Literal["in_progress", "completed", "incomplete"]
    order: int
    block_order: int
    # Provider tracking
    provider: str
    provider_id: str
    provider_item_type: str
    # Anthropic extended thinking
    signature: str
    # OpenAI reasoning
    summary: List[str]
    encrypted_content: str
    created_at: str
    finished_at: str


# Union of all part types
MessagePartInput = Union[TextPartInput, MediaPartInput, ToolPartInput, ThinkingPartInput]


# ============================================================================
# Message Format Types
# ============================================================================

class ResponseMessage(TypedDict):
    """Simple OpenAI/Anthropic format message (legacy compatibility)."""
    role: Literal["user", "assistant", "system"]
    content: Union[str, List[Dict[str, Any]]]


class SimpleMessage(TypedDict):
    """Simple OpenAI/Anthropic format message."""
    role: Literal["user", "assistant", "system"]
    content: Union[str, List[Dict[str, Any]]]


class RichMessage(TypedDict, total=False):
    """
    Rich domain-style message with parts.
    
    Important: content and parts are mutually exclusive:
    - Use 'content' for standard OpenAI/Anthropic format (string or list of content parts)
    - Use 'parts' for rich SDK format (list of message parts with full metadata)
    - 'text' is optional and only used as a summary when 'parts' is present
    - Never provide both 'content' and 'parts' together
    """
    id: str  # Optional, auto-generated
    role: Literal["user", "assistant", "system"]
    member_id: str  # Optional but can be set
    text: str  # Optional text summary (only with parts)
    content: Union[str, List[Dict[str, Any]]]  # Standard format (XOR with parts)
    parts: List[MessagePartInput]  # Rich format (XOR with content)
    cost: float
    tokens: int
    created_at: str  # ISO format
    meta_data: Dict[str, Any]


# Union for flexibility
InputMessage = Union[SimpleMessage, RichMessage, Dict[str, Any]]


class TextConfig(TypedDict, total=False):
    """Text output configuration."""
    format: Union[str, Dict[str, Any]]
    verbosity: Literal["low", "medium", "high"]


class ToolDefinition(TypedDict, total=False):
    """Tool definition for client or server execution."""
    type: Literal["function"]
    tool_type: Literal["client", "server"]
    function: Dict[str, Any]


class MCPServerDefinition(TypedDict, total=False):
    """
    MCP (Model Context Protocol) server definition.
    
    MCP tools are executed server-side (not by SDK client).
    Matches OpenAI and Anthropic MCP server format.
    """
    name: str  # Required: Server label/name
    url: str  # Required: MCP server URL
    type: Literal["url"]  # Required: Always "url"
    authorization_token: str  # Optional: Auth token for MCP server
    tool_configuration: Dict[str, Any]  # Optional: Tool filtering/config


class ResponseCreateRequest(TypedDict, total=False):
    """Request to create a stateless response."""
    messages: List[InputMessage]
    
    # Config (mutually exclusive)
    agent_id: str
    model: str
    
    # LLM config
    temperature: float
    max_tokens: int
    reasoning: bool  # Enable extended reasoning/thinking
    reasoning_tokens: int  # Token budget for reasoning (≥1024 for Anthropic)
    reasoning_effort: Literal["low", "medium", "high"]  # Effort level
    beta_headers: List[str]  # Anthropic beta feature headers
    
    # Prompts and output
    system: Union[str, List[Dict[str, Any]]]
    text: TextConfig
    
    # Tools (FunctionDefinitions - client or server execution)
    tools: List[ToolDefinition]
    tool_choice: Union[str, Dict[str, Any]]
    
    # MCP Servers (separate from tools - server-side execution)
    mcp_servers: List[MCPServerDefinition]
    
    # Web search configuration
    web_search: WebSearchConfig
    
    # Metadata
    member_id: str
    metadata: Dict[str, Any]
    overwrites: Dict[str, Any]
    
    # Streaming
    stream: bool


class ResponseCreateResponse(TypedDict):
    """Response from creating a stateless response."""
    response_id: str
    context_id: str
    model: str
    created: int
    status: str
    object: str


# ============================================================================
# Activations API Types
# ============================================================================

class ActivationRequest(TypedDict, total=False):
    """Request to submit an agent activation."""
    agent_id: str
    thread_id: str
    room_id: str
    replied_id: str
    override_message_id: str


class ActivationResponse(TypedDict):
    """Response from submitting an activation."""
    response_id: str
    agent_id: str
    thread_id: str
    queued: bool
    message: str


class CancellationResponse(TypedDict):
    """Response from canceling a response."""
    success: bool
    response_id: str
    message: str
    timestamp: str


class BulkCancellationResponse(TypedDict, total=False):
    """Response from bulk cancellation."""
    success: bool
    thread_id: str
    total_responses: int
    total_active: int
    total_queued: int
    cancelled_responses: List[str]
    discarded_queued_responses: List[str]
    failed_responses: List[str]
    timeout_responses: List[str]
    message: str
    timestamp: str
    details: Dict[str, Any]


class ThreadStatusResponse(TypedDict):
    """Thread status information."""
    thread_id: str
    status: str
    queue_length: int


class ActivationInfo(TypedDict, total=False):
    """Information about a single activation."""
    response_id: str
    agent_id: str
    status: str
    timestamp: str


class ThreadActivationsResponse(TypedDict):
    """Response with thread activations."""
    thread_id: str
    thread_status: str
    active_response_id: Optional[str]
    queued_activations: List[ActivationInfo]
    queue_length: int


class ActivationStatsResponse(TypedDict):
    """System-wide activation statistics."""
    active_count: int
    queue_count: int
    active_activations: List[ActivationInfo]


# ============================================================================
# SSE Event Types
# ============================================================================

class SSEEvent(TypedDict, total=False):
    """Server-Sent Event."""
    event: str
    data: Dict[str, Any]
    id: str
    retry: int


# ============================================================================
# Stream Event Types (re-exported from event_types)
# ============================================================================

# Import all event types for convenience
from .event_types import (
    # Data payload types
    MessagePartAddedData,
    MessagePartUpdatedData,
    MessagePartDoneData,
    ResponseScheduledData,
    ResponseRescheduledData,
    ResponseStartedData,
    ResponseResumedData,
    ResponseSuspendedData,
    ResponseStoppedData,
    ResponseInterruptedData,
    ResponseRequeuedData,
    ResponseCompletedData,
    ResponseEmptyData,
    ResponseFailedData,
    ResponseFallbackData,
    ResponseRetryData,
    # Full event types
    MessagePartAddedEvent,
    MessagePartUpdatedEvent,
    MessagePartDoneEvent,
    ResponseScheduledEvent,
    ResponseRescheduledEvent,
    ResponseStartedEvent,
    ResponseResumedEvent,
    ResponseSuspendedEvent,
    ResponseStoppedEvent,
    ResponseInterruptedEvent,
    ResponseRequeuedEvent,
    ResponseCompletedEvent,
    ResponseEmptyEvent,
    ResponseFailedEvent,
    ResponseFallbackEvent,
    ResponseRetryEvent,
    # Union types
    StreamEventData,
    StreamEvent,
)

