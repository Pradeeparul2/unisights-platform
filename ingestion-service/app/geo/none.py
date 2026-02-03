from typing import Optional, Dict, Any
from app.geo.provider import GeoProvider


class NoGeoProvider(GeoProvider):
    """
    Geo provider that disables geolocation.
    """

    def lookup(self, ip: Optional[str]) -> Optional[Dict[str, Any]]:
        return None
