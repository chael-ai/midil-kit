# Consumer Strategies - Base

**Location:** `midil/event/consumer/strategies/base.py`

## Overview

The base consumer strategy module defines the abstract base classes and core interfaces for event consumers in the Midil event system. It provides the foundation for both pull-based and push-based consumer implementations.

## Main Classes

### ConsumerMessage

Extended message class for consumer-specific functionality.

**Attributes:**
- Inherits all attributes from `Message`
- `ack_handle`: Token or handle required to ack/nack/delete the message

### BaseConsumerConfig

Base configuration model for event consumers.

**Attributes:**
- `type`: Type of the consumer configuration (validated with regex pattern)

### EventConsumer

Abstract base class for event consumers.

**Key Methods:**
- `subscribe(subscriber)`: Register an event subscriber
- `unsubscribe(subscriber)`: Remove an event subscriber
- `dispatch(message)`: Dispatch events to all registered subscribers
- `start()`: Begin consuming events (abstract)
- `stop()`: Stop consuming events (abstract)
- `ack(message)`: Acknowledge message receipt (abstract)
- `nack(message, requeue=False)`: Negative acknowledge message (abstract)

**Attributes:**
- `_subscribers`: Set of registered event subscribers
- `_config`: Consumer configuration
- `_subscription_lock`: Thread lock for subscription management

## How It Fits in the Event System

Base consumer strategy provides:
1. **Abstract Interface**: Common interface for all consumer types
2. **Subscriber Management**: Thread-safe subscriber registration/removal
3. **Event Dispatching**: Concurrent event processing to subscribers
4. **Error Handling**: Retryable vs non-retryable error classification
5. **Lifecycle Management**: Start/stop methods for consumer lifecycle
6. **Message Acknowledgment**: ACK/NACK support for message processing

## Example Usage

```python
from midil.event.consumer.strategies.base import EventConsumer, BaseConsumerConfig
from midil.event.message import Message

class CustomConsumer(EventConsumer):
    def __init__(self, config: BaseConsumerConfig):
        super().__init__(config)
        self.running = False
    
    async def start(self):
        """Start consuming events"""
        self.running = True
        # Start your consumer logic here
        pass
    
    async def stop(self):
        """Stop consuming events"""
        self.running = False
        # Cleanup logic here
        pass
    
    async def ack(self, message: Message):
        """Acknowledge message processing"""
        # Implement acknowledgment logic
        pass
    
    async def nack(self, message: Message, requeue: bool = False):
        """Negative acknowledge message"""
        # Implement negative acknowledgment logic
        pass

# Usage
config = BaseConsumerConfig(type="custom")
consumer = CustomConsumer(config)

# Subscribe to events
@consumer.subscribe
async def handle_event(event):
    print(f"Received event: {event.body}")

# Start consuming
await consumer.start()
```

## See Also

- [Pull Consumer Strategy](pull.md) - Pull-based consumer implementation
- [Push Consumer Strategy](push.md) - Push-based consumer implementation
- [Event Bus](../event_bus.md) - Main event system interface
- [Event Message](../message.md) - Message structure
