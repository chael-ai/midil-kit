from pymidil.event.producer.base import EventProducer
from pymidil.event.producer.base import BaseProducerConfig
import aioboto3
from typing import Any, Dict, Literal, Optional
import json
from pydantic import Field
from pymidil.event.message import MessageBody
from botocore.utils import ArnParser

_MAX_SQS_ATTRIBUTES = 10


def build_sqs_message_attributes(headers: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """Map flat string-ish headers (incl. traceparent) to SQS MessageAttributes."""
    attributes: Dict[str, Dict[str, str]] = {}
    for key, value in headers.items():
        if value is None or not isinstance(value, (str, int, float, bool)):
            continue
        attributes[str(key)] = {"DataType": "String", "StringValue": str(value)}
        if len(attributes) >= _MAX_SQS_ATTRIBUTES:
            break
    return attributes


class SQSProducerEventConfig(BaseProducerConfig):
    type: Literal["sqs"] = "sqs"
    queue_url: str = Field(..., description="URL of the queue")

    @property
    def region(self) -> str:
        arn_parser = ArnParser()
        arn = arn_parser.parse_arn(self.queue_url)
        return arn["region"]


class SQSProducer(EventProducer):
    def __init__(self, config: SQSProducerEventConfig) -> None:
        super().__init__(config)
        self._config: SQSProducerEventConfig = config
        self._session = aioboto3.Session()

    async def publish(
        self, payload: MessageBody, metadata: Optional[Dict[str, Any]] = None, **kwargs
    ) -> None:
        message = json.dumps(payload)
        headers = self._inject_trace(metadata)
        params: Dict[str, Any] = {
            "QueueUrl": self._config.queue_url,
            "MessageBody": message,
        }
        attributes = build_sqs_message_attributes(headers)
        if attributes:
            params["MessageAttributes"] = attributes
        async with self._session.client("sqs", region_name=self._config.region) as sqs:  # type: ignore[attr-defined]
            await sqs.send_message(**params)

    async def close(self) -> None:
        pass
