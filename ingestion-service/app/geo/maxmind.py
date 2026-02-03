import logging
from typing import Optional, Dict, Any

import geoip2.database
import geoip2.errors

from app.geo.provider import GeoProvider
from app.core.settings import Settings

logger = logging.getLogger(__name__)


class MaxMindGeoProvider(GeoProvider):
    """
    Geo provider using MaxMind GeoLite2 database.
    """

    def __init__(self, settings: Settings):
        self.db_path = settings.geoip_db_path
        self.reader: geoip2.database.Reader | None = None

        try:
            self.reader = geoip2.database.Reader(self.db_path)
            logger.info(
                "MaxMind GeoIP database loaded",
                extra={"path": self.db_path},
            )
        except Exception as e:
            logger.exception("Failed to load MaxMind GeoIP database")
            raise RuntimeError("GeoIP database initialization failed") from e

    def lookup(self, ip: Optional[str]) -> Optional[Dict[str, Any]]:
        if not ip or not self.reader:
            return None

        try:
            geo = self.reader.city(ip)
            return {
                "country": geo.country.iso_code,
                "region": geo.subdivisions.most_specific.name,
                "city": geo.city.name,
                "lat": geo.location.latitude,
                "lon": geo.location.longitude,
            }
        except geoip2.errors.AddressNotFoundError:
            # Common for private / unknown IPs
            return None
        except Exception as e:
            logger.warning(f"Geo lookup failed: {e}")
            return None
