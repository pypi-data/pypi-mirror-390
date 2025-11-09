"""
Cookbook 05: Multi-User Conversations

Demonstrates:
- Multiple users in same conversation thread
- User context isolation with member_id
- Turn-taking and user identification
- Per-user personalization
"""

import asyncio
import sys
from typing import Dict, List, Any
from dataclasses import dataclass
from utils import (
    print_header,
    print_section,
    print_message,
    print_success,
    print_info,
    get_client,
)

sys.path.insert(0, "../..")
from agents.types import SimpleMessage


@dataclass
class User:
    """Represents a user in the conversation."""
    member_id: str
    name: str
    color_icon: str


async def run_multi_user_chat_room() -> None:
    """Simulate a chatroom with multiple users and an AI assistant."""
    
    print_header("Cookbook: Multi-User Chat Room")
    
    print("Scenario: Group conversation where AI assists multiple users")
    print("The AI tracks context for each user using member_id\n")
    
    # Define users
    users = [
        User(member_id="user_001", name="Alice", color_icon="🔵"),
        User(member_id="user_002", name="Bob", color_icon="🔴"),
        User(member_id="user_003", name="Charlie", color_icon="🟢"),
    ]
    
    # Conversation flow
    conversation = [
        (users[0], "Hi! I'm Alice, a data scientist working on ML models."),
        (users[1], "Hey Alice! I'm Bob, I work in product management."),
        (users[0], "Nice to meet you Bob! What brings you here?"),
        (users[1], "I'm trying to understand how to evaluate ML models for our product."),
        (users[2], "Hi everyone! Charlie here, I'm a backend engineer."),
        (users[0], "Welcome Charlie! Are you working with ML too?"),
        (users[2], "Yes, I need to deploy Alice's models to production."),
        (users[1], "AI Assistant, can you summarize what each person does based on our conversation?"),
    ]
    
    # Shared conversation history
    history: List[SimpleMessage] = [
        SimpleMessage(  # type: ignore
            role="system",
            content=(
                "You are a helpful AI assistant in a group chat. Track each user's "
                "context separately. Remember who said what. Address users by name. "
                "Be friendly and facilitate collaboration."
            ),
        ),
    ]
    
    async with get_client() as client:
        print_section("Group Conversation")
        
        for i, (user, message) in enumerate(conversation, 1):
            print(f"\n{user.color_icon} {user.name} (ID: {user.member_id}):")
            print(f"  {message}")
            
            # Add to history
            history.append(
                SimpleMessage(  # type: ignore
                    role="user",
                    content=f"[{user.name}]: {message}",
                )
            )
            
            # After certain messages, get AI response
            if i % 3 == 0 or i == len(conversation):
                print("\n🤖 AI Assistant:")
                print("  ", end="", flush=True)
                
                full_text = ""
                
                try:
                    # Use member_id to track which user triggered this response
                    async for event in client.responses.create_stream(
                        messages=history,
                        model="gpt-4o",
                        member_id=user.member_id,  # Track who triggered this
                        temperature=0.7,
                        max_tokens=300,
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
                            break
                    
                    print("\n")
                    
                    # Add AI response to history
                    if full_text.strip():
                        history.append(
                            SimpleMessage(role="assistant", content=full_text)  # type: ignore
                        )
                
                except Exception as e:
                    print(f"\n  ❌ Exception: {e}\n")
    
    print_section("Summary")
    print_success(f"Managed conversation with {len(users)} users")
    print_success(f"Total messages: {len(history)}")
    print("\nKey demonstration points:")
    print("  ✓ Multi-user context tracking")
    print("  ✓ User identification with member_id")
    print("  ✓ Shared conversation history")
    print("  ✓ Per-user attribution")


async def run_personalized_responses() -> None:
    """Demonstrate personalized responses based on user context."""
    
    print_header("Cookbook: Personalized User Responses")
    
    print("Scenario: AI provides personalized responses based on user preferences\n")
    
    # Users with different preferences
    users_with_prefs = [
        {
            "user": User(member_id="user_101", name="Emma", color_icon="💜"),
            "preferences": "technical, detailed explanations with code examples",
            "question": "How do I optimize database queries?",
        },
        {
            "user": User(member_id="user_102", name="Frank", color_icon="💛"),
            "preferences": "simple, non-technical explanations with analogies",
            "question": "How do I optimize database queries?",
        },
        {
            "user": User(member_id="user_103", name="Grace", color_icon="🧡"),
            "preferences": "business-focused, ROI and impact oriented",
            "question": "How do I optimize database queries?",
        },
    ]
    
    async with get_client() as client:
        for user_data in users_with_prefs:
            user = user_data["user"]
            prefs = user_data["preferences"]
            question = user_data["question"]
            
            print_section(f"{user.name}'s Personalized Response")
            print_info(f"Preferences: {prefs}")
            print(f"\n{user.color_icon} {user.name}: {question}\n")
            
            # Create personalized system prompt
            messages: List[SimpleMessage] = [
                SimpleMessage(  # type: ignore
                    role="system",
                    content=(
                        f"You are assisting {user.name}. Their communication preference "
                        f"is: {prefs}. Adapt your response style accordingly."
                    ),
                ),
                SimpleMessage(role="user", content=question),  # type: ignore
            ]
            
            print("🤖 AI Assistant:")
            print("  ", end="", flush=True)
            
            full_text = ""
            
            try:
                async for event in client.responses.create_stream(
                    messages=messages,
                    model="gpt-4o",
                    member_id=user.member_id,
                    metadata={"user_preferences": prefs},
                    temperature=0.7,
                    max_tokens=400,
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
                        break
                
                print("\n")
            
            except Exception as e:
                print(f"\n  ❌ Exception: {e}\n")
    
    print_section("Summary")
    print("Key demonstration points:")
    print("  ✓ Per-user customization with member_id")
    print("  ✓ Adaptive response styles")
    print("  ✓ Metadata for user preferences")
    print("  ✓ Same question, different answers")
    print("\nProduction usage:")
    print("  → Store user preferences in database")
    print("  → Load preferences using member_id")
    print("  → Track user interaction patterns")
    print("  → A/B test different response styles")


async def main() -> None:
    """Run all multi-user demonstrations."""
    await run_multi_user_chat_room()
    print("\n" + "="*80 + "\n")
    await run_personalized_responses()


if __name__ == "__main__":
    asyncio.run(main())

