+++
slug = "deploying-grafana-mimir-on-kubernetes"
lastmod = "2026-10-27"
title = "Deploying Grafana Mimir on Kubernetes"
description = "Deploying a classic Mimir metrics backend with Rook Ceph: versioned Helm values, S3 credentials, authentication and verification boundaries."
date =  "2024-11-19"
draft = false
toc = true
categories = ["mimir", "kubernetes" ]
tags = ["mimir", "kubernetes" ]
image = "mimir.svg"
author = "Fabio M. Lopes"
+++

I deployed Mimir alongside Loki and Grafana on a seven-node AlmaLinux Kubernetes cluster, using Rook Ceph as S3-compatible object storage. Mimir provided a central metrics backend for multiple Prometheus servers. Loki handled logs through a separate ingestion and storage path.

**Technical revision — October 2026:** this revision corrects the Helm chart and argument order, the Ceph Secret name, and bucket commands that omitted the Ceph endpoint. It also separates a historical configuration example from claims that require runtime and failure testing.

## Architecture and versions

Prometheus sends metrics to Mimir using remote write. Grafana queries Mimir using PromQL. In the classic architecture, ingesters receive samples and produce blocks that are stored in object storage; store gateways make those blocks available to the query path. This is not a log-storage backend for Loki.

The downloadable [values.yaml](values.yaml) targets **grafana/mimir-distributed chart 5.6.0, Mimir 2.15.0**, rendered for Kubernetes 1.30 with Helm 3.17.3. These versions define a reproducible historical reference for this revision; they are not asserted to be the exact versions from the original deployment or a current production baseline.

Current Mimir charts use a newer ingest-storage architecture by default. Follow the [current deployment guide](https://grafana.com/docs/mimir/latest/set-up/helm-chart/) for a new installation, and review Kafka and migration requirements before moving from classic architecture.

{{< code-file file="values.yaml" lang="yaml" >}}

The sample enables tenant isolation, uses separate buckets for blocks, ruler and Alertmanager state, and injects credentials through a Kubernetes Secret. It disables the bundled MinIO and the historical Grafana Agent metamonitoring integration.

Zone-aware replication is disabled explicitly. The three ingesters and store gateways, two query components and routing replicas are illustrative topology choices, not evidence of high availability. Verify anti-affinity, replication, available nodes, PVC placement and disruption behavior. Resource requests, limits, caches and disk sizing still need to match measured series cardinality, ingestion rate, retention and query load.

## Ceph identity and buckets

Use a dedicated Ceph user with restricted access to the three Mimir buckets. If Rook manages a `CephObjectStoreUser` named `mimir` for `object-store`, its Secret is:

```bash
kubectl -n rook-ceph describe secret rook-ceph-object-user-object-store-mimir
```

The old example incorrectly read the Loki user's Secret. Keep these identities separate. Through your secret-management workflow, provide a `mimir-s3` Secret in namespace `mimir` with `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`. The chart injects these values and enables environment expansion. The source values file contains variable references rather than real key material.

Create the buckets against the actual Ceph endpoint. This Bash example assumes an AWS CLI profile `ceph-mimir` with that user's credentials:

```bash
export AWS_PROFILE=ceph-mimir
export CEPH_S3_ENDPOINT=https://s3.example.com
# For an internal CA:
# export AWS_CA_BUNDLE=/path/to/internal-ca.pem
for bucket in mimir-blocks mimir-ruler mimir-alertmanager; do
  aws --endpoint-url "$CEPH_S3_ENDPOINT" --region us-east-1 s3 mb "s3://$bucket"
done
```

Unlike the AWS CLI URL, the Mimir S3 `endpoint` field in this example uses `host:port`, without a scheme; `insecure: false` selects TLS. Configure trusted certificates for the Mimir containers as well as the CLI. Do not bypass certificate validation to work around a missing internal CA.

## Render before installing

Download `values.yaml`, adapt the endpoint, DNS and StorageClass, and render the exact chart:

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
helm template mimir grafana/mimir-distributed --version 5.6.0   --namespace mimir --kube-version 1.30.0 -f values.yaml > rendered.yaml
```

After reviewing the manifests and target environment, the historical installation command is:

```bash
helm upgrade --install mimir grafana/mimir-distributed --version 5.6.0   --namespace mimir --create-namespace -f values.yaml --wait --timeout 10m
```

The release is `mimir` and the chart is `grafana/mimir-distributed`. Local lint and rendering passed during this revision. No cluster installation, object-store connection or failure test was performed.

## Secure the write and query paths

Mimir uses `X-Scope-OrgID` to identify a tenant. An authenticating reverse proxy must authorize clients and control the tenant header. Enabling multi-tenancy does not by itself authenticate callers. See [Mimir authentication and authorization](https://grafana.com/docs/mimir/latest/manage/secure/authentication-and-authorization/).

Configure Prometheus remote write to the authenticated Mimir endpoint at `/api/v1/push`; configure the Grafana Prometheus data source to the authenticated query endpoint with the `/prometheus` prefix. Match credentials and tenant identity at the proxy. The old metamonitoring example pointed to a Prometheus service as if it were Mimir; that configuration has been removed.

Before using the service, verify:

- Pod readiness, ring membership, PVCs and placement across the intended failure domains.
- A known metric written through Prometheus and queried through Grafana, including the correct tenant.
- Bucket access, successful block uploads and queries for data older than the ingesters' recent window.
- Rejection of unauthorized requests and cross-tenant access attempts.
- Restarts, node failure, recovery, retention and resource usage under representative load.

The storage cluster's total disk capacity does not determine Mimir's replica count. Ingestion rate, active series, retention and query behavior are the inputs to sizing. A successful Helm render is a useful first check; operational claims require the runtime evidence above.
