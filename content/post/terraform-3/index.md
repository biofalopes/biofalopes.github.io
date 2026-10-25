+++
title = "Raising the Bar in Platform Operations: Moving Beyond Day-1 Terraform Provisioning"
description = "Overcoming the anti-pattern of using Terraform for initial Day-1 infrastructure provisioning and abandoning it on Day 2."
date =  "2026-10-25"
draft = false
toc = false
categories = ["terraform", "SRE", "DevOps", "Production Engineering"]
tags = ["terraform", "SRE", "DevOps", "Production Engineering"]
image = "terraform.jpg"
author = "Fabio M. Lopes"
+++

In enterprise environments operating on sovereign clouds, AWS Outposts, or air-gapped infrastructure, a frustrating anti-pattern frequently takes root: **using Terraform for initial Day-1 infrastructure provisioning and abandoning it on Day 2**.

Day 1 goes smoothly. The platform team writes HCL modules, provisions the VPCs, databases, load balancers, and ECS clusters, and delivers the environment. But once workloads go live, fear sets in. Management worries that running `terraform apply` on Day 2 might accidentally destroy a production database, overwrite container image tags updated by application teams, or conflict with network settings managed by other departments. As a result, Day-2 operations degrade into manual console tweaks, undocumented fixes, and severe state drift.

Overcoming this fear requires elevating platform operations beyond basic resource creation. By establishing strict team boundaries, isolating state files, and decoupling infrastructure code from application delivery pipelines, teams can safely operate Terraform in production with complete confidence.

---

## The Operational Context: Multi-Account & Team Topology

To understand how to solve the Day-2 dilemma, we must first look at a common enterprise deployment model operating on AWS Outposts across three isolated accounts:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             AWS Outposts Environment                             │
│                                                                                  │
│   ┌───────────────────────┐  ┌───────────────────────┐  ┌────────────────────┐   │
│   │   Development Acct    │  │  Pre-Production Acct  │  │  Production Acct   │   │
│   │   (Test & Dev)        │  │  (Staging / Pre)      │  │  (Zero Partner     │   │
│   │                       │  │                       │  │   Direct Access)   │   │
│   └───────────────────────┘  └───────────┬───────────┘  └─────────▲──────────┘   │
└──────────────────────────────────────────┼────────────────────────┼──────────────┘
                                           │ ECR Image              │ Controlled
                                           │ Sync                   │ Deployment
                                           ▼                        │ Pipeline
                                ┌───────────────────────────────────┴──────────┐
                                │          Internal GitLab CI/CD               │
                                │  • Partner pushes application code           │
                                │  • Automated build & ECR image sync          │
                                │  • Task Definition Revision & Deploy Gate    │
                                └──────────────────────────────────────────────┘

```

### Team Boundaries & Responsibilities

In this model, four distinct groups interact with the platform:

1. **Network Team:** Owns the core VPCs, Subnets, Direct Connect, and primary CIDR blocks.
2. **Security Team:** Manages edge security, central IAM boundary policies, and institutional F5 WAF rules.
3. **Platform / Infrastructure Team (SRE):** Owns ECS Clusters, Capacity Providers, Databases (RDS/ElastiCache), Storage (NFS/EFS/S3), ALBs, and Terraform IaC.
4. **External Application Partners:** Develop Node.js and PHP microservices. They version code in an internal, self-hosted GitLab instance and have **zero direct IAM access to the AWS Production Account**.

---

## Pattern 1: Respecting Team Boundaries via Data Sources

A common cause of Day-2 incidents is Terraform attempting to modify resources owned by other departments. If your HCL code defines a VPC as a `resource "aws_vpc"`, Terraform expects full ownership of that VPC. If the Network Team alters a tag or CIDR block outside your code, your next `terraform apply` will attempt to revert or recreate it.

### The Solution: Only Consume External Assets as Data Sources

Never declare network infrastructure or edge security appliances as `resource` blocks if your team does not own their lifecycle. Query them dynamically via `data` sources using explicit filters or tags:

```hcl
# data_sources.tf

# 1. Query VPC owned and managed by the Network Team
data "aws_vpc" "network_team_vpc" {
  filter {
    name   = "tag:Name"
    values = ["PROD-NETWORK-VPC"]
  }
}

# 2. Query App Subnets managed by Network Team
data "aws_subnets" "app_subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.network_team_vpc.id]
  }
  tags = {
    Tier = "Private-App"
  }
}

# 3. Reference Security Groups owned by Security Team (e.g., F5 WAF)
data "aws_security_group" "f5_waf_sg" {
  filter {
    name   = "group-name"
    values = ["f5-waf-edge-allowed-sg"]
  }
}

```

By using `data` blocks, Terraform treats these assets as read-only references. Your platform code can attach ALBs to the subnets or link security rules to the F5 WAF without any risk of altering or deleting the underlying network resources.

---

## Pattern 2: Decoupling IaC from Application Deployments

The single biggest friction point between Platform and Application teams on ECS is **Task Definition image tag drift**.

When an external partner publishes a new release (e.g., updating a Node.js image tag from `v1.2.0` to `v1.2.1`), an automated pipeline updates the ECS Service to point to the new task revision. However, your Terraform state file still references `v1.2.0`. If a platform engineer runs `terraform apply` two weeks later to resize an ALB, Terraform will detect the image mismatch and downgrade the production application to `v1.2.0`.

### The Solution: `lifecycle { ignore_changes }`

To solve this, use Terraform to provision the foundational ECS Cluster, Capacity Providers, Load Balancers, Security Groups, and initial ECS Service structure, but yield ongoing control of the container image and desired task count to the application deployment pipeline:

```hcl
# ecs_service.tf

resource "aws_ecs_service" "app_service" {
  name            = "app-core-service"
  cluster         = aws_ecs_cluster.outposts_cluster.id
  task_definition = aws_ecs_task_definition.initial_template.arn
  desired_count   = 2

  capacity_provider_strategy {
    capacity_provider = aws_ecs_capacity_provider.asg_provider.name
    weight            = 100
  }

  network_configuration {
    subnets         = data.aws_subnets.app_subnets.ids
    security_groups = [aws_security_group.allow_app_sg.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app_tg.arn
    container_name   = "app"
    container_port   = 8080
  }

  # CRITICAL DAY-2 GUARDRAIL:
  # Prevents Terraform from reverting image revisions or replica counts 
  # updated dynamically by application CI/CD pipelines.
  lifecycle {
    ignore_changes = [
      task_definition,
      desired_count
    ]
  }
}

```

With `ignore_changes` configured, your platform team can modify infrastructure parameters (scaling thresholds, target group health checks, security group ingress rules) at any time without interfering with application deployments.

---

## Pattern 3: Least-Privilege Security Group Chaining

Building a robust Day-2 architecture requires strict traffic segregation. Rather than opening broad IP ranges across subnets, construct a chained security group architecture following the exact physical flow of data:

`Internet ──> F5 WAF ──> Application Load Balancer ──> ECS Application ──> Database / NFS`

```hcl
# security_groups.tf

# 1. ALB Security Group (Accepts HTTPS only from F5 WAF IPs)
resource "aws_security_group" "allow_waf_sg" {
  name        = "allow-waf-sg"
  description = "Allow F5 WAF access to ALB"
  vpc_id      = data.aws_vpc.network_team_vpc.id

  ingress {
    description = "HTTPS from F5 WAF endpoints"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.f5_waf_allowed_ips
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 2. Application Security Group (Accepts traffic ONLY from ALB SG)
resource "aws_security_group" "allow_app_sg" {
  name        = "allow-app-sg"
  description = "Allow traffic from ALB to application tasks"
  vpc_id      = data.aws_vpc.network_team_vpc.id

  ingress {
    description     = "HTTP from ALB Security Group"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.allow_waf_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 3. Database Security Group (Accepts traffic ONLY from App SG)
resource "aws_security_group" "allow_db_sg" {
  name        = "allow-db-sg"
  description = "Allow database access from application tasks"
  vpc_id      = data.aws_vpc.network_team_vpc.id

  ingress {
    description     = "PostgreSQL port from App SG"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.allow_app_sg.id]
  }
}

# 4. Storage Security Group (Accepts NFS traffic ONLY from App SG)
resource "aws_security_group" "allow_nfs_sg" {
  name        = "allow-nfs-sg"
  description = "Allow NFS access from application tasks"
  vpc_id      = data.aws_vpc.network_team_vpc.id

  ingress {
    description     = "NFS 2049 from App SG"
    from_port       = 2049
    to_port         = 2049
    protocol        = "tcp"
    security_groups = [aws_security_group.allow_app_sg.id]
  }
}

```

---

## Pattern 4: Eliminating Deployment Toil with Self-Service Pipelines

In many legacy setups, external application partners push container images to a Pre-Production ECR, an automated job synchronizes the image to Production ECR, and then **a manual support ticket is opened asking the platform team to update the ECS task definition revision in Production**.

This manual step introduces operational friction, human error, and unnecessary delay.

To eliminate this toil without giving external partners direct AWS credentials, delegate application updates to an automated **internal GitLab CI pipeline** using scoped IAM Roles via OIDC.

```
[Partner Pushes Code] ──> [GitLab CI: Build & Test] ──> [Sync to Prod ECR]
                                                               │
                                                               ▼
                                                  [Approval Gate in GitLab]
                                                               │ (Lead Approves)
                                                               ▼
                                                  [AWS ECS Update-Service]

```

### Self-Service Pipeline Definition (`.gitlab-ci.yml`)

```yaml
stages:
  - build
  - sync-ecr
  - deploy-approval
  - deploy-prod

variables:
  AWS_REGION: "sa-east-1"
  PROD_ECR_REPO: "123456789012.dkr.ecr.sa-east-1.amazonaws.com/app-prod"
  ECS_CLUSTER: "ecs-outposts-prod"
  ECS_SERVICE: "app-core-service"

build_preprod:
  stage: build
  script:
    - docker build -t $PROD_ECR_REPO:$CI_COMMIT_SHA .
    - docker push $PROD_ECR_REPO:$CI_COMMIT_SHA

sync_to_prod_ecr:
  stage: sync-ecr
  script:
    - echo "Synchronizing container image $CI_COMMIT_SHA to Production ECR..."
    # Automated ECR image replication logic

approve_prod_deployment:
  stage: deploy-approval
  script:
    - echo "Deployment approved for commit $CI_COMMIT_SHA"
  when: manual # Requires explicit UI approval from Tech Lead / SRE
  only:
    - main

deploy_production_ecs:
  stage: deploy-prod
  script:
    - echo "Registering new Task Definition revision for release $CI_COMMIT_SHA..."
    - TASK_DEF=$(aws ecs describe-task-definition --task-definition app-core-task)
    - NEW_TASK_DEF=$(echo $TASK_DEF | jq --arg IMAGE "$PROD_ECR_REPO:$CI_COMMIT_SHA" '.taskDefinition | .containerDefinitions[0].image = $IMAGE | del(.taskDefinitionArn, .revision, .status, .requiresAttributes, .compatibilities, .registeredAt, .registeredBy)')
    - NEW_TASK_INFO=$(aws ecs register-task-definition --cli-input-json "$NEW_TASK_DEF")
    - NEW_REVISION=$(echo $NEW_TASK_INFO | jq -r '.taskDefinition.taskDefinitionArn')
    
    # Update ECS Service without invoking Terraform
    - aws ecs update-service --cluster $ECS_CLUSTER --service $ECS_SERVICE --task-definition $NEW_REVISION
  dependencies:
    - approve_prod_deployment
  only:
    - main

```

---

## Day-2 Infrastructure Guardrails

To give management complete confidence in running Terraform continuously, implement three non-negotiable safety rules in your platform repository:

### 1. Prevent Destruction of Stateful Assets

Enforce the `prevent_destroy` lifecycle rule on all databases, storage volumes, and stateful buckets. If a code change or accidental CLI command attempts to drop a resource, Terraform aborts execution immediately before contacting the AWS API:

```hcl
resource "aws_db_instance" "production_db" {
  identifier        = "prod-db-postgres"
  allocated_storage = 200
  engine            = "postgres"
  instance_class    = "db.m6i.xlarge"

  lifecycle {
    prevent_destroy = true # Physically blocks 'terraform destroy' or destructive replaces
  }
}

```

### 2. Isolate State Files into Micro-Stacks

Never maintain a single monolitic `.tfstate` file containing networking, databases, and application compute resources together. Split your HCL repositories into independent layers:

```text
terraform-platform/
└── environments/
    └── prod/
        ├── 01-base-iam/          # Execution Roles, KMS Keys
        ├── 02-datastores/        # RDS Postgres, ElastiCache Redis, S3
        └── 03-compute-ecs/       # ECS Cluster, ALBs, Target Groups, Services

```

An execution inside `03-compute-ecs` has no physical connection to the state file of `02-datastores`. Even in a worst-case scenario where an engineer executes an invalid plan in the compute layer, the database layer remains untouched.

### 3. Automated Drift Detection

Run a daily, read-only `terraform plan -detailed-exitcode` job inside your CI/CD pipeline. If an engineer makes a manual change in the AWS Console, the pipeline detects the drift and alerts the platform team instantly, allowing you to reconcile code and state before it causes a production incident.

---

Moving beyond Day-1 Terraform provisioning is not about giving application developers free rein over your cloud accounts, nor is it about running dangerous manual applies from developer laptops. It is about **establishing clear architectural boundaries and automation guardrails**. By isolating state files, protecting stateful resources, leveraging data sources for external boundaries, and using `ignore_changes` to decouple application releases from infrastructure state, platform teams can eliminate deployment toil, maintain strict compliance, and operate Terraform in production on Day 2 with absolute confidence.