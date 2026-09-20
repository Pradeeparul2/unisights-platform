# Unisights Production Helm Chart

`unisights-prod` is a production deployment overlay for the local `unisights`
chart. It enables production-oriented defaults without changing the local chart:
TLS ingress, an external Secret contract, ingestion autoscaling, Druid query
role replicas, resource guardrails, disruption budgets, and namespace network
policies.

## Prerequisites

- Kubernetes cluster with a production StorageClass and a CNI that enforces
  `NetworkPolicy` resources.
- Helm 3.15+ and `kubectl` access to the target cluster.
- NGINX Ingress Controller and cert-manager (or equivalent controllers).
- DNS records for the configured ingestion, Superset, and Druid hosts.
- Metrics Server for the ingestion-service HPA.
- Immutable images for `ingestion-service` and Superset, published to a private
  registry accessible to the cluster.
- A Secret manager, such as External Secrets Operator, Sealed Secrets, or your
  cloud provider's secret integration.

## Required Configuration

Before deploying, create a protected environment-specific values file (for
example, `values.production.yaml`) that overrides every `REPLACE_WITH_*` value
in [values.yaml](values.yaml):

```yaml
namespace: unisights-production

production:
  hosts:
    ingestion: ingest.analytics.example.com
    superset: analytics.example.com
    druidRouter: druid.analytics.example.com
  tlsSecretName: unisights-production-tls

unisights:
  storageClass: gp3-encrypted
  ingestionService:
    image:
      repository: registry.example.com/unisights/ingestion-service
      tag: "1.0.0"
  superset:
    image: registry.example.com/unisights/superset:1.0.0
  ingress:
    className: nginx
    annotations:
      cert-manager.io/cluster-issuer: letsencrypt-prod
    hosts:
      ingestion: ingest.analytics.example.com
      superset: analytics.example.com
      kafdrop: disabled.example.invalid
      druidRouter: druid.analytics.example.com
    tls:
      - secretName: unisights-production-tls
        hosts:
          - ingest.analytics.example.com
          - analytics.example.com
          - druid.analytics.example.com
```

Use image digests in regulated or high-assurance environments instead of tags.

## Secrets

The chart never creates a Secret when
`unisights.secrets.existingSecret` is set. Provision the Secret named
`unisights-production-secrets` in the `unisights-production` namespace before
installing. It must expose these keys:

```text
POSTGRES_PASSWORD
SUPERSET_DB_USER
SUPERSET_DB_PASSWORD
SUPERSET_SECRET_KEY
SUPERSET_ADMIN_PASSWORD
MINIO_ROOT_USER
MINIO_ROOT_PASSWORD
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

Use External Secrets or an equivalent controller to source these values from a
managed secret store. Do not pass secrets through Helm `--set` arguments or
commit them to an override file.

## Install

Build the local chart dependency, then validate and install the release:

```sh
helm dependency build ./k8s/helm/unisights-prod

helm lint ./k8s/helm/unisights-prod
helm template unisights-production ./k8s/helm/unisights-prod \
  -f values.production.yaml | kubectl apply --dry-run=server -f -

helm upgrade --install unisights-production ./k8s/helm/unisights-prod \
  --namespace unisights-production \
  --create-namespace \
  -f values.production.yaml \
  --wait --timeout 20m
```

Validate the deployment after installation:

```sh
kubectl get pods,svc,ingress,pdb,hpa -n unisights-production
kubectl get networkpolicy,resourcequota,limitrange -n unisights-production
kubectl rollout status deployment/unisights-ingestion-service -n unisights-production
kubectl rollout status deployment/unisights-druid-broker -n unisights-production
```

## Included Controls

- TLS-only NGINX Ingress configuration with cert-manager annotations.
- Kafdrop disabled; it is not a production access surface.
- Three baseline ingestion-service replicas with an HPA from 3 to 12 pods.
- Two Druid brokers and routers, two historicals, and three middleManagers.
- Druid ingestion task JVM memory bounds and four task slots per middleManager.
- ResourceQuota and LimitRange to stop unbounded namespace resource use.
- PodDisruptionBudgets for ingestion-service, broker, and router.
- Default-deny ingress policy with explicit access from workload pods and the
  `ingress-nginx` namespace.
- Explicit Superset SQLAlchemy configuration using PostgreSQL metadata storage.

## Required HA Work

The dependency still includes single-node Kafka, PostgreSQL, MinIO, and
Zookeeper for functional compatibility with local development. These must be
replaced with managed or HA-operated services before claiming full production
availability or durability:

- Managed Kafka or an operator-managed multi-broker KRaft cluster with TLS,
  ACLs, replication, retention, and backup strategy.
- Managed PostgreSQL or a HA PostgreSQL cluster with PITR backups and restore
  drills.
- Durable object storage (such as cloud S3) rather than single-node MinIO.
- Backup and restore procedures for Druid metadata, deep storage, and Superset
  metadata.
- Centralized logs, metrics, alerting, and regular capacity/load testing.

Do not expose Kafka, PostgreSQL, MinIO, Druid coordinator, or the Druid broker
publicly. Only the ingestion endpoint, authenticated Superset UI, and (when
needed) a separately protected Druid Router endpoint belong behind Ingress.
