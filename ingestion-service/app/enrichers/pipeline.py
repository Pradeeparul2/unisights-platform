from typing import Dict, Any, List
from app.enrichers.base import Enricher


class EnrichmentPipeline:
    """
    Applies a list of enrichers sequentially.
    """

    def __init__(self, enrichers: List[Enricher]):
        self.enrichers = enrichers

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = payload
        for enricher in self.enrichers:
            data = enricher.enrich(data)
        return data
