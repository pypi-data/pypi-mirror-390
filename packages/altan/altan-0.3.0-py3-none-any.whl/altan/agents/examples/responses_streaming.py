"""
Streaming example using the Responses API with SSE.
"""

import asyncio
from python_sdk import AgentClient, ResponseMessage


async def main():
    """Streaming response example."""
    
    # Initialize client
    async with AgentClient(base_url="http://localhost:8000") as client:
        
        # Example 1: Basic streaming
        print("=== Example 1: Basic streaming ===")
        print("Streaming response...\n")
        
        async for event in client.responses.create_stream(
            messages=[
                {"role": "user", "content": "Write a short poem about coding"}
            ],
            model="gpt-4o",
            temperature=0.9,
            member_id="user_123",
        ):
            if event.data:
                event_type = event.data.get('type')
                
                if event_type == 'stream.ready':
                    print("🔄 Stream ready")
                
                elif event_type == 'response.submitted':
                    print("📤 Response submitted")
                    print(f"Response ID: {event.data.get('data', {}).get('response_id')}\n")
                
                elif event_type == 'message_part.created':
                    print("✨ Message part created")
                
                elif event_type == 'message_part.updated':
                    # Print text as it streams
                    text = event.data.get('data', {}).get('text', '')
                    if text:
                        print(text, end='', flush=True)
                
                elif event_type == 'message_part.completed':
                    print("\n\n✅ Message part completed")
                
                elif event_type == 'response.stream_complete':
                    print("🏁 Stream complete\n")
        
        # Example 2: Streaming with tools
        print("\n=== Example 2: Streaming with tool calls ===")
        
        async for event in client.responses.create_stream(
            messages=[
                {"role": "user", "content": "Search for information about Python 3.12"}
            ],
            model="gpt-4o",
            tools=[
                {
                    "type": "function",
                    "tool_type": "client",
                    "function": {
                        "name": "web_search",
                        "description": "Search the web for information",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Search query"
                                }
                            },
                            "required": ["query"]
                        }
                    }
                }
            ],
            member_id="user_123",
        ):
            if event.data:
                event_type = event.data.get('type')
                
                if event_type == 'tool.call':
                    tool_data = event.data.get('data', {})
                    print(f"\n🔧 Tool call: {tool_data.get('name')}")
                    print(f"   Input: {tool_data.get('input')}")
                
                elif event_type == 'tool.result':
                    tool_data = event.data.get('data', {})
                    print(f"✅ Tool result: {tool_data.get('result')[:100]}...")
                
                elif event_type == 'message_part.updated':
                    text = event.data.get('data', {}).get('text', '')
                    if text:
                        print(text, end='', flush=True)
        
        # Example 3: Reasoning model (o-series)
        print("\n\n=== Example 3: Reasoning model ===")
        
        async for event in client.responses.create_stream(
            messages=[
                {
                    "role": "user",
                    "content": "Solve this math problem: If x^2 + 5x + 6 = 0, what are the values of x?"
                }
            ],
            model="o3-mini",
            reasoning={"effort": "high"},
            reasoning_effort="high",
            reasoning_tokens=5000,
            member_id="user_123",
        ):
            if event.data:
                event_type = event.data.get('type')
                
                if event_type == 'thinking.started':
                    print("🤔 Model is thinking...")
                
                elif event_type == 'thinking.updated':
                    thinking_text = event.data.get('data', {}).get('text', '')
                    if thinking_text:
                        print(f"   Thinking: {thinking_text[:80]}...")
                
                elif event_type == 'message_part.updated':
                    text = event.data.get('data', {}).get('text', '')
                    if text:
                        print(text, end='', flush=True)
                
                elif event_type == 'response.stream_complete':
                    print("\n\n✅ Reasoning complete")
        
        print("\n✅ All streaming examples completed!")


if __name__ == "__main__":
    asyncio.run(main())

