"""
Altan SDK - AI Agents Module

Friendly AI agent interface with support for multiple models, streaming, web search,
and conversation management.
"""

from .agent import Agent, MessageHistory
from .agents import AgentClient
from .agents.types import (
    ResponseMessage,
    SimpleMessage,
    RichMessage,
    ResponseCreateResponse,
    TextConfig,
    ToolDefinition,
    MCPServerDefinition,
    WebSearchConfig,
)
from .agents.managed_types import ManagedEvent, Response
from .agents.history import MessageHistory as AgentMessageHistory
from .agents.errors import (
    AgentError,
    ValidationError,
    ServiceUnavailableError,
    TimeoutError,
    NotFoundError,
    RateLimitError,
    InternalServerError,
)

__all__ = [
    # Main friendly interface
    "Agent",
    "MessageHistory",
    
    # Advanced interface
    "AgentClient",
    
    # Types
    "ResponseMessage",
    "SimpleMessage", 
    "RichMessage",
    "ResponseCreateResponse",
    "TextConfig",
    "ToolDefinition",
    "MCPServerDefinition",
    "WebSearchConfig",
    "ManagedEvent",
    "Response",
    
    # Utilities
    "AgentMessageHistory",
    
    # Errors
    "AgentError",
    "ValidationError",
    "ServiceUnavailableError",
    "TimeoutError",
    "NotFoundError", 
    "RateLimitError",
    "InternalServerError",
]
