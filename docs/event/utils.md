# Event Utilities

**Location:** `midil/event/utils.py`

## Overview

The utils module provides utility functions for event processing, particularly for working with AWS SQS queue URLs and extracting region information.

## Main Functions

### get_region_from_sqs_queue_url(queue_url)

Extracts the AWS region from an SQS queue URL.

**Parameters:**
- `queue_url`: The SQS queue URL (e.g., "https://sqs.us-east-1.amazonaws.com/123456789/my-queue")

**Returns:**
- `str`: The AWS region (e.g., "us-east-1")

**Raises:**
- `ValueError`: If the queue URL format is invalid

**Example:**
```python
from midil.event.utils import get_region_from_sqs_queue_url

# Extract region from queue URL
queue_url = "https://sqs.us-east-1.amazonaws.com/123456789/my-queue"
region = get_region_from_sqs_queue_url(queue_url)
print(region)  # "us-east-1"
```

## How It Fits in the Event System

Utility functions provide:
1. **AWS Integration**: Helper functions for AWS service integration
2. **URL Parsing**: Extract metadata from service URLs
3. **Error Handling**: Proper error handling for invalid URLs
4. **Logging**: Error logging for debugging purposes

## Example Usage

```python
from midil.event.utils import get_region_from_sqs_queue_url
from loguru import logger

def process_sqs_queue(queue_url):
    try:
        region = get_region_from_sqs_queue_url(queue_url)
        logger.info(f"Processing queue in region: {region}")
        
        # Use region for AWS client configuration
        import boto3
        sqs_client = boto3.client('sqs', region_name=region)
        
    except ValueError as e:
        logger.error(f"Invalid queue URL: {e}")
        raise
```

## See Also

- [SQS Producer](../producer/sqs.md) - SQS producer implementation
- [SQS Consumer](../consumer/sqs.md) - SQS consumer implementation
- [Event Bus](event_bus.md) - Main event system interface
