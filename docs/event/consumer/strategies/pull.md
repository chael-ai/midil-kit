# Pull Consumer Strategy

**Location:** `midil/event/consumer/strategies/pull.py`

## Overview

The pull consumer strategy implements a polling-based approach for consuming events. It continuously polls an event source for new messages and processes them as they become available.

## Main Classes

### PullEventConsumerConfig

Configuration class for pull-based consumers.

**Attributes:**
- `poll_interval`: Interval between polls if no messages (default: 0.1 seconds)

### PullEventConsumer

Abstract base class for pull-based event consumers.

**Key Methods:**
- `_poll_loop()`: Abstract method for polling implementation
- `start()`: Start the consumer and polling loop
- `stop()`: Stop the consumer and cleanup
- `_handle_task_exception(task)`: Handle task exceptions and crashes
- `_reset_state()`: Reset consumer state after stopping
- `_close()`: Override for custom cleanup logic

**Attributes:**
- `_running`: Boolean flag for consumer state
- `_loop_task`: Asyncio task for the polling loop

## How It Fits in the Event System

Pull consumer strategy provides:
1. **Polling Mechanism**: Continuous polling for new messages
2. **Task Management**: Asyncio task management for polling loops
3. **Error Handling**: Crash detection and exception handling
4. **State Management**: Running state tracking and cleanup
5. **Lifecycle Control**: Start/stop methods with proper cleanup
6. **Extensibility**: Abstract polling method for custom implementations

## Example Usage

```python
from midil.event.consumer.strategies.pull import PullEventConsumer, PullEventConsumerConfig
from midil.event.message import Message
import asyncio

class CustomPullConsumer(PullEventConsumer):
    def __init__(self, config: PullEventConsumerConfig):
        super().__init__(config)
        self.message_queue = []
    
    async def _poll_loop(self):
        """Implement custom polling logic"""
        while self._running:
            # Poll your event source
            messages = await self._fetch_messages()
            
            if messages:
                for message in messages:
                    await self.dispatch(message)
            else:
                # Wait for poll interval if no messages
                await asyncio.sleep(self._config.poll_interval)
    
    async def _fetch_messages(self):
        """Fetch messages from your event source"""
        # Implement your polling logic here
        return []

# Usage
config = PullEventConsumerConfig(
    type="custom",
    poll_interval=1.0
)
consumer = CustomPullConsumer(config)

# Subscribe to events
@consumer.subscribe
async def handle_event(event):
    print(f"Received event: {event.body}")

# Start consuming
await consumer.start()
```

## See Also

- [Base Consumer Strategy](base.md) - Base consumer implementation
- [SQS Consumer](../sqs.md) - SQS pull consumer implementation
- [Event Bus](../event_bus.md) - Main event system interface
