from typing import Dict, Any
import time

from app.enrichers.base import Enricher
from app.utils.time import now_ms



class EventEnricher(Enricher):
    """
    Builds event-level payloads.
    """

    def enrich(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        event = payload["event"]
        base = payload["base"]

        return {
            "schema_version": 1,
            "event_type": event["type"],
            "event_name": event.get("data", {}).get("name"),
            "event_timestamp": event.get("data", {}).get("timestamp"),
            "event_data": event.get("data"),
            "asset_id": base["asset_id"],
            "session_id": base["session_id"],
            "page_url": base.get("page_url"),
            "received_at": now_ms(),
        }
