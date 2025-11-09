"""
Cookbook 08: Deep Research with Anthropic Web Search

Demonstrates:
- Deep, multi-turn research using Claude with web search
- Iterative knowledge building across multiple searches
- Academic and technical research workflows
- Source verification and citation tracking
- Domain-specific filtering for quality sources

Uses Anthropic's web-search-20250305 with managed streaming API.
Each example uses exactly 3 research turns for focused, efficient research.
"""

import asyncio
from logging import basicConfig, INFO
import sys
from typing import List, Dict, Any

sys.path.insert(0, "../..")
from agents import AgentClient, MessageHistory
from agents.types import WebSearchConfig, WebSearchFilters

basicConfig(level=INFO)


# ============================================================================
# Example 1: Academic Paper Research
# ============================================================================

async def example_01_academic_paper_research():
    """
    Deep dive into academic literature on a specific topic.
    
    Shows:
    - Multi-turn academic research
    - Progressive refinement of search queries
    - Citation and source tracking
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: Academic Paper Research")
    print("="*80)
    
    client = AgentClient()
    history = MessageHistory()
    
    # Configure for academic sources
    filters: WebSearchFilters = {
        "allowed_domains": [
            "arxiv.org",
            "nature.com",
            "sciencedirect.com",
            "science.org",
            "pnas.org",
            "ieee.org",
            "acm.org"
        ]
    }
    
    web_search: WebSearchConfig = {
        "enabled": True,
        "max_searches": 3,
        "filters": filters
    }
    
    print("\n📚 Research Topic: Transformer Architecture Evolution")
    print("   Model: claude-sonnet-4-5-latest")
    print("   Turns: 3")
    
    all_sources = []
    
    # Turn 1: Overview
    print("\n" + "-"*80)
    print("🔍 TURN 1: Architecture Overview")
    print("-"*80)
    
    history.add_user(
        "Research the evolution of transformer architectures. Start with the original "
        "'Attention is All You Need' paper and trace major developments like BERT, GPT, and T5."
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    async for event in client.responses.stream(
        messages=history,
        model="claude-sonnet-4-5-latest",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "tool_request" and event.get("name") == "web_search":
            print("\n[Searching academic databases...]", end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
            for part in event.get("parts", []):
                if part.get("type") == "tool" and part.get("name") == "web_search":
                    sources = part.get("sources", [])
                    all_sources.extend(sources)
                    print(f"\n📄 Found {len(sources)} papers")
    
    # Turn 2: Recent innovations
    print("\n" + "-"*80)
    print("🔍 TURN 2: Recent Innovations")
    print("-"*80)
    
    history.add_user(
        "What are the most recent innovations in transformer architectures from 2024-2025? "
        "Focus on efficiency improvements and new capabilities."
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    async for event in client.responses.stream(
        messages=history,
        model="claude-sonnet-4-5-latest",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "tool_request" and event.get("name") == "web_search":
            print("\n[Searching recent publications...]", end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
            for part in event.get("parts", []):
                if part.get("type") == "tool" and part.get("name") == "web_search":
                    sources = part.get("sources", [])
                    all_sources.extend(sources)
                    print(f"\n📄 Found {len(sources)} recent papers")
    
    # Turn 3: Synthesis
    print("\n" + "-"*80)
    print("📊 TURN 3: Timeline Synthesis")
    print("-"*80)
    
    history.add_user(
        "Create a timeline of the 10 most important transformer innovations from 2017 to present, "
        "with brief descriptions of each breakthrough."
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    async for event in client.responses.stream(
        messages=history,
        model="claude-sonnet-4-5-latest",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
    
    # Summary
    print("\n" + "="*80)
    print("📊 RESEARCH SUMMARY")
    print("="*80)
    print(f"Turns: {len(history.get_messages()) // 2}")
    print(f"Total sources: {len(all_sources)}")
    unique_urls = set(source.get('url') for source in all_sources)
    print(f"Unique papers: {len(unique_urls)}")


# ============================================================================
# Example 2: Technical Problem Deep Dive
# ============================================================================

async def example_02_technical_problem_research():
    """
    Research a complex technical problem with iterative refinement.
    
    Shows:
    - Problem understanding
    - Solution exploration
    - Implementation recommendations
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: Technical Problem Deep Dive")
    print("="*80)
    
    client = AgentClient()
    history = MessageHistory()
    
    filters: WebSearchFilters = {
        "allowed_domains": [
            "arxiv.org",
            "github.com",
            "stackoverflow.com",
            "medium.com",
            "ieee.org"
        ]
    }
    
    web_search: WebSearchConfig = {
        "enabled": True,
        "max_searches": 3,
        "filters": filters
    }
    
    print("\n🔧 Research Topic: Distributed Training of LLMs")
    print("   Turns: 3")
    
    # Turn 1: Problem space
    print("\n" + "-"*80)
    print("🔍 TURN 1: Understanding the Problem")
    print("-"*80)
    
    history.add_user(
        "Research the challenges of distributed training for large language models. "
        "What are the main bottlenecks and technical challenges?"
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    async for event in client.responses.stream(
        messages=history,
        model="claude-sonnet-4-5-latest",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "tool_request" and event.get("name") == "web_search":
            print("\n[Researching distributed training...]", end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
    
    # Turn 2: Solutions
    print("\n" + "-"*80)
    print("🔍 TURN 2: Solution Approaches")
    print("-"*80)
    
    history.add_user(
        "Compare data parallelism, model parallelism, and pipeline parallelism. "
        "How do frameworks like DeepSpeed, Megatron-LM, and FSDP implement these?"
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    async for event in client.responses.stream(
        messages=history,
        model="claude-sonnet-4-5-latest",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "tool_request" and event.get("name") == "web_search":
            print("\n[Researching solutions...]", end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
    
    # Turn 3: Recommendations
    print("\n" + "-"*80)
    print("🔍 TURN 3: Practical Recommendations")
    print("-"*80)
    
    history.add_user(
        "Based on this research, what would you recommend for training a 70B parameter model "
        "on 64 A100 GPUs? Give specific configuration suggestions."
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    async for event in client.responses.stream(
        messages=history,
        model="claude-sonnet-4-5-latest",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
    
    print(f"\n✅ Research completed: {len(history.get_messages()) // 2} turns")


# ============================================================================
# Example 3: Comparative Analysis
# ============================================================================

async def example_03_comparative_analysis():
    """
    Deep comparative analysis of competing technologies.
    
    Shows:
    - Multi-faceted comparison
    - Evidence gathering
    - Decision framework
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: Comparative Analysis")
    print("="*80)
    
    client = AgentClient()
    history = MessageHistory()
    
    filters: WebSearchFilters = {
        "allowed_domains": [
            "arxiv.org",
            "github.com",
            "papers.nips.cc",
            "openreview.net"
        ]
    }
    
    web_search: WebSearchConfig = {
        "enabled": True,
        "max_searches": 3,
        "filters": filters
    }
    
    print("\n⚖️  Research Topic: Vision Transformers vs CNNs")
    print("   Turns: 3")
    
    # Turn 1: Background
    print("\n" + "-"*80)
    print("🔍 TURN 1: Architecture Foundations")
    print("-"*80)
    
    history.add_user(
        "Compare Vision Transformers (ViT) and CNNs for computer vision. "
        "Explain their fundamental design philosophies and evolution."
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    async for event in client.responses.stream(
        messages=history,
        model="claude-sonnet-4-5-latest",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "tool_request" and event.get("name") == "web_search":
            print("\n[Researching architectures...]", end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
    
    # Turn 2: Performance
    print("\n" + "-"*80)
    print("🔍 TURN 2: Performance Comparison")
    print("-"*80)
    
    history.add_user(
        "Compare their performance on ImageNet, COCO, and other benchmarks. "
        "Include accuracy, training time, inference speed, and parameter efficiency."
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    async for event in client.responses.stream(
        messages=history,
        model="claude-sonnet-4-5-latest",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "tool_request" and event.get("name") == "web_search":
            print("\n[Searching benchmarks...]", end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
    
    # Turn 3: Decision matrix
    print("\n" + "-"*80)
    print("📊 TURN 3: Decision Framework")
    print("-"*80)
    
    history.add_user(
        "Create a decision matrix with key criteria and when to use each architecture. "
        "Include data requirements, computational resources, and specific use cases."
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    async for event in client.responses.stream(
        messages=history,
        model="claude-sonnet-4-5-latest",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
    
    print(f"\n✅ Comparative analysis completed: {len(history.get_messages()) // 2} turns")


# ============================================================================
# Example 4: Longitudinal Research
# ============================================================================

async def example_04_longitudinal_study():
    """
    Track the evolution of a field over time.
    
    Shows:
    - Time-based research
    - Trend analysis
    - Future predictions
    """
    print("\n" + "="*80)
    print("EXAMPLE 4: Longitudinal Study")
    print("="*80)
    
    client = AgentClient()
    history = MessageHistory()
    
    filters: WebSearchFilters = {
        "allowed_domains": [
            "arxiv.org",
            "nature.com",
            "science.org",
            "cell.com",
            "nih.gov"
        ]
    }
    
    web_search: WebSearchConfig = {
        "enabled": True,
        "max_searches": 3,
        "filters": filters
    }
    
    print("\n📈 Research Topic: mRNA Vaccine Technology Evolution")
    print("   Turns: 3")
    
    # Turn 1: Early foundations
    print("\n" + "-"*80)
    print("🔍 TURN 1: Early Foundations (1990s-2010s)")
    print("-"*80)
    
    history.add_user(
        "Research the early foundational work on mRNA vaccines from the 1990s through 2010s. "
        "Who were the key researchers and what were the major breakthroughs?"
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    async for event in client.responses.stream(
        messages=history,
        model="claude-sonnet-4-5-latest",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "tool_request" and event.get("name") == "web_search":
            print("\n[Researching early mRNA work...]", end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
    
    # Turn 2: COVID acceleration
    print("\n" + "-"*80)
    print("🔍 TURN 2: COVID-19 Era (2020-2022)")
    print("-"*80)
    
    history.add_user(
        "How did COVID-19 accelerate mRNA vaccine development? "
        "What were the unprecedented achievements and current applications beyond COVID?"
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    async for event in client.responses.stream(
        messages=history,
        model="claude-sonnet-4-5-latest",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "tool_request" and event.get("name") == "web_search":
            print("\n[Researching COVID developments...]", end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
    
    # Turn 3: Timeline
    print("\n" + "-"*80)
    print("📊 TURN 3: Complete Timeline & Future")
    print("-"*80)
    
    history.add_user(
        "Create a comprehensive timeline of mRNA vaccine evolution with key milestones. "
        "Include predictions for the next 5 years based on current research directions."
    )
    
    print("\n🤖 Assistant: ", end="", flush=True)
    
    async for event in client.responses.stream(
        messages=history,
        model="claude-sonnet-4-5-latest",
        web_search=web_search
    ):
        if event.get("type") == "text":
            print(event["delta"], end="", flush=True)
        elif event.get("type") == "complete":
            print("\n")
            history.add_assistant(event)
    
    print(f"\n✅ Longitudinal study completed: {len(history.get_messages()) // 2} turns")


# ============================================================================
# Main - Run All Examples
# ============================================================================

async def main():
    """Run all deep research examples."""
    print("\n" + "="*80)
    print("DEEP RESEARCH WITH ANTHROPIC WEB SEARCH")
    print("="*80)
    print("\nDemonstrates comprehensive research workflows using:")
    print("  • Claude Sonnet 4.5 with web-search-20250305")
    print("  • Managed streaming API for real-time results")
    print("  • 3-turn research pattern for focused insights")
    print("  • Academic and technical source filtering")
    
    try:
        await example_01_academic_paper_research()
        await example_02_technical_problem_research()
        await example_03_comparative_analysis()
        await example_04_longitudinal_study()
        
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
    # asyncio.run(example_01_academic_paper_research())
    # asyncio.run(example_02_technical_problem_research())
    # asyncio.run(example_03_comparative_analysis())
    # asyncio.run(example_04_longitudinal_study())
