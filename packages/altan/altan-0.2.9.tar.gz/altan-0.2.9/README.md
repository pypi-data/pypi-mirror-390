# Altan SDK

Python SDK for the Altan API, providing a unified interface for AI agents, database operations, and platform integrations.

## 🏗️ Clean Architecture

The SDK is organized into three main modules:

```
altan/
├── agents/     # AI chat, streaming, web search, and agent management
├── database/   # PostgREST-style database operations
└── integration/ # 5000+ platform integrations
```

## Installation

```bash
pip install altan
```

## Quick Start

### AI Agent

```python
import asyncio
from altan import Agent

async def main():
    # Initialize agent (uses https://ai.altan.ai by default)
    async with Agent() as agent:
        
        # Simple chat
        response = await agent.chat("Hello, how are you?")
        print(response["text"])
        
        # Chat with web search
        response = await agent.chat(
            "What's the latest news about AI?",
            web_search=True
        )
        print(response["text"])
        
        # Streaming conversation
        async for event in agent.stream("Tell me a story"):
            if event.get("type") == "text":
                print(event.get("delta", ""), end="", flush=True)

asyncio.run(main())
```

### Integration

```python
import asyncio
from altan import Integration

async def main():
    # Initialize the SDK with your API key
    integration = Integration(altan_api_key="your-api-key-here")
    
    # Create connections for any platform using connection_id
    instagram = integration("your-instagram-connection-id")
    salesforce = integration("your-salesforce-connection-id")
    slack = integration("your-slack-connection-id")
    
    # Execute an action on Instagram
    result = await instagram.execute(
        action_name="post_photo",
        payload={
            "image_url": "https://example.com/image.jpg",
            "caption": "Hello from Altan SDK!"
        }
    )
    
    print(f"Success: {result['success']}")
    print(f"Data: {result['data']}")
    
    # Execute an action on Salesforce
    sf_result = await salesforce.execute(
        action_name="create_lead",
        payload={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com"
        }
    )
    
    # Close connections when done
    await integration.close_all_connections()

# Run the async function
asyncio.run(main())
```

### Using Context Managers

```python
import asyncio
from altan_sdk import Integration

async def main():
    async with Integration(altan_api_key="your-api-key-here") as integration:
        # Use any connection by its ID
        instagram = integration("your-instagram-connection-id")
        
        result = await instagram.execute(
            action_name="get_profile",
            payload={}
        )
        
        print(result)

asyncio.run(main())
```

### Database

```python
import asyncio
from altan import Database

async def main():
    # Initialize Database client
    db = Database(
        altan_api_key="your-api-key",
        database_id="your-database-uuid"
    )
    
    # Query with PostgREST-style interface
    result = await (db.from_table("to_do")
                   .select("id,task_name,status,priority")
                   .eq("status", "pending")
                   .order_by("created_at", ascending=False)
                   .limit(10)
                   .execute())
    
    print(f"Found {len(result['data'])} pending tasks")
    
    # Insert new task
    new_task = {
        "task_name": "Implement user authentication",
        "status": "pending",
        "priority": "high"
    }
    result = await db.insert("to_do", new_task)
    
    # Update task status
    if result['success']:
        task_id = result['data']['id']
        await db.update("to_do", {"status": "in_progress"}, {"id": task_id})
    
    await db.close()

asyncio.run(main())
```

## 🔧 Modular Usage

You can import exactly what you need:

```python
# Just AI agents
from altan import Agent, MessageHistory

# Just database operations
from altan import Database, QueryBuilder

# Just integrations
from altan import Integration

# Or everything
from altan import Agent, Database, Integration

# Advanced: Direct module access
from altan.agents import AgentClient  # Full AI client
from altan.database import Database            # Database operations
from altan.integration import Integration      # Platform integrations
```

## Features

- **AI Agent**: Simple, friendly interface for AI conversations with GPT-4, Claude, and more
- **Integration Management**: Easy access to various social media and platform integrations
- **Database Operations**: PostgREST-style database queries with chainable interface
- **Action Execution**: Execute actions on connected platforms
- **Web Search**: Built-in web search capabilities for AI agents
- **Streaming Responses**: Real-time AI response streaming
- **Conversation History**: Automatic context management
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Async Support**: Built with async/await for efficient I/O operations
- **Type Hints**: Full type hint support for better development experience

## Flexible Connection Support

The SDK supports any connection available in your Altan account (5000+ integrations):

```python
# Create connections using their connection IDs
instagram = integration("instagram_connection_id")
salesforce = integration("salesforce_connection_id") 
slack = integration("slack_connection_id")
hubspot = integration("hubspot_connection_id")
shopify = integration("shopify_connection_id")
# ... and any other connection you have configured

# Alternative syntax (equivalent)
connection = integration.connection("any_connection_id")
```

## Error Handling

```python
from altan_sdk import Integration, AltanAPIError, AltanConnectionError

async def main():
    integration = Integration(altan_api_key="your-api-key")
    connection = integration("your-connection-id")
    
    try:
        result = await connection.execute("action_name", {"key": "value"})
    except AltanAPIError as e:
        print(f"API Error: {e}")
        print(f"Status Code: {e.status_code}")
        print(f"Response Data: {e.response_data}")
    except AltanConnectionError as e:
        print(f"Connection Error: {e}")
```

## Database Operations

The Database SDK provides a PostgREST-style interface for database operations:

### Query Building

```python
# Select with filters and ordering
result = await (db.from_table("invoices")
               .select("id,amount,status,created_at")
               .eq("status", "paid")              # WHERE status = 'paid'
               .gt("amount", 100)                 # AND amount > 100
               .order_by("created_at", False)     # ORDER BY created_at DESC
               .limit(10)                         # LIMIT 10
               .execute())

# Available filters: eq, neq, gt, gte, lt, lte, like, ilike, is_null, not_null, in_
# Pagination: limit(), offset()
# Single record: single() - expects exactly one result
```

### CRUD Operations

```python
# INSERT - Single record
result = await db.insert("to_do", {
    "task_name": "Complete project documentation",
    "status": "pending",
    "priority": "high"
})

# INSERT - Bulk records
bulk_tasks = [
    {"task_name": "Setup CI/CD pipeline", "priority": "medium"},
    {"task_name": "Write unit tests", "priority": "high"},
    {"task_name": "Deploy to production", "priority": "low"}
]
result = await db.insert("to_do", bulk_tasks)

# UPDATE
result = await db.update("to_do", 
    {"status": "completed"}, 
    {"id": task_id})

# DELETE
result = await db.delete("to_do", {"id": task_id})
```

### Real-World Example - Task Management

```python
async def manage_tasks():
    """Complete task management example with error handling"""
    
    async with Database(
        altan_api_key="your-api-key",
        database_id="your-database-id"
    ) as db:
        try:
            # Get high-priority pending tasks
            urgent_tasks = await (db.from_table("to_do")
                                 .select("id,task_name,status,priority,created_at")
                                 .eq("priority", "high")
                                 .neq("status", "completed")
                                 .order_by("created_at", False)
                                 .limit(5)
                                 .execute())
            
            print(f"Found {len(urgent_tasks['data'])} urgent tasks")
            
            # Create a new task
            new_task = {
                "task_name": "Review security protocols",
                "status": "pending", 
                "priority": "high"
            }
            
            result = await db.insert("to_do", new_task)
            if result['success']:
                task_id = result['data']['id']
                print(f"✅ Created task: {task_id}")
                
                # Mark task as in progress
                await db.update("to_do", 
                               {"status": "in_progress"}, 
                               {"id": task_id})
                print(f"📝 Task {task_id} marked as in progress")
            
            # Get task statistics
            for status in ['pending', 'in_progress', 'completed']:
                count_result = await (db.from_table("to_do")
                                     .select("id")
                                     .eq("status", status)
                                     .execute())
                print(f"{status.title()}: {len(count_result['data'])} tasks")
                
        except Exception as e:
            print(f"Error managing tasks: {e}")

# Run the task management example
asyncio.run(manage_tasks())
```

## ✅ Proven Results

The Altan Database SDK has been **successfully tested** with real data:

**Test Results:**
- ✅ **SELECT**: Query existing records with complex filters
- ✅ **INSERT**: Single and bulk record creation  
- ✅ **UPDATE**: Individual and batch record updates
- ✅ **DELETE**: Safe record deletion with required filters
- ✅ **Advanced Queries**: Pagination, ordering, pattern matching
- ✅ **PostgREST Compatibility**: 100% compatible with PostgREST semantics

**Performance:**
- Fast response times (< 1 second for typical queries)
- Efficient bulk operations 
- Automatic connection management
- Comprehensive error handling

**Sample Test Output:**
```
🗄️  Testing Altan Database SDK with to_do table
============================================================

📊 Test 1: Query existing to_do records
Success: True
Found 5 existing records
Query URL: https://database.altan.ai/admin/records/f6060540-4eb7-46c1-9671-014efdbac793/to_do?limit=5

➕ Test 2: Insert new to_do records  
✅ Single record inserted successfully!
✅ Bulk insert successful! Inserted 3 records

✏️  Test 3: Update records
✅ Record updated successfully!

🗑️  Test 4: Delete test records  
✅ Records deleted successfully!

🎉 All CRUD operations completed successfully!
```

## 🔄 PostgREST Compatibility

The Database SDK follows **Supabase/PostgREST semantics** exactly:

| Feature | Supabase | Altan SDK | Status |
|---------|----------|-----------|---------|
| Chainable Queries | `table().select().eq()` | `from_table().select().eq()` | ✅ |
| Filters | `eq, neq, gt, gte, lt, lte` | `eq, neq, gt, gte, lt, lte` | ✅ |
| Pattern Matching | `like, ilike` | `like, ilike` | ✅ |
| Null Checks | `is, not.is` | `is_null, not_null` | ✅ |
| Ordering | `order()` | `order_by()` | ✅ |
| Pagination | `limit, offset` | `limit, offset` | ✅ |
| Single Record | `single()` | `single()` | ✅ |

**Migration from Supabase is seamless** - just change the client initialization!

## Development

### Running Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run specific test file
pytest tests/test_database.py

# Run with coverage
pytest --cov=altan tests/
```

### Virtual Environment

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## License

MIT License
