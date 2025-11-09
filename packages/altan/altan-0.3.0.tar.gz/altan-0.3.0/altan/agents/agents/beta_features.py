"""
Beta Features Management

Pre-defined constants for beta feature headers, similar to OpenAI SDK.
Makes it easier to enable and discover beta features.
"""

from typing import List


class BetaFeatures:
    """
    Constants for beta feature headers.
    
    Use these instead of hardcoding header strings to get IDE autocomplete
    and ensure correct spelling.
    
    Example:
        ```python
        from altan.agents.agents import BetaFeatures
        
        response = await client.responses.create(
            messages=[...],
            model="claude-sonnet-4",
            reasoning=True,
            beta_headers=[BetaFeatures.EXTENDED_THINKING],
        )
        ```
    """
    
    # Anthropic beta features
    EXTENDED_THINKING = "extended-thinking-2024-12-05"
    """Enable extended thinking mode (Anthropic Claude)."""
    
    PROMPT_CACHING = "prompt-caching-2024-07-31"
    """Enable prompt caching to reduce costs (Anthropic)."""
    
    COMPUTER_USE = "computer-use-2024-10-22"
    """Enable computer use capabilities (Anthropic)."""
    
    MESSAGE_BATCHES = "message-batches-2024-09-24"
    """Enable message batching for bulk requests (Anthropic)."""
    
    # OpenAI beta features (if needed)
    REALTIME_API = "realtime=v1"
    """Enable realtime API (OpenAI)."""
    
    ASSISTANTS_V2 = "assistants=v2"
    """Enable assistants API v2 (OpenAI)."""
    
    @classmethod
    def all_anthropic(cls) -> List[str]:
        """
        Get all Anthropic beta feature headers.
        
        Returns:
            List of all Anthropic beta headers
        """
        return [
            cls.EXTENDED_THINKING,
            cls.PROMPT_CACHING,
            cls.COMPUTER_USE,
            cls.MESSAGE_BATCHES,
        ]
    
    @classmethod
    def all_openai(cls) -> List[str]:
        """
        Get all OpenAI beta feature headers.
        
        Returns:
            List of all OpenAI beta headers
        """
        return [
            cls.REALTIME_API,
            cls.ASSISTANTS_V2,
        ]


# Convenience aliases
EXTENDED_THINKING = BetaFeatures.EXTENDED_THINKING
PROMPT_CACHING = BetaFeatures.PROMPT_CACHING
COMPUTER_USE = BetaFeatures.COMPUTER_USE
MESSAGE_BATCHES = BetaFeatures.MESSAGE_BATCHES

