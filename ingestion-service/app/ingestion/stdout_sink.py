import json
import logging
from typing import Dict, Any

from app.ingestion.sink import EventSink

logger = logging.getLogger(__name__)


class StdoutSink(EventSink):
    """
    Stdout-based ingestion sink.

    Used for:
    - Local development
    - CI / testing
    - Demos
    - Kafka-less deployments

    Writes events as JSON to stdout.
    """

    async def start(self) -> None:
        logger.info("Stdout sink initialized")

    async def stop(self) -> None:
        logger.info("Stdout sink stopped")

    async def publish_event(
        self,
        topic: str,
        key: str,
        event: Dict[str, Any],
    ) -> None:
        payload = {
            "type": "event",
            "topic": topic,
            "key": key,
            "data": event,
        }
        print(json.dumps(payload, ensure_ascii=False))

    async def publish_session(
        self,
        topic: str,
        key: str,
        session: Dict[str, Any],
    ) -> None:
        payload = {
            "type": "session",
            "topic": topic,
            "key": key,
            "data": session,
        }
        print(json.dumps(payload, ensure_ascii=False))
