"""
Basic example of using the Responses API (stateless mode).
"""

import asyncio
from python_sdk import AgentClient, ResponseMessage


async def main():
    """Basic stateless response example."""
    
    # Initialize client
    async with AgentClient(base_url="http://localhost:8000") as client:
        
        # Example 1: Simple inline configuration
        print("=== Example 1: Simple inline configuration ===")
        response = await client.responses.create(
            messages=[
                {"role": "user", "content": "What is the capital of France?"}
            ],
            model="gpt-4o",
            temperature=0.7,
            max_tokens=1000,
            member_id="user_123",
        )
        
        print(f"Response ID: {response.response_id}")
        print(f"Context ID: {response.context_id}")
        print(f"Model: {response.model}")
        print(f"Status: {response.status}")
        print()
        
        # Example 2: Using agent_id with overwrites
        print("=== Example 2: Using agent_id with overwrites ===")
        response = await client.responses.create(
            messages=[
                {"role": "user", "content": "Tell me about Python"}
            ],
            agent_id="agent_abc123",
            overwrites={
                "temperature": 0.5,  # Override agent's default temperature
            },
            member_id="user_123",
        )
        
        print(f"Response ID: {response.response_id}")
        print(f"Context ID: {response.context_id}")
        print()
        
        # Example 3: With system prompt and text configuration
        print("=== Example 3: With system prompt ===")
        response = await client.responses.create(
            messages=[
                {"role": "user", "content": "Explain quantum computing"}
            ],
            model="gpt-4o",
            system="You are a helpful physics teacher.",
            text={
                "verbosity": "medium",
                "format": {"type": "text"}
            },
            member_id="user_123",
        )
        
        print(f"Response ID: {response.response_id}")
        print()
        
        # Example 4: Multi-part content with images
        print("=== Example 4: Multi-part content ===")
        response = await client.responses.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What's in this image?"},
                        {"type": "image_url", "image_url": "https://example.com/image.jpg"}
                    ]
                }
            ],
            model="gpt-4o",
            member_id="user_123",
        )
        
        print(f"Response ID: {response.response_id}")
        print()
        
        print("✅ All examples completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())

