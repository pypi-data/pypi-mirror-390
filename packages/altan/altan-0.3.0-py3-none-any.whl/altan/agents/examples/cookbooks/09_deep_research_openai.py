"""
Cookbook 09: Deep Research with OpenAI Web Search

Demonstrates:
- Deep, multi-turn research using GPT-5 with web search
- Real-time information gathering and synthesis
- Location-aware research and local context
- Action trace analysis for transparency
- Industry and business research workflows

Uses OpenAI's web_search_2025_08_26 with managed streaming API.
Each example uses exactly 3 research turns for focused, efficient research.
"""

import asyncio
from logging import basicConfig, INFO
import sys
from typing import List, Dict, Any

sys.path.insert(0, "../..")
from agents import AgentClient, MessageHistory
from agents.types import WebSearchConfig, WebSearchFilters, ApproximateLocation

basicConfig(level=INFO)


# ============================================================================
# Example 1: Market Research and Analysis
# ============================================================================

async def example_01_market_research():
    """
    Deep market research with competitive analysis.
    
    Shows:
    - Industry trend analysis
    - Competitive landscape
    - Strategic recommendations
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: Market Research and Analysis")
    print("="*80)
    
    client = AgentClient()
    history = MessageHistory()
    
    filters: WebSearchFilters = {
        "allowed_domains": [
            "techcrunch.com",
            "bloomberg.com",
            "reuters.com",
            "forbes.com",
            "wsj.com"
        ]
    }
    
    web_search: WebSearchConfig = {
        "enabled": True,
        "type": "web_search_2025_08_26",
        "filters": filters,
        "search_context_size": "high",
        "include_sources": True,
        "include_actions": True
    }
    
    print("\n💼 Research Topic: AI Infrastructure Market")
    print("   Model: gpt-5")
    print("   Turns: 3")
    
    # Turn 1: Market overview
    print("\n" + "-"*80)
    print("🔍 TURN 1: Market Overview")
    print("-"*80)
    
    history.add_user(
        "Research the AI infrastructure market. What's the current market size, "
        "key players (AWS, Google Cloud, Azure, CoreWeave), and recent growth trends?"
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    async for event in client.responses.stream(
        messages=history,
        model="gpt-5",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "tool_request" and event.get("name") == "web_search":
            print("\n[Searching market data...]", end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
            for part in event.get("parts", []):
                if part.get("type") == "tool" and part.get("name") == "web_search":
                    sources = part.get("sources", [])
                    actions = part.get("actions", [])
                    print(f"\n📊 Found {len(sources)} sources via {len(actions)} actions")
    
    # Turn 2: Recent developments
    print("\n" + "-"*80)
    print("🔍 TURN 2: Recent Developments")
    print("-"*80)
    
    history.add_user(
        "What are the most significant market developments from the last 6 months? "
        "Include funding rounds, new launches, and partnerships."
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    async for event in client.responses.stream(
        messages=history,
        model="gpt-5",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "tool_request" and event.get("name") == "web_search":
            print("\n[Searching recent news...]", end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
    
    # Turn 3: Executive summary
    print("\n" + "-"*80)
    print("📊 TURN 3: Executive Summary")
    print("-"*80)
    
    history.add_user(
        "Create an executive summary with key findings, market metrics, "
        "competitive positioning, and strategic recommendations."
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    async for event in client.responses.stream(
        messages=history,
        model="gpt-5",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
    
    print(f"\n✅ Market research completed: {len(history.get_messages()) // 2} turns")


# ============================================================================
# Example 2: Location-Aware Research
# ============================================================================

async def example_02_location_aware_research():
    """
    Deep research with location context for local insights.
    
    Shows:
    - Location-specific information
    - Regional trends
    - Geo-contextualized recommendations
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: Location-Aware Research")
    print("="*80)
    
    client = AgentClient()
    history = MessageHistory()
    
    location: ApproximateLocation = {
        "type": "approximate",
        "city": "San Francisco",
        "region": "California",
        "country": "US",
        "timezone": "America/Los_Angeles"
    }
    
    web_search: WebSearchConfig = {
        "enabled": True,
        "type": "web_search_2025_08_26",
        "user_location": location,
        "search_context_size": "high",
        "include_sources": True
    }
    
    print("\n🌎 Research Topic: Local AI Ecosystem")
    print(f"   Location: {location['city']}, {location['region']}")
    print("   Turns: 3")
    
    # Turn 1: Local landscape
    print("\n" + "-"*80)
    print("🔍 TURN 1: AI Ecosystem Overview")
    print("-"*80)
    
    history.add_user(
        "Research the AI startup ecosystem in my area. What are the most prominent "
        "AI companies, recent funding rounds, and key players?"
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    async for event in client.responses.stream(
        messages=history,
        model="gpt-5",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "tool_request" and event.get("name") == "web_search":
            print("\n[Searching local ecosystem...]", end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
    
    # Turn 2: Resources
    print("\n" + "-"*80)
    print("🔍 TURN 2: Local Resources & Events")
    print("-"*80)
    
    history.add_user(
        "What are the best local universities, research labs, accelerators, "
        "and recent AI events or conferences in my area?"
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    async for event in client.responses.stream(
        messages=history,
        model="gpt-5",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "tool_request" and event.get("name") == "web_search":
            print("\n[Researching local resources...]", end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
    
    # Turn 3: Opportunities
    print("\n" + "-"*80)
    print("🔍 TURN 3: Opportunities")
    print("-"*80)
    
    history.add_user(
        "Based on this research, what are the best opportunities for someone "
        "looking to work in or start an AI company in this area?"
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    async for event in client.responses.stream(
        messages=history,
        model="gpt-5",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
    
    print(f"\n✅ Location-aware research completed: {len(history.get_messages()) // 2} turns")


# ============================================================================
# Example 3: Real-Time Event Research
# ============================================================================

async def example_03_realtime_event_research():
    """
    Real-time research on current events.
    
    Shows:
    - Live information gathering
    - Multi-source verification
    - Impact analysis
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: Real-Time Event Research")
    print("="*80)
    
    client = AgentClient()
    history = MessageHistory()
    
    filters: WebSearchFilters = {
        "allowed_domains": [
            "nytimes.com",
            "reuters.com",
            "apnews.com",
            "bbc.com",
            "wsj.com"
        ]
    }
    
    web_search: WebSearchConfig = {
        "enabled": True,
        "type": "web_search_2025_08_26",
        "filters": filters,
        "search_context_size": "high",
        "include_sources": True
    }
    
    print("\n📰 Research Topic: AI Policy Developments")
    print("   Turns: 3")
    
    # Turn 1: Current state
    print("\n" + "-"*80)
    print("🔍 TURN 1: Current Policy Landscape")
    print("-"*80)
    
    history.add_user(
        "What are the latest developments in AI regulation and policy worldwide? "
        "Focus on recent announcements from the US, EU, and China."
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    async for event in client.responses.stream(
        messages=history,
        model="gpt-5",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "tool_request" and event.get("name") == "web_search":
            print("\n[Searching policy news...]", end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
    
    # Turn 2: Industry reaction
    print("\n" + "-"*80)
    print("🔍 TURN 2: Stakeholders & Response")
    print("-"*80)
    
    history.add_user(
        "Who are the key stakeholders driving these policies and how has "
        "the tech industry responded? Include major AI companies."
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    async for event in client.responses.stream(
        messages=history,
        model="gpt-5",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "tool_request" and event.get("name") == "web_search":
            print("\n[Researching reactions...]", end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
    
    # Turn 3: Implications
    print("\n" + "-"*80)
    print("🔍 TURN 3: Future Implications")
    print("-"*80)
    
    history.add_user(
        "What are the potential implications for AI development and deployment "
        "over the next 1-2 years based on these policy developments?"
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    async for event in client.responses.stream(
        messages=history,
        model="gpt-5",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
    
    print(f"\n✅ Real-time research completed: {len(history.get_messages()) // 2} turns")


# ============================================================================
# Example 4: Cross-Domain Knowledge Synthesis
# ============================================================================

async def example_04_cross_domain_synthesis():
    """
    Synthesize knowledge across multiple domains.
    
    Shows:
    - Multi-disciplinary research
    - Pattern identification
    - Knowledge integration
    """
    print("\n" + "="*80)
    print("EXAMPLE 4: Cross-Domain Synthesis")
    print("="*80)
    
    client = AgentClient()
    history = MessageHistory()
    
    web_search: WebSearchConfig = {
        "enabled": True,
        "type": "web_search_2025_08_26",
        "search_context_size": "high",
        "include_sources": True,
        "include_actions": True
    }
    
    print("\n🔬 Research Topic: AI in Climate Science")
    print("   Turns: 3")
    
    # Turn 1: Applications
    print("\n" + "-"*80)
    print("🔍 TURN 1: AI Applications")
    print("-"*80)
    
    history.add_user(
        "Research how AI is being applied to climate science. "
        "What are the main use cases from weather forecasting to climate modeling?"
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    async for event in client.responses.stream(
        messages=history,
        model="gpt-5",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "tool_request" and event.get("name") == "web_search":
            print("\n[Searching AI in climate...]", end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
    
    # Turn 2: Breakthroughs and challenges
    print("\n" + "-"*80)
    print("🔍 TURN 2: Breakthroughs & Challenges")
    print("-"*80)
    
    history.add_user(
        "What are recent breakthroughs and what are the main challenges? "
        "Include data quality, interpretability, and uncertainty issues."
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    async for event in client.responses.stream(
        messages=history,
        model="gpt-5",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "tool_request" and event.get("name") == "web_search":
            print("\n[Researching progress...]", end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
    
    # Turn 3: Future roadmap
    print("\n" + "-"*80)
    print("🔍 TURN 3: Future Roadmap")
    print("-"*80)
    
    history.add_user(
        "Based on this research, outline a 5-year roadmap. "
        "What are the most promising directions for AI in climate science?"
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    async for event in client.responses.stream(
        messages=history,
        model="gpt-5",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
            for part in event.get("parts", []):
                if part.get("type") == "tool" and part.get("name") == "web_search":
                    actions = part.get("actions", [])
                    if actions:
                        print(f"\n🎯 Research used {len(actions)} web actions")
    
    print(f"\n✅ Cross-domain research completed: {len(history.get_messages()) // 2} turns")


# ============================================================================
# Example 5: Investigative Deep Dive
# ============================================================================

async def example_05_investigative_research():
    """
    Investigative journalism-style research.
    
    Shows:
    - Timeline reconstruction
    - Evidence synthesis
    - Comprehensive analysis
    """
    print("\n" + "="*80)
    print("EXAMPLE 5: Investigative Deep Dive")
    print("="*80)
    
    client = AgentClient()
    history = MessageHistory()
    
    web_search: WebSearchConfig = {
        "enabled": True,
        "type": "web_search_2025_08_26",
        "search_context_size": "high",
        "include_sources": True,
        "include_actions": True
    }
    
    print("\n🔎 Research Topic: LLM Evolution")
    print("   Turns: 3")
    
    # Turn 1: Timeline
    print("\n" + "-"*80)
    print("🔍 TURN 1: Building Timeline")
    print("-"*80)
    
    history.add_user(
        "Create a timeline of major LLM releases from 2018 to present. "
        "Include model name, organization, parameters, and key innovations."
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    async for event in client.responses.stream(
        messages=history,
        model="gpt-5",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "tool_request" and event.get("name") == "web_search":
            print("\n[Building timeline...]", end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
    
    # Turn 2: Organizational dynamics
    print("\n" + "-"*80)
    print("🔍 TURN 2: Key Players & Dynamics")
    print("-"*80)
    
    history.add_user(
        "Map the organizational dynamics between OpenAI, Google, Anthropic, and Meta. "
        "Include competitive positioning and resource requirements."
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    async for event in client.responses.stream(
        messages=history,
        model="gpt-5",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "tool_request" and event.get("name") == "web_search":
            print("\n[Analyzing organizations...]", end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
    
    # Turn 3: Future trajectory
    print("\n" + "-"*80)
    print("🔍 TURN 3: Future Trajectory")
    print("-"*80)
    
    history.add_user(
        "What are expert predictions for the next major milestones? "
        "What technical and societal challenges need to be addressed?"
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    total_actions = 0
    
    async for event in client.responses.stream(
        messages=history,
        model="gpt-5",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
            for part in event.get("parts", []):
                if part.get("type") == "tool" and part.get("name") == "web_search":
                    actions = part.get("actions", [])
                    total_actions += len(actions)
    
    print(f"\n✅ Investigative research completed: {len(history.get_messages()) // 2} turns")
    if total_actions:
        print(f"   Total web actions across all turns: {total_actions}")


# ============================================================================
# Main - Run All Examples
# ============================================================================

async def main():
    """Run all deep research examples."""
    print("\n" + "="*80)
    print("DEEP RESEARCH WITH OPENAI WEB SEARCH")
    print("="*80)
    print("\nDemonstrates comprehensive research workflows using:")
    print("  • GPT-5 with web_search_2025_08_26")
    print("  • Managed streaming API for real-time results")
    print("  • 3-turn research pattern for focused insights")
    print("  • Location awareness and action tracing")
    
    try:
        await example_01_market_research()
        await example_02_location_aware_research()
        await example_03_realtime_event_research()
        await example_04_cross_domain_synthesis()
        await example_05_investigative_research()
        
        print("\n" + "="*80)
        print("✅ ALL RESEARCH EXAMPLES COMPLETED")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run all examples
    asyncio.run(main())
    
    # Or run individual examples:
    # asyncio.run(example_01_market_research())
    # asyncio.run(example_02_location_aware_research())
    # asyncio.run(example_03_realtime_event_research())
    # asyncio.run(example_04_cross_domain_synthesis())
    # asyncio.run(example_05_investigative_research())
