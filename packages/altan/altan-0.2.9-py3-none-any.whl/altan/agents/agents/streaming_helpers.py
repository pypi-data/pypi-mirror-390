"""
Streaming Helper Functions

High-level utilities for common streaming patterns.
Makes it easier to work with SSE streams.
"""

import asyncio
import logging
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Union

from .managed_types import ManagedEvent, Response, ResponseComplete
from .types import SimpleMessage, RichMessage
from .history import MessageHistory

logger = logging.getLogger(__name__)


async def stream_and_accumulate(
    client: Any,
    messages: Union[MessageHistory, List[Union[SimpleMessage, RichMessage, dict]]],
    **kwargs
) -> Response:
    """
    Stream a response and return the complete accumulated result.
    
    Convenience function that handles all the streaming boilerplate.
    Equivalent to chat() but uses streaming under the hood.
    
    Args:
        client: ResponsesClient instance
        messages: Messages or MessageHistory
        **kwargs: Additional arguments passed to stream()
        
    Returns:
        Complete Response object
        
    Example:
        ```python
        response = await stream_and_accumulate(
            client.responses,
            messages=history,
            model="gpt-4o",
        )
        print(response["text"])
        ```
    """
    full_text = ""
    full_thinking = ""
    all_parts = []
    tool_calls = []
    response_data = {}
    
    async for event in client.stream(messages=messages, **kwargs):
        if event["type"] == "text":
            full_text += event.get("delta", "")
        elif event["type"] == "thinking":
            full_thinking += event.get("delta", "")
        elif event["type"] == "complete":
            # Use complete event data
            return event  # Already a Response
    
    # Build response if complete event wasn't received
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


async def stream_with_callback(
    client: Any,
    messages: Union[MessageHistory, List[Union[SimpleMessage, RichMessage, dict]]],
    on_text: Optional[Callable[[str], None]] = None,
    on_thinking: Optional[Callable[[str], None]] = None,
    on_tool_request: Optional[Callable[[Dict[str, Any]], None]] = None,
    on_tool_result: Optional[Callable[[Dict[str, Any]], None]] = None,
    on_complete: Optional[Callable[[Response], None]] = None,
    on_error: Optional[Callable[[str], None]] = None,
    **kwargs
) -> Response:
    """
    Stream a response with callbacks for each event type.
    
    Makes it easy to handle different event types without manual type checking.
    Callbacks are called synchronously during streaming.
    
    Args:
        client: ResponsesClient instance
        messages: Messages or MessageHistory
        on_text: Called for each text chunk (receives delta string)
        on_thinking: Called for each thinking chunk (receives delta string)
        on_tool_request: Called for tool requests (receives tool dict)
        on_tool_result: Called for tool results (receives result dict)
        on_complete: Called when response completes (receives Response)
        on_error: Called on error (receives error message)
        **kwargs: Additional arguments passed to stream()
        
    Returns:
        Complete Response object
        
    Example:
        ```python
        def print_chunk(delta: str):
            print(delta, end="", flush=True)
        
        response = await stream_with_callback(
            client.responses,
            messages=history,
            model="gpt-4o",
            on_text=print_chunk,
            on_complete=lambda r: print(f"\n\nDone! Used {r['models_used']}"),
        )
        ```
    """
    response: Optional[Response] = None
    
    try:
        async for event in client.stream(messages=messages, **kwargs):
            event_type = event.get("type")
            
            if event_type == "text" and on_text:
                on_text(event.get("delta", ""))
            
            elif event_type == "thinking" and on_thinking:
                on_thinking(event.get("delta", ""))
            
            elif event_type == "tool_request" and on_tool_request:
                on_tool_request(event)
            
            elif event_type == "tool_result" and on_tool_result:
                on_tool_result(event)
            
            elif event_type == "complete":
                response = event
                if on_complete:
                    on_complete(response)
            
            elif event_type == "error":
                error_msg = event.get("error_message", "Unknown error")
                if on_error:
                    on_error(error_msg)
                raise Exception(f"Stream error: {error_msg}")
        
        if response is None:
            raise Exception("Stream ended without complete event")
        
        return response
    
    except Exception as e:
        if on_error:
            on_error(str(e))
        raise


async def stream_to_list(
    client: Any,
    messages: Union[MessageHistory, List[Union[SimpleMessage, RichMessage, dict]]],
    **kwargs
) -> List[ManagedEvent]:
    """
    Collect all stream events into a list.
    
    Useful for debugging, testing, or when you need all events at once.
    
    Args:
        client: ResponsesClient instance
        messages: Messages or MessageHistory
        **kwargs: Additional arguments passed to stream()
        
    Returns:
        List of all events from the stream
        
    Example:
        ```python
        events = await stream_to_list(
            client.responses,
            messages=history,
            model="gpt-4o",
        )
        
        # Analyze events
        text_events = [e for e in events if e["type"] == "text"]
        print(f"Received {len(text_events)} text chunks")
        ```
    """
    events: List[ManagedEvent] = []
    
    async for event in client.stream(messages=messages, **kwargs):
        events.append(event)
    
    return events


async def stream_text_only(
    client: Any,
    messages: Union[MessageHistory, List[Union[SimpleMessage, RichMessage, dict]]],
    **kwargs
) -> AsyncGenerator[str, None]:
    """
    Stream only text deltas, filtering out other event types.
    
    Simplest streaming interface - just yields text chunks.
    
    Args:
        client: ResponsesClient instance
        messages: Messages or MessageHistory
        **kwargs: Additional arguments passed to stream()
        
    Yields:
        Text delta strings
        
    Example:
        ```python
        async for chunk in stream_text_only(client.responses, messages=history, model="gpt-4o"):
            print(chunk, end="", flush=True)
        ```
    """
    async for event in client.stream(messages=messages, **kwargs):
        if event.get("type") == "text":
            yield event.get("delta", "")


async def stream_with_timeout(
    client: Any,
    messages: Union[MessageHistory, List[Union[SimpleMessage, RichMessage, dict]]],
    timeout: float,
    **kwargs
) -> Response:
    """
    Stream with a timeout for the entire operation.
    
    Raises asyncio.TimeoutError if streaming takes longer than timeout.
    
    Args:
        client: ResponsesClient instance
        messages: Messages or MessageHistory
        timeout: Maximum time in seconds to wait for complete response
        **kwargs: Additional arguments passed to stream()
        
    Returns:
        Complete Response object
        
    Raises:
        asyncio.TimeoutError: If streaming exceeds timeout
        
    Example:
        ```python
        try:
            response = await stream_with_timeout(
                client.responses,
                messages=history,
                model="gpt-4o",
                timeout=30.0,  # 30 second max
            )
        except asyncio.TimeoutError:
            print("Response took too long!")
        ```
    """
    return await asyncio.wait_for(
        stream_and_accumulate(client, messages, **kwargs),
        timeout=timeout
    )


async def stream_with_progress(
    client: Any,
    messages: Union[MessageHistory, List[Union[SimpleMessage, RichMessage, dict]]],
    on_progress: Callable[[int, int], None],
    update_interval: float = 0.5,
    **kwargs
) -> Response:
    """
    Stream with periodic progress updates.
    
    Calls progress callback with (tokens_so_far, estimated_total) periodically.
    Useful for showing progress bars or status indicators.
    
    Args:
        client: ResponsesClient instance
        messages: Messages or MessageHistory
        on_progress: Callback(current_tokens, estimated_total)
        update_interval: How often to call callback (seconds)
        **kwargs: Additional arguments passed to stream()
        
    Returns:
        Complete Response object
        
    Example:
        ```python
        def show_progress(current, total):
            percent = (current / total * 100) if total > 0 else 0
            print(f"\rProgress: {percent:.1f}%", end="")
        
        response = await stream_with_progress(
            client.responses,
            messages=history,
            model="gpt-4o",
            on_progress=show_progress,
        )
        ```
    """
    token_count = 0
    last_update = asyncio.get_event_loop().time()
    
    response: Optional[Response] = None
    
    async for event in client.stream(messages=messages, **kwargs):
        if event.get("type") == "text":
            # Rough token estimate (4 chars = 1 token)
            delta = event.get("delta", "")
            token_count += len(delta) // 4
            
            # Update progress periodically
            now = asyncio.get_event_loop().time()
            if now - last_update >= update_interval:
                # Estimate total based on max_tokens or use rough estimate
                estimated_total = kwargs.get("max_tokens", token_count * 2)
                on_progress(token_count, estimated_total)
                last_update = now
        
        elif event.get("type") == "complete":
            response = event
            # Final progress update
            final_tokens = sum(
                u.get("total_tokens", 0)
                for u in response.get("usage", [])
            )
            if final_tokens > 0:
                on_progress(final_tokens, final_tokens)
    
    if response is None:
        raise Exception("Stream ended without complete event")
    
    return response

