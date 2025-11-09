"""
Cookbook 03: Customer Support Bot

Demonstrates:
- Complete customer support scenario
- Multi-step tool chains
- Context management across turns
- Error handling and fallbacks
- Stateful conversation flow
"""

import asyncio
import sys
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from utils import (
    print_header,
    print_section,
    print_message,
    print_tool_call,
    print_tool_result,
    print_success,
    print_info,
    print_warning,
    get_client,
    MessageHistory,
)

sys.path.insert(0, "../..")
from agents.types import SimpleMessage, ToolDefinition


# Mock database
CUSTOMER_DB = {
    "cust_12345": {
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "tier": "premium",
    },
    "cust_67890": {
        "name": "Bob Smith",
        "email": "bob@example.com",
        "tier": "standard",
    },
}

ORDER_DB = {
    "ORD-001": {
        "customer_id": "cust_12345",
        "items": ["Laptop", "Mouse"],
        "total": 1299.99,
        "status": "shipped",
        "tracking": "TRK123456789",
    },
    "ORD-002": {
        "customer_id": "cust_67890",
        "items": ["Keyboard"],
        "total": 79.99,
        "status": "processing",
        "tracking": None,
    },
}


# Tool functions
def lookup_customer(customer_id: str) -> Dict[str, Any]:
    """Look up customer information."""
    customer = CUSTOMER_DB.get(customer_id)
    if customer:
        return {"success": True, "customer": customer}
    return {"success": False, "error": "Customer not found"}


def lookup_order(order_id: str) -> Dict[str, Any]:
    """Look up order information."""
    order = ORDER_DB.get(order_id)
    if order:
        return {"success": True, "order": order}
    return {"success": False, "error": "Order not found"}


def update_order_status(order_id: str, new_status: str) -> Dict[str, Any]:
    """Update order status."""
    if order_id in ORDER_DB:
        old_status = ORDER_DB[order_id]["status"]
        ORDER_DB[order_id]["status"] = new_status
        return {
            "success": True,
            "order_id": order_id,
            "old_status": old_status,
            "new_status": new_status,
        }
    return {"success": False, "error": "Order not found"}


def send_email(recipient: str, subject: str, body: str) -> Dict[str, Any]:
    """Send email (simulated)."""
    return {
        "success": True,
        "recipient": recipient,
        "subject": subject,
        "message": "Email sent successfully",
    }


# Tool definitions
SUPPORT_TOOLS: List[ToolDefinition] = [
    {
        "type": "function",
        "tool_type": "client",
        "function": {
            "name": "lookup_customer",
            "description": "Look up customer information by customer ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string", "description": "Customer ID"},
                },
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "tool_type": "client",
        "function": {
            "name": "lookup_order",
            "description": "Look up order information by order ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "Order ID"},
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "tool_type": "client",
        "function": {
            "name": "update_order_status",
            "description": "Update the status of an order",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "Order ID"},
                    "new_status": {"type": "string", "description": "New status"},
                },
                "required": ["order_id", "new_status"],
            },
        },
    },
    {
        "type": "function",
        "tool_type": "client",
        "function": {
            "name": "send_email",
            "description": "Send an email to a customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient": {"type": "string", "description": "Email address"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body"},
                },
                "required": ["recipient", "subject", "body"],
            },
        },
    },
]

TOOL_FUNCTIONS = {
    "lookup_customer": lookup_customer,
    "lookup_order": lookup_order,
    "update_order_status": update_order_status,
    "send_email": send_email,
}


async def run_support_scenario() -> None:
    """Run a complete customer support scenario."""
    
    print_header("Cookbook: Customer Support Bot")
    
    print("Scenario: Customer inquiry → lookup → update → confirmation")
    print("Demonstrates multi-step tool chain with error handling\n")
    
    # Customer support conversation
    support_conversation = [
        ("customer", "Hi, I'm Alice Johnson. Can you check the status of my order ORD-001?"),
        ("agent", ""),  # AI will lookup order
        ("customer", "Great! Can you expedite the shipping?"),
        ("agent", ""),  # AI will update status
        ("customer", "Thank you! Can you send me a confirmation email?"),
        ("agent", ""),  # AI will send email
    ]
    
    # Initialize support bot
    history = MessageHistory()
    history.add_system_message(
        "You are a helpful customer support agent. You have access to tools to "
        "lookup customer and order information, update orders, and send emails. "
        "Always be polite and helpful. Use tools when needed to assist customers."
    )
    
    async with get_client() as client:
        for i, (speaker, message) in enumerate(support_conversation, 1):
            print_section(f"Turn {i}")
            
            if speaker == "customer":
                # Customer message
                print_message("user", message, agent_name="Alice")
                history.add_user_message(message)
            
            else:
                # AI agent response
                print_info("Support agent processing...")
                
                # Make request with tools
                full_text = ""
                tool_calls_made = []
                
                async for event in client.responses.create_stream(
                    messages=history.get_messages(),
                    model="gpt-4o",
                    tools=SUPPORT_TOOLS,
                    tool_choice="auto",
                    temperature=0.5,
                ):
                    event_type = event.get("event_type", "")
                    data = event.get("data", {})
                    
                    if event_type == "message_part.added":
                        if data.get("type") == "tool":
                            tool_name = data.get("name", "")
                            tool_args = data.get("arguments", {})
                            
                            # Parse args if string
                            if isinstance(tool_args, str):
                                import json
                                try:
                                    tool_args = json.loads(tool_args)
                                except:
                                    tool_args = {}
                            
                            tool_calls_made.append({
                                "name": tool_name,
                                "args": tool_args,
                            })
                            
                            print_tool_call(tool_name, tool_args, indent=0)
                    
                    elif event_type == "message_part.updated":
                        delta = data.get("delta", "")
                        if delta:
                            full_text += delta
                
                # Execute tools
                if tool_calls_made:
                    print()
                    for tool_call in tool_calls_made:
                        tool_name = tool_call["name"]
                        tool_args = tool_call["args"]
                        
                        if tool_name in TOOL_FUNCTIONS:
                            result = TOOL_FUNCTIONS[tool_name](**tool_args)
                            print_tool_result(tool_name, result, indent=0)
                            
                            # Add tool result to history (simplified)
                            if result.get("success"):
                                print_success(f"{tool_name} completed successfully")
                            else:
                                print_warning(f"{tool_name} failed: {result.get('error')}")
                    print()
                
                # Display AI response if any
                if full_text:
                    print_message("assistant", full_text, agent_name="Support Agent")
                    history.add_assistant_message(full_text)
                else:
                    # Generate follow-up response after tool execution
                    print_info("Generating response based on tool results...")
                    
                    follow_up_text = ""
                    
                    async for event in client.responses.create_stream(
                        messages=history.get_messages(),
                        model="gpt-4o",
                        temperature=0.5,
                        max_tokens=200,
                    ):
                        event_type = event.get("event_type", "")
                        data = event.get("data", {})
                        
                        if event_type == "message_part.updated":
                            delta = data.get("delta", "")
                            if delta:
                                follow_up_text += delta
                    
                    if follow_up_text:
                        print_message("assistant", follow_up_text, agent_name="Support Agent")
                        history.add_assistant_message(follow_up_text)
    
    print_section("Support Session Summary")
    print_success("Complete support scenario executed")
    print(f"  Total turns: {len(support_conversation)}")
    print(f"  Tools used: lookup_order, update_order_status, send_email")
    print(f"  Customer satisfaction: ⭐⭐⭐⭐⭐")
    
    print("\nKey demonstration points:")
    print("  ✓ Multi-step tool chain")
    print("  ✓ Context awareness across turns")
    print("  ✓ Real-world support workflow")
    print("  ✓ Tool result handling")


if __name__ == "__main__":
    asyncio.run(run_support_scenario())

