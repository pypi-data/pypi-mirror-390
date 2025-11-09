"""
Cookbook 02: Function Calling & Tool Usage

Demonstrates:
- Tool/function definitions
- Tool call execution
- Tool result handling
- Multi-step tool chains
"""

import asyncio
import sys
import json
from typing import Dict, Any, List
from utils import (
    print_header,
    print_section,
    print_message,
    print_tool_call,
    print_tool_result,
    print_success,
    print_info,
    print_event,
    get_client,
    MessageHistory,
)
from utils.display import Colors

sys.path.insert(0, "../..")
from agents.types import ToolDefinition, StreamEvent


# Simulated tool functions
def get_weather(location: str, unit: str = "fahrenheit") -> Dict[str, Any]:
    """Simulate getting weather data."""
    # Mock weather data
    weather_data = {
        "San Francisco": {"temp": 65, "condition": "Partly cloudy", "humidity": 70},
        "New York": {"temp": 45, "condition": "Rainy", "humidity": 85},
        "London": {"temp": 50, "condition": "Foggy", "humidity": 90},
        "Tokyo": {"temp": 72, "condition": "Sunny", "humidity": 60},
    }
    
    data = weather_data.get(location, {"temp": 70, "condition": "Unknown", "humidity": 50})
    
    if unit == "celsius":
        data["temp"] = int((data["temp"] - 32) * 5/9)
        unit_str = "°C"
    else:
        unit_str = "°F"
    
    return {
        "location": location,
        "temperature": f"{data['temp']}{unit_str}",
        "condition": data["condition"],
        "humidity": f"{data['humidity']}%",
    }


def search_database(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Simulate database search."""
    # Mock search results
    all_results = [
        {"id": 1, "title": "Introduction to AI", "relevance": 0.95},
        {"id": 2, "title": "Machine Learning Basics", "relevance": 0.92},
        {"id": 3, "title": "Neural Networks Explained", "relevance": 0.88},
        {"id": 4, "title": "Deep Learning Fundamentals", "relevance": 0.85},
        {"id": 5, "title": "Natural Language Processing", "relevance": 0.80},
        {"id": 6, "title": "Computer Vision Techniques", "relevance": 0.75},
    ]
    
    return all_results[:limit]


def calculate(expression: str) -> Dict[str, Any]:
    """Safely evaluate a mathematical expression."""
    try:
        # Simple safe evaluation (in production, use a proper math parser)
        result = eval(expression, {"__builtins__": {}}, {})
        return {"expression": expression, "result": result, "success": True}
    except Exception as e:
        return {"expression": expression, "error": str(e), "success": False}


# Tool definitions
TOOLS: List[ToolDefinition] = [
    {
        "type": "function",
        "tool_type": "server",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name (e.g., 'San Francisco')",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit",
                    },
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "tool_type": "server",
        "function": {
            "name": "search_database",
            "description": "Search for articles in the knowledge base",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "tool_type": "server",
        "function": {
            "name": "calculate",
            "description": "Evaluate a mathematical expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate",
                    },
                },
                "required": ["expression"],
            },
        },
    },
]


# Tool execution mapping
TOOL_FUNCTIONS = {
    "get_weather": get_weather,
    "search_database": search_database,
    "calculate": calculate,
}


async def run_function_calling() -> None:
    """Demonstrate function calling with various tools."""
    
    print_header("Cookbook: Function Calling & Tool Usage")
    
    print("This cookbook demonstrates how to use tools/functions with the SDK.")
    print("The AI can call tools to get real data and perform actions.\n")
    
    # Test scenarios
    scenarios = [
        {
            "name": "Weather Lookup",
            "prompt": "What's the weather like in San Francisco and Tokyo?",
            "description": "Demonstrates multiple tool calls in one response",
        },
        {
            "name": "Knowledge Search",
            "prompt": "Search for articles about neural networks and tell me about the top result",
            "description": "Demonstrates tool call followed by interpretation",
        },
        {
            "name": "Calculator",
            "prompt": "What is 15 * 23 + 89?",
            "description": "Demonstrates computational tool usage",
        },
    ]
    
    async with get_client() as client:
        for i, scenario in enumerate(scenarios, 1):
            print_section(f"Scenario {i}: {scenario['name']}")
            print(f"Description: {scenario['description']}\n")
            
            # User message
            print_message("user", scenario["prompt"])
            
            # Initialize conversation
            history = MessageHistory()
            history.add_user_message(scenario["prompt"])
            
            # First request - AI will likely call tools
            print_message("assistant", "", agent_name="gpt-4o")
            
            message_parts = []
            current_part_type = None
            
            async for event in client.responses.create_stream(
                messages=history.get_messages(),
                model="gpt-5",
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.7,
                reasoning=True,
                reasoning_effort="low"
            ):
                event_type = event.get("event_type", "")
                data = event.get("data", {})
                
                if event_type == "message_part.added":
                    part_type = data.get("type")
                    current_part_type = part_type
                    # Collect all parts (text, tool, thinking)
                    part_data = data.copy()
                    
                    # Initialize arguments field for tool parts
                    if part_type == "tool" and "arguments" not in part_data:
                        part_data["arguments"] = ""
                    
                    message_parts.append(part_data)
                    
                    if part_type == "tool":
                        # Tool call started - we'll show details when complete
                        print_tool_call(data.get("name", ""), {}, indent=1)
                    elif part_type == "thinking":
                        # Thinking started
                        print(f"  {Colors.DIM}💭 [thinking...]{Colors.RESET} ", end="", flush=True)
                    elif part_type == "text":
                        # Text part started
                        print("  ", end="", flush=True)
                
                elif event_type == "message_part.updated":
                    delta = data.get("delta", "")
                    part_id = data.get("id")
                    
                    if delta and current_part_type == "text":
                        # Only stream text deltas
                        print(delta, end="", flush=True)
                    elif delta and current_part_type == "thinking":
                        # Stream thinking deltas with dimmed color
                        print(f"{Colors.DIM}{delta}{Colors.RESET}", end="", flush=True)
                    elif delta and current_part_type == "tool":
                        # Accumulate tool arguments deltas
                        if part_id:
                            for part in message_parts:
                                if part.get("id") == part_id:
                                    # Append delta to arguments
                                    current_args = part.get("arguments", "")
                                    part["arguments"] = current_args + delta
                                    break
                
                elif event_type == "message_part.completed":
                    # Update part with final data
                    part_id = data.get("id")
                    for part in message_parts:
                        if part.get("id") == part_id:
                            # Merge final data, but preserve accumulated arguments if not in data
                            if "arguments" in part and "arguments" not in data:
                                data["arguments"] = part["arguments"]
                            part.update(data)
                            break
                    
                    # Handle completion based on part type
                    part_type = data.get("type")
                    if part_type == "tool":
                        # Show the completed tool call
                        tool_name = data.get("name", "")
                        tool_args_str = data.get("arguments", "{}")
                        
                        # Get the accumulated arguments from our tracking
                        for part in message_parts:
                            if part.get("id") == part_id:
                                tool_args_str = part.get("arguments", "{}")
                                break
                        
                        try:
                            tool_args = json.loads(tool_args_str) if isinstance(tool_args_str, str) else tool_args_str
                        except Exception as e:
                            print(f"\n  ⚠️  Failed to parse tool arguments: {tool_args_str}")
                            print(f"  Error: {e}")
                            tool_args = {}
                        print_tool_call(tool_name, tool_args, indent=1)
                    elif part_type in ["text", "thinking"]:
                        # End the line for text/thinking
                        print()
                
                elif event_type == "response.completed":
                    pass
                else:
                    print_info(f"unknown event_type: {event_type}")

            
            # Build full text from text parts
            full_text = ""
            for part in message_parts:
                if part.get("type") == "text":
                    full_text += part.get("text", "")
            
            # Add the assistant's response with parts to history (IMPORTANT!)
            # This is the manual way - collecting parts and adding them explicitly
            if message_parts:
                history.add_rich_assistant_message(message_parts, full_text)
                print_success(f"Added assistant message to history ({len(message_parts)} parts)")
            
            # Extract tool calls from completed message parts
            tool_calls = []
            for part in message_parts:
                if part.get("type") == "tool":
                    tool_name = part.get("name", "")
                    tool_args_str = part.get("arguments", "{}")
                    
                    print_info(f"Extracting tool call: {tool_name}, args_str: {tool_args_str}")
                    
                    try:
                        tool_args = json.loads(tool_args_str) if isinstance(tool_args_str, str) else tool_args_str
                    except Exception as e:
                        print(f"  ⚠️  Failed to parse tool arguments for {tool_name}: {e}")
                        print(f"  Raw arguments: {tool_args_str}")
                        tool_args = {}
                    
                    tool_calls.append({
                        "id": part.get("tool_call_id", ""),
                        "name": tool_name,
                        "arguments": tool_args,
                    })
            
            # Execute tool calls if any
            if tool_calls:
                print()
                print_success(f"Executing {len(tool_calls)} tool call(s)...")
                
                # Execute tools and add results to history
                tool_result_parts = []
                for tool_call in tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["arguments"]
                    tool_id = tool_call["id"]
                    
                    if tool_name in TOOL_FUNCTIONS:
                        result = TOOL_FUNCTIONS[tool_name](**tool_args)
                        print_tool_result(tool_name, result, indent=1)
                        
                        # Create tool result part (manual way)
                        tool_result_parts.append({
                            "type": "tool",
                            "tool_call_id": tool_id,
                            "name": tool_name,
                            "result": result,
                        })
                
                # Add tool results to history as a message with parts
                if tool_result_parts:
                    history.add_rich_assistant_message(tool_result_parts, "")
                    print_success(f"Added tool results to history ({len(tool_result_parts)} parts)")
                    print_info(f"Total messages in history: {len(history.get_messages())}")
            else:
                print_success("Response completed (no tools used)")
            
            print()
    
    print_section("Summary")
    print_success("Demonstrated low-level manual tool usage:")
    print("  ✓ Manual message part collection from events")
    print("  ✓ Explicit addition of parts to history with add_rich_assistant_message()")
    print("  ✓ Manual tool result part creation")
    print("  ✓ Proper multi-turn message history with parts")
    print()
    print("Key Low-Level Patterns Shown:")
    print("  → Collect parts during event streaming")
    print("  → Update parts on message_part.completed")
    print("  → Add complete parts to history after streaming")
    print("  → Create tool result parts manually")
    print("  → Add tool results as separate messages with parts")
    print()
    print("💡 For easier tool handling, see 02_function_calling_managed.py!")
    print("   The managed API handles all of this automatically.")


if __name__ == "__main__":
    asyncio.run(run_function_calling())

