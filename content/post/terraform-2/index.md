+++
slug = "managing-aws-autoscaling-groups-and-load-balancers-using-terraform"
lastmod = "2026-10-26"
title = "Managing AWS Autoscaling Groups and Load Balancers using Terraform"
description = "Using Terraform to manage AWS Autoscaling Groups and Load Balancers"
date = "2022-08-01"
draft = false
toc = true
categories = ["terraform", "aws"]
tags = ["terraform", "aws"]
image = "aws-diagram.jpg"
+++

This lab builds on my first AWS/Terraform example: two subnets, an Application Load Balancer (ALB), and an Auto Scaling Group (ASG) that launches web servers in two Availability Zones.

**October 2026 revision:** the original subnets were outside the declared VPC CIDR. This version derives them from the VPC, uses a Launch Template instead of a Launch Configuration, and restricts instance HTTP ingress to the ALB security group. AWS recommends [migrating to Launch Templates](https://docs.aws.amazon.com/autoscaling/ec2/userguide/launch-configurations.html); new accounts cannot create launch configurations.

## Scope and prerequisites

This is an HTTP laboratory serving a static, non-sensitive page. It creates billable EC2, ALB and public IPv4 resources. The instances use public subnets for outbound package installation without a NAT gateway, but accept HTTP only from the ALB. There is no SSH ingress or embedded key pair.

For production, design private application subnets, outbound connectivity, HTTPS with an ACM certificate, logging, access management and an application-specific scaling signal. Two Availability Zones provide placement options; actual availability still depends on healthy capacity, application behavior and dependencies.

Use Terraform 1.9 or newer and the AWS provider 6.70.0. Supply an **Amazon Linux 2023 x86_64 AMI ID for your selected region**. The region must expose at least two usable Availability Zones. Do not substitute an Ubuntu AMI: the bootstrap uses `dnf` and `httpd`.

Authenticate using the AWS provider's normal credential chain, such as an AWS SSO profile. Keep credentials outside the configuration:

```bash
aws sso login --profile sandbox
export AWS_PROFILE=sandbox
```

The environment-variable syntax above is for Bash. In PowerShell, use `$env:AWS_PROFILE = "sandbox"`.

## Complete configuration

Download [main.tf](main.tf) into an empty lab directory. `terraform init` installs the pinned provider and writes `.terraform.lock.hcl`; commit that lockfile in your lab repository to retain provider checksums.

{{< code-file file="main.tf" lang="hcl" >}}

## How the pieces fit

The VPC is `10.10.0.0/16`. `cidrsubnet` derives `10.10.1.0/24` and `10.10.2.0/24`, keeping both subnets inside it. A default route through the internet gateway supplies the lab's outbound connectivity.

The ALB accepts HTTP and forwards to its target group. The ASG registers its instances with that target group; the instance security group accepts port 80 only from the ALB security group. User data installs Apache and writes the hostname into the page. IMDSv2 is required, although this bootstrap does not need to query instance metadata.

The ASG starts with two instances and a range of two to four. Target tracking adjusts capacity toward 50% average CPU utilization and manages its own alarms. `ignore_changes = [desired_capacity]` assigns running capacity to autoscaling after initial creation; Terraform still manages the minimum and maximum bounds.

The ASG references a **numeric Launch Template version**, so changing the template is visible to Terraform and can trigger an instance refresh. Refresh preferences retain healthy capacity while replacements start. This requires spare capacity and sufficient quotas; it is not a guarantee of uninterrupted application service. Check refresh status and application traffic during any rollout.

## Validate, plan and verify

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan -var="ami_id=ami-REPLACE_WITH_YOUR_AL2023_AMI" -out=lab.tfplan
```

Replace the illustrative AMI ID before planning. Review account, region, subnet placement, instance counts and costs in the saved plan. To provision this lab after that review:

```bash
terraform apply lab.tfplan
terraform output -raw lab_url
```

Check target-group health, fetch the page through the ALB, and observe ASG activity and CloudWatch metrics before assessing scaling. A format/schema check cannot prove that an AMI boots or that your account has sufficient quota. The configuration passed `terraform validate` with Terraform 1.9.8 and AWS provider 6.70.0. It was not deployed into an AWS account.

Clean up when finished:

```bash
terraform plan -destroy -var="ami_id=ami-REPLACE_WITH_YOUR_AL2023_AMI" -out=destroy.tfplan
terraform apply destroy.tfplan
```

Keep state and plan files private: they may contain sensitive infrastructure information. Review the destroy plan just as carefully as the creation plan.

## References

- [AWS Launch Templates](https://docs.aws.amazon.com/autoscaling/ec2/userguide/launch-templates.html)
- [Terraform AWS Launch Template resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/launch_template)
- [Terraform AWS Auto Scaling Group resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/autoscaling_group)
