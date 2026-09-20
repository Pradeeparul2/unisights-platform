# Unisights Helm Chart

Kubernetes (Helm) port of the `docker/docker-compose.yml` stack: Kafka (KRaft), Zookeeper,
Postgres, MinIO, Druid (coordinator/broker/historical/middleManager/router), the
`ingestion-service` FastAPI app, Kafdrop, and Superset.

## Prerequisites

- Helm 3.x, a Kubernetes cluster with a default (or named) `StorageClass`
- The `ingestion-service` image pushed to a registry you control
  (`docker/../ingestion-service/Dockerfile`) — set `ingestionService.image.repository/tag`
- A Superset image built from `docker/superset/Dockerfile` — set `superset.image`

## Install

```sh
helm install unisights ./k8s/helm/unisights \
  --set ingestionService.image.repository=ghcr.io/your-org/ingestion-service \
  --set ingestionService.image.tag=1.0.0 \
  --set superset.image=ghcr.io/your-org/unisights-superset:1.0.0 \
  -f values-secrets.yaml   # your own overrides for the `secrets:` block
```

Never commit real credentials into `values.yaml`. Override `secrets.*` via
`--set`, a gitignored `values-secrets.yaml`, or an External Secrets
Operator/Sealed Secrets in production.

## What maps to what

| docker-compose service                             | k8s resource                                                                                             |
| -------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| kafka                                              | StatefulSet + headless Service (`unisights-kafka`)                                                       |
| kafdrop                                            | Deployment + Service (optional, `kafdrop.enabled`)                                                       |
| ingestion-service                                  | Deployment + Service (+ optional HPA)                                                                    |
| postgres                                           | StatefulSet + Service, init script via ConfigMap mounted at `/docker-entrypoint-initdb.d`                |
| zookeeper                                          | StatefulSet + Service                                                                                    |
| coordinator/broker/historical/middlemanager/router | One templated Deployment/StatefulSet per role (`templates/druid.yaml`), looped over `values.druid.roles` |
| minio                                              | StatefulSet + Service                                                                                    |
| supervisor-deployer                                | Helm `post-install,post-upgrade` hook Job that submits the Kafka supervisor specs to Druid               |
| superset                                           | StatefulSet + Service, init script run as the container command                                          |

## Notable differences from docker-compose

- `depends_on: condition: service_healthy` has no direct k8s equivalent; each
  workload uses a `busybox` `initContainer` that polls the dependency's port
  before starting.
- Local bind mounts for scripts/specs became `ConfigMap`s. `docker/superset/main_dashboard.zip`
  (92KB, well under the 1MiB ConfigMap limit) is embedded via
  `files/superset/main_dashboard.zip` and base64-encoded into the
  `unisights-superset-dashboard` ConfigMap at render time (`.Files.Get | b64enc`),
  then mounted at `/app/main_dashboard.zip` for `init-superset.sh` to import on
  startup. Toggle with `superset.dashboard.enabled`. If the dashboard export grows
  past ~1MiB, switch to baking it into the Superset image or an initContainer that
  fetches it from object storage instead.
- Named Docker volumes became `PersistentVolumeClaim`s (`volumeClaimTemplates`
  on the StatefulSets). Set `storageClass` in `values.yaml` if you don't want
  the cluster default.
- Secrets (`POSTGRES_PASSWORD`, MinIO keys, Superset secret key/admin
  password) live in a single `Secret` (`unisights-secrets`) instead of `.env`.
- Non-persistent Druid roles (`broker`, `router`) run as `Deployment`s with an
  `emptyDir` for `/opt/druid/var` so they can scale/reschedule freely;
  persistent roles (`coordinator`, `historical`, `middlemanager`) are
  `StatefulSet`s with real PVCs.

## Not yet covered / next steps

- No `NetworkPolicy` restricting cross-service traffic.
- No TLS termination beyond what you configure on the `Ingress`.
- Flink jobs are commented out in compose and are intentionally not ported.
- Consider replacing self-hosted Kafka/Postgres with managed services (MSK,
  Confluent Cloud, RDS/Cloud SQL) for production; this chart assumes
  self-hosted for parity with the current compose setup.

helm upgrade --install unisights .\k8s\helm\unisights --set ingestionService.image.repository=unisights/ingestion-service --set ingestionService.image.tag=local --set superset.image=unisights/superset:local --set ingestionService.replicas=1

helm uninstall unisights -n unisights

kubectl get pods -n unisights -w

kubectl port-forward -n unisights svc/unisights-ingestion-service 8000:8000

kubectl port-forward -n unisights svc/unisights-superset 8088:8088

kubectl port-forward -n unisights svc/unisights-kafdrop 9003:9003

kubectl port-forward -n unisights svc/unisights-druid-router 8888:8888
