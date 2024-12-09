+++
title = "Installing a Ceph Cluster"
description = "Using cephadm to easily deploy a Ceph Cluster"
date = "2024-12-07"
draft = false
toc = false
tags = ["ceph"]
categories = ["ceph"]
image = "ceph_banner.jpg"
author = "Fabio M. Lopes"
+++

In this example I used the Red Hat Ceph, but the procedure is the same for the community version. The official guide for RHCS 7 can be found here: [RedHat guide](https://docs.redhat.com/en/documentation/red_hat_ceph_storage/7/html/installation_guide/index)

### Preparation:

* Configure a Workbench
* Populate the hosts inventory
* Run the preflight playbook
* Create the `initial-config.yaml`
* Run the Bootstrap Script

SSH Key Distribution:

1. Create an `admin` user on all servers, with a password and sudo privileges.
2. Generate an SSH key pair for the `admin` user on the workbench.
3. Use `ssh-copy-id` to copy the public key to all servers for the `admin` user.
4. Copy the public and private keys to `/home/admin/.ssh` on MON 1.

**Bootstrap**: Execute from MON 1, using `sudo` as the `admin` user.

#### initial-config.yaml:

This initial-config.yaml file defines the configuration for a Ceph cluster, specifying the roles and placement of various Ceph services across multiple hosts. The configuration uses a declarative approach, listing each host and assigning it one or more roles.

The file is structured as a YAML document containing several sections, each representing a different Ceph service. Each section defines the service_type (e.g., host, mon, mgr, osd, rgw, grafana), and then specifies the placement and configuration details for that service.

Host definitions: Multiple sections define individual hosts (ceph-workbench, ceph-1 through ceph-20). Each host has an addr (IP address) and hostname, and is assigned one or more labels (ceph, mons, mgrs, osds, rgws, grafana). These labels determine which Ceph services will be deployed on that host. For example, hosts with the mons label will run the Ceph monitors.

Service placement: Sections for mon, mgr, osd, rgw, and grafana define the placement of these services using the placement directive, which references the labels defined in the host sections. This ensures that the monitors are deployed on hosts labeled mons, OSDs (Object Storage Daemons) on hosts labeled osds, etc.

OSD Configuration: The osd service section includes data_devices: all: true, indicating that all available data devices on the OSD hosts should be used for storage.

RGW Configuration: The rgw (RADOS Gateway) service is configured with a service_id of ceph-cluster and placed on hosts labeled rgws.

Grafana Configuration: The grafana service is defined with a specific configuration, including enabling anonymous access (anonymous_access: true), specifying the protocol (protocol: https), and setting an initial admin password (initial_admin_password: 'super_difficult_pwd'). This indicates that Grafana will be deployed for monitoring the Ceph cluster.

In summary, this configuration file describes a distributed Ceph cluster with a designated workbench host and multiple hosts serving as monitors, managers, OSDs, RADOS Gateways, and a Grafana instance for monitoring and management. The use of labels and placement directives simplifies the deployment process and ensures that the services are distributed according to the defined roles. The password for grafana should be changed after deployment.

```json
service_type: host
addr: 10.0.0.19
hostname: ceph-workbench
labels:
 - _admin
---
service_type: host
addr: 10.0.0.20
hostname: ceph-1
labels:
 - ceph
 - mons
 - mgrs
 - osds
---
service_type: host
addr: 10.0.0.21
hostname: ceph-2
labels:
 - ceph
 - mons
 - mgrs
 - osds
---
service_type: host
addr: 10.0.0.22
hostname: ceph-3
labels:
 - ceph
 - mons
 - mgrs
 - osds
---
service_type: host
addr: 10.0.0.23
hostname: ceph-4
labels:
 - ceph
 - osds
---
service_type: host
addr: 10.0.0.24
hostname: ceph-5
labels:
 - ceph
 - osds
---
service_type: host
addr: 10.0.0.25
hostname: ceph-6
labels:
 - ceph
 - osds
---
service_type: host
addr: 10.0.0.26
hostname: ceph-7
labels:
 - ceph
 - osds
---
service_type: host
addr: 10.0.0.27
hostname: ceph-8
labels:
 - ceph
 - osds
---
service_type: host
addr: 10.0.0.28
hostname: ceph-9
labels:
 - ceph
 - osds
---
service_type: host
addr: 10.0.0.29
hostname: ceph-10
labels:
 - ceph
 - osds
---
service_type: host
addr: 10.0.0.30
hostname: ceph-11
labels:
 - ceph
 - osds
---
service_type: host
addr: 10.0.0.31
hostname: ceph-12
labels:
 - ceph
 - osds
---
service_type: host
addr: 10.0.0.32
hostname: ceph-13
labels:
 - ceph
 - osds
---
service_type: host
addr: 10.0.0.33
hostname: ceph-14
labels:
 - ceph
 - osds
---
service_type: host
addr: 10.0.0.34
hostname: ceph-15
labels:
 - ceph
 - osds
---
service_type: host
addr: 10.0.0.35
hostname: ceph-16
labels:
 - ceph
 - osds
---
service_type: host
addr: 10.0.0.36
hostname: ceph-17
labels:
 - ceph
 - osds
---
service_type: host
addr: 10.0.0.37
hostname: ceph-18
labels:
 - ceph
 - osds
 - grafana
---
service_type: host
addr: 10.0.0.38
hostname: ceph-19
labels:
 - ceph
 - osds
 - rgws
---
service_type: host
addr: 10.0.0.39
hostname: ceph-20
labels:
 - ceph
 - osds
 - rgws
---
service_type: mon
placement:
  label: mons
---
service_type: mgr
placement:
  label: mgrs
---
service_type: osd
placement:
  label: osds
data_devices:
  all: true
---
service_type: rgw
service_id: ceph-cluster
placement:
  label: rgws
---
service_type: grafana
placement:
  label: grafana
spec:
  anonymous_access: true
  protocol: https
  initial_admin_password: 'super_difficult_pwd'
```

The initial-config.yaml file defines a Ceph cluster topology consisting of 20 hosts in total, distributed as follows:

1 Workbench Host: ceph-workbench acts as the administrative workstation for managing the cluster. It does not run any Ceph daemons.

3 Monitor (MON) Nodes: Three hosts (ceph-1, ceph-2, ceph-3) are designated as monitor nodes. These are crucial for cluster management and coordination.

1 Manager (MGR) Nodes: Three hosts (ceph-1, ceph-2, ceph-3) are designated as manager nodes. These nodes handle higher-level cluster management tasks.

16 Object Storage Daemon (OSD) Nodes: Sixteen hosts (ceph-1, ceph-2, ceph-3, ceph-4 through ceph-16) are configured as OSD nodes. These nodes store the actual data within the Ceph cluster. All available data devices on these nodes will be used for storage.

2 RADOS Gateway (RGW) Nodes: Two hosts (ceph-19, ceph-20) are designated as RGW nodes. These provide object storage access via the S3 protocol.

1 Grafana Node: One host (ceph-18) is dedicated to running Grafana, a monitoring and visualization tool, providing a user interface for cluster monitoring. It's configured for anonymous access, which should be changed for production use.

Therefore, the topology is a distributed cluster with replication and high availability provided by the multiple monitor nodes, and scalability and storage capacity provided by the numerous OSD nodes. The managers provide high-level management, and the RGW provides external access to the object storage. Grafana enables monitoring of the entire system.

#### initial-ceph.conf:

The initial-ceph.conf gfile was used to set the images to a local registry, instead of the public ones. This is useful for airgapped installations and also for extra security.

```
[mgr]
mgr/cephadm/container_image_prometheus = internal-registry.org.local/cdnas/ose-prometheus:v4.15
mgr/cephadm/container_image_node_exporter = internal-registry.org.local/cdnas/ose-prometheus-node-exporter:v4.15
mgr/cephadm/container_image_grafana = internal-registry.org.local/cdnas/grafana-rhel9:latest --remove-signatures
mgr/cephadm/container_image_alertmanager = internal-registry.org.local/cdnas/ose-prometheus-alertmanager:v4.15 --remove-signatures
```

#### Bootstrap:

According to the documentation, you must run the bootstrap from MON 1 with user admin:

```bash
sudo cephadm --image internal-registry.org.local/cdnas/rhceph-7-rhel9:7-424 bootstrap --cluster-network 10.0.0.0/24 --mon-ip 10.0.0.20 --ssh-user admin --apply-spec initial-config.yaml --config initial-ceph.conf
```

At this point, if everything went well, the cluster will be already deployed. Now you can set up the specifics on your environment, such as CRUSH rules, radosgw pool, adjustments on the osd tree and so on:

#### OSD Tree:

Check the OSD Tree:
```bash
ceph osd tree
```

Create the new buckets:
```bash
ceph osd crush add-bucket custom root
ceph osd crush add-bucket curitiba datacenter
ceph osd crush move curitiba root=custom
ceph osd crush add-bucket room room
ceph osd crush move room datacenter=curitiba
ceph osd crush add-bucket AT45 rack
ceph osd crush add-bucket AT46 rack
ceph osd crush add-bucket AT47 rack
ceph osd crush move AT45 room=room-3b
ceph osd crush move AT46 room=room-3b
ceph osd crush move AT47 room=room-3b
```

Move the nodes:
```bash
ceph osd crush move ceph-1 rack=AT45
ceph osd crush move ceph-2 rack=AT45
```
Since it is a new cluster, no data movement is expected. However, in a production environment, moving nodes will definitely cause data to be moved, so you should proceed with caution.

#### CRUSH Rule:

In this example I created Erasure Code profiles and rules, and also a new replicated rule in order to avoid using the default one. This is for extra safety, since newly added OSDs get added to the default root on the OSD tree. By creating a new root and moving all OSDs under it, you prevent data movement if someone inadvertently adds an OSD to the cluster.  

Erasure Code profile:
```
ceph osd erasure-code-profile set 8_4 k=8 m=4 crush-root=custom
```

Erasure Code CRUSH Rule:
```
ceph osd crush rule create-erasure 8_4_erasure_rule 8_4
```

Replicated Rule for root custom:
```
ceph osd crush rule create-replicated replicated_rule_custom custom host
```

After moving all the OSDs from root default to root custom, the crush rules need to be adjusted:

New rules:
```json
[
    {
        "rule_id": 0,
        "rule_name": "replicated_rule",
        "type": 1,
        "steps": [
            {
                "op": "take",
                "item": -1,
                "item_name": "default"
            },
            {
                "op": "chooseleaf_firstn",
                "num": 0,
                "type": "host"
            },
            {
                "op": "emit"
            }
        ]
    },
    {
        "rule_id": 1,
        "rule_name": "2_2_erasure_rule",
        "type": 3,
        "steps": [
            {
                "op": "set_chooseleaf_tries",
                "num": 5
            },
            {
                "op": "set_choose_tries",
                "num": 100
            },
            {
                "op": "take",
                "item": -43,
                "item_name": "custom"
            },
            {
                "op": "chooseleaf_indep",
                "num": 0,
                "type": "host"
            },
            {
                "op": "emit"
            }
        ]
    },
    {
        "rule_id": 2,
        "rule_name": "4_2_erasure_rule",
        "type": 3,
        "steps": [
            {
                "op": "set_chooseleaf_tries",
                "num": 5
            },
            {
                "op": "set_choose_tries",
                "num": 100
            },
            {
                "op": "take",
                "item": -43,
                "item_name": "custom"
            },
            {
                "op": "chooseleaf_indep",
                "num": 0,
                "type": "host"
            },
            {
                "op": "emit"
            }
        ]
    },
    {
        "rule_id": 3,
        "rule_name": "8_4_erasure_rule",
        "type": 3,
        "steps": [
            {
                "op": "set_chooseleaf_tries",
                "num": 5
            },
            {
                "op": "set_choose_tries",
                "num": 100
            },
            {
                "op": "take",
                "item": -43,
                "item_name": "custom"
            },
            {
                "op": "chooseleaf_indep",
                "num": 0,
                "type": "host"
            },
            {
                "op": "emit"
            }
        ]
    },
    {
        "rule_id": 4,
        "rule_name": "replicated_rule_custom",
        "type": 1,
        "steps": [
            {
                "op": "take",
                "item": -43,
                "item_name": "serpro"
            },
            {
                "op": "chooseleaf_firstn",
                "num": 0,
                "type": "host"
            },
            {
                "op": "emit"
            }
        ]
    }
]
```

Modify the pool rules:
```bash
ceph osd pool set .mgr crush_rule replicated_rule_custom
ceph osd pool set .rgw.root crush_rule replicated_rule_custom
ceph osd pool set default.rgw.log crush_rule replicated_rule_custom
ceph osd pool set default.rgw.control crush_rule replicated_rule_custom
ceph osd pool set default.rgw.meta crush_rule replicated_rule_custom
```

#### Creation of a Pool for radosgw:
```
ceph osd pool create default.rgw.buckets.data 128 128 erasure 8_4 8_4_erasure_rule
ceph osd pool create default.rgw.buckets.index 128 128 replicated replicated_rule_custom
ceph osd pool create default.rgw.buckets.non-ec 128 128 replicated replicated_rule_custom
ceph osd pool application enable default.rgw.buckets.data rgw
ceph osd pool application enable default.rgw.buckets.index rgw
ceph osd pool application enable default.rgw.buckets.non-ec rgw
```

Test User for radosgw:
```
radosgw-admin user create --uid="poseidon" --display-name="poseidon"
```

Usually these pools get automatically created the first time you access the radosgw gateway and create a bucket. But since it is desirable to choose specific CRUSH rules, I prefer to create them previously according to my needs.