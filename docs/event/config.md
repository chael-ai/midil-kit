# Event Configuration

**Location:** `midil/event/config.py`

## Overview

The configuration module defines the data models and type definitions for configuring event producers and consumers in the Midil event system.

## Main Classes

### EventConfig

Main configuration model for the EventBus.

**Attributes:**
- `consumers`: Optional named configurations for event consumers
- `producers`: Optional named configurations for event producers

### ProducerConfig

Union type for producer configurations with discriminator field.

**Supported Types:**
- `SQSProducerEventConfig`: SQS producer configuration
- `RedisProducerEventConfig`: Redis producer configuration

### ConsumerConfig

Union type for consumer configurations with discriminator field.

**Supported Types:**
- `SQSConsumerEventConfig`: SQS consumer configuration
- `WebhookConsumerEventConfig`: Webhook consumer configuration

### EventConsumerType

Enum defining supported consumer types:
- `SQS`: Amazon SQS consumer
- `WEBHOOK`: HTTP webhook consumer

### EventProducerType

Enum defining supported producer types:
- `REDIS`: Redis pub/sub producer
- `SQS`: Amazon SQS producer

## How It Fits in the Event System

Configuration models provide:
1. **Type Safety**: Pydantic models with validation
2. **Discriminated Unions**: Automatic type selection based on discriminator fields
3. **Named Configurations**: Support for multiple named producers/consumers
4. **Validation**: Built-in validation for configuration parameters

## Example Usage

```python
from midil.event.config import EventConfig
from midil.event.producer.sqs import SQSProducerEventConfig
from midil.event.consumer.sqs import SQSConsumerEventConfig

# Create event configuration
config = EventConfig(
    producers={
        "main_queue": SQSProducerEventConfig(
            type="sqs",
            queue_url="https://sqs.us-east-1.amazonaws.com/123456789/my-queue"
        )
    },
    consumers={
        "worker": SQSConsumerEventConfig(
            type="sqs",
            queue_url="https://sqs.us-east-1.amazonaws.com/123456789/my-queue",
            visibility_timeout=30,
            max_number_of_messages=10
        )
    }
)

# Use with EventBus
from midil.event import EventBus
bus = EventBus(config)
```

## See Also

- [Event Bus](event_bus.md) - Main event system interface
- [SQS Producer](../producer/sqs.md) - SQS producer configuration
- [SQS Consumer](../consumer/sqs.md) - SQS consumer configuration
- [Redis Producer](../producer/redis.md) - Redis producer configuration
