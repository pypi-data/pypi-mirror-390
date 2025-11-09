"""
Cookbook 00: API Comparison - Low-Level vs Managed

This cookbook shows the SAME functionality implemented with:
1. Low-Level API (maximum control, more code)
2. Managed API (simple, less code)

Choose the API level that matches your needs!
"""

import asyncio
import sys

sys.path.insert(0, "../..")
from agents import AgentClient, MessageHistory


# ============================================================================
# Task: Get AI response and print it
# ============================================================================

async def task_with_low_level_api() -> None:
    """Implement task using low-level API (create_stream)."""
    
    print("=" * 80)
    print("📚 LOW-LEVEL API (Maximum Control)")
    print("=" * 80)
    print()
    
    messages = [
        {"role": "user", "content": "Tell me a fun fact about Python programming."}
    ]
    
    async with AgentClient(base_url="http://localhost:8000") as client:
        # Manual event handling
        message_parts = []
        current_part_id = None
        full_text = ""
        
        print("👤 User: Tell me a fun fact about Python programming.")
        print()
        print("🤖 Assistant:")
        print("  ", end="", flush=True)
        
        async for event in client.responses.create_stream(
            messages=messages,
            model="gpt-4o",
            temperature=0.7,
            max_tokens=200,
        ):
            event_type = event.get("event_type", "")
            data = event.get("data", {})
            
            # Manually handle each event type
            if event_type == "message_part.added":
                part_type = data.get("type")
                if part_type in ("text", "tool", "thinking"):
                    message_parts.append(data.copy())
                    current_part_id = data.get("id")
            
            elif event_type == "message_part.updated":
                delta = data.get("delta", "")
                if delta:
                    full_text += delta
                    print(delta, end="", flush=True)
            
            elif event_type == "message_part.completed":
                part_id = data.get("id")
                for part in message_parts:
                    if part.get("id") == part_id:
                        part.update(data)
                        break
            
            elif event_type == "response.completed":
                print("\n")
        
        # Manually add to history
        messages.append({"role": "assistant", "content": full_text})
        
        print(f"✓ Response completed ({len(full_text)} chars)")
        print(f"  • Manually handled {len(message_parts)} parts")
        print(f"  • Total messages: {len(messages)}")
    
    print()


async def task_with_managed_api() -> None:
    """Implement SAME task using managed API (stream)."""
    
    print("=" * 80)
    print("📚 MANAGED API (Simple & Easy)")
    print("=" * 80)
    print()
    
    history = MessageHistory()
    history.add_user("Tell me a fun fact about Python programming.")
    
    async with AgentClient(base_url="http://localhost:8000") as client:
        print("👤 User: Tell me a fun fact about Python programming.")
        print()
        print("🤖 Assistant:")
        print("  ", end="", flush=True)
        
        # Simple event handling - just handle what you care about
        async for event in client.responses.stream(
            history,
            model="gpt-4o",
            temperature=0.7,
            max_tokens=200,
        ):
            if event["type"] == "text":
                print(event["delta"], end="", flush=True)
            elif event["type"] == "complete":
                print("\n")
                history.add_assistant(event)
        
        print(f"✓ Response completed ({len(history.get_last_assistant_message() or '')} chars)")
        print(f"  • Automatically managed parts")
        print(f"  • Total messages: {len(history)}")
    
    print()


async def task_with_ultra_simple_api() -> None:
    """Implement SAME task using ultra-simple API (chat)."""
    
    print("=" * 80)
    print("📚 ULTRA-SIMPLE API (Just Get the Answer)")
    print("=" * 80)
    print()
    
    history = MessageHistory()
    history.add_user("Tell me a fun fact about Python programming.")
    
    async with AgentClient(base_url="http://localhost:8000") as client:
        print("👤 User: Tell me a fun fact about Python programming.")
        print()
        
        # Just get the response (blocks until complete)
        response = await client.responses.chat(
            history,
            model="gpt-4o",
            temperature=0.7,
            max_tokens=200,
        )
        
        print("🤖 Assistant:")
        print(f"  {response['text']}")
        print()
        
        history.add_assistant(response)
        
        print(f"✓ Response completed ({len(response['text'])} chars)")
        print(f"  • No streaming - just the answer")
        print(f"  • Total messages: {len(history)}")
    
    print()


# ============================================================================
# Code Comparison Summary
# ============================================================================

def show_code_comparison() -> None:
    """Show side-by-side code comparison."""
    
    print("=" * 80)
    print("📊 Code Comparison Summary")
    print("=" * 80)
    print()
    
    print("LOW-LEVEL API (Expert - Maximum Control):")
    print("-" * 80)
    print("""
    # Manual event handling, part collection, text accumulation
    message_parts = []
    full_text = ""
    
    async for event in client.responses.create_stream(messages, model="gpt-4o"):
        event_type = event.get("event_type", "")
        data = event.get("data", {})
        
        if event_type == "message_part.added":
            message_parts.append(data.copy())
        elif event_type == "message_part.updated":
            full_text += data.get("delta", "")
            print(data.get("delta", ""), end="")
        elif event_type == "message_part.completed":
            # Update part with final data...
        # ... more event handling ...
    
    messages.append({"role": "assistant", "content": full_text})
    
    Lines of code: ~25-30
    Complexity: High
    Control: Maximum
    """)
    
    print()
    print("MANAGED API (Recommended - Balance):")
    print("-" * 80)
    print("""
    # Automatic part management, simple events
    history = MessageHistory()
    history.add_user("Hello!")
    
    async for event in client.responses.stream(history, model="gpt-4o"):
        if event["type"] == "text":
            print(event["delta"], end="")
        elif event["type"] == "complete":
            history.add_assistant(event)
    
    Lines of code: ~8-10
    Complexity: Low
    Control: Good
    """)
    
    print()
    print("ULTRA-SIMPLE API (Beginner - Just Works):")
    print("-" * 80)
    print("""
    # Just get the answer
    history = MessageHistory()
    history.add_user("Hello!")
    
    response = await client.responses.chat(history, model="gpt-4o")
    print(response["text"])
    history.add_assistant(response)
    
    Lines of code: ~5
    Complexity: Minimal
    Control: Basic
    """)
    
    print()


# ============================================================================
# Feature Comparison
# ============================================================================

def show_feature_comparison() -> None:
    """Show feature comparison table."""
    
    print("=" * 80)
    print("📋 Feature Comparison")
    print("=" * 80)
    print()
    
    features = [
        ("Feature", "Low-Level", "Managed", "Ultra-Simple"),
        ("-" * 20, "-" * 15, "-" * 15, "-" * 15),
        ("Streaming", "✓ Full control", "✓ Simplified", "✗ Blocking"),
        ("Text parts", "Manual", "Automatic", "Automatic"),
        ("Thinking parts", "Manual", "Automatic", "Automatic"),
        ("Tool handling", "Manual", "Auto/Manual", "Automatic"),
        ("History mgmt", "Manual", "Built-in", "Built-in"),
        ("Error handling", "Manual", "Built-in", "Built-in"),
        ("Multi-turn tools", "Manual", "Manual", "Automatic"),
        ("Lines of code", "25-30+", "8-15", "5-8"),
        ("Learning curve", "Steep", "Gentle", "Minimal"),
        ("Flexibility", "Maximum", "High", "Basic"),
    ]
    
    # Print table
    for row in features:
        print(f"{row[0]:20} | {row[1]:15} | {row[2]:15} | {row[3]:15}")
    
    print()


# ============================================================================
# When to Use Each API
# ============================================================================

def show_recommendations() -> None:
    """Show recommendations for when to use each API."""
    
    print("=" * 80)
    print("💡 Recommendations: When to Use Each API")
    print("=" * 80)
    print()
    
    print("Use LOW-LEVEL API when:")
    print("  • You need maximum control over every event")
    print("  • You're building custom streaming UIs")
    print("  • You need to handle events in specific ways")
    print("  • You're debugging or learning the system internals")
    print()
    
    print("Use MANAGED API when:")
    print("  • You want streaming with simplified events (RECOMMENDED)")
    print("  • You need to show different content types (text, thinking)")
    print("  • You want to control tool execution")
    print("  • You're building interactive chat applications")
    print()
    
    print("Use ULTRA-SIMPLE API when:")
    print("  • You just need the final answer")
    print("  • Streaming isn't important")
    print("  • You want tools to execute automatically")
    print("  • You're building simple request/response flows")
    print()


# ============================================================================
# Main Runner
# ============================================================================

async def run_comparison() -> None:
    """Run all comparison examples."""
    
    print("\n")
    print("🌟" * 40)
    print("API COMPARISON: LOW-LEVEL vs MANAGED vs ULTRA-SIMPLE")
    print("🌟" * 40)
    print("\n")
    
    # Show same task with different APIs
    await task_with_low_level_api()
    await task_with_managed_api()
    await task_with_ultra_simple_api()
    
    # Show comparisons
    show_code_comparison()
    show_feature_comparison()
    show_recommendations()
    
    # Final summary
    print("=" * 80)
    print("✨ Summary")
    print("=" * 80)
    print()
    print("The SDK provides 3 API levels for different use cases:")
    print()
    print("  1️⃣  Ultra-Simple: chat() - Just get answers")
    print("  2️⃣  Managed: stream() - Streaming with simple events")
    print("  3️⃣  Low-Level: create_stream() - Maximum control")
    print()
    print("All APIs are available - choose what works for you!")
    print("Start with Managed API and move up/down as needed.")
    print()


if __name__ == "__main__":
    asyncio.run(run_comparison())

