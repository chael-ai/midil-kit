# WebSocket Consumer

**Location:** `midil/event/consumer/websocket.py`

## Overview

The WebSocket Consumer provides real-time event consumption via WebSocket connections. It implements the push-based consumer strategy and integrates with FastAPI for WebSocket handling.

## Main Classes

### WebSocketPushConsumerEventConfig

Configuration class for WebSocket consumer.

**Attributes:**
- `type`: Consumer type (always "websocket")
- `endpoint`: WebSocket endpoint path (default: "/events/ws")

### WebSocketPushConsumer

WebSocket consumer implementation that extends PushEventConsumer.

**Key Methods:**
- `entrypoint`: Returns FastAPI APIRouter for WebSocket integration
- `_handler(websocket)`: WebSocket connection handler
- `start()`: Setup WebSocket endpoint
- `stop()`: Clean up WebSocket connections
- `ack(message)`: No-op for push mode
- `nack(message, requeue=True)`: No-op for push mode

**Attributes:**
- `connections`: List of active WebSocket connections

## How It Fits in the Event System

WebSocket Consumer provides:
1. **Real-time Communication**: Bidirectional WebSocket support
2. **FastAPI Integration**: Seamless integration with FastAPI WebSocket endpoints
3. **Connection Management**: Automatic connection tracking and cleanup
4. **JSON Messaging**: Automatic JSON serialization/deserialization
5. **Push Mode**: Event-driven processing without polling
6. **Multiple Connections**: Support for multiple concurrent WebSocket connections

## Example Usage

```python
from midil.event.consumer.websocket import WebSocketPushConsumer, WebSocketPushConsumerEventConfig
from midil.event import EventBus, EventConfig
from fastapi import FastAPI

# Configure WebSocket consumer
websocket_config = WebSocketPushConsumerEventConfig(
    type="websocket",
    endpoint="/ws/events"
)

# Create event bus with WebSocket consumer
config = EventConfig(
    consumers={"websocket": websocket_config}
)
bus = EventBus(config)

# Subscribe to WebSocket events
@bus.subscriber(target="websocket")
async def handle_websocket_event(event):
    print(f"Received WebSocket event: {event.body}")
    # Process the WebSocket event
    await process_websocket_event(event.body)

# Start consuming
await bus.start()

# Integrate with FastAPI
app = FastAPI()
websocket_consumer = bus.consumers["websocket"]
app.include_router(websocket_consumer.entrypoint)

# WebSocket will be available at /ws/events
```

## Client-Side Usage

```javascript
// Connect to WebSocket endpoint
const ws = new WebSocket('ws://localhost:8000/ws/events');

ws.onopen = function(event) {
    console.log('WebSocket connected');
    
    // Send an event
    ws.send(JSON.stringify({
        id: 'event-123',
        body: { type: 'user_action', data: { user_id: 123 } },
        timestamp: new Date().toISOString()
    }));
};

ws.onmessage = function(event) {
    const message = JSON.parse(event.data);
    console.log('Received event:', message);
};
```

## See Also

- [Event Bus](../event_bus.md) - Main event system interface
- [Push Consumer Strategy](strategies/push.md) - Push-based consumer strategy
- [Webhook Consumer](webhook.md) - HTTP webhook consumer
- [Event Message](../message.md) - Message structure
