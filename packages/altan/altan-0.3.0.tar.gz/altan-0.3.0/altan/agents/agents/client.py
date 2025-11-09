"""
Main Altan Agent Client

Unified client providing access to both Responses and Activations APIs.
"""

import logging
import os
from typing import Dict, Optional

from .base_client import BaseClient
from .responses import ResponsesClient
from .activations import ActivationsClient

logger = logging.getLogger(__name__)


class AgentClient:
    """
    Main client for Altan AI platform.
    
    Provides access to:
    - Responses API: Stateless LLM responses (OpenAI/Anthropic-compatible)
    - Activations API: Event-driven agent activations
    
    Example:
        ```python
        import asyncio
        from agents import AgentClient
        
        async def main():
            async with AgentClient(base_url="http://localhost:8000") as client:
                # Use responses API
                response = await client.responses.create(
                    messages=[{"role": "user", "content": "Hello!"}],
                    model="gpt-4o",
                )
                print(f"Response ID: {response.response_id}")
                
                # Use activations API
                activation = await client.activations.submit(
                    agent_id="agent_123",
                    thread_id="thread_456",
                )
                print(f"Activation submitted: {activation.response_id}")
        
        asyncio.run(main())
        ```
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        keepalive_expiry: float = 30.0,
        proxy: Optional[str] = None,
        trust_env: bool = True,
        default_headers: Optional[Dict[str, str]] = None,
        user_agent: Optional[str] = None,
        debug: bool = False,
    ):
        """
        Initialize Altan Agent client with enterprise-grade settings.
        
        Environment variables (auto-detected if parameters not provided):
            ALTAN_API_KEY: API key for authentication
            ALTAN_BASE_URL: Base URL of the API
            ALTAN_TIMEOUT: Request timeout in seconds
            ALTAN_MAX_RETRIES: Maximum number of retry attempts
            ALTAN_PROXY: Proxy URL (HTTP/HTTPS/SOCKS)
            ALTAN_DEBUG: Enable debug mode (1 or true)
        
        Args:
            base_url: Base URL of the API (default: env ALTAN_BASE_URL or https://ai.altan.ai)
            api_key: API key for authentication (default: env ALTAN_API_KEY)
            timeout: Request timeout in seconds (default: env ALTAN_TIMEOUT or 60.0)
            max_retries: Maximum retry attempts (default: env ALTAN_MAX_RETRIES or 3)
            max_connections: Maximum concurrent connections (default: 100)
            max_keepalive_connections: Maximum idle connections to keep alive (default: 20)
            keepalive_expiry: Time to keep idle connections alive in seconds (default: 30.0)
            proxy: Proxy URL (default: env ALTAN_PROXY or HTTP_PROXY/HTTPS_PROXY if trust_env=True)
            trust_env: Trust environment variables for proxy config (default: True)
            default_headers: Default headers to include in all requests
            user_agent: Custom user agent string
            debug: Enable debug mode with verbose logging (default: env ALTAN_DEBUG or False)
            
        Note:
            The client now includes:
            - Exponential backoff with jitter for retries
            - Proper HTTP/2 connection pooling
            - Graceful connection lifecycle management
            - Automatic resource cleanup
            - Request/response hooks for customization
            - Proxy support (HTTP/HTTPS/SOCKS)
            - Environment variable configuration
        """
        # Read from environment variables if not provided
        base_url = base_url or os.getenv("ALTAN_BASE_URL", "https://ai.altan.ai")
        api_key = api_key or os.getenv("ALTAN_API_KEY")
        timeout = timeout if timeout is not None else float(os.getenv("ALTAN_TIMEOUT", "60.0"))
        max_retries = max_retries if max_retries is not None else int(os.getenv("ALTAN_MAX_RETRIES", "3"))
        proxy = proxy or os.getenv("ALTAN_PROXY")
        
        # Debug mode from env
        if not debug:
            debug_env = os.getenv("ALTAN_DEBUG", "").lower()
            debug = debug_env in ("1", "true", "yes")
        
        # Enable debug logging if requested
        if debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)
            logger.debug("Debug mode enabled")
        
        self._base_client = BaseClient(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=keepalive_expiry,
            proxy=proxy,
            trust_env=trust_env,
            default_headers=default_headers,
            user_agent=user_agent,
        )
        
        # Initialize sub-clients
        self._responses_client = ResponsesClient(self._base_client)
        self._activations_client = ActivationsClient(self._base_client)
    
    @property
    def responses(self) -> ResponsesClient:
        """
        Access the Responses API client.
        
        The Responses API provides stateless LLM interactions without requiring
        thread_id or room_id. Context is persisted in Redis.
        
        Returns:
            ResponsesClient instance
        """
        return self._responses_client
    
    @property
    def activations(self) -> ActivationsClient:
        """
        Access the Activations API client.
        
        The Activations API provides event-driven agent execution with full
        conversation context and database persistence.
        
        Returns:
            ActivationsClient instance
        """
        return self._activations_client
    
    async def close(self):
        """Close the client and release resources."""
        await self._base_client.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

