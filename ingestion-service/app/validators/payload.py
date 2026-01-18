import logging
from typing import Dict, Any

from app.validators.base import Validator

logger = logging.getLogger(__name__)

class PayloadValidator(Validator):
    """
    Validates decrypted analytics payload.
    """

    REQUIRED_FIELDS = {
        "asset_id": str,
        "session_id": str,
        "events": list,
        "device_info": dict,
        "utm_params": dict,
    }

    def validate(self, data: Dict[str, Any]) -> None:
        for field, expected_type in self.REQUIRED_FIELDS.items():
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

            if not isinstance(data[field], expected_type):
                raise ValueError(
                    f"Invalid type for '{field}', expected {expected_type.__name__}"
                )

        # Optional sanity checks
        if len(data["events"]) == 0:
            # No events to ingest, but session metadata may still matter
            logger.debug(
                "Empty events list received",
                extra={
                    "asset_id": data.get("asset_id"),
                    "session_id": data.get("session_id"),
                },
            )
            return {"status": "accepted", "events": 0}
