from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional


class Settings(BaseSettings):
    # ------------------------------------------------------------------
    # App
    # ------------------------------------------------------------------
    app_name: str = "unisights-analytics"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    port: int = Field(default=8000, env="PORT")

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------
    ingestion_mode: str = Field(
        default="kafka",
        env="INGESTION_MODE",
        description="kafka | stdout"
    )

    # ------------------------------------------------------------------
    # Kafka
    # ------------------------------------------------------------------
    kafka_brokers: List[str] = Field(
        default=["localhost:9092"],
        env="KAFKA_BROKERS"
    )
    kafka_event_topic: str = Field(
        default="analytics.events",
        env="EVENT_TOPIC"
    )
    kafka_session_topic: str = Field(
        default="analytics.sessions",
        env="SESSION_TOPIC"
    )
    kafka_retries: int = Field(default=5, env="KAFKA_RETRIES")
    kafka_linger_ms: int = Field(default=10, env="KAFKA_LINGER_MS")
    kafka_batch_size: int = Field(default=16384, env="KAFKA_BATCH_SIZE")

    # ------------------------------------------------------------------
    # Geo
    # ------------------------------------------------------------------
    geo_provider: str = Field(
        default="maxmind",
        env="GEO_PROVIDER",
        description="maxmind | none"
    )
    geoip_db_path: str = Field(
        default="geo/GeoLite2-City.mmdb",
        env="GEOIP_DB_PATH"
    )

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        env="CORS_ORIGINS",
    )

    # ------------------------------------------------------------------
    # Rate limiting (future use)
    # ------------------------------------------------------------------
    rate_limit_enabled: bool = Field(default=False, env="RATE_LIMIT_ENABLED")
    rate_limit_per_minute: int = Field(default=600, env="RATE_LIMIT_PER_MINUTE")

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance.
    Ensures settings are loaded once per process.
    """
    settings = Settings()

    # ---- Runtime validation ----

    if settings.ingestion_mode not in {"kafka", "stdout"}:
        raise RuntimeError(
            f"Invalid INGESTION_MODE: {settings.ingestion_mode}"
        )

    if settings.geo_provider not in {"maxmind", "none"}:
        raise RuntimeError(
            f"Invalid GEO_PROVIDER: {settings.geo_provider}"
        )

    return settings
