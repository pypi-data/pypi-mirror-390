"""
Basic examples of using the Activations API.
"""

import asyncio
from python_sdk import AgentClient


async def main():
    """Basic activations examples."""
    
    async with AgentClient(base_url="http://localhost:8000") as client:
        
        # Example 1: Submit a basic activation
        print("=== Example 1: Submit activation ===")
        response = await client.activations.submit(
            agent_id="agent_123",
            thread_id="thread_456",
            room_id="room_789",
        )
        
        print(f"Response ID: {response.response_id}")
        print(f"Agent ID: {response.agent_id}")
        print(f"Thread ID: {response.thread_id}")
        print(f"Queued: {response.queued}")
        print(f"Message: {response.message}")
        print()
        
        # Example 2: Retry/resume from a specific message
        print("=== Example 2: Retry from message ===")
        response = await client.activations.retry(
            agent_id="agent_123",
            thread_id="thread_456",
            override_message_id="msg_abc",
            room_id="room_789",
        )
        
        print(f"Response ID: {response.response_id}")
        print(f"Retrying from message: msg_abc")
        print()
        
        # Example 3: Get activation statistics
        print("=== Example 3: Get activation stats ===")
        stats = await client.activations.get_stats()
        
        print(f"Active activations: {stats.active_count}")
        print(f"Queued activations: {stats.queue_count}")
        print()
        
        # Example 4: Get thread status
        print("=== Example 4: Get thread status ===")
        status = await client.activations.get_thread_status(thread_id="thread_456")
        
        print(f"Thread ID: {status.thread_id}")
        print(f"Status: {status.status}")
        print(f"Queue length: {status.queue_length}")
        print()
        
        # Example 5: Get thread activations
        print("=== Example 5: Get thread activations ===")
        activations = await client.activations.get_thread_activations(
            thread_id="thread_456",
            include_queued=True,
        )
        
        print(f"Thread ID: {activations.thread_id}")
        print(f"Status: {activations.thread_status}")
        print(f"Active response: {activations.active_response_id}")
        print(f"Queue length: {activations.queue_length}")
        print(f"Queued activations: {len(activations.queued_activations)}")
        print()
        
        # Example 6: Set thread status
        print("=== Example 6: Set thread status ===")
        result = await client.activations.set_thread_status(
            thread_id="thread_456",
            status="paused",
        )
        
        print(f"Updated status: {result.status}")
        print()
        
        # Example 7: Cancel a response
        print("=== Example 7: Cancel response ===")
        try:
            cancellation = await client.activations.cancel_response(
                response_id=response.response_id,
                reason="User cancelled",
                timeout=5.0,
            )
            
            if cancellation.success:
                print(f"✅ Response cancelled: {cancellation.response_id}")
                print(f"Message: {cancellation.message}")
            else:
                print(f"⏱️  Cancellation timeout")
        except Exception as e:
            print(f"❌ Cancellation failed: {e}")
        print()
        
        # Example 8: Clear thread queue
        print("=== Example 8: Clear thread queue ===")
        result = await client.activations.clear_thread_queue(thread_id="thread_456")
        
        print(f"Success: {result.get('success')}")
        print(f"Cleared items: {result.get('cleared_items', 0)}")
        print()
        
        print("✅ All examples completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())

