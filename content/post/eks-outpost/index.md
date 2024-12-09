+++
title = "Deploying a Local EKS Cluster on AWS Outposts"
description = "Using terraform to deploy the resources and the parameters required for the local Control Plane"
date =  "2024-12-06"
draft = false
toc = false
categories = ["aws", "terraform", "kubernetes" ]
tags = ["aws", "terraform", "kubernetes" ]
image = "eks.jpg"
author = "Fabio M. Lopes"
+++

The Terraform code provisions an EKS cluster on an AWS Outpost, with the control plane running locally on the Outpost. This differs significantly from deploying an EKS cluster in a standard AWS region, primarily in how worker nodes are managed.

The Amazon EKS update history demonstrates the platform's continuous evolution, focusing on enhanced security, scalability, and integration with other AWS services. Since its initial release in June 2018, there's been a significant increase in available features and functionalities, including support for newer Kubernetes versions, expansion to new AWS regions, and the introduction of new deployment options like Fargate and local clusters on AWS Outposts, which is the focus of this work. The introduction of features like managed node groups significantly simplified infrastructure management, automating tasks such as provisioning and lifecycle management of nodes. The availability of EKS-optimized AMIs, including options with GPU support and the Bottlerocket operating system, offers greater flexibility and performance for diverse workloads. Furthermore, integration with services like Amazon EBS, EFS, and FSx for Lustre, via CSI drivers, expanded storage options for the clusters. However, for a local Amazon EKS cluster on AWS Outposts, these resources are significantly more limited; managed node groups are unavailable.

We also observed that the Control Plane AMIs are automatically provisioned with Bottlerocket, where we only specify the major Kubernetes release, and the latest minor version is selected. The challenge lies in provisioning worker nodes, which requires selecting an EKS-optimized AMI from the available options in the AWS catalog; only versions with Amazon Linux 2023 are found. While not inherently problematic, ensuring both control plane and worker nodes use the same Kubernetes version proved difficult, requiring testing three or four AMIs to find the closest match.

Finally, we lacked the usual EKS add-ons, which in this scenario require manual provisioning, such as CSI, CNI, Cluster Load Balancer Controller, Metrics Server, or Kube-prometheus-stack, to name a few but not necessarily all.

Important Considerations for Provisioning EKS on Outposts:
AMI: Ensure you use an Amazon Machine Image (AMI) compatible with your Outpost and the chosen Kubernetes version. Review the use of data.aws_ami; manually specifying the AMI is strongly recommended to guarantee compatibility. Not all region-available versions are available on the Outpost; there's usually a two-version lag.

Security: Carefully review security rules in the Security Groups. Limit access only to necessary ports and IPs.

Scalability: Adjust min_size, desired_capacity, and max_size values in the ASG to meet scalability needs. Arbitrary values were configured only to enable code construction and simplified usage tests for the proof of concept.

High Availability: For high availability, consider creating the cluster across multiple subnets associated with the Outpost. Due to limitations in the proof-of-concept environment, only available subnets were used.

Monitoring: Implement a monitoring system for the EKS cluster and worker nodes. CloudWatch is the most straightforward option, but due to associated costs and integration with pre-existing tools, other options might be more suitable, such as a Grafana stack (Loki, Mimir, Grafana, Tempo, Prometheus).

The following is a commented version of the code, highlighting key configurations and differences compared to an EKS cluster in a region:

### Part 1: EKS Control Plane
This section describes the infrastructure required for the EKS control plane on the Outpost. Note that the control plane configuration is similar to a region cluster, but with the crucial addition of the outpost_config.

#### providers.tf:
```yaml
provider "aws" {
  region  = local.region
}
```

#### terraform.tf:
```yaml
terraform {
  backend "s3" {
    bucket = "outposts-bucket"
    key    = "eks-local-terraform-state"
    region = "us-east-1"
  }
}
```

#### variables.tf:
```yaml
variable "eks_cluster_name" {
  type    = string
  default = "eks_local"
}
variable "eks_cluster_version" {
  type    = string
  default = "1.30" # available versions differ between regional and local cluster
}
variable "eks_vpc" {
  type    = string
  default = "vpc-id0000" # replace with your vpc id 
}
variable "eks_subnet" {
  type    = string
  default = "subnet-id0000" # replace with your subnet id 
}
variable "bastion_subnet" {
  type    = string
  default = "subnet-id0000" # replace with your subnet id  
}
variable "control_plane_instance_type" {
  type    = string
  default = "m5.large" # Choose an instance type that is available in your outpost
}
variable "tags" {
  type        = map(any)
  description = "(Optional) Tags to apply to all tag-able resources."
  default     = {
    terraform = "true"
  }
}
```

#### outputs.tf:
```yaml
output "eks_cluster_endpoint" {
  description = "EKS Cluster Endpoint"
  value       = aws_eks_cluster.eks_cluster.endpoint
}

output "eks_cluster_ca" {
  value = base64decode(aws_eks_cluster.eks_cluster.certificate_authority[0].data)
}

output "eks_cluster_arn" {
  description = "EKS Cluster ARN"
  value       = aws_eks_cluster.eks_cluster.arn
}

output "kubeconfig" {
  value = <<EOF
apiVersion: v1
kind: Config
clusters:
- cluster:
    server: ${aws_eks_cluster.eks_cluster.endpoint}
    certificate-authority-data: ${aws_eks_cluster.eks_cluster.certificate_authority.0.data}
  name: ${aws_eks_cluster.eks_cluster.name}
contexts:
- context:
    cluster: ${aws_eks_cluster.eks_cluster.name}
    user: ${aws_eks_cluster.eks_cluster.name}
  name: ${aws_eks_cluster.eks_cluster.name}
current-context: ${aws_eks_cluster.eks_cluster.name}
users:
- name: ${aws_eks_cluster.eks_cluster.name}
  user:
    exec:
      apiVersion: "client.authentication.k8s.io/v1beta1"
      command: "aws"
      args:
        - "eks"
        - "get-token"
        - "--cluster-name"
        - "${aws_eks_cluster.eks_cluster.name}"
        - "--region"
        - "${local.region}"
EOF
  description = "Kubeconfig for the EKS Cluster"
  sensitive   = true
}
```

#### main.tf:
```yaml
locals {
  region    = "us-east-1"
}

data "aws_outposts_outpost" "my_outpost" {
  id = "op-06d4362ae79bc4247"  # Outpost id
}

data "aws_vpc" "vpc_eks" {
  id = var.eks_vpc
}
data "aws_subnet" "vpc_eks" {
  id = var.eks_subnet
}

data "aws_subnet" "vpc_bastion" {
  id = var.bastion_subnet
}

# Role for the Control Plane
resource "aws_iam_role" "eks_cluster_role" {
  name = "eks-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      },
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Control Plane Policies
resource "aws_iam_role_policy_attachment" "eks_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster_role.name
}

resource "aws_iam_role_policy_attachment" "eks_LocalOutpost_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSLocalOutpostClusterPolicy"
  role       = aws_iam_role.eks_cluster_role.name
}

resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_cluster_role.name
}

resource "aws_iam_role_policy_attachment" "eks_VPCResourceController_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSVPCResourceController"
  role       = aws_iam_role.eks_cluster_role.name
}

resource "aws_iam_role_policy_attachment" "eks_ssm_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  role       = aws_iam_role.eks_cluster_role.name
}

resource "aws_iam_role_policy_attachment" "eks_cloudwatch_logs" {
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
  role       = aws_iam_role.eks_cluster_role.name
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "eks_log_group" {
  name              = "/aws/eks/${var.eks_cluster_name}/cluster-logs"
  retention_in_days = 7
}

# Security group for EKS control plane in Outposts
resource "aws_security_group" "control_plane_sg" {
  name        = "${var.eks_cluster_name}-control-plane-sg"
  vpc_id      = data.aws_vpc.vpc_eks.id
  description = "Security group for EKS control plane in Outposts"

  ingress {
    description = "Allow inbound HTTPS for EKS API server"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [data.aws_subnet.subnet_eks.cidr_block, data.aws_subnet.subnet_bastion.cidr_block]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EKS Cluster
resource "aws_eks_cluster" "eks_cluster" {
  name    = var.eks_cluster_name
  version = var.eks_cluster_version
  role_arn = aws_iam_role.eks_cluster_role.arn

  enabled_cluster_log_types = ["audit"] # choose accordingly

  vpc_config {
    endpoint_private_access = true
    endpoint_public_access  = false
    security_group_ids      = [aws_security_group.control_plane_sg.id]
    subnet_ids              = [data.aws_subnet.subnet_eks.id]
  }

  outpost_config {
    outpost_arns                = [data.aws_outposts_outpost.my_outpost.arn]
    control_plane_instance_type = var.control_plane_instance_type
  }

  access_config {
    authentication_mode                         = "CONFIG_MAP"  # Local Outpost clusters only support config_map
    bootstrap_cluster_creator_admin_permissions = true
  }

  upgrade_policy {
    support_type = "STANDARD" # you can set it to anything but it will end up as EXTENDED.
  }

  tags = var.tags

  depends_on = [
    aws_iam_role_policy_attachment.eks_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.eks_VPCResourceController_policy,
    aws_iam_role_policy_attachment.eks_LocalOutpost_policy
  ]

}

# writes a kubeconfig file locally
resource "null_resource" "write_kubeconfig" {
  provisioner "local-exec" {
    command = <<EOT
      aws eks update-kubeconfig --name ${aws_eks_cluster.eks_cluster.name} --region ${local.region}
    EOT
  }
}
```

After provisioning the Control Plane, it's necessary to configure the aws-auth ConfigMap with the role that will be associated with the worker nodes. In this example it was also associated the instance profile associated with a bastion host, used to access the EKS cluster via kubectl:

#### Config Map aws-auth:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: arn:aws:iam::597088017848:role/eks-nodegroup-role
      username: system:node:{{EC2PrivateDNSName}}
      groups:
        - system:bootstrappers
        - system:nodes
    - rolearn: arn:aws:iam::597088017848:role/myrole-ec2-ssm-enhanced
      username: bastion
      groups:
        - system:masters
```

### Part 2: EKS Nodes

When provisioning EKS on Outpost as a Local Cluster, it is not possible to use Node Groups. The solution is to create a Launch Template, associate it with an Autoscaling Group and use a _user-data_ script to configure the nodes in the EKS cluster.

#### providers.tf:
```yaml
provider "aws" {
  region  = local.region
}
```

#### terraform.tf:
```yaml
terraform {
  backend "s3" {
    bucket = "outposts-bucket"
    key    = "eks-local-terraform-state"
    region = "us-east-1"
  }
}
```

#### variables.tf:
```yaml
variable "eks_cluster_name" {
  type    = string
  default = "eks_local"
}
variable "eks_cluster_version" {
  type    = string
  default = "1.30" # available versions differ between regional and local cluster
}
variable "eks_vpc" {
  type    = string
  default = "vpc-id0000" # replace with your vpc id 
}
variable "eks_subnet" {
  type    = string
  default = "subnet-id0000" # replace with your subnet id 
}
variable "bastion_subnet" {
  type    = string
  default = "subnet-id0000" # replace with your subnet id  
}
variable "control_plane_instance_type" {
  type    = string
  default = "m5.large"
}
variable "control_plane_instance_type" {
  type    = string
  default = "m5.large" # Choose an instance type that is available in your outpost
}
variable "node_group_min_size" {
  type    = string
  default = "1"
}
variable "node_group_desired_size" {
  type    = string
  default = "2"
}
variable "node_group_max_size" {
  type    = string
  default = "3"
}
variable "node_group_name" {
  type        = string
  description = "(Optional) The name to be used for the self-managed node group. By default, the module will generate a unique name."
  default     = "node_group"
}
variable "tags" {
  type        = map(any)
  description = "(Optional) Tags to apply to all tag-able resources."
  default     = {
    terraform = "true"
  }
}
```

#### main.tf:
```yaml
locals {
  region    = "us-east-1"
}

data "aws_outposts_outpost" "my_outpost" {
  id = "op-id0000" # your Outpost ID
}

data "aws_vpc" "vpc_eks" {
  id = var.eks_vpc
}
data "aws_subnet" "subnet_eks" {
  id = var.eks_subnet
}

data "aws_subnet" "subnet_bastion" {
  id = var.bastion_subnet
}

data "aws_eks_cluster" "eks_cluster" {
  name = var.eks_cluster_name
}

data "aws_security_group" "control_plane_sg" {
  name = "${var.eks_cluster_name}-control-plane-sg"
}

# Instance Type
data "aws_ec2_instance_type" "selected_instance" {
  instance_type = var.node_group_instance_type
}

# AMI
data "aws_ami" "eks_ami" {
  owners      = ["amazon"]
  most_recent = true
  filter {
    name   = "name"
    values = ["amazon-eks-node-${data.aws_eks_cluster.eks_cluster.version}*"]
  }
  filter {
    name   = "architecture"
    values = data.aws_ec2_instance_type.selected_instance.supported_architectures
  }
  filter {
    name   = "virtualization-type"
    values = data.aws_ec2_instance_type.selected_instance.supported_virtualization_types
  }
  filter {
    name   = "root-device-type"
    values = data.aws_ec2_instance_type.selected_instance.supported_root_device_types
  }
}

# User Data for the Worker Nodes - Script to join the nodes to the EKS cluster. `--enable-local-outpost true` is crucial.
data "template_file" "user_data" {
  template = <<-EOT
              #!/bin/bash
              set -o xtrace
              /etc/eks/bootstrap.sh ${var.eks_cluster_name} \
              --enable-local-outpost true \
              --cluster-id '${data.aws_eks_cluster.eks_cluster.id}'
            EOT
}

# Worker Nodes Role
resource "aws_iam_role" "eks_nodegroup_role" {
  name = "eks-nodegroup-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      },
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Node Policies - These policies ensure that nodes have correct access to the necessary resources.
resource "aws_iam_role_policy_attachment" "nodegroup_cni_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_nodegroup_role.name
}

resource "aws_iam_role_policy_attachment" "nodegroup_worker_node_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_nodegroup_role.name
}

resource "aws_iam_role_policy_attachment" "nodegroup_ecr_read_only_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.eks_nodegroup_role.name
}

resource "aws_iam_role_policy_attachment" "nodegroup_ssm_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  role       = aws_iam_role.eks_nodegroup_role.name
}

# IAM Instance Profile
resource "aws_iam_instance_profile" "eks_node_instance_profile" {
  name = "${var.eks_cluster_name}-node-instance-profile"
  role = aws_iam_role.eks_nodegroup_role.name
}

# Worker Nodes Security group
resource "aws_security_group" "nodes_sg" {
  name        = "${var.eks_cluster_name}-nodes-sg"
  vpc_id      = data.aws_vpc.vpc_eks.id
  description = "Security group for EKS nodes in Outposts"

  ingress {
    description = "Allow all node-to-node communication"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    self        = true
  }

  ingress {
    description     = "Allow nodes to communicate with EKS control plane"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [data.aws_security_group.control_plane_sg.id]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Launch Template for the Worker Nodes
resource "aws_launch_template" "outposts_node_template" {
  name_prefix   = "${var.eks_cluster_name}-node-template-"
  # image_id      = data.aws_ami.eks_ami.id
  image_id      =  "ami-023745e977279d33c" # Either use the filters set previously or pick manually an ami from the catalog to ensure version matching with the control plane nodes
  instance_type = var.node_group_instance_type
  user_data     = base64encode(data.template_file.user_data.rendered)

  vpc_security_group_ids = [aws_security_group.nodes_sg.id]
  key_name               = "my-precious-key" # SSH key

  iam_instance_profile {
    name = aws_iam_instance_profile.eks_node_instance_profile.name
  }
}

# ASG for Worker Nodes
resource "aws_autoscaling_group" "outposts_asg" {
  name                = "${var.eks_cluster_name}-asg"
  desired_capacity    = 2
  max_size            = 4
  min_size            = 1
  vpc_zone_identifier = [data.aws_subnet.subnet_eks.id]
  launch_template {
    id      = aws_launch_template.outposts_node_template.id
    version = "$Latest"
  }

  health_check_type         = "EC2"
  health_check_grace_period = 300
  force_delete              = true

  tag {
    key                 = "Name"
    value               = "${var.eks_cluster_name}-${var.node_group_name}"
    propagate_at_launch = true
  }
  tag {
    key                 = "kubernetes.io/cluster/${var.eks_cluster_name}"
    value               = "owned"
    propagate_at_launch = true
  }
}
```

After a couple of minutes, the worker nodes will get registered in the kubernetes cluster. The master nodes remain as NotReady due to the absence of the CNI. 