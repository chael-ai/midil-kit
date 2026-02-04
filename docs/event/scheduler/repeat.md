# Repeat Scheduler

**Location:** `midil/event/scheduler/repeat.py`

## Overview

The repeat scheduler provides local periodic task execution with support for both single-instance and distributed execution patterns. It includes Redis-based distributed locking to prevent duplicate execution across multiple instances.

## Main Classes

### RedisLockManager

Manages Redis-based distributed locks for task execution.

**Key Methods:**
- `acquire()`: Acquire a distributed lock with TTL

### TaskLauncher

Utility class for launching async tasks.

**Key Methods:**
- `launch(coro)`: Launch an async coroutine

### ExecutionStrategy

Protocol for execution strategies (async vs sync).

### AsyncExecutionStrategy

Strategy for executing async functions.

### SyncExecutionStrategy

Strategy for executing sync functions in thread pool.

### PeriodicTask

Main class for periodic task execution.

**Key Methods:**
- `start()`: Start the periodic task
- `_loop()`: Main execution loop

**Attributes:**
- `func`: Function to execute
- `seconds`: Interval between executions
- `wait_first`: Whether to wait before first execution
- `raise_exceptions`: Whether to raise exceptions
- `max_repetitions`: Maximum number of repetitions
- `lock_manager`: Optional Redis lock manager

## Decorators

### repeat_every(seconds, wait_first=False, raise_exceptions=False, max_repetitions=None)

Decorator for creating periodic tasks.

### repeat_every_distributed(seconds, lock_key, redis_client, wait_first=False, raise_exceptions=False, max_repetitions=None, lock_ttl=None)

Decorator for creating distributed periodic tasks with Redis locking.

## How It Fits in the Event System

Repeat scheduler provides:
1. **Periodic Execution**: Regular task execution at specified intervals
2. **Distributed Locking**: Redis-based locking for multi-instance deployments
3. **Flexible Execution**: Support for both async and sync functions
4. **Error Handling**: Configurable exception handling and retry logic
5. **Resource Management**: Proper cleanup and resource management
6. **Scalability**: Support for high-frequency task execution

## Example Usage

### Basic Periodic Task

```python
from midil.event.scheduler.repeat import repeat_every
import asyncio

@repeat_every(seconds=60, wait_first=True)
async def cleanup_old_data():
    """Clean up old data every minute"""
    print("Cleaning up old data...")
    # Your cleanup logic here

# Start the task
await cleanup_old_data()
```

### Distributed Periodic Task

```python
from midil.event.scheduler.repeat import repeat_every_distributed
import redis.asyncio as redis

# Create Redis client
redis_client = redis.from_url("redis://localhost:6379")

@repeat_every_distributed(
    seconds=300,  # 5 minutes
    lock_key="data-sync-lock",
    redis_client=redis_client,
    lock_ttl=600  # 10 minutes
)
async def sync_data():
    """Sync data every 5 minutes (distributed)"""
    print("Syncing data...")
    # Your sync logic here

# Start the distributed task
await sync_data()
```

### Manual Task Management

```python
from midil.event.scheduler.repeat import PeriodicTask, RedisLockManager
import redis.asyncio as redis

# Create Redis client
redis_client = redis.from_url("redis://localhost:6379")

# Create lock manager
lock_manager = RedisLockManager(
    client=redis_client,
    key="my-task-lock",
    ttl=300
)

# Create periodic task
task = PeriodicTask(
    func=lambda: print("Executing task..."),
    seconds=30,
    wait_first=False,
    raise_exceptions=True,
    max_repetitions=10,
    lock_manager=lock_manager
)

# Start the task
task.start()
```

### Sync Function Execution

```python
from midil.event.scheduler.repeat import repeat_every

@repeat_every(seconds=120)
def sync_function():
    """Sync function executed every 2 minutes"""
    print("Executing sync function...")
    # Your sync logic here

# Start the task
await sync_function()
```

## See Also

- [AWS EventBridge Scheduler](aws_event_bridge.md) - AWS-based event scheduling
- [Event Bus](../event_bus.md) - Main event system interface
- [Redis Producer](../producer/redis.md) - Redis integration
