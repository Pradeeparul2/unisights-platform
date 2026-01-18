from fastapi import APIRouter, Request, HTTPException
import logging
from typing import Dict, Any

from app.core.settings import get_settings
from app.utils.ip import get_client_ip
from app.enrichers.session import SessionEnricher
from app.enrichers.event import EventEnricher
from app.validators.payload import PayloadValidator
from app.validators.event import EventValidator


router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()


@router.post("/events", status_code=202)
async def collect_events(request: Request, payload: Dict[str, Any]):
    """
    Collect analytics events and forward them to the configured ingestion sink.
    """
    sink = request.app.state.sink
    geo_provider = request.app.state.geo_provider
    decryptor = request.app.state.decryptor

    # -------------------------------------------------
    # Decrypt payload
    # -------------------------------------------------

    try:
        decrypted = decryptor.decrypt(
            payload.get("data"),
            payload.get("id"),
        )
    except Exception:
        logger.warning("Payload decryption failed")
        raise HTTPException(status_code=400, detail="Invalid payload")
    
    # -------------------------------------------------
    # Validate payload
    # -------------------------------------------------

    payload_validator = PayloadValidator()

    try:
        payload_validator.validate(decrypted)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # -------------------------------------------------
    # Validate required fields
    # -------------------------------------------------

    required_fields = ["asset_id", "session_id", "events", "device_info", "utm_params"]
    for field in required_fields:
        if field not in decrypted:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}",
            )

    if not isinstance(decrypted["events"], list):
        raise HTTPException(status_code=400, detail="Events must be a list")

    # -------------------------------------------------
    # Resolve geo (optional)
    # -------------------------------------------------

    client_ip = get_client_ip(request)
    geo = geo_provider.lookup(client_ip)

    # -------------------------------------------------
    # Build session metadata via enricher
    # -------------------------------------------------

    session_enricher = SessionEnricher(
        user_agent=request.headers.get("user-agent"),
        geo=geo,
    )

    session_meta = session_enricher.enrich(decrypted)

    # -------------------------------------------------
    # Publish events
    # -------------------------------------------------

    event_enricher = EventEnricher()
    event_validator = EventValidator()
    published_events = 0

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

        await sink.publish_event(
            settings.kafka_event_topic,
            decrypted["asset_id"],
            enriched_event,
        )

        published_events += 1

    # -------------------------------------------------
    # Publish session metadata (once per request)
    # -------------------------------------------------

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
