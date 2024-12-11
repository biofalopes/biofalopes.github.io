+++
title = "Deploying Rook Ceph on Kubernetes for Grafana Loki and Mimir"
description = "Using Rook to leverage Ceph storage on a Kubernetes cluster for Grafana Loki and Mimir"
date = "2024-11-15"
draft = false
toc = false
categories = ["ceph", "kubernetes"]
tags = ["ceph", "kubernetes"]
image = "rook.png"
+++

## Deploying Rook Ceph on Kubernetes: A Detailed Walkthrough

This blog post documents my experience deploying Rook, a Ceph orchestrator for Kubernetes, within our existing cluster.  This setup provides a highly available, scalable object storage solution integrated directly into our Kubernetes environment. The process involved careful disk preparation, Rook deployment, and subsequent configuration and testing.

### Rook, Ceph, and the Why

Rook simplifies the deployment and management of Ceph, a distributed storage system, within Kubernetes.  This means we get a robust, self-managing, and scalable storage solution without the complexities of manual Ceph installation. For this deployment, we used Rook v1.13.3 and Ceph v18.2. The base directory for all operations was `/srv/cluster-logs/rook`.

### Preparing the Storage

Before deploying Rook, I had to prepare the storage devices that would serve as OSDs (Object Storage Devices). This involved wiping any existing filesystem information on the chosen disks.  The initial disk listing (`lsblk`) confirmed the available disks and partitions:

```bash
NAME                           MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
sda                              8:0    0   3.6T  0 disk
sdb                              8:16   0   3.6T  0 disk
sdc                              8:32   0   3.6T  0 disk
sdd                              8:48   0   3.6T  0 disk
sde                              8:64   0   3.6T  0 disk
sdf                              8:80   0   3.6T  0 disk
sdg                              8:96   0   3.6T  0 disk
sdh                              8:112  0   3.6T  0 disk
sdi                              8:128  0   3.6T  0 disk
sdj                              8:144  0   3.6T  0 disk
sdk                              8:160  0   3.6T  0 disk
sdl                              8:176  0   3.6T  0 disk
sdm                              8:192  0 223.5G  0 disk
├─sdm1                           8:193  0   600M  0 part /boot/efi
├─sdm2                           8:194  0     1G  0 part /boot
└─sdm3                           8:195  0 221.9G  0 part
  ├─almalinux_logsrv1233-root  253:0    0    70G  0 lvm  /
  └─almalinux_logsrv1233-swap  253:1    0     4G  0 lvm
nvme2n1                        259:4    0   1.5T  0 disk
nvme1n1                        259:5    0   1.5T  0 disk
nvme0n1                        259:6    0   1.5T  0 disk
nvme3n1                        259:7    0   1.5T  0 disk
```

The `wipefs` command was used remotely via SSH to securely wipe the selected disks:

```bash
# Wipe selected disks across multiple nodes
for j in {247..251}; do ssh admin@10.0.0.$j "for i in {a..l}; do sudo wipefs -a /dev/sd\$i; done"; done
for j in {246..251}; do ssh admin@10.0.0.$j "sudo wipefs -a /dev/nvme0n1"; done
for j in {246..251}; do ssh admin@10.0.0.$j "sudo wipefs -a /dev/nvme1n1"; done
for j in {246..251}; do ssh admin@10.0.0.$j "sudo wipefs -a /dev/nvme2n1"; done
for j in {246..251}; do ssh admin@10.0.0.$j "sudo wipefs -a /dev/nvme3n1"; done
```

This script iterates through a range of IP addresses (10.0.0.247 to 10.0.0.251) representing our worker nodes and executes the `wipefs` command on each specified device. This ensures clean disks for our Ceph OSDs.


### Rook Deployment

**1. Cloning the Repository:**

The Rook repository was cloned to the specified base directory:

```bash
cd /srv/cluster-logs/
git clone --single-branch --branch v1.13.3 https://github.com/rook/rook.git
cd rook/deploy/examples
```

Cloning a specific branch ensures consistency and avoids potential issues with newer features.

**2. Creating Core Components:**

Basic Rook components were created using `kubectl`:

```bash
kubectl create -f crds.yaml -f common.yaml -f operator.yaml
```

These YAML files define the Custom Resource Definitions (CRDs), common resources, and the operator itself, forming the foundation for the Rook deployment.

**3. Deploying the Ceph Cluster:**

The core of the deployment is the `cluster.yaml` file:


```yaml
apiVersion: ceph.rook.io/v1
kind: CephCluster
metadata:
  name: rook-ceph
  namespace: rook-ceph
spec:
  cephVersion:
    image: registry.internal/ceph:v18.2.1 # Custom Ceph Image
    allowUnsupported: false # Strict Ceph version check
  # ... other specifications such as data directory, monitoring, network settings ...
  storage:
    useAllNodes: true # Utilize all nodes for OSD placement
    useAllDevices: true # Utilize all available devices
  # ... advanced settings such as placement, cleanup policies, resource allocation, etc.
```

This YAML file defines the Ceph cluster configuration, including the Ceph version (using a custom image from `registry.internal`), data directory location, monitoring settings, network parameters, OSD placement strategy and more.  The `useAllNodes` and `useAllDevices` options simplified OSD deployment by utilizing all available resources.

The cluster was created with:

```bash
cd /srv/cluster-logs/rook/deploy
kubectl create -f cluster.yaml
```


**4. Deploying the Toolbox:**

The Rook toolbox provides useful CLI tools for managing the Ceph cluster:

```bash
kubectl create -f examples/toolbox.yaml
```

This deploys a container providing access to Ceph commands within the Kubernetes environment.

**5. Verification:**

The status of the Rook deployment was verified using:

```bash
kubectl -n rook-ceph get pod
```

This command lists all pods in the `rook-ceph` namespace, showing the status of various components like MONs, OSDs, and managers.

**6. Accessing the Ceph CLI:**

The Ceph CLI was accessed using the toolbox:

```bash
k -n rook-ceph exec -ti rook-ceph-tools-6cfb855d85-p2kfg -- bash
```

This command provides a summary of the Ceph cluster status:

```bash
bash-4.4$ ceph -s
  cluster:
    id:     aca5b61e-a4fa-4e2e-b9d2-e6c1f59f7563
    health: HEALTH_OK

  services:
    mon: 3 daemons, quorum a,b,c (age 2d)
    mgr: a(active, since 5h), standbys: b
    osd: 112 osds: 112 up (since 2d), 112 in (since 2d)
    rgw: 1 daemon active (1 hosts, 1 zones)

  data:
    pools:   9 pools, 89 pgs
    objects: 379 objects, 16 MiB
    usage:   11 GiB used, 346 TiB / 346 TiB avail
    pgs:     89 active+clean
```

**7. Object Storage (RADOS Gateway):**

Object storage was deployed using:


```yaml
apiVersion: ceph.rook.io/v1
kind: CephObjectStore
metadata:
  name: object-store
  namespace: rook-ceph
spec:
  metadataPool:
    failureDomain: host
    replicated:
      size: 3
  dataPool:
    failureDomain: host
    # For production it is recommended to use more chunks, such as 4+2 or 8+4
    erasureCoded:
      dataChunks: 4
      codingChunks: 2
  preservePoolsOnDelete: true
  gateway:
    # sslCertificateRef:
    port: 80
    # securePort: 443
    instances: 1
```

This YAML file configures the RADOS Gateway (RGW), providing object storage compatible with S3.  The configuration includes the selection of metadata and data pools, as well as gateway settings like port and number of instances.

An Ingress resource was then created to expose the RGW externally, allowing access to the object storage over HTTP.


```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rook-ceph-rgw
  namespace: rook-ceph
spec:
  ingressClassName: haproxy
  rules:
  - host: s3-k8s-logs.internal
    http:
      paths:
      - backend:
          service:
            name: rook-ceph-rgw-object-store
            port:
              number: 80
        path: /
        pathType: ImplementationSpecific
  - host: s3-in-k8s-logs.internal
    http:
      paths:
      - backend:
          service:
            name: rook-ceph-rgw-object-store
            port:
              number: 80
        path: /
        pathType: ImplementationSpecific
  tls:
  - hosts:
    - s3-k8s-logs.internal
    - s3-in-k8s-logs.internal
```

**8. RBD Pool and StorageClass:**

A block storage pool (`rbd-pool`) and a corresponding StorageClass (`rook-ceph-block`) were created to allow Kubernetes pods to provision Persistent Volumes using Ceph RBD.  The StorageClass definition includes parameters for cluster ID, pool name, image format, and other RBD specific settings:

```yaml
apiVersion: ceph.rook.io/v1
kind: CephBlockPool
metadata:
  name: rbd-pool
  namespace: rook-ceph
spec:
  failureDomain: host
  replicated:
    size: 3
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
   name: rook-ceph-block
provisioner: rook-ceph.rbd.csi.ceph.com
parameters:
    clusterID: rook-ceph
    pool: rbd-pool
    imageFormat: "2"
    imageFeatures: layering
    csi.storage.k8s.io/provisioner-secret-name: rook-csi-rbd-provisioner
    csi.storage.k8s.io/provisioner-secret-namespace: rook-ceph
    csi.storage.k8s.io/controller-expand-secret-name: rook-csi-rbd-provisioner
    csi.storage.k8s.io/controller-expand-secret-namespace: rook-ceph
    csi.storage.k8s.io/node-stage-secret-name: rook-csi-rbd-node
    csi.storage.k8s.io/node-stage-secret-namespace: rook-ceph
    csi.storage.k8s.io/fstype: ext4

reclaimPolicy: Delete
allowVolumeExpansion: true
```

**9. Dashboard Ingress:**

An Ingress resource was configured to expose the Ceph dashboard.  This allows accessing the dashboard through a web browser.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rook-ceph-dashboard
  namespace: rook-ceph
spec:
  ingressClassName: haproxy
  rules:
  - host: ceph-k8s-logs.internal
    http:
      paths:
      - backend:
          service:
            name: rook-ceph-mgr-dashboard
            port:
              number: 8443
        path: /
        pathType: ImplementationSpecific
  tls:
  - hosts:
    - ceph-k8s-logs.internal
```

**10. Dashboard SSL:**

The process involved disabling SSL on the dashboard temporarily, due to initial compatibility issues with the existing HAProxy setup.

```bash
k -n rook-ceph exec -ti rook-ceph-tools-6cfb855d85-p2kfg -- bash
bash-4.4$ ceph config set mgr mgr/dashboard/ssl false
bash-4.4$ ceph mgr module disable dashboard
bash-4.4$ ceph mgr module enable dashboard
```

**11. Upgrades:**

Rook and Ceph were upgraded incrementally by cloning the updated repository and applying the necessary YAML manifests, in order to test the procedure before any workload were running in the cluster. The incremental upgrade strategy ensures minimal downtime and risk during the upgrade process.

```bash
cd deploy/examples
kubectl apply -f common.yaml -f crds.yaml
kubectl -n $ROOK_OPERATOR_NAMESPACE set image deploy/rook-ceph-operator rook-ceph-operator=rook/ceph:v1.15.2
```

This detailed walkthrough provides a comprehensive guide to deploying and managing Rook Ceph within a Kubernetes cluster.  The use of Rook simplifies the process considerably, allowing for a highly available and scalable storage solution integrated directly into our Kubernetes infrastructure. The careful configuration ensures our storage system is tuned for performance and resilience.
