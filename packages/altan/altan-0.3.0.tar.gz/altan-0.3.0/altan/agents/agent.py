"""
Friendly Agent class for Altan SDK

A simplified, user-friendly wrapper around the AI functionality.
"""

import asyncio
from typing import AsyncGenerator, List, Optional, Union, Dict, Any, Callable

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
from .agents.history import MessageHistory
from .agents.errors import (
    AgentError,
    ValidationError,
    ServiceUnavailableError,
    TimeoutError,
    NotFoundError,
    RateLimitError,
    InternalServerError,
)


class Agent:
    """
    Friendly AI Agent for the Altan SDK.
    
    Provides a simple, intuitive interface for AI interactions without requiring
    knowledge of the underlying API structure.
    
    Example:
        ```python
        import asyncio
        from altan import Agent
        
        async def main():
            async with Agent() as agent:
                # Simple chat
                response = await agent.chat("Hello, how are you?")
                print(response["text"])
                
                # Streaming chat
                async for chunk in agent.stream("Tell me a story"):
                    if chunk["type"] == "text":
                        print(chunk["delta"], end="", flush=True)
        
        asyncio.run(main())
        ```
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://ai.altan.ai",
        timeout: float = 60.0,
        max_retries: int = 3,
    ):
        """
        Initialize the Agent.
        
        Args:
            api_key: Optional API key for authentication
            base_url: Base URL of the AI API (default: https://ai.altan.ai)
            timeout: Request timeout in seconds (default: 60.0)
            max_retries: Maximum number of retry attempts (default: 3)
        """
        self._client = AgentClient(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
        )
        self._history = MessageHistory()
    
    @property
    def history(self) -> MessageHistory:
        """
        Access the conversation history.
        
        Returns:
            MessageHistory instance for managing conversation context
        """
        return self._history
    
    async def chat(
        self,
        message: Union[str, List[Union[SimpleMessage, RichMessage, dict]]],
        *,
        model: str = "gpt-4o",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system: Optional[str] = None,
        tools: Optional[List[Union[ToolDefinition, dict]]] = None,
        web_search: Optional[Union[WebSearchConfig, dict, bool]] = None,
        reasoning: Optional[bool] = None,
        reasoning_effort: Optional[str] = None,
        max_turns: int = 1,
        auto_execute: bool = True,
        use_history: bool = True,
    ) -> Response:
        """
        Have a chat conversation with the AI.
        
        Args:
            message: Your message (string) or list of messages for complex conversations
            model: AI model to use (default: "gpt-4o")
            temperature: Creativity level 0.0-2.0 (lower = more focused)
            max_tokens: Maximum response length
            system: System prompt to set AI personality/behavior
            tools: List of tools the AI can use
            web_search: Enable web search (True/False or detailed config)
            reasoning: Enable extended reasoning for complex problems
            reasoning_effort: Reasoning effort level ("low", "medium", "high")
            max_turns: Maximum conversation turns for tool execution
            auto_execute: Automatically execute tools
            use_history: Use conversation history for context
            
        Returns:
            Response object with text, parts, and metadata
            
        Example:
            ```python
            # Simple chat
            response = await agent.chat("What's the weather like?")
            print(response["text"])
            
            # With web search
            response = await agent.chat(
                "What's the latest news about AI?",
                web_search=True
            )
            
            # With custom system prompt
            response = await agent.chat(
                "Explain quantum physics",
                system="You are a physics professor. Explain things simply.",
                model="claude-sonnet-4"
            )
            ```
        """
        # Handle simple string message
        if isinstance(message, str):
            if use_history:
                self._history.add_user_message(message)
                messages = self._history.get_messages()
            else:
                messages = [{"role": "user", "content": message}]
        else:
            messages = message
        
        # Handle simple web_search boolean
        web_search_config = None
        if web_search is True:
            web_search_config = {"enabled": True}
        elif web_search is False:
            web_search_config = None
        elif web_search is not None:
            web_search_config = web_search
        
        # Make the request
        response = await self._client.responses.chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system=system,
            tools=tools,
            web_search=web_search_config,
            reasoning=reasoning,
            reasoning_effort=reasoning_effort,
            max_turns=max_turns,
            auto_execute=auto_execute,
        )
        
        # Add response to history if using history
        if use_history and isinstance(message, str):
            self._history.add_assistant_message(response["text"])
        
        return response
    
    async def stream(
        self,
        message: Union[str, List[Union[SimpleMessage, RichMessage, dict]]],
        *,
        model: str = "gpt-4o",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system: Optional[str] = None,
        tools: Optional[List[Union[ToolDefinition, dict]]] = None,
        web_search: Optional[Union[WebSearchConfig, dict, bool]] = None,
        reasoning: Optional[bool] = None,
        reasoning_effort: Optional[str] = None,
        auto_execute: bool = False,
        tool_executor: Optional[Callable[[str, Dict[str, Any]], Any]] = None,
        use_history: bool = True,
    ) -> AsyncGenerator[ManagedEvent, None]:
        """
        Stream a conversation with the AI, receiving real-time updates.
        
        Args:
            message: Your message (string) or list of messages
            model: AI model to use (default: "gpt-4o")
            temperature: Creativity level 0.0-2.0
            max_tokens: Maximum response length
            system: System prompt to set AI behavior
            tools: List of tools the AI can use
            web_search: Enable web search (True/False or detailed config)
            reasoning: Enable extended reasoning
            reasoning_effort: Reasoning effort level ("low", "medium", "high")
            auto_execute: Automatically execute server tools
            tool_executor: Function to execute tools: (name, args) -> result
            use_history: Use conversation history for context
            
        Yields:
            ManagedEvent objects (TextChunk, ToolRequest, ResponseComplete, etc.)
            
        Example:
            ```python
            async for event in agent.stream("Tell me a story"):
                if event["type"] == "text":
                    print(event["delta"], end="", flush=True)
                elif event["type"] == "complete":
                    print("\nDone!")
            ```
        """
        # Handle simple string message
        if isinstance(message, str):
            if use_history:
                self._history.add_user_message(message)
                messages = self._history.get_messages()
            else:
                messages = [{"role": "user", "content": message}]
        else:
            messages = message
        
        # Handle simple web_search boolean
        web_search_config = None
        if web_search is True:
            web_search_config = {"enabled": True}
        elif web_search is False:
            web_search_config = None
        elif web_search is not None:
            web_search_config = web_search
        
        # Collect response for history
        full_text = ""
        
        # Stream the response
        async for event in self._client.responses.stream(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system=system,
            tools=tools,
            web_search=web_search_config,
            reasoning=reasoning,
            reasoning_effort=reasoning_effort,
            auto_execute=auto_execute,
            tool_executor=tool_executor,
        ):
            # Collect text for history
            if event.get("type") == "text":
                full_text += event.get("delta", "")
            elif event.get("type") == "complete" and use_history and isinstance(message, str):
                # Add complete response to history
                response_text = event.get("text", full_text)
                if response_text:
                    self._history.add_assistant_message(response_text)
            
            yield event
    
    async def activate(
        self,
        agent_id: str,
        thread_id: str,
        room_id: Optional[str] = None,
    ):
        """
        Activate a configured agent in a specific thread.
        
        Args:
            agent_id: ID of the configured agent
            thread_id: Thread/conversation ID
            room_id: Optional room ID for group conversations
            
        Returns:
            Activation response with response_id and status
            
        Example:
            ```python
            activation = await agent.activate(
                agent_id="my_support_agent",
                thread_id="customer_123"
            )
            print(f"Activated: {activation.response_id}")
            ```
        """
        return await self._client.activations.submit(
            agent_id=agent_id,
            thread_id=thread_id,
            room_id=room_id,
        )
    
    def clear_history(self):
        """Clear the conversation history."""
        self._history = MessageHistory()
    
    def add_system_message(self, content: str):
        """
        Add a system message to set AI behavior.
        
        Args:
            content: System message content
        """
        self._history.add_system_message(content)
    
    def get_conversation(self) -> List[dict]:
        """
        Get the current conversation history.
        
        Returns:
            List of message dictionaries
        """
        return self._history.get_messages()
    
    async def close(self):
        """Close the agent and release resources."""
        await self._client.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Re-export commonly used types for convenience
__all__ = [
    "Agent",
    "ResponseMessage",
    "SimpleMessage", 
    "RichMessage",
    "MessageHistory",
    "AgentError",
    "ValidationError",
    "ServiceUnavailableError",
    "TimeoutError",
    "NotFoundError", 
    "RateLimitError",
    "InternalServerError",
]
