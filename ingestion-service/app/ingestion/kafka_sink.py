import json
import logging
from typing import Dict, Any

from kafka import KafkaProducer
from kafka.errors import KafkaError

from app.core.settings import Settings
from app.ingestion.sink import EventSink

logger = logging.getLogger(__name__)


class KafkaSink(EventSink):
    """
    Kafka-based ingestion sink.
    Publishes session and event data to Kafka topics.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.producer: KafkaProducer | None = None

    async def start(self) -> None:
        """
        Initialize Kafka producer.
        """
        logger.info("Initializing Kafka sink")

        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.settings.kafka_brokers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                retries=self.settings.kafka_retries,
                batch_size=self.settings.kafka_batch_size,
                linger_ms=self.settings.kafka_linger_ms,
            )
            logger.info(
                "Kafka producer ready",
                extra={"brokers": self.settings.kafka_brokers},
            )
        except KafkaError as e:
            logger.exception("Failed to initialize Kafka producer")
            raise RuntimeError("Kafka initialization failed") from e

    async def stop(self) -> None:
        """
        Close Kafka producer gracefully.
        """
        if self.producer:
            logger.info("Closing Kafka producer")
            self.producer.close()
            self.producer = None

    async def publish_event(
        self,
        topic: str,
        key: str,
        event: Dict[str, Any],
    ) -> None:
        """
        Publish a single event message.
        """
        if not self.producer:
            raise RuntimeError("Kafka producer not initialized")

        try:
            future = self.producer.send(
                topic=topic,
                key=key.encode("utf-8"),
                value=event,
            )
            future.add_errback(
                lambda e: logger.error(f"Kafka event publish failed: {e}")
            )
        except KafkaError as e:
            logger.error("Kafka publish_event error", exc_info=e)

    async def publish_session(
        self,
        topic: str,
        key: str,
        session: Dict[str, Any],
    ) -> None:
        """
        Publish session-level metadata.
        """
        if not self.producer:
            raise RuntimeError("Kafka producer not initialized")

        try:
            future = self.producer.send(
                topic=topic,
                key=key.encode("utf-8"),
                value=session,
            )
            future.add_errback(
                lambda e: logger.error(f"Kafka session publish failed: {e}")
            )
        except KafkaError as e:
            logger.error("Kafka publish_session error", exc_info=e)
