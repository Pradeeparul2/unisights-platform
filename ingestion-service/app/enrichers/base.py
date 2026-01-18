from abc import ABC, abstractmethod
from typing import Dict, Any


class Enricher(ABC):
    """
    Base class for all enrichers.
    """

    @abstractmethod
    def enrich(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        pass
