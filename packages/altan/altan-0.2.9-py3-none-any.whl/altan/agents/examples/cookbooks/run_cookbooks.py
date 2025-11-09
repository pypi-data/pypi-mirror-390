"""
SDK Cookbooks Runner

Interactive menu to run individual cookbooks or all of them in sequence.
"""

import asyncio
import sys
import os
import importlib.util
from typing import List, Dict, Any, Optional


# ANSI colors
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    BLUE = "\033[34m"


# Cookbook definitions
COOKBOOKS = [
    # Managed API (Recommended) - Start here!
    {
        "id": "0",
        "file": "00_api_comparison.py",
        "title": "API Comparison (START HERE)",
        "description": "Compare all 3 API levels side-by-side",
        "tags": ["beginner", "overview", "comparison"],
    },
    {
        "id": "1m",
        "file": "01_basic_chat_managed.py",
        "title": "Basic Chat (Managed API)",
        "description": "Simple chat with managed API - ultra-easy!",
        "tags": ["beginner", "managed", "recommended"],
    },
    {
        "id": "2m",
        "file": "02_function_calling_managed.py",
        "title": "Function Calling (Managed API)",
        "description": "Easy tool usage with ToolRegistry and auto-execution",
        "tags": ["beginner", "managed", "tools", "recommended"],
    },
    # Low-Level API (Advanced)
    {
        "id": 1,
        "file": "01_basic_chat.py",
        "title": "Basic Multi-Turn Chat (Low-Level)",
        "description": "Manual event handling and part collection",
        "tags": ["advanced", "low-level", "streaming"],
    },
    {
        "id": 2,
        "file": "02_function_calling.py",
        "title": "Function Calling (Low-Level)",
        "description": "Manual tool execution and part management",
        "tags": ["advanced", "low-level", "tools"],
    },
    {
        "id": "3b",
        "file": "03b_rich_message_format.py",
        "title": "Rich Message Format & Parts",
        "description": "Proper message part collection and RichMessage usage",
        "tags": ["intermediate", "message-parts", "rich-format"],
    },
    {
        "id": 4,
        "file": "04_multi_agent_collaboration.py",
        "title": "Multi-Agent Collaboration",
        "description": "Multiple agents working together",
        "tags": ["advanced", "multi-agent", "collaboration"],
    },
    {
        "id": 5,
        "file": "05_multi_user_conversations.py",
        "title": "Multi-User Conversations",
        "description": "Multiple users with member_id tracking",
        "tags": ["intermediate", "multi-user", "member-id"],
    },
    {
        "id": 6,
        "file": "06_code_assistant.py",
        "title": "Code Assistant",
        "description": "Code generation, review, and refinement",
        "tags": ["intermediate", "code-gen", "iteration"],
    },
    {
        "id": 7,
        "file": "07_web_search.py",
        "title": "Web Search (OpenAI & Anthropic)",
        "description": "Citations, sources, actions, multi-turn research",
        "tags": ["intermediate", "web-search", "research"],
    },
    {
        "id": 8,
        "file": "08_deep_research_anthropic.py",
        "title": "Deep Research with Anthropic",
        "description": "Academic papers, technical analysis, comparative studies",
        "tags": ["advanced", "research", "anthropic", "managed", "new"],
    },
    {
        "id": "9a",
        "file": "09_deep_research_openai.py",
        "title": "Deep Research with OpenAI",
        "description": "Market research, location-aware, real-time events",
        "tags": ["advanced", "research", "openai", "managed", "new"],
    },
    {
        "id": 9,
        "file": "09_parallel_requests.py",
        "title": "Parallel & Concurrent Requests",
        "description": "Batch processing and concurrent execution",
        "tags": ["advanced", "async", "performance"],
    },
    {
        "id": 10,
        "file": "10_advanced_streaming.py",
        "title": "Advanced Streaming Patterns",
        "description": "All 16 event types, typing indicators, partial rendering",
        "tags": ["advanced", "streaming", "events"],
    },
]


def print_banner() -> None:
    """Print the welcome banner."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'═' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}   SDK Cookbooks - Interactive Demo Runner{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'═' * 80}{Colors.RESET}\n")
    print(f"{Colors.BLUE}Practical examples showcasing SDK capabilities{Colors.RESET}")
    print(f"{Colors.BLUE}OpenAI Cookbook style - real-world scenarios{Colors.RESET}")
    print()
    print(f"{Colors.GREEN}💡 New to the SDK? Start with cookbook 0 (API Comparison)!{Colors.RESET}\n")


def print_menu() -> None:
    """Print the cookbook selection menu."""
    print(f"{Colors.BOLD}{Colors.GREEN}Available Cookbooks:{Colors.RESET}\n")
    
    # Group cookbooks
    managed_cookbooks = [c for c in COOKBOOKS if "managed" in c["tags"] or "comparison" in c["tags"]]
    low_level_cookbooks = [c for c in COOKBOOKS if "low-level" in c["tags"]]
    other_cookbooks = [c for c in COOKBOOKS if c not in managed_cookbooks and c not in low_level_cookbooks]
    
    # Print managed API section
    if managed_cookbooks:
        print(f"{Colors.BOLD}{Colors.CYAN}  Managed API (Recommended - Start Here):{Colors.RESET}")
        for cookbook in managed_cookbooks:
            tags_str = ", ".join(cookbook["tags"])
            print(f"  {Colors.BOLD}{cookbook['id']}.{Colors.RESET} {cookbook['title']}")
            print(f"     {Colors.BLUE}{cookbook['description']}{Colors.RESET}")
            print(f"     Tags: {Colors.YELLOW}{tags_str}{Colors.RESET}")
            print()
    
    # Print low-level API section
    if low_level_cookbooks:
        print(f"{Colors.BOLD}{Colors.CYAN}  Low-Level API (Advanced - Maximum Control):{Colors.RESET}")
        for cookbook in low_level_cookbooks:
            tags_str = ", ".join(cookbook["tags"])
            print(f"  {Colors.BOLD}{cookbook['id']}.{Colors.RESET} {cookbook['title']}")
            print(f"     {Colors.BLUE}{cookbook['description']}{Colors.RESET}")
            print(f"     Tags: {Colors.YELLOW}{tags_str}{Colors.RESET}")
            print()
    
    # Print other cookbooks
    if other_cookbooks:
        print(f"{Colors.BOLD}{Colors.CYAN}  Other Examples:{Colors.RESET}")
        for cookbook in other_cookbooks:
            tags_str = ", ".join(cookbook["tags"])
            print(f"  {Colors.BOLD}{cookbook['id']}.{Colors.RESET} {cookbook['title']}")
            print(f"     {Colors.BLUE}{cookbook['description']}{Colors.RESET}")
            print(f"     Tags: {Colors.YELLOW}{tags_str}{Colors.RESET}")
            print()
    
    print(f"  {Colors.BOLD}A.{Colors.RESET} Run All Cookbooks")
    print(f"  {Colors.BOLD}Q.{Colors.RESET} Quit\n")


def get_user_choice() -> str:
    """Get user's menu selection."""
    choice = input(f"{Colors.GREEN}Select a cookbook (0, 1m, 2m, 1, 2, ..., A, Q):{Colors.RESET} ").strip().upper()
    return choice


async def run_cookbook(cookbook: Dict[str, Any]) -> bool:
    """Run a single cookbook."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'─' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}Running: {cookbook['title']}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'─' * 80}{Colors.RESET}\n")
    
    # Import and run the cookbook
    file_path = os.path.join(os.path.dirname(__file__), cookbook["file"])
    
    if not os.path.exists(file_path):
        print(f"{Colors.RED}✗ File not found: {cookbook['file']}{Colors.RESET}")
        return False
    
    try:
        # Load the module
        spec = importlib.util.spec_from_file_location(f"cookbook_{cookbook['id']}", file_path)
        if spec is None or spec.loader is None:
            print(f"{Colors.RED}✗ Could not load cookbook{Colors.RESET}")
            return False
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Run the main function
        if hasattr(module, "main"):
            await module.main()
        else:
            # Look for run functions
            for attr_name in dir(module):
                if attr_name.startswith("run_") and callable(getattr(module, attr_name)):
                    func = getattr(module, attr_name)
                    if asyncio.iscoroutinefunction(func):
                        await func()
                    else:
                        func()
        
        print(f"\n{Colors.GREEN}✓ Cookbook completed successfully{Colors.RESET}")
        return True
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠ Cookbook interrupted by user{Colors.RESET}")
        return False
    except Exception as e:
        print(f"\n{Colors.RED}✗ Error running cookbook: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_cookbooks() -> None:
    """Run all cookbooks in sequence."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}Running all cookbooks...{Colors.RESET}\n")
    
    results = []
    
    for i, cookbook in enumerate(COOKBOOKS, 1):
        print(f"{Colors.BOLD}[{i}/{len(COOKBOOKS)}]{Colors.RESET} ", end="")
        success = await run_cookbook(cookbook)
        results.append((cookbook["title"], success))
        
        if not success:
            choice = input(f"\n{Colors.YELLOW}Continue to next cookbook? (Y/n):{Colors.RESET} ").strip().lower()
            if choice == 'n':
                break
        
        if i < len(COOKBOOKS):
            print(f"\n{Colors.BLUE}{'─' * 80}{Colors.RESET}")
            await asyncio.sleep(1)  # Brief pause between cookbooks
    
    # Summary
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'═' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}Summary - All Cookbooks{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'═' * 80}{Colors.RESET}\n")
    
    success_count = sum(1 for _, success in results if success)
    
    for title, success in results:
        status = f"{Colors.GREEN}✓" if success else f"{Colors.RED}✗"
        print(f"  {status} {title}{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}Result: {success_count}/{len(results)} cookbooks completed successfully{Colors.RESET}\n")


async def interactive_mode() -> None:
    """Run the interactive menu."""
    print_banner()
    
    while True:
        print_menu()
        choice = get_user_choice()
        
        if choice == 'Q':
            print(f"\n{Colors.GREEN}Thanks for exploring the SDK cookbooks!{Colors.RESET}\n")
            break
        
        elif choice == 'A':
            await run_all_cookbooks()
            input(f"\n{Colors.BLUE}Press Enter to return to menu...{Colors.RESET}")
        
        else:
            # Try to find cookbook by ID (supports both int and string IDs)
            cookbook = None
            
            # First try exact string match
            cookbook = next((c for c in COOKBOOKS if str(c["id"]).upper() == choice), None)
            
            # If not found and choice is a digit, try int match
            if not cookbook and choice.isdigit():
                cookbook_id = int(choice)
                cookbook = next((c for c in COOKBOOKS if c["id"] == cookbook_id), None)
            
            if cookbook:
                await run_cookbook(cookbook)
                input(f"\n{Colors.BLUE}Press Enter to return to menu...{Colors.RESET}")
            else:
                print(f"{Colors.RED}Invalid cookbook ID: {choice}{Colors.RESET}\n")


def main() -> None:
    """Main entry point."""
    try:
        if len(sys.argv) > 1:
            # Command-line mode
            arg = sys.argv[1].upper()
            
            if arg == 'ALL':
                asyncio.run(run_all_cookbooks())
            else:
                # Try to find cookbook by ID (supports both int and string IDs)
                cookbook = None
                
                # First try exact string match
                cookbook = next((c for c in COOKBOOKS if str(c["id"]).upper() == arg), None)
                
                # If not found and arg is a digit, try int match
                if not cookbook and arg.isdigit():
                    cookbook_id = int(arg)
                    cookbook = next((c for c in COOKBOOKS if c["id"] == cookbook_id), None)
                
                if cookbook:
                    asyncio.run(run_cookbook(cookbook))
                else:
                    print(f"{Colors.RED}Invalid cookbook ID: {arg}{Colors.RESET}")
                    print(f"{Colors.YELLOW}Usage: python run_cookbooks.py [0|1M|2M|1|2|...|ALL]{Colors.RESET}")
        else:
            # Interactive mode
            asyncio.run(interactive_mode())
    
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Exiting...{Colors.RESET}\n")


if __name__ == "__main__":
    main()

