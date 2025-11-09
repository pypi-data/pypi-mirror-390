"""
Request/Response Hook System

Provides interceptors for customizing request/response behavior, similar to
middleware in web frameworks. Useful for logging, metrics, custom auth, etc.
"""

import logging
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RequestContext:
    """Context information for a request hook."""
    method: str
    url: str
    headers: Dict[str, str]
    json_data: Optional[Dict[str, Any]]
    params: Optional[Dict[str, Any]]
    request_id: Optional[str] = None
    attempt: int = 0
    
    def set_header(self, key: str, value: str):
        """Add or update a header."""
        self.headers[key] = value
    
    def set_param(self, key: str, value: Any):
        """Add or update a query parameter."""
        if self.params is None:
            self.params = {}
        self.params[key] = value


@dataclass
class ResponseContext:
    """Context information for a response hook."""
    method: str
    url: str
    status_code: int
    headers: Dict[str, str]
    data: Any
    request_id: Optional[str] = None
    attempt: int = 0
    elapsed_ms: float = 0.0


# Type aliases for hooks
RequestHook = Callable[[RequestContext], None]
ResponseHook = Callable[[ResponseContext], None]
ErrorHook = Callable[[Exception, RequestContext], None]


class HookManager:
    """
    Manages request/response hooks for HTTP client.
    
    Hooks are called in registration order. They can modify request/response
    context or perform side effects (logging, metrics, etc.).
    
    Example:
        ```python
        def log_request(ctx: RequestContext):
            print(f"{ctx.method} {ctx.url}")
        
        def add_custom_auth(ctx: RequestContext):
            ctx.set_header("X-Custom-Auth", "token")
        
        manager = HookManager()
        manager.add_request_hook(log_request)
        manager.add_request_hook(add_custom_auth)
        ```
    """
    
    def __init__(self):
        """Initialize empty hook lists."""
        self._request_hooks: List[RequestHook] = []
        self._response_hooks: List[ResponseHook] = []
        self._error_hooks: List[ErrorHook] = []
    
    def add_request_hook(self, hook: RequestHook) -> None:
        """
        Add a request hook.
        
        The hook will be called before each request is sent.
        It can modify the request context (headers, params, etc.).
        
        Args:
            hook: Function that accepts RequestContext
        """
        self._request_hooks.append(hook)
        logger.debug(f"Added request hook: {hook.__name__}")
    
    def add_response_hook(self, hook: ResponseHook) -> None:
        """
        Add a response hook.
        
        The hook will be called after each successful response.
        It can inspect response data and perform side effects.
        
        Args:
            hook: Function that accepts ResponseContext
        """
        self._response_hooks.append(hook)
        logger.debug(f"Added response hook: {hook.__name__}")
    
    def add_error_hook(self, hook: ErrorHook) -> None:
        """
        Add an error hook.
        
        The hook will be called when a request fails.
        It can inspect the error and request context.
        
        Args:
            hook: Function that accepts (Exception, RequestContext)
        """
        self._error_hooks.append(hook)
        logger.debug(f"Added error hook: {hook.__name__}")
    
    def remove_request_hook(self, hook: RequestHook) -> bool:
        """Remove a request hook. Returns True if found and removed."""
        try:
            self._request_hooks.remove(hook)
            logger.debug(f"Removed request hook: {hook.__name__}")
            return True
        except ValueError:
            return False
    
    def remove_response_hook(self, hook: ResponseHook) -> bool:
        """Remove a response hook. Returns True if found and removed."""
        try:
            self._response_hooks.remove(hook)
            logger.debug(f"Removed response hook: {hook.__name__}")
            return True
        except ValueError:
            return False
    
    def remove_error_hook(self, hook: ErrorHook) -> bool:
        """Remove an error hook. Returns True if found and removed."""
        try:
            self._error_hooks.remove(hook)
            logger.debug(f"Removed error hook: {hook.__name__}")
            return True
        except ValueError:
            return False
    
    def clear_hooks(self) -> None:
        """Remove all hooks."""
        self._request_hooks.clear()
        self._response_hooks.clear()
        self._error_hooks.clear()
        logger.debug("Cleared all hooks")
    
    def run_request_hooks(self, context: RequestContext) -> None:
        """
        Execute all request hooks.
        
        Hooks are called in registration order. If a hook raises an exception,
        it's logged but doesn't prevent other hooks from running.
        
        Args:
            context: Request context to pass to hooks
        """
        for hook in self._request_hooks:
            try:
                hook(context)
            except Exception as e:
                logger.error(
                    f"Request hook {hook.__name__} failed: {e}",
                    exc_info=True
                )
    
    def run_response_hooks(self, context: ResponseContext) -> None:
        """
        Execute all response hooks.
        
        Hooks are called in registration order. If a hook raises an exception,
        it's logged but doesn't prevent other hooks from running.
        
        Args:
            context: Response context to pass to hooks
        """
        for hook in self._response_hooks:
            try:
                hook(context)
            except Exception as e:
                logger.error(
                    f"Response hook {hook.__name__} failed: {e}",
                    exc_info=True
                )
    
    def run_error_hooks(self, error: Exception, context: RequestContext) -> None:
        """
        Execute all error hooks.
        
        Hooks are called in registration order. If a hook raises an exception,
        it's logged but doesn't prevent other hooks from running.
        
        Args:
            error: The exception that occurred
            context: Request context when error occurred
        """
        for hook in self._error_hooks:
            try:
                hook(error, context)
            except Exception as e:
                logger.error(
                    f"Error hook {hook.__name__} failed: {e}",
                    exc_info=True
                )
    
    def has_hooks(self) -> bool:
        """Check if any hooks are registered."""
        return bool(
            self._request_hooks or 
            self._response_hooks or 
            self._error_hooks
        )
    
    @property
    def request_hook_count(self) -> int:
        """Get number of registered request hooks."""
        return len(self._request_hooks)
    
    @property
    def response_hook_count(self) -> int:
        """Get number of registered response hooks."""
        return len(self._response_hooks)
    
    @property
    def error_hook_count(self) -> int:
        """Get number of registered error hooks."""
        return len(self._error_hooks)


# Pre-built common hooks

def logging_request_hook(context: RequestContext) -> None:
    """
    Built-in hook for logging requests.
    
    Example:
        ```python
        client._base_client._hook_manager.add_request_hook(logging_request_hook)
        ```
    """
    logger.info(
        f"Request: {context.method} {context.url}",
        extra={
            "request_id": context.request_id,
            "method": context.method,
            "url": context.url,
            "attempt": context.attempt,
        }
    )


def logging_response_hook(context: ResponseContext) -> None:
    """
    Built-in hook for logging responses.
    
    Example:
        ```python
        client._base_client._hook_manager.add_response_hook(logging_response_hook)
        ```
    """
    logger.info(
        f"Response: {context.status_code} ({context.elapsed_ms:.2f}ms)",
        extra={
            "request_id": context.request_id,
            "status_code": context.status_code,
            "elapsed_ms": context.elapsed_ms,
            "attempt": context.attempt,
        }
    )


def metrics_hook_factory(metrics_client: Any) -> RequestHook:
    """
    Factory for creating metrics collection hooks.
    
    Args:
        metrics_client: Client for reporting metrics (e.g., Prometheus, StatsD)
    
    Returns:
        Request hook that reports metrics
    
    Example:
        ```python
        import prometheus_client
        
        counter = prometheus_client.Counter('api_requests_total', 'Total API requests')
        
        def metrics_hook(ctx):
            counter.labels(method=ctx.method).inc()
        
        client._base_client._hook_manager.add_request_hook(metrics_hook)
        ```
    """
    def metrics_hook(context: RequestContext) -> None:
        # This is a template - customize for your metrics backend
        try:
            metrics_client.increment(
                "altan_sdk.requests",
                tags={
                    "method": context.method,
                    "endpoint": context.url,
                }
            )
        except Exception as e:
            logger.debug(f"Metrics hook failed: {e}")
    
    return metrics_hook


def custom_header_hook(headers: Dict[str, str]) -> RequestHook:
    """
    Factory for creating hooks that add custom headers.
    
    Args:
        headers: Dictionary of headers to add to every request
    
    Returns:
        Request hook that adds the headers
    
    Example:
        ```python
        hook = custom_header_hook({
            "X-Custom-Header": "value",
            "X-Request-Source": "production",
        })
        client._base_client._hook_manager.add_request_hook(hook)
        ```
    """
    def header_hook(context: RequestContext) -> None:
        for key, value in headers.items():
            context.set_header(key, value)
    
    return header_hook

