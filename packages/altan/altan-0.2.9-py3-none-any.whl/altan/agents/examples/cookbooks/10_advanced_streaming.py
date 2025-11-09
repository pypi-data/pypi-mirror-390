"""
Cookbook 10: Advanced Streaming Patterns

Demonstrates:
- Real-time event-by-event processing
- All 16 StreamEvent types
- Token-by-token display
- Event-specific handling
- Streaming UX patterns
"""

import asyncio
import sys
from typing import Dict, Any
from collections import defaultdict
from utils import (
    print_header,
    print_section,
    print_message,
    print_event,
    print_success,
    print_info,
    print_divider,
    get_client,
)

sys.path.insert(0, "../..")
from agents.types import (
    StreamEvent,
    MessagePartAddedEvent,
    MessagePartUpdatedEvent,
    MessagePartDoneEvent,
    ResponseStartedEvent,
    ResponseCompletedEvent,
)


async def run_comprehensive_event_tracking() -> None:
    """Demonstrate comprehensive tracking of all streaming events."""
    
    print_header("Cookbook: Advanced Streaming - Event Type Coverage")
    
    print("This cookbook demonstrates handling all 16 possible StreamEvent types.")
    print("We'll track every event that occurs during a streaming response.\n")
    
    # Event counters
    event_counts: Dict[str, int] = defaultdict(int)
    event_timeline: list = []
    
    # Message parts
    text_parts = []
    tool_parts = []
    thinking_parts = []
    
    # Accumulated text
    accumulated_text = ""
    
    print_section("Starting Streaming Request")
    
    prompt = "Write a haiku about artificial intelligence, then explain why haikus are exactly 17 syllables."
    print_message("user", prompt)
    
    print_info("Watching for all event types...")
    print_divider()
    
    start_time = asyncio.get_event_loop().time()
    
    async with get_client() as client:
        async for event in client.responses.create_stream(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4o",
            temperature=0.7,
            max_tokens=500,
        ):
            event_type = event.get("event_type", "unknown")
            event_data = event.get("data", {})
            
            # Track event
            event_counts[event_type] += 1
            event_timeline.append({
                "type": event_type,
                "timestamp": asyncio.get_event_loop().time() - start_time,
                "data": event_data,
            })
            
            # Type-specific handling
            if event_type == "response.started":
                print_event(event_type, event_data)
                print_info(f"Response ID: {event_data.get('response_id', 'N/A')}")
            
            elif event_type == "message_part.added":
                part_type = event_data.get("type", "unknown")
                part_id = event_data.get("id", "N/A")
                print_event(event_type, {"type": part_type, "id": part_id})
                
                if part_type == "text":
                    text_parts.append(event_data)
                elif part_type == "tool":
                    tool_parts.append(event_data)
                elif part_type == "thinking":
                    thinking_parts.append(event_data)
            
            elif event_type == "message_part.updated":
                delta = event_data.get("delta", "")
                if delta:
                    accumulated_text += delta
                    # Show delta inline without repeating event line
                    print(f"  📝 +\"{delta.replace(chr(10), '\\n')[:50]}{'...' if len(delta) > 50 else ''}\"")
            
            elif event_type == "message_part.completed":
                part_type = event_data.get("type", "unknown")
                part_id = event_data.get("id", "N/A")
                print_event(event_type, {"type": part_type, "id": part_id})
            
            elif event_type == "response.completed":
                print_event(event_type)
                usage = event_data.get("usage", [])
                if usage:
                    print_info(f"Token usage: {usage}")
            
            elif event_type == "response.failed":
                print_event(event_type, event_data)
                error = event_data.get("error_message", "Unknown error")
                print(f"  ❌ Error: {error}")
            
            elif event_type == "response.fallback":
                print_event(event_type, event_data)
                print_info(
                    f"Fallback: {event_data.get('from_model')} → {event_data.get('to_model')}"
                )
            
            elif event_type == "response.retry":
                print_event(event_type, event_data)
                retry_count = event_data.get("retry_count", 0)
                print_info(f"Retry attempt #{retry_count}")
            
            else:
                # Handle any other event types
                print_event(event_type, event_data)
    
    duration = asyncio.get_event_loop().time() - start_time
    
    # Display results
    print_divider()
    print_section("Final Response")
    if accumulated_text:
        print(accumulated_text)
        print()
    
    print_section("Event Analytics")
    
    print("\n📊 Event Type Frequency:")
    for event_type, count in sorted(event_counts.items(), key=lambda x: -x[1]):
        print(f"  {event_type:30} : {count:3} times")
    
    print("\n📦 Message Parts:")
    print(f"  Text parts: {len(text_parts)}")
    print(f"  Tool parts: {len(tool_parts)}")
    print(f"  Thinking parts: {len(thinking_parts)}")
    
    print("\n⏱️  Timing:")
    print(f"  Total duration: {duration:.2f}s")
    print(f"  Total events: {sum(event_counts.values())}")
    print(f"  Events/second: {sum(event_counts.values())/duration:.1f}")
    
    print("\n📈 Event Timeline:")
    for i, entry in enumerate(event_timeline[:10], 1):
        print(f"  {i}. [{entry['timestamp']:.3f}s] {entry['type']}")
    if len(event_timeline) > 10:
        print(f"  ... and {len(event_timeline) - 10} more events")
    
    print_success("Comprehensive event tracking completed")


async def run_realtime_typing_indicator() -> None:
    """Demonstrate real-time typing indicator pattern."""
    
    print_header("Cookbook: Real-Time Typing Indicator")
    
    print("This pattern simulates a chat interface with typing indicators.\n")
    
    print_section("Conversation with Typing Indicators")
    
    questions = [
        "What is machine learning?",
        "Can you give me a simple example?",
        "Thanks!",
    ]
    
    async with get_client() as client:
        for i, question in enumerate(questions, 1):
            print_message("user", question)
            
            print("🤖 Assistant: ", end="", flush=True)
            print("⌨️  typing", end="", flush=True)
            
            full_text = ""
            is_first_token = True
            
            async for event in client.responses.create_stream(
                messages=[{"role": "user", "content": question}],
                model="gpt-4o",
                temperature=0.7,
                max_tokens=200,
            ):
                event_type = event.get("event_type", "")
                data = event.get("data", {})
                
                if event_type == "message_part.updated":
                    delta = data.get("delta", "")
                    if delta:
                        if is_first_token:
                            # Clear typing indicator
                            print("\r🤖 Assistant: ", end="", flush=True)
                            is_first_token = False
                        
                        full_text += delta
                        print(delta, end="", flush=True)
            
            print("\n")
            
            if i < len(questions):
                # Simulate user reading/thinking
                await asyncio.sleep(0.5)
    
    print_success("Typing indicator pattern demonstrated")


async def run_partial_response_rendering() -> None:
    """Demonstrate rendering partial responses as they arrive."""
    
    print_header("Cookbook: Partial Response Rendering")
    
    print("This pattern shows how to render structured content as it streams.\n")
    
    print_section("Streaming Structured Content")
    
    prompt = "List 5 programming languages and briefly explain each one."
    print_message("user", prompt)
    
    print("🤖 Assistant:\n")
    
    # Track when we're in a list item
    current_buffer = ""
    item_count = 0
    
    async with get_client() as client:
        async for event in client.responses.create_stream(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4o",
            temperature=0.7,
            max_tokens=600,
        ):
            event_type = event.get("event_type", "")
            data = event.get("data", {})
            
            if event_type == "message_part.updated":
                delta = data.get("delta", "")
                if delta:
                    current_buffer += delta
                    
                    # Check if we completed a list item (simple heuristic)
                    if "\n" in delta and current_buffer.strip():
                        # Flush the current item
                        lines = current_buffer.split("\n")
                        for line in lines[:-1]:
                            if line.strip():
                                item_count += 1
                                print(f"  ✓ Item {item_count}: {line.strip()}")
                        current_buffer = lines[-1]
                    else:
                        # Show streaming progress
                        print(".", end="", flush=True)
            
            elif event_type == "response.completed":
                # Flush any remaining content
                if current_buffer.strip():
                    item_count += 1
                    print(f"\n  ✓ Item {item_count}: {current_buffer.strip()}")
                print()
    
    print_success(f"Rendered {item_count} items with progressive display")


async def main() -> None:
    """Run all advanced streaming demonstrations."""
    await run_comprehensive_event_tracking()
    print("\n" + "="*80 + "\n")
    await run_realtime_typing_indicator()
    print("\n" + "="*80 + "\n")
    await run_partial_response_rendering()


if __name__ == "__main__":
    asyncio.run(main())

