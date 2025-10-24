# Event Context

**Location:** `midil/event/context.py`

## Overview

The `EventContext` provides context management for event processing, allowing you to track event metadata and maintain context across async operations using Python's `contextvars`.

## Main Classes and Functions

### EventContext

A context object that holds event metadata and parent relationships.

**Attributes:**
- `id`: Unique identifier for the event
- `event_type`: Type of the event
- `parent`: Optional parent EventContext for nested events

### get_current_event()

Retrieves the current event context from the context variable. Returns `None` if no context is set.

### event_context(event_type, id=None, parent_override=NOTSET)

Async context manager that sets a new EventContext for the current execution scope.

**Parameters:**
- `event_type`: Type of the event
- `id`: Optional event ID (generates UUID if not provided)
- `parent_override`: Explicit parent context to use, or omit to use current context if available

## How It Fits in the Event System

Event context provides:
1. **Event Tracking**: Maintains event metadata across async operations
2. **Nested Events**: Supports parent-child relationships for event hierarchies
3. **Context Isolation**: Uses contextvars for thread-safe context management
4. **Event Correlation**: Enables tracing and debugging of event flows

## Example Usage

```python
from midil.event.context import event_context, get_current_event

# Using the context manager
async def process_user_event():
    async with event_context("user.created", id="user-123") as ctx:
        print(f"Processing event: {ctx.id} of type {ctx.event_type}")
        
        # Nested event with parent relationship
        async with event_context("user.notification", parent_override=ctx) as child_ctx:
            print(f"Child event: {child_ctx.id}, parent: {child_ctx.parent.id}")
            
            # Get current context anywhere in the call stack
            current = get_current_event()
            print(f"Current event: {current.id}")

# Manual context access
async def some_handler():
    current_event = get_current_event()
    if current_event:
        print(f"Handling event: {current_event.id}")
    else:
        print("No event context available")
```

## See Also

- [Event Bus](event_bus.md) - Main event system interface
- [Event Message](message.md) - Message structure
- [Event Exceptions](exceptions.md) - Error handling
