# Event Exceptions

**Location:** `midil/event/exceptions.py`

## Overview

The exceptions module defines the error hierarchy for the event system, providing specific exception types for different failure scenarios in event processing.

## Exception Hierarchy

### BaseEventError

Base class for all event-related errors.

### Consumer Errors

#### ConsumerError
Base class for consumer-related errors.

#### ConsumerCrashError
Raised when a consumer crashes during operation.

#### ConsumerNotImplementedError
Raised when a consumer type is not implemented.

#### ConsumerStartError
Raised when a consumer fails to start.

#### ConsumerStopError
Raised when a consumer fails to stop.

### Producer Errors

#### ProducerError
Base class for producer-related errors.

#### ProducerNotImplementedError
Raised when a producer type is not implemented.

### Transport Errors

#### TransportNotImplementedError
Raised when a transport type is not implemented.

### Event Processing Errors

#### RetryableEventError
Raised when an error is retryable and event processing should be retried.

#### NonRetryableEventError
Raised when an error is non-retryable and event processing should be stopped.

## How It Fits in the Event System

Exception handling provides:
1. **Error Classification**: Specific exception types for different failure scenarios
2. **Retry Logic**: Distinguishes between retryable and non-retryable errors
3. **Debugging**: Clear error messages with context information
4. **Graceful Degradation**: Proper error handling in event processing pipelines

## Example Usage

```python
from midil.event.exceptions import (
    ConsumerNotImplementedError,
    ProducerNotImplementedError,
    RetryableEventError,
    NonRetryableEventError
)

# Handle consumer errors
try:
    consumer = create_consumer("unsupported_type")
except ConsumerNotImplementedError as e:
    print(f"Consumer type '{e.type}' is not supported")

# Handle producer errors
try:
    producer = create_producer("invalid_type")
except ProducerNotImplementedError as e:
    print(f"Producer type '{e.type}' is not supported")

# Handle event processing errors
async def process_event(event):
    try:
        # Some processing logic
        result = await some_operation(event)
        return result
    except TemporaryError as e:
        # This is a temporary error, should be retried
        raise RetryableEventError(f"Temporary failure: {e}")
    except PermanentError as e:
        # This is a permanent error, should not be retried
        raise NonRetryableEventError(f"Permanent failure: {e}")
```

## See Also

- [Event Bus](event_bus.md) - Main event system interface
- [Event Context](context.md) - Event context management
- [Event Message](message.md) - Message structure
