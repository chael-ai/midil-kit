# midil

A Python SDK for backend systems development. Built async-first with modular, opt-in dependencies.

---

## Installation

```bash
pip install midil[full]
```

Install only what you need:

```bash
pip install midil[auth]     # httpx, pyjwt — authentication & HTTP client
pip install midil[web]      # fastapi, starlette, uvicorn
pip install midil[cli]      # click, rich, cookiecutter — CLI tooling
pip install midil[aws]      # aioboto3 — SQS, EventBridge
pip install midil[redis]    # redis — event streaming
pip install midil[mongodb]  # pymongo — pagination integrations
pip install midil[full]     # everything
```

Requires Python 3.12+.

---

## Modules

| Module | What it does |
|---|---|
| `midil.auth` | JWT verification, Cognito client credentials flow, pluggable auth interfaces |
| `midil.http_client` | HTTPX-based client with retry, backoff, and auth integration |
| `midil.event` | Event dispatching, SQS/Redis consumers, EventBridge scheduler |
| `midil.jsonapi` | JSON:API document building and query parameter parsing |
| `midil.midilapi` | FastAPI middleware, dependencies, and pagination strategies |
| `midil.logger` | Structured logging setup via loguru |
| `midil.cli` | `midil` CLI — project scaffolding and service launcher |

---

## Quick start

**Auth**
```python
from midil.auth.cognito import CognitoClientCredentialsAuthenticator, CognitoJWTAuthorizer

authenticator = CognitoClientCredentialsAuthenticator(
    client_id="...",
    client_secret="...",
    cognito_domain="your-domain.auth.region.amazoncognito.com",
)

headers = await authenticator.get_headers()

authorizer = CognitoJWTAuthorizer(user_pool_id="...", region="us-east-1")
claims = await authorizer.verify(token)
```

**Event system**
```python
from midil.event.event_bus import EventBus
from midil.event.subscriber.base import EventSubscriber
from midil.event.message import Message

class OrderPlacedHandler(EventSubscriber):
    async def handle(self, event: Message) -> None:
        ...

    async def on_error(self, event: Message, error: Exception) -> None:
        ...

bus = EventBus()
bus.subscribe(OrderPlacedHandler())

await bus.publish({"order_id": "123"})
await bus.start()
```

**FastAPI integration**
```python
from fastapi import FastAPI
from midil.midilapi.middleware.auth_middleware import CognitoAuthMiddleware
from midil.midilapi.dependencies.jsonapi import parse_sort, parse_include

app = FastAPI()
app.add_middleware(CognitoAuthMiddleware)
```

---

## CLI

```bash
midil init        # scaffold a new service
midil launch      # start the service with uvicorn
midil version     # show SDK version
```

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
