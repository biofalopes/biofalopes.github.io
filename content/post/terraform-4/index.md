---
title: "Raising the Bar in Platform Operations: Moving Beyond Day-1 Terraform Provisioning"
description: "A first-person case study on overcoming Day-2 Terraform fears, decoupling IaC from application deployments on AWS Outposts, and the engineering trade-offs we accepted along the way."
date: "2026-10-25"
draft: true
toc: true
categories: ["Platform Engineering", "SRE", "Terraform", "AWS"]
tags: ["Terraform", "AWS Outposts", "ECS", "GitLab CI", "SRE", "IaC", "Trade-Offs"]
author: "Fabio M. Lopes"
---

In our cloud platform team, we recently confronted a problem that many enterprise infrastructure organizations face: **Terraform worked brilliantly for initial Day-1 provisioning, but was abandoned for Day-2 operations out of management fear**.

After deploying our foundational infrastructure on AWS Outposts, ongoing updates degraded into manual console changes, undocumented tweaks, and severe state drift. 

Rather than treating this as a generic industry debate, this post outlines **how we approached Day-2 Terraform operations in our specific environment**, the architecture we built to restore trust, and—most importantly—**the engineering trade-offs we consciously accepted** along the way.

---

## Our Operational Context & Constraints

To understand why we made our architectural choices, it is essential to look at our actual operating environment and team topology:


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
│  • External partner pushes Node/PHP code     │
│  • Automated build & ECR image sync          │
│  • Task Definition Revision & Deploy Gate    │
└──────────────────────────────────────────────┘

```

### 1. Multi-Account Isolation
We manage three isolated AWS accounts per application on AWS Outposts: **Development**, **Pre-Production**, and **Production**. External development partners build Node.js and PHP applications. They have access to Pre-Production, but **zero direct IAM access or console permissions in Production**.

### 2. Multi-Team Boundaries
Four distinct groups interact with the platform:
* **Network Team:** Owns core VPCs, Subnets, and Direct Connect routing.
* **Security Team:** Owns central IAM boundary policies and institutional **F5 WAF** edge appliances.
* **Platform Team (Our Team):** Owns ECS Clusters, Capacity Providers, Databases (RDS/ElastiCache), Shared Storage (NFS/EFS), ALBs, and IaC.
* **External Application Partner:** Develops software, pushes code to our internal self-hosted GitLab, and builds container images.

### 3. The Legacy Bottleneck
Initially, our environment was built manually in the AWS Console. When our external partner updated an application in Pre-Production, an automated mechanism synced the ECR image to Production. However, **our platform team had to be manually requested via tickets to update the ECS Task Definition revision in Production**. 

Management resisted using Terraform on Day 2 because they feared an automated `terraform apply` might overwrite live application image tags, break network dependencies, or accidentally destroy stateful assets.

---

## Decision 1: Boundary Isolation via Read-Only Data Sources

### Our Approach
To prevent our Terraform code from ever attempting to modify or delete assets owned by Network or Security teams, we decided **never to declare shared network resources as `resource` blocks**. Instead, we consume them strictly as `data` sources using explicit tags or names.

```hcl
# data_sources.tf

# Read-only VPC managed by Network Team
data "aws_vpc" "network_team_vpc" {
  filter {
    name   = "tag:Name"
    values = ["PROD-NETWORK-VPC"]
  }
}

# Read-only Subnets managed by Network Team
data "aws_subnets" "app_subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.network_team_vpc.id]
  }
  tags = {
    Tier = "Private-App"
  }
}

# Read-only F5 WAF Security Group managed by Security Team
data "aws_security_group" "f5_waf_sg" {
  filter {
    name   = "group-name"
    values = ["f5-waf-edge-allowed-sg"]
  }
}

```

### ⚖️ The Trade-Offs

* **What We Gained:** Absolute safety. Terraform cannot physically modify or destroy VPCs, subnets, or F5 WAF configurations.
* **The Trade-Off We Accepted:** **Coupling to Tag Naming Conventions**. If the Network Team renames a subnet tag or modifies a security group name without notifying us, our `terraform plan` breaks at runtime. We traded infrastructure autonomy for cross-team safety, requiring strict communication protocols whenever underlying network tags change.

---

## Decision 2: Decoupling IaC from Application Deployments

### Our Approach

The biggest cause of Day-2 state drift in ECS is container image tags. When an application partner publishes a new release (e.g., updating a container from `v1.0.0` to `v1.0.1`), an external pipeline updates the ECS Service. However, Terraform's `.tfstate` still points to `v1.0.0`. Running `terraform apply` later to adjust a load balancer would inadvertently downgrade the application.

We resolved this by using Terraform to provision the foundational ECS Cluster, ALBs, Target Groups, and initial ECS Service, while explicitly telling Terraform to **yield lifecycle control of task revisions and replica counts**:

```hcl
# ecs_service.tf

resource "aws_ecs_service" "app_service" {
  name            = "app-core-service"
  cluster         = aws_ecs_cluster.outposts_cluster.id
  task_definition = aws_ecs_task_definition.initial_template.arn
  desired_count   = 2

  network_configuration {
    subnets         = data.aws_subnets.app_subnets.ids
    security_groups = [aws_security_group.allow_app_sg.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app_tg.arn
    container_name   = "app"
    container_port   = 8080
  }

  # DAY-2 GUARDRAIL:
  # Yield control of task definition revisions and scaling to app pipelines
  lifecycle {
    ignore_changes = [
      task_definition,
      desired_count
    ]
  }
}

```

### ⚖️ The Trade-Offs

* **What We Gained:** Our platform team can modify infrastructure parameters (ALBs, Security Groups, IAM roles) on Day 2 without risking application downgrades or interfering with partner deployments.
* **The Trade-Off We Accepted:** **Incomplete State Representation**. Terraform is no longer the single source of truth for *which application container version* or *how many replicas* are running in production. We had to accept that application state auditability now lives in ECS/ECR APIs, while infrastructure state lives in Terraform.

---

## Decision 3: Automating Deployments via Internal GitLab CI with Approval Gates

### Our Approach

To eliminate the manual toil of our team updating task definition revisions on every partner release, we designed a self-service pipeline in our self-hosted **GitLab CI**.

Because external partners have no direct access to the AWS Production Account, the pipeline uses an **OIDC-assumed IAM Role with strict permissions** limited exclusively to `ecs:RegisterTaskDefinition` and `ecs:UpdateService`, protected by a manual approval gate:

```yaml
# .gitlab-ci.yml (excerpt)

stages:
  - sync-ecr
  - approve
  - deploy-prod

approve_prod_deployment:
  stage: approve
  script:
    - echo "Deployment approved for release $CI_COMMIT_SHA"
  when: manual # Requires explicit click/approval in GitLab UI by Tech Lead/SRE
  only:
    - main

deploy_production_ecs:
  stage: deploy-prod
  script:
    - echo "Registering new Task Definition revision for image $CI_COMMIT_SHA..."
    - TASK_DEF=$(aws ecs describe-task-definition --task-definition app-core-task)
    - NEW_TASK_DEF=$(echo$TASK_DEF | jq --arg IMAGE "$PROD_ECR_REPO:$CI_COMMIT_SHA" '.taskDefinition \vert{} .containerDefinitions[0].image = $IMAGE | del(.taskDefinitionArn, .revision, .status, .requiresAttributes, .compatibilities, .registeredAt, .registeredBy)')
    - NEW_TASK_INFO=$(aws ecs register-task-definition --cli-input-json "$NEW_TASK_DEF")
    - NEW_REVISION=$(echo$NEW_TASK_INFO | jq -r '.taskDefinition.taskDefinitionArn')
    
    # Update ECS Service directly without invoking Terraform
    - aws ecs update-service --cluster ecs-outposts-prod --service app-core-service --task-definition $NEW_REVISION
  dependencies:
    - approve_prod_deployment
  only:
    - main

```

### ⚖️ The Trade-Offs

* **What We Gained:** Complete elimination of manual deployment tickets. Application releases move smoothly without partner access to Production AWS credentials.
* **The Trade-Off We Accepted:** **Human-in-the-Loop Bottleneck**. By requiring a manual approval gate in GitLab CI before Production deployment, we intentionally sacrificed 100% continuous deployment (CD) velocity in favor of operational governance and risk mitigation.

---

## Decision 4: Blast Radius Reduction & Destruction Guardrails

### Our Approach

To address management's core fear—accidental resource destruction—we implemented two strict policies in our repository architecture:

1. **Stateful Resource Protection:** Enforcing `prevent_destroy` on all stateful resources (RDS databases, S3 buckets, ElastiCache clusters):
```hcl
resource "aws_db_instance" "production_db" {
  # ...
  lifecycle {
    prevent_destroy = true # Aborts execution at CLI level if a destroy is attempted
  }
}

```


2. **Micro-Stack State Isolation:** Splitting our state files into three independent layers (`01-base-iam`, `02-datastores`, `03-compute-ecs`) with separate S3 backends and DynamoDB locks.

### ⚖️ The Trade-Offs

* **What We Gained:** A syntax error or invalid plan in the compute layer (`03-compute-ecs`) can never physically touch or corrupt the database state file (`02-datastores`).
* **The Trade-Off We Accepted:** **Increased Repository & Pipeline Complexity**. Managing three state files instead of one requires managing multiple Terraform initializations, passing outputs between stacks via `data "terraform_remote_state"`, and orchestrating dependent pipelines in CI/CD.

---

## Summary of Architectural Trade-Offs

| Decision Made | Key Benefit | Trade-Off Accepted |
| --- | --- | --- |
| **Read-Only Data Sources** (VPC, WAF) | Prevents accidental modification of network/security assets. | Vulnerable to pipeline breaks if Network/Security renames tags. |
| **`ignore_changes` on ECS Tasks** | Decouples IaC updates from application releases. | Terraform state no longer tracks active application image versions. |
| **GitLab OIDC + Approval Gate** | Eliminates manual tickets without giving partner AWS access. | Introduces a manual bottleneck (approval step) in the release flow. |
| **Micro-Stack State Isolation** | Limits blast radius; isolates databases from compute runs. | Increases IaC maintenance overhead and cross-stack output management. |

---

## Conclusion

There are no universal "best practices" or absolute truths in Infrastructure-as-Code. Every architectural pattern is simply a choice that solves one set of problems while introducing new trade-offs.

In our AWS Outposts environment, choosing to decouple application lifecycles from Terraform, isolating state files into micro-stacks, and enforcing approval gates in GitLab CI allowed us to **overcome management's fear of Day-2 operations**. By being transparent about the trade-offs we accepted, we built a platform that balances operational velocity with strict enterprise governance.