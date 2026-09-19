# Unisights Ingestion Service

FastAPI service that receives Unisights analytics payloads, enriches them with
session and request metadata, and publishes event and session records to Kafka
or stdout.

## Responsibilities

- Receive analytics payloads at `POST /collect/events`.
- Validate individual events and skip malformed events.
- Add session metadata, user-agent information, receive timestamps, and optional
  MaxMind GeoIP data.
- Publish individual events to the configured event topic.
- Publish session metadata to the configured session topic.
- Expose liveness and readiness endpoints for container orchestration.

The service is part of the larger local stack in `../docker`, which also
contains Kafka, Flink, Druid, MinIO, PostgreSQL, and Superset configuration.

## Requirements

- Python 3.12 or newer
- A Kafka broker for Kafka mode
- The MaxMind database at `geo/GeoLite2-City.mmdb` when GeoIP is enabled

Install dependencies from the service directory:

```powershell
python -m pip install -r requirements.txt
```

## Run Locally

For a Kafka-backed local run, configure the broker and database paths first:

```powershell
$env:KAFKA_BROKERS='["localhost:9092"]'
$env:GEOIP_DB_PATH='geo/GeoLite2-City.mmdb'
$env:INGESTION_MODE='kafka'
uvicorn app.main:app --reload
```

For development without Kafka, use the stdout sink:

```powershell
$env:INGESTION_MODE='stdout'
$env:GEO_PROVIDER='none'
uvicorn app.main:app --reload
```

The service listens on `http://localhost:8000`. Interactive API documentation
is available at `http://localhost:8000/docs`.

## Docker Compose

From the repository's `docker` directory:

```powershell
docker compose up --build ingestion-service kafka
```

The Compose configuration supplies the container broker address
`kafka:9092`. Do not use `localhost:9092` from inside the ingestion-service
container because that points back to the container itself.

## Configuration

Settings are loaded from environment variables and an optional `.env` file.

| Variable           | Default                  | Description                          |
| ------------------ | ------------------------ | ------------------------------------ |
| `INGESTION_MODE`   | `kafka`                  | `kafka` or `stdout`                  |
| `KAFKA_BROKERS`    | `["localhost:9092"]`     | JSON list of Kafka brokers           |
| `EVENT_TOPIC`      | `events-stream`          | Kafka topic for individual events    |
| `SESSION_TOPIC`    | `sessions-stream`        | Kafka topic for session metadata     |
| `KAFKA_LINGER_MS`  | `10`                     | Kafka producer linger time           |
| `KAFKA_BATCH_SIZE` | `16384`                  | Kafka producer batch size            |
| `GEO_PROVIDER`     | `maxmind`                | `maxmind` or `none`                  |
| `GEOIP_DB_PATH`    | `geo/GeoLite2-City.mmdb` | MaxMind database path                |
| `CORS_ORIGINS`     | localhost ports 3000     | JSON list of allowed browser origins |
| `PORT`             | `8000`                   | Service port                         |

Complex values such as `KAFKA_BROKERS` and `CORS_ORIGINS` must be valid JSON
arrays when supplied through environment variables.

## Endpoints

### `POST /collect/events`

Receives an analytics payload through the Unisights FastAPI integration. The
payload must contain:

```json
{
  "asset_id": "site-123",
  "session_id": "session-456",
  "events": [
    {
      "type": "page_view",
      "data": {
        "name": "page_view",
        "timestamp": 1710000000000
      }
    }
  ],
  "device_info": {},
  "utm_params": {}
}
```

Each accepted event receives an event ID, schema version, receive timestamp,
asset ID, session ID, and page URL. A separate session record is published for
the payload.

### `GET /health`

Returns a liveness response indicating that the process is running.

### `GET /ready`

Returns readiness when the configured sink has initialized. Kafka mode also
checks the producer connection state.

## Testing

Run the unit test suite from this directory:

```powershell
python -m pytest -q
```

The tests cover validators, event and session enrichment, and the stdout sink.

## Project Layout

```text
app/main.py                 FastAPI application and ingestion handler
app/core/settings.py        Environment-backed configuration
app/validators/             Payload and event validation
app/enrichers/              Session and event enrichment
app/ingestion/              Kafka and stdout sink implementations
app/geo/                    GeoIP provider implementations
app/crypto/                 Payload decryptor implementations
tests/                      Unit tests
```

## Operational Notes

- Kafka mode requires the broker to be reachable before application startup.
- The MaxMind database is optional only when `GEO_PROVIDER=none`.
- The service does not intentionally publish the client IP address; it stores
  derived GeoIP fields instead.
- Configure trusted proxy behavior before relying on forwarded client-IP
  headers in production.
- Keep Kafka credentials, encryption secrets, and database credentials out of
  source control.
