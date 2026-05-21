from midil.event.producer.base import EventProducer
from midil.event.producer.base import BaseProducerConfig
import aioboto3
from typing import Literal
import json
from pydantic import Field
from midil.event.utils import get_region_from_sqs_queue_url
from midil.event.message import MessageBody


class SQSProducerEventConfig(BaseProducerConfig):
    type: Literal["sqs"] = "sqs"
    queue_url: str = Field(..., description="URL of the queue")

    @property
    def region(self) -> str:
        return get_region_from_sqs_queue_url(self.queue_url)


class SQSProducer(EventProducer):
    def __init__(self, config: SQSProducerEventConfig) -> None:
        super().__init__(config)
        self._config: SQSProducerEventConfig = config
        self._session = aioboto3.Session()

    async def publish(self, payload: MessageBody, **kwargs) -> None:
        message = json.dumps(payload)
        async with self._session.client("sqs", region_name=self._config.region) as sqs:
            await sqs.send_message(QueueUrl=self._config.queue_url, MessageBody=message)

    async def close(self) -> None:
        pass
