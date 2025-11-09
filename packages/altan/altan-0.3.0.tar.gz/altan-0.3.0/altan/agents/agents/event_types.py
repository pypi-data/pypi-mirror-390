"""
Event type definitions for SSE streaming events.

These TypedDicts provide proper typing for events emitted during response streaming,
matching the domain events from responses/domain/events/.
"""

from typing import Any, Dict, List, Union
from typing_extensions import TypedDict


# ============================================================================
# Streaming Event Data Payloads (message parts)
# ============================================================================

class MessagePartAddedData(TypedDict, total=False):
    """Data payload for message_part.added event."""
    name: str
    event_name: str
    response_id: str
    agent_id: str
    thread_id: str
    room_id: str
    message_id: str
    # Part payload fields (spread from part_payload)
    id: str
    type: str
    text: str
    order: int
    block_order: int
    provider: str
    provider_id: str
    provider_item_type: str
    created_at: str
    finished_at: str
    # Tool/thinking specific fields that may be present
    tool_call_id: str
    tool_id: str
    name: str
    input: Dict[str, Any]
    arguments: Dict[str, Any]
    result: Union[Dict[str, Any], str]
    error: Union[Dict[str, Any], str]
    status: str
    summary: List[str]


class MessagePartUpdatedData(TypedDict, total=False):
    """Data payload for message_part.updated event."""
    name: str
    event_name: str
    id: str
    delta: Any
    index: int
    type: str
    response_id: str
    agent_id: str
    thread_id: str
    room_id: str
    message_id: str


class MessagePartDoneData(TypedDict, total=False):
    """Data payload for message_part.completed event."""
    name: str
    event_name: str
    response_id: str
    agent_id: str
    thread_id: str
    room_id: str
    message_id: str
    # Part payload fields (spread from part_payload)
    id: str
    type: str
    text: str
    order: int
    block_order: int
    provider: str
    provider_id: str
    provider_item_type: str
    created_at: str
    finished_at: str
    # Tool/thinking specific fields that may be present
    tool_call_id: str
    tool_id: str
    name: str
    input: Dict[str, Any]
    arguments: Dict[str, Any]
    result: Union[Dict[str, Any], str]
    error: Union[Dict[str, Any], str]
    status: str
    summary: List[str]


# ============================================================================
# Response Lifecycle Event Data Payloads
# ============================================================================

class ResponseScheduledData(TypedDict, total=False):
    """Data payload for response.scheduled event."""
    name: str
    event_name: str
    response_id: str
    agent_id: str
    thread_id: str
    room_id: str


class ResponseRescheduledData(TypedDict, total=False):
    """Data payload for response.rescheduled event."""
    name: str
    event_name: str
    response_id: str
    agent_id: str
    override_message_id: str
    thread_id: str
    room_id: str


class ResponseStartedData(TypedDict, total=False):
    """Data payload for response.started event."""
    name: str
    event_name: str
    response_id: str
    agent_id: str
    thread_id: str
    room_id: str


class ResponseResumedData(TypedDict, total=False):
    """Data payload for response.resumed event."""
    name: str
    event_name: str
    response_id: str
    agent_id: str
    resume_from: str
    thread_id: str
    room_id: str


class ResponseSuspendedData(TypedDict, total=False):
    """Data payload for response.suspended event."""
    name: str
    event_name: str
    response_id: str
    agent_id: str
    reason: str
    thread_id: str
    room_id: str


class ResponseStoppedData(TypedDict, total=False):
    """Data payload for response.stopped event."""
    name: str
    event_name: str
    response_id: str
    agent_id: str
    by: str
    thread_id: str
    room_id: str


class ResponseInterruptedData(TypedDict, total=False):
    """Data payload for response.interrupted event."""
    name: str
    event_name: str
    response_id: str
    agent_id: str
    reason: str
    thread_id: str
    room_id: str


class ResponseRequeuedData(TypedDict, total=False):
    """Data payload for response.requeued event."""
    name: str
    event_name: str
    response_id: str
    agent_id: str
    next_run_at: str
    thread_id: str
    room_id: str


class ResponseCompletedData(TypedDict, total=False):
    """Data payload for response.completed event."""
    name: str
    event_name: str
    response_id: str
    agent_id: str
    models_used: List[str]
    usage: List[Dict[str, Any]]
    thread_id: str
    room_id: str


class ResponseEmptyData(TypedDict, total=False):
    """Data payload for response.empty event."""
    name: str
    event_name: str
    response_id: str
    agent_id: str
    models_used: List[str]
    usage: List[Dict[str, Any]]
    thread_id: str
    room_id: str


class ResponseFailedData(TypedDict, total=False):
    """Data payload for response.failed event."""
    name: str
    event_name: str
    response_id: str
    agent_id: str
    error_code: str
    error_message: str
    retryable: bool
    thread_id: str
    room_id: str
    timestamp: str


class ResponseFallbackData(TypedDict, total=False):
    """Data payload for response.fallback event."""
    name: str
    event_name: str
    response_id: str
    agent_id: str
    error_code: str
    error_message: str
    error_type: str
    status_code: int
    from_provider: str
    from_model: str
    to_provider: str
    to_model: str
    thread_id: str
    room_id: str
    timestamp: str


class ResponseRetryData(TypedDict, total=False):
    """Data payload for response.retry event."""
    name: str
    event_name: str
    response_id: str
    agent_id: str
    error_code: str
    error_message: str
    error_type: str
    status_code: int
    provider: str
    model: str
    retry_count: int
    thread_id: str
    room_id: str
    timestamp: str


# ============================================================================
# Union of all event data payloads
# ============================================================================

StreamEventData = Union[
    MessagePartAddedData,
    MessagePartUpdatedData,
    MessagePartDoneData,
    ResponseScheduledData,
    ResponseRescheduledData,
    ResponseStartedData,
    ResponseResumedData,
    ResponseSuspendedData,
    ResponseStoppedData,
    ResponseInterruptedData,
    ResponseRequeuedData,
    ResponseCompletedData,
    ResponseEmptyData,
    ResponseFailedData,
    ResponseFallbackData,
    ResponseRetryData,
]


# ============================================================================
# Full Event Types (matching Event.to_dict() structure)
# ============================================================================

class MessagePartAddedEvent(TypedDict, total=False):
    """Full event for message_part.added."""
    event_id: str
    event_type: str
    occurred_on: str
    data: MessagePartAddedData
    extras: Dict[str, Any]


class MessagePartUpdatedEvent(TypedDict, total=False):
    """Full event for message_part.updated."""
    event_id: str
    event_type: str
    occurred_on: str
    data: MessagePartUpdatedData
    extras: Dict[str, Any]


class MessagePartDoneEvent(TypedDict, total=False):
    """Full event for message_part.completed."""
    event_id: str
    event_type: str
    occurred_on: str
    data: MessagePartDoneData
    extras: Dict[str, Any]


class ResponseScheduledEvent(TypedDict, total=False):
    """Full event for response.scheduled."""
    event_id: str
    event_type: str
    occurred_on: str
    data: ResponseScheduledData
    extras: Dict[str, Any]


class ResponseRescheduledEvent(TypedDict, total=False):
    """Full event for response.rescheduled."""
    event_id: str
    event_type: str
    occurred_on: str
    data: ResponseRescheduledData
    extras: Dict[str, Any]


class ResponseStartedEvent(TypedDict, total=False):
    """Full event for response.started."""
    event_id: str
    event_type: str
    occurred_on: str
    data: ResponseStartedData
    extras: Dict[str, Any]


class ResponseResumedEvent(TypedDict, total=False):
    """Full event for response.resumed."""
    event_id: str
    event_type: str
    occurred_on: str
    data: ResponseResumedData
    extras: Dict[str, Any]


class ResponseSuspendedEvent(TypedDict, total=False):
    """Full event for response.suspended."""
    event_id: str
    event_type: str
    occurred_on: str
    data: ResponseSuspendedData
    extras: Dict[str, Any]


class ResponseStoppedEvent(TypedDict, total=False):
    """Full event for response.stopped."""
    event_id: str
    event_type: str
    occurred_on: str
    data: ResponseStoppedData
    extras: Dict[str, Any]


class ResponseInterruptedEvent(TypedDict, total=False):
    """Full event for response.interrupted."""
    event_id: str
    event_type: str
    occurred_on: str
    data: ResponseInterruptedData
    extras: Dict[str, Any]


class ResponseRequeuedEvent(TypedDict, total=False):
    """Full event for response.requeued."""
    event_id: str
    event_type: str
    occurred_on: str
    data: ResponseRequeuedData
    extras: Dict[str, Any]


class ResponseCompletedEvent(TypedDict, total=False):
    """Full event for response.completed."""
    event_id: str
    event_type: str
    occurred_on: str
    data: ResponseCompletedData
    extras: Dict[str, Any]


class ResponseEmptyEvent(TypedDict, total=False):
    """Full event for response.empty."""
    event_id: str
    event_type: str
    occurred_on: str
    data: ResponseEmptyData
    extras: Dict[str, Any]


class ResponseFailedEvent(TypedDict, total=False):
    """Full event for response.failed."""
    event_id: str
    event_type: str
    occurred_on: str
    data: ResponseFailedData
    extras: Dict[str, Any]


class ResponseFallbackEvent(TypedDict, total=False):
    """Full event for response.fallback."""
    event_id: str
    event_type: str
    occurred_on: str
    data: ResponseFallbackData
    extras: Dict[str, Any]


class ResponseRetryEvent(TypedDict, total=False):
    """Full event for response.retry."""
    event_id: str
    event_type: str
    occurred_on: str
    data: ResponseRetryData
    extras: Dict[str, Any]


# ============================================================================
# Union of all full event types
# ============================================================================

StreamEvent = Union[
    MessagePartAddedEvent,
    MessagePartUpdatedEvent,
    MessagePartDoneEvent,
    ResponseScheduledEvent,
    ResponseRescheduledEvent,
    ResponseStartedEvent,
    ResponseResumedEvent,
    ResponseSuspendedEvent,
    ResponseStoppedEvent,
    ResponseInterruptedEvent,
    ResponseRequeuedEvent,
    ResponseCompletedEvent,
    ResponseEmptyEvent,
    ResponseFailedEvent,
    ResponseFallbackEvent,
    ResponseRetryEvent,
]

