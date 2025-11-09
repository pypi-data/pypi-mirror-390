"""
Cookbook 04: Multi-Agent Collaboration

Demonstrates:
- Multiple agents working together
- Agent handoffs with context passing
- Different agents for different tasks
- Aggregating multi-agent outputs
"""

import asyncio
import sys
from typing import List, Dict, Any
from utils import (
    print_header,
    print_section,
    print_message,
    print_agent_action,
    print_success,
    print_info,
    get_client,
    MessageHistory,
)

sys.path.insert(0, "../..")
from agents.types import SimpleMessage


class Agent:
    """Represents an AI agent with specific capabilities."""
    
    def __init__(
        self,
        name: str,
        role: str,
        model: str,
        system_prompt: str,
        temperature: float = 0.7,
    ):
        self.name = name
        self.role = role
        self.model = model
        self.system_prompt = system_prompt
        self.temperature = temperature
    
    async def process(
        self,
        client: Any,
        user_input: str,
        context: str = "",
    ) -> str:
        """Process input and return response."""
        messages: List[SimpleMessage] = [
            SimpleMessage(role="system", content=self.system_prompt),  # type: ignore
        ]
        
        if context:
            messages.append(
                SimpleMessage(role="user", content=f"CONTEXT FROM PREVIOUS AGENT:\n{context}")  # type: ignore
            )
        
        messages.append(SimpleMessage(role="user", content=user_input))  # type: ignore
        
        print_agent_action(
            self.name,
            f"Processing with {self.model}...",
            f"Role: {self.role}",
        )
        
        full_text = ""
        print("  ", end="", flush=True)
        
        try:
            async for event in client.responses.create_stream(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                max_tokens=800,
            ):
                event_type = event.get("event_type", "")
                data = event.get("data", {})
                
                if event_type == "message_part.updated":
                    delta = data.get("delta", "")
                    if delta:
                        full_text += delta
                        print(delta, end="", flush=True)
                
                elif event_type == "response.failed":
                    error_msg = data.get("error_message", "Unknown error")
                    print(f"\n  ❌ Error: {error_msg}")
                    return f"[Error: {error_msg}]"
            
            print("\n")
            return full_text
            
        except Exception as e:
            print(f"\n  ❌ Exception: {e}")
            return f"[Exception: {e}]"


async def run_multi_agent_research_system() -> None:
    """Demonstrate multi-agent collaboration on a research task."""
    
    print_header("Cookbook: Multi-Agent Research System")
    
    print("Scenario: Three specialized agents collaborate to research and write a report\n")
    print("  🔍 Researcher: Gathers and summarizes information")
    print("  📊 Analyst: Identifies patterns and insights")
    print("  ✍️  Writer: Produces polished final output\n")
    
    # Define our agents
    researcher = Agent(
        name="🔍 Researcher",
        role="Information Gatherer",
        model="gpt-4o",
        system_prompt=(
            "You are a research specialist. Your job is to gather and summarize "
            "key information about topics. Be thorough but concise. Focus on facts, "
            "statistics, and important details. Organize information clearly."
        ),
        temperature=0.5,
    )
    
    analyst = Agent(
        name="📊 Analyst",
        role="Pattern Recognition",
        model="gpt-4o",
        system_prompt=(
            "You are an analytical expert. Review the research provided and identify "
            "key patterns, trends, and insights. Highlight what's most important. "
            "Draw connections between different pieces of information. Be critical and insightful."
        ),
        temperature=0.6,
    )
    
    writer = Agent(
        name="✍️  Writer",
        role="Content Producer",
        model="gpt-4o",
        system_prompt=(
            "You are a professional writer. Take the research and analysis provided "
            "and create a well-structured, engaging final report. Use clear language, "
            "good formatting, and compelling narrative. Make it publication-ready."
        ),
        temperature=0.7,
    )
    
    # Research topic
    topic = "The impact of artificial intelligence on healthcare in the next decade"
    
    async with get_client() as client:
        # Step 1: Researcher gathers information
        print_section("Step 1: Research Phase")
        print_message("user", f"Research topic: {topic}")
        
        research_output = await researcher.process(
            client,
            f"Research this topic and provide a comprehensive summary: {topic}",
        )
        print_success(f"Research completed ({len(research_output)} characters)")
        
        # Step 2: Analyst reviews and analyzes
        print_section("Step 2: Analysis Phase")
        print_info("Passing research to analyst...")
        
        analysis_output = await analyst.process(
            client,
            "Analyze the research provided and identify the top 3 most important insights.",
            context=research_output,
        )
        print_success(f"Analysis completed ({len(analysis_output)} characters)")
        
        # Step 3: Writer creates final report
        print_section("Step 3: Writing Phase")
        print_info("Passing research and analysis to writer...")
        
        combined_context = f"RESEARCH:\n{research_output}\n\nANALYSIS:\n{analysis_output}"
        
        final_output = await writer.process(
            client,
            "Create a polished executive summary report (2-3 paragraphs) based on the research and analysis.",
            context=combined_context,
        )
        print_success(f"Final report completed ({len(final_output)} characters)")
        
        # Display final result
        print_section("Final Report")
        print(final_output)
    
    # Summary
    print_section("Collaboration Summary")
    print_success("3 agents collaborated successfully")
    print_success(f"Total output: {len(research_output) + len(analysis_output) + len(final_output)} characters")
    print("\nKey demonstration points:")
    print("  ✓ Sequential agent collaboration")
    print("  ✓ Context passing between agents")
    print("  ✓ Specialized agents for different tasks")
    print("  ✓ Information refinement pipeline")
    print("\nProduction patterns:")
    print("  → Use different models for different agent roles")
    print("  → Adjust temperature per agent personality")
    print("  → Cache intermediate results")
    print("  → Add error handling and retries")


async def run_multi_agent_debate() -> None:
    """Demonstrate agents debating different perspectives."""
    
    print_header("Cookbook: Multi-Agent Debate System")
    
    print("Scenario: Two agents debate different sides of an issue\n")
    
    # Define debating agents
    advocate = Agent(
        name="👍 Advocate",
        role="Pro Side",
        model="gpt-4o",
        system_prompt=(
            "You are debating the PRO side. Make strong, well-reasoned arguments "
            "supporting your position. Be persuasive but fair. Cite examples."
        ),
        temperature=0.7,
    )
    
    critic = Agent(
        name="👎 Critic",
        role="Con Side",
        model="gpt-4o",
        system_prompt=(
            "You are debating the CON side. Make strong, well-reasoned arguments "
            "against the proposition. Be persuasive but fair. Cite examples."
        ),
        temperature=0.7,
    )
    
    moderator = Agent(
        name="⚖️  Moderator",
        role="Moderator",
        model="gpt-4o",
        system_prompt=(
            "You are a debate moderator. Summarize both sides fairly and provide "
            "a balanced conclusion. Don't take sides, but highlight the strongest points."
        ),
        temperature=0.5,
    )
    
    topic = "Remote work should be the default for all software companies"
    
    async with get_client() as client:
        print_section("Debate Topic")
        print(f"  {topic}\n")
        
        # Round 1: Opening statements
        print_section("Round 1: Opening Statements")
        
        pro_arg = await advocate.process(
            client,
            f"Give your opening statement on this debate topic: {topic}",
        )
        
        con_arg = await critic.process(
            client,
            f"Give your opening statement on this debate topic: {topic}",
        )
        
        # Round 2: Rebuttals
        print_section("Round 2: Rebuttals")
        
        pro_rebuttal = await advocate.process(
            client,
            "Provide a rebuttal to the opposition's argument.",
            context=f"Opposition's argument:\n{con_arg}",
        )
        
        con_rebuttal = await critic.process(
            client,
            "Provide a rebuttal to the opposition's argument.",
            context=f"Opposition's argument:\n{pro_arg}",
        )
        
        # Moderation
        print_section("Moderator's Summary")
        
        debate_context = f"""
        PRO OPENING: {pro_arg}
        
        CON OPENING: {con_arg}
        
        PRO REBUTTAL: {pro_rebuttal}
        
        CON REBUTTAL: {con_rebuttal}
        """
        
        summary = await moderator.process(
            client,
            "Provide a balanced summary of this debate and identify the strongest points from each side.",
            context=debate_context,
        )
        
        print_success("Debate completed")
    
    print_section("Summary")
    print("Key demonstration points:")
    print("  ✓ Adversarial multi-agent systems")
    print("  ✓ Context awareness across agents")
    print("  ✓ Structured multi-turn interaction")
    print("  ✓ Neutral moderation agent")


async def main() -> None:
    """Run both multi-agent demonstrations."""
    await run_multi_agent_research_system()
    print("\n" + "="*80 + "\n")
    await run_multi_agent_debate()


if __name__ == "__main__":
    asyncio.run(main())

