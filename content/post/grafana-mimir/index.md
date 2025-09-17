+++
title = "Deploying Grafana Mimir on Kubernetes"
description = "Deploying of Mimir, a horizontally scalable, highly available time series database, on a seven-node on-premises Kubernetes cluster."
date =  "2024-11-19"
draft = false
toc = false
categories = ["mimir", "kubernetes" ]
tags = ["mimir", "kubernetes" ]
image = "mimir.svg"
author = "Fabio M. Lopes"
+++

This document details the deployment of Mimir, a horizontally scalable, highly available time series database, on a seven-node on-premises Kubernetes cluster. The cluster, running AlmaLinux on bare-metal servers with a combined storage capacity of approximately 300TB, leverages Rook Ceph for storage management. This deployment will serve as a central repository for metrics gathered from multiple Prometheus servers, providing a robust and scalable solution for long-term metric storage and analysis. The configuration emphasizes high availability and resilience, leveraging the resources of the seven-node cluster to ensure optimal performance and minimize potential single points of failure. Specific configurations and considerations regarding resource allocation, storage management, and security are outlined in the following sections.

**1. Helm Repository Addition and Update:**

```bash
helm repo add grafana https://grafana.github.io/helm-charts 
helm repo update
```

**2. Custom `values.yaml` Configuration:**

This `values.yaml` file customizes the Mimir deployment. Key customizations are noted below.

```yaml
metaMonitoring:
  serviceMonitor:
    enabled: true
  grafanaAgent:
    enabled: true
    installOperator: false
    logs:
      remote:
        url: "http://loki-gateway.loki.svc/loki/api/v1/push"
    metrics:
      remote:
        url: "https://kube-prometheus-stack-prometheus.monitoring.svc:9090/api/v1/push" 
        headers:
          X-Scope-OrgID: metamonitoring

global:
  dnsService: coredns
  dnsNamespace: kube-system
  clusterDomain: sp-logs.

mimir:
  structuredConfig:
    limits:
      max_global_series_per_user: 1000000
    common:
      storage:
        backend: s3 
        s3:
          endpoint: rook-ceph-rgw-object-store.rook-ceph.svc.sp-logs
          region: us-east-1
          secret_access_key: <secret_key> 
          access_key_id: <access_key> 
    blocks_storage:
      s3:
        bucket_name: mimir-blocks
    alertmanager_storage:
      s3:
        bucket_name: mimir-alertmanager
    ruler_storage:
      s3:
        bucket_name: mimir-ruler

# The following sections define resource limits and replicas for different Mimir components.  The replica counts (especially `ingester` and `index-cache` set to 7) are customized to match the 7-node cluster.  Adjust based on your needs.  Also note the generous resource limits, especially for `ingester`.  These should be adjusted based on the expected load.

alertmanager:
  persistentVolume:
    enabled: true
  replicas: 2
  resources:
    limits:
      memory: 1.4Gi
    requests:
      cpu: 1
      memory: 1Gi
  statefulSet:
    enabled: true

compactor:
  persistentVolume:
    size: 20Gi
  resources:
    limits:
      memory: 2.1Gi
    requests:
      cpu: 1
      memory: 1.5Gi

distributor:
  replicas: 2
  resources:
    limits:
      memory: 5.7Gi
    requests:
      cpu: 2
      memory: 4Gi

ingester:
  persistentVolume:
    size: 50Gi
  replicas: 7
  resources:
    limits:
      memory: 12Gi 
    requests:
      cpu: 3.5
      memory: 8Gi
  topologySpreadConstraints: {}
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:
            matchExpressions:
              - key: target
                operator: In
                values:
                  - ingester
          topologyKey: 'kubernetes.io/hostname'

        - labelSelector:
            matchExpressions:
              - key: app.kubernetes.io/component
                operator: In
                values:
                  - ingester
          topologyKey: 'kubernetes.io/hostname'

  zoneAwareReplication:
    topologyKey: 'kubernetes.io/hostname'

# other Mimir configurations:
admin-cache:
  enabled: true
  replicas: 2

chunks-cache:
  enabled: true
  replicas: 2

index-cache:
  enabled: true
  replicas: 7

metadata-cache:
  enabled: true

results-cache:
  enabled: true
  replicas: 2

minio:
  enabled: false

overrides_exporter:
  replicas: 1
  resources:
    limits:
      memory: 128Mi
    requests:
      cpu: 100m
      memory: 128Mi

querier:
  replicas: 1
  resources:
    limits:
      memory: 5.6Gi
    requests:
      cpu: 2
      memory: 4Gi

query_frontend:
  replicas: 1
  resources:
    limits:
      memory: 2.8Gi
    requests:
      cpu: 2
      memory: 2Gi

ruler:
  replicas: 1
  resources:
    limits:
      memory: 2.8Gi
    requests:
      cpu: 1
      memory: 2Gi

store_gateway:
  persistentVolume:
    size: 10Gi
  replicas: 2
  resources:
    limits:
      memory: 2.1Gi
    requests:
      cpu: 1
      memory: 1.5Gi
  topologySpreadConstraints: {}
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:
            matchExpressions:
              - key: target
                operator: In
                values:
                  - store-gateway
          topologyKey: 'kubernetes.io/hostname'

        - labelSelector:
            matchExpressions:
              - key: app.kubernetes.io/component
                operator: In
                values:
                  - store-gateway
          topologyKey: 'kubernetes.io/hostname'
  zoneAwareReplication:
    topologyKey: 'kubernetes.io/hostname'

nginx:
  replicas: 1
  resources:
    limits:
      memory: 731Mi
    requests:
      cpu: 1
      memory: 512Mi
  ingress:
    enabled: true
    annotations: {}
    hosts:
      - host: mimir.mydomain
        paths:
          - path: /
            pathType: ImplementationSpecific
    tls:
      - hosts:
          - mimir.mydomain
```

**3. Ceph Object Store User Creation:**

This section describes creating a user for Mimir in the Rook Ceph object store. Using a Kubernetes manifest is the preferred approach over `radosgw-admin`.

```yaml
apiVersion: ceph.rook.io/v1
kind: CephObjectStoreUser
metadata:
  name: mimir
  namespace: rook-ceph
spec:
  store: object-store
  displayName: mimir
  capabilities:
    user: "*"
    bucket: "*"
```

```bash
k apply -f CephObjectStoreUser.yaml
```

**4. Retrieving S3 Access Keys:**

The command below retrieves the S3 access keys from the Kubernetes secret.

```bash
k -n rook-ceph get secret rook-ceph-object-user-object-store-loki -oyaml
```

**5. Bucket Creation:**

The following commands create the necessary S3 buckets.  **Note the use of `--no-verify-ssl`.**

```bash
aws --no-verify-ssl s3 mb s3://mimir-blocks --region us-east-1
aws --no-verify-ssl s3 mb s3://mimir-ruler --region us-east-1
aws --no-verify-ssl s3 mb s3://mimir-alertmanager --region us-east-1
```

**6. Mimir Installation:**

This command installs Mimir using the customized `values.yaml` file.

```bash
helm install --namespace mimir grafana/mimir mimir -f values.yaml
```

**Security Considerations:**

* **Hardcoded Credentials:**  The `values.yaml` file contains hardcoded AWS access keys. This is a major security vulnerability.  Use Kubernetes Secrets to manage these credentials securely.
* **Authentication:** Authentication is initially disabled.  Enabling authentication is crucial for security and multi-tenancy, ans you should enable it as soon as everything is working smoothly. By the time i wrote this, i wasn´t there yet.