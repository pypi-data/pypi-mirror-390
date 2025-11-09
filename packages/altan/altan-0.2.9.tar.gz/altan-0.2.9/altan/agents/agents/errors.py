"""
Exception classes for Agent Evolution SDK
"""

from typing import Optional, Dict, Any


class AgentError(Exception):
    """Base exception for all Agent Evolution SDK errors."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response


class ValidationError(AgentError):
    """Raised when request validation fails (HTTP 400)."""
    pass


class NotFoundError(AgentError):
    """Raised when a resource is not found (HTTP 404)."""
    pass


class ServiceUnavailableError(AgentError):
    """Raised when service is unavailable (HTTP 503)."""
    pass


class TimeoutError(AgentError):
    """Raised when a request times out (HTTP 504)."""
    pass


class RateLimitError(AgentError):
    """Raised when rate limit is exceeded (HTTP 429)."""
    pass


class InternalServerError(AgentError):
    """Raised when server encounters an error (HTTP 500)."""
    pass


def handle_error_response(status_code: int, response_data: Dict[str, Any]) -> AgentError:
    """
    Convert HTTP error response to appropriate exception.
    
    Args:
        status_code: HTTP status code
        response_data: Response body as dict
        
    Returns:
        Appropriate AgentError subclass
    """
    detail = response_data.get("detail", "Unknown error")
    
    if isinstance(detail, dict):
        message = detail.get("message", str(detail))
    else:
        message = str(detail)
    
    error_map = {
        400: ValidationError,
        404: NotFoundError,
        429: RateLimitError,
        500: InternalServerError,
        503: ServiceUnavailableError,
        504: TimeoutError,
    }
    
    error_class = error_map.get(status_code, AgentError)
    return error_class(message, status_code=status_code, response=response_data)

