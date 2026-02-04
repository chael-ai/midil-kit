# Redis Producer

**Location:** `midil/event/producer/redis.py`

## Overview

The Redis Producer provides integration with Redis pub/sub for publishing events to Redis channels. It implements the EventProducer interface for Redis-based event publishing.

## Main Classes

### RedisProducerEventConfig

Configuration class for Redis producer.

**Attributes:**
- `type`: Producer type (always "redis")
- `channel`: Channel to publish the event to
- `url`: Endpoint of the Redis server

### RedisProducer

Redis producer implementation that extends EventProducer.

**Key Methods:**
- `publish(payload, **kwargs)`: Publish event to Redis channel
- `close()`: Close Redis connection

## How It Fits in the Event System

Redis Producer provides:
1. **Redis Integration**: Native Redis pub/sub integration
2. **JSON Serialization**: Automatic JSON serialization of event payloads
3. **Channel Publishing**: Publish events to specific Redis channels
4. **Connection Management**: Efficient Redis connection management
5. **Real-time Messaging**: Low-latency event publishing
6. **Scalability**: Support for high-throughput event publishing

## Example Usage

```python
from midil.event.producer.redis import RedisProducer, RedisProducerEventConfig
from midil.event import EventBus, EventConfig

# Configure Redis producer
redis_config = RedisProducerEventConfig(
    type="redis",
    channel="events",
    url="redis://localhost:6379"
)

# Create event bus with Redis producer
config = EventConfig(
    producers={"main": redis_config}
)
bus = EventBus(config)

# Publish events
await bus.publish(
    {"user_id": 123, "action": "created", "data": {"name": "John"}},
    target="main"
)

# Publish to specific channel
await bus.publish(
    {"order_id": 456, "status": "shipped"},
    target="main"
)
```

## Direct Usage

```python
from midil.event.producer.redis import RedisProducer, RedisProducerEventConfig

# Create producer directly
config = RedisProducerEventConfig(
    type="redis",
    channel="notifications",
    url="redis://localhost:6379"
)
producer = RedisProducer(config)

# Publish events
await producer.publish({"message": "Hello, Redis!"})
await producer.publish({"data": [1, 2, 3]})

# Cleanup
await producer.close()
```

## Redis Subscriber Example

```python
import redis.asyncio as redis

# Subscribe to Redis channel
redis_client = redis.from_url("redis://localhost:6379")
pubsub = redis_client.pubsub()

async def handle_redis_events():
    await pubsub.subscribe("events")
    async for message in pubsub.listen():
        if message["type"] == "message":
            print(f"Received: {message['data']}")

# Start listening
await handle_redis_events()
```

## See Also

- [Producer Base](base.md) - Base producer implementation
- [Event Bus](../event_bus.md) - Main event system interface
- [Event Message](../message.md) - Message structure
