"""
Connection class for handling individual connections
"""

from typing import Dict, Any, Optional
import httpx
from ..exceptions import AltanAPIError, AltanConnectionError


class Connection:
    """Represents a connection to a specific integration (e.g., Instagram)"""
    
    def __init__(self, connection_id: str, api_key: str, base_url: str = "https://integration.altan.ai", timeout: int = 90.0):
        """
        Initialize a connection
        
        Args:
            connection_id: The ID of the connection
            api_key: The Altan API key
            base_url: Base URL for the Altan API
            timeout: Timeout for the HTTP client
        """
        self.connection_id = connection_id
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self._client = httpx.AsyncClient(
            headers={"X-Altan-Key": self.api_key},
            timeout=timeout
        )
    
    async def execute(self, action_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action on this connection
        
        Args:
            action_name: The ID of the action type to execute
            payload: The payload to send with the action
            
        Returns:
            Dict containing the response from the API
            
        Raises:
            AltanAPIError: If the API returns an error
            AltanConnectionError: If there's a connection error
        """
        url = f"{self.base_url}/connection/{self.connection_id}/actions/{action_name}/execute"
        
        is_success = False
        try:
            response = await self._client.post(
                url,
                json={"payload": payload}
            )
            
            # Handle different response types
            content_type = response.headers.get('content-type', '').lower()
            is_success = True
            
            if response.status_code >= 400:
                try:
                    error_data = response.json() if 'application/json' in content_type else response.text
                except:
                    error_data = response.text
                
                raise AltanAPIError(
                    f"API request failed: {response.status_code}  -- {error_data}",
                    status_code=response.status_code,
                    response_data=error_data
                )
            
            # Parse response based on content type
            if 'application/json' in content_type:
                try:
                    data = response.json()
                except:
                    data = {"payload": response.text}
            else:
                # For non-JSON responses (files, text, etc.)
                data = {"payload": response.content}
            
            # Un-nest response for a cleaner interface
            data = data.get("data", {})
            stats = data.pop("__stats", {})
            data = {**data, **stats, "success": is_success}

            return data
            
        except httpx.TimeoutException:
            raise AltanConnectionError("Request timed out")
        except httpx.ConnectError:
            raise AltanConnectionError("Failed to connect to Altan API")
        except httpx.RequestError as e:
            raise AltanConnectionError(f"Request error: {str(e)}")
    
    async def close(self):
        """Close the HTTP client"""
        await self._client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
