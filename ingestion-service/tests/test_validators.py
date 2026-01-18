import pytest
from app.validators.payload import PayloadValidator
from app.validators.event import EventValidator


def test_payload_validator_valid():
    payload = {
        "asset_id": "a1",
        "session_id": "s1",
        "events": [{}],
        "device_info": {},
        "utm_params": {},
    }

    PayloadValidator().validate(payload)


def test_payload_validator_missing_field():
    payload = {
        "asset_id": "a1",
        "events": [],
        "device_info": {},
        "utm_params": {},
    }

    with pytest.raises(ValueError):
        PayloadValidator().validate(payload)


def test_event_validator_valid():
    event = {
        "type": "page_view",
        "data": {"timestamp": 123},
    }

    EventValidator().validate(event)


def test_event_validator_invalid():
    event = {
        "type": "page_view",
        "data": "not-a-dict",
    }

    with pytest.raises(ValueError):
        EventValidator().validate(event)
