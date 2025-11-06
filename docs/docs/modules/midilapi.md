# MidilAPI Documentation

##  Overview

MidilAPI is a powerful and opinionated Python API framework built on top of FastAPI, designed to accelerate the development of web services that adhere to the [JSONAPI specification](https://jsonapi.org/). It provides a structured approach to API development, integrating robust authentication, standardized query parameter parsing, and streamlined project scaffolding.

__Key Features:__

- __JSONAPI Compliance__: Ensures consistent data exchange and API interactions by enforcing JSONAPI standards.
- __FastAPI Foundation__: Leverages FastAPI's high performance, automatic OpenAPI documentation, and intuitive dependency injection system.
- __Integrated Authentication__: Provides out-of-the-box support for JWT-based authentication, with specific integration for AWS Cognito.
- __Standardized Query Parameters__: Simplifies the handling of common API patterns like sorting and including related resources, following JSONAPI conventions.
- __CLI Scaffolding__: Enables rapid project setup and consistent project structures through the `midil` command-line interface.

###  Prerequisites

- Python 3.8+
- `midil-kit` installed (usually via `pip install midil-kit`)

###  Setting up

To begin using MidilAPI, you'll typically start by scaffolding a new service using the `midil` CLI.
Use the `midil init <service>` command to create a new project:

```bash
midil init <service>

# Example:
midil init my-awesome-api
```

This command will:

- Create a new directory `services/my-awesome-api`.
- Populate it with a basic FastAPI application structure, including `main.py`, `pyproject.toml`, and a `README.md`.
- Configure the project to use MidilAPI's features.

When initializing a service for the first time the midil-kit CLI will walk you through service descriptions like assigning the name of the service, the version of the service, the author and so on. You can default through these steps by hitting `Enter` on every prompting.

##  MidilAPI Module File Structure

The `midilapi` module itself, as part of the `midil-kit`, by default has a well-defined internal structure. This structure organizes its core components, dependencies, and middleware.

```javascript
midilapi/
├── __init__.py                 # MidilAPI application class (MidilAPI)
├── config.py                   # Configuration models (ServerConfig, MidilApiConfig)
├── exceptions.py               # Custom exceptions and handlers
├── responses.py                # JSONAPIResponse class
├── utils.py                    # Utility functions
├── dependencies/
│   ├── __init__.py
│   ├── auth.py                 # Authentication dependencies (authorize_request)
│   └── jsonapi.py              # JSON:API query parameter dependencies (parse_sort, parse_include)
└── middleware/
    ├── __init__.py
    └── auth_middleware.py      # Authentication middleware (BaseAuthMiddleware, CognitoAuthMiddleware)
```

__Explanation of Key Directories/Files within `midilapi/`:__

- __`__init__.py`__: This is the entry point for the `midilapi` module. It defines the `MidilAPI` class, which extends FastAPI to provide JSONAPI specific enhancements, and exports key utilities like `register_jsonapi_exception_handlers` and `JSONAPIResponse`.

- __`config.py`__: Contains Pydantic models (`ServerConfig`, `MidilApiConfig`) for defining and validating configuration settings related to the API server, such as host and port.

- __`exceptions.py`__: Houses custom exception classes and functions for registering JSONAPI compliant exception handlers, ensuring consistent error responses.

- __`responses.py`__: Defines the `JSONAPIResponse` class, which is a custom FastAPI response class to ensure all API responses adhere to the JSONAPI specification.

- __`utils.py`__: A module for general utility functions that support the `midilapi` framework.

- __`dependencies/`__: This sub-directory contains FastAPI dependency functions that can be injected into your API routes.

  - `auth.py`: Provides `authorize_request`, a dependency for authenticating requests using JWT tokens and integrating with AWS Cognito.
  - `jsonapi.py`: Offers `parse_sort` and `parse_include` dependencies for parsing JSONAPI standard query parameters for sorting and including related resources.

- __`middleware/`__: This sub-directory contains Starlette/FastAPI middleware classes for global request processing.
  - `auth_middleware.py`: Defines `BaseAuthMiddleware` and `CognitoAuthMiddleware` for handling authentication across all incoming requests, storing authentication context in the request state.

Understanding this internal structure is crucial for developers who wish to extend, customize, or deeply integrate with the `midilapi` framework.

##  Core Components and Features

###  The `MidilAPI` Application Class

The heart of your MidilAPI service is the `MidilAPI` class, which extends FastAPI.

__Location__: `midilapi/__init__.py`

```python showLineNumbers
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from typing import Any, Dict
from midil.midilapi.exceptions import register_jsonapi_exception_handlers
from midil.midilapi.responses import JSONAPIResponse
from midil.midilapi.utils import _update_openapi_jsonapi_media_types


class MidilAPI(FastAPI):
    """
    FastAPI subclass that globally sets JSON:API media types in OpenAPI schema.
    """
    def openapi(self) -> Dict[str, Any]:
        # ... (implementation details) ...
        pass

# Exported utilities
__all__ = ["MidilAPI", "register_jsonapi_exception_handlers", "JSONAPIResponse"]
```

__Key Responsibilities__:

- __JSON:API OpenAPI Integration__: Automatically modifies the generated OpenAPI schema to include JSON:API media types (`application/vnd.api+json`), ensuring your API documentation reflects JSON:API standards.
- __Standardized Responses__: Provides `JSONAPIResponse` for consistent JSON:API formatted responses.
- __Exception Handling__: Integrates `register_jsonapi_exception_handlers` to convert common HTTP exceptions into JSON:API error objects.

__Basic Usage__:

```python showLineNumbers
from midil.midilapi import MidilAPI, register_jsonapi_exception_handlers

app = MidilAPI(
    title="My Awesome API",
    version="1.0.0",
    description="A sample API built with MidilAPI."
)

# Register JSON:API compliant exception handlers
register_jsonapi_exception_handlers(app)

@app.get("/health", response_model=JSONAPIResponse)
async def health_check():
    return {"data": {"type": "status", "id": "1", "attributes": {"status": "ok"}}}
```

###  Configuration

MidilAPI uses Pydantic models for type-safe and validated configuration.

__Location__: `midilapi/config.py`

```python showLineNumbers
from midil.utils.models import SnakeCaseModel
from pydantic import Field


class ServerConfig(SnakeCaseModel):
    host: str = Field(
        default="0.0.0.0", description="Host on which the application will run."
    )
    port: int = Field(
        default=8000, description="Port on which the application will run."
    )


class MidilApiConfig(SnakeCaseModel, extra="allow"):
    server: ServerConfig = Field(
        default=ServerConfig(), description="Server configuration."
    )
```

These configurations define how your MidilAPI application runs, including network settings. They are typically loaded at application startup, often managed by the `midil` CLI's `launch` command.


##  JSON:API Query Parameters

MidilAPI simplifies parsing common JSON:API query parameters like `sort` and `include`.

__Location__: `midilapi/dependencies/jsonapi.py`

```python showLineNumbers
from typing import List, Optional
from fastapi import Query, Depends
from midil.jsonapi.query import Sort, SortField, Include


def parse_sort(sort: Optional[List[str]] = Query(None, alias="sort")) -> Optional[Sort]:
    """
    Parses the 'sort' query parameter into a `Sort` object.
    e.g., ?sort=-created_at,name
    """
    if sort:
        return Sort(fields=[SortField.from_raw(s) for s in sort])
    return None


def parse_include(
    include: Optional[List[str]] = Query(None, alias="include")
) -> Optional[Include]:
    """
    Parses the 'include' query parameter into an `Include` object.
    e.g., ?include=author,comments.author
    """
    if include:
        return Include(relationships=include)
    return None
```

__Usage__:

Integrate these functions as dependencies in your endpoint definitions:

```python showLineNumbers
from midil.midilapi import MidilAPI
from midil.midilapi.dependencies.jsonapi import parse_sort, parse_include
from midil.jsonapi.query import Sort, Include
from midil.midilapi.responses import JSONAPIResponse
from fastapi import Depends

app = MidilAPI()

@app.get("/articles", response_model=JSONAPIResponse)
async def list_articles(
    sort: Optional[Sort] = Depends(parse_sort),
    include: Optional[Include] = Depends(parse_include)
):
    """
    Retrieves a list of articles, supporting JSON:API sorting and eager loading of relationships.
    Example: GET /articles?sort=-createdAt,title&include=author,comments.author
    """
    # In a real application, you would use 'sort' and 'include' to modify your database query
    response_data = {
        "type": "articles",
        "id": "1",
        "attributes": {"title": "Sample Article"},
        "relationships": {}
    }

    if sort:
        print(f"Sorting by: {sort.fields}")
        # Apply sorting logic here
    if include:
        print(f"Including relationships: {include.relationships}")
        # Apply eager loading logic here, e.g., fetch author and comments
        if "author" in include.relationships:
            response_data["relationships"]["author"] = {
                "data": {"type": "users", "id": "101"}
            }

    return {"data": response_data}
```


