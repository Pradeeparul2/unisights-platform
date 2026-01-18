from typing import Dict, Any

from app.validators.base import Validator


class EventValidator(Validator):
    """
    Validates a single analytics event.
    """

    REQUIRED_FIELDS = {
        "type": str,
        "data": dict,
    }

    def validate(self, event: Dict[str, Any]) -> None:
        for field, expected_type in self.REQUIRED_FIELDS.items():
            if field not in event:
                raise ValueError(f"Event missing field: {field}")

            if not isinstance(event[field], expected_type):
                raise ValueError(
                    f"Invalid type for event field '{field}', expected {expected_type.__name__}"
                )

        # Optional: enforce timestamp presence if you want
        timestamp = event["data"].get("timestamp")
        if timestamp is not None and not isinstance(timestamp, (int, float)):
            raise ValueError("Event timestamp must be a number")
