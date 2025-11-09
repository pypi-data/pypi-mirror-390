"""
Activations API Client

Client for the event-driven agent activations API.
"""

import logging
from typing import AsyncGenerator, Dict, List, Optional

from .base_client import BaseClient
from .types import (
    ActivationRequest,
    ActivationResponse,
    CancellationResponse,
    BulkCancellationResponse,
    ThreadStatusResponse,
    ThreadActivationsResponse,
    ActivationStatsResponse,
    ActivationInfo,
    SSEEvent,
)

logger = logging.getLogger(__name__)


class ActivationsClient:
    """Client for agent activations API."""
    
    def __init__(self, base_client: BaseClient):
        """
        Initialize activations client.
        
        Args:
            base_client: Base HTTP client instance
        """
        self._client = base_client
    
    async def submit(
        self,
        agent_id: str,
        thread_id: str,
        room_id: Optional[str] = None,
        replied_id: Optional[str] = None,
        override_message_id: Optional[str] = None,
    ) -> ActivationResponse:
        """
        Submit a new agent activation.
        
        Args:
            agent_id: ID of the agent to activate
            thread_id: ID of the conversation thread
            room_id: Optional room ID
            replied_id: Optional ID of message being replied to
            override_message_id: Optional message ID to override from
            
        Returns:
            ActivationResponse with response_id and status
            
        Raises:
            ValidationError: Invalid request parameters
            ServiceUnavailableError: Service is draining
            AgentError: Other API errors
            
        Example:
            ```python
            response = await client.activations.submit(
                agent_id="agent_123",
                thread_id="thread_456",
            )
            print(f"Response ID: {response.response_id}")
            ```
        """
        request_data = {
            "agent_id": agent_id,
            "thread_id": thread_id,
        }
        
        if room_id is not None:
            request_data["room_id"] = room_id
        if replied_id is not None:
            request_data["replied_id"] = replied_id
        if override_message_id is not None:
            request_data["override_message_id"] = override_message_id
        
        response_data = await self._client._request(
            method="POST",
            path="/api/v1/activations",
            json_data=request_data,
        )
        
        # TypedDict: return the dict directly, type checker will validate it
        return response_data  # type: ignore[return-value]
    
    async def retry(
        self,
        agent_id: str,
        thread_id: str,
        override_message_id: str,
        room_id: Optional[str] = None,
        replied_id: Optional[str] = None,
    ) -> ActivationResponse:
        """
        Retry/resume an agent activation from a specific message.
        
        Args:
            agent_id: ID of the agent to activate
            thread_id: ID of the conversation thread
            override_message_id: Message ID to retry/resume from (required)
            room_id: Optional room ID
            replied_id: Optional ID of message being replied to
            
        Returns:
            ActivationResponse with response_id and status
            
        Raises:
            ValidationError: Invalid request or missing override_message_id
            ServiceUnavailableError: Service is draining
            AgentError: Other API errors
        """
        request_data = {
            "agent_id": agent_id,
            "thread_id": thread_id,
            "override_message_id": override_message_id,
        }
        
        if room_id is not None:
            request_data["room_id"] = room_id
        if replied_id is not None:
            request_data["replied_id"] = replied_id
        
        response_data = await self._client._request(
            method="POST",
            path="/api/v1/activations/retry",
            json_data=request_data,
        )
        
        # TypedDict: return the dict directly, type checker will validate it
        return response_data  # type: ignore[return-value]
    
    async def submit_stream(
        self,
        agent_id: str,
        thread_id: str,
        room_id: Optional[str] = None,
        replied_id: Optional[str] = None,
        override_message_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> AsyncGenerator[SSEEvent, None]:
        """
        Submit an activation and stream progress via SSE.
        
        Args:
            agent_id: ID of the agent to activate
            thread_id: ID of the conversation thread
            room_id: Optional room ID
            replied_id: Optional ID of message being replied to
            override_message_id: Optional message ID to override from
            session_id: Optional session ID for tracking
            
        Yields:
            SSEEvent objects with activation progress
            
        Example:
            ```python
            async for event in client.activations.submit_stream(
                agent_id="agent_123",
                thread_id="thread_456",
            ):
                if event.data:
                    print(f"Event: {event.data.get('type')}")
            ```
        """
        request_data = {
            "agent_id": agent_id,
            "thread_id": thread_id,
        }
        
        if room_id is not None:
            request_data["room_id"] = room_id
        if replied_id is not None:
            request_data["replied_id"] = replied_id
        if override_message_id is not None:
            request_data["override_message_id"] = override_message_id
        
        params = {}
        if session_id is not None:
            params["session_id"] = session_id
        
        async for event in self._client._stream(
            method="POST",
            path="/api/v1/activations/stream",
            json_data=request_data,
            params=params,
        ):
            yield event
    
    async def retry_stream(
        self,
        agent_id: str,
        thread_id: str,
        override_message_id: str,
        room_id: Optional[str] = None,
        replied_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> AsyncGenerator[SSEEvent, None]:
        """
        Retry an activation with SSE streaming.
        
        Args:
            agent_id: ID of the agent to activate
            thread_id: ID of the conversation thread
            override_message_id: Message ID to retry from (required)
            room_id: Optional room ID
            replied_id: Optional ID of message being replied to
            session_id: Optional session ID for tracking
            
        Yields:
            SSEEvent objects with activation progress
        """
        request_data = {
            "agent_id": agent_id,
            "thread_id": thread_id,
            "override_message_id": override_message_id,
        }
        
        if room_id is not None:
            request_data["room_id"] = room_id
        if replied_id is not None:
            request_data["replied_id"] = replied_id
        
        params = {}
        if session_id is not None:
            params["session_id"] = session_id
        
        async for event in self._client._stream(
            method="POST",
            path="/api/v1/activations/retry/stream",
            json_data=request_data,
            params=params,
        ):
            yield event
    
    async def create_event_stream(
        self,
        session_id: Optional[str] = None,
        event_types: Optional[List[str]] = None,
        agent_ids: Optional[List[str]] = None,
        thread_ids: Optional[List[str]] = None,
        channels: Optional[List[str]] = None,
    ) -> AsyncGenerator[SSEEvent, None]:
        """
        Create a generic event stream with optional filtering.
        
        Args:
            session_id: Optional session ID for tracking
            event_types: Filter by event types
            agent_ids: Filter by agent IDs
            thread_ids: Filter by thread IDs
            channels: Filter by channels
            
        Yields:
            SSEEvent objects from the filtered stream
        """
        params = {}
        if session_id is not None:
            params["session_id"] = session_id
        if event_types is not None:
            params["event_types"] = ",".join(event_types)
        if agent_ids is not None:
            params["agent_ids"] = ",".join(agent_ids)
        if thread_ids is not None:
            params["thread_ids"] = ",".join(thread_ids)
        if channels is not None:
            params["channels"] = ",".join(channels)
        
        async for event in self._client._stream(
            method="GET",
            path="/api/v1/activations/events/stream",
            params=params,
        ):
            yield event
    
    async def cancel_response(
        self,
        response_id: str,
        force: bool = False,
        reason: Optional[str] = None,
        timeout: float = 5.0,
    ) -> CancellationResponse:
        """
        Cancel an active agent response.
        
        Args:
            response_id: ID of the response to cancel
            force: Force immediate cancellation
            reason: Optional cancellation reason
            timeout: Timeout for acknowledgment (1.0-30.0 seconds)
            
        Returns:
            CancellationResponse with success status
            
        Raises:
            ValidationError: Invalid parameters
            NotFoundError: Response not found
            TimeoutError: Cancellation timeout
            AgentError: Other errors
            
        Example:
            ```python
            result = await client.activations.cancel_response(
                response_id="resp_123",
                reason="User cancelled",
            )
            if result.success:
                print("Response cancelled successfully")
            ```
        """
        params = {
            "force": force,
            "timeout": timeout,
        }
        if reason is not None:
            params["reason"] = reason
        
        response_data = await self._client._request(
            method="DELETE",
            path=f"/api/v1/activations/{response_id}",
            params=params,
        )
        
        # TypedDict: return the dict directly, type checker will validate it
        return response_data  # type: ignore[return-value]
    
    async def cancel_thread_responses(
        self,
        thread_id: str,
        force: bool = False,
        reason: Optional[str] = None,
        timeout: float = 5.0,
    ) -> BulkCancellationResponse:
        """
        Cancel all active responses in a thread.
        
        Args:
            thread_id: ID of the thread
            force: Force immediate cancellation
            reason: Optional cancellation reason
            timeout: Timeout for acknowledgment (1.0-30.0 seconds)
            
        Returns:
            BulkCancellationResponse with detailed results
            
        Example:
            ```python
            result = await client.activations.cancel_thread_responses(
                thread_id="thread_456",
            )
            print(f"Cancelled {len(result.cancelled_responses)} responses")
            ```
        """
        params = {
            "force": force,
            "timeout": timeout,
        }
        if reason is not None:
            params["reason"] = reason
        
        response_data = await self._client._request(
            method="DELETE",
            path=f"/api/v1/activations/threads/{thread_id}/responses",
            params=params,
        )
        
        # TypedDict: return the dict directly, type checker will validate it
        return response_data  # type: ignore[return-value]
    
    async def get_stats(self) -> ActivationStatsResponse:
        """
        Get system-wide activation statistics.
        
        Returns:
            ActivationStatsResponse with current statistics
            
        Example:
            ```python
            stats = await client.activations.get_stats()
            print(f"Active: {stats.active_count}, Queued: {stats.queue_count}")
            ```
        """
        response_data = await self._client._request(
            method="GET",
            path="/api/v1/activations/stats",
        )
        
        # TypedDict: return the dict directly, type checker will validate it
        return response_data  # type: ignore[return-value]
    
    async def get_thread_activations(
        self,
        thread_id: str,
        include_queued: bool = True,
    ) -> ThreadActivationsResponse:
        """
        Get all activations for a specific thread.
        
        Args:
            thread_id: ID of the thread
            include_queued: Include queued activations
            
        Returns:
            ThreadActivationsResponse with activation details
            
        Example:
            ```python
            activations = await client.activations.get_thread_activations(
                thread_id="thread_456",
            )
            print(f"Active: {activations.active_response_id}")
            print(f"Queue length: {activations.queue_length}")
            ```
        """
        params = {"include_queued": include_queued}
        
        response_data = await self._client._request(
            method="GET",
            path=f"/api/v1/activations/threads/{thread_id}/activations",
            params=params,
        )
        
        # TypedDict: return the dict directly, type checker will validate it
        return response_data  # type: ignore[return-value]
    
    async def get_thread_status(self, thread_id: str) -> ThreadStatusResponse:
        """
        Get the status of a thread.
        
        Args:
            thread_id: ID of the thread
            
        Returns:
            ThreadStatusResponse with status and queue length
        """
        response_data = await self._client._request(
            method="GET",
            path=f"/api/v1/activations/threads/{thread_id}/status",
        )
        
        # TypedDict: return the dict directly, type checker will validate it
        return response_data  # type: ignore[return-value]
    
    async def set_thread_status(
        self,
        thread_id: str,
        status: str,
    ) -> ThreadStatusResponse:
        """
        Set the status of a thread.
        
        Args:
            thread_id: ID of the thread
            status: New status for the thread
            
        Returns:
            ThreadStatusResponse with updated status
        """
        params = {"status": status}
        
        response_data = await self._client._request(
            method="POST",
            path=f"/api/v1/activations/threads/{thread_id}/status",
            params=params,
        )
        
        # TypedDict: return the dict directly, type checker will validate it
        return response_data  # type: ignore[return-value]
    
    async def clear_thread_queue(self, thread_id: str) -> Dict:
        """
        Clear the queue of pending activations for a thread.
        
        Args:
            thread_id: ID of the thread
            
        Returns:
            Dict with operation result
        """
        return await self._client._request(
            method="POST",
            path=f"/api/v1/activations/threads/{thread_id}/clear-queue",
        )
    
    async def listen_response_events(
        self,
        response_id: str,
        channels: Optional[List[str]] = None,
    ) -> AsyncGenerator[SSEEvent, None]:
        """
        Listen to events for a specific response.
        
        Args:
            response_id: ID of the response
            channels: Optional list of channels to filter
            
        Yields:
            SSEEvent objects for the response
        """
        params = {}
        if channels is not None:
            params["channels"] = ",".join(channels)
        
        async for event in self._client._stream(
            method="GET",
            path=f"/api/v1/activations/responses/{response_id}/stream",
            params=params,
        ):
            yield event

