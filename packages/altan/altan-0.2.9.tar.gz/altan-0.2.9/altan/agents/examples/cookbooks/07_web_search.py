"""
Cookbook 07: Web Search Functionality

Demonstrates:
- Web search with OpenAI (web_search_2025_08_26)
- Web search with Anthropic (web-search-20250305)
- Low-level API with manual event processing
- Managed API with simplified events
- Multi-turn conversations with web search context
- Citations, sources, and action traces
- Domain filtering and location context

This shows comprehensive web search capabilities across providers.
"""

import asyncio
from logging import basicConfig, INFO
import sys
from typing import Dict, Any, List

sys.path.insert(0, "../..")
from agents import AgentClient, MessageHistory
from agents.types import WebSearchConfig, WebSearchFilters, ApproximateLocation

basicConfig(level=INFO)


# ============================================================================
# Example 1: OpenAI Web Search - Low-Level API
# ============================================================================

async def example_01_openai_low_level():
    """
    Low-level web search with OpenAI.
    
    Shows:
    - Direct web_search configuration
    - Raw event processing
    - Extracting citations, sources, and actions from tool parts
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: OpenAI Web Search - Low-Level API")
    print("="*80)
    
    client = AgentClient()
    
    # Configure web search with domain filtering
    filters: WebSearchFilters = {
        "allowed_domains": ["techcrunch.com", "theverge.com", "arstechnica.com"]
    }
    
    web_search: WebSearchConfig = {
        "enabled": True,
        "type": "web_search_2025_08_26",
        "filters": filters,
        "search_context_size": "high",
        "include_sources": True,
        "include_actions": True
    }
    
    print("\n📋 Configuration:")
    print(f"   Provider: OpenAI (gpt-4o)")
    print(f"   Tool: web_search_2025_08_26")
    print(f"   Context size: high")
    print(f"   Allowed domains: {filters['allowed_domains']}")
    
    # Stream the response
    print("\n🔄 Streaming response...")
    
    text_chunks = []
    tool_parts = []
    
    async for event in client.responses.create_stream(
        messages=[
            {"role": "user", "content": "What are the latest AI developments announced this week?"}
        ],
        model="gpt-4o",
        web_search=web_search
    ):
        event_type = event.get("event_type")
        data = event.get("data", {})
        
        if event_type == "message_part.updated":
            part_type = data.get("type")
            if part_type == "text":
                delta = data.get("delta", "")
                text_chunks.append(delta)
                print(delta, end="", flush=True)
        
        elif event_type == "message_part.done":
            part = data.get("part", {})
            if part.get("type") == "tool":
                tool_parts.append(part)
        
        elif event_type == "response.completed":
            print("\n\n✅ Response completed")
    
    # Process web search results
    print("\n" + "="*80)
    print("WEB SEARCH RESULTS")
    print("="*80)
    
    for part in tool_parts:
        if part.get("name") == "web_search":
            print(f"\n🔍 Web Search Tool Call: {part.get('tool_call_id')}")
            
            # Citations
            citations = part.get("citations", [])
            if citations:
                print(f"\n📎 Citations ({len(citations)}):")
                for i, citation in enumerate(citations, 1):
                    print(f"   {i}. {citation.get('url')}")
                    if citation.get('title'):
                        print(f"      Title: {citation['title']}")
                    if citation.get('location'):
                        print(f"      Location: {citation['location']}")
            
            # Sources
            sources = part.get("sources", [])
            if sources:
                print(f"\n🔗 Sources ({len(sources)}):")
                for i, source in enumerate(sources, 1):
                    print(f"   {i}. {source.get('url')}")
                    if source.get('title'):
                        print(f"      Title: {source['title']}")
            
            # Actions
            actions = part.get("actions", [])
            if actions:
                print(f"\n🎯 Actions ({len(actions)}):")
                for i, action in enumerate(actions, 1):
                    action_type = action.get('type')
                    if action_type == 'search':
                        print(f"   {i}. Search: {action.get('query')}")
                        sources_count = len(action.get('sources', []))
                        if sources_count:
                            print(f"      Found {sources_count} sources")
                    elif action_type == 'open_page':
                        print(f"   {i}. Opened: {action.get('url')}")
                    elif action_type == 'find_in_page':
                        print(f"   {i}. Found '{action.get('pattern')}' in {action.get('url')}")


# ============================================================================
# Example 2: Anthropic Web Search - Low-Level API
# ============================================================================

async def example_02_anthropic_low_level():
    """
    Low-level web search with Anthropic.
    
    Shows:
    - Anthropic server_tool_use format
    - Beta headers requirement
    - Max searches limit
    - Blocked domains filtering
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: Anthropic Web Search - Low-Level API")
    print("="*80)
    
    client = AgentClient()
    
    # Configure web search for Anthropic
    filters: WebSearchFilters = {
        "allowed_domains": ["nasa.gov", "noaa.gov", "climate.gov"]
        # Note: Anthropic only allows one of allowed_domains OR blocked_domains
    }
    
    web_search: WebSearchConfig = {
        "enabled": True,
        "max_searches": 3,  # Anthropic-specific: limit searches
        "filters": filters
    }
    
    print("\n📋 Configuration:")
    print(f"   Provider: Anthropic (claude-sonnet-4-5-latest)")
    print(f"   Tool: web_search_20250305")
    print(f"   Max searches: 3")
    print(f"   Allowed domains: {filters['allowed_domains']}")
    
    # Stream the response
    print("\n🔄 Streaming response...")
    
    text_chunks = []
    tool_parts = []
    
    async for event in client.responses.create_stream(
        messages=[
            {"role": "user", "content": "Find the latest climate change data from official sources"}
        ],
        model="claude-sonnet-4-5-latest",  # Required for web search
        web_search=web_search
    ):
        event_type = event.get("event_type")
        data = event.get("data", {})
        
        if event_type == "message_part.updated":
            part_type = data.get("type")
            if part_type == "text":
                delta = data.get("delta", "")
                text_chunks.append(delta)
                print(delta, end="", flush=True)
        
        elif event_type == "message_part.done":
            part = data.get("part", {})
            if part.get("type") == "tool":
                tool_parts.append(part)
        
        elif event_type == "response.completed":
            print("\n\n✅ Response completed")
    
    # Process web search results
    print("\n" + "="*80)
    print("WEB SEARCH RESULTS")
    print("="*80)
    
    for part in tool_parts:
        if part.get("name") == "web_search":
            print(f"\n🔍 Web Search Tool Call: {part.get('tool_call_id')}")
            
            # Sources (Anthropic provides rich source metadata)
            sources = part.get("sources", [])
            if sources:
                print(f"\n📚 Sources ({len(sources)}):")
                for i, source in enumerate(sources, 1):
                    print(f"   {i}. {source.get('url')}")
                    if source.get('title'):
                        print(f"      Title: {source['title']}")
                    if source.get('page_age'):
                        print(f"      Age: {source['page_age']}")
            
            # Citations
            citations = part.get("citations", [])
            if citations:
                print(f"\n📎 Citations ({len(citations)}):")
                for i, citation in enumerate(citations, 1):
                    print(f"   {i}. {citation.get('url')}")


# ============================================================================
# Example 3: OpenAI Web Search - Managed API
# ============================================================================

async def example_03_openai_managed():
    """
    Managed API web search with OpenAI.
    
    Shows:
    - Simplified event handling
    - MessageHistory integration
    - Easy result access
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: OpenAI Web Search - Managed API")
    print("="*80)
    
    client = AgentClient()
    history = MessageHistory()
    
    # Configure web search with location context
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
        "search_context_size": "high",
        "user_location": location,
        "include_sources": True
    }
    
    print("\n📋 Configuration:")
    print(f"   Provider: OpenAI (gpt-4o)")
    print(f"   Location: {location['city']}, {location['region']}")
    print(f"   Context size: high")
    
    # Add user message
    history.add_user("What's the weather forecast for my area this week?")
    
    print("\n🔄 Streaming with managed API...")
    
    # Stream with managed API
    async for event in client.responses.stream(
        messages=history,
        model="gpt-4o",
        web_search=web_search
    ):
        event_type = event.get("type")
        
        if event_type == "text":
            print(event["delta"], end="", flush=True)
        
        elif event_type == "tool_request":
            tool_name = event.get("name")
            if tool_name == "web_search":
                print(f"\n🔍 Searching the web...", flush=True)
        
        elif event_type == "complete":
            print("\n\n✅ Complete")
            
            # Add to history
            history.add_assistant(event)
            
            # Show web search metadata
            parts = event.get("parts", [])
            for part in parts:
                if part.get("type") == "tool" and part.get("name") == "web_search":
                    citations = part.get("citations", [])
                    sources = part.get("sources", [])
                    
                    if sources:
                        print(f"\n🔗 Found {len(sources)} sources:")
                        for source in sources[:3]:  # Show first 3
                            print(f"   • {source.get('url')}")
                    
                    if citations:
                        print(f"\n📎 {len(citations)} citations in text")


# ============================================================================
# Example 4: Anthropic Web Search - Managed API
# ============================================================================

async def example_04_anthropic_managed():
    """
    Managed API web search with Anthropic.
    
    Shows:
    - Anthropic beta headers
    - Max searches limit
    - Research-focused filtering
    """
    print("\n" + "="*80)
    print("EXAMPLE 4: Anthropic Web Search - Managed API")
    print("="*80)
    
    client = AgentClient()
    history = MessageHistory()
    
    # Configure web search for research
    filters: WebSearchFilters = {
        "allowed_domains": [
            "arxiv.org",
            "nature.com",
            "sciencedirect.com",
            "scholar.google.com"
        ]
        # Note: Anthropic only allows one of allowed_domains OR blocked_domains
    }
    
    web_search: WebSearchConfig = {
        "enabled": True,
        "max_searches": 2,  # Limit to 2 searches
        "filters": filters
    }
    
    print("\n📋 Configuration:")
    print(f"   Provider: Anthropic (claude-sonnet-4-5-latest)")
    print(f"   Max searches: 2")
    print(f"   Domains: Academic sources only")
    
    # Add user message
    history.add_user("What are the latest breakthroughs in quantum computing?")
    
    print("\n🔄 Streaming with managed API...")
    
    # Stream with managed API
    async for event in client.responses.stream(
        messages=history,
        model="claude-sonnet-4-5-latest",
        web_search=web_search
    ):
        event_type = event.get("type")
        
        if event_type == "text":
            print(event["delta"], end="", flush=True)
        
        elif event_type == "tool_request":
            tool_name = event.get("name")
            if tool_name == "web_search":
                print(f"\n🔍 Searching academic sources...", flush=True)
        
        elif event_type == "complete":
            print("\n\n✅ Complete")
            
            # Add to history
            history.add_assistant(event)
            
            # Show sources
            parts = event.get("parts", [])
            for part in parts:
                if part.get("type") == "tool" and part.get("name") == "web_search":
                    sources = part.get("sources", [])
                    
                    if sources:
                        print(f"\n📚 Academic Sources ({len(sources)}):")
                        for source in sources:
                            url = source.get('url', '')
                            title = source.get('title', 'No title')
                            print(f"   • {title}")
                            print(f"     {url}")
                            if source.get('page_age'):
                                print(f"     Published: {source['page_age']}")


# ============================================================================
# Example 5: OpenAI Web Search - Multi-Turn with chat()
# ============================================================================

async def example_05_openai_multiturn():
    """
    Multi-turn conversation with web search using chat() API.
    
    Shows:
    - Blocking chat() API for simplicity
    - Web search context across turns
    - Follow-up questions with search context
    """
    print("\n" + "="*80)
    print("EXAMPLE 5: OpenAI Web Search - Multi-Turn with chat()")
    print("="*80)
    
    client = AgentClient()
    history = MessageHistory()
    
    # Configure web search
    web_search: WebSearchConfig = {
        "enabled": True,
        "type": "web_search_2025_08_26",
        "search_context_size": "medium",
        "include_sources": True
    }
    
    print("\n📋 Multi-turn conversation with web search")
    print("   Provider: OpenAI (gpt-4o)")
    print("   Mode: Blocking chat() API")
    
    # Turn 1: Initial web search
    print("\n" + "-"*80)
    print("TURN 1: Initial Question")
    print("-"*80)
    
    history.add_user("What's the current state of electric vehicle adoption?")
    
    response = await client.responses.chat(
        messages=history,
        model="gpt-4o",
        web_search=web_search,
        max_turns=1
    )
    
    print(f"\n🤖 Assistant:\n{response['text']}")
    
    # Show sources
    for part in response["parts"]:
        if part.get("type") == "tool" and part.get("name") == "web_search":
            sources = part.get("sources", [])
            if sources:
                print(f"\n🔗 Sources: {len(sources)} URLs consulted")
    
    history.add_assistant(response)
    
    # Turn 2: Follow-up question (uses previous search context)
    print("\n" + "-"*80)
    print("TURN 2: Follow-up Question")
    print("-"*80)
    
    history.add_user("Which countries have the highest adoption rates?")
    
    response = await client.responses.chat(
        messages=history,
        model="gpt-4o",
        web_search=web_search,
        max_turns=1
    )
    
    print(f"\n🤖 Assistant:\n{response['text']}")
    
    # Show if another search was performed
    search_count = sum(
        1 for part in response["parts"] 
        if part.get("type") == "tool" and part.get("name") == "web_search"
    )
    
    if search_count > 0:
        print(f"\n🔍 Performed {search_count} additional search(es)")
    else:
        print(f"\n💭 Used previous search context (no new search needed)")
    
    history.add_assistant(response)
    
    print(f"\n📊 Conversation: {len(history.get_messages())} messages")


# ============================================================================
# Example 6: Anthropic Web Search - Multi-Turn Research
# ============================================================================

async def example_06_anthropic_multiturn():
    """
    Multi-turn research conversation with Anthropic web search.
    
    Shows:
    - Extended research with max_searches limit
    - Academic domain filtering
    - Building research context across turns
    """
    print("\n" + "="*80)
    print("EXAMPLE 6: Anthropic Web Search - Multi-Turn Research")
    print("="*80)
    
    client = AgentClient()
    history = MessageHistory()
    
    # Configure for academic research
    filters: WebSearchFilters = {
        "allowed_domains": [
            "nature.com",
            "science.org",
            "pnas.org",
            "nih.gov"
        ]
    }
    
    web_search: WebSearchConfig = {
        "enabled": True,
        "max_searches": 2,
        "filters": filters
    }
    
    print("\n📋 Research Configuration:")
    print(f"   Provider: Anthropic (claude-sonnet-4-5-latest)")
    print(f"   Max searches per request: 2")
    print(f"   Focus: Scientific/medical sources")
    
    # Turn 1: Broad research question
    print("\n" + "-"*80)
    print("TURN 1: Broad Research Question")
    print("-"*80)
    
    history.add_user("What are the latest findings on mRNA vaccine technology?")
    
    response = await client.responses.chat(
        messages=history,
        model="claude-sonnet-4-5-latest",
        web_search=web_search,
        max_turns=1
    )
    
    print(f"\n🤖 Assistant:\n{response['text']}")
    history.add_assistant(response)
    
    # Show sources
    for part in response["parts"]:
        if part.get("type") == "tool" and part.get("name") == "web_search":
            sources = part.get("sources", [])
            if sources:
                print(f"\n📚 Research Sources ({len(sources)}):")
                for source in sources:
                    print(f"   • {source.get('url')}")
    
    # Turn 2: Specific follow-up
    print("\n" + "-"*80)
    print("TURN 2: Specific Follow-up")
    print("-"*80)
    
    history.add_user("What are the key challenges in scaling production?")
    
    response = await client.responses.chat(
        messages=history,
        model="claude-sonnet-4-5-latest",
        web_search=web_search,
        max_turns=1
    )
    
    print(f"\n🤖 Assistant:\n{response['text']}")
    history.add_assistant(response)
    
    print(f"\n📊 Research Thread: {len(history.get_messages())} messages")


# ============================================================================
# Example 7: Comparative Search - OpenAI vs Anthropic
# ============================================================================

async def example_07_comparative():
    """
    Compare web search results between providers.
    
    Shows:
    - Same query on both providers
    - Different configurations
    - Result comparison
    """
    print("\n" + "="*80)
    print("EXAMPLE 7: Comparative Search - OpenAI vs Anthropic")
    print("="*80)
    
    client = AgentClient()
    
    query = "What are the major AI safety concerns discussed by researchers?"
    
    # OpenAI configuration
    openai_search: WebSearchConfig = {
        "enabled": True,
        "type": "web_search_2025_08_26",
        "search_context_size": "high",
        "include_sources": True
    }
    
    # Anthropic configuration
    anthropic_search: WebSearchConfig = {
        "enabled": True,
        "max_searches": 2
    }
    
    print(f"\n❓ Query: {query}\n")
    
    # OpenAI search
    print("-"*80)
    print("🔵 OpenAI (gpt-4o)")
    print("-"*80)
    
    openai_response = await client.responses.chat(
        messages=[{"role": "user", "content": query}],
        model="gpt-4o",
        web_search=openai_search
    )
    
    print(f"\n{openai_response['text'][:300]}...")
    
    openai_sources = 0
    for part in openai_response["parts"]:
        if part.get("type") == "tool" and part.get("name") == "web_search":
            openai_sources = len(part.get("sources", []))
            actions = part.get("actions", [])
            print(f"\n📊 OpenAI Results:")
            print(f"   Sources: {openai_sources}")
            print(f"   Citations: {len(part.get('citations', []))}")
            print(f"   Actions: {len(actions)}")
    
    # Anthropic search
    print("\n" + "-"*80)
    print("🟣 Anthropic (claude-sonnet-4-5-latest)")
    print("-"*80)
    
    anthropic_response = await client.responses.chat(
        messages=[{"role": "user", "content": query}],
        model="claude-sonnet-4-5-latest",
        web_search=anthropic_search
    )
    
    print(f"\n{anthropic_response['text'][:300]}...")
    
    anthropic_sources = 0
    for part in anthropic_response["parts"]:
        if part.get("type") == "tool" and part.get("name") == "web_search":
            anthropic_sources = len(part.get("sources", []))
            print(f"\n📊 Anthropic Results:")
            print(f"   Sources: {anthropic_sources}")
            print(f"   Citations: {len(part.get('citations', []))}")
    
    # Comparison
    print("\n" + "="*80)
    print("📊 COMPARISON")
    print("="*80)
    print(f"OpenAI sources:    {openai_sources}")
    print(f"Anthropic sources: {anthropic_sources}")


# ============================================================================
# Example 8: Advanced - Location-Aware News Search
# ============================================================================

async def example_08_location_aware():
    """
    Location-aware web search for local content.
    
    Shows:
    - Full location context (city, region, country, timezone)
    - Local news filtering
    - Streaming with location hints
    """
    print("\n" + "="*80)
    print("EXAMPLE 8: Location-Aware News Search")
    print("="*80)
    
    client = AgentClient()
    
    # Configure for Tokyo, Japan
    location: ApproximateLocation = {
        "type": "approximate",
        "city": "Tokyo",
        "region": "Kanto",
        "country": "JP",
        "timezone": "Asia/Tokyo"
    }
    
    filters: WebSearchFilters = {
        "allowed_domains": ["japantimes.co.jp", "nhk.or.jp", "asahi.com"]
    }
    
    web_search: WebSearchConfig = {
        "enabled": True,
        "type": "web_search_2025_08_26",
        "filters": filters,
        "user_location": location,
        "search_context_size": "high",
        "include_sources": True
    }
    
    print("\n📋 Configuration:")
    print(f"   Location: Tokyo, Japan")
    print(f"   Timezone: Asia/Tokyo")
    print(f"   Sources: Japanese news outlets")
    
    print("\n🔄 Searching for local news...")
    
    response = await client.responses.chat(
        messages=[
            {"role": "user", "content": "What are the top news stories today in my area?"}
        ],
        model="gpt-4o",
        web_search=web_search
    )
    
    print(f"\n🤖 Assistant:\n{response['text']}")
    
    # Show sources with location context
    for part in response["parts"]:
        if part.get("type") == "tool" and part.get("name") == "web_search":
            sources = part.get("sources", [])
            if sources:
                print(f"\n🗾 Local Sources ({len(sources)}):")
                for source in sources:
                    print(f"   • {source.get('url')}")


# ============================================================================
# Example 9: Advanced - Research Workflow
# ============================================================================

async def example_09_research_workflow():
    """
    Complete research workflow with web search.
    
    Shows:
    - Initial broad search
    - Iterative refinement
    - Citation tracking
    - Building comprehensive research
    """
    print("\n" + "="*80)
    print("EXAMPLE 9: Research Workflow")
    print("="*80)
    
    client = AgentClient()
    history = MessageHistory()
    
    # Configure for comprehensive research
    filters: WebSearchFilters = {
        "allowed_domains": [
            "arxiv.org",
            "nature.com",
            "science.org",
            "ieee.org",
            "acm.org"
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
    
    print("\n📋 Research Workflow Configuration:")
    print(f"   Provider: OpenAI (gpt-4o)")
    print(f"   Focus: Academic papers and publications")
    print(f"   Method: Iterative refinement")
    
    all_citations = []
    all_sources = []
    
    # Step 1: Broad search
    print("\n" + "-"*80)
    print("STEP 1: Broad Literature Search")
    print("-"*80)
    
    history.add_user("Find recent papers on large language model alignment techniques")
    
    response = await client.responses.chat(
        messages=history,
        model="gpt-4o",
        web_search=web_search
    )
    
    print(f"\n🔎 Initial Search Results:")
    print(f"{response['text'][:200]}...\n")
    
    # Collect citations
    for part in response["parts"]:
        if part.get("type") == "tool" and part.get("name") == "web_search":
            citations = part.get("citations", [])
            sources = part.get("sources", [])
            all_citations.extend(citations)
            all_sources.extend(sources)
            
            print(f"   Found {len(sources)} papers")
            print(f"   {len(citations)} inline citations")
    
    history.add_assistant(response)
    
    # Step 2: Specific technique
    print("\n" + "-"*80)
    print("STEP 2: Focus on Specific Technique")
    print("-"*80)
    
    history.add_user("Tell me more about RLHF (Reinforcement Learning from Human Feedback)")
    
    response = await client.responses.chat(
        messages=history,
        model="gpt-4o",
        web_search=web_search
    )
    
    print(f"\n🔎 Refined Search Results:")
    print(f"{response['text'][:200]}...\n")
    
    # Collect more citations
    for part in response["parts"]:
        if part.get("type") == "tool" and part.get("name") == "web_search":
            citations = part.get("citations", [])
            sources = part.get("sources", [])
            all_citations.extend(citations)
            all_sources.extend(sources)
            
            actions = part.get("actions", [])
            print(f"   Actions performed: {len(actions)}")
            for action in actions:
                if action.get('type') == 'search':
                    print(f"   • Search: {action.get('query')}")
    
    history.add_assistant(response)
    
    # Step 3: Practical applications
    print("\n" + "-"*80)
    print("STEP 3: Practical Applications")
    print("-"*80)
    
    history.add_user("What are the practical implementations of this in production systems?")
    
    response = await client.responses.chat(
        messages=history,
        model="gpt-4o",
        web_search=web_search
    )
    
    print(f"\n🔎 Application Search Results:")
    print(f"{response['text'][:200]}...\n")
    
    history.add_assistant(response)
    
    # Summary
    print("\n" + "="*80)
    print("📊 RESEARCH SUMMARY")
    print("="*80)
    print(f"Total turns: {len(history.get_messages()) // 2}")
    print(f"Total citations collected: {len(all_citations)}")
    print(f"Total sources consulted: {len(all_sources)}")
    
    # Show unique domains
    unique_domains = set()
    for source in all_sources:
        url = source.get('url', '')
        if '://' in url:
            domain = url.split('://')[1].split('/')[0]
            unique_domains.add(domain)
    
    print(f"Unique domains: {len(unique_domains)}")
    print(f"   {', '.join(list(unique_domains)[:5])}")


# ============================================================================
# Example 10: Advanced - Action Traces Analysis
# ============================================================================

async def example_10_action_traces():
    """
    Analyze web search action traces.
    
    Shows:
    - Detailed action logging
    - Search, open_page, and find_in_page actions
    - Performance insights
    """
    print("\n" + "="*80)
    print("EXAMPLE 10: Action Traces Analysis")
    print("="*80)
    
    client = AgentClient()
    
    # Configure to capture all actions
    web_search: WebSearchConfig = {
        "enabled": True,
        "type": "web_search_2025_08_26",
        "search_context_size": "high",
        "include_sources": True,
        "include_actions": True  # Critical: request action traces
    }
    
    print("\n📋 Configuration:")
    print(f"   Provider: OpenAI (gpt-4o)")
    print(f"   Action tracing: ENABLED")
    
    response = await client.responses.chat(
        messages=[
            {"role": "user", "content": "Find information about the latest SpaceX launch and its mission objectives"}
        ],
        model="gpt-4o",
        web_search=web_search
    )
    
    print(f"\n🤖 Assistant:\n{response['text'][:300]}...\n")
    
    # Analyze actions
    for part in response["parts"]:
        if part.get("type") == "tool" and part.get("name") == "web_search":
            actions = part.get("actions", [])
            
            if actions:
                print(f"🎯 Action Traces ({len(actions)}):")
                print("="*80)
                
                for i, action in enumerate(actions, 1):
                    action_type = action.get('type')
                    status = action.get('status', 'unknown')
                    
                    print(f"\n{i}. {action_type.upper().replace('_', ' ')} [{status}]")
                    
                    if action_type == 'search':
                        query = action.get('query')
                        sources = action.get('sources', [])
                        print(f"   Query: {query}")
                        print(f"   Results: {len(sources)} sources")
                        if sources:
                            print(f"   First source: {sources[0]}")
                    
                    elif action_type == 'open_page':
                        url = action.get('url')
                        print(f"   URL: {url}")
                    
                    elif action_type == 'find_in_page':
                        url = action.get('url')
                        pattern = action.get('pattern')
                        print(f"   URL: {url}")
                        print(f"   Pattern: {pattern}")
                
                print("\n" + "="*80)
                print(f"Total actions: {len(actions)}")
                search_count = sum(1 for a in actions if a.get('type') == 'search')
                open_count = sum(1 for a in actions if a.get('type') == 'open_page')
                find_count = sum(1 for a in actions if a.get('type') == 'find_in_page')
                
                print(f"   Searches: {search_count}")
                print(f"   Pages opened: {open_count}")
                print(f"   Find operations: {find_count}")


# ============================================================================
# Main - Run All Examples
# ============================================================================

async def main():
    """Run all web search examples."""
    print("\n" + "="*80)
    print("WEB SEARCH COOKBOOK - ALL EXAMPLES")
    print("="*80)
    print("\nThis cookbook demonstrates web search functionality with:")
    print("  • OpenAI (web_search_2025_08_26)")
    print("  • Anthropic (web-search-20250305)")
    print("  • Low-level and managed APIs")
    print("  • Multi-turn conversations")
    print("  • Citations, sources, and action traces")
    
    try:
        # Low-level examples
        await example_01_openai_low_level()
        await example_02_anthropic_low_level()
        
        # Managed API examples
        await example_03_openai_managed()
        await example_04_anthropic_managed()
        
        # Multi-turn examples
        await example_05_openai_multiturn()
        await example_06_anthropic_multiturn()
        
        # Advanced examples
        await example_07_comparative()
        await example_08_location_aware()
        await example_09_research_workflow()
        await example_10_action_traces()
        
        print("\n" + "="*80)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run all examples
    asyncio.run(main())
    
    # Or run individual examples:
    # asyncio.run(example_01_openai_low_level())
    # asyncio.run(example_03_openai_managed())
    # asyncio.run(example_05_openai_multiturn())

