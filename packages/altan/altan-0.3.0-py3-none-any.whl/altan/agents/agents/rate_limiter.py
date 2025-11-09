"""
Client-Side Rate Limiting

Implements token bucket algorithm to prevent hitting API rate limits.
Useful for controlling request rate before sending to the server.
"""

import asyncio
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter for client-side rate limiting.
    
    Prevents overwhelming the API by limiting requests per second.
    Uses the token bucket algorithm for smooth rate limiting with bursts.
    
    Example:
        ```python
        # Allow 100 requests/second with bursts up to 200
        limiter = RateLimiter(rate=100, burst=200)
        
        async def make_request():
            await limiter.acquire()  # Waits if rate limit exceeded
            response = await client.responses.create(...)
            return response
        ```
    """
    
    def __init__(self, rate: float, burst: Optional[int] = None):
        """
        Initialize rate limiter.
        
        Args:
            rate: Maximum requests per second
            burst: Maximum burst size (tokens available immediately). 
                   Defaults to rate if not specified.
        """
        if rate <= 0:
            raise ValueError("Rate must be positive")
        
        self.rate = rate
        self.burst = burst if burst is not None else int(rate)
        
        if self.burst < 1:
            self.burst = 1
        
        # Token bucket state
        self._tokens = float(self.burst)
        self._last_update = time.time()
        self._lock = asyncio.Lock()
        
        logger.debug(f"RateLimiter initialized: {rate} req/s, burst={self.burst}")
    
    async def acquire(self, tokens: float = 1.0) -> None:
        """
        Acquire tokens from the bucket, waiting if necessary.
        
        This method will block until enough tokens are available.
        
        Args:
            tokens: Number of tokens to acquire (default: 1.0)
        """
        if tokens <= 0:
            return
        
        async with self._lock:
            while True:
                # Refill tokens based on time elapsed
                now = time.time()
                elapsed = now - self._last_update
                self._last_update = now
                
                # Add tokens at the configured rate
                self._tokens += elapsed * self.rate
                
                # Cap at burst size
                if self._tokens > self.burst:
                    self._tokens = float(self.burst)
                
                # Check if we have enough tokens
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return
                
                # Calculate wait time for next token
                tokens_needed = tokens - self._tokens
                wait_time = tokens_needed / self.rate
                
                # Release lock while waiting
                logger.debug(f"Rate limit reached, waiting {wait_time:.3f}s")
                await asyncio.sleep(wait_time)
                # Loop will refill tokens after sleep
    
    def try_acquire(self, tokens: float = 1.0) -> bool:
        """
        Try to acquire tokens without waiting.
        
        Returns True if tokens were acquired, False otherwise.
        This is a non-blocking alternative to acquire().
        
        Args:
            tokens: Number of tokens to try to acquire (default: 1.0)
            
        Returns:
            True if tokens were acquired, False if rate limit exceeded
        """
        if tokens <= 0:
            return True
        
        # Refill tokens based on time elapsed
        now = time.time()
        elapsed = now - self._last_update
        self._last_update = now
        
        # Add tokens at the configured rate
        self._tokens += elapsed * self.rate
        
        # Cap at burst size
        if self._tokens > self.burst:
            self._tokens = float(self.burst)
        
        # Check if we have enough tokens
        if self._tokens >= tokens:
            self._tokens -= tokens
            return True
        
        return False
    
    def get_available_tokens(self) -> float:
        """
        Get the number of currently available tokens.
        
        Returns:
            Number of tokens available for immediate use
        """
        # Refill tokens based on time elapsed (without acquiring lock)
        now = time.time()
        elapsed = now - self._last_update
        tokens = self._tokens + (elapsed * self.rate)
        
        # Cap at burst size
        if tokens > self.burst:
            tokens = float(self.burst)
        
        return tokens
    
    def reset(self) -> None:
        """Reset the rate limiter to initial state (full tokens)."""
        self._tokens = float(self.burst)
        self._last_update = time.time()
        logger.debug("RateLimiter reset")


class NoopRateLimiter(RateLimiter):
    """
    No-op rate limiter that doesn't actually limit.
    
    Useful for disabling rate limiting without changing code.
    """
    
    def __init__(self):
        """Initialize no-op rate limiter."""
        # Don't call super().__init__() to avoid validation
        self.rate = float('inf')
        self.burst = float('inf')
        self._tokens = float('inf')
        self._last_update = time.time()
        self._lock = asyncio.Lock()
    
    async def acquire(self, tokens: float = 1.0) -> None:
        """Immediately return without waiting."""
        return
    
    def try_acquire(self, tokens: float = 1.0) -> bool:
        """Always return True."""
        return True

