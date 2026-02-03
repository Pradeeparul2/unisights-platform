from app.core.settings import Settings
from app.geo.provider import GeoProvider
from app.geo.maxmind import MaxMindGeoProvider


class NoGeoProvider(GeoProvider):
    """
    No-op geo provider.
    Always returns None.
    """

    def lookup(self, ip: str | None):
        return None


def create_geo_provider(settings: Settings) -> GeoProvider:
    """
    Create and return the configured geo provider.

    Supported providers:
    - maxmind
    - none
    """

    if settings.geo_provider == "maxmind":
        return MaxMindGeoProvider(settings)

    if settings.geo_provider == "none":
        return NoGeoProvider()

    raise ValueError(
        f"Unsupported GEO_PROVIDER: {settings.geo_provider}"
    )
