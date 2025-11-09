"""
Altan SDK - Python SDK for Altan API

A unified SDK providing:
- AI Agents: Chat with GPT-4, Claude, and other models
- Database: PostgREST-style database operations (DEPRECATED)
- Integration: Access to 5000+ platform integrations
"""

# Main modules
from .agents import Agent, MessageHistory
from .integration import Integration

# Deprecated database module (will issue deprecation warning on import)
from .database import Database, QueryBuilder

# Exceptions
from .exceptions import AltanSDKError, AltanAPIError, AltanConnectionError, AltanAuthenticationError

__version__ = "0.3.0"
__all__ = [
    # AI Agents
    "Agent",
    "MessageHistory",
    
    # Database
    "Database", 
    "QueryBuilder", 
    
    # Integration
    "Integration",
    
    # Exceptions
    "AltanSDKError", 
    "AltanAPIError", 
    "AltanConnectionError", 
    "AltanAuthenticationError"
]
