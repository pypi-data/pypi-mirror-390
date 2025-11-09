"""
Synchronous API wrapper for Agent Evolution SDK

Provides synchronous versions of all async APIs for compatibility with
non-async codebases, similar to OpenAI Python SDK's dual API.
"""

import asyncio
import logging
from typing import Any, Dict, Generator, List, Optional, Union

from .client import AgentClient
from .types import (
    ResponseCreateResponse,
    SimpleMessage,
    RichMessage,
    TextConfig,
    ToolDefinition,
    MCPServerDefinition,
    WebSearchConfig,
    ActivationResponse,
    CancellationResponse,
    BulkCancellationResponse,
    ThreadStatusResponse,
    ThreadActivationsResponse,
    ActivationStatsResponse,
    SSEEvent,
    StreamEvent,
)
from .managed_types import ManagedEvent, Response
from .history import MessageHistory
from .tools import ToolRegistry

logger = logging.getLogger(__name__)


class SyncResponsesClient:
    """Synchronous version of ResponsesClient."""
    
    def __init__(self, async_client):
        self._async_client = async_client
    
    def create(
        self,
        messages: List[Union[SimpleMessage, RichMessage, dict]],
        *,
        agent_id: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        reasoning: Optional[bool] = None,
        reasoning_tokens: Optional[int] = None,
        reasoning_effort: Optional[str] = None,
        beta_headers: Optional[List[str]] = None,
        system: Optional[Union[str, List[dict]]] = None,
        text: Optional[Union[TextConfig, dict]] = None,
        tools: Optional[List[Union[ToolDefinition, dict]]] = None,
        tool_choice: Optional[Union[str, dict]] = None,
        mcp_servers: Optional[List[Union[MCPServerDefinition, dict]]] = None,
        web_search: Optional[Union[WebSearchConfig, dict]] = None,
        member_id: Optional[str] = None,
        metadata: Optional[dict] = None,
        overwrites: Optional[dict] = None,
        timeout: Optional[float] = None,
    ) -> ResponseCreateResponse:
        """
        Create a stateless response (synchronous, non-streaming).
        
        See AsyncResponsesClient.create() for full documentation.
        """
        return asyncio.run(
            self._async_client.create(
                messages=messages,
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
                tools=tools,
                tool_choice=tool_choice,
                mcp_servers=mcp_servers,
                web_search=web_search,
                member_id=member_id,
                metadata=metadata,
                overwrites=overwrites,
            )
        )
    
    def create_stream(
        self,
        messages: List[Union[SimpleMessage, RichMessage, dict]],
        *,
        current_message: Optional[Union[RichMessage, dict]] = None,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        reasoning: Optional[bool] = None,
        reasoning_tokens: Optional[int] = None,
        reasoning_effort: Optional[str] = None,
        beta_headers: Optional[List[str]] = None,
        system: Optional[Union[str, List[dict]]] = None,
        text: Optional[Union[TextConfig, dict]] = None,
        tools: Optional[List[Union[ToolDefinition, dict]]] = None,
        tool_choice: Optional[Union[str, dict]] = None,
        mcp_servers: Optional[List[Union[MCPServerDefinition, dict]]] = None,
        web_search: Optional[Union[WebSearchConfig, dict]] = None,
        member_id: Optional[str] = None,
        metadata: Optional[dict] = None,
        overwrites: Optional[dict] = None,
        timeout: Optional[float] = None,
    ) -> Generator[StreamEvent, None, None]:
        """
        Create a stateless response with SSE streaming (synchronous).
        
        Returns a generator that yields stream events.
        
        See AsyncResponsesClient.create_stream() for full documentation.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            async_gen = self._async_client.create_stream(
                messages=messages,
                current_message=current_message,
                session_id=session_id,
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
                tools=tools,
                tool_choice=tool_choice,
                mcp_servers=mcp_servers,
                web_search=web_search,
                member_id=member_id,
                metadata=metadata,
                overwrites=overwrites,
            )
            
            # Convert async generator to sync generator
            while True:
                try:
                    yield loop.run_until_complete(async_gen.__anext__())
                except StopAsyncIteration:
                    break
        finally:
            loop.close()
    
    def stream(
        self,
        messages: Union[MessageHistory, List[Union[SimpleMessage, RichMessage, dict]]],
        *,
        current_message: Optional[Union[RichMessage, dict]] = None,
        agent_id: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        reasoning: Optional[bool] = None,
        reasoning_tokens: Optional[int] = None,
        reasoning_effort: Optional[str] = None,
        beta_headers: Optional[List[str]] = None,
        system: Optional[Union[str, List[dict]]] = None,
        text: Optional[Union[TextConfig, dict]] = None,
        tools: Optional[Union[List[Union[ToolDefinition, dict]], ToolRegistry]] = None,
        tool_choice: Optional[Union[str, dict]] = None,
        mcp_servers: Optional[List[Union[MCPServerDefinition, dict]]] = None,
        web_search: Optional[Union[WebSearchConfig, dict]] = None,
        member_id: Optional[str] = None,
        metadata: Optional[dict] = None,
        overwrites: Optional[dict] = None,
        auto_execute: bool = False,
        tool_executor: Optional[Any] = None,
        timeout: Optional[float] = None,
    ) -> Generator[ManagedEvent, None, None]:
        """
        Stream a response with high-level managed events (synchronous).
        
        Returns a generator that yields managed events.
        
        See AsyncResponsesClient.stream() for full documentation.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            async_gen = self._async_client.stream(
                messages=messages,
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
                tools=tools,
                tool_choice=tool_choice,
                mcp_servers=mcp_servers,
                web_search=web_search,
                member_id=member_id,
                metadata=metadata,
                overwrites=overwrites,
                auto_execute=auto_execute,
                tool_executor=tool_executor,
            )
            
            # Convert async generator to sync generator
            while True:
                try:
                    yield loop.run_until_complete(async_gen.__anext__())
                except StopAsyncIteration:
                    break
        finally:
            loop.close()
    
    def chat(
        self,
        messages: Union[MessageHistory, List[Union[SimpleMessage, RichMessage, dict]]],
        *,
        agent_id: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        reasoning: Optional[bool] = None,
        reasoning_tokens: Optional[int] = None,
        reasoning_effort: Optional[str] = None,
        beta_headers: Optional[List[str]] = None,
        system: Optional[Union[str, List[dict]]] = None,
        text: Optional[Union[TextConfig, dict]] = None,
        tools: Optional[Union[List[Union[ToolDefinition, dict]], ToolRegistry]] = None,
        tool_choice: Optional[Union[str, dict]] = None,
        mcp_servers: Optional[List[Union[MCPServerDefinition, dict]]] = None,
        web_search: Optional[Union[WebSearchConfig, dict]] = None,
        member_id: Optional[str] = None,
        metadata: Optional[dict] = None,
        overwrites: Optional[dict] = None,
        max_turns: int = 1,
        auto_execute: bool = True,
        timeout: Optional[float] = None,
    ) -> Response:
        """
        Get a complete response (synchronous, non-streaming).
        
        See AsyncResponsesClient.chat() for full documentation.
        """
        return asyncio.run(
            self._async_client.chat(
                messages=messages,
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
                tools=tools,
                tool_choice=tool_choice,
                mcp_servers=mcp_servers,
                web_search=web_search,
                member_id=member_id,
                metadata=metadata,
                overwrites=overwrites,
                max_turns=max_turns,
                auto_execute=auto_execute,
            )
        )


class SyncActivationsClient:
    """Synchronous version of ActivationsClient."""
    
    def __init__(self, async_client):
        self._async_client = async_client
    
    def submit(
        self,
        agent_id: str,
        thread_id: str,
        room_id: Optional[str] = None,
        replied_id: Optional[str] = None,
        override_message_id: Optional[str] = None,
    ) -> ActivationResponse:
        """Submit a new agent activation (synchronous)."""
        return asyncio.run(
            self._async_client.submit(
                agent_id=agent_id,
                thread_id=thread_id,
                room_id=room_id,
                replied_id=replied_id,
                override_message_id=override_message_id,
            )
        )
    
    def retry(
        self,
        agent_id: str,
        thread_id: str,
        override_message_id: str,
        room_id: Optional[str] = None,
        replied_id: Optional[str] = None,
    ) -> ActivationResponse:
        """Retry/resume an agent activation (synchronous)."""
        return asyncio.run(
            self._async_client.retry(
                agent_id=agent_id,
                thread_id=thread_id,
                override_message_id=override_message_id,
                room_id=room_id,
                replied_id=replied_id,
            )
        )
    
    def submit_stream(
        self,
        agent_id: str,
        thread_id: str,
        room_id: Optional[str] = None,
        replied_id: Optional[str] = None,
        override_message_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Generator[SSEEvent, None, None]:
        """Submit an activation and stream progress via SSE (synchronous)."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            async_gen = self._async_client.submit_stream(
                agent_id=agent_id,
                thread_id=thread_id,
                room_id=room_id,
                replied_id=replied_id,
                override_message_id=override_message_id,
                session_id=session_id,
            )
            
            while True:
                try:
                    yield loop.run_until_complete(async_gen.__anext__())
                except StopAsyncIteration:
                    break
        finally:
            loop.close()
    
    def cancel_response(
        self,
        response_id: str,
        force: bool = False,
        reason: Optional[str] = None,
        timeout: float = 5.0,
    ) -> CancellationResponse:
        """Cancel an active agent response (synchronous)."""
        return asyncio.run(
            self._async_client.cancel_response(
                response_id=response_id,
                force=force,
                reason=reason,
                timeout=timeout,
            )
        )
    
    def get_stats(self) -> ActivationStatsResponse:
        """Get system-wide activation statistics (synchronous)."""
        return asyncio.run(self._async_client.get_stats())
    
    def get_thread_activations(
        self,
        thread_id: str,
        include_queued: bool = True,
    ) -> ThreadActivationsResponse:
        """Get all activations for a specific thread (synchronous)."""
        return asyncio.run(
            self._async_client.get_thread_activations(
                thread_id=thread_id,
                include_queued=include_queued,
            )
        )
    
    def get_thread_status(self, thread_id: str) -> ThreadStatusResponse:
        """Get the status of a thread (synchronous)."""
        return asyncio.run(self._async_client.get_thread_status(thread_id))


class SyncAgentClient:
    """
    Synchronous version of Agent Evolution client.
    
    Provides synchronous API for non-async codebases, similar to OpenAI SDK.
    All async operations are wrapped with asyncio.run().
    
    Example:
        ```python
        from altan.agents.agents import SyncAgentClient
        
        # No async/await needed!
        client = SyncAgentClient(base_url="http://localhost:8000")
        
        response = client.responses.chat(
            messages=[{"role": "user", "content": "Hello!"}],
            model="gpt-4o",
        )
        print(response["text"])
        
        client.close()
        ```
    
    Note:
        For async applications, use AgentClient instead for better
        performance and concurrency.
    """
    
    def __init__(
        self,
        base_url: str = "https://ai.altan.ai",
        api_key: Optional[str] = None,
        timeout: float = 60.0,
        max_retries: int = 3,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        keepalive_expiry: float = 30.0,
    ):
        """
        Initialize synchronous Agent Evolution client.
        
        Args:
            base_url: Base URL of the API
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            max_connections: Maximum concurrent connections
            max_keepalive_connections: Maximum idle connections to keep alive
            keepalive_expiry: Time to keep idle connections alive in seconds
        """
        # Create async client
        self._async_client = AgentClient(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=keepalive_expiry,
        )
        
        # Create sync wrappers
        self._responses = SyncResponsesClient(self._async_client.responses)
        self._activations = SyncActivationsClient(self._async_client.activations)
    
    @property
    def responses(self) -> SyncResponsesClient:
        """Access the Responses API client (synchronous)."""
        return self._responses
    
    @property
    def activations(self) -> SyncActivationsClient:
        """Access the Activations API client (synchronous)."""
        return self._activations
    
    def close(self):
        """Close the client and release resources (synchronous)."""
        asyncio.run(self._async_client.close())
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.close()


# Convenience alias (like OpenAI uses "OpenAI" for sync and "AsyncOpenAI" for async)
Client = SyncAgentClient
AsyncClient = AgentClient

