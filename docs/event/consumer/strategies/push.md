# Push Consumer Strategy

**Location:** `midil/event/consumer/strategies/push.py`

## Overview

The push consumer strategy implements an event-driven approach for consuming events. Instead of polling, it receives events through external triggers like HTTP requests or WebSocket connections.

## Main Classes

### PushEventConsumerConfig

Configuration class for push-based consumers.

**Attributes:**
- No additional attributes beyond base configuration

### PushEventConsumer

Abstract base class for push-based event consumers.

**Key Methods:**
- `entrypoint`: Property that returns framework-specific entrypoint object
- `start()`: Setup the push consumer (typically no-op)
- `stop()`: Cleanup the push consumer
- `ack(message)`: Acknowledge message (typically no-op for push mode)
- `nack(message, requeue=True)`: Negative acknowledge (typically no-op for push mode)

## How It Fits in the Event System

Push consumer strategy provides:
1. **Event-Driven Processing**: No polling, events are pushed to the consumer
2. **Framework Integration**: Entrypoint property for framework integration
3. **Minimal Overhead**: No continuous polling or background tasks
4. **External Triggers**: Events triggered by external systems (HTTP, WebSocket, etc.)
5. **Stateless Operation**: Typically stateless with no persistent connections
6. **Immediate Processing**: Events are processed as soon as they arrive

## Example Usage

```python
from midil.event.consumer.strategies.push import PushEventConsumer, PushEventConsumerConfig
from midil.event.message import Message
from fastapi import APIRouter

class CustomPushConsumer(PushEventConsumer):
    def __init__(self, config: PushEventConsumerConfig):
        super().__init__(config)
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup HTTP routes for the consumer"""
        @self.router.post("/events")
        async def receive_event(request):
            # Parse request and create message
            body = await request.json()
            message = Message(
                id=body.get("id", "unknown"),
                body=body.get("data", {}),
                metadata={"source": "http"}
            )
            await self.dispatch(message)
            return {"status": "ok"}
    
    @property
    def entrypoint(self):
        """Return FastAPI router for integration"""
        return self.router
    
    async def start(self):
        """Setup push consumer"""
        # No continuous polling needed
        pass
    
    async def stop(self):
        """Cleanup push consumer"""
        # Cleanup if needed
        pass

# Usage
config = PushEventConsumerConfig(type="custom")
consumer = CustomPushConsumer(config)

# Subscribe to events
@consumer.subscribe
async def handle_event(event):
    print(f"Received push event: {event.body}")

# Get FastAPI router for integration
app.include_router(consumer.entrypoint)
```

## See Also

- [Base Consumer Strategy](base.md) - Base consumer implementation
- [Webhook Consumer](../webhook.md) - HTTP webhook push consumer
- [WebSocket Consumer](../websocket.md) - WebSocket push consumer
- [Event Bus](../event_bus.md) - Main event system interface
