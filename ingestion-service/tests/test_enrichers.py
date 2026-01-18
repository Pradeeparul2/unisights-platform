from app.enrichers.session import SessionEnricher
from app.enrichers.event import EventEnricher


def test_session_enricher():
    payload = {
        "asset_id": "a1",
        "session_id": "s1",
        "page_url": "/",
        "device_info": {"os": "Linux"},
        "utm_params": {"utm_source": "google"},
    }

    enricher = SessionEnricher(
        user_agent="test-agent",
        geo={"country": "IN"},
    )

    session = enricher.enrich(payload)

    assert session["asset_id"] == "a1"
    assert session["geo"]["country"] == "IN"
    assert session["user_agent"] == "test-agent"
    assert session["schema_version"] == 1


def test_event_enricher():
    enricher = EventEnricher()

    enriched = enricher.enrich({
        "base": {
            "asset_id": "a1",
            "session_id": "s1",
            "page_url": "/pricing",
        },
        "event": {
            "type": "click",
            "data": {"name": "buy", "timestamp": 123},
        },
    })

    assert enriched["event_type"] == "click"
    assert enriched["event_name"] == "buy"
    assert enriched["asset_id"] == "a1"
