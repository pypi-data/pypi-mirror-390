"""Client utilities for SDK cookbooks."""

import sys
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

# Add SDK to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../.."))

from altan.agents import AgentClient
from altan.agents.agents.types import SimpleMessage, RichMessage


# Global client instance
_client: Optional[AgentClient] = None


def get_client(base_url: str = "http://localhost:8000", timeout: float = 120.0) -> AgentClient:
    """Get or create the global client instance."""
    global _client
    if _client is None:
        _client = AgentClient(base_url=base_url, timeout=timeout)
    return _client


def format_messages(messages: List[Dict[str, str]]) -> List[SimpleMessage]:
    """Convert simple dict messages to typed SimpleMessage format."""
    return [
        SimpleMessage(role=msg["role"], content=msg["content"])  # type: ignore
        for msg in messages
    ]


@dataclass
class MessageHistory:
    """Helper class to manage conversation history."""
    
    messages: List[SimpleMessage] = field(default_factory=list)
    max_history: int = 50
    
    def add_user_message(self, content: str) -> None:
        """Add a user message to history."""
        self.messages.append(SimpleMessage(role="user", content=content))  # type: ignore
        self._trim_history()
    
    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to history."""
        self.messages.append(SimpleMessage(role="assistant", content=content))  # type: ignore
        self._trim_history()
    
    def add_system_message(self, content: str) -> None:
        """Add a system message to history."""
        self.messages.append(SimpleMessage(role="system", content=content))  # type: ignore
        self._trim_history()
    
    def get_messages(self) -> List[SimpleMessage]:
        """Get all messages in history."""
        return self.messages.copy()
    
    def clear(self) -> None:
        """Clear all messages."""
        self.messages = []
    
    def _trim_history(self) -> None:
        """Trim history to max length, keeping system messages."""
        if len(self.messages) <= self.max_history:
            return
        
        # Keep system messages and recent messages
        system_messages = [m for m in self.messages if m["role"] == "system"]
        other_messages = [m for m in self.messages if m["role"] != "system"]
        
        # Keep most recent messages
        keep_count = self.max_history - len(system_messages)
        other_messages = other_messages[-keep_count:]
        
        self.messages = system_messages + other_messages
    
    def get_last_assistant_message(self) -> Optional[str]:
        """Get the content of the last assistant message."""
        for msg in reversed(self.messages):
            if msg["role"] == "assistant":
                return msg["content"]  # type: ignore
        return None
    
    def add_rich_assistant_message(self, parts: List[Dict[str, Any]], full_text: str = "") -> None:
        """
        Add an assistant message with full parts structure (RichMessage format).
        
        This preserves tool calls, thinking parts, and other structured data.
        Use this when you need to maintain the complete message structure.
        
        Args:
            parts: List of message parts from streaming events
            full_text: Optional text summary (for simple display)
        """
        from agents.types import RichMessage
        
        # If we have parts, use RichMessage format
        if parts:
            rich_msg: RichMessage = {
                "role": "assistant",
                "parts": parts,  # type: ignore
            }
            if full_text:
                rich_msg["text"] = full_text
            self.messages.append(rich_msg)  # type: ignore
        else:
            # Fallback to simple message
            self.add_assistant_message(full_text)

