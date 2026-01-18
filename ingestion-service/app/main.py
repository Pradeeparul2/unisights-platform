from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.settings import get_settings
from app.core.logging import setup_logging
from app.ingestion.factory import create_sink
from app.geo.factory import create_geo_provider
from app.crypto.factory import create_decryptor

from app.api.routes.collect import router as collect_router
from app.api.routes.health import router as health_router

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

    # Initialize decryptor (AES-GCM / none)
    decryptor = create_decryptor(settings)

    # Store shared dependencies on app.state
    app.state.sink = sink
    app.state.geo_provider = geo_provider
    app.state.decryptor = decryptor

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

app.include_router(collect_router, prefix="/collect", tags=["collect"])
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
