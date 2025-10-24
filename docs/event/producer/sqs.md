# SQS Producer

**Location:** `midil/event/producer/sqs.py`

## Overview

The SQS Producer provides integration with Amazon Simple Queue Service (SQS) for publishing events to SQS queues. It implements the EventProducer interface for SQS-based event publishing.

## Main Classes

### SQSProducerEventConfig

Configuration class for SQS producer.

**Attributes:**
- `type`: Producer type (always "sqs")
- `queue_url`: URL of the SQS queue

**Properties:**
- `region`: Extracted from queue URL using utility function

### SQSProducer

SQS producer implementation that extends EventProducer.

**Key Methods:**
- `publish(payload, **kwargs)`: Publish event to SQS queue
- `close()`: Close SQS session (no-op for SQS)

## How It Fits in the Event System

SQS Producer provides:
1. **AWS Integration**: Native SQS integration with boto3
2. **JSON Serialization**: Automatic JSON serialization of event payloads
3. **Region Detection**: Automatic AWS region detection from queue URL
4. **Session Management**: Efficient boto3 session management
5. **Error Handling**: Proper error handling for SQS operations
6. **Scalability**: Support for high-throughput event publishing

## Example Usage

```python
from midil.event.producer.sqs import SQSProducer, SQSProducerEventConfig
from midil.event import EventBus, EventConfig

# Configure SQS producer
sqs_config = SQSProducerEventConfig(
    type="sqs",
    queue_url="https://sqs.us-east-1.amazonaws.com/123456789/my-queue"
)

# Create event bus with SQS producer
config = EventConfig(
    producers={"main": sqs_config}
)
bus = EventBus(config)

# Publish events
await bus.publish(
    {"user_id": 123, "action": "created", "data": {"name": "John"}},
    target="main"
)

# Publish with metadata
await bus.publish(
    {"order_id": 456, "status": "shipped"},
    target="main",
    metadata={"priority": "high", "source": "api"}
)
```

## Direct Usage

```python
from midil.event.producer.sqs import SQSProducer, SQSProducerEventConfig

# Create producer directly
config = SQSProducerEventConfig(
    type="sqs",
    queue_url="https://sqs.us-east-1.amazonaws.com/123456789/my-queue"
)
producer = SQSProducer(config)

# Publish events
await producer.publish({"message": "Hello, SQS!"})
await producer.publish({"data": [1, 2, 3]})

# Cleanup
await producer.close()
```

## See Also

- [Producer Base](base.md) - Base producer implementation
- [SQS Consumer](../consumer/sqs.md) - SQS consumer implementation
- [Event Bus](../event_bus.md) - Main event system interface
- [Event Utils](../utils.md) - Utility functions for SQS
