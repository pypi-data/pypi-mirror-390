"""
Responses API Client

Client for the stateless responses API (OpenAI/Anthropic-compatible).
"""

import logging
from typing import AsyncGenerator, Callable, List, Optional, Union, Any, Dict

from .base_client import BaseClient
from .types import (
    ResponseCreateRequest,
    ResponseCreateResponse,
    ResponseMessage,
    SimpleMessage,
    RichMessage,
    InputMessage,
    TextConfig,
    ToolDefinition,
    MCPServerDefinition,
    SSEEvent,
    StreamEvent,
    WebSearchConfig,
)
from .managed_types import ManagedEvent, Response
from .stream_manager import StreamManager, _clean_message_part
from .history import MessageHistory

# Conditional import for ToolRegistry to avoid circular dependency
try:
    from .tools import ToolRegistry
except ImportError:
    ToolRegistry = None  # type: ignore

logger = logging.getLogger(__name__)


def _validate_web_search_config(web_search: Optional[Union[WebSearchConfig, dict]]) -> None:
    """
    Validate web search configuration.
    
    Raises:
        ValueError: If configuration is invalid
    """
    if web_search is None:
        return
    
    # Extract filters
    filters = web_search.get("filters")
    if filters is None:
        return
    
    # Check for both allowed_domains and blocked_domains
    allowed = filters.get("allowed_domains")
    blocked = filters.get("blocked_domains")
    
    if allowed and blocked:
        raise ValueError(
            "Web search filters error: Cannot specify both 'allowed_domains' and 'blocked_domains'. "
            "Anthropic's web search API only allows one or the other. "
            "Please use either 'allowed_domains' (whitelist) OR 'blocked_domains' (blacklist), not both."
        )


class ResponsesClient:
    """Client for stateless responses API."""
    
    def __init__(self, base_client: BaseClient):
        """
        Initialize responses client.
        
        Args:
            base_client: Base HTTP client instance
        """
        self._client = base_client
    
    async def create(
        self,
        messages: List[Union[SimpleMessage, RichMessage, dict]],
        *,
        # Config (mutually exclusive)
        agent_id: Optional[str] = None,
        model: Optional[str] = None,
        # LLM config
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        reasoning: Optional[bool] = None,
        reasoning_tokens: Optional[int] = None,
        reasoning_effort: Optional[str] = None,
        beta_headers: Optional[List[str]] = None,
        # Prompts and output
        system: Optional[Union[str, List[dict]]] = None,
        text: Optional[Union[TextConfig, dict]] = None,
        # Tools (FunctionDefinitions - client/server execution)
        tools: Optional[List[Union[ToolDefinition, dict]]] = None,
        tool_choice: Optional[Union[str, dict]] = None,
        # MCP Servers (server-side execution)
        mcp_servers: Optional[List[Union[MCPServerDefinition, dict]]] = None,
        # Web search
        web_search: Optional[Union[WebSearchConfig, dict]] = None,
        # Metadata
        member_id: Optional[str] = None,
        metadata: Optional[dict] = None,
        overwrites: Optional[dict] = None,
    ) -> ResponseCreateResponse:
        """
        Create a stateless response (non-streaming).
        
        Supports flexible message formats:
        - **Simple**: OpenAI/Anthropic style with role and content
          Example: `{"role": "user", "content": "Hello!"}`
        - **Rich**: Domain-style with message parts for advanced use cases
          Example: `{"role": "user", "parts": [{"type": "text", "text": "Hello!"}]}`
        
        Args:
            messages: List of messages in simple or rich format
            agent_id: Reference to existing agent (mutually exclusive with model)
            model: Model name for inline config (mutually exclusive with agent_id)
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            reasoning: Enable extended reasoning/thinking (bool). When True:
                - **Anthropic**: Enables extended thinking mode with budget based on reasoning_tokens/reasoning_effort
                - **OpenAI**: Enables reasoning for o-series/gpt-5 models with effort level
            reasoning_tokens: Token budget for reasoning (Anthropic: budget_tokens ≥1024, if not set uses percentage of max_tokens)
            reasoning_effort: Reasoning effort level ("low", "medium", "high"):
                - **Anthropic**: Controls percentage of max_tokens allocated (low=15%, medium=30%, high=60%)
                - **OpenAI**: Maps to effort parameter (low→low, medium→medium, high→high)
            beta_headers: Anthropic beta feature headers (list of strings, e.g., ["extended-thinking-2024-12-05"])
            system: System prompt (string or list of content blocks)
            text: Text output configuration
            tools: Tool definitions (FunctionDefinitions for client/server execution)
            tool_choice: Tool choice strategy
            mcp_servers: MCP server definitions (for server-side tool execution)
            web_search: Web search configuration (WebSearchConfig TypedDict):
                - enabled: bool [required] - Enable web search
                - type: "web_search" | "web_search_2025_08_26" [OpenAI] - Tool version
                - search_context_size: "low" | "medium" | "high" [OpenAI] - Search depth
                - max_searches: int [Anthropic] - Limit searches (maps to max_uses)
                - filters: WebSearchFilters - Domain filtering
                  - allowed_domains: List[str] - Whitelist domains
                  - blocked_domains: List[str] - Blacklist domains
                  - NOTE: Use either allowed_domains OR blocked_domains, not both
                - user_location: ApproximateLocation - User location context
                  - type: "approximate" [required]
                  - city: str [optional]
                  - region: str [optional]
                  - country: str [optional] - ISO-3166-1 alpha-2
                  - timezone: str [optional] - IANA timezone
                - include_sources: bool - Request full source URLs
                - include_actions: bool - Include action traces
            member_id: User/member identifier
            metadata: Additional metadata
            overwrites: Configuration overwrites (when using agent_id)
            
        Returns:
            ResponseCreateResponse with response_id and context_id
            
        Raises:
            ValidationError: Invalid request parameters
            ServiceUnavailableError: Service is unavailable
            AgentError: Other API errors
            
        Example:
            ```python
            # Basic usage
            response = await client.responses.create(
                messages=[{"role": "user", "content": "Hello!"}],
                model="gpt-4o",
                temperature=0.7,
            )
            
            # With reasoning enabled (Anthropic)
            response = await client.responses.create(
                messages=[{"role": "user", "content": "Solve this complex problem..."}],
                model="claude-sonnet-4-latest",
                reasoning=True,
                reasoning_effort="high",  # 60% of max_tokens for thinking
                max_tokens=8000,
            )
            
            # With reasoning enabled (OpenAI o-series)
            response = await client.responses.create(
                messages=[{"role": "user", "content": "Analyze this..."}],
                model="o1",
                reasoning=True,
                reasoning_effort="medium",
            )
            
            # With web search enabled (OpenAI)
            response = await client.responses.create(
                messages=[{"role": "user", "content": "What's the latest news about AI?"}],
                model="gpt-4o",
                web_search={
                    "enabled": True,
                    "type": "web_search_2025_08_26",
                    "filters": {"allowed_domains": ["techcrunch.com", "nytimes.com"]},
                    "search_context_size": "high",
                    "include_sources": True
                }
            )
            
            # With web search enabled (Anthropic)
            response = await client.responses.create(
                messages=[{"role": "user", "content": "Research climate change data"}],
                model="claude-sonnet-4-5-latest",
                web_search={
                    "enabled": True,
                    "max_searches": 3,
                    "filters": {"allowed_domains": ["nasa.gov", "noaa.gov"]}
                }
            )
            ```
        """
        # Validate web search configuration
        _validate_web_search_config(web_search)
        
        # Convert messages to dicts (ResponseMessage is already a dict via TypedDict)
        message_dicts = [
            dict(msg) if not isinstance(msg, dict) else msg
            for msg in messages
        ]
        
        # Build request data
        request_data = {
            "messages": message_dicts,
            "stream": False,
        }
        
        # Add optional parameters
        if agent_id is not None:
            request_data["agent_id"] = agent_id
        if model is not None:
            request_data["model"] = model
        if temperature is not None:
            request_data["temperature"] = temperature
        if max_tokens is not None:
            request_data["max_tokens"] = max_tokens
        if reasoning is not None:
            request_data["reasoning"] = reasoning
        if reasoning_tokens is not None:
            request_data["reasoning_tokens"] = reasoning_tokens
        if reasoning_effort is not None:
            request_data["reasoning_effort"] = reasoning_effort
        if beta_headers is not None:
            request_data["beta_headers"] = beta_headers
        if system is not None:
            request_data["system"] = system
        if text is not None:
            request_data["text"] = dict(text) if not isinstance(text, dict) else text
        if tools is not None:
            request_data["tools"] = [
                dict(t) if not isinstance(t, dict) else t
                for t in tools
            ]
        if tool_choice is not None:
            request_data["tool_choice"] = tool_choice
        if mcp_servers is not None:
            request_data["mcp_servers"] = [
                dict(s) if not isinstance(s, dict) else s
                for s in mcp_servers
            ]
        if web_search is not None:
            request_data["web_search"] = web_search
        if member_id is not None:
            request_data["member_id"] = member_id
        if metadata is not None:
            request_data["metadata"] = metadata
        if overwrites is not None:
            request_data["overwrites"] = overwrites
        
        # Make request
        response_data = await self._client._request(
            method="POST",
            path="/api/v1/responses",
            json_data=request_data,
        )
        
        # TypedDict: return the dict directly, type checker will validate it
        return response_data  # type: ignore[return-value]
    
    async def create_stream(
        self,
        messages: List[Union[SimpleMessage, RichMessage, dict]],
        *,
        current_message: Optional[Union[RichMessage, dict]] = None,
        session_id: Optional[str] = None,
        # Config (mutually exclusive)
        agent_id: Optional[str] = None,
        model: Optional[str] = None,
        # LLM config
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        reasoning: Optional[bool] = None,
        reasoning_tokens: Optional[int] = None,
        reasoning_effort: Optional[str] = None,
        beta_headers: Optional[List[str]] = None,
        # Prompts and output
        system: Optional[Union[str, List[dict]]] = None,
        text: Optional[Union[TextConfig, dict]] = None,
        # Tools (FunctionDefinitions - client/server execution)
        tools: Optional[List[Union[ToolDefinition, dict]]] = None,
        tool_choice: Optional[Union[str, dict]] = None,
        # MCP Servers (server-side execution)
        mcp_servers: Optional[List[Union[MCPServerDefinition, dict]]] = None,
        # Web search
        web_search: Optional[Union[WebSearchConfig, dict]] = None,
        # Metadata
        member_id: Optional[str] = None,
        metadata: Optional[dict] = None,
        overwrites: Optional[dict] = None,
    ) -> AsyncGenerator[StreamEvent, None]:
        """
        Create a stateless response with SSE streaming.
        
        Supports flexible message formats:
        - **Simple**: OpenAI/Anthropic style with role and content
        - **Rich**: Domain-style with message parts for advanced use cases
        
        Args:
            messages: List of completed messages (conversation history)
            current_message: Optional message being built across turns (for multi-turn tool execution)
            session_id: Optional session ID for tracking
            (All other args same as create())
            
        Yields:
            StreamEvent objects with typed event data (message parts, lifecycle events)
            
        Raises:
            ValidationError: Invalid request parameters
            ServiceUnavailableError: Service is unavailable
            AgentError: Other API errors
            
        Example:
            ```python
            async for event in client.responses.create_stream(
                messages=[
                    ResponseMessage(role="user", content="Hello!")
                ],
                model="gpt-4o",
            ):
                event_type = event.get('event_type')
                data = event.get('data', {})
                
                if event_type == 'message_part.updated':
                    print(f"Content delta: {data.get('delta')}")
            ```
        """
        # Validate web search configuration
        _validate_web_search_config(web_search)
        
        # Convert messages to dicts (ResponseMessage is already a dict via TypedDict)
        message_dicts = [
            dict(msg) if not isinstance(msg, dict) else msg
            for msg in messages
        ]
        
        # Build request data
        request_data = {
            "messages": message_dicts,
            "stream": True,
        }
        
        # Add current_message if provided
        if current_message is not None:
            request_data["current_message"] = (
                dict(current_message) if not isinstance(current_message, dict) else current_message
            )
        
        # Add optional parameters (same as create())
        if agent_id is not None:
            request_data["agent_id"] = agent_id
        if model is not None:
            request_data["model"] = model
        if temperature is not None:
            request_data["temperature"] = temperature
        if max_tokens is not None:
            request_data["max_tokens"] = max_tokens
        if reasoning is not None:
            request_data["reasoning"] = reasoning
        if reasoning_tokens is not None:
            request_data["reasoning_tokens"] = reasoning_tokens
        if reasoning_effort is not None:
            request_data["reasoning_effort"] = reasoning_effort
        if beta_headers is not None:
            request_data["beta_headers"] = beta_headers
        if system is not None:
            request_data["system"] = system
        if text is not None:
            request_data["text"] = dict(text) if not isinstance(text, dict) else text
        if tools is not None:
            request_data["tools"] = [
                dict(t) if not isinstance(t, dict) else t
                for t in tools
            ]
        if tool_choice is not None:
            request_data["tool_choice"] = tool_choice
        if mcp_servers is not None:
            request_data["mcp_servers"] = [
                dict(s) if not isinstance(s, dict) else s
                for s in mcp_servers
            ]
        if web_search is not None:
            request_data["web_search"] = web_search
        if member_id is not None:
            request_data["member_id"] = member_id
        if metadata is not None:
            request_data["metadata"] = metadata
        if overwrites is not None:
            request_data["overwrites"] = overwrites
        
        # Build query params
        params = {}
        if session_id is not None:
            params["session_id"] = session_id
        
        # Stream events - unwrap SSE wrapper to get actual event data
        async for sse_event in self._client._stream(
            method="POST",
            path="/api/v1/responses/stream",
            json_data=request_data,
            params=params,
        ):
            # Extract the actual event from SSE wrapper: {'data': {'event_type': '...', 'data': {...}}}
            # Unwrap to: {'event_type': '...', 'data': {...}}
            event_data = sse_event.get("data")
            if event_data is not None:
                yield event_data  # type: ignore[misc]
    
    async def get_status(self, response_id: str) -> dict:
        """
        Get status of a stateless response.
        
        Args:
            response_id: ID of the response
            
        Returns:
            Response status information
            
        Note:
            This endpoint is currently a placeholder.
        """
        return await self._client._request(
            method="GET",
            path=f"/api/v1/responses/{response_id}",
        )
    
    # ========================================================================
    # High-Level Managed API (Simple & Easy to Use)
    # ========================================================================
    
    async def stream(
        self,
        messages: Union[MessageHistory, List[Union[SimpleMessage, RichMessage, dict]]],
        *,
        current_message: Optional[Union[RichMessage, dict]] = None,
        # Config
        agent_id: Optional[str] = None,
        model: Optional[str] = None,
        # LLM config
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        reasoning: Optional[bool] = None,
        reasoning_tokens: Optional[int] = None,
        reasoning_effort: Optional[str] = None,
        beta_headers: Optional[List[str]] = None,
        # Prompts and output
        system: Optional[Union[str, List[dict]]] = None,
        text: Optional[Union[TextConfig, dict]] = None,
        # Tools
        tools: Optional[Union[List[Union[ToolDefinition, dict]], "ToolRegistry"]] = None,
        tool_choice: Optional[Union[str, dict]] = None,
        # MCP Servers
        mcp_servers: Optional[List[Union[MCPServerDefinition, dict]]] = None,
        # Web search
        web_search: Optional[Union[WebSearchConfig, dict]] = None,
        # Metadata
        member_id: Optional[str] = None,
        metadata: Optional[dict] = None,
        overwrites: Optional[dict] = None,
        # Managed stream options
        auto_execute: bool = False,
        tool_executor: Optional[Callable[[str, Dict[str, Any]], Any]] = None,
    ) -> AsyncGenerator[ManagedEvent, None]:
        """
        Stream a response with high-level managed events.
        
        This is the recommended streaming API for most use cases. It provides:
        - Simplified events (TextChunk, ThinkingChunk, ToolRequest, etc.)
        - Automatic text/thinking accumulation
        - Optional tool auto-execution
        - Easy integration with MessageHistory
        
        Args:
            messages: MessageHistory object or list of messages
            model: Model name (e.g., "gpt-4o", "claude-sonnet-4")
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            reasoning: Enable reasoning/thinking mode
            tools: Tool definitions or ToolRegistry
            auto_execute: Auto-execute server tools (requires tool_executor)
            tool_executor: Function to execute tools: (name, args) -> result
            (other args same as create_stream)
            
        Yields:
            ManagedEvent objects (TextChunk, ToolRequest, ResponseComplete, etc.)
            
        Example:
            ```python
            history = MessageHistory()
            history.add_user("Tell me a story")
            
            async for event in client.responses.stream(history, model="gpt-4o"):
                if event["type"] == "text":
                    print(event["delta"], end="", flush=True)
                elif event["type"] == "complete":
                    history.add_assistant(event)
            ```
        """
        # Extract messages from MessageHistory if provided
        if isinstance(messages, MessageHistory):
            message_list = messages.get_messages()
        else:
            message_list = messages
        
        # Handle ToolRegistry
        tool_defs = None
        executor = tool_executor
        
        if tools is not None:
            if hasattr(tools, "get_definitions"):
                # It's a ToolRegistry
                tool_defs = tools.get_definitions()  # type: ignore
                # If auto_execute and no executor provided, use registry's execute method
                if auto_execute and executor is None:
                    executor = tools.execute  # type: ignore
            else:
                # It's a list of tool definitions
                tool_defs = tools  # type: ignore
        
        # Create raw stream
        raw_stream = self.create_stream(
            messages=message_list,
            current_message=current_message,
            agent_id=agent_id,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            reasoning=reasoning,
            reasoning_tokens=reasoning_tokens,
            reasoning_effort=reasoning_effort,
            beta_headers=beta_headers,
            system=system,
            text=text,
            tools=tool_defs,
            tool_choice=tool_choice,
            mcp_servers=mcp_servers,
            web_search=web_search,
            member_id=member_id,
            metadata=metadata,
            overwrites=overwrites,
        )
        
        # Process through stream manager
        manager = StreamManager(
            auto_execute=auto_execute,
            tool_executor=executor,
        )
        
        async for event in manager.process_stream(raw_stream):
            yield event
    
    async def chat(
        self,
        messages: Union[MessageHistory, List[Union[SimpleMessage, RichMessage, dict]]],
        *,
        # Config
        agent_id: Optional[str] = None,
        model: Optional[str] = None,
        # LLM config
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        reasoning: Optional[bool] = None,
        reasoning_tokens: Optional[int] = None,
        reasoning_effort: Optional[str] = None,
        beta_headers: Optional[List[str]] = None,
        # Prompts and output
        system: Optional[Union[str, List[dict]]] = None,
        text: Optional[Union[TextConfig, dict]] = None,
        # Tools
        tools: Optional[Union[List[Union[ToolDefinition, dict]], "ToolRegistry"]] = None,
        tool_choice: Optional[Union[str, dict]] = None,
        # MCP Servers
        mcp_servers: Optional[List[Union[MCPServerDefinition, dict]]] = None,
        # Web search
        web_search: Optional[Union[WebSearchConfig, dict]] = None,
        # Metadata
        member_id: Optional[str] = None,
        metadata: Optional[dict] = None,
        overwrites: Optional[dict] = None,
        # Chat options
        max_turns: int = 1,
        auto_execute: bool = True,
    ) -> Response:
        """
        Get a complete response (non-streaming, blocks until complete).
        
        This is the simplest API for getting AI responses. It:
        - Blocks until the response is complete
        - Returns a Response object with text, parts, and metadata
        - Optionally auto-executes tools and loops for multi-turn conversations
        
        Args:
            messages: MessageHistory object or list of messages
            model: Model name (e.g., "gpt-4o", "claude-sonnet-4")
            max_turns: Maximum conversation turns (for tool execution loops)
            auto_execute: Auto-execute tools and continue (requires ToolRegistry)
            (other args same as stream)
            
        Returns:
            Response object with text, thinking, parts, and metadata
            
        Example:
            ```python
            history = MessageHistory()
            history.add_user("What's the weather in Tokyo?")
            
            response = await client.responses.chat(
                history,
                model="gpt-4o",
                tools=registry,
                auto_execute=True,
            )
            
            print(response["text"])
            history.add_assistant(response)
            
            # With web search (OpenAI)
            response = await client.responses.chat(
                messages=[{"role": "user", "content": "Latest AI news?"}],
                model="gpt-4o",
                web_search={
                    "enabled": True,
                    "filters": {"allowed_domains": ["techcrunch.com"]},
                    "search_context_size": "high",
                    "include_sources": True
                }
            )
            # Access web search results from tool parts
            for part in response["parts"]:
                if part.get("type") == "tool" and part.get("name") == "web_search":
                    print(f"Citations: {part.get('citations', [])}")
                    print(f"Sources: {part.get('sources', [])}")
            ```
        """
        # Extract messages from MessageHistory if provided
        if isinstance(messages, MessageHistory):
            message_list = messages.get_messages()
        else:
            message_list = messages
        
        # Handle ToolRegistry
        tool_defs = None
        executor = None
        
        if tools is not None:
            if hasattr(tools, "get_definitions"):
                # It's a ToolRegistry
                tool_defs = tools.get_definitions()  # type: ignore
                if auto_execute:
                    executor = tools.execute  # type: ignore
            else:
                # It's a list of tool definitions
                tool_defs = tools  # type: ignore
        
        # Track current message being built across turns
        current_msg: Optional[Dict[str, Any]] = None
        
        # Run conversation loop
        for turn in range(max_turns):
            full_text = ""
            full_thinking = ""
            all_parts = []
            tool_calls = []
            response_data = {}

            logger.info(f"Chat turn {turn + 1}: Starting with {len(message_list)} messages")
            logger.info(f"Chat turn {turn + 1}: Current message: {current_msg}")
            logger.info(f"Chat turn {turn + 1}: Model: {model}")
            # Stream the response (continue current_msg if exists)
            async for event in self.stream(
                messages=message_list,
                current_message=current_msg,
                agent_id=agent_id,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                reasoning=reasoning,
                reasoning_tokens=reasoning_tokens,
                reasoning_effort=reasoning_effort,
                beta_headers=beta_headers,
                system=system,
                text=text,
                tools=tool_defs,
                tool_choice=tool_choice,
                mcp_servers=mcp_servers,
                web_search=web_search,
                member_id=member_id,
                metadata=metadata,
                overwrites=overwrites,
                auto_execute=False,  # We handle execution manually here
                tool_executor=None,
            ):
                event_type = event.get("type")
                
                if event_type == "complete":
                    full_text = event.get("text", "")
                    full_thinking = event.get("thinking", "")
                    all_parts = event.get("parts", [])
                    tool_calls = event.get("tool_calls", [])
                    response_data = event
                    break
            
            # Check if we have tool calls and should execute them
            if tool_calls and auto_execute and executor:
                logger.info(f"Turn {turn + 1}: Executing {len(tool_calls)} tool(s)")
                
                # Execute tools and update parts with results IN PLACE
                for tool_call in tool_calls:
                    tool_name = tool_call.get("name", "")
                    tool_args = tool_call.get("args", {})
                    tool_id = tool_call.get("id", "")
                    
                    try:
                        # Execute tool
                        result = await executor(tool_name, tool_args)
                        logger.info(f"Tool {tool_name} executed successfully, updating part")
                        
                        # Find and update the corresponding tool part with the result
                        for part in all_parts:
                            if part.get("type") == "tool" and (
                                part.get("tool_call_id") == tool_id or part.get("id") == tool_id
                            ):
                                part["result"] = result
                                part["error"] = None
                                logger.info(f"Updated tool part {tool_id} with result")
                                break
                        else:
                            # If tool part not found, log warning but continue
                            logger.warning(f"Could not find tool part for {tool_name} (id={tool_id}), skipping result")
                    
                    except Exception as e:
                        logger.error(f"Tool execution failed for {tool_name}: {e}")
                        
                        # Find and update the corresponding tool part with the error
                        for part in all_parts:
                            if part.get("type") == "tool" and (
                                part.get("tool_call_id") == tool_id or part.get("id") == tool_id
                            ):
                                part["error"] = str(e)
                                part["result"] = None
                                break
                
                # Clean all parts to match TypedDict definitions
                cleaned_parts = [_clean_message_part(part) for part in all_parts]
                
                # Update current_msg with ALL parts (text, thinking, and tool parts with results)
                # Only include parts (not text) to ensure mutual exclusivity
                current_msg = {
                    "role": "assistant",
                    "parts": cleaned_parts,  # Includes text, thinking, AND tool parts
                }
                
                # Get message_id from first part if available
                if all_parts and all_parts[0].get("message_id"):
                    current_msg["id"] = all_parts[0]["message_id"]
                
                logger.info(f"Updated current_message with {len(cleaned_parts)} parts (text, thinking, and tool parts with results)")
                
                # Continue to next turn
                continue
            
            # No tool calls or not auto-executing, return response
            response: Response = {
                "text": full_text,
                "thinking": full_thinking,
                "parts": all_parts,
                "tool_calls": tool_calls,
                "models_used": response_data.get("models_used", []),
                "usage": response_data.get("usage", []),
                "response_id": response_data.get("response_id", ""),
                "context_id": response_data.get("context_id", ""),
            }
            return response
        
        # Max turns reached, return last response
        logger.warning(f"Max turns ({max_turns}) reached in chat()")
        response: Response = {
            "text": full_text,
            "thinking": full_thinking,
            "parts": all_parts,
            "tool_calls": tool_calls,
            "models_used": response_data.get("models_used", []),
            "usage": response_data.get("usage", []),
            "response_id": response_data.get("response_id", ""),
            "context_id": response_data.get("context_id", ""),
        }
        return response

