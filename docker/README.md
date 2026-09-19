# Unisights Docker Stack

This directory contains the Docker Compose environment for the Unisights analytics platform. It runs the ingestion service, Kafka, Druid, MinIO, PostgreSQL, Superset, and supporting services for local development and integration testing.

## Architecture

```text
Analytics SDK
    |
    v
Ingestion Service :8000
    |
    v
Kafka :9092 (internal) / :9093 (host)
    |
    +--> Druid supervisor specs --> Druid
    |
    +--> Optional Flink processing

Druid --> Superset
Druid segments and task logs --> MinIO
Druid and Superset metadata --> PostgreSQL
```

## Requirements

- Docker Desktop with Docker Compose support
- At least 8 GB of memory available to Docker for the complete stack
- Ports listed below available on the host

## Start the Stack

Run commands from this directory:

```powershell
docker compose up --build
```

To start in the background:

```powershell
docker compose up --build -d
```

Compose reads configuration from `.env` in this directory. The ingestion service is built from `../ingestion-service`.

For a smaller ingestion-only environment:

```powershell
docker compose up --build kafka ingestion-service
```

## Services and Ports

| Service             |      Host port | Purpose                               |
| ------------------- | -------------: | ------------------------------------- |
| `ingestion-service` |         `8000` | Analytics HTTP ingestion API          |
| `kafka`             | `9092`, `9093` | Internal and external Kafka listeners |
| `kafdrop`           |         `9003` | Kafka web UI                          |
| `postgres`          |         `5432` | Druid and Superset metadata database  |
| `zookeeper`         |         `2181` | Druid coordination service            |
| `coordinator`       |         `8081` | Druid coordinator and indexing API    |
| `broker`            |         `8082` | Druid query broker                    |
| `historical`        |         `8083` | Druid historical node                 |
| `middlemanager`     |         `8091` | Druid task execution                  |
| `router`            |         `8888` | Druid web/API router                  |
| `minio`             |         `9000` | S3-compatible deep storage API        |
| `minio`             |         `9001` | MinIO web console                     |
| `superset`          |         `8088` | Analytics dashboards                  |

The Flink job manager, task manager, and submitter definitions are currently commented out in `docker-compose.yml`. The Flink source files remain under `flink/` for future use.

## Useful URLs

- Ingestion API: <http://localhost:8000>
- Ingestion API docs: <http://localhost:8000/docs>
- Ingestion health: <http://localhost:8000/health>
- Kafdrop: <http://localhost:9003>
- Druid router: <http://localhost:8888>
- Druid coordinator: <http://localhost:8081>
- Superset: <http://localhost:8088>
- MinIO console: <http://localhost:9001>

## Data Flow

1. `ingestion-service` publishes individual events to `events-stream`.
2. `ingestion-service` publishes session metadata to `sessions-stream`.
3. `supervisor-deployer` submits the JSON supervisor specifications in `druid/supervisor_specs/` to Druid.
4. Druid reads Kafka data and stores segments in the MinIO `druid-segments` bucket.
5. Superset connects to Druid through the Druid broker and imports the bundled dashboard when available.

The `supervisor-deployer` is a one-shot container. It waits for Kafka, the ingestion service, the Druid coordinator, and the Druid broker to become healthy before submitting the supervisors.

## Configuration

The main configuration file is `.env`. Important settings include:

- `INGESTION_KAFKA_BROKERS`: broker address used by the ingestion container; normally `kafka:9092`.
- `INGESTION_EVENT_TOPIC`: event topic, default `events-stream`.
- `INGESTION_SESSION_TOPIC`: session topic, default `sessions-stream`.
- `KAFKA_ADVERTISED_LISTENERS`: Kafka listener addresses. Containers use `kafka:9092`; host applications use `localhost:9093`.
- `DRUID_POSTGRES_*`: Druid metadata database credentials.
- `MINIO_ROOT_USER` and `MINIO_ROOT_PASSWORD`: MinIO credentials.
- `SUPERSET_*`: Superset metadata database and secret-key settings.

Container-to-container connections must use service names such as `kafka`, `postgres`, `broker`, and `minio`, not `localhost`.

## Common Commands

View running containers:

```powershell
docker compose ps
```

Follow ingestion logs:

```powershell
docker compose logs -f ingestion-service
```

Follow the Druid supervisor deployment:

```powershell
docker compose logs -f supervisor-deployer
```

Restart one service:

```powershell
docker compose restart ingestion-service
```

Stop the stack while preserving named volumes:

```powershell
docker compose down
```

Stop the stack and remove stored data:

```powershell
docker compose down -v
```

The `-v` option deletes Kafka-related runtime data, Druid data, MinIO data, PostgreSQL metadata, and Superset home data. Use it only when a clean local environment is intended.

## Troubleshooting

### Ingestion service is unhealthy

Check the service and Kafka logs:

```powershell
docker compose logs ingestion-service kafka
```

The ingestion service waits for Kafka health before starting. From inside the Compose network, the broker address must be `kafka:9092`.

### Supervisor deployment fails

Inspect the deployment logs and confirm that Druid coordinator, broker, Kafka, and ingestion service are healthy:

```powershell
docker compose logs supervisor-deployer coordinator broker
```

Supervisor definitions are stored in `druid/supervisor_specs/`. Re-run the one-shot deployment with:

```powershell
docker compose up supervisor-deployer
```

### Superset does not start

Superset depends on PostgreSQL, Druid coordinator, and the Druid broker. Check those services first:

```powershell
docker compose logs postgres coordinator broker superset
```

### Kafka access from the host fails

Use `localhost:9093` from applications running on the host. Use `kafka:9092` only from containers attached to `unisights-network`.

## Security Notes

The checked-in `.env` contains development credentials and defaults. Replace all passwords, access keys, and secret keys before using this stack outside a local development environment. Do not expose Kafka, PostgreSQL, MinIO, Druid, or Superset directly to the public internet without authentication and network controls.

The Compose file also contains development fallback credentials for PostgreSQL, MinIO, and Superset. Explicitly set the corresponding environment variables in a private deployment configuration.

## Related Documentation

- Ingestion service: `../ingestion-service/README.md`
- Druid supervisor specifications: `druid/supervisor_specs/`
- Druid runtime configuration: `druid/environment`
- MinIO policy: `minio/policy.json`
- Superset initialization: `superset/init-superset.sh`
- Flink session job: `flink/session_aggregator.py`
