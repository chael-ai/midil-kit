# EventBus

**Location:** `midil/event/event_bus.py`

## Overview

The `EventBus` is the main interface for event-driven communication in the Midil framework. It provides a unified way to publish events, subscribe to event handlers, and manage the lifecycle of event producers and consumers.

## Main Classes

### EventBusFactory

A factory class for creating event producers, consumers, and their configurations.

**Key Methods:**
- `create_producer(config)`: Creates an EventProducer instance based on configuration
- `create_consumer(config)`: Creates an EventConsumer instance (pull or push) based on configuration  
- `create_config(transport, **kwargs)`: Creates a configuration object for a given transport type

**Supported Producers:** Redis, SQS
**Supported Consumers:** SQS, Webhook

### EventBus

The main event bus class that orchestrates event publishing and consumption.

**Key Methods:**
- `publish(payload, target=None, metadata=None)`: Publish an event to producers
- `subscribe(handler, target=None)`: Register an event subscriber/handler
- `subscriber(target=None, middlewares=None, **kwargs)`: Decorator to register a function as an event subscriber
- `start()`: Start all event consumers
- `stop()`: Stop all event consumers and close producers

## How It Fits in the Event System

The EventBus serves as the central coordinator that:
1. Manages multiple producers and consumers
2. Routes events between producers and consumers
3. Provides a unified API for event operations
4. Handles configuration and lifecycle management

## Example Usage

```python
from midil.event import EventBus, EventConfig
from midil.event.producer.sqs import SQSProducerEventConfig
from midil.event.consumer.sqs import SQSConsumerEventConfig

# Configure the event bus
config = EventConfig(
    producers={
        "main": SQSProducerEventConfig(
            type="sqs",
            queue_url="https://sqs.us-east-1.amazonaws.com/123456789/my-queue"
        )
    },
    consumers={
        "worker": SQSConsumerEventConfig(
            type="sqs", 
            queue_url="https://sqs.us-east-1.amazonaws.com/123456789/my-queue"
        )
    }
)

# Create and use the event bus
bus = EventBus(config)

# Subscribe to events
@bus.subscriber()
async def handle_user_created(event):
    print(f"User created: {event.body}")

# Start consuming
await bus.start()

# Publish an event
await bus.publish({"user_id": 123, "name": "John"}, target="main")
```

## See Also

- [Event Context](context.md) - Event context management
- [Event Config](config.md) - Configuration models
- [Event Exceptions](exceptions.md) - Error handling
- [SQS Consumer](../consumer/sqs.md) - SQS consumer implementation
- [SQS Producer](../producer/sqs.md) - SQS producer implementation
