# Unisights - Real-Time Web Analytics Platform 🚀

Unisights is an **open-source, privacy-first real-time analytics platform**
designed for modern websites and applications. It empowers developers and
businesses to capture user interactions in real time, process them efficiently,
store data scalably, and visualize insights through interactive dashboards while
prioritizing user privacy and data ownership.

## 🌟 The Idea Behind Unisights

Unisights provides a self-hosted analytics solution for high-performance data
collection and actionable insights without relying on third-party services. It
is designed to run on your infrastructure, using WebAssembly for efficient
in-browser event tracking and a real-time processing and visualization pipeline.

The platform can track user sessions on high-traffic sites or analyze web
applications while keeping data ownership with the operator.

## Repository Components

- `ingestion-service/`: FastAPI service for receiving, validating, enriching,
  and publishing analytics events.
- `docker/`: Local Docker Compose environment for Kafka, Druid, MinIO,
  PostgreSQL, Superset, and the ingestion service.
- `docker/druid/supervisor_specs/`: Druid Kafka ingestion specifications.
- `docker/flink/`: Flink session aggregation prototype. Flink services are
  currently disabled in Compose.
- `k8s/helm/unisights/`: Helm chart for local Kubernetes and integration
  testing.
- `k8s/helm/unisights-prod/`: Production deployment overlay with external
  secrets, TLS ingress, autoscaling, resource guardrails, disruption budgets,
  and network policies.

## Architecture

```text
Browser or SDK
      |
      v
FastAPI ingestion service
      |
      v
Kafka events-stream and sessions-stream
      |
      v
Druid ingestion and query layer
      |
      v
Superset dashboards
```

MinIO stores Druid deep-storage data, while PostgreSQL stores Druid and
Superset metadata.

## Quick Start

Requirements:

- Docker Desktop with Docker Compose
- At least 8 GB of memory available to Docker for the complete stack

Start the local platform:

```powershell
cd docker
docker compose up --build
```

Run it in the background:

```powershell
docker compose up --build -d
```

The main local URLs are:

- Ingestion API: <http://localhost:8000>
- Ingestion API docs: <http://localhost:8000/docs>
- Kafka UI: <http://localhost:9003>
- Druid router: <http://localhost:8888>
- Superset: <http://localhost:8088>
- MinIO console: <http://localhost:9001>

For service-specific setup, configuration, API details, and troubleshooting,
see [docker/README.md](docker/README.md) and
[ingestion-service/README.md](ingestion-service/README.md).

## Kubernetes

Use the local Helm chart for minikube, kind, or development clusters. It
includes the complete self-hosted stack and is intended for integration testing:

```powershell
helm dependency build .\k8s\helm\unisights
helm lint .\k8s\helm\unisights
```

For production deployment, use the separate production overlay. It requires
immutable images, a pre-provisioned external Secret, TLS/DNS infrastructure,
and a production StorageClass:

```powershell
helm dependency build .\k8s\helm\unisights-prod
helm lint .\k8s\helm\unisights-prod
```

See the [local Kubernetes chart guide](k8s/helm/unisights/README.md) and the
[production Kubernetes guide](k8s/helm/unisights-prod/README.md) for required
values, validation, and install commands.

## Local Ingestion Development

From `ingestion-service/`, install the Python dependencies and run the service
without Docker:

```powershell
python -m pip install -r requirements.txt
$env:INGESTION_MODE='stdout'
$env:GEO_PROVIDER='none'
uvicorn app.main:app --reload
```

Run the unit tests:

```powershell
python -m pytest -q
```

## Documentation

- [Docker stack guide](docker/README.md): Compose services, ports, startup,
  configuration, and troubleshooting.
- [Ingestion service guide](ingestion-service/README.md): local development,
  API behavior, configuration, and tests.
- [Local Kubernetes chart guide](k8s/helm/unisights/README.md): Helm values,
  local cluster deployment, and service access.
- [Production Kubernetes guide](k8s/helm/unisights-prod/README.md): production
  prerequisites, secret contract, deployment, and HA work.

## Data and Privacy

The ingestion service publishes event and session records rather than raw
client IP addresses. It can derive approximate GeoIP fields from the request
address and adds user-agent and receive-time metadata. Review the ingestion
service privacy documentation before deploying with real user data.

## Security

The Docker configuration is intended for local development. Replace all
development passwords, MinIO keys, and Superset secret keys before using the
stack outside a private local environment. Do not commit production secrets or
expose Kafka, PostgreSQL, MinIO, Druid coordinator/broker, or an unauthenticated
Superset instance directly to the public internet. Use the production Helm
overlay with TLS ingress and externally managed secrets for cluster deployment.

## Repository Status

The ingestion and Kafka-to-Druid path is the active implementation. Encryption
modules and the Flink session aggregation job are present as supporting or
prototype components and should be verified against the active runtime before
production use.
