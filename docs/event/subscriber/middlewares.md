# Subscriber Middlewares

**Location:** `midil/event/subscriber/middlewares.py`

## Overview

The middlewares module provides built-in middleware implementations for event subscribers, including grouping, retry logic, and logging functionality.

## Main Classes

### GroupMiddleware

Middleware that runs multiple middlewares in parallel.

**Key Methods:**
- `__call__(event, call_next)`: Execute middlewares in parallel

**Attributes:**
- `middlewares`: List of SubscriberMiddleware instances
- `fail_fast`: Whether to stop on first failure

### RetryMiddleware

Middleware that applies retry logic to event handlers.

**Key Methods:**
- `__call__(event, call_next)`: Apply retry policy to handler

**Attributes:**
- `func`: Retry policy function

### LoggingMiddleware

Middleware that provides logging for event processing.

**Key Methods:**
- `__call__(event, call_next)`: Log event processing lifecycle

## How It Fits in the Event System

Subscriber middlewares provide:
1. **Parallel Execution**: Run multiple middlewares concurrently
2. **Retry Logic**: Automatic retry for failed event processing
3. **Logging**: Comprehensive logging for event processing
4. **Error Handling**: Graceful error handling and recovery
5. **Performance**: Optimized parallel processing
6. **Debugging**: Enhanced debugging capabilities

## Example Usage

### Group Middleware

```python
from midil.event.subscriber.middlewares import GroupMiddleware, LoggingMiddleware
from midil.event.subscriber.base import SubscriberMiddleware
from midil.event.message import Message

# Custom middleware
class MetricsMiddleware(SubscriberMiddleware):
    async def __call__(self, event: Message, call_next):
        print(f"Recording metrics for event: {event.id}")
        result = await call_next(event)
        print(f"Metrics recorded for event: {event.id}")
        return result

# Create group middleware
group = GroupMiddleware(
    middlewares=[
        LoggingMiddleware(),
        MetricsMiddleware()
    ],
    fail_fast=True  # Stop on first failure
)

# Use with function subscriber
from midil.event.subscriber.base import FunctionSubscriber

async def handle_event(event):
    print(f"Processing event: {event.body}")

subscriber = FunctionSubscriber(
    handler=handle_event,
    middlewares=[group]
)
```

### Retry Middleware

```python
from midil.event.subscriber.middlewares import RetryMiddleware
from midil.utils.retry import ExponentialBackoffPolicy
from midil.event.subscriber.base import FunctionSubscriber

# Create retry policy
retry_policy = ExponentialBackoffPolicy(
    max_attempts=5,
    base_delay=1.0,
    max_delay=60.0
)

# Create retry middleware
retry_middleware = RetryMiddleware(retry_policy)

# Use with function subscriber
async def handle_event(event):
    print(f"Processing event: {event.body}")
    # Your processing logic that might fail

subscriber = FunctionSubscriber(
    handler=handle_event,
    middlewares=[retry_middleware]
)
```

### Logging Middleware

```python
from midil.event.subscriber.middlewares import LoggingMiddleware
from midil.event.subscriber.base import FunctionSubscriber

# Create logging middleware
logging_middleware = LoggingMiddleware()

# Use with function subscriber
async def handle_event(event):
    print(f"Processing event: {event.body}")

subscriber = FunctionSubscriber(
    handler=handle_event,
    middlewares=[logging_middleware]
)
```

### Combined Middleware Chain

```python
from midil.event.subscriber.middlewares import (
    GroupMiddleware, 
    RetryMiddleware, 
    LoggingMiddleware
)
from midil.utils.retry import ExponentialBackoffPolicy
from midil.event.subscriber.base import FunctionSubscriber

# Create retry policy
retry_policy = ExponentialBackoffPolicy(max_attempts=3)

# Create middleware chain
middlewares = [
    LoggingMiddleware(),
    RetryMiddleware(retry_policy),
    GroupMiddleware([
        LoggingMiddleware(),
        # Add more middlewares as needed
    ])
]

# Use with function subscriber
async def handle_event(event):
    print(f"Processing event: {event.body}")

subscriber = FunctionSubscriber(
    handler=handle_event,
    middlewares=middlewares
)
```

### Event Bus Integration

```python
from midil.event import EventBus
from midil.event.subscriber.middlewares import RetryMiddleware, LoggingMiddleware
from midil.utils.retry import ExponentialBackoffPolicy

# Create retry policy
retry_policy = ExponentialBackoffPolicy(max_attempts=5)

# Create event bus
bus = EventBus()

# Subscribe with middleware
@bus.subscriber(middlewares=[
    LoggingMiddleware(),
    RetryMiddleware(retry_policy)
])
async def handle_user_created(event):
    print(f"User created: {event.body}")
    # Your processing logic

# Start the event bus
await bus.start()
```

## See Also

- [Subscriber Base](base.md) - Base subscriber implementation
- [Event Bus](../event_bus.md) - Main event system interface
- [Event Message](../message.md) - Message structure
