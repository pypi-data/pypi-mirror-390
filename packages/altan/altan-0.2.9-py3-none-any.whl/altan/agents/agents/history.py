"""
Message history management for conversations.

Provides a convenient way to manage conversation context with support for
both simple messages and rich message parts.
"""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field

from .types import SimpleMessage, RichMessage, InputMessage
from .managed_types import Response, ResponseComplete


@dataclass
class MessageHistory:
    """
    Helper class to manage conversation history.
    
    Supports both simple messages (role + content) and rich messages (with parts).
    Automatically handles message trimming and provides convenient methods.
    
    Example:
        ```python
        history = MessageHistory()
        history.add_user("Hello!")
        
        # Stream response
        async for event in client.responses.stream(history, model="gpt-4o"):
            if event["type"] == "text":
                print(event["delta"], end="")
            elif event["type"] == "complete":
                history.add_assistant(event)
        ```
    """
    
    messages: List[Union[SimpleMessage, RichMessage, Dict[str, Any]]] = field(default_factory=list)
    max_history: int = 50
    
    # ========================================================================
    # Simple API (most common)
    # ========================================================================
    
    def add_user(self, content: str) -> None:
        """
        Add a user message to history.
        
        Args:
            content: Message text content
        """
        self.add_user_message(content)
    
    def add_assistant(self, content: Union[str, Response, ResponseComplete, Dict[str, Any]]) -> None:
        """
        Add an assistant message to history.
        
        Accepts multiple formats for convenience:
        - String: Simple text message
        - Response/ResponseComplete: From managed API
        - Dict: Raw message dict
        
        Args:
            content: Message content in various formats
        """
        if isinstance(content, str):
            self.add_assistant_message(content)
        elif isinstance(content, dict):
            # Check if it's a Response/ResponseComplete event
            if content.get("type") == "complete":
                # Extract parts (preferred) or fallback to text
                parts = content.get("parts", [])
                text = content.get("text", "")
                if parts:
                    # Only use parts (not text) to ensure mutual exclusivity
                    self.add_rich_assistant_message(parts)
                else:
                    self.add_assistant_message(text)
            elif "parts" in content:
                # RichMessage or Response object with parts
                parts = content.get("parts", [])
                text = content.get("text", "")
                if parts:
                    self.add_rich_assistant_message(parts)
                else:
                    self.add_assistant_message(text)
            elif "text" in content or "content" in content:
                # Simple message or Response without parts
                text = content.get("text") or content.get("content", "")
                self.add_assistant_message(str(text))
            else:
                # Raw message dict - append as-is
                self.messages.append(content)
                self._trim_history()
    
    def add_system(self, content: str) -> None:
        """
        Add a system message to history.
        
        Args:
            content: System prompt or instruction
        """
        self.add_system_message(content)
    
    # ========================================================================
    # Standard API (backward compatible)
    # ========================================================================
    
    def add_user_message(self, content: str) -> None:
        """Add a user message to history."""
        msg: SimpleMessage = {"role": "user", "content": content}  # type: ignore
        self.messages.append(msg)
        self._trim_history()
    
    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to history."""
        msg: SimpleMessage = {"role": "assistant", "content": content}  # type: ignore
        self.messages.append(msg)
        self._trim_history()
    
    def add_system_message(self, content: str) -> None:
        """Add a system message to history."""
        msg: SimpleMessage = {"role": "system", "content": content}  # type: ignore
        self.messages.append(msg)
        self._trim_history()
    
    def add_rich_assistant_message(
        self, 
        parts: List[Dict[str, Any]], 
        text: str = ""
    ) -> None:
        """
        Add an assistant message with full parts structure (RichMessage format).
        
        This preserves tool calls, thinking parts, and other structured data.
        Use this when you need to maintain the complete message structure.
        
        Args:
            parts: List of message parts from streaming events
            text: Optional text summary (for simple display - only used if no parts)
        """
        if parts:
            # When parts exist, only include parts (not text)
            # This ensures text and parts are mutually exclusive
            rich_msg: RichMessage = {
                "role": "assistant",
                "parts": parts,  # type: ignore
            }
            self.messages.append(rich_msg)
        else:
            # Fallback to simple message with text only
            self.add_assistant_message(text)
        self._trim_history()
    
    # ========================================================================
    # Tool Result Support
    # ========================================================================
    
    def add_tool_result(
        self,
        tool_call_id: str,
        result: Any,
        name: Optional[str] = None
    ) -> None:
        """
        Add a tool result to history.
        
        This is useful for manual tool execution workflows where you need to
        send tool results back to the AI.
        
        Args:
            tool_call_id: ID of the tool call
            result: Tool execution result
            name: Optional tool name
        """
        # Find the last assistant message with parts
        for i in range(len(self.messages) - 1, -1, -1):
            msg = self.messages[i]
            if msg.get("role") == "assistant" and "parts" in msg:
                # Add tool result part
                parts = msg.get("parts", [])
                
                # Find the tool part and update it
                for part in parts:
                    if part.get("type") == "tool" and part.get("tool_call_id") == tool_call_id:
                        part["result"] = result
                        return
                
                # If not found, create a new tool result part
                tool_part = {
                    "type": "tool",
                    "tool_call_id": tool_call_id,
                    "result": result,
                }
                if name:
                    tool_part["name"] = name
                parts.append(tool_part)
                return
        
        # If no assistant message found, create a new one with the tool result
        rich_msg: RichMessage = {
            "role": "assistant",
            "parts": [{  # type: ignore
                "type": "tool",
                "tool_call_id": tool_call_id,
                "result": result,
                "name": name or "",
            }],
        }
        self.messages.append(rich_msg)
        self._trim_history()
    
    # ========================================================================
    # Query Methods
    # ========================================================================
    
    def get_messages(self) -> List[Union[SimpleMessage, RichMessage, Dict[str, Any]]]:
        """Get all messages in history."""
        return self.messages.copy()
    
    def get_last_assistant_message(self) -> Optional[str]:
        """Get the content of the last assistant message."""
        for msg in reversed(self.messages):
            if msg.get("role") == "assistant":
                # Try to get text field first (RichMessage), then content (SimpleMessage)
                return msg.get("text") or msg.get("content")  # type: ignore
        return None
    
    def get_last_user_message(self) -> Optional[str]:
        """Get the content of the last user message."""
        for msg in reversed(self.messages):
            if msg.get("role") == "user":
                return msg.get("content")  # type: ignore
        return None
    
    def has_messages(self) -> bool:
        """Check if history has any messages."""
        return len(self.messages) > 0
    
    def count(self) -> int:
        """Get the number of messages in history."""
        return len(self.messages)
    
    # ========================================================================
    # Management Methods
    # ========================================================================
    
    def clear(self) -> None:
        """Clear all messages."""
        self.messages = []
    
    def _trim_history(self) -> None:
        """Trim history to max length, keeping system messages."""
        if len(self.messages) <= self.max_history:
            return
        
        # Keep system messages and recent messages
        system_messages = [m for m in self.messages if m.get("role") == "system"]
        other_messages = [m for m in self.messages if m.get("role") != "system"]
        
        # Keep most recent messages
        keep_count = self.max_history - len(system_messages)
        other_messages = other_messages[-keep_count:]
        
        self.messages = system_messages + other_messages
    
    def __len__(self) -> int:
        """Get the number of messages in history."""
        return len(self.messages)
    
    def __iter__(self):
        """Iterate over messages."""
        return iter(self.messages)

