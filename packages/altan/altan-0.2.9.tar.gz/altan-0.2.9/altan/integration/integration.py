"""
Integration class for the Altan SDK
"""

from typing import Dict, Any, Optional
from .connection import Connection
from ..exceptions import AltanAuthenticationError


class Integration:
    """Main Integration class for the Altan SDK"""
    
    def __init__(self, altan_api_key: str, base_url: str = "https://integration.altan.ai"):
        """
        Initialize the Integration client
        
        Args:
            altan_api_key: Your Altan API key
            base_url: Base URL for the Altan API (defaults to https://integration.altan.ai)
        """
        if not altan_api_key:
            raise AltanAuthenticationError("altan_api_key is required")
        
        self.api_key = altan_api_key
        self.base_url = base_url.rstrip('/')
        self._connections = {}
    
    def connection(self, connection_id: str) -> Connection:
        """
        Get a connection instance for a specific connection ID
        
        Args:
            connection_id: The ID of the connection
            
        Returns:
            Connection instance
        """
        if connection_id not in self._connections:
            self._connections[connection_id] = Connection(
                connection_id=connection_id,
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._connections[connection_id]
    
    def __call__(self, connection_id: str) -> Connection:
        """
        Make the Integration instance callable to create connections
        
        Args:
            connection_id: The ID of any connection
            
        Returns:
            Connection instance
            
        Example:
            integration = Integration(api_key="key")
            instagram_conn = integration("instagram_connection_id")
            salesforce_conn = integration("salesforce_connection_id")
        """
        return self.connection(connection_id)
    
    async def close_all_connections(self):
        """Close all active connections"""
        for connection in self._connections.values():
            await connection.close()
        self._connections.clear()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_all_connections()
