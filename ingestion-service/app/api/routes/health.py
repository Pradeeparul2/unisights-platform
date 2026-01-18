from fastapi import APIRouter, Request, HTTPException
import time

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Liveness probe.
    The service is running.
    """
    return {
        "status": "ok",
        "service": "unisights-analytics",
        "timestamp": int(time.time() * 1000),
    }


@router.get("/ready")
async def readiness_check(request: Request):
    """
    Readiness probe.
    The service is ready to receive traffic.
    """
    sink = request.app.state.sink

    # Basic readiness: sink initialized
    if not sink:
        raise HTTPException(
            status_code=503,
            detail="Ingestion sink not initialized",
        )

    # Kafka-specific readiness (non-invasive)
    # StdoutSink will always be ready
    if hasattr(sink, "producer"):
        producer = getattr(sink, "producer", None)
        if producer is None:
            raise HTTPException(
                status_code=503,
                detail="Kafka producer not ready",
            )

        # Optional: lightweight connectivity check
        try:
            producer.bootstrap_connected()
        except Exception:
            raise HTTPException(
                status_code=503,
                detail="Kafka not reachable",
            )

    return {
        "status": "ready",
        "timestamp": int(time.time() * 1000),
    }
