+++
slug = "deploying-grafana-loki-on-kubernetes"
lastmod = "2026-10-27"
title = "Deploying Grafana Loki on Kubernetes"
description = "Lessons from deploying Loki with Rook Ceph object storage: log architecture, tenant isolation, versioned Helm configuration and operational checks."
date =  "2024-10-22"
draft = false
toc = true
categories = ["loki", "kubernetes", "grafana"]
tags = ["loki", "kubernetes", "grafana", "log aggregation", "monitoring"]
image = "architecture.svg"
author = "Fabio M. Lopes"
+++

I deployed Loki as part of an observability platform on a seven-node, AlmaLinux bare-metal Kubernetes cluster, using Rook Ceph for object storage. The goal was to centralize logs from infrastructure services, including Ceph and HAProxy, and query them through Grafana.

**Technical revision — October 2026:** the original article incorrectly described Mimir as Loki's log-storage backend and reversed the release/chart arguments in the installation command. The architecture and commands below correct those errors. The versioned example is a historical reference, not a recommendation to start a new production deployment on these releases.

## Where logs and metrics go

Loki ingests and queries **logs**. Mimir ingests and queries **Prometheus metrics**. Each uses its own buckets in the S3-compatible Ceph object store; Grafana queries both as separate data sources. Mimir is not in Loki's log-storage path.

```text
Log files → collector → authenticating gateway → Loki → Ceph S3 log buckets
Prometheus → authenticating gateway → Mimir → Ceph S3 metric buckets
Grafana → Loki (LogQL) and Mimir (PromQL)
```

Loki's distributors accept writes and route them to ingesters. Ingesters maintain recent data and write chunks to object storage. Queriers retrieve log data from ingesters and storage; query frontends and schedulers coordinate query work. The compactor handles index compaction and, when explicitly configured, retention.

Labels identify streams. High-cardinality labels can greatly increase stream count and index overhead; they should not be described as creating one index shard per label. Keep labels bounded and use log content or structured metadata for values such as request IDs.

## Versioned configuration

The downloadable [values.yaml](values.yaml) targets **grafana/loki chart 6.24.0, Loki 3.3.2**, with a Kubernetes 1.30 rendering target. These are reference versions selected for this revision; the original deployment's exact chart version was not recorded in the article. The example was checked with Helm 3.17.3 using lint and template rendering. It has not been installed into a cluster during this revision.

For a new deployment, select supported versions and follow the [current Loki installation guide](https://grafana.com/docs/loki/latest/setup/install/helm/install-microservices/). The chart has since moved to the Grafana Community repository; review its migration instructions instead of applying these historical values to a current chart.

{{< code-file file="values.yaml" lang="yaml" >}}

Important choices in this example:

- Three ingesters and replication factor three require enough schedulable nodes. The chart's anti-affinity and your storage topology must be checked; replicas alone do not prove fault tolerance.
- Zone-aware replication is explicitly disabled. This is a host-level reference, not a claim of resilience across availability zones.
- The compactor runs as a singleton. Its responsibilities do not justify one replica per cluster node. Retention is not enabled by this example; define and test a retention policy before relying on automatic deletion. See [Loki retention](https://grafana.com/docs/loki/latest/operations/storage/retention/).
- PVCs reference `rook-ceph-block`. Confirm that StorageClass, free space, placement and reclaim policy before use.
- Replica counts, cache defaults, resources and disruption budgets require load testing. They are not a sizing recommendation for a 300 TB storage cluster.
- Canary and Helm tests are disabled until an authenticated collection/query path is configured. Enable equivalent end-to-end monitoring before production use.

## Object storage and credentials

Provision a dedicated Ceph user with access limited to Loki's buckets. With a Rook `CephObjectStoreUser` named `loki` in object store `object-store`, inspect the generated Secret's metadata with:

```bash
kubectl -n rook-ceph describe secret rook-ceph-object-user-object-store-loki
```

That Secret belongs to the `rook-ceph` namespace. A Secret reference cannot cross namespaces: use your secret-management workflow to supply a separate `loki-s3` Secret in namespace `loki`, containing `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`. The chart injects these variables and expands them in the Loki configuration. Do not commit key values or rendered configuration containing real credentials.

Configure a trusted HTTPS endpoint in the values file. For an internal CA, install or mount the required CA and configure the client trust settings for the chosen version. `insecure: false` assumes a certificate chain the client trusts; it does not install your CA.

Bucket commands must point explicitly to Ceph, not the default AWS S3 endpoint. The following Bash example assumes an AWS CLI profile `ceph-loki` that already contains the restricted Ceph user's credentials:

```bash
export AWS_PROFILE=ceph-loki
export CEPH_S3_ENDPOINT=https://s3.example.com
# If the endpoint uses an internal CA:
# export AWS_CA_BUNDLE=/path/to/internal-ca.pem
for bucket in loki-chunks loki-ruler loki-admin; do
  aws --endpoint-url "$CEPH_S3_ENDPOINT" --region us-east-1 s3 mb "s3://$bucket"
done
```

Use the same endpoint, bucket names and region/signature settings in Loki. Create buckets once, and verify existing buckets rather than assuming a failed creation command means the storage is unusable. TLS verification remains enabled.

## Render and install deliberately

In an empty working directory, download `values.yaml`, adapt its endpoint and DNS settings, and review the manifests:

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
helm template loki grafana/loki --version 6.24.0   --namespace loki --kube-version 1.30.0 -f values.yaml > rendered.yaml
```

The correct command order is **release name, chart name**, followed by flags. After verifying the target cluster, namespace, Secrets, storage, resources and authentication design, the corresponding historical installation command is:

```bash
helm upgrade --install loki grafana/loki --version 6.24.0   --namespace loki --create-namespace -f values.yaml --wait --timeout 10m
```

`helm template` verifies chart rendering; it does not validate storage connectivity, application configuration at runtime or the cluster's capacity to schedule the pods.

## Authentication, collection and verification

`auth_enabled: true` enables Loki's multi-tenant mode. Clients must supply the appropriate `X-Scope-OrgID`, but that header alone is not proof of identity. Put an authenticating and authorizing proxy in front of the API, and have it set or validate tenant identity. The chart's routing gateway does not automatically establish this security boundary. Keep direct service access restricted. See [Loki authentication](https://grafana.com/docs/loki/latest/operations/authentication/).

The original collection example used Promtail. It reached end of life on **March 2, 2026**. Use a supported collector such as Grafana Alloy for a new setup, following the [Promtail migration guidance](https://grafana.com/docs/loki/latest/send-data/promtail/). Give the collector only the filesystem permissions it needs; running as root is not a universal prerequisite.

Add Loki's authenticated query endpoint as a Grafana data source. Validate ingestion and querying for a known log line, tenant separation, pod placement, PVC binding and object-store access. Then test restarts and node failure under representative load. Those checks are necessary before claiming high availability or choosing the final replica counts.
