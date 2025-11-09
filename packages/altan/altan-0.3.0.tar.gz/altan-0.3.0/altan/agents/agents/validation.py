"""
Client-Side Validation Helpers

Pre-flight validation to catch errors before sending to API.
Provides helpful error messages and reduces unnecessary API calls.
"""

import logging
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


def validate_messages(
    messages: List[Union[Dict[str, Any], Any]],
    allow_empty: bool = False
) -> None:
    """
    Validate message list format.
    
    Checks:
    - Messages is a non-empty list
    - Each message has required fields (role, content or parts)
    - Role values are valid
    - Content/parts are properly formatted
    
    Args:
        messages: List of messages to validate
        allow_empty: Whether to allow empty message list
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(messages, list):
        raise ValidationError(
            f"messages must be a list, got {type(messages).__name__}"
        )
    
    if not messages and not allow_empty:
        raise ValidationError("messages list cannot be empty")
    
    valid_roles = {"user", "assistant", "system"}
    
    for i, msg in enumerate(messages):
        if not isinstance(msg, dict):
            raise ValidationError(
                f"Message {i} must be a dict, got {type(msg).__name__}"
            )
        
        # Check role
        if "role" not in msg:
            raise ValidationError(f"Message {i} missing required field: 'role'")
        
        role = msg["role"]
        if role not in valid_roles:
            raise ValidationError(
                f"Message {i} has invalid role '{role}'. "
                f"Must be one of: {', '.join(valid_roles)}"
            )
        
        # Check content or parts
        has_content = "content" in msg
        has_parts = "parts" in msg
        
        if not has_content and not has_parts:
            raise ValidationError(
                f"Message {i} must have either 'content' or 'parts'"
            )
        
        if has_content and has_parts:
            raise ValidationError(
                f"Message {i} cannot have both 'content' and 'parts'. "
                "These fields are mutually exclusive."
            )
        
        # Validate content if present
        if has_content:
            content = msg["content"]
            if not isinstance(content, (str, list)):
                raise ValidationError(
                    f"Message {i} content must be string or list, "
                    f"got {type(content).__name__}"
                )
            
            if isinstance(content, str) and not content.strip():
                raise ValidationError(f"Message {i} content cannot be empty")
        
        # Validate parts if present
        if has_parts:
            parts = msg["parts"]
            if not isinstance(parts, list):
                raise ValidationError(
                    f"Message {i} parts must be a list, "
                    f"got {type(parts).__name__}"
                )
            
            if not parts:
                raise ValidationError(f"Message {i} parts list cannot be empty")
            
            for j, part in enumerate(parts):
                if not isinstance(part, dict):
                    raise ValidationError(
                        f"Message {i}, part {j} must be a dict, "
                        f"got {type(part).__name__}"
                    )
                
                if "type" not in part:
                    raise ValidationError(
                        f"Message {i}, part {j} missing required field: 'type'"
                    )


def validate_tools(tools: List[Union[Dict[str, Any], Any]]) -> None:
    """
    Validate tool definitions.
    
    Checks:
    - Tools is a list
    - Each tool has required fields (type, function)
    - Function has name, description, parameters
    - Parameters schema is valid
    
    Args:
        tools: List of tool definitions to validate
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(tools, list):
        raise ValidationError(
            f"tools must be a list, got {type(tools).__name__}"
        )
    
    for i, tool in enumerate(tools):
        if not isinstance(tool, dict):
            raise ValidationError(
                f"Tool {i} must be a dict, got {type(tool).__name__}"
            )
        
        # Check type
        if "type" not in tool:
            raise ValidationError(f"Tool {i} missing required field: 'type'")
        
        if tool["type"] != "function":
            raise ValidationError(
                f"Tool {i} has unsupported type '{tool['type']}'. "
                "Only 'function' is supported."
            )
        
        # Check function
        if "function" not in tool:
            raise ValidationError(f"Tool {i} missing required field: 'function'")
        
        func = tool["function"]
        if not isinstance(func, dict):
            raise ValidationError(
                f"Tool {i} function must be a dict, "
                f"got {type(func).__name__}"
            )
        
        # Check function fields
        if "name" not in func:
            raise ValidationError(
                f"Tool {i} function missing required field: 'name'"
            )
        
        if not isinstance(func["name"], str) or not func["name"].strip():
            raise ValidationError(
                f"Tool {i} function name must be a non-empty string"
            )
        
        if "description" in func:
            if not isinstance(func["description"], str):
                raise ValidationError(
                    f"Tool {i} function description must be a string"
                )
        
        # Validate parameters if present
        if "parameters" in func:
            params = func["parameters"]
            if not isinstance(params, dict):
                raise ValidationError(
                    f"Tool {i} function parameters must be a dict, "
                    f"got {type(params).__name__}"
                )
            
            # Check parameters schema
            if "type" in params and params["type"] != "object":
                raise ValidationError(
                    f"Tool {i} function parameters type must be 'object', "
                    f"got '{params['type']}'"
                )
            
            if "properties" in params:
                if not isinstance(params["properties"], dict):
                    raise ValidationError(
                        f"Tool {i} function parameters properties must be a dict"
                    )


def validate_model(model: str) -> None:
    """
    Validate model name.
    
    Args:
        model: Model name to validate
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(model, str):
        raise ValidationError(
            f"model must be a string, got {type(model).__name__}"
        )
    
    if not model.strip():
        raise ValidationError("model cannot be empty")


def validate_temperature(temperature: float) -> None:
    """
    Validate temperature parameter.
    
    Args:
        temperature: Temperature value to validate
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(temperature, (int, float)):
        raise ValidationError(
            f"temperature must be a number, got {type(temperature).__name__}"
        )
    
    if temperature < 0.0 or temperature > 2.0:
        raise ValidationError(
            f"temperature must be between 0.0 and 2.0, got {temperature}"
        )


def validate_max_tokens(max_tokens: int) -> None:
    """
    Validate max_tokens parameter.
    
    Args:
        max_tokens: Max tokens value to validate
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(max_tokens, int):
        raise ValidationError(
            f"max_tokens must be an integer, got {type(max_tokens).__name__}"
        )
    
    if max_tokens < 1:
        raise ValidationError(
            f"max_tokens must be positive, got {max_tokens}"
        )


def validate_request_params(
    messages: List[Union[Dict[str, Any], Any]],
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    tools: Optional[List[Union[Dict[str, Any], Any]]] = None,
) -> None:
    """
    Validate common request parameters.
    
    Validates all provided parameters in one call.
    Useful for pre-flight checks before API calls.
    
    Args:
        messages: Messages to validate
        model: Model name to validate (if provided)
        temperature: Temperature to validate (if provided)
        max_tokens: Max tokens to validate (if provided)
        tools: Tools to validate (if provided)
        
    Raises:
        ValidationError: If any validation fails
    """
    validate_messages(messages)
    
    if model is not None:
        validate_model(model)
    
    if temperature is not None:
        validate_temperature(temperature)
    
    if max_tokens is not None:
        validate_max_tokens(max_tokens)
    
    if tools is not None:
        validate_tools(tools)


