# Subscriber Base

**Location:** `midil/event/subscriber/base.py`

## Overview

The subscriber base module defines the abstract base classes and interfaces for event subscribers in the Midil event system. It provides the foundation for implementing event handlers with middleware support.

## Main Classes

### EventSubscriber

Abstract base class for event subscribers.

**Key Methods:**
- `handle(event)`: Abstract method to handle incoming events
- `authorize(event)`: Optional authorization check (default: True)
- `should_handle(event)`: Optional event validation (default: True)
- `on_error(event, error)`: Error handling hook
- `on_success(event)`: Success handling hook
- `__call__(event)`: Orchestrates the event handling lifecycle

### SubscriberMiddleware

Abstract base class for subscriber middlewares.

**Key Methods:**
- `__call__(event, call_next)`: Process event through middleware chain

### FunctionSubscriber

A subscriber that wraps a function handler with middleware chain.

**Key Methods:**
- `handle(event)`: Apply middlewares to the handler function

**Attributes:**
- `handler`: The function to handle the event
- `middlewares`: List of SubscriberMiddleware instances

## How It Fits in the Event System

Subscriber base provides:
1. **Event Handling**: Abstract interface for event processing
2. **Middleware Support**: Chainable middleware for event processing
3. **Lifecycle Hooks**: Error handling and success callbacks
4. **Authorization**: Built-in authorization support
5. **Validation**: Event validation before processing
6. **Function Wrapping**: Easy function-to-subscriber conversion

## Example Usage

### Basic Event Subscriber

```python
from midil.event.subscriber.base import EventSubscriber
from midil.event.message import Message

class UserEventHandler(EventSubscriber):
    async def handle(self, event: Message) -> None:
        """Handle user events"""
        print(f"Processing user event: {event.body}")
        # Your event processing logic here
    
    async def authorize(self, event: Message) -> bool:
        """Check if event is authorized"""
        return event.metadata.get("authorized", False)
    
    async def should_handle(self, event: Message) -> bool:
        """Validate event before processing"""
        return event.body.get("user_id") is not None
    
    async def on_error(self, event: Message, error: Exception) -> None:
        """Handle processing errors"""
        print(f"Error processing event {event.id}: {error}")
    
    async def on_success(self, event: Message) -> None:
        """Handle successful processing"""
        print(f"Successfully processed event {event.id}")

# Usage
handler = UserEventHandler()
await handler(event)
```

### Function Subscriber with Middleware

```python
from midil.event.subscriber.base import FunctionSubscriber, SubscriberMiddleware
from midil.event.message import Message

# Custom middleware
class LoggingMiddleware(SubscriberMiddleware):
    async def __call__(self, event: Message, call_next):
        print(f"Processing event: {event.id}")
        result = await call_next(event)
        print(f"Finished processing: {event.id}")
        return result

# Event handler function
async def handle_user_created(event: Message):
    print(f"User created: {event.body}")

# Create function subscriber with middleware
subscriber = FunctionSubscriber(
    handler=handle_user_created,
    middlewares=[LoggingMiddleware()]
)

# Use the subscriber
await subscriber(event)
```

### Decorator Usage

```python
from midil.event import EventBus
from midil.event.subscriber.base import FunctionSubscriber, SubscriberMiddleware

# Custom middleware
class RetryMiddleware(SubscriberMiddleware):
    async def __call__(self, event: Message, call_next):
        for attempt in range(3):
            try:
                return await call_next(event)
            except Exception as e:
                if attempt == 2:
                    raise e
                print(f"Retry {attempt + 1} for event {event.id}")

# Create event bus
bus = EventBus()

# Subscribe with middleware
@bus.subscriber(middlewares=[RetryMiddleware()])
async def handle_event(event):
    print(f"Handling event: {event.body}")
    # Your processing logic
```

## See Also

- [Subscriber Middlewares](middlewares.md) - Built-in middleware implementations
- [Event Bus](../event_bus.md) - Main event system interface
- [Event Message](../message.md) - Message structure
