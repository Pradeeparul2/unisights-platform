import json
import pytest
from app.ingestion.stdout_sink import StdoutSink


@pytest.mark.asyncio
async def test_stdout_sink_event(capsys):
    sink = StdoutSink()
    await sink.start()

    await sink.publish_event(
        topic="analytics.events",
        key="asset-1",
        event={"foo": "bar"},
    )

    captured = capsys.readouterr()
    data = json.loads(captured.out)

    assert data["type"] == "event"
    assert data["topic"] == "analytics.events"
    assert data["key"] == "asset-1"
    assert data["data"]["foo"] == "bar"


@pytest.mark.asyncio
async def test_stdout_sink_session(capsys):
    sink = StdoutSink()
    await sink.start()

    await sink.publish_session(
        topic="analytics.sessions",
        key="asset-1",
        session={"session_id": "abc"},
    )

    captured = capsys.readouterr()
    data = json.loads(captured.out)

    assert data["type"] == "session"
    assert data["data"]["session_id"] == "abc"
