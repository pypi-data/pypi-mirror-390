"""
Streaming examples using the Activations API with SSE.
"""

import asyncio
from python_sdk import AgentClient


async def main():
    """Activations streaming examples."""
    
    async with AgentClient(base_url="http://localhost:8000") as client:
        
        # Example 1: Submit activation with streaming
        print("=== Example 1: Submit with streaming ===")
        
        async for event in client.activations.submit_stream(
            agent_id="agent_123",
            thread_id="thread_456",
            room_id="room_789",
            session_id="session_abc",
        ):
            if event.data:
                event_type = event.data.get('type')
                
                if event_type == 'stream.ready':
                    print("🔄 Stream ready")
                
                elif event_type == 'activation.submitted':
                    data = event.data.get('data', {})
                    print(f"📤 Activation submitted")
                    print(f"   Response ID: {data.get('response_id')}")
                
                elif event_type == 'activation.processing':
                    print("⚙️  Processing activation...")
                
                elif event_type == 'message_part.created':
                    print("✨ Message part created")
                
                elif event_type == 'message_part.updated':
                    text = event.data.get('data', {}).get('text', '')
                    if text:
                        print(text, end='', flush=True)
                
                elif event_type == 'message_part.completed':
                    print("\n✅ Message part completed")
                
                elif event_type == 'activation.completed':
                    print("🏁 Activation completed")
                
                elif event_type == 'stream.complete':
                    print("✅ Stream complete\n")
        
        # Example 2: Retry with streaming
        print("\n=== Example 2: Retry with streaming ===")
        
        async for event in client.activations.retry_stream(
            agent_id="agent_123",
            thread_id="thread_456",
            override_message_id="msg_abc",
            room_id="room_789",
        ):
            if event.data:
                event_type = event.data.get('type')
                
                if event_type == 'stream.ready':
                    print("🔄 Retry stream ready")
                
                elif event_type == 'message_part.updated':
                    text = event.data.get('data', {}).get('text', '')
                    if text:
                        print(text, end='', flush=True)
                
                elif event_type == 'stream.complete':
                    print("\n✅ Retry complete\n")
        
        # Example 3: Generic event stream with filters
        print("\n=== Example 3: Filtered event stream ===")
        
        event_count = 0
        async for event in client.activations.create_event_stream(
            agent_ids=["agent_123"],
            event_types=["activation.submitted", "activation.completed"],
            channels=["activations"],
        ):
            event_count += 1
            if event.data:
                print(f"Event #{event_count}: {event.data.get('type')}")
            
            # Break after 10 events for demo purposes
            if event_count >= 10:
                break
        
        print(f"Received {event_count} events\n")
        
        # Example 4: Listen to specific response
        print("\n=== Example 4: Listen to response events ===")
        
        # First submit an activation to get a response_id
        response = await client.activations.submit(
            agent_id="agent_123",
            thread_id="thread_456",
        )
        
        response_id = response.response_id
        print(f"Listening to response: {response_id}\n")
        
        async for event in client.activations.listen_response_events(
            response_id=response_id,
            channels=["responses", "activations"],
        ):
            if event.data:
                event_type = event.data.get('type')
                print(f"📡 {event_type}")
                
                # Stop when response is complete
                if event_type in ['response.stream_complete', 'activation.completed']:
                    break
        
        print("\n✅ All streaming examples completed!")


if __name__ == "__main__":
    asyncio.run(main())

