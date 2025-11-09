"""
Altan SDK - Python SDK for Altan API

A unified SDK providing:
- AI Agents: Chat with GPT-4, Claude, and other models
- Database: PostgREST-style database operations
- Integration: Access to 5000+ platform integrations
"""

# Main modules
from .agents import Agent, MessageHistory
from .database import Database, QueryBuilder
from .integration import Integration

# Exceptions
from .exceptions import AltanSDKError, AltanAPIError, AltanConnectionError, AltanAuthenticationError

__version__ = "0.2.1"
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
