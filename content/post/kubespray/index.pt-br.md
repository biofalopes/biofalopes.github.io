+++
title = "Construindo um Cluster Kubernetes com Kubespray: Uma Jornada Pessoal"
description = "Minha experiência configurando um cluster Kubernetes em 7 nós bare-metal usando Kubespray"
date = "2024-11-09"
draft = false
toc = false
categories = ["ansible", "kubernetes"]
tags = ["ansible", "kubernetes"]
image = "kubespray.svg"
author = "Fabio M. Lopes"
+++

## Construindo um Cluster Kubernetes com Kubespray e Stack de Monitoramento: Uma Jornada Pessoal

Este post detalha minha experiência configurando um cluster Kubernetes em 7 nós bare-metal usando Kubespray, seguido pela implantação de um stack de monitoramento abrangente composto por Rook, Mimir, Grafana e Loki, que serão descritos em posts separados. Esta configuração fornece recursos robustos de armazenamento, métricas e logs para nosso uso interno.

### Kubespray: O Orquestrador

Kubespray é uma ferramenta poderosa baseada em Ansible para implantar e gerenciar clusters Kubernetes. Ele automatiza o processo complexo de configurar um plano de controle Kubernetes e nós de trabalho, lidando com tarefas como instalar componentes Kubernetes, configurar rede e gerenciar etcd. Ele permite personalização flexível por meio de arquivos de inventário e variáveis de grupo. Escolhi a versão 2.26.0 para esta implantação na época.

### Pré-requisitos

Como usei servidores bare metal que ficaram disponíveis de outro projeto, instalei previamente o sistema operacional e configurei tudo, desde pacotes até rede e autenticação.

### Configuração Passo a Passo

**1. Clonagem do Git e Imagem Docker:**

Primeiro, clonamos o repositório Kubespray e puxamos a imagem Docker necessária:

```bash
# Clona o repositório Kubespray
git clone https://github.com/kubernetes-sigs/kubespray.git
git checkout v2.26.0

# Puxa a imagem Docker do Kubespray
docker pull quay.io/kubespray/kubespray:v2.26.0
```

Isso garante que tenhamos a versão mais recente (ou a versão específica que precisamos) do Kubespray. A imagem Docker contém todos os componentes Ansible necessários e evita possíveis conflitos com instalações locais. **Nunca** use a versão mais recente commitada no repositório, sempre use uma versão estável.

**2. Configuração do Inventário:**

O coração da configuração do Kubespray reside em seus arquivos de inventário. Eles definem os nós em seu cluster, suas funções e informações de rede relevantes. Meu arquivo de inventário (`inventory/k8s-logs/hosts.yml`) se parece com isto:

```yaml
all:
  hosts:
    # Nós de Trabalho
    logsrv1234:
      ansible_host: 10.0.0.245  # IP de conexão Ansible
      ip: 10.1.0.45             # Endereço IP interno
      access_ip: 10.1.0.45       # IP para acesso externo (se necessário)
      node_labels:
        node-role.kubernetes.io/node: "" # Rótulo indicando que é um nó de trabalho

    # ... (entradas semelhantes para outros nós de trabalho logsrv1233 - logsrv1228) ...

    # Nó de Ingress
    ingress-1:
      ansible_host: 10.0.0.241
      ip: 10.1.0.41
      access_ip: 10.1.0.41
      node_labels:
        node-role.kubernetes.io/node: "" # Nó de Ingress também precisa de função de nó

    # Nós Master
    master-1:
      ansible_host: 10.0.0.242
      ip: 10.1.0.42
      access_ip: 10.1.0.42
      node_labels:
        node-role.kubernetes.io/master: "" # Rótulo designando um nó master

    # ... (entradas semelhantes para master-2 e master-3) ...

  children:
    # Agrupando hosts com base em suas funções para gerenciamento simplificado
    kube_control_plane:
      hosts:
        master-1:
        master-2:
        master-3:
    kube_node:
      hosts:
        logsrv1234:
        logsrv1233:
        # ... outros nós de trabalho e ingress ...
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
      hosts: {} # Configuração do Calico (vazia por enquanto)
```

Isso define meticulosamente cada nó, seus endereços IP (ansible\_host para conexão Ansible, ip para comunicação interna do cluster e access\_ip para acesso externo) e sua função dentro do cluster Kubernetes usando rótulos de nó. A seção `children` agrupa os hosts para facilitar o gerenciamento nos playbooks do Ansible.

**3. Variáveis de Grupo:**

O diretório `group_vars` contém arquivos YAML que definem variáveis globais e específicas do grupo para a implantação do Kubespray. O arquivo `all.yml` define configurações gerais:

```yaml
---
bin_dir: /usr/local/bin
loadbalancer_apiserver_port: 6443
loadbalancer_apiserver_healthcheck_port: 8081
upstream_dns_servers:
  - 10.0.0.15
  - 10.0.0.16
http_proxy: "http://proxy.internal:3128" # ambiente sem acesso direto à internet
https_proxy: "http://proxy.internal:3128" # ambiente sem acesso direto à internet
no_proxy: "10.0.0.0/8,localhost,127.0.0.0/8,172.16.0.0/16,*.internal" # ambiente sem acesso direto à internet
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

E `k8s-cluster.yml` configura as configurações específicas do Kubernetes:

```yaml
---
kube_version: v1.30.4        # Versão do Kubernetes
kube_network_plugin: calico # Plugin CNI a ser usado
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

Essas variáveis definem parâmetros cruciais como a versão do Kubernetes, configuração de rede, configurações de proxy e muito mais. Os comentários dentro dos arquivos YAML oferecem mais detalhes sobre o propósito dessas variáveis.

**4. Geração de Chave SSH:**

Em seguida, um par de chaves SSH é gerado para autenticação sem senha nos nós bare metal:

```bash
ssh-keygen -t rsa -f id_rsa_kubespray
```

Esta chave será usada pelo Ansible para se conectar e gerenciar os nós do cluster sem exigir a entrada manual de senha. Lembre-se de copiar a chave pública para o arquivo `authorized_keys` de todos os nós.

**5. Executando o Kubespray dentro de um Contêiner Docker:**

Para executar o Kubespray, usamos um contêiner Docker para isolar o ambiente:

```bash
docker run --rm -it \
  --mount type=bind,source="$(pwd)"/inventory/k8s-logs,dst=/inventory \
  --mount type=bind,source="${HOME}"/cluster-logs/kubespray/id_rsa_kubespray,dst=/root/.ssh/id_rsa \
  quay.io/kubespray/kubespray:v2.26.0 bash
```

Este comando executa a imagem Kubespray, montando o diretório de inventário e a chave privada SSH no contêiner. A flag `--rm` remove o contêiner após a execução. O comando `bash` inicia um shell bash dentro do contêiner.

**6. Executando o Playbook:**

Uma vez dentro do contêiner, o playbook principal do Kubespray é executado:

```bash
ansible-playbook -i inventory/hosts.yml cluster.yml -b
```

`-i inventory/hosts.yml` especifica o arquivo de inventário, `cluster.yml` é o playbook principal e `-b` habilita a execução become (sudo). Este comando inicia a implantação automatizada de todo o cluster Kubernetes.

**7. Obtendo o kubeconfig:**

Após a execução bem-sucedida do playbook, o arquivo Kubernetes `admin.conf` está localizado em `/etc/kubernetes/admin.conf` em qualquer nó master. Este arquivo é copiado e usado para autenticar com o cluster usando `kubectl`.

**8. Ajustes do kubectl:**

Para acesso de fora da rede local (por exemplo, via VPN), o arquivo `kubeconfig` pode precisar de ajustes para usar endereços IP em vez de FQDNs para uma conexão adequada.

**9. Implantação de Rook, Mimir, Grafana e Loki (Não detalhado aqui):**

Após a configuração do cluster Kubernetes, instalei o Rook para armazenamento persistente, o Mimir para armazenamento de métricas de longo prazo, o Grafana para visualizar as métricas e o Loki para agregação de logs. Essas etapas estão além do escopo deste post, mas foram cruciais para criar nosso stack de monitoramento. Descreverei cada instalação em posts dedicados.

Todo este processo fornece uma base sólida para um cluster Kubernetes robusto e escalável. O uso do Kubespray simplificou significativamente a implantação, e o stack de monitoramento garante que possamos gerenciar e solucionar problemas de nossa infraestrutura de forma eficaz. As configurações detalhadas de inventário e variáveis de grupo fornecem um modelo sólido para futuras implantações de cluster.
