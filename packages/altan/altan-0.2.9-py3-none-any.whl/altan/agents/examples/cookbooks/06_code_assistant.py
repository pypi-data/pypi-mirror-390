"""
Cookbook 06: Code Assistant

Demonstrates:
- Code generation with structured output
- Code review with suggestions
- Iterative refinement
- Multi-file code generation
"""

import asyncio
import sys
from typing import List
from utils import (
    print_header,
    print_section,
    print_message,
    print_success,
    print_info,
    print_error,
    print_divider,
    get_client,
    MessageHistory,
)

sys.path.insert(0, "../..")
from agents.types import SimpleMessage


async def run_code_generation() -> None:
    """Demonstrate code generation with iteration."""
    
    print_header("Cookbook: Code Assistant")
    
    print("Scenario: Generate, review, and refine code with AI assistance\n")
    
    # Code generation workflow
    print_section("Step 1: Initial Code Generation")
    
    initial_request = "Write a Python function to calculate Fibonacci numbers using memoization"
    print_message("user", initial_request)
    
    generated_code = ""
    
    async with get_client() as client:
        print_info("Generating code...")
        print("```python")
        
        try:
            async for event in client.responses.create_stream(
                messages=[
                    SimpleMessage(  # type: ignore
                        role="system",
                        content="You are an expert Python developer. Write clean, well-documented code.",
                    ),
                    SimpleMessage(role="user", content=initial_request),  # type: ignore
                ],
                model="gpt-4o",
                temperature=0.3,  # Lower temperature for more deterministic code
                max_tokens=500,
            ):
                event_type = event.get("event_type", "")
                data = event.get("data", {})
                
                if event_type == "message_part.updated":
                    delta = data.get("delta", "")
                    if delta:
                        generated_code += delta
                        print(delta, end="", flush=True)
                
                elif event_type == "response.failed":
                    error_msg = data.get("error_message", "Unknown error")
                    print(f"\n```\n❌ Error: {error_msg}")
                    return
            
            print("\n```\n")
            print_success("Code generated")
        
        except Exception as e:
            print(f"\n```\n❌ Exception: {e}")
            return
        
        # Step 2: Code review
        print_section("Step 2: Code Review")
        
        review_request = f"Review this code and suggest improvements:\n\n{generated_code}"
        print_message("user", "Please review the generated code")
        
        print_info("AI reviewing code...")
        print()
        
        review_comments = ""
        
        try:
            async for event in client.responses.create_stream(
                messages=[
                    SimpleMessage(  # type: ignore
                        role="system",
                        content="You are a code reviewer. Provide constructive feedback on code quality, performance, and best practices.",
                    ),
                    SimpleMessage(role="user", content=review_request),  # type: ignore
                ],
                model="gpt-4o",
                temperature=0.5,
                max_tokens=600,
            ):
                event_type = event.get("event_type", "")
                data = event.get("data", {})
                
                if event_type == "message_part.updated":
                    delta = data.get("delta", "")
                    if delta:
                        review_comments += delta
                        print(delta, end="", flush=True)
                
                elif event_type == "response.failed":
                    error_msg = data.get("error_message", "Unknown error")
                    print(f"\n❌ Error: {error_msg}")
                    return
            
            print("\n")
            print_success("Code review completed")
        
        except Exception as e:
            print(f"\n❌ Exception: {e}")
            return
        
        # Step 3: Refinement
        print_section("Step 3: Code Refinement")
        
        refine_request = f"""Based on the review comments, improve this code:

ORIGINAL CODE:
{generated_code}

REVIEW COMMENTS:
{review_comments}

Please provide the improved version."""
        
        print_message("user", "Please apply the review suggestions")
        
        print_info("Refining code...")
        print("```python")
        
        refined_code = ""
        
        try:
            async for event in client.responses.create_stream(
                messages=[
                    SimpleMessage(  # type: ignore
                        role="system",
                        content="You are an expert Python developer. Apply code review feedback to improve code.",
                    ),
                    SimpleMessage(role="user", content=refine_request),  # type: ignore
                ],
                model="gpt-4o",
                temperature=0.3,
                max_tokens=600,
            ):
                event_type = event.get("event_type", "")
                data = event.get("data", {})
                
                if event_type == "message_part.updated":
                    delta = data.get("delta", "")
                    if delta:
                        refined_code += delta
                        print(delta, end="", flush=True)
                
                elif event_type == "response.failed":
                    error_msg = data.get("error_message", "Unknown error")
                    print(f"\n```\n❌ Error: {error_msg}")
                    return
            
            print("\n```\n")
            print_success("Code refinement completed")
        
        except Exception as e:
            print(f"\n```\n❌ Exception: {e}")
            return
    
    print_section("Summary")
    print("Key demonstration points:")
    print("  ✓ Initial code generation")
    print("  ✓ Automated code review")
    print("  ✓ Iterative refinement")
    print("  ✓ Lower temperature for deterministic code")
    print("\nProduction patterns:")
    print("  → Add syntax validation")
    print("  → Run automated tests")
    print("  → Check for security issues")
    print("  → Generate documentation")


async def run_multi_file_generation() -> None:
    """Demonstrate generating multiple related files."""
    
    print_header("Cookbook: Multi-File Code Generation")
    
    print("Scenario: Generate a complete mini-project with multiple files\n")
    
    project_request = """Create a simple Python REST API with:
1. A main Flask app (app.py)
2. A User model (models.py)
3. API routes (routes.py)

Keep it minimal but production-ready."""
    
    print_section("Project Request")
    print_message("user", project_request)
    
    files_to_generate = [
        ("models.py", "Generate the models.py file with a User model"),
        ("routes.py", "Generate the routes.py file with user CRUD endpoints"),
        ("app.py", "Generate the app.py file that ties everything together"),
    ]
    
    generated_files = {}
    
    async with get_client() as client:
        for filename, prompt in files_to_generate:
            print_section(f"Generating {filename}")
            
            full_prompt = f"""{project_request}

Now generate only the {filename} file. Include imports and make it complete."""
            
            print_info(f"Generating {filename}...")
            print(f"```python\n# {filename}")
            
            file_content = ""
            
            try:
                async for event in client.responses.create_stream(
                    messages=[
                        SimpleMessage(  # type: ignore
                            role="system",
                            content="You are an expert Python/Flask developer. Generate production-ready code with error handling.",
                        ),
                        SimpleMessage(role="user", content=full_prompt),  # type: ignore
                    ],
                    model="gpt-4o",
                    temperature=0.3,
                    max_tokens=800,
                ):
                    event_type = event.get("event_type", "")
                    data = event.get("data", {})
                    
                    if event_type == "message_part.updated":
                        delta = data.get("delta", "")
                        if delta:
                            file_content += delta
                            print(delta, end="", flush=True)
                    
                    elif event_type == "response.failed":
                        error_msg = data.get("error_message", "Unknown error")
                        print(f"\n```\n❌ Error generating {filename}: {error_msg}")
                        file_content = f"# Error: {error_msg}"
                        break
                
                generated_files[filename] = file_content
                print("\n```\n")
                if file_content and not file_content.startswith("# Error:"):
                    print_success(f"{filename} generated ({len(file_content)} characters)")
                else:
                    print_error(f"{filename} generation failed")
            
            except Exception as e:
                print(f"\n```\n❌ Exception: {e}")
                generated_files[filename] = f"# Exception: {e}"
    
    print_section("Project Summary")
    print_success(f"Generated {len(generated_files)} files")
    for filename in generated_files.keys():
        print(f"  ✓ {filename}")
    
    print("\nNext steps:")
    print("  → Save files to disk")
    print("  → Run linting and formatting")
    print("  → Add tests")
    print("  → Generate requirements.txt")


async def main() -> None:
    """Run all code assistant demonstrations."""
    await run_code_generation()
    print("\n" + "="*80 + "\n")
    await run_multi_file_generation()


if __name__ == "__main__":
    asyncio.run(main())

