from __future__ import annotations

import asyncio
import hashlib
import json
from typing import Any, Dict, Literal, Optional

from loguru import logger
from pydantic import Field

from midil.event.connector.health import ConnectorHealth
from midil.event.consumer.strategies.pull import (
    PullEventConsumer,
    PullEventConsumerConfig,
)
from midil.event.message import Message


class HTTPPollingConsumerConfig(PullEventConsumerConfig):
    """
    Configuration for the HTTP polling consumer.

    poll_interval controls how often the URL is hit. The consumer emits
    a Message only when the response body changes (SHA-256 content hash),
    so low intervals are safe for idempotent GET endpoints.
    """

    type: Literal["http_polling"] = "http_polling"
    url: str = Field(..., description="Endpoint to poll")
    method: str = Field(default="GET", description="HTTP method")
    headers: Dict[str, str] = Field(default_factory=dict)
    poll_interval: float = Field(
        default=60.0, description="Seconds between polls", ge=1.0
    )
    timeout: float = Field(default=10.0, description="Request timeout in seconds", gt=0)


class HTTPPollingConsumer(PullEventConsumer):
    """
    Pull connector that polls a REST endpoint on a fixed interval.

    A Message is dispatched only when the response body changes, detected
    via SHA-256 content hashing. This makes the connector safe to run at
    short intervals against idempotent APIs without flooding subscribers.

    Suitable for integrating third-party APIs that do not support webhooks
    or push-based event delivery.

    Requires: midil[auth]  (httpx)
    """

    def __init__(self, config: HTTPPollingConsumerConfig) -> None:
        super().__init__(config)
        self._config: HTTPPollingConsumerConfig = config
        self._last_hash: Optional[str] = None

    async def _poll_loop(self) -> None:
        try:
            import httpx
        except ImportError:
            raise ImportError(
                "HTTP polling requires the 'auth' extra: pip install midil[auth]"
            )

        async with httpx.AsyncClient(timeout=self._config.timeout) as client:
            while self._running:
                await self._poll_once(client)
                await asyncio.sleep(self._config.poll_interval)

    async def _poll_once(self, client: Any) -> None:
        try:
            response = await client.request(
                self._config.method,
                self._config.url,
                headers=self._config.headers,
            )
            response.raise_for_status()
            body = response.json()
            content_hash = self._hash(body)

            if content_hash != self._last_hash:
                self._last_hash = content_hash
                await self.dispatch(
                    Message(
                        id=content_hash,
                        body=body,
                        metadata={
                            "url": self._config.url,
                            "status_code": response.status_code,
                        },
                    )
                )
        except Exception as exc:
            logger.warning(f"[http_polling] Poll error [{self._config.url}]: {exc}")

    async def ack(self, message: Message) -> None:
        pass  # polling has no ack semantics

    async def nack(self, message: Message, requeue: bool = False) -> None:
        pass

    async def health(self) -> ConnectorHealth:
        try:
            import time

            import httpx

            start = time.monotonic()
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.head(self._config.url)
                latency_ms = (time.monotonic() - start) * 1000
                if response.status_code < 500:
                    return ConnectorHealth.healthy(latency_ms=latency_ms)
                return ConnectorHealth.unhealthy(f"HTTP {response.status_code}")
        except Exception as exc:
            return ConnectorHealth.unhealthy(str(exc))

    @staticmethod
    def _hash(body: Any) -> str:
        serialized = json.dumps(body, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode()).hexdigest()
