# Event Message

**Location:** `midil/event/message.py`

## Overview

The message module defines the core data structures for event messages in the Midil event system, providing a standardized format for event payloads and metadata.

## Main Classes

### Message

The base message class that represents an event message.

**Attributes:**
- `id`: Unique identifier for the message (string or int)
- `body`: The actual message payload (sequence, mapping, or string)
- `timestamp`: When the message was published or received (datetime, defaults to UTC now)
- `metadata`: Additional message properties or headers (dict, defaults to empty dict)

### MessageBody

Type alias for message body content:
- `Sequence[Any]`: List or tuple of values
- `Mapping[Any, Any]`: Dictionary-like object
- `str`: String content

## How It Fits in the Event System

The Message class provides:
1. **Standardized Format**: Consistent structure for all event messages
2. **Metadata Support**: Additional headers and properties for event context
3. **Timestamping**: Automatic timestamp generation for event tracking
4. **Flexible Payload**: Support for various data types in message body
5. **Idempotency**: Unique IDs for message deduplication

## Example Usage

```python
from midil.event.message import Message
from datetime import datetime

# Create a message with dictionary payload
message = Message(
    id="msg-123",
    body={"user_id": 123, "action": "created", "data": {"name": "John"}},
    timestamp=datetime.utcnow(),
    metadata={"source": "api", "version": "1.0"}
)

# Create a message with string payload
text_message = Message(
    id="msg-456",
    body="Hello, World!",
    metadata={"type": "notification"}
)

# Access message properties
print(f"Message ID: {message.id}")
print(f"Payload: {message.body}")
print(f"Timestamp: {message.timestamp}")
print(f"Source: {message.metadata.get('source')}")

# Convert to JSON
json_data = message.model_dump_json()
print(f"JSON: {json_data}")
```

## See Also

- [Event Bus](event_bus.md) - Main event system interface
- [Event Context](context.md) - Event context management
- [Consumer Message](../consumer/strategies/base.md) - Extended message for consumers
