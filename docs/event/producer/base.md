# Producer Base

**Location:** `midil/event/producer/base.py`

## Overview

The producer base module defines the abstract base classes and interfaces for event producers in the Midil event system. It provides the foundation for implementing various event publishing backends.

## Main Classes

### BaseProducerConfig

Base configuration model for event producers.

**Attributes:**
- `type`: Type of the producer configuration

### EventProducer

Abstract base class for event producers.

**Key Methods:**
- `publish(payload, **kwargs)`: Asynchronously publish an event (abstract)
- `close()`: Release resources and cleanup (abstract)

## How It Fits in the Event System

Base producer provides:
1. **Abstract Interface**: Common interface for all producer types
2. **Event Publishing**: Standardized event publishing interface
3. **Resource Management**: Proper cleanup and resource management
4. **Extensibility**: Foundation for custom producer implementations
5. **Configuration**: Base configuration model for producer settings
6. **Async Support**: Asynchronous event publishing support

## Example Usage

```python
from midil.event.producer.base import EventProducer, BaseProducerConfig
from midil.event.message import MessageBody

class CustomProducer(EventProducer):
    def __init__(self, config: BaseProducerConfig):
        self.config = config
        # Initialize your producer backend
    
    async def publish(self, payload: MessageBody, **kwargs) -> None:
        """Publish an event to the backend"""
        # Implement your publishing logic
        print(f"Publishing event: {payload}")
        # Send to your event backend
    
    async def close(self) -> None:
        """Cleanup resources"""
        # Implement cleanup logic
        pass

# Usage
config = BaseProducerConfig(type="custom")
producer = CustomProducer(config)

# Publish an event
await producer.publish({"user_id": 123, "action": "created"})

# Cleanup
await producer.close()
```

## See Also

- [SQS Producer](sqs.md) - SQS producer implementation
- [Redis Producer](redis.md) - Redis producer implementation
- [Event Bus](../event_bus.md) - Main event system interface
- [Event Message](../message.md) - Message structure
