"""
Cookbook 09: Parallel & Concurrent Request Patterns

Demonstrates:
- Batch processing multiple queries
- Parallel agent execution
- Concurrent streaming
- Result aggregation
- Performance optimization
"""

import asyncio
import sys
from typing import List, Dict, Any
from utils import (
    print_header,
    print_section,
    print_message,
    print_success,
    print_info,
    print_divider,
    get_client,
)

sys.path.insert(0, "../..")
from agents.types import SimpleMessage


async def process_single_query(
    client: Any,
    query: str,
    query_id: int,
) -> Dict[str, Any]:
    """Process a single query and return results."""
    start_time = asyncio.get_event_loop().time()
    
    full_text = ""
    event_count = 0
    
    async for event in client.responses.create_stream(
        messages=[SimpleMessage(role="user", content=query)],  # type: ignore
        model="gpt-4o",
        temperature=0.7,
        max_tokens=200,
    ):
        event_count += 1
        
        event_type = event.get("event_type", "")
        data = event.get("data", {})
        
        if event_type == "message_part.updated":
            delta = data.get("delta", "")
            if delta:
                full_text += delta
    
    duration = asyncio.get_event_loop().time() - start_time
    
    return {
        "query_id": query_id,
        "query": query,
        "response": full_text,
        "duration": duration,
        "event_count": event_count,
    }


async def run_parallel_batch_processing() -> None:
    """Demonstrate processing multiple queries in parallel."""
    
    print_header("Cookbook: Parallel Batch Processing")
    
    print("Scenario: Process multiple user queries simultaneously")
    print("This is useful for batch operations, analytics, etc.\n")
    
    # Batch of queries to process
    queries = [
        "What is Python?",
        "What is JavaScript?",
        "What is Rust?",
        "What is Go?",
        "What is TypeScript?",
    ]
    
    print_section("Sequential Processing (Baseline)")
    print_info(f"Processing {len(queries)} queries sequentially...\n")
    
    sequential_start = asyncio.get_event_loop().time()
    sequential_results = []
    
    async with get_client() as client:
        for i, query in enumerate(queries, 1):
            print(f"  Processing {i}/{len(queries)}: {query[:40]}...", end="", flush=True)
            result = await process_single_query(client, query, i)
            sequential_results.append(result)
            print(f" ✓ ({result['duration']:.2f}s)")
    
    sequential_duration = asyncio.get_event_loop().time() - sequential_start
    
    print_success(f"Sequential processing completed in {sequential_duration:.2f}s")
    
    # Parallel processing
    print_section("Parallel Processing (Optimized)")
    print_info(f"Processing {len(queries)} queries in parallel...\n")
    
    parallel_start = asyncio.get_event_loop().time()
    
    async with get_client() as client:
        # Create tasks for all queries
        tasks = [
            process_single_query(client, query, i)
            for i, query in enumerate(queries, 1)
        ]
        
        # Execute all tasks concurrently
        parallel_results = await asyncio.gather(*tasks)
    
    parallel_duration = asyncio.get_event_loop().time() - parallel_start
    
    print_success(f"Parallel processing completed in {parallel_duration:.2f}s")
    
    # Display results
    print_section("Performance Comparison")
    
    speedup = sequential_duration / parallel_duration if parallel_duration > 0 else 0
    
    print(f"  Sequential time: {sequential_duration:.2f}s")
    print(f"  Parallel time:   {parallel_duration:.2f}s")
    print(f"  Speedup:         {speedup:.2f}x faster")
    print(f"  Time saved:      {sequential_duration - parallel_duration:.2f}s ({(1 - parallel_duration/sequential_duration)*100:.1f}%)")
    
    print("\n📊 Individual Query Performance:")
    for result in parallel_results:
        print(f"  Query {result['query_id']}: {result['duration']:.2f}s, {result['event_count']} events")


async def run_concurrent_streaming_display() -> None:
    """Demonstrate displaying multiple streams concurrently."""
    
    print_header("Cookbook: Concurrent Streaming Display")
    
    print("Scenario: Display multiple AI responses streaming simultaneously")
    print("Like a multi-agent dashboard or parallel research.\n")
    
    queries = [
        ("Agent A", "Explain quantum computing in one sentence."),
        ("Agent B", "Explain blockchain in one sentence."),
        ("Agent C", "Explain neural networks in one sentence."),
    ]
    
    print_section("Concurrent Streaming Responses")
    
    # Track responses for each agent
    responses: Dict[str, str] = {name: "" for name, _ in queries}
    completed: Dict[str, bool] = {name: False for name, _ in queries}
    
    async def stream_response(agent_name: str, query: str, client: Any) -> None:
        """Stream a single response and track it."""
        async for event in client.responses.create_stream(
            messages=[SimpleMessage(role="user", content=query)],  # type: ignore
            model="gpt-4o",
            temperature=0.7,
            max_tokens=100,
        ):
            event_type = event.get("event_type", "")
            data = event.get("data", {})
            
            if event_type == "message_part.updated":
                delta = data.get("delta", "")
                if delta:
                    responses[agent_name] += delta
            
            elif event_type == "response.completed":
                completed[agent_name] = True
    
    async with get_client() as client:
        # Start all streams concurrently
        tasks = [
            stream_response(name, query, client)
            for name, query in queries
        ]
        
        # Monitor progress
        monitor_task = asyncio.create_task(asyncio.gather(*tasks))
        
        # Display progress while streaming
        while not all(completed.values()):
            # Clear screen section (simulated)
            print("\033[2J\033[H", end="")  # Clear screen
            print_section("Live Streaming Status")
            
            for agent_name, _ in queries:
                status = "✓" if completed[agent_name] else "⌨️"
                response_preview = responses[agent_name][:60] + "..." if len(responses[agent_name]) > 60 else responses[agent_name]
                print(f"{status} {agent_name}: {response_preview}")
            
            await asyncio.sleep(0.2)
        
        # Wait for all to complete
        await monitor_task
    
    # Final display
    print("\033[2J\033[H", end="")  # Clear screen
    print_section("Final Responses")
    
    for agent_name, query in queries:
        print(f"\n🤖 {agent_name}:")
        print(f"  Q: {query}")
        print(f"  A: {responses[agent_name]}")
    
    print_success("All concurrent streams completed")


async def run_parallel_agent_collaboration() -> None:
    """Demonstrate parallel execution of different agent tasks."""
    
    print_header("Cookbook: Parallel Agent Collaboration")
    
    print("Scenario: Multiple agents work on different parts of a task simultaneously\n")
    
    async def research_task(client: Any, aspect: str) -> Dict[str, Any]:
        """Research a specific aspect."""
        print_info(f"Agent researching: {aspect}")
        
        full_text = ""
        
        async for event in client.responses.create_stream(
            messages=[
                SimpleMessage(  # type: ignore
                    role="user",
                    content=f"In 2-3 sentences, explain {aspect}",
                ),
            ],
            model="gpt-4o",
            temperature=0.6,
            max_tokens=150,
        ):
            event_type = event.get("event_type", "")
            data = event.get("data", {})
            
            if event_type == "message_part.updated":
                delta = data.get("delta", "")
                if delta:
                    full_text += delta
        
        return {"aspect": aspect, "findings": full_text}
    
    # Research aspects
    aspects = [
        "the history of artificial intelligence",
        "current applications of AI in healthcare",
        "future challenges of AI development",
    ]
    
    print_section("Parallel Research Execution")
    
    start_time = asyncio.get_event_loop().time()
    
    async with get_client() as client:
        # Execute all research tasks in parallel
        tasks = [research_task(client, aspect) for aspect in aspects]
        results = await asyncio.gather(*tasks)
    
    duration = asyncio.get_event_loop().time() - start_time
    
    # Display findings
    print_section("Research Findings")
    
    for result in results:
        print(f"\n📚 {result['aspect'].title()}:")
        print(f"  {result['findings']}")
    
    print(f"\n{print_success(f'Parallel research completed in {duration:.2f}s')}")
    print_info(f"Processing {len(aspects)} research tasks in parallel saved time")


async def main() -> None:
    """Run all parallel processing demonstrations."""
    await run_parallel_batch_processing()
    print("\n" + "="*80 + "\n")
    await run_concurrent_streaming_display()
    print("\n" + "="*80 + "\n")
    await run_parallel_agent_collaboration()


if __name__ == "__main__":
    asyncio.run(main())

