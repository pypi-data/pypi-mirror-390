"""
Base HTTP client for Altan AI SDK
"""

import asyncio
import json
import logging
import random
import time
import uuid
from typing import Any, AsyncGenerator, Dict, Optional
from urllib.parse import urljoin

import httpx

from .errors import handle_error_response, AgentError
from .types import SSEEvent
from .hooks import HookManager, RequestContext, ResponseContext

logger = logging.getLogger(__name__)


class BaseClient:
    """
    Enterprise-grade HTTP client with:
    - HTTP/2 connection pooling with proper limits
    - Exponential backoff with jitter
    - Graceful connection lifecycle management
    - Proper resource cleanup
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
        proxy: Optional[str] = None,
        trust_env: bool = True,
        default_headers: Optional[Dict[str, str]] = None,
        user_agent: Optional[str] = None,
    ):
        """
        Initialize base client with enterprise-grade settings.
        
        Args:
            base_url: Base URL of the API (e.g., "http://localhost:8000")
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds (applies to read operations)
            max_retries: Maximum number of retry attempts (default: 3)
            max_connections: Maximum concurrent connections (default: 100)
            max_keepalive_connections: Maximum idle connections to keep alive (default: 20)
            keepalive_expiry: Time to keep idle connections alive in seconds (default: 30.0)
            proxy: Proxy URL (e.g., "http://proxy.example.com:8080", "socks5://localhost:1080")
            trust_env: Whether to trust environment variables for proxy config (default: True)
            default_headers: Default headers to include in all requests
            user_agent: Custom user agent string
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.max_retries = max_retries
        self.default_timeout = timeout
        self.default_headers = default_headers or {}
        self.user_agent = user_agent or "agents-sdk/0.1.0"
        
        # Configure granular timeouts for different operations
        timeout_config = httpx.Timeout(
            connect=10.0,      # Connection establishment
            read=timeout,      # Reading response data
            write=10.0,        # Sending request data
            pool=5.0,          # Acquiring connection from pool
        )
        
        # Configure connection limits for HTTP/2 multiplexing
        # This prevents "stream not closed cleanly" errors
        limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=keepalive_expiry,
        )
        
        # HTTP/2 configuration to prevent stream errors
        # - Disable HTTP/2 by default for stability (enable if server supports it well)
        # - If HTTP/2 is needed, these limits prevent multiplexing issues
        http2_enabled = False  # Set to True if server fully supports HTTP/2
        
        # Configure transport with proxy support
        transport = httpx.AsyncHTTPTransport(
            retries=0,  # We handle retries at application level
            http2=http2_enabled,
            proxy=httpx.Proxy(proxy) if proxy else None,
        )
        
        # Create async client with enterprise settings
        self._client = httpx.AsyncClient(
            timeout=timeout_config,
            limits=limits,
            follow_redirects=True,
            http2=http2_enabled,
            transport=transport,
            trust_env=trust_env,  # Auto-detect proxy from env vars
        )
        
        # Hook system for request/response interceptors
        self._hook_manager = HookManager()
        
        # Track if client is closed
        self._closed = False
    
    def _build_url(self, path: str) -> str:
        """Build full URL from path."""
        return urljoin(self.base_url + "/", path.lstrip("/"))
    
    def _build_headers(self, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Build request headers with defaults, auth, and extras."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": self.user_agent,
            "Connection": "keep-alive",  # Explicit keepalive for HTTP/1.1
        }
        
        # Add default headers
        headers.update(self.default_headers)
        
        # Add API key if provided
        if self.api_key:
            headers["X-Altan-Key"] = self.api_key
        
        # Extra headers override defaults
        if extra_headers:
            headers.update(extra_headers)
        
        return headers
    
    def _calculate_backoff(self, attempt: int, base_delay: float = 1.0) -> float:
        """
        Calculate exponential backoff with jitter.
        
        Formula: min(base_delay * 2^attempt + random_jitter, max_delay)
        Jitter prevents thundering herd problem.
        
        Args:
            attempt: Current retry attempt (0-indexed)
            base_delay: Base delay in seconds (default: 1.0)
            
        Returns:
            Delay in seconds
        """
        max_delay = 60.0  # Cap at 60 seconds
        
        # Exponential backoff: 1s, 2s, 4s, 8s, 16s, 32s, 60s
        delay = min(base_delay * (2 ** attempt), max_delay)
        
        # Add jitter: +/- 25% randomization
        jitter = delay * 0.25 * random.uniform(-1, 1)
        
        return max(0.1, delay + jitter)  # Minimum 100ms
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """
        Determine if an error is retryable.
        
        Retryable errors:
        - Network errors (connection, timeout)
        - 5xx server errors
        - 429 rate limit (with backoff)
        - Specific HTTP/2 errors
        
        Non-retryable errors:
        - 4xx client errors (except 429)
        - Authentication errors
        """
        # Network-level errors are always retryable
        if isinstance(error, (httpx.NetworkError, httpx.TimeoutException)):
            return True
        
        # Check HTTP status codes
        if isinstance(error, AgentError):
            status = error.status_code
            if status is None:
                return True  # Network error wrapped in AgentError
            
            # Retryable status codes
            if status >= 500:  # 5xx server errors
                return True
            if status == 429:  # Rate limit
                return True
            if status == 503:  # Service unavailable
                return True
            if status == 504:  # Gateway timeout
                return True
        
        return False
    
    async def _request(
        self,
        method: str,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request with exponential backoff retry logic.
        
        Implements:
        - Automatic retry on transient failures
        - Exponential backoff with jitter
        - Graceful error handling
        - Resource cleanup
        
        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            path: API path
            json_data: JSON request body
            params: Query parameters
            headers: Additional headers
            timeout: Override default timeout for this request (in seconds)
            
        Returns:
            Response data as dict
            
        Raises:
            AgentError: On request failure after all retries
        """
        if self._closed:
            raise AgentError("Client has been closed")
        
        # Use custom timeout if provided, otherwise use default
        request_timeout = timeout if timeout is not None else self.default_timeout
        
        url = self._build_url(path)
        request_headers = self._build_headers(headers)
        request_id = str(uuid.uuid4())
        
        # Create request context for hooks
        request_context = RequestContext(
            method=method,
            url=url,
            headers=request_headers,
            json_data=json_data,
            params=params,
            request_id=request_id,
            attempt=0,
        )
        
        last_error: Optional[Exception] = None
        
        # Retry loop with exponential backoff
        for attempt in range(self.max_retries + 1):
            # Update attempt in context
            request_context.attempt = attempt
            
            # Run request hooks
            self._hook_manager.run_request_hooks(request_context)
            
            # Use potentially modified headers/params from hooks
            request_headers = request_context.headers
            params = request_context.params
            
            start_time = time.time()
            try:
                response = await self._client.request(
                    method=method,
                    url=url,
                    json=json_data,
                    params=params,
                    headers=request_headers,
                    timeout=request_timeout,
                )
                
                # Handle error responses
                if response.status_code >= 400:
                    try:
                        error_data = response.json()
                    except Exception:
                        error_data = {"detail": response.text}
                    
                    error = handle_error_response(response.status_code, error_data)
                    
                    # Check if error is retryable
                    if attempt < self.max_retries and self._is_retryable_error(error):
                        last_error = error
                        delay = self._calculate_backoff(attempt)
                        logger.warning(
                            f"Request failed (attempt {attempt + 1}/{self.max_retries + 1}): "
                            f"{error.message}. Retrying in {delay:.2f}s..."
                        )
                        await asyncio.sleep(delay)
                        continue
                    
                    # Non-retryable or max retries reached
                    raise error
                
                # Parse successful response
                response_data = {}
                if response.status_code == 204:  # No content
                    response_data = {}
                else:
                    response_data = response.json()
                
                # Calculate elapsed time
                elapsed_ms = (time.time() - start_time) * 1000
                
                # Run response hooks
                response_context = ResponseContext(
                    method=method,
                    url=url,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    data=response_data,
                    request_id=request_id,
                    attempt=attempt,
                    elapsed_ms=elapsed_ms,
                )
                self._hook_manager.run_response_hooks(response_context)
                
                return response_data
            
            except httpx.TimeoutException as e:
                last_error = e
                self._hook_manager.run_error_hooks(e, request_context)
                
                if attempt < self.max_retries:
                    delay = self._calculate_backoff(attempt)
                    logger.warning(
                        f"Request timeout (attempt {attempt + 1}/{self.max_retries + 1}). "
                        f"Retrying in {delay:.2f}s..."
                    )
                    await asyncio.sleep(delay)
                    continue
                
                raise AgentError(
                    f"Request timed out after {self.max_retries + 1} attempts",
                    status_code=408
                ) from e
            
            except httpx.NetworkError as e:
                last_error = e
                self._hook_manager.run_error_hooks(e, request_context)
                
                if attempt < self.max_retries:
                    delay = self._calculate_backoff(attempt)
                    logger.warning(
                        f"Network error (attempt {attempt + 1}/{self.max_retries + 1}): {str(e)}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    await asyncio.sleep(delay)
                    continue
                
                raise AgentError(
                    f"Network error after {self.max_retries + 1} attempts: {str(e)}"
                ) from e
            
            except httpx.RequestError as e:
                last_error = e
                self._hook_manager.run_error_hooks(e, request_context)
                
                # Check if it's a retryable request error
                if attempt < self.max_retries and (
                    "stream" in str(e).lower() or 
                    "connection" in str(e).lower() or
                    "reset" in str(e).lower()
                ):
                    delay = self._calculate_backoff(attempt)
                    logger.warning(
                        f"Request error (attempt {attempt + 1}/{self.max_retries + 1}): {str(e)}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    await asyncio.sleep(delay)
                    continue
                
                raise AgentError(
                    f"Request failed: {str(e)}"
                ) from e
        
        # Should never reach here, but handle gracefully
        raise AgentError(
            f"Request failed after {self.max_retries + 1} attempts: {str(last_error)}"
        )
    
    async def _stream(
        self,
        method: str,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> AsyncGenerator[SSEEvent, None]:
        """
        Stream SSE events with robust error handling and resource cleanup.
        
        Implements:
        - Graceful connection handling
        - Proper resource cleanup on errors
        - SSE protocol compliance
        - Connection state tracking
        
        Args:
            method: HTTP method
            path: API path
            json_data: JSON request body
            params: Query parameters
            headers: Additional headers
            
        Yields:
            SSEEvent objects
            
        Raises:
            AgentError: On stream failure
        """
        if self._closed:
            raise AgentError("Client has been closed")
        
        url = self._build_url(path)
        request_headers = self._build_headers(headers)
        request_headers["Accept"] = "text/event-stream"
        request_headers["Cache-Control"] = "no-cache"
        
        response = None
        try:
            # Create streaming request
            response = self._client.stream(
                method=method,
                url=url,
                json=json_data,
                params=params,
                headers=request_headers,
            )
            
            async with response as stream:
                # Handle error responses before streaming
                if stream.status_code >= 400:
                    try:
                        error_data = await stream.aread()
                        error_json = json.loads(error_data) if error_data else {}
                    except Exception:
                        error_json = {
                            "detail": error_data.decode() if error_data else "Unknown error"
                        }
                    
                    raise handle_error_response(stream.status_code, error_json)
                
                # Parse SSE stream
                event_data: Dict[str, str] = {}
                
                try:
                    async for line in stream.aiter_lines():
                        line = line.strip()
                        
                        if not line:
                            # Empty line = end of event
                            if event_data:
                                yield self._parse_sse_event(event_data)
                                event_data = {}
                            continue
                        
                        if line.startswith(":"):
                            # Comment line (keepalive), skip
                            continue
                        
                        if ":" in line:
                            field, _, value = line.partition(":")
                            value = value.lstrip()
                            
                            # Accumulate multi-line data
                            if field == "data":
                                if "data" in event_data:
                                    event_data["data"] += "\n" + value
                                else:
                                    event_data["data"] = value
                            else:
                                event_data[field] = value
                    
                    # Yield final event if any (in case stream ends without empty line)
                    if event_data:
                        yield self._parse_sse_event(event_data)
                
                except httpx.RemoteProtocolError as e:
                    # HTTP/2 stream errors - log and raise
                    logger.error(f"HTTP/2 protocol error during streaming: {str(e)}")
                    raise AgentError(
                        f"Stream protocol error: {str(e)}. "
                        "This may indicate HTTP/2 multiplexing issues. "
                        "Consider disabling HTTP/2 or reducing concurrent connections.",
                        status_code=None
                    ) from e
                
                except httpx.ReadError as e:
                    # Connection read errors - connection was closed
                    logger.warning(f"Stream read error (connection closed): {str(e)}")
                    raise AgentError(
                        f"Stream connection closed unexpectedly: {str(e)}",
                        status_code=None
                    ) from e
        
        except httpx.TimeoutException as e:
            logger.error(f"Stream timeout: {str(e)}")
            raise AgentError(
                f"Stream timed out. Consider increasing timeout or checking network stability.",
                status_code=408
            ) from e
        
        except httpx.NetworkError as e:
            logger.error(f"Stream network error: {str(e)}")
            raise AgentError(
                f"Stream network error: {str(e)}",
                status_code=None
            ) from e
        
        except httpx.RequestError as e:
            logger.error(f"Stream request error: {str(e)}")
            raise AgentError(
                f"Stream failed: {str(e)}"
            ) from e
        
        except Exception as e:
            # Catch-all for unexpected errors
            logger.error(f"Unexpected stream error: {str(e)}", exc_info=True)
            raise AgentError(
                f"Unexpected stream error: {str(e)}"
            ) from e
        
        finally:
            # Ensure response is cleaned up
            if response is not None:
                try:
                    await response.aclose()
                except Exception as cleanup_error:
                    logger.debug(f"Error during stream cleanup: {cleanup_error}")
    
    def _parse_sse_event(self, event_data: Dict[str, str]) -> SSEEvent:
        """Parse SSE event data."""
        # Parse data field as JSON if possible
        data_str = event_data.get("data", "")
        try:
            data = json.loads(data_str) if data_str else None
        except json.JSONDecodeError:
            data = {"raw": data_str}
        
        # Build SSEEvent as a dict (TypedDict)
        result: SSEEvent = {}  # type: ignore[typeddict-item]
        if event_data.get("event"):
            result["event"] = event_data["event"]
        if data is not None:
            result["data"] = data
        if event_data.get("id"):
            result["id"] = event_data["id"]
        if "retry" in event_data:
            result["retry"] = int(event_data["retry"])
        
        return result
    
    async def close(self):
        """
        Close the HTTP client and cleanup resources.
        
        This method is idempotent and safe to call multiple times.
        """
        if self._closed:
            return
        
        self._closed = True
        
        try:
            await self._client.aclose()
            logger.debug("HTTP client closed successfully")
        except Exception as e:
            logger.warning(f"Error during client cleanup: {e}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        if self._closed:
            raise AgentError("Cannot reuse closed client")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with proper cleanup."""
        await self.close()
    
    def __del__(self):
        """
        Destructor to ensure cleanup.
        
        Note: This is a safety net. Users should explicitly call close()
        or use the async context manager.
        """
        if not self._closed and hasattr(self, "_client"):
            logger.warning(
                "BaseClient was not properly closed. "
                "Use 'async with' or call close() explicitly."
            )

