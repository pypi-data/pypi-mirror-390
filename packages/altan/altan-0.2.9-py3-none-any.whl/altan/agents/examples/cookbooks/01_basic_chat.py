"""
Cookbook 01: Basic Multi-Turn Chat

Demonstrates:
- Simple conversational AI
- Multi-turn conversation with context retention
- Personality consistency
- Streaming responses with live updates
"""

import asyncio
import sys
from typing import Dict, Any
from utils import (
    print_header,
    print_section,
    print_message,
    print_event,
    print_success,
    print_error,
    print_warning,
    print_info,
    print_stream_stats,
    get_client,
    MessageHistory,
)

sys.path.insert(0, "../../../..")
from altan.agents.agents.types import StreamEvent


async def run_basic_chat() -> None:
    """Run a multi-turn conversation demonstrating basic chat functionality."""
    
    print_header("Cookbook: Basic Multi-Turn Chat")
    
    print("This cookbook demonstrates a natural conversation with context retention.")
    print("The assistant maintains context across multiple turns.\n")
    
    # Conversation turns
    conversation = [
        "Hi! My name is Sarah and I'm learning about AI.",
        "What are the three main types of machine learning?",
        "Can you explain supervised learning in simple terms?",
        "Great! Now, can you remind me what my name is?",
        "Thanks! Can you give me an example of supervised learning in real life?",
    ]
    
    # Initialize history
    history = MessageHistory()
    history.add_system_message(
        "You are a friendly AI tutor. Be concise but informative. "
        "Remember details about the user."
    )
    
    async with get_client() as client:
        for i, user_input in enumerate(conversation, 1):
            print_section(f"Turn {i}/{len(conversation)}")
            
            # Add user message and display
            history.add_user_message(user_input)
            print_message("user", user_input)
            
            # Stream the response
            print("🤖 Assistant:")
            print("  ", end="", flush=True)
            
            # Collect message parts
            message_parts = []
            current_part_id = None
            full_text = ""
            event_count = 0
            start_time = asyncio.get_event_loop().time()
            
            try:
                async for event in client.responses.create_stream(
                    messages=history.get_messages(),
                    model="gpt-4o",
                    temperature=0.7,
                    max_tokens=300,
                ):
                    event_count += 1
                    
                    event_type = event.get("event_type", "")
                    data = event.get("data", {})
                    
                    # Collect message parts as they're added
                    if event_type == "message_part.added":
                        part_type = data.get("type")
                        if part_type in ("text", "tool", "thinking"):
                            message_parts.append(data.copy())
                            current_part_id = data.get("id")
                    
                    # Update parts with deltas
                    elif event_type == "message_part.updated":
                        delta = data.get("delta", "")
                        if delta:
                            full_text += delta
                            print(delta, end="", flush=True)
                    
                    # Mark parts as complete
                    elif event_type == "message_part.completed":
                        # Update the part with final data
                        part_id = data.get("id")
                        for part in message_parts:
                            if part.get("id") == part_id:
                                part.update(data)
                                break
                    
                    elif event_type == "response.completed":
                        print("\n")
                        duration = asyncio.get_event_loop().time() - start_time
                        print_success(f"Response completed in {duration:.2f}s ({len(full_text)} chars, {len(message_parts)} parts)")
                    
                    elif event_type == "response.failed":
                        print("\n")
                        error_msg = data.get("error_message", "Unknown error")
                        print_error(f"Response failed: {error_msg}")
                        return
                
                # Add complete assistant message to history
                if full_text.strip() or message_parts:
                    # Option 1: Simple format (what we're using here for basic chat)
                    history.add_assistant_message(full_text)
                    
                    # Option 2: Rich format with parts (uncomment to use)
                    # Preserves tool calls, thinking, and other structured data
                    # history.add_rich_assistant_message(message_parts, full_text)
                    
                    print_info(f"Added to history (total messages: {len(history.get_messages())})")
                else:
                    print_warning("No response text received")
                
            except KeyboardInterrupt:
                print("\n")
                print_warning("Stream interrupted by user")
                return
            except Exception as e:
                print("\n")
                print_error(f"Unexpected error: {e}")
                import traceback
                traceback.print_exc()
                return
    
    print_section("Conversation Summary")
    print_success(f"Completed {len(conversation)} turns successfully")
    print_success(f"Total messages in history: {len(history.get_messages())}")
    print("\nKey demonstration points:")
    print("  ✓ Context retention (remembered user's name)")
    print("  ✓ Multi-turn coherence")
    print("  ✓ Streaming with live token display")
    print("  ✓ Message history management")


if __name__ == "__main__":
    asyncio.run(run_basic_chat())

