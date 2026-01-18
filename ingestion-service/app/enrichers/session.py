from typing import Dict, Any, Optional
import time

from app.enrichers.base import Enricher
from app.utils.time import now_ms


class SessionEnricher(Enricher):
    """
    Builds session-level metadata.
    """

    def __init__(
        self,
        user_agent: Optional[str],
        geo: Optional[Dict[str, Any]],
    ):
        self.user_agent = user_agent
        self.geo = geo

    def enrich(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "schema_version": 1,
            "asset_id": payload["asset_id"],
            "session_id": payload["session_id"],
            "page_url": payload.get("page_url"),
            "entry_page": payload.get("entry_page"),
            "exit_page": payload.get("exit_page"),
            "scroll_depth": payload.get("scroll_depth"),
            "time_on_page": payload.get("time_on_page"),
            "device": payload.get("device_info"),
            "utm": payload.get("utm_params"),
            "geo": self.geo,
            "user_agent": self.user_agent,
            "received_at": now_ms(),
        }
