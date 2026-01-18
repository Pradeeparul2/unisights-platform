from app.core.settings import Settings
from app.ingestion.sink import EventSink
from app.ingestion.kafka_sink import KafkaSink
from app.ingestion.stdout_sink import StdoutSink


def create_sink(settings: Settings) -> EventSink:
    """
    Create and return the configured ingestion sink.

    Supported modes:
    - kafka
    - stdout
    """

    if settings.ingestion_mode == "kafka":
        return KafkaSink(settings)

    if settings.ingestion_mode == "stdout":
        return StdoutSink()

    raise ValueError(
        f"Unsupported INGESTION_MODE: {settings.ingestion_mode}"
    )
