+++
title = "Building a Kubernetes Cluster with Kubespray: A Personal Journey"
description = "My experience setting up a Kubernetes cluster on 7 bare-metal nodes using Kubespray"
date =  "2024-11-09"
draft = false
toc = false
categories = ["ansible", "kubernetes" ]
tags = ["ansible", "kubernetes" ]
image = "kubespray.svg"
author = "Fabio M. Lopes"
+++
## Building a Kubernetes Cluster with Kubespray and Monitoring Stack: A Personal Journey

This blog post details my experience setting up a Kubernetes cluster on 7 bare-metal nodes using Kubespray, followed by the deployment of a comprehensive monitoring stack comprised of Rook, Mimir, Grafana, and Loki, which will be described in separated posts.  This setup provides robust storage, metrics, and logging capabilities for our internal use.

### Kubespray: The Orchestrator

Kubespray is a powerful Ansible-based tool for deploying and managing Kubernetes clusters. It automates the complex process of setting up a Kubernetes control plane and worker nodes, handling tasks like installing Kubernetes components, configuring networking, and managing etcd.  It allows for flexible customization through inventory files and group variables.  I chose version 2.26.0 for this deployment at the time.

### Prerequisites

Since I used bare metal servers that became available from another project, I previously installed the operating system and configured everything, from packages to network and authentication.

### Step-by-Step Setup

**1. Git Cloning and Docker Image:**

First, we clone the Kubespray repository and pull the necessary Docker image:

```bash
# Clone the Kubespray repository
git clone https://github.com/kubernetes-sigs/kubespray.git
git checkout v2.26.0

# Pull the Kubespray Docker image
docker pull quay.io/kubespray/kubespray:v2.26.0
```

This ensures we have the latest version (or the specific version we need) of Kubespray. The Docker image contains all necessary Ansible components and avoids potential conflicts with local installations. **Never** use the latest version commited to the repository, always use a stable release.

**2. Inventory Configuration:**

The heart of Kubespray's configuration lies in its inventory files. These define the nodes in your cluster, their roles, and relevant network information. My inventory file (`inventory/k8s-logs/hosts.yml`) looks like this:

```yaml
all:
  hosts:
    # Worker Nodes
    logsrv1234:
      ansible_host: 10.0.0.245  # Ansible connection IP
      ip: 10.1.0.45             # Internal IP address
      access_ip: 10.1.0.45       # IP for external access (if needed)
      node_labels:
        node-role.kubernetes.io/node: "" # Label indicating it's a worker node

    # ... (similar entries for other worker nodes logsrv1233 - logsrv1228) ...

    # Ingress Node
    ingress-1:
      ansible_host: 10.0.0.241
      ip: 10.1.0.41
      access_ip: 10.1.0.41
      node_labels:
        node-role.kubernetes.io/node: "" # Ingress node also needs node role

    # Master Nodes
    master-1:
      ansible_host: 10.0.0.242
      ip: 10.1.0.42
      access_ip: 10.1.0.42
      node_labels:
        node-role.kubernetes.io/master: "" # Label designating a master node

    # ... (similar entries for master-2 and master-3) ...

  children:
    # Grouping hosts based on their roles for simplified management
    kube_control_plane:
      hosts:
        master-1:
        master-2:
        master-3:
    kube_node:
      hosts:
        logsrv1234:
        logsrv1233:
        # ... other worker and ingress node ...
    etcd:
      hosts:
        master-1:
        master-2:
        master-3:
    k8s_cluster:
      children:
        kube_control_plane:
        kube_node:
    calico_rr:
      hosts: {} # Calico configuration (empty for now)
```

This meticulously defines each node, its IP addresses (ansible_host for Ansible connection, ip for cluster internal communication, and access_ip for external access), and its role within the Kubernetes cluster using node labels.  The `children` section groups hosts for easier management in Ansible playbooks.


**3. Group Variables:**

The `group_vars` directory contains YAML files that set global and group-specific variables for the Kubespray deployment.  The `all.yml` file sets general settings:

```yaml
---
bin_dir: /usr/local/bin
loadbalancer_apiserver_port: 6443
loadbalancer_apiserver_healthcheck_port: 8081
upstream_dns_servers:
  - 10.0.0.15
  - 10.0.0.16
http_proxy: "http://proxy.internal:3128" # environment without direct internet access
https_proxy: "http://proxy.internal:3128" # environment without direct internet access
no_proxy: "10.0.0.0/8,localhost,127.0.0.0/8,172.16.0.0/16,*.internal" # environment without direct internet access
no_proxy_exclude_workers: false
kube_webhook_token_auth: false
kube_webhook_token_auth_url_skip_tls_verify: false
ntp_enabled: false
ntp_manage_config: false
ntp_servers:
  - "0.pool.ntp.org iburst"
  - "1.pool.ntp.org iburst"
  - "2.pool.ntp.org iburst"
  - "3.pool.ntp.org iburst"
unsafe_show_logs: false
allow_unsupported_distribution_setup: false
```

And `k8s-cluster.yml` configures Kubernetes-specific settings:

```yaml
---
kube_version: v1.30.4        # Kubernetes version
kube_network_plugin: calico # CNI plugin to be used
kube_config_dir: /etc/kubernetes
kube_script_dir: "{{ bin_dir }}/kubernetes-scripts"
kube_manifest_dir: "{{ kube_config_dir }}/manifests"
kube_cert_dir: "{{ kube_config_dir }}/ssl"
kube_token_dir: "{{ kube_config_dir }}/tokens"
kube_api_anonymous_auth: true
local_release_dir: "/tmp/releases"
retry_stagger: 5
kube_owner: kube
kube_cert_group: kube-cert
kube_log_level: 2
credentials_dir: "{{ inventory_dir }}/credentials"
kube_network_plugin_multus: false
kube_service_addresses: 10.36.192.0/18
kube_pods_subnet: 172.16.0.0/16
kube_network_node_prefix: 24
enable_dual_stack_networks: false
kube_service_addresses_ipv6: fd85:ee78:d8a6:8607::1000/116
kube_pods_subnet_ipv6: fd85:ee78:d8a6:8607::1:0000/112
kube_network_node_prefix_ipv6: 120
kube_apiserver_ip: "{{ kube_service_addresses | ipaddr('net') | ipaddr(1) | ipaddr('address') }}"
kube_apiserver_port: 6443
kube_proxy_mode: ipvs
kube_proxy_strict_arp: true
kube_proxy_nodeport_addresses: >-
  {%- if kube_proxy_nodeport_addresses_cidr is defined -%}
  [{{ kube_proxy_nodeport_addresses_cidr }}]
  {%- else -%}
  []
  {%- endif -%}  
kube_encrypt_secret_data: false
cluster_name: k8s-logs
ndots: 2
dns_mode: coredns
enable_nodelocaldns: true
enable_nodelocaldns_secondary: false
nodelocaldns_ip: 169.254.25.10
nodelocaldns_health_port: 9254
nodelocaldns_second_health_port: 9256
nodelocaldns_bind_metrics_host_ip: false
nodelocaldns_secondary_skew_seconds: 5
enable_coredns_k8s_external: false
coredns_k8s_external_zone: k8s_external.local
enable_coredns_k8s_endpoint_pod_names: false
resolvconf_mode: host_resolvconf
deploy_netchecker: false
skydns_server: "{{ kube_service_addresses | ipaddr('net') | ipaddr(3) | ipaddr('address') }}"
skydns_server_secondary: "{{ kube_service_addresses | ipaddr('net') | ipaddr(4) | ipaddr('address') }}"
dns_domain: "{{ cluster_name }}"
container_manager: containerd
kata_containers_enabled: false
kubeadm_certificate_key: "{{ lookup('password', credentials_dir + '/kubeadm_certificate_key.creds length=64 chars=hexdigits') | lower }}"
k8s_image_pull_policy: IfNotPresent
kubernetes_audit: false
default_kubelet_config_dir: "{{ kube_config_dir }}/dynamic_kubelet_dir"
podsecuritypolicy_enabled: false
volume_cross_zone_attachment: false
persistent_volumes_enabled: false
event_ttl_duration: "1h0m0s"
auto_renew_certificates: false
kubeadm_patches:
  enabled: false
  source_dir: "{{ inventory_dir }}/patches"
  dest_dir: "{{ kube_config_dir }}/patches"
containerd_limit_open_file_num: 1048576
kube_proxy_metrics_bind_address: 0.0.0.0:10249
kube_vip_enabled: true
kube_vip_controlplane_enabled: true
kube_vip_address: 10.46.0.40
apiserver_loadbalancer_domain_name: master-k8s-logs.local
loadbalancer_apiserver:
  address: 10.0.0.40
  port: 6443
kube_vip_interface: ens224
kube_vip_services_enabled: false
kube_vip_arp_enabled: true
```

These variables define crucial parameters like the Kubernetes version, networking configuration, proxy settings, and more. The comments within the YAML files offer further detail on the purpose of these variables.

**4. SSH Key Generation:**

Next, an SSH key pair is generated for passwordless authentication to the bare metal nodes:

```bash
ssh-keygen -t rsa -f id_rsa_kubespray
```

This key will be used by Ansible to connect to and manage the cluster nodes without requiring manual password entry.  Remember to copy the public key to all the nodes' `authorized_keys` file.

**5. Running Kubespray within a Docker Container:**

To run Kubespray, we use a Docker container to isolate the environment:

```bash
docker run --rm -it \
  --mount type=bind,source="$(pwd)"/inventory/k8s-logs,dst=/inventory \
  --mount type=bind,source="${HOME}"/cluster-logs/kubespray/id_rsa_kubespray,dst=/root/.ssh/id_rsa \
  quay.io/kubespray/kubespray:v2.26.0 bash
```
This command runs the Kubespray image, mounting the inventory directory and the SSH private key into the container. The `--rm` flag removes the container after execution. The `bash` command starts a bash shell within the container.

**6. Running the Playbook:**

Once inside the container, the main Kubespray playbook is run:

```bash
ansible-playbook -i inventory/hosts.yml cluster.yml -b
```

`-i inventory/hosts.yml` specifies the inventory file, `cluster.yml` is the main playbook, and `-b` enables become (sudo) execution.  This command initiates the automated deployment of the entire Kubernetes cluster.

**7. Obtaining the kubeconfig:**

After successful playbook execution, the Kubernetes `admin.conf` file is located at `/etc/kubernetes/admin.conf` on any master node. This file is copied and used to authenticate with the cluster using `kubectl`.

**8. kubectl Adjustments:**

For access from outside the local network (e.g., via VPN), the `kubeconfig` file may need adjustments to use IP addresses instead of FQDNs for proper connection.

**9. Rook, Mimir, Grafana, and Loki Deployment (Not detailed here):**

Following the Kubernetes cluster setup, I installed Rook for persistent storage, Mimir for long-term metrics storage, Grafana for visualizing the metrics, and Loki for log aggregation. These steps are beyond the scope of this post but were crucial for creating our monitoring stack. I will describe each installation on dedicated posts.

This entire process provides a solid foundation for a robust and scalable Kubernetes cluster. The use of Kubespray significantly streamlined the deployment, and the monitoring stack ensures we can effectively manage and troubleshoot our infrastructure. The detailed inventory and group variable configurations provide a solid template for future cluster deployments.