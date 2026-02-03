from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class GeoProvider(ABC):
    """
    Abstract base class for Geo providers.

    Implementations:
    - MaxMindGeoProvider
    - NoGeoProvider
    """

    @abstractmethod
    def lookup(self, ip: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Resolve geo information for an IP address.

        Returns:
            {
              "country": str | None,
              "region": str | None,
              "city": str | None,
              "lat": float | None,
              "lon": float | None
            }
        """
        pass
