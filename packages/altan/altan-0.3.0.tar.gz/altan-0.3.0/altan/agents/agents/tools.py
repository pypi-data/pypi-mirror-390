"""
Tool registry and execution utilities.

Provides a convenient way to register and manage tools for AI function calling.
"""

import inspect
import logging
from typing import Any, Callable, Dict, List, Optional

from .types import ToolDefinition

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Registry for managing tools/functions for AI execution.
    
    Provides:
    - Easy tool registration
    - Automatic schema generation from Python functions
    - Tool execution
    - Type validation
    
    Example:
        ```python
        registry = ToolRegistry()
        
        @registry.tool
        def get_weather(location: str, unit: str = "fahrenheit") -> dict:
            '''Get current weather for a location.'''
            return {"temp": 72, "condition": "sunny"}
        
        # Or register explicitly
        registry.register("calculate", calculate_function)
        
        # Use with client
        response = await client.responses.chat(
            history,
            model="gpt-4o",
            tools=registry,
        )
        ```
    """
    
    def __init__(self):
        """Initialize empty tool registry."""
        self._tools: Dict[str, Callable] = {}
        self._definitions: List[ToolDefinition] = []
    
    def register(
        self,
        name: str,
        function: Callable,
        description: Optional[str] = None,
        tool_type: str = "server",
    ) -> None:
        """
        Register a tool function.
        
        Args:
            name: Tool name (must match function calls from AI)
            function: Callable to execute
            description: Optional description (uses docstring if not provided)
            tool_type: "client" or "server" (default: "server")
        """
        self._tools[name] = function
        
        # Generate definition
        definition = self._generate_definition(name, function, description, tool_type)
        self._definitions.append(definition)
        
        logger.debug(f"Registered tool: {name} (type={tool_type})")
    
    def tool(
        self,
        description: Optional[str] = None,
        tool_type: str = "server",
    ) -> Callable:
        """
        Decorator to register a tool.
        
        Args:
            description: Optional description override
            tool_type: "client" or "server"
            
        Example:
            ```python
            @registry.tool
            def my_function(arg1: str, arg2: int) -> str:
                '''Does something useful.'''
                return result
            ```
        """
        def decorator(func: Callable) -> Callable:
            name = func.__name__
            self.register(name, func, description, tool_type)
            return func
        return decorator
    
    async def execute(self, name: str, args: Dict[str, Any]) -> Any:
        """
        Execute a registered tool.
        
        Args:
            name: Tool name
            args: Tool arguments
            
        Returns:
            Tool execution result
            
        Raises:
            ValueError: Tool not found
        """
        if name not in self._tools:
            logger.error(f"Tool not found: {name}. Available tools: {list(self._tools.keys())}")
            raise ValueError(f"Tool not found: {name}")
        
        function = self._tools[name]
        logger.debug(f"Executing tool: {name} with args: {args}")
        
        # Handle async functions
        try:
            if inspect.iscoroutinefunction(function):
                result = await function(**args)
            else:
                result = function(**args)
            logger.debug(f"Tool {name} execution completed: {result}")
            return result
        except Exception as e:
            logger.error(f"Tool {name} execution failed: {e}", exc_info=True)
            raise
    
    def get_definitions(self) -> List[ToolDefinition]:
        """Get all tool definitions for API calls."""
        return self._definitions.copy()
    
    def has_tool(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self._tools
    
    def _generate_definition(
        self,
        name: str,
        function: Callable,
        description: Optional[str],
        tool_type: str,
    ) -> ToolDefinition:
        """Generate OpenAI-compatible tool definition from function."""
        
        # Get description from docstring if not provided
        if description is None:
            description = function.__doc__ or f"Execute {name}"
            description = description.strip()
        
        # Get function signature
        sig = inspect.signature(function)
        
        # Build parameters schema
        properties: Dict[str, Any] = {}
        required: List[str] = []
        
        for param_name, param in sig.parameters.items():
            # Skip self/cls parameters
            if param_name in ("self", "cls"):
                continue
            
            # Determine parameter type
            param_type = "string"  # default
            if param.annotation != inspect.Parameter.empty:
                ann = param.annotation
                if ann == int:
                    param_type = "integer"
                elif ann == float:
                    param_type = "number"
                elif ann == bool:
                    param_type = "boolean"
                elif ann in (list, List):
                    param_type = "array"
                elif ann in (dict, Dict):
                    param_type = "object"
            
            properties[param_name] = {
                "type": param_type,
                "description": f"Parameter {param_name}",
            }
            
            # Check if required (no default value)
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        # Build tool definition
        definition: ToolDefinition = {
            "type": "function",
            "tool_type": tool_type,  # type: ignore
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }
        
        return definition
    
    def __len__(self) -> int:
        """Get number of registered tools."""
        return len(self._tools)
    
    def __contains__(self, name: str) -> bool:
        """Check if tool is registered."""
        return name in self._tools

