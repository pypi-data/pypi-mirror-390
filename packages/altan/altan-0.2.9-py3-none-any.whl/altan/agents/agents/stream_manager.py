"""
Stream manager for processing raw events into managed high-level events.

This module provides the core logic for converting low-level SSE events into
simplified, easy-to-use managed events.
"""

import json
import logging
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Union

from .types import StreamEvent
from .managed_types import (
    ManagedEvent,
    TextChunk,
    ThinkingChunk,
    ToolRequest,
    ToolResult,
    ResponseComplete,
    ResponseStarted,
    ResponseError,
)

logger = logging.getLogger(__name__)


# Valid fields for each part type (based on TypedDict definitions)
TEXT_PART_FIELDS = {
    "id", "type", "text", "order", "block_order", "provider", "provider_id",
    "provider_item_type", "created_at", "finished_at", "annotations"
}

MEDIA_PART_FIELDS = {
    "id", "type", "url", "mime_type", "file_name", "file_size", "order",
    "block_order", "meta_data", "created_at", "finished_at"
}

TOOL_PART_FIELDS = {
    "id", "type", "tool_call_id", "tool_id", "name", "input", "arguments",
    "result", "error", "order", "block_order", "act_now", "act_done",
    "intent", "use_intent", "provider", "provider_id", "provider_item_type",
    "server_label", "approval_request_id", "citations", "sources", "actions",
    "created_at", "finished_at"
}

THINKING_PART_FIELDS = {
    "id", "type", "text", "status", "order", "block_order", "provider",
    "provider_id", "provider_item_type", "signature", "summary",
    "encrypted_content", "created_at", "finished_at"
}


def _clean_message_part(part: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean a message part to only include fields defined in TypedDict.
    
    Removes extra fields like event_name, room_member_id, member_id, response_id,
    agent_id, name (when not a tool), etc. that are event metadata but not part data.
    """
    part_type = part.get("type")
    
    if part_type == "text":
        valid_fields = TEXT_PART_FIELDS
    elif part_type == "media":
        valid_fields = MEDIA_PART_FIELDS
    elif part_type == "tool":
        valid_fields = TOOL_PART_FIELDS
    elif part_type == "thinking":
        valid_fields = THINKING_PART_FIELDS
    else:
        # Unknown type, return as-is
        return part
    
    # Filter to only valid fields
    cleaned = {k: v for k, v in part.items() if k in valid_fields}
    
    return cleaned


class StreamManager:
    """
    Manages streaming events and converts them to high-level managed events.
    
    Handles:
    - Text/thinking part accumulation
    - Tool call detection and execution
    - Response completion
    - Error handling
    
    Key Insight:
    - Server-executed tools (web_search, MCP): Results arrive in message_part.completed
    - Client-executed tools: Need to yield tool_request for SDK user to execute
    """
    
    def __init__(
        self,
        auto_execute: bool = False,
        tool_executor: Optional[Callable[[str, Dict[str, Any]], Any]] = None,
    ):
        """
        Initialize stream manager.
        
        Args:
            auto_execute: Whether to auto-execute client tools
            tool_executor: Function to execute tools (name, args) -> result
        """
        self.auto_execute = auto_execute
        self.tool_executor = tool_executor
        
        # Content accumulation
        self._text_parts: Dict[str, str] = {}  # part_id -> accumulated text
        self._thinking_parts: Dict[str, str] = {}  # part_id -> accumulated thinking
        
        # Tool tracking with lifecycle states
        self._tool_parts: Dict[str, Dict[str, Any]] = {}  # part_id -> tool state
        self._completed_tool_ids: set = set()  # Track which tools have been processed
        
        # All parts for final response
        self._all_parts: List[Dict[str, Any]] = []
        
        # Current streaming context
        self._current_part_id: Optional[str] = None
        self._current_part_type: Optional[str] = None
        
        # Response metadata
        self._response_id: Optional[str] = None
        self._context_id: Optional[str] = None
        self._models_used: List[str] = []
        self._usage: List[Dict[str, Any]] = []
    
    async def process_stream(
        self,
        raw_stream: AsyncGenerator[StreamEvent, None],
    ) -> AsyncGenerator[ManagedEvent, None]:
        """
        Process raw event stream into managed events.
        
        Args:
            raw_stream: Raw SSE event stream from create_stream()
            
        Yields:
            ManagedEvent objects (TextChunk, ToolRequest, ResponseComplete, etc.)
        """
        try:
            async for event in raw_stream:
                event_type = event.get("event_type", "")
                data = event.get("data", {})
                
                if event_type in ["message_part.added", "message_part.completed"]:
                    logger.info(f"Message part {event_type}: {data.get("type", "unknown")}")
                elif event_type in ["response.started", "response.completed", "response.failed"]:
                    logger.info(f"Response {event_type}: {data.get("response_id", "unknown")}")
                elif event_type in ["response.error"]:
                    logger.info(f"Response error: {data.get("error_message", "unknown")}")
                elif event_type in ["message_part.updated"]:
                    pass
                else:
                    logger.info(f"Received raw event: {event_type} with data keys: {list(data.keys()) if isinstance(data, dict) else 'not-a-dict'}")

                # Process event and yield managed events
                async for managed_event in self._process_event(event_type, data):
                    yield managed_event
        
        except Exception as e:
            logger.error(f"Stream processing error: {e}", exc_info=True)
            error_event: ResponseError = {
                "type": "error",
                "error_message": str(e),
                "error_code": "stream_error",
                "retryable": False,
            }
            yield error_event
    
    async def _process_event(
        self,
        event_type: str,
        data: Dict[str, Any],
    ) -> AsyncGenerator[ManagedEvent, None]:
        """Process a single raw event and yield managed events."""
        
        logger.debug(f"Processing event: {event_type}")
        
        # Response lifecycle events
        if event_type == "response.started":
            self._response_id = data.get("response_id")
            started_event: ResponseStarted = {
                "type": "started",
                "response_id": data.get("response_id", ""),
                "agent_id": data.get("agent_id", ""),
            }
            yield started_event
        
        elif event_type == "response.completed":
            # Process any accumulated tool parts before completing
            async for tool_event in self._process_accumulated_tools():
                yield tool_event
            
            # Build final complete event
            complete_event = await self._build_complete_event(data)
            yield complete_event
        
        elif event_type == "response.failed":
            error_event: ResponseError = {
                "type": "error",
                "error_message": data.get("error_message", "Unknown error"),
                "error_code": data.get("error_code", ""),
                "retryable": data.get("retryable", False),
            }
            yield error_event
        
        # Message part events
        elif event_type == "message_part.added":
            part_type = data.get("type")
            part_id = data.get("id")
            
            if not part_id:
                return
            
            self._current_part_id = part_id
            self._current_part_type = part_type
            
            # Initialize content accumulators
            if part_type == "text":
                self._text_parts[part_id] = ""
            elif part_type == "thinking":
                self._thinking_parts[part_id] = ""
            elif part_type == "tool":
                # Initialize tool state tracking
                self._tool_parts[part_id] = {
                    "part_id": part_id,
                    "tool_call_id": data.get("tool_call_id", part_id),
                    "name": data.get("name", ""),
                    "tool_type": data.get("tool_type", "server"),
                    "tool_id": data.get("tool_id", ""),
                    "server_label": data.get("server_label", ""),
                    "arguments_str": "",  # Accumulated from streaming
                    "is_completed": False,
                }
                logger.info(f"Tool part added: {data.get('name')} (id={part_id}, type={data.get('tool_type', 'server')})")
            
            # Store complete part data for final response
            self._all_parts.append(data.copy())
            logger.debug(f"Part stored: {part_type} (id={part_id}, order={data.get('order')}, block={data.get('block_order')})")
        
        elif event_type == "message_part.updated":
            delta = data.get("delta", "")
            part_type = data.get("type") or self._current_part_type
            part_id = data.get("id") or self._current_part_id
            
            if not (delta and part_type and part_id):
                return
            
            if part_type == "text":
                # Accumulate and stream text
                self._text_parts[part_id] = self._text_parts.get(part_id, "") + delta
                yield TextChunk(type="text", delta=delta)
            
            elif part_type == "thinking":
                # Accumulate and stream thinking
                self._thinking_parts[part_id] = self._thinking_parts.get(part_id, "") + delta
                yield ThinkingChunk(type="thinking", delta=delta)
            
            elif part_type == "tool":
                # Accumulate tool arguments (JSON string being streamed)
                if part_id in self._tool_parts:
                    self._tool_parts[part_id]["arguments_str"] += delta
        
        elif event_type == "message_part.completed":
            part_type = data.get("type")
            part_id = data.get("id")
            
            if not part_id:
                return
            
            # Update stored part with complete data
            updated_part = None
            for part in self._all_parts:
                if part.get("id") == part_id:
                    part.update(data)
                    updated_part = part
                    break
            
            # Handle tool completion - pass the full updated part
            if part_type == "tool" and part_id in self._tool_parts:
                full_part_data = updated_part if updated_part else data
                async for event in self._handle_tool_completed(part_id, full_part_data):
                    yield event
    
    async def _process_accumulated_tools(
        self,
    ) -> AsyncGenerator[Union[ToolRequest, ToolResult], None]:
        """
        Process any remaining incomplete tools at response completion.
        
        This is a safety net for tools that didn't receive message_part.completed.
        In normal flow, tools are processed when completed.
        """
        incomplete_tools = [
            (part_id, tool) for part_id, tool in self._tool_parts.items()
            if not tool.get("is_completed") and part_id not in self._completed_tool_ids
        ]
        
        if not incomplete_tools:
            return
        
        logger.warning(f"Processing {len(incomplete_tools)} incomplete tools at response end")
        
        for part_id, tool_state in incomplete_tools:
            logger.warning(f"Incomplete tool: {tool_state.get('name')} (id={part_id})")
            # Mark as completed to avoid reprocessing
            self._completed_tool_ids.add(part_id)
            # Process with what we have
            async for event in self._process_tool(part_id, tool_state, {}):
                yield event
    
    async def _handle_tool_completed(
        self,
        part_id: str,
        completed_data: Dict[str, Any],
    ) -> AsyncGenerator[Union[ToolRequest, ToolResult], None]:
        """
        Handle tool part completion event.
        
        Key logic:
        - Server-executed tools: Already have results, don't yield tool_request
        - Client-executed tools: Need execution, yield tool_request or auto-execute
        """
        if part_id in self._completed_tool_ids:
            logger.debug(f"Tool {part_id} already processed, skipping")
            return
        
        tool_state = self._tool_parts.get(part_id)
        if not tool_state:
            logger.warning(f"Tool state not found for part_id={part_id}")
            return
        
        # Mark as completed
        tool_state["is_completed"] = True
        self._completed_tool_ids.add(part_id)
        
        # Process the tool
        async for event in self._process_tool(part_id, tool_state, completed_data):
            yield event
    
    async def _process_tool(
        self,
        part_id: str,
        tool_state: Dict[str, Any],
        completed_data: Dict[str, Any],
    ) -> AsyncGenerator[Union[ToolRequest, ToolResult], None]:
        """
        Process a tool part - core logic for tool handling.
        
        Determines if tool needs client execution or already has server result.
        """
        tool_name = tool_state.get("name") or completed_data.get("name", "")
        tool_call_id = tool_state.get("tool_call_id", part_id)
        tool_type = tool_state.get("tool_type", "server")
        
        if not tool_name:
            logger.warning(f"Tool part {part_id} missing name, skipping")
            return
        
        # Parse arguments with elegant priority
        arguments = self._parse_tool_arguments(tool_state, completed_data)
        
        # Check if server already executed this tool
        # Look for result indicators: result, sources, citations, actions
        has_server_result = any(
            field in completed_data 
            for field in ["result", "sources", "citations", "actions"]
        )
        
        if tool_type == "server":
            # Server-executed tool (web_search, MCP, etc.)
            if has_server_result:
                logger.info(f"Server tool completed with results: {tool_name} (id={part_id})")
            else:
                logger.info(f"Server tool completed (results in parts): {tool_name} (id={part_id})")
            # Never yield tool_request for server tools - they execute on backend
            # Results are in message parts
            self._store_tool_call(tool_call_id, tool_name, arguments, tool_state)
        
        elif self.auto_execute and tool_type == "client" and self.tool_executor:
            # Client tool with auto-execution
            logger.info(f"Auto-executing client tool: {tool_name} (id={part_id})")
            async for event in self._execute_and_yield_tool(tool_call_id, tool_name, arguments):
                yield event
            self._store_tool_call(tool_call_id, tool_name, arguments, tool_state)
        
        else:
            # Client tool needs manual execution - yield tool_request
            logger.info(f"Yielding tool request: {tool_name} (id={part_id}, type={tool_type})")
            yield self._create_tool_request(tool_call_id, tool_name, arguments, tool_state)
            self._store_tool_call(tool_call_id, tool_name, arguments, tool_state)
    
    def _parse_tool_arguments(
        self,
        tool_state: Dict[str, Any],
        completed_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Parse tool arguments with elegant priority handling.
        
        Priority:
        1. completed_data['arguments'] as dict (final, validated)
        2. completed_data['arguments'] as string (parse JSON)
        3. tool_state['arguments_str'] (accumulated from streaming)
        4. Empty dict fallback
        """
        # Priority 1: Dict from completed event
        if "arguments" in completed_data:
            arg = completed_data["arguments"]
            if isinstance(arg, dict):
                return arg
            if isinstance(arg, str):
                return self._safe_json_parse(arg, "completed_data.arguments")
        
        # Priority 2: Accumulated string from streaming
        if "arguments_str" in tool_state:
            return self._safe_json_parse(tool_state["arguments_str"], "tool_state.arguments_str")
        
        # Fallback
        return {}
    
    def _safe_json_parse(self, json_str: str, source: str) -> Dict[str, Any]:
        """
        Safely parse JSON string, return empty dict on error.
        
        Handles malformed formats like: {}{"query": "..."} by trying to extract valid JSON.
        """
        if not json_str:
            return {}
        
        # Try direct parse first
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        # Handle malformed format: {}{"query": "..."} - extract the second JSON object
        # This happens when arguments accumulate with a prefix
        if json_str.startswith("{}") and len(json_str) > 2:
            try:
                return json.loads(json_str[2:])  # Skip the empty {} prefix
            except json.JSONDecodeError:
                pass
        
        # Try to find the first valid JSON object in the string
        for i in range(len(json_str)):
            if json_str[i] == '{':
                try:
                    result = json.loads(json_str[i:])
                    if result and isinstance(result, dict):
                        logger.debug(f"Extracted JSON from position {i} in {source}")
                        return result
                except json.JSONDecodeError:
                    continue
        
        # Give up - log and return empty dict
        logger.warning(f"Failed to parse {source}: {json_str[:100]}...")
        return {}
    
    def _store_tool_call(
        self,
        tool_call_id: str,
        tool_name: str,
        arguments: Dict[str, Any],
        tool_state: Dict[str, Any],
    ) -> None:
        """Store tool call info for final response."""
        if not hasattr(self, "_final_tool_calls"):
            self._final_tool_calls: List[Dict[str, Any]] = []
        
        self._final_tool_calls.append({
            "id": tool_call_id,
            "name": tool_name,
            "args": arguments,
            "tool_type": tool_state.get("tool_type", "server"),
            "tool_id": tool_state.get("tool_id", ""),
        })
    
    def _create_tool_request(
        self,
        tool_call_id: str,
        tool_name: str,
        arguments: Dict[str, Any],
        tool_state: Dict[str, Any],
    ) -> ToolRequest:
        """Create a tool request event."""
        return ToolRequest(
            type="tool_request",
            id=tool_call_id,
            name=tool_name,
            args=arguments,
            tool_type=tool_state.get("tool_type", "server"),
            tool_id=tool_state.get("tool_id", ""),
            server_label=tool_state.get("server_label", ""),
        )
    
    async def _execute_and_yield_tool(
        self,
        tool_call_id: str,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> AsyncGenerator[ToolResult, None]:
        """Execute tool and yield result event."""
        try:
            result = await self._execute_tool(tool_name, arguments)
            logger.debug(f"Tool {tool_name} executed: {str(result)[:100]}")
            
            yield ToolResult(
                type="tool_result",
                id=tool_call_id,
                name=tool_name,
                result=result,
                success=True,
            )
        except Exception as e:
            logger.error(f"Tool execution failed for {tool_name}: {e}", exc_info=True)
            yield ToolResult(
                type="tool_result",
                id=tool_call_id,
                name=tool_name,
                error=str(e),
                success=False,
            )
    
    async def _execute_tool(
        self,
        name: str,
        args: Dict[str, Any],
    ) -> Any:
        """Execute a tool using the provided executor."""
        if not self.tool_executor:
            raise ValueError("No tool executor provided")
        
        # Check if executor is async
        import inspect
        if inspect.iscoroutinefunction(self.tool_executor):
            return await self.tool_executor(name, args)
        else:
            return self.tool_executor(name, args)
    
    async def _build_complete_event(
        self,
        data: Dict[str, Any],
    ) -> ResponseComplete:
        """Build the final complete event with all accumulated data."""
        
        # Ensure all parts have their accumulated content
        for part in self._all_parts:
            part_id = part.get("id")
            part_type = part.get("type")
            
            if part_type == "text" and part_id in self._text_parts:
                part["text"] = self._text_parts[part_id]
            elif part_type == "thinking" and part_id in self._thinking_parts:
                part["text"] = self._thinking_parts[part_id]
        
        # Clean all parts to match TypedDict definitions
        cleaned_parts = [_clean_message_part(part) for part in self._all_parts]
        
        # Combine all text/thinking
        full_text = "".join(self._text_parts.values())
        full_thinking = "".join(self._thinking_parts.values())
        
        # Get final tool calls
        tool_calls = getattr(self, "_final_tool_calls", [])
        
        # Build complete event
        return ResponseComplete(
            type="complete",
            text=full_text,
            thinking=full_thinking,
            parts=cleaned_parts,
            tool_calls=tool_calls,
            models_used=data.get("models_used", self._models_used),
            usage=data.get("usage", self._usage),
            response_id=data.get("response_id", self._response_id or ""),
            context_id=self._context_id or "",
        )
    
    def reset(self) -> None:
        """Reset state for new stream."""
        self._text_parts = {}
        self._thinking_parts = {}
        self._tool_parts = {}
        self._completed_tool_ids = set()
        self._all_parts = []
        self._current_part_id = None
        self._current_part_type = None
        self._response_id = None
        self._context_id = None
        self._models_used = []
        self._usage = []
        if hasattr(self, "_final_tool_calls"):
            self._final_tool_calls = []

