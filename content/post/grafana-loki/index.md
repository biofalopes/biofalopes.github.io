+++
title = "Deploying Grafana Loki on Kubernetes"
description = "Deploying Loki, a horizontally scalable, highly available, multi-tenant log aggregation system inspired by Prometheus, on a seven-node on-premises Kubernetes cluster.  Includes detailed explanations and integration with Mimir and Grafana."
date =  "2024-10-22"
draft = false
toc = true
categories = ["loki", "kubernetes", "grafana"]
tags = ["loki", "kubernetes", "grafana", "log aggregation", "monitoring"]
image = "logs-loki-diagram.svg"
author = "Fabio M. Lopes"
+++

This document details the deployment of Loki, a horizontally scalable, highly available, multi-tenant log aggregation system inspired by Prometheus, on a seven-node on-premises Kubernetes cluster.  We'll explore not only the Loki deployment itself but also its integration with Mimir (for long-term log storage) and Grafana (for visualization and querying). The cluster, running AlmaLinux on bare-metal servers with a combined storage capacity of approximately 300TB, leverages Rook Ceph for storage management.  This deployment will serve as a central repository for logs gathered from multiple Promtail endpoints, primarily for Ceph clusters, providing a robust and scalable solution for long-term log storage and analysis. The configuration emphasizes high availability and resilience, leveraging the resources of the seven-node cluster to ensure optimal performance and minimize potential single points of failure.  Specific configurations and considerations regarding resource allocation, storage management, and security are outlined in the following sections.


**Understanding Loki's Architecture**

Before diving into the deployment, let's understand Loki's core components:

* **Promtail:**  This is Loki's agent. It runs on your application servers and collects logs, sending them to the Loki stack.  It supports various log formats and can be configured to scrape logs from files, systemd journals, and more.

* **Distributor:** This component receives log streams from Promtail and distributes them to the Ingesters.  It acts as a load balancer, ensuring even distribution across the Ingester cluster.

* **Ingester:** These components receive and process the log streams. They perform tasks such as label indexing and chunk creation.  The number of Ingesters should scale with the volume of logs ingested.

* **Querier:** This component handles log queries.  It receives queries from clients (like Grafana) and retrieves the relevant log data from the storage backend (in this case, Mimir).

* **Compactor:**  This component merges and compresses log chunks, optimizing storage space over time.

* **Index:**  Loki uses an index to quickly search and filter logs based on labels.  The `values.yaml` file configures the index's properties (periodicity, storage, etc.).


**Loki, Mimir, and Grafana: A Powerful Trio**

While Loki handles log ingestion and querying, it's often used in conjunction with Mimir and Grafana to create a complete log monitoring solution:

* **Loki:**  Handles the ingestion, indexing, and querying of logs.

* **Mimir:**  Acts as the long-term storage backend for Loki.  It provides highly scalable and efficient storage for your logs, crucial for retaining logs for extended periods. Mimir uses a time-series database optimized for storing large volumes of log data, ensuring efficient retrieval.

* **Grafana:** Provides a user-friendly interface for querying, visualizing, and exploring logs stored in Loki.  It allows users to create dashboards, set alerts, and perform complex log analysis.

This combined approach allows for effective log management: Loki handles the real-time ingestion and querying needs, Mimir ensures cost-effective long-term storage, and Grafana empowers users to easily analyze and understand the logs.


**1. Helm Repository Addition and Update:**

```bash
helm repo add grafana https://grafana.github.io/helm-charts  # Adds the Grafana Helm chart repository.
helm repo update                                             # Updates the local Helm repository cache.
```

**2. Custom `values.yaml` Configuration:**

This `values.yaml` file customizes the Loki deployment.  Key customizations are explained below.  The commented-out lines represent optional configurations which can be uncommented and adjusted as needed.

```yaml
global:
  clusterDomain: "k8s-logs"
  dnsService: "coredns"

loki:
  auth_enabled: false
  schemaConfig:
    configs:
      - from: 2024-04-01
        store: tsdb
        object_store: s3
        schema: v13
        index:
          prefix: loki_index_
          period: 24h
  ingester:
    chunk_encoding: snappy
  tracing:
    enabled: true
  querier:
    max_concurrent: 4
  limits_config:
    ingestion_rate_strategy: local
    max_global_streams_per_user: 1000
    per_stream_rate_limit: 512M
    per_stream_rate_limit_burst: 1024M
    ingestion_burst_size_mb: 1000
    ingestion_rate_mb: 5000
    max_entries_limit_per_query: 100000
  storage:
    type: s3
    bucketNames:
      chunks: "chunks"
      ruler: "ruler"
      admin: "loki-admin"
    s3:
      endpoint: rook-ceph-rgw-object-store.rook-ceph.svc.k8s-logs
      region: us-east-1
      secretAccessKey: <secret_key>
      accessKeyId: <access_key>
      signatureVersion: v4
      s3ForcePathStyle: true
      insecure: true

deploymentMode: Distributed

ingester:
  replicas: 7
querier:
  replicas: 7
  maxUnavailable: 4
queryFrontend:
  replicas: 7
  maxUnavailable: 4
queryScheduler:
  replicas: 7
distributor:
  replicas: 7
  maxUnavailable: 4
compactor:
  replicas: 7
indexGateway:
  replicas: 7
  maxUnavailable: 4

bloomCompactor:
  replicas: 0
bloomGateway:
  replicas: 0

backend:
  replicas: 0
read:
  replicas: 0
write:
  replicas: 0

singleBinary:
  replicas: 0
```

**Explanation of Key `values.yaml` Configurations:**

* `global.clusterDomain`:  Specifies the cluster domain for internal DNS resolution.
* `loki.auth_enabled`: Disables authentication for simplicity (recommended for initial setup, but should be enabled in production).
* `loki.schemaConfig`: Defines the schema version and storage settings for Loki's data.  `object_store: s3` indicates that the logs are stored in an S3-compatible object store (provided by Rook Ceph in this case).
* `loki.ingester.chunk_encoding`: Specifies the compression algorithm for log chunks. `snappy` offers a good balance between compression and speed.
* `loki.tracing.enabled`: Enables tracing, helpful for debugging and performance monitoring.
* `loki.limits_config`:  Sets various limits on ingestion rates, query sizes, and other resources to prevent overload and ensure stability.  The values provided here are examples and should be tuned based on your expected load.
* `loki.storage.type`: Defines the storage type as S3-compatible.
* `loki.storage.s3`: Configures the connection to the Rook Ceph S3-compatible object store.  Ensure that the `endpoint`, `region`, `secretAccessKey`, and `accessKeyId` are correctly configured. `insecure: true` should **only** be used in development or testing environments; it's crucial to disable this in production.
* `deploymentMode: Distributed`:  Configures Loki to run in distributed mode, leveraging multiple components for high availability and scalability.
* `ingester`, `querier`, `queryFrontend`, `distributor`, `compactor`, `indexGateway`:  These sections specify the number of replicas for each Loki component.  The values are set to 7 to match the number of nodes in the cluster, ensuring high availability.  `maxUnavailable` limits the number of pods that can be unavailable during updates.


**3. CephObjectStoreUser Creation:**

This creates a user for Loki in the Rook Ceph object store.

```yaml
apiVersion: ceph.rook.io/v1
kind: CephObjectStoreUser
metadata:
  name: loki
  namespace: rook-ceph
spec:
  store: object-store
  displayName: loki
  capabilities:
    user: "*"
    bucket: "*"
```

```bash
k apply -f CephObjectStoreUser.yaml
```

**4. Retrieving S3 Access Keys:**

```bash
kubectl -n rook-ceph get secret rook-ceph-object-user-object-store-loki -oyaml
```

**5. Bucket Creation:**

These commands create the necessary S3 buckets for storing Loki's data.  The use of `--no-verify-ssl` is strongly discouraged in production.

```bash
aws --no-verify-ssl s3 mb s3://chunks --region us-east-1
aws --no-verify-ssl s3 mb s3://ruler --region us-east-1
aws --no-verify-ssl s3 mb s3://loki-admin --region us-east-1
```

**6. Loki Installation:**

This installs Loki using the customized `values.yaml` file.

```bash
helm install --namespace loki grafana/loki loki -f override-values.yaml
```

**7. Grafana Configuration (Visualization):**

After Loki is installed, you'll need to configure Grafana to connect to it. This involves adding a Loki data source in Grafana, specifying the Loki endpoint (usually `http://loki-query-frontend.<namespace>.svc.cluster.local`).  Refer to the Grafana documentation for detailed instructions on configuring Loki as a data source, which is very straightforward.

This expanded post provides a more comprehensive guide to deploying Loki on Kubernetes, emphasizing its integration with Grafana for a complete log management solution.