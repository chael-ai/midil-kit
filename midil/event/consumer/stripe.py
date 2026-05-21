from __future__ import annotations

from typing import Any, Dict, Literal

from loguru import logger
from pydantic import Field

from midil.event.connector.health import ConnectorHealth
from midil.event.consumer.strategies.push import (
    PushEventConsumer,
    PushEventConsumerConfig,
)
from midil.event.message import Message
from fastapi import Response, APIRouter, Request
from fastapi.exceptions import HTTPException
import stripe


class StripeWebhookConsumerConfig(PushEventConsumerConfig):
    """
    Configuration for the Stripe webhook consumer.

    webhook_secret is the signing secret from the Stripe dashboard.
    Every incoming request is validated against it before dispatch.
    """

    type: Literal["stripe_webhook"] = "stripe_webhook"
    webhook_secret: str = Field(..., description="Stripe webhook signing secret")
    route_path: str = Field(
        default="/webhooks/stripe",
        description="Path to mount the webhook endpoint on",
    )


class StripeWebhookConsumer(PushEventConsumer):
    """
    Push connector that receives and validates Stripe webhook events.

    Validates the Stripe-Signature header on every request. On success,
    dispatches a Message whose body is event.data.object and whose
    metadata carries stripe_event_type for subscriber-side routing.

    The connector exposes a FastAPI APIRouter via the entrypoint property.
    Mount it on your app:

        app.include_router(bus.consumers["stripe"].entrypoint)

    Requires: midil[web] + pip install stripe
    """

    def __init__(self, config: StripeWebhookConsumerConfig) -> None:
        super().__init__(config)
        self._config: StripeWebhookConsumerConfig = config
        self._router = self._build_router()

    @property
    def entrypoint(self) -> Any:
        return self._router

    async def start(self) -> None:
        logger.info(f"[stripe_webhook] Ready at {self._config.route_path}")

    async def stop(self) -> None:
        self._subscribers.clear()
        logger.info("[stripe_webhook] Stopped")

    async def ack(self, message: Message) -> None:
        pass

    async def nack(self, message: Message, requeue: bool = False) -> None:
        logger.warning(
            f"[stripe_webhook] Event {message.id} could not be processed, requeue={requeue}"
        )

    async def health(self) -> ConnectorHealth:
        return ConnectorHealth.healthy()

    def _build_router(self) -> Any:
        router = APIRouter()

        @router.post(self._config.route_path, include_in_schema=True)
        async def receive(request: Request) -> Response:
            return await self._handle(request)

        return router

    async def _handle(self, request: Any) -> Any:
        payload = await request.body()
        sig_header = request.headers.get("Stripe-Signature", "")

        try:
            event: Dict[str, Any] = stripe.Webhook.construct_event(
                payload, sig_header, self._config.webhook_secret
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.errors.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid Stripe signature")

        message = Message(
            id=event["id"],
            body=event["data"]["object"],
            metadata={
                "stripe_event_type": event["type"],
                "api_version": event.get("api_version"),
                "livemode": event.get("livemode", False),
            },
        )
        logger.debug(f"[stripe_webhook] {event['type']} ({event['id']})")
        await self.dispatch(message)
        return Response(status_code=200)
