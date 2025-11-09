"""
Simplified event types for managed streaming API.

These high-level events abstract away the complexity of raw streaming events,
making it easier to build applications with the SDK.
"""

from typing import Any, Dict, List, Literal, Union
from typing_extensions import TypedDict

# Import web search types from types module
from .types import WebSearchCitation, WebSearchSource, WebSearchAction


# ============================================================================
# Managed Event Types (High-Level Simplified Events)
# ============================================================================

class TextChunk(TypedDict, total=False):
    """Text content delta from the assistant."""
    type: Literal["text"]
    delta: str
    text: str  # Accumulated text so far


class ThinkingChunk(TypedDict, total=False):
    """Thinking/reasoning content delta."""
    type: Literal["thinking"]
    delta: str
    text: str  # Accumulated thinking so far
    status: Literal["in_progress", "completed", "incomplete"]


class ToolRequest(TypedDict, total=False):
    """Request to execute a tool (client-side execution needed)."""
    type: Literal["tool_request"]
    id: str  # tool_call_id
    name: str  # Tool/function name
    args: Dict[str, Any]  # Parsed arguments
    tool_type: str  # "client" or "server"
    tool_id: str  # Domain tool ID
    server_label: str  # For MCP tools


class ToolResult(TypedDict, total=False):
    """Result from tool execution (auto-executed)."""
    type: Literal["tool_result"]
    id: str  # tool_call_id
    name: str
    result: Any
    error: Union[str, Dict[str, Any]]
    success: bool


class ResponseComplete(TypedDict, total=False):
    """Final complete response with all data."""
    type: Literal["complete"]
    text: str  # Full accumulated text
    thinking: str  # Full accumulated thinking
    parts: List[Dict[str, Any]]  # All message parts
    tool_calls: List[Dict[str, Any]]  # Tool calls made
    models_used: List[str]
    usage: List[Dict[str, Any]]
    response_id: str
    context_id: str


class ResponseStarted(TypedDict, total=False):
    """Response has started."""
    type: Literal["started"]
    response_id: str
    agent_id: str


class ResponseError(TypedDict, total=False):
    """Response failed with error."""
    type: Literal["error"]
    error_message: str
    error_code: str
    retryable: bool


class WebSearchResult(TypedDict, total=False):
    """
    Web search results with citations and sources.
    
    This event is emitted when a web search tool completes, containing:
    - answer: The synthesized answer text
    - citations: URL citations with inline references
    - sources: Full source URLs that were consulted
    - actions: Action traces showing what the search actually did
    """
    type: Literal["web_search_tool_result"]
    id: str  # tool_call_id
    name: str  # Should be "web_search"
    answer: str
    citations: List[WebSearchCitation]
    sources: List[WebSearchSource]
    actions: List[WebSearchAction]


# Union of all managed event types
ManagedEvent = Union[
    TextChunk,
    ThinkingChunk,
    ToolRequest,
    ToolResult,
    WebSearchResult,
    ResponseComplete,
    ResponseStarted,
    ResponseError,
]


# ============================================================================
# Response Objects (for non-streaming API)
# ============================================================================

class Response(TypedDict, total=False):
    """Complete response object from chat() method."""
    text: str  # Main text content
    thinking: str  # Reasoning/thinking content if any
    parts: List[Dict[str, Any]]  # Message parts
    tool_calls: List[Dict[str, Any]]  # Tool calls made
    models_used: List[str]
    usage: List[Dict[str, Any]]
    response_id: str
    context_id: str
    
    # Helper methods would be on a class wrapper
    def get_text(self) -> str:
        """Get the text content."""
        return self.get("text", "")
    
    def has_tool_calls(self) -> bool:
        """Check if response contains tool calls."""
        return len(self.get("tool_calls", [])) > 0

