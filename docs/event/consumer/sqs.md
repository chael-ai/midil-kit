# SQS Consumer

**Location:** `midil/event/consumer/sqs.py`

## Overview

The SQS Consumer provides integration with Amazon Simple Queue Service (SQS) for consuming events from SQS queues. It implements the pull-based consumer strategy with long polling and automatic retry mechanisms.

## Main Classes

### SQSConsumerEventConfig

Configuration class for SQS consumer.

**Attributes:**
- `type`: Consumer type (always "sqs")
- `queue_url`: URL of the SQS queue
- `dlq_url`: Optional URL of the dead-letter queue
- `visibility_timeout`: Visibility timeout in seconds (default: 30)
- `max_number_of_messages`: Max messages to receive per poll (1-10, default: 10)
- `wait_time_seconds`: Wait time for long polling (0-20, default: 20)
- `poll_interval`: Interval between polls if no messages (default: 0.1)
- `backoff_base_delay`: Base delay for backoff in seconds (default: 5)
- `backoff_max_delay`: Max delay for backoff in seconds (default: 300)

**Properties:**
- `region`: Extracted from queue URL
- `dlq_region`: Extracted from DLQ URL (if configured)

### SQSConsumer

SQS consumer implementation that extends PullEventConsumer.

**Key Methods:**
- `ack(message)`: Acknowledge (delete) message from SQS queue
- `nack(message, requeue=True)`: Negative acknowledge with DLQ support
- `_poll_loop()`: Main polling loop for receiving messages
- `_process_message(message)`: Process individual SQS messages

## How It Fits in the Event System

SQS Consumer provides:
1. **AWS Integration**: Native SQS integration with boto3
2. **Long Polling**: Efficient message retrieval with configurable wait times
3. **Dead Letter Queue**: Automatic DLQ support for failed messages
4. **Retry Logic**: Exponential backoff for failed message processing
5. **Batch Processing**: Support for receiving multiple messages per poll
6. **Visibility Timeout**: Configurable message visibility for processing time

## Example Usage

```python
from midil.event.consumer.sqs import SQSConsumer, SQSConsumerEventConfig
from midil.event import EventBus, EventConfig

# Configure SQS consumer
sqs_config = SQSConsumerEventConfig(
    type="sqs",
    queue_url="https://sqs.us-east-1.amazonaws.com/123456789/my-queue",
    dlq_url="https://sqs.us-east-1.amazonaws.com/123456789/my-dlq",
    visibility_timeout=30,
    max_number_of_messages=10,
    wait_time_seconds=20
)

# Create event bus with SQS consumer
config = EventConfig(
    consumers={"worker": sqs_config}
)
bus = EventBus(config)

# Subscribe to events
@bus.subscriber(target="worker")
async def handle_sqs_event(event):
    print(f"Received SQS event: {event.body}")
    # Process the event
    await process_event(event.body)

# Start consuming
await bus.start()
```

## See Also

- [Event Bus](../event_bus.md) - Main event system interface
- [Pull Consumer Strategy](strategies/pull.md) - Pull-based consumer strategy
- [SQS Producer](../producer/sqs.md) - SQS producer implementation
- [Event Message](../message.md) - Message structure
