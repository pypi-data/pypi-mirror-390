"""
Cookbook 03b: Rich Message Format with Message Parts

Demonstrates:
- Proper message part collection
- RichMessage format usage
- Preserving tool calls in conversation
- Multi-part messages (text + tools + thinking)
- Full message structure for advanced use cases
"""

import asyncio
import sys
from typing import List, Dict, Any
from utils import (
    print_header,
    print_section,
    print_message,
    print_tool_call,
    print_success,
    print_info,
    print_warning,
    get_client,
)

sys.path.insert(0, "../..")
from agents.types import RichMessage, ToolDefinition


# Simple mock tool
def get_current_time(timezone: str = "UTC") -> Dict[str, Any]:
    """Get current time in specified timezone."""
    from datetime import datetime
    return {
        "timezone": timezone,
        "time": datetime.now().isoformat(),
        "timestamp": datetime.now().timestamp(),
    }


TOOLS: List[ToolDefinition] = [
    {
        "type": "function",
        "tool_type": "client",
        "function": {
            "name": "get_current_time",
            "description": "Get the current time in a timezone",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "Timezone (e.g., 'UTC', 'America/New_York')",
                        "default": "UTC",
                    },
                },
            },
        },
    },
]


async def run_rich_message_demo() -> None:
    """Demonstrate proper RichMessage format with message parts."""
    
    print_header("Cookbook: Rich Message Format with Message Parts")
    
    print("This cookbook demonstrates how to properly collect and preserve")
    print("message parts (text, tool calls, thinking) in RichMessage format.\n")
    
    # Conversation history using RichMessage format
    conversation: List[RichMessage] = []
    
    # System message
    conversation.append(RichMessage(  # type: ignore
        role="system",
        text="You are a helpful assistant with access to tools. Use tools when appropriate.",
    ))
    
    # User message
    user_query = "What time is it right now?"
    conversation.append(RichMessage(  # type: ignore
        role="user",
        text=user_query,
    ))
    
    print_section("Turn 1: Initial Request with Tools")
    print_message("user", user_query)
    
    async with get_client() as client:
        print_info("Streaming response (collecting all message parts)...")
        print()
        
        # Collect ALL message parts
        message_parts = []
        full_text = ""
        tool_calls_detected = []
        
        try:
            async for event in client.responses.create_stream(
                messages=conversation,  # type: ignore
                model="gpt-4o",
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.7,
            ):
                event_type = event.get("event_type", "")
                data = event.get("data", {})
                
                # CRITICAL: Collect parts as they're added
                if event_type == "message_part.added":
                    part_type = data.get("type")
                    print_info(f"Part added: {part_type} (id: {data.get('id', 'N/A')[:8]}...)")
                    
                    # Store the complete part data
                    message_parts.append(data.copy())
                    
                    # Track tool calls for display
                    if part_type == "tool":
                        import json
                        tool_name = data.get("name", "")
                        tool_args = data.get("arguments", {})
                        if isinstance(tool_args, str):
                            try:
                                tool_args = json.loads(tool_args)
                            except:
                                pass
                        
                        tool_calls_detected.append({
                            "name": tool_name,
                            "args": tool_args,
                        })
                        print_tool_call(tool_name, tool_args)
                
                # Update parts with deltas (text accumulation)
                elif event_type == "message_part.updated":
                    delta = data.get("delta", "")
                    if delta:
                        full_text += delta
                        print(delta, end="", flush=True)
                
                # Mark parts as completed (update with final data)
                elif event_type == "message_part.completed":
                    part_id = data.get("id")
                    print_info(f"Part completed: {part_id[:8] if part_id else 'N/A'}...")
                    
                    # Update the part with final data
                    for part in message_parts:
                        if part.get("id") == part_id:
                            part.update(data)
                            break
                
                elif event_type == "response.completed":
                    print("\n")
                    print_success("Response completed")
            
            # Build RichMessage with ALL parts
            assistant_message: RichMessage = {
                "role": "assistant",
                "parts": message_parts,  # type: ignore - All collected parts
            }
            
            # Optional: add text summary for simple display
            if full_text:
                assistant_message["text"] = full_text
            
            # Add to conversation
            conversation.append(assistant_message)
            
            print_success(f"Message added with {len(message_parts)} parts")
            print(f"  - Text parts: {sum(1 for p in message_parts if p.get('type') == 'text')}")
            print(f"  - Tool parts: {sum(1 for p in message_parts if p.get('type') == 'tool')}")
            print(f"  - Thinking parts: {sum(1 for p in message_parts if p.get('type') == 'thinking')}")
            
        except Exception as e:
            print_warning(f"Error: {e}")
            return
        
        # Show the conversation structure
        print_section("Conversation Structure")
        print(f"Total messages in conversation: {len(conversation)}")
        print()
        
        for i, msg in enumerate(conversation, 1):
            role = msg.get("role", "unknown")
            parts = msg.get("parts", [])
            text = msg.get("text", "")
            
            print(f"{i}. Role: {role}")
            if parts:
                print(f"   Parts: {len(parts)}")
                for j, part in enumerate(parts, 1):
                    part_type = part.get("type", "unknown")
                    part_id = part.get("id", "N/A")
                    print(f"     {j}. Type: {part_type}, ID: {part_id[:8] if part_id else 'N/A'}...")
            if text and not parts:
                print(f"   Text: {text[:50]}...")
            print()
    
    print_section("Key Demonstration Points")
    print_success("Message parts properly collected during streaming")
    print_success("RichMessage format preserves complete structure")
    print_success("Tool calls maintained in conversation history")
    print_success("Parts include: text, tools, thinking, etc.")
    
    print("\n💡 When to use RichMessage format:")
    print("  ✓ Multi-turn conversations with tool calls")
    print("  ✓ Need to preserve full message structure")
    print("  ✓ Reasoning/thinking parts (o-series models)")
    print("  ✓ Complex multi-part responses")
    print("  ✓ Building chat interfaces that show parts separately")
    
    print("\n💡 When SimpleMessage is fine:")
    print("  ✓ Simple text-only conversations")
    print("  ✓ No tools involved")
    print("  ✓ Just need text content")


async def run_multi_part_message_demo() -> None:
    """Show a message with multiple text parts."""
    
    print_header("Multi-Part Message Example")
    
    print("Sometimes messages have multiple parts of the same type.\n")
    
    print_section("Example: Message with Multiple Parts")
    
    async with get_client() as client:
        message_parts = []
        
        async for event in client.responses.create_stream(
            messages=[{"role": "user", "content": "Write 3 short paragraphs about Python."}],
            model="gpt-4o",
            temperature=0.7,
            max_tokens=400,
        ):
            event_type = event.get("event_type", "")
            data = event.get("data", {})
            
            if event_type == "message_part.added":
                message_parts.append(data.copy())
                print_info(f"Part {len(message_parts)} added: {data.get('type')}")
            
            elif event_type == "message_part.updated":
                delta = data.get("delta", "")
                if delta:
                    print(delta, end="", flush=True)
            
            elif event_type == "message_part.completed":
                part_id = data.get("id")
                for part in message_parts:
                    if part.get("id") == part_id:
                        part.update(data)
                        break
        
        print("\n")
        print_success(f"Message has {len(message_parts)} part(s)")
        
        # Show part breakdown
        for i, part in enumerate(message_parts, 1):
            print(f"\nPart {i}:")
            print(f"  Type: {part.get('type')}")
            print(f"  ID: {part.get('id', 'N/A')}")
            if part.get('text'):
                preview = part['text'][:100]
                print(f"  Text: {preview}{'...' if len(part.get('text', '')) > 100 else ''}")


async def main() -> None:
    """Run all RichMessage format demonstrations."""
    await run_rich_message_demo()
    print("\n" + "="*80 + "\n")
    await run_multi_part_message_demo()


if __name__ == "__main__":
    asyncio.run(main())


