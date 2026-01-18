from abc import ABC, abstractmethod
from typing import Dict, Any


class EventSink(ABC):
    """
    Abstract base class for ingestion sinks.

    A sink is responsible for delivering:
    - session metadata
    - individual events

    Implementations:
    - KafkaSink
    - StdoutSink
    - (future) HttpSink, FileSink
    """

    @abstractmethod
    async def start(self) -> None:
        """
        Initialize the sink.
        Called once on application startup.
        """
        pass

    @abstractmethod
    async def stop(self) -> None:
        """
        Clean up resources.
        Called once on application shutdown.
        """
        pass

    @abstractmethod
    async def publish_event(
        self,
        topic: str,
        key: str,
        event: Dict[str, Any],
    ) -> None:
        """
        Publish a single analytics event.
        """
        pass

    @abstractmethod
    async def publish_session(
        self,
        topic: str,
        key: str,
        session: Dict[str, Any],
    ) -> None:
        """
        Publish session-level metadata.
        """
        pass
