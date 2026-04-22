from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging
from dataclasses import asdict

from app.core.settings import get_settings
from app.core.logging import setup_logging
from app.ingestion.factory import create_sink
from app.geo.factory import create_geo_provider
from app.utils.ip import get_client_ip
from app.enrichers.session import SessionEnricher
from app.enrichers.event import EventEnricher
from app.validators.payload import PayloadValidator
from app.validators.event import EventValidator
from app.api.routes.health import router as health_router
from unisights import UnisightsOptions
from unisights.fastapi import unisights_fastapi

# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------

setup_logging()
logger = logging.getLogger(__name__)

settings = get_settings()

# -------------------------------------------------------------------
# Lifespan (startup / shutdown)
# -------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Analytics Ingestion Service")

    # Initialize ingestion sink (Kafka / stdout)
    sink = create_sink(settings)
    await sink.start()

    # Initialize geo provider (MaxMind / none)
    geo_provider = create_geo_provider(settings)

    # Store shared dependencies on app.state
    app.state.sink = sink
    app.state.geo_provider = geo_provider

    logger.info(
        "Service started",
        extra={
            "ingestion_mode": settings.ingestion_mode,
            "geo_provider": settings.geo_provider,
        },
    )

    yield

    logger.info("🛑 Shutting down Analytics Ingestion Service")

    await sink.stop()

    logger.info("Shutdown complete")


# -------------------------------------------------------------------
# Unisights event handler
# -------------------------------------------------------------------

async def handle_unisights_event(payload, request: Request):
    sink = request.app.state.sink
    geo_provider = request.app.state.geo_provider

    # Unisights payload objects expose `.data`; support both raw dicts and typed payloads.
    request_payload = getattr(payload, "data", payload)

    if hasattr(request_payload, "dict"):
        request_payload = request_payload.dict()

    decrypted = request_payload

    if hasattr(decrypted, '__dataclass_fields__'):
        decrypted = asdict(decrypted)
    client_ip = get_client_ip(request)
    geo = geo_provider.lookup(client_ip)

    session_enricher = SessionEnricher(
        user_agent=request.headers.get("user-agent"),
        geo=geo,
    )

    session_meta = session_enricher.enrich(decrypted)

    event_enricher = EventEnricher()
    event_validator = EventValidator()
    published_events = 0
    event_tasks = []

    for event in decrypted["events"]:
        try:
            event_validator.validate(event)
        except ValueError:
            logger.debug("Skipping invalid event", extra={"event": event})
            continue

        enriched_event = event_enricher.enrich(
            {
                "event": event,
                "base": decrypted,
            }
        )

        event_tasks.append(
            sink.publish_event(
                settings.kafka_event_topic,
                decrypted["asset_id"],
                enriched_event,
            )
        )

        published_events += 1

    # Publish all events concurrently
    if event_tasks:
        await asyncio.gather(*event_tasks, return_exceptions=True)

    await sink.publish_session(
        settings.kafka_session_topic,
        decrypted["asset_id"],
        session_meta,
    )

    logger.info(
        "Analytics payload ingested",
        extra={
            "asset_id": decrypted["asset_id"],
            "session_id": decrypted["session_id"],
            "events": published_events,
            "geo": geo.get("country") if geo else None,
        },
    )

    return {"status": "accepted", "events": published_events}

options = UnisightsOptions(
    path="/collect/events",
    handler=handle_unisights_event,
    validate_schema=True,
)

unisights_router = unisights_fastapi(options)

# -------------------------------------------------------------------
# FastAPI app
# -------------------------------------------------------------------

app = FastAPI(
    title="Unisights Analytics Ingestion",
    description="Privacy-first, open-source analytics ingestion service",
    version="1.0.0",
    lifespan=lifespan,
)

# -------------------------------------------------------------------
# Routers
# -------------------------------------------------------------------

app.include_router(unisights_router)
app.include_router(health_router, tags=["health"])

# -------------------------------------------------------------------
# Middleware
# -------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# Root (optional)
# -------------------------------------------------------------------

@app.get("/")
async def root():
    return {
        "service": "unisights-analytics",
        "status": "running",
        "docs": "/docs",
    }
