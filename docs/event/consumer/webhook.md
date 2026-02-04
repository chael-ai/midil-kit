# Webhook Consumer

**Location:** `midil/event/consumer/webhook.py`

## Overview

The Webhook Consumer provides HTTP webhook integration for receiving events via HTTP POST requests. It implements the push-based consumer strategy and integrates with FastAPI for HTTP handling.

## Main Classes

### WebhookMessage

Extended message class for webhook events.

**Attributes:**
- Inherits all attributes from `Message`
- `headers`: Additional HTTP headers from the webhook request

### WebhookConsumerEventConfig

Configuration class for webhook consumer.

**Attributes:**
- `type`: Consumer type (always "webhook")
- `endpoint`: HTTP endpoint path for webhook (default: "/events")

### WebhookConsumer

Webhook consumer implementation that extends PushEventConsumer.

**Key Methods:**
- `entrypoint`: Returns FastAPI APIRouter for integration
- `_handler(request)`: HTTP request handler for webhook events
- `_hash_body(body)`: Generate unique ID from request body
- `start()`: Setup webhook consumer routes
- `stop()`: Clean up webhook consumer
- `ack(message)`: No-op for push mode
- `nack(message, requeue=True)`: No-op for push mode

## How It Fits in the Event System

Webhook Consumer provides:
1. **HTTP Integration**: Native HTTP webhook support
2. **FastAPI Integration**: Seamless integration with FastAPI applications
3. **Request Processing**: Automatic JSON parsing and header extraction
4. **ID Generation**: SHA256 hash-based message IDs for deduplication
5. **Error Handling**: Proper HTTP error responses for failed processing
6. **Push Mode**: Event-driven processing without polling

## Example Usage

```python
from midil.event.consumer.webhook import WebhookConsumer, WebhookConsumerEventConfig
from midil.event import EventBus, EventConfig
from fastapi import FastAPI

# Configure webhook consumer
webhook_config = WebhookConsumerEventConfig(
    type="webhook",
    endpoint="/webhooks/events"
)

# Create event bus with webhook consumer
config = EventConfig(
    consumers={"webhook": webhook_config}
)
bus = EventBus(config)

# Subscribe to webhook events
@bus.subscriber(target="webhook")
async def handle_webhook_event(event):
    print(f"Received webhook: {event.body}")
    print(f"Headers: {event.headers}")
    # Process the webhook event
    await process_webhook(event.body, event.headers)

# Start consuming
await bus.start()

# Integrate with FastAPI
app = FastAPI()
webhook_consumer = bus.consumers["webhook"]
app.include_router(webhook_consumer.entrypoint)

# The webhook will be available at /webhooks/events
```

## See Also

- [Event Bus](../event_bus.md) - Main event system interface
- [Push Consumer Strategy](strategies/push.md) - Push-based consumer strategy
- [WebSocket Consumer](websocket.md) - WebSocket consumer implementation
- [Event Message](../message.md) - Message structure
