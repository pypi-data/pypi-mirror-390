"""
Usage and Cost Tracking

Tracks token usage and estimated costs across API calls.
Useful for monitoring and budget management.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
import threading

logger = logging.getLogger(__name__)


@dataclass
class UsageStats:
    """Statistics for a single API call."""
    request_id: Optional[str] = None
    model: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0
    timestamp: Optional[float] = None


class UsageTracker:
    """
    Tracks token usage and costs across API calls.
    
    Automatically updated when responses include usage information.
    Thread-safe for concurrent access.
    
    Example:
        ```python
        client = AgentClient()
        
        # Make some requests
        response = await client.responses.chat(...)
        
        # Check usage
        print(f"Total tokens: {client.usage.total_tokens}")
        print(f"Total cost: ${client.usage.total_cost:.4f}")
        print(f"Requests: {client.usage.request_count}")
        ```
    """
    
    def __init__(self):
        """Initialize usage tracker."""
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_cost = 0.0
        self.request_count = 0
        
        self._history: List[UsageStats] = []
        self._lock = threading.Lock()
        
        logger.debug("UsageTracker initialized")
    
    def add_usage(
        self,
        usage: Union[Dict[str, Any], List[Dict[str, Any]]],
        model: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> None:
        """
        Add usage information from a response.
        
        Args:
            usage: Usage dict or list of usage dicts from API response
            model: Model name for cost estimation
            request_id: Optional request ID for tracking
        """
        with self._lock:
            # Handle both single dict and list of dicts
            usage_list = usage if isinstance(usage, list) else [usage]
            
            for usage_item in usage_list:
                # Extract token counts
                prompt = usage_item.get("prompt_tokens", 0)
                completion = usage_item.get("completion_tokens", 0)
                total = usage_item.get("total_tokens", prompt + completion)
                
                # Update totals
                self.prompt_tokens += prompt
                self.completion_tokens += completion
                self.total_tokens += total
                self.request_count += 1
                
                # Estimate cost (rough estimates, update with actual pricing)
                cost = self._estimate_cost(
                    prompt=prompt,
                    completion=completion,
                    model=model or usage_item.get("model", "unknown")
                )
                self.total_cost += cost
                
                # Store in history
                import time
                stats = UsageStats(
                    request_id=request_id,
                    model=model or usage_item.get("model"),
                    prompt_tokens=prompt,
                    completion_tokens=completion,
                    total_tokens=total,
                    estimated_cost=cost,
                    timestamp=time.time(),
                )
                self._history.append(stats)
                
                logger.debug(
                    f"Usage added: {total} tokens, ${cost:.6f} "
                    f"(model={stats.model})"
                )
    
    def _estimate_cost(
        self,
        prompt: int,
        completion: int,
        model: str
    ) -> float:
        """
        Estimate cost based on token counts and model.
        
        Note: These are rough estimates. Actual pricing may vary.
        Update this method with current pricing from your provider.
        """
        # Rough pricing estimates (per 1M tokens) as of 2024
        pricing = {
            # OpenAI
            "gpt-4o": {"prompt": 2.50, "completion": 10.00},
            "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
            "gpt-4-turbo": {"prompt": 10.00, "completion": 30.00},
            "gpt-3.5-turbo": {"prompt": 0.50, "completion": 1.50},
            "o1": {"prompt": 15.00, "completion": 60.00},
            "o1-mini": {"prompt": 3.00, "completion": 12.00},
            
            # Anthropic
            "claude-sonnet-4": {"prompt": 3.00, "completion": 15.00},
            "claude-sonnet-4-5": {"prompt": 3.00, "completion": 15.00},
            "claude-opus-4": {"prompt": 15.00, "completion": 75.00},
            "claude-haiku-4": {"prompt": 0.25, "completion": 1.25},
        }
        
        # Find matching pricing (case-insensitive, partial match)
        model_lower = model.lower()
        model_pricing = None
        
        for model_key, price in pricing.items():
            if model_key in model_lower or model_lower in model_key:
                model_pricing = price
                break
        
        # Default to GPT-4o pricing if unknown
        if model_pricing is None:
            model_pricing = pricing["gpt-4o"]
            logger.debug(f"Unknown model '{model}', using GPT-4o pricing")
        
        # Calculate cost (pricing is per 1M tokens)
        prompt_cost = (prompt / 1_000_000) * model_pricing["prompt"]
        completion_cost = (completion / 1_000_000) * model_pricing["completion"]
        
        return prompt_cost + completion_cost
    
    def get_history(self, limit: Optional[int] = None) -> List[UsageStats]:
        """
        Get usage history.
        
        Args:
            limit: Maximum number of recent entries to return
            
        Returns:
            List of UsageStats, most recent first
        """
        with self._lock:
            history = list(reversed(self._history))
            if limit:
                history = history[:limit]
            return history
    
    def get_stats_by_model(self) -> Dict[str, Dict[str, Any]]:
        """
        Get aggregated statistics grouped by model.
        
        Returns:
            Dict mapping model name to stats (tokens, cost, request count)
        """
        with self._lock:
            stats: Dict[str, Dict[str, Any]] = {}
            
            for entry in self._history:
                model = entry.model or "unknown"
                
                if model not in stats:
                    stats[model] = {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0,
                        "estimated_cost": 0.0,
                        "request_count": 0,
                    }
                
                stats[model]["prompt_tokens"] += entry.prompt_tokens
                stats[model]["completion_tokens"] += entry.completion_tokens
                stats[model]["total_tokens"] += entry.total_tokens
                stats[model]["estimated_cost"] += entry.estimated_cost
                stats[model]["request_count"] += 1
            
            return stats
    
    def reset(self) -> None:
        """Reset all counters and history."""
        with self._lock:
            self.total_tokens = 0
            self.prompt_tokens = 0
            self.completion_tokens = 0
            self.total_cost = 0.0
            self.request_count = 0
            self._history.clear()
            logger.debug("UsageTracker reset")
    
    def __str__(self) -> str:
        """String representation of current usage."""
        return (
            f"UsageTracker("
            f"requests={self.request_count}, "
            f"tokens={self.total_tokens}, "
            f"cost=${self.total_cost:.4f})"
        )
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return self.__str__()

