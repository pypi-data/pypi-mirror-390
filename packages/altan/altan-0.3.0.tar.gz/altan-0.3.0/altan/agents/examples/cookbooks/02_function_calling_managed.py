"""
Cookbook 02: Function Calling & Tool Usage (Managed API)

Demonstrates:
- ToolRegistry for easy tool management
- Manual tool execution with ToolRequest events
- Automatic tool execution with auto_execute
- Multi-turn tool loops with chat()

This shows the NEW managed API for function calling.
"""

import asyncio
from logging import basicConfig, INFO
import sys
from typing import Dict, Any

sys.path.insert(0, "../..")
from agents import AgentClient, MessageHistory, ToolRegistry

basicConfig(level=INFO)


# ============================================================================
# Tool Functions (same as before, but cleaner registration)
# ============================================================================

def get_weather(location: str, unit: str = "fahrenheit") -> Dict[str, Any]:
    """Get current weather for a location."""
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


def calculate(expression: str) -> Dict[str, Any]:
    """Safely evaluate a mathematical expression."""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return {"expression": expression, "result": result, "success": True}
    except Exception as e:
        return {"expression": expression, "error": str(e), "success": False}


def search_articles(query: str, limit: int = 3) -> list:
    """Search for articles in the knowledge base."""
    all_results = [
        {"id": 1, "title": "Introduction to AI", "relevance": 0.95},
        {"id": 2, "title": "Machine Learning Basics", "relevance": 0.92},
        {"id": 3, "title": "Neural Networks Explained", "relevance": 0.88},
        {"id": 4, "title": "Deep Learning Fundamentals", "relevance": 0.85},
        {"id": 5, "title": "Natural Language Processing", "relevance": 0.80},
    ]
    return all_results[:limit]


# ============================================================================
# Example 1: Manual Tool Execution (Full Control)
# ============================================================================

async def run_manual_tool_execution() -> None:
    """Demonstrate manual tool execution with tool_request events."""
    
    print("=" * 80)
    print("📚 Example 1: Manual Tool Execution")
    print("=" * 80)
    print()
    print("Description: Full control - see tool requests, execute manually (single turn)")
    print()
    
    # Create tool registry
    registry = ToolRegistry()
    registry.register("get_weather", get_weather)
    registry.register("calculate", calculate)
    
    history = MessageHistory()
    history.add_user("What's the weather in Tokyo and what's 15 * 23?")
    
    print("👤 User:")
    print("  What's the weather in Tokyo and what's 15 * 23?")
    print()
    
    print("🤖 Assistant:")
    print()
    
    async with AgentClient(base_url="http://localhost:8000") as client:
        async for event in client.responses.stream(
            history,
            model="gpt-5",
            tools=registry,
            auto_execute=False,  # Manual control - just see tool requests
        ):
            if event["type"] == "text":
                print(f"  {event['delta']}", end="", flush=True)
            
            elif event["type"] == "thinking":
                # Stream thinking/reasoning
                pass  # Optionally print thinking
            
            elif event["type"] == "tool_request":
                # Tool requested - we can execute manually if desired
                print(f"\n  🔧 Tool Requested: {event['name']}({event['args']})")
                
                # Execute the tool
                result = await registry.execute(event["name"], event["args"])
                print(f"  📦 Tool Result: {result}")
                print("  ", end="")
            
            elif event["type"] == "complete":
                print("\n")
                history.add_assistant(event)
                print(f"✓ Response completed (single turn)")
                if event.get("tool_calls"):
                    print(f"  • Tool calls detected: {len(event['tool_calls'])}")
                    print(f"  • Use chat() with auto_execute=True for multi-turn loop")
    
    print()


# ============================================================================
# Example 2: Automatic Tool Execution (Streaming)
# ============================================================================

async def run_auto_tool_execution_streaming() -> None:
    """Demonstrate automatic tool execution with streaming."""
    
    print("=" * 80)
    print("📚 Example 2: Auto Tool Execution (Streaming)")
    print("=" * 80)
    print()
    print("Description: Tools execute automatically, stream results")
    print()
    
    # Create tool registry with decorator
    registry = ToolRegistry()
    
    @registry.tool
    def get_weather(location: str, unit: str = "fahrenheit") -> Dict[str, Any]:
        """Get current weather for a location."""
        weather_data = {
            "San Francisco": {"temp": 65, "condition": "Partly cloudy"},
            "Tokyo": {"temp": 72, "condition": "Sunny"},
        }
        data = weather_data.get(location, {"temp": 70, "condition": "Unknown"})
        if unit == "celsius":
            data["temp"] = int((data["temp"] - 32) * 5/9)
        return {
            "location": location,
            "temperature": f"{data['temp']}°{'C' if unit == 'celsius' else 'F'}",
            "condition": data["condition"],
        }
    
    history = MessageHistory()
    history.add_user("What's the weather in San Francisco?")
    
    print("👤 User:")
    print("  What's the weather in San Francisco?")
    print()
    
    print("🤖 Assistant:")
    print()
    
    async with AgentClient(base_url="http://localhost:8000") as client:
        async for event in client.responses.stream(
            history,
            model="gpt-5",
            tools=registry,
            auto_execute=True,  # Auto-execute tools
        ):
            if event["type"] == "text":
                print(f"  {event['delta']}", end="", flush=True)
            
            elif event["type"] == "tool_result":
                # Tool was auto-executed
                print(f"\n  ✓ Tool '{event['name']}' executed: {event['result']}\n  ", end="", flush=True)
            
            elif event["type"] == "complete":
                print("\n")
                history.add_assistant(event)
                print(f"✓ Response completed")
    
    print()


# ============================================================================
# Example 3: Ultra-Simple with Auto Tool Loop
# ============================================================================

async def run_ultra_simple_with_tools() -> None:
    """Demonstrate ultra-simple chat() with automatic tool loop."""
    
    print("=" * 80)
    print("📚 Example 3: Ultra-Simple with Auto Tool Loop")
    print("=" * 80)
    print()
    print("Description: Just call chat() and let it handle everything")
    print()
    
    # Create tool registry
    registry = ToolRegistry()
    registry.register("get_weather", get_weather)
    registry.register("calculate", calculate)
    registry.register("search_articles", search_articles)
    
    history = MessageHistory()
    history.add_user(
        "What's the weather in Tokyo? Also calculate 42 * 137 for me, "
        "and search for articles about AI."
    )
    
    print("👤 User:")
    print("  What's the weather in Tokyo? Also calculate 42 * 137 for me,")
    print("  and search for articles about AI.")
    print()
    
    print("🤖 Processing...")
    print()
    
    async with AgentClient(base_url="http://localhost:8000") as client:
        # Just call chat() - it handles tool execution automatically
        response = await client.responses.chat(
            history,
            model="gpt-5",
            tools=registry,
            auto_execute=True,
            max_turns=100,  # Allow multiple turns for tool execution
        )
        
        print("🤖 Assistant:")
        print(f"  {response['text']}")
        print()
        
        # Add to history
        history.add_assistant(response)
        
        print(f"✓ Response completed")
        if response.get("tool_calls"):
            print(f"  • Tools used: {', '.join(tc['name'] for tc in response['tool_calls'])}")
        print(f"  • Total messages in history: {len(history)}")
    
    print()


# ============================================================================
# Example 4: Custom Tool Executor
# ============================================================================

async def run_custom_tool_executor() -> None:
    """Demonstrate custom tool executor with logging."""
    
    print("=" * 80)
    print("📚 Example 4: Custom Tool Executor")
    print("=" * 80)
    print()
    print("Description: Use a custom function to execute tools with logging")
    print()
    
    # Simple tool dict (no registry)
    TOOLS = [
        {
            "type": "function",
            "tool_type": "server",
            "function": {
                "name": "calculate",
                "description": "Evaluate a mathematical expression",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "Math expression"}
                    },
                    "required": ["expression"],
                },
            },
        }
    ]
    
    # Custom executor with logging
    async def my_executor(name: str, args: Dict[str, Any]) -> Any:
        print(f"    🔧 Executing: {name}({args})")
        if name == "calculate":
            result = calculate(**args)
            print(f"    ✓ Result: {result}")
            return result
        raise ValueError(f"Unknown tool: {name}")
    
    history = MessageHistory()
    history.add_user("Calculate 999 + 1")
    
    print("👤 User:")
    print("  Calculate 999 + 1")
    print()
    
    print("🤖 Assistant:")
    print()
    
    async with AgentClient(base_url="http://localhost:8000") as client:
        async for event in client.responses.stream(
            history,
            model="gpt-5",
            tools=TOOLS,
            auto_execute=True,
            tool_executor=my_executor,  # Custom executor
        ):
            if event["type"] == "text":
                print(f"  {event['delta']}", end="", flush=True)
            
            elif event["type"] == "complete":
                print("\n")
                history.add_assistant(event)
                print(f"✓ Response completed")
    
    print()


# ============================================================================
# Main Runner
# ============================================================================

async def run_all_examples() -> None:
    """Run all function calling examples."""
    
    print("\n")
    print("🌟" * 40)
    print("FUNCTION CALLING EXAMPLES - MANAGED API")
    print("🌟" * 40)
    print("\n")
    
    # Example 1: Manual execution
    await run_manual_tool_execution()
    
    # Example 2: Auto execution (streaming)
    await run_auto_tool_execution_streaming()
    
    # Example 3: Ultra-simple
    await run_ultra_simple_with_tools()
    
    # Example 4: Custom executor
    await run_custom_tool_executor()
    
    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print()
    print("✓ Demonstrated 4 tool execution patterns:")
    print("  1. Manual (Multi-Turn): Full control, manual loop for final response")
    print("  2. Auto (Single-Turn): Auto-execute with stream(), one API call")
    print("  3. Ultra-Simple (Multi-Turn): chat() handles everything automatically")
    print("  4. Custom Executor: Provide your own execution function")
    print()
    print("Key Differences:")
    print("  • stream() = Single API call (manual loop needed for multi-turn)")
    print("  • chat() = Automatic multi-turn loop (simplest for tool conversations)")
    print("  • Manual = Full control over execution timing and error handling")
    print("  • Auto = Convenient, but less control over individual tool execution")
    print()
    print("Key Features:")
    print("  • ToolRegistry: Easy tool registration with decorators")
    print("  • Automatic execution: No manual result handling (when enabled)")
    print("  • Multi-turn loops: chat() continues until no more tools needed")
    print("  • Flexible: Choose your complexity level based on use case")
    print()


if __name__ == "__main__":
    asyncio.run(run_all_examples())

