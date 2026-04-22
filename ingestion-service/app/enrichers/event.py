from typing import Dict, Any
import uuid

from app.enrichers.base import Enricher
from app.utils.time import now_ms
from app.utils.json import safe_json_loads



class EventEnricher(Enricher):
    """
    Builds event-level payloads.
    """

    def enrich(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        event = payload["event"]
        base = payload["base"]
        event_data = self._normalize_event_data(event.get("data"))

        return {
            "event_id": str(uuid.uuid4()),
            "schema_version": 1,
            "event_type": event["type"],
            "event_name": event_data.get("name"),
            "event_timestamp": event_data.get("timestamp"),
            "event_data": event_data,
            "asset_id": base["asset_id"],
            "session_id": base["session_id"],
            "page_url": base.get("page_url"),
            "received_at": now_ms(),
        }

    def _normalize_event_data(self, event_data: Any) -> Dict[str, Any]:
        if not isinstance(event_data, dict):
            return {}

        normalized = dict(event_data)
        nested_data = normalized.get("data")

        if isinstance(nested_data, str):
            try:
                normalized["data"] = safe_json_loads(nested_data)
            except ValueError:
                # Keep the original string when it is not valid JSON text.
                pass

        return normalized
