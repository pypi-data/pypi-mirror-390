"""
Cookbook 01: Basic Multi-Turn Chat (Managed API)

Demonstrates:
- Ultra-simple chat with automatic history management
- Streaming with simplified events
- MessageHistory integration
- Progressive complexity levels

This shows the NEW managed API that makes it extremely easy to use.
"""

import asyncio
import sys

sys.path.insert(0, "../..")
from agents import AgentClient, MessageHistory


async def run_ultra_simple_chat() -> None:
    """Simplest possible chat example."""
    
    print("=" * 80)
    print("📚 Ultra-Simple Chat (Blocking API)")
    print("=" * 80)
    print()
    
    history = MessageHistory()
    history.add_system("You are a friendly AI tutor. Be concise but informative.")
    history.add_user("Hi! My name is Sarah and I'm learning about AI.")
    
    async with AgentClient(base_url="http://localhost:8000") as client:
        print("👤 User:")
        print("  Hi! My name is Sarah and I'm learning about AI.")
        print()
        
        # Ultra-simple: just get the response
        response = await client.responses.chat(
            history,
            model="gpt-4o",
            temperature=0.7,
            max_tokens=300,
        )
        
        print("🤖 Assistant:")
        print(f"  {response['text']}")
        print()
        
        # Add to history
        history.add_assistant(response)
        
        print(f"✓ Response received ({len(response['text'])} chars)")
        print(f"✓ Total messages in history: {len(history)}")
        print()


async def run_simple_streaming_chat() -> None:
    """Simple streaming chat with print-as-you-go."""
    
    print("=" * 80)
    print("📚 Simple Streaming Chat")
    print("=" * 80)
    print()
    
    history = MessageHistory()
    history.add_system("You are a friendly AI tutor. Be concise but informative.")
    
    conversation = [
        "Hi! My name is Sarah and I'm learning about AI.",
        "What are the three main types of machine learning?",
        "Can you explain supervised learning in simple terms?",
    ]
    
    async with AgentClient(base_url="http://localhost:8000") as client:
        for i, user_input in enumerate(conversation, 1):
            print(f"─" * 80)
            print(f"Turn {i}/{len(conversation)}")
            print(f"─" * 80)
            print()
            
            history.add_user(user_input)
            print(f"👤 User:")
            print(f"  {user_input}")
            print()
            
            print("🤖 Assistant:")
            print("  ", end="", flush=True)
            
            # Stream and print deltas
            async for event in client.responses.stream(
                history,
                model="gpt-4o",
                temperature=0.7,
                max_tokens=300,
            ):
                if event["type"] == "text":
                    # Just print the text delta
                    print(event["delta"], end="", flush=True)
                
                elif event["type"] == "complete":
                    # Response done, add to history
                    print("\n")
                    history.add_assistant(event)
                    print(f"✓ Response completed ({len(event['text'])} chars)")
            
            print()


async def run_moderate_complexity_chat() -> None:
    """Chat with more control over what you see."""
    
    print("=" * 80)
    print("📚 Moderate Complexity Chat (with Reasoning)")
    print("=" * 80)
    print()
    
    history = MessageHistory()
    history.add_system("You are a helpful AI assistant that thinks step by step.")
    history.add_user("What is the capital of France and why was it chosen?")
    
    print("👤 User:")
    print("  What is the capital of France and why was it chosen?")
    print()
    
    print("🤖 Assistant:")
    
    async with AgentClient(base_url="http://localhost:8000") as client:
        async for event in client.responses.stream(
            history,
            model="claude-sonnet-4-latest",
            reasoning=True,
            reasoning_effort="medium",
            max_tokens=2000,
        ):
            # Handle different event types
            if event["type"] == "thinking":
                # Show thinking in dimmed color
                print(f"\033[2m{event['delta']}\033[0m", end="", flush=True)
            
            elif event["type"] == "text":
                # Show text normally
                print(event["delta"], end="", flush=True)
            
            elif event["type"] == "started":
                print(f"  [Response started: {event['response_id'][:8]}...]")
                print()
            
            elif event["type"] == "complete":
                print("\n")
                history.add_assistant(event)
                
                print(f"✓ Response completed")
                if event.get("thinking"):
                    print(f"  • Thinking: {len(event['thinking'])} chars")
                if event.get("text"):
                    print(f"  • Text: {len(event['text'])} chars")
                if event.get("models_used"):
                    print(f"  • Models: {', '.join(event['models_used'])}")
            
            elif event["type"] == "error":
                print(f"\n❌ Error: {event['error_message']}")
    
    print()


async def run_all_examples() -> None:
    """Run all chat examples."""
    
    print("\n")
    print("🌟" * 40)
    print("BASIC CHAT EXAMPLES - MANAGED API")
    print("🌟" * 40)
    print("\n")
    
    # Ultra-simple (blocking)
    await run_ultra_simple_chat()
    
    # Simple streaming
    await run_simple_streaming_chat()
    
    # Moderate complexity
    await run_moderate_complexity_chat()
    
    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print()
    print("✓ Demonstrated 3 complexity levels:")
    print("  1. Ultra-simple: chat() for blocking responses")
    print("  2. Simple: stream() for live text streaming")
    print("  3. Moderate: Handle different event types (text, thinking)")
    print()
    print("Key Benefits:")
    print("  • No manual event handling or text accumulation")
    print("  • MessageHistory manages conversation state")
    print("  • Progressive complexity - use what you need")
    print("  • Backward compatible - low-level API still available")
    print()


if __name__ == "__main__":
    asyncio.run(run_all_examples())

