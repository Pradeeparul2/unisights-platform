import logging
import sys
from typing import Optional

from app.core.settings import get_settings


class HealthFilter(logging.Filter):
    """
    Filter out noisy health/readiness logs.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        if record.args:
            msg = record.getMessage()
            return not (
                "/health" in msg or
                "/ready" in msg
            )
        return True


def setup_logging(level: Optional[str] = None) -> None:
    """
    Configure application-wide logging.

    - Logs to stdout (container-friendly)
    - Structured format
    - Environment-aware log level
    """

    settings = get_settings()

    log_level = level or (
        logging.DEBUG if settings.debug else logging.INFO
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers (important for reloads)
    while root_logger.handlers:
        root_logger.handlers.pop()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s "
            "%(levelname)s "
            "%(name)s "
            "%(message)s"
        ),
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    handler.setFormatter(formatter)
    handler.addFilter(HealthFilter())

    root_logger.addHandler(handler)

    # Reduce noisy third-party loggers
    logging.getLogger("kafka").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    root_logger.info(
        "Logging initialized",
        extra={
            "level": logging.getLevelName(log_level),
            "environment": settings.environment,
        },
    )
