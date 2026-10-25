+++
title = "Beyond Day-1 Terraform: Rethinking Platform Operations in My Environment"
description = "Reflections on infrastructure ownership, ECS deployments, and Terraform lifecycle management in a multi-account AWS environment."
date =  "2026-10-25"
draft = false
toc = false
categories = ["terraform", "SRE", "DevOps", "Production Engineering"]
tags = ["terraform", "SRE", "DevOps", "Production Engineering"]
image = "terraform.jpg"
author = "Fabio M. Lopes"
+++


## Introduction: The Day-2 Challenge

I've been thinking about a challenge in the infrastructure environment I work with: how to keep Terraform relevant after the initial provisioning phase, without interfering with ongoing application deployments or resources managed by other teams.

Provisioning infrastructure with Terraform is relatively straightforward when the boundaries are clear and the environment is being built from scratch. The situation becomes more complicated once applications are running, multiple teams share responsibilities, and operational changes start happening through different workflows.

In our context, we operate across multiple AWS accounts, with workloads involving AWS Outposts, ECS, and supporting infrastructure. Networking, security, platform operations, and application delivery have different ownership boundaries.

This introduces a practical question:

**How can we continue managing infrastructure through Terraform while respecting the operational autonomy of the teams responsible for other parts of the environment?**

I don't think there's a single answer that applies to every organization. What follows are some of the challenges I've encountered, the architectural decisions I'm exploring, and the trade-offs I consider relevant to our environment.

## 1. Understanding the Environment and Its Boundaries

Our environment follows a multi-account model, with separate AWS accounts for development, pre-production, and production.

Several teams participate in operating the platform:

- **Network team:** Responsible for core networking components such as VPCs, subnets, and connectivity.
- **Security team:** Responsible for centralized security policies, edge protection, and components such as the F5 WAF.
- **Platform team:** Responsible for infrastructure components supporting application workloads, including ECS, load balancers, databases, and infrastructure automation.
- **Application teams and external partners:** Responsible for developing and delivering applications, with production access mediated through internal processes.

These responsibilities introduce an important distinction: not everything an application depends on should necessarily be managed by the same Terraform configuration.

The challenge is not simply technical. It is also about respecting ownership boundaries.

### Decision 1: Reference Infrastructure Owned by Other Teams

In our case, some infrastructure components already exist and are managed independently of the application platform.

For example, the networking team may own the VPC and subnets used by our workloads. Having our Terraform configuration manage those resources directly would introduce overlapping responsibilities.

For this reason, I prefer referencing externally managed resources through Terraform data sources when the corresponding AWS provider supports them.

```hcl
data "aws_vpc" "platform_vpc" {
  filter {
    name   = "tag:Name"
    values = ["PROD-NETWORK-VPC"]
  }
}

data "aws_subnets" "application" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.platform_vpc.id]
  }

  tags = {
    Tier = "Private-App"
  }
}
```

This allows our Terraform configuration to consume existing infrastructure without assuming responsibility for its lifecycle.

Of course, using data sources doesn't eliminate dependencies. If another team changes or removes a referenced resource, our deployments may still be affected.

But in our organizational structure, this separation better reflects how responsibilities are actually distributed.

## 2. Separating Infrastructure Management from Application Delivery

Another challenge comes from how Terraform interacts with ECS application deployments.

In our environment, application teams deliver new container images through internal GitLab CI/CD pipelines. These pipelines can register new ECS task definition revisions and update running services.

Terraform, however, may still contain references to the task definitions used during initial provisioning.

This creates a potential conflict.

Consider the following scenario:

1. Terraform provisions an ECS service using an initial task definition.
2. An application pipeline deploys a new version and updates the ECS service.
3. A platform engineer later runs Terraform to modify an unrelated infrastructure component.
4. Terraform detects that the ECS service differs from its configuration and may attempt to restore the previously declared task definition.

This is not necessarily a Terraform problem. It is a consequence of having two different workflows attempting to control the same resource attribute.

### Decision 2: Define Which Workflow Owns Each Attribute

For our environment, I'm considering a clearer separation between the infrastructure lifecycle and the application release lifecycle.

Terraform remains responsible for provisioning and managing infrastructure components such as ECS clusters, capacity providers, networking configuration, load balancers, and the initial service structure.

Application delivery pipelines manage new task definition revisions and ECS service deployments.

One way to support this arrangement is to use Terraform's `ignore_changes` lifecycle argument:

```hcl
resource "aws_ecs_service" "application" {
  name            = "app-core-service"
  cluster         = aws_ecs_cluster.platform.id
  task_definition = aws_ecs_task_definition.initial.arn
  desired_count   = 2

  lifecycle {
    ignore_changes = [
      task_definition,
      desired_count
    ]
  }
}
```

In this configuration, Terraform does not attempt to reconcile changes to these attributes for an existing service during normal planning.

There is an important trade-off here.

By ignoring changes to `task_definition`, we are intentionally giving up Terraform's ability to detect and correct differences in that attribute. The deployment pipeline becomes responsible for managing it.

The same applies to `desired_count`, which should only be ignored if another mechanism, such as Application Auto Scaling or an operational workflow, is expected to manage the running task count.

**I see `ignore_changes` less as a workaround and more as an explicit ownership decision.**

It can be useful when responsibilities are well-defined, but it can also hide configuration drift if applied too broadly.

## 3. Security Groups That Reflect the Actual Traffic Flow

Security group management is another area where ownership and infrastructure design intersect.

Our application traffic follows a path that includes an institutional F5 WAF before reaching the AWS Application Load Balancer and ECS workloads.

A simplified representation is:

```
Client
  |
  v
F5 WAF
  |
  v
Application Load Balancer
  |
  v
ECS Services
  |
  +----> Database
  |
  +----> Shared Storage
```

Given this topology, my preference is to make security group rules reflect the actual communication requirements between components.

For example, where the network architecture supports it:

- The ALB accepts application traffic from the expected WAF endpoints.
- ECS tasks accept application traffic from the ALB security group.
- Database services accept connections only from the application components that require access.
- Shared storage access is limited to the appropriate workloads and protocols.

This approach helps reduce unnecessarily broad ingress permissions.

However, it also requires understanding the infrastructure outside AWS, particularly how traffic reaches the ALB through the F5 appliances.

Depending on the network architecture, preserving source addresses, NAT behavior, routing, and the availability of security group references can influence the implementation.

For this reason, I don't consider a generic security group template sufficient.

The rules need to represent the actual traffic flow of our environment, not just an idealized architecture diagram.

## 4. Reducing Manual Work in Application Deployments

One operational concern in our setup is the separation between application delivery and production infrastructure access.

External application partners should not require broad AWS production permissions just to release a new version of their applications.

At the same time, making every release dependent on a manual intervention from the infrastructure team introduces unnecessary operational work.

The challenge is finding a balance between controlled access and deployment autonomy.

### Decision 3: Use Internal CI/CD as the Deployment Boundary

An approach that makes sense for our environment is to use internal GitLab pipelines as the controlled interface for production deployments.

The intended workflow is:

```
Application Change
       |
       v
GitLab CI - Build & Test
       |
       v
Container Image Publication
       |
       v
Image Promotion / Synchronization
       |
       v
Production Approval Gate
       |
       v
Register ECS Task Revision
       |
       v
Update ECS Service
```

Under this model, application teams interact with the deployment process rather than directly managing AWS production resources.

The pipeline can use scoped IAM permissions, with short-lived credentials through OIDC where supported and configured.

An approval gate can be applied according to our production change-control requirements.

Terraform remains responsible for the infrastructure configuration, while the deployment pipeline handles application revisions.

This separation does not eliminate the need for monitoring, rollback procedures, or permission management.

But it potentially reduces repetitive operational tasks while maintaining the access boundaries required by our organization.

## 5. Making Terraform Changes More Predictable

The main reason I want to revisit our Terraform practices is not simply to automate more resources.

It is to make subsequent infrastructure changes easier to understand, review, and execute.

In a production environment, a Terraform plan that contains unexpected changes to databases, application revisions, and networking resources is difficult to approve with confidence.

A few practices appear particularly relevant to our situation.

### Separating Terraform State by Operational Responsibility

I prefer separating Terraform state according to meaningful infrastructure boundaries.

For example:

```
terraform-platform/
└── environments/
    └── prod/
        ├── 01-base-iam/
        ├── 02-datastores/
        └── 03-compute-ecs/
```

This structure is only illustrative. The appropriate boundaries depend on resource dependencies, ownership, and how changes are approved.

Separating state can reduce the scope of an individual plan and make changes easier to review.

It does not guarantee complete isolation, however. Resources managed in different states may still depend on one another through IDs, outputs, networking, or application behavior.

The goal is to reduce unnecessary coupling, not to assume that independent state files imply independent systems.

### Protecting Stateful Resources

For infrastructure such as production databases, accidental resource replacement is a concern.

Terraform's `prevent_destroy` lifecycle argument is one safeguard worth considering.

```hcl
resource "aws_db_instance" "production" {
  identifier = "prod-db-postgres"

  lifecycle {
    prevent_destroy = true
  }
}
```

This prevents Terraform from planning the destruction of that resource while the lifecycle rule remains in the configuration.

However, it is not a substitute for AWS deletion protection, backups, access controls, or change reviews.

In particular, removing the resource configuration may also remove the lifecycle protection, so it should not be treated as an absolute safeguard.

For our environment, I see it as one layer in a broader production protection strategy.

### Detecting Unexpected Changes

Another practice I'm evaluating is running automated Terraform plans to identify differences between the declared configuration and the current infrastructure.

For instance:

```bash
terraform plan -detailed-exitcode
```

The exit codes can distinguish between an unchanged configuration, a plan containing proposed changes, and an execution error.

One limitation is that not every difference represents unintended drift. Some changes may be expected, while others result from configuration updates rather than manual infrastructure modifications.

A dedicated refresh-only plan can help identify changes in remote infrastructure:

```bash
terraform plan -refresh-only -detailed-exitcode
```

In either case, the results still require interpretation.

The objective is to make unexpected changes visible before they become part of a production deployment.

## 6. The Trade-Offs I'm Willing to Make

Looking at these decisions together, the underlying theme is ownership.

In our environment, there are several competing objectives:

- Infrastructure should remain reproducible and manageable through code.
- Application teams need a practical way to release software.
- Network and security teams must retain control over their respective components.
- Production changes need to remain auditable and predictable.

These objectives do not always align automatically.

Using `ignore_changes` means accepting that some resource attributes will no longer be reconciled by Terraform.

Separating state means introducing explicit dependencies between independently managed infrastructure layers.

Using CI/CD for production deployment means investing in secure pipeline identities, approval mechanisms, and recovery procedures.

None of these choices comes without operational cost.

But for the environment I'm working with, I believe these trade-offs are worth examining because they address the actual boundaries between our teams and systems.

## Final Thoughts

My intention is not to argue that every organization should structure Terraform this way.

An environment where a single platform team owns networking, infrastructure, and application delivery may benefit from a completely different approach.

The same applies to organizations using Kubernetes, GitOps-based workflows, or other deployment mechanisms.

What I'm trying to improve in our context is the relationship between infrastructure provisioning and ongoing platform operations.

Terraform should not necessarily stop being useful once the environment is created. At the same time, keeping Terraform involved in Day-2 operations requires deciding which parts of the infrastructure it should continue to control.

For me, the most important takeaway is that **Day-2 infrastructure management is as much about defining ownership boundaries as it is about writing Terraform code.**

The next step is to validate these boundaries through actual operational changes, review the resulting Terraform plans, and adjust the approach based on what works in our environment.

That is the direction I'm pursuing: not a universal Terraform architecture, but a more deliberate and predictable way of operating the platform I work with.