"""The server module provides the REST interface for the AI gateway.

We grouped the API interface into several groups:

- /v1/* - The OpenAI compatible universal API interface.
- /admin/* - The administrative interface for managing the gateway.
- /health/readiness - Health probe for checking if the server is ready.
- /health/liveness - Health probe for checking if the server is alive.
"""

from typing import AsyncIterator
from fastapi import FastAPI
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi_healthchecks.api.router import HealthcheckRouter, Probe


@asynccontextmanager
async def app_lifecycle(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan context manager."""
    Instrumentator().expose(app, tags=["Metrics"])
    yield


app = FastAPI(title="Symbiosis AI Gateway", version="0.1.0", lifespan=app_lifecycle)

app.include_router(
    HealthcheckRouter(
        Probe(name="readiness", checks=[]),
        Probe(name="liveness", checks=[]),
    ),
    prefix="/health",
)
