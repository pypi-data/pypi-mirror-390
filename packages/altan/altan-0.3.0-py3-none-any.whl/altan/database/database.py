"""
Database class for the Altan SDK - PostgREST-style interface
"""

from typing import Dict, Any, List, Optional, Union
import httpx
from ..exceptions import AltanAPIError, AltanConnectionError


class QueryBuilder:
    """Query builder for database operations with PostgREST-style chainable interface"""
    
    def __init__(self, client: httpx.AsyncClient, base_url: str, table: str):
        self._client = client
        self._base_url = base_url
        self._table = table
        self._select_fields = "*"
        self._filters = []
        self._order = []
        self._limit_value = None
        self._offset_value = None
        self._single = False
    
    def select(self, fields: str = "*") -> "QueryBuilder":
        """
        Select specific fields
        
        Args:
            fields: Comma-separated field names or "*" for all fields
            
        Returns:
            QueryBuilder instance for chaining
            
        Example:
            .select("id,name,email")
            .select("*")
        """
        self._select_fields = fields
        return self
    
    def eq(self, column: str, value: Any) -> "QueryBuilder":
        """
        Filter where column equals value
        
        Args:
            column: Column name
            value: Value to match
            
        Returns:
            QueryBuilder instance for chaining
        """
        self._filters.append(f"{column}=eq.{value}")
        return self
    
    def neq(self, column: str, value: Any) -> "QueryBuilder":
        """Filter where column does not equal value"""
        self._filters.append(f"{column}=neq.{value}")
        return self
    
    def gt(self, column: str, value: Any) -> "QueryBuilder":
        """Filter where column is greater than value"""
        self._filters.append(f"{column}=gt.{value}")
        return self
    
    def gte(self, column: str, value: Any) -> "QueryBuilder":
        """Filter where column is greater than or equal to value"""
        self._filters.append(f"{column}=gte.{value}")
        return self
    
    def lt(self, column: str, value: Any) -> "QueryBuilder":
        """Filter where column is less than value"""
        self._filters.append(f"{column}=lt.{value}")
        return self
    
    def lte(self, column: str, value: Any) -> "QueryBuilder":
        """Filter where column is less than or equal to value"""
        self._filters.append(f"{column}=lte.{value}")
        return self
    
    def like(self, column: str, pattern: str) -> "QueryBuilder":
        """Filter where column matches pattern (case sensitive)"""
        self._filters.append(f"{column}=like.{pattern}")
        return self
    
    def ilike(self, column: str, pattern: str) -> "QueryBuilder":
        """Filter where column matches pattern (case insensitive)"""
        self._filters.append(f"{column}=ilike.{pattern}")
        return self
    
    def is_null(self, column: str) -> "QueryBuilder":
        """Filter where column is null"""
        self._filters.append(f"{column}=is.null")
        return self
    
    def not_null(self, column: str) -> "QueryBuilder":
        """Filter where column is not null"""
        self._filters.append(f"{column}=not.is.null")
        return self
    
    def in_(self, column: str, values: List[Any]) -> "QueryBuilder":
        """Filter where column is in list of values"""
        values_str = ",".join([f'"{v}"' if isinstance(v, str) else str(v) for v in values])
        self._filters.append(f"{column}=in.({values_str})")
        return self
    
    def order_by(self, column: str, ascending: bool = True) -> "QueryBuilder":
        """
        Order results by column
        
        Args:
            column: Column name to order by
            ascending: True for ASC, False for DESC
            
        Returns:
            QueryBuilder instance for chaining
        """
        direction = "asc" if ascending else "desc"
        self._order.append(f"{column}.{direction}")
        return self
    
    def limit(self, count: int) -> "QueryBuilder":
        """Limit number of results"""
        self._limit_value = count
        return self
    
    def offset(self, count: int) -> "QueryBuilder":
        """Offset results (for pagination)"""
        self._offset_value = count
        return self
    
    def single(self) -> "QueryBuilder":
        """
        Expect a single result (will error if more than one)
        Useful for getting one specific record
        """
        self._single = True
        return self
    
    def _build_url(self) -> str:
        """Build the final URL with query parameters"""
        url = f"{self._base_url}/{self._table}"
        params = []
        
        # Add select fields
        if self._select_fields != "*":
            params.append(f"select={self._select_fields}")
        
        # Add filters
        for filter_param in self._filters:
            params.append(filter_param)
        
        # Add ordering
        if self._order:
            params.append(f"order={','.join(self._order)}")
        
        # Add limit
        if self._limit_value is not None:
            params.append(f"limit={self._limit_value}")
        
        # Add offset
        if self._offset_value is not None:
            params.append(f"offset={self._offset_value}")
        
        if params:
            url += "?" + "&".join(params)
        
        return url
    
    async def execute(self) -> Dict[str, Any]:
        """
        Execute the query and return results
        
        Returns:
            Dict containing success status, data, and stats
            
        Raises:
            AltanAPIError: If the API returns an error
            AltanConnectionError: If there's a connection error
        """
        url = self._build_url()
        
        headers = {}
        if self._single:
            headers["Accept"] = "application/vnd.pgrst.object+json"
        
        try:
            response = await self._client.get(url, headers=headers)
            
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                except:
                    error_data = response.text
                
                raise AltanAPIError(
                    f"Database query failed: {response.status_code}",
                    status_code=response.status_code,
                    response_data=error_data
                )
            
            # Parse response
            try:
                data = response.json()
            except:
                data = response.text
            
            return {
                "success": True,
                "data": data,
                "__stats": {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "url": str(response.url),
                    "elapsed_time": response.elapsed.total_seconds(),
                    "response_type": "json",
                    "query_url": url
                }
            }
            
        except httpx.TimeoutException:
            raise AltanConnectionError("Database request timed out")
        except httpx.ConnectError:
            raise AltanConnectionError("Failed to connect to Altan Database API")
        except httpx.RequestError as e:
            raise AltanConnectionError(f"Database request error: {str(e)}")


class Database:
    """Database client for Altan SDK with PostgREST-style interface"""
    
    def __init__(self, 
                 altan_api_key: Optional[str] = None,
                 bearer_token: Optional[str] = None,
                 database_id: Optional[str] = None, 
                 base_url: str = "http://database.altan.ai"):
        """
        Initialize the Database client
        
        Args:
            altan_api_key: Your Altan API key (for X-Altan-Key header)
            bearer_token: Bearer token for authorization (recommended)
            database_id: UUID of the database to connect to (optional for Bearer auth)
            base_url: Base URL for the Altan Database API
            
        Note:
            Either altan_api_key or bearer_token must be provided.
            Bearer token auth works without database_id in URL path.
        """
        if not altan_api_key and not bearer_token:
            raise ValueError("Either altan_api_key or bearer_token must be provided")
        
        self.api_key = altan_api_key
        self.bearer_token = bearer_token
        self.database_id = database_id
        self.base_url = base_url.rstrip('/')
        
        # Build headers based on available auth
        headers = {}
        if self.api_key:
            headers["X-Altan-Key"] = self.api_key
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        
        self._client = httpx.AsyncClient(
            headers=headers,
            timeout=90.0
        )
        
        # Use working URL pattern: no database_id in URL for Bearer auth
        if self.bearer_token:
            self._records_url = f"{self.base_url}/admin/records"
        else:
            if not database_id:
                raise ValueError("database_id is required when using altan_api_key authentication")
            self._records_url = f"{self.base_url}/admin/records/{self.database_id}"
    
    def from_table(self, table: str) -> QueryBuilder:
        """
        Create a query builder for a specific table
        
        Args:
            table: Name of the table
            
        Returns:
            QueryBuilder instance for chaining operations
            
        Example:
            db.from_table("invoices").select("*").eq("status", "paid").execute()
        """
        return QueryBuilder(self._client, self._records_url, table)
    
    def from_(self, table: str) -> QueryBuilder:
        """
        Create a query builder for a specific table (Supabase-style alias)
        
        Args:
            table: Name of the table
            
        Returns:
            QueryBuilder instance for chaining operations
            
        Example:
            db.from_("tasks").select("*").eq("status", "active").execute()
        """
        return self.from_table(table)
    
    # Convenience methods for common table operations
    def table(self, table: str) -> QueryBuilder:
        """Alias for from_table"""
        return self.from_table(table)
    
    async def insert(self, table: str, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Insert data into a table
        
        Args:
            table: Table name
            data: Single record (dict) or multiple records (list of dicts)
            
        Returns:
            Dict containing success status, inserted data, and stats
        """
        url = f"{self._records_url}/{table}"
        
        try:
            response = await self._client.post(
                url,
                json=data,
                headers={"Prefer": "return=representation"}
            )
            
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                except:
                    error_data = response.text
                
                raise AltanAPIError(
                    f"Insert failed: {response.status_code}",
                    status_code=response.status_code,
                    response_data=error_data
                )
            
            try:
                result_data = response.json()
            except:
                result_data = response.text
            
            return {
                "success": True,
                "data": result_data,
                "__stats": {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "url": str(response.url),
                    "elapsed_time": response.elapsed.total_seconds(),
                    "response_type": "json",
                    "operation": "insert"
                }
            }
            
        except httpx.TimeoutException:
            raise AltanConnectionError("Insert request timed out")
        except httpx.ConnectError:
            raise AltanConnectionError("Failed to connect to Altan Database API")
        except httpx.RequestError as e:
            raise AltanConnectionError(f"Insert request error: {str(e)}")
    
    async def update(self, table: str, data: Dict[str, Any], filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Update data in a table
        
        Args:
            table: Table name
            data: Data to update
            filters: Conditions for which records to update (optional)
            
        Returns:
            Dict containing success status, updated data, and stats
        """
        url = f"{self._records_url}/{table}"
        
        # Add filters as query parameters
        if filters:
            params = []
            for key, value in filters.items():
                params.append(f"{key}=eq.{value}")
            if params:
                url += "?" + "&".join(params)
        
        try:
            response = await self._client.patch(
                url,
                json=data,
                headers={"Prefer": "return=representation"}
            )
            
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                except:
                    error_data = response.text
                
                raise AltanAPIError(
                    f"Update failed: {response.status_code}",
                    status_code=response.status_code,
                    response_data=error_data
                )
            
            try:
                result_data = response.json()
            except:
                result_data = response.text
            
            return {
                "success": True,
                "data": result_data,
                "__stats": {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "url": str(response.url),
                    "elapsed_time": response.elapsed.total_seconds(),
                    "response_type": "json",
                    "operation": "update"
                }
            }
            
        except httpx.TimeoutException:
            raise AltanConnectionError("Update request timed out")
        except httpx.ConnectError:
            raise AltanConnectionError("Failed to connect to Altan Database API")
        except httpx.RequestError as e:
            raise AltanConnectionError(f"Update request error: {str(e)}")
    
    async def delete(self, table: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete data from a table
        
        Args:
            table: Table name
            filters: Conditions for which records to delete
            
        Returns:
            Dict containing success status and stats
        """
        url = f"{self._records_url}/{table}"
        
        # Add filters as query parameters
        params = []
        for key, value in filters.items():
            params.append(f"{key}=eq.{value}")
        
        if not params:
            raise ValueError("Delete operation requires at least one filter to prevent accidental deletion of all records")
        
        url += "?" + "&".join(params)
        
        try:
            response = await self._client.delete(url)
            
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                except:
                    error_data = response.text
                
                raise AltanAPIError(
                    f"Delete failed: {response.status_code}",
                    status_code=response.status_code,
                    response_data=error_data
                )
            
            return {
                "success": True,
                "data": {"deleted": True},
                "__stats": {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "url": str(response.url),
                    "elapsed_time": response.elapsed.total_seconds(),
                    "response_type": "json",
                    "operation": "delete"
                }
            }
            
        except httpx.TimeoutException:
            raise AltanConnectionError("Delete request timed out")
        except httpx.ConnectError:
            raise AltanConnectionError("Failed to connect to Altan Database API")
        except httpx.RequestError as e:
            raise AltanConnectionError(f"Delete request error: {str(e)}")
    
    async def close(self):
        """Close the HTTP client"""
        await self._client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()