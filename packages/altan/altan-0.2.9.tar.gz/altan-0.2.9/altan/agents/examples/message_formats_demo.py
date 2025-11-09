"""
Message Formats Demo

Demonstrates the flexible message input formats supported by the Agent Evolution SDK:
1. Simple Format (OpenAI/Anthropic style)
2. Rich Format (Domain-style with message parts)
3. Mixed Formats (combining both in the same request)
"""

import asyncio
from agents import AgentClient
from agents.types import SimpleMessage, RichMessage, TextPartInput


async def simple_format_example():
    """Example using simple OpenAI/Anthropic message format."""
    print("\n=== Simple Format Example ===")
    
    client = AgentClient(
        api_url="http://localhost:8000",
        api_key="your-api-key"
    )
    
    # Simple messages with just role and content
    simple_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Python?"},
        {"role": "assistant", "content": "Python is a high-level programming language."},
        {"role": "user", "content": "Tell me more!"}
    ]
    
    response = await client.responses.create(
        messages=simple_messages,
        model="gpt-4o",
        temperature=0.7
    )
    
    print(f"Response ID: {response['response_id']}")
    print(f"Status: {response['status']}")


async def rich_format_example():
    """Example using rich domain-style message format with parts."""
    print("\n=== Rich Format Example ===")
    
    client = AgentClient(
        api_url="http://localhost:8000",
        api_key="your-api-key"
    )
    
    # Rich message with explicit parts and metadata
    rich_messages: list[RichMessage] = [
        {
            "role": "user",
            "member_id": "user-123",  # Optional: specify member ID
            "text": "Hello, assistant!",  # Optional: text summary
            "parts": [
                {
                    "type": "text",
                    "text": "Hello, assistant!",
                    "order": 0,
                    "block_order": 0
                }
            ],
            "meta_data": {
                "source": "web_client",
                "session_id": "abc-123"
            }
        },
        {
            "role": "assistant",
            "parts": [
                {
                    "type": "thinking",
                    "text": "The user is greeting me. I should respond warmly.",
                    "status": "completed",
                    "order": 0
                },
                {
                    "type": "text",
                    "text": "Hello! How can I help you today?",
                    "order": 1
                }
            ],
            "tokens": 50,
            "cost": 0.001
        }
    ]
    
    response = await client.responses.create(
        messages=rich_messages,
        model="gpt-4o",
        temperature=0.7
    )
    
    print(f"Response ID: {response['response_id']}")
    print(f"Status: {response['status']}")


async def mixed_format_example():
    """Example mixing simple and rich formats in the same request."""
    print("\n=== Mixed Format Example ===")
    
    client = AgentClient(
        api_url="http://localhost:8000",
        api_key="your-api-key"
    )
    
    # Mix simple and rich messages
    mixed_messages = [
        # Simple message
        {"role": "system", "content": "You are a helpful assistant."},
        
        # Simple message
        {"role": "user", "content": "What is the weather?"},
        
        # Rich message with tool call
        {
            "role": "assistant",
            "parts": [
                {
                    "type": "text",
                    "text": "Let me check the weather for you.",
                    "order": 0
                },
                {
                    "type": "tool",
                    "name": "get_weather",
                    "tool_call_id": "call_123",
                    "arguments": {"location": "San Francisco"},
                    "result": {"temperature": 72, "condition": "Sunny"},
                    "order": 1
                }
            ]
        },
        
        # Simple message
        {"role": "user", "content": "Great, thanks!"}
    ]
    
    response = await client.responses.create(
        messages=mixed_messages,
        model="gpt-4o",
        temperature=0.7
    )
    
    print(f"Response ID: {response['response_id']}")


async def auto_id_generation_example():
    """Example showing auto-generated IDs and ordering."""
    print("\n=== Auto ID Generation Example ===")
    
    client = AgentClient(
        api_url="http://localhost:8000",
        api_key="your-api-key"
    )
    
    # Rich message without IDs or explicit ordering
    # IDs and order will be auto-generated on the server
    messages: list[RichMessage] = [
        {
            "role": "user",
            "parts": [
                # No id, order, or block_order specified - will be auto-assigned
                {"type": "text", "text": "First part"},
                {"type": "text", "text": "Second part"},
                {"type": "text", "text": "Third part"}
            ]
        }
    ]
    
    response = await client.responses.create(
        messages=messages,
        model="gpt-4o"
    )
    
    print(f"Response ID: {response['response_id']}")
    print("Note: Message and part IDs were auto-generated server-side")


async def streaming_with_rich_format():
    """Example using rich format with streaming."""
    print("\n=== Streaming with Rich Format Example ===")
    
    client = AgentClient(
        api_url="http://localhost:8000",
        api_key="your-api-key"
    )
    
    messages: list[RichMessage] = [
        {
            "role": "user",
            "parts": [
                {
                    "type": "text",
                    "text": "Tell me a story about a dragon."
                }
            ],
            "member_id": "user-456",
            "meta_data": {"context": "storytelling"}
        }
    ]
    
    async for event in client.responses.create_stream(
        messages=messages,
        model="gpt-4o",
        temperature=0.9
    ):
        if event.get("data"):
            event_type = event["data"].get("type")
            print(f"Event: {event_type}")
            
            if event_type == "message_part.updated":
                content = event["data"].get("data", {}).get("text", "")
                if content:
                    print(f"Content: {content}")


async def main():
    """Run all examples."""
    print("Agent Evolution SDK - Message Formats Demo")
    print("=" * 50)
    
    try:
        # Simple format (most common)
        await simple_format_example()
        
        # Rich format (advanced use cases)
        await rich_format_example()
        
        # Mixed formats
        await mixed_format_example()
        
        # Auto ID generation
        await auto_id_generation_example()
        
        # Streaming with rich format
        await streaming_with_rich_format()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

