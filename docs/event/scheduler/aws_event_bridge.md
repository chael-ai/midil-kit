# AWS EventBridge Scheduler

**Location:** `midil/event/scheduler/aws_event_bridge.py`

## Overview

The AWS EventBridge Scheduler provides integration with AWS EventBridge for scheduling and emitting events. It supports both immediate event emission and scheduled event execution using AWS EventBridge and EventBridge Scheduler.

## Main Classes

### AWSEventBridgeScheduler

Scheduler class for AWS EventBridge integration.

**Key Methods:**
- `put_event(detail_type, source, detail, event_bus_name)`: Emit an immediate event to EventBridge
- `schedule_event(schedule_name, endpoint, execution_time, data, role_arn)`: Schedule a future event execution

## How It Fits in the Event System

AWS EventBridge Scheduler provides:
1. **Event Emission**: Immediate event emission to EventBridge
2. **Event Scheduling**: Future event execution scheduling
3. **AWS Integration**: Native AWS EventBridge and Scheduler integration
4. **Event Routing**: Event routing through AWS EventBridge rules
5. **Scheduled Execution**: Delayed and scheduled event processing
6. **Event Bus Integration**: Integration with AWS EventBridge event buses

## Example Usage

### Immediate Event Emission

```python
from midil.event.scheduler.aws_event_bridge import AWSEventBridgeScheduler

# Create scheduler
scheduler = AWSEventBridgeScheduler(region="us-east-1")

# Emit immediate event
await scheduler.put_event(
    detail_type="User Created",
    source="myapp.users",
    detail={"user_id": 123, "name": "John Doe"},
    event_bus_name="default"
)
```

### Scheduled Event Execution

```python
from datetime import datetime, timedelta
from midil.event.scheduler.aws_event_bridge import AWSEventBridgeScheduler

# Create scheduler
scheduler = AWSEventBridgeScheduler(region="us-east-1")

# Schedule event for future execution
execution_time = datetime.utcnow() + timedelta(hours=1)
await scheduler.schedule_event(
    schedule_name="user-reminder-123",
    endpoint="arn:aws:lambda:us-east-1:123456789:function:send-reminder",
    execution_time=execution_time,
    data={"user_id": 123, "reminder_type": "welcome"},
    role_arn="arn:aws:iam::123456789:role/EventBridgeSchedulerRole"
)
```

### Integration with Event Bus

```python
from midil.event import EventBus, EventConfig
from midil.event.scheduler.aws_event_bridge import AWSEventBridgeScheduler

# Create scheduler
scheduler = AWSEventBridgeScheduler(region="us-east-1")

# Emit event through EventBridge
async def emit_user_event(user_data):
    await scheduler.put_event(
        detail_type="User Action",
        source="myapp.users",
        detail=user_data,
        event_bus_name="default"
    )

# Use in your application
await emit_user_event({"user_id": 123, "action": "login"})
```

## AWS EventBridge Rules

To route events from EventBridge to your application, you can create rules:

```json
{
  "Rules": [
    {
      "Name": "UserEventsRule",
      "EventPattern": {
        "source": ["myapp.users"],
        "detail-type": ["User Created", "User Action"]
      },
      "Targets": [
        {
          "Id": "1",
          "Arn": "arn:aws:sqs:us-east-1:123456789:user-events-queue"
        }
      ]
    }
  ]
}
```

## See Also

- [Repeat Scheduler](repeat.md) - Local repeat scheduler
- [Event Bus](../event_bus.md) - Main event system interface
- [SQS Producer](../producer/sqs.md) - SQS producer for EventBridge targets
