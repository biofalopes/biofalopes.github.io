+++
title = "Preparing for the AWS DevOps Engineer Professional Recertification: My Study Approach and Resources"

description = "How I'm going to prepare for the renewal of AWS DevOps Professional Certification - DOP-C02."
categories = ["aws", "devops"]
tags = ["aws", "dop-c02", "devops", "certification", "cloudformation", "sre"]
date =  "2026-11-13"
draft = false
toc = true
image = "banner.png"
author = "Fabio M. Lopes"
+++

AWS has a large portfolio, and even experienced engineers can't be expected to know every service or keep track of every new feature.

This is one of the reasons I still find certification exams worthwhile. They give me a reason to revisit technologies I haven't used in a while, explore services outside my daily work, and occasionally question how I've been doing things.

For this renewal, I have to prepare for the full [AWS Certified DevOps Engineer – Professional (DOP-C02)](https://aws.amazon.com/certification/certified-devops-engineer-professional/) exam, since I missed the opportunity to use the recent Skill Builder maintenance path that extends certification validity by one year.

## My study approach

I'm starting with the official exam guide to understand the current scope and identify where I need to spend more time.

I don't plan to go through an entire course from the beginning. I've worked with CI/CD, infrastructure as code, Linux, containers, and AWS, so reviewing concepts I already use every day wouldn't be the best use of my time.

Instead, I'll focus on the AWS-specific details that I may have forgotten or haven't had much opportunity to work with.


Knowing how to implement pipelines with GitLab CI, Azure DevOps or Jenkins doesn't automatically mean I know all the details of CodePipeline, CodeBuild, or CodeDeploy.

I need to understand how these services work together, what deployment options they support, how permissions are handled, and what happens when something fails.

I also want to pay attention to the reasoning behind AWS's recommended solutions. In a real environment, there are often several ways to solve the same problem. The exam tends to introduce constraints that make one approach more appropriate than another.

## What I'll be focusing on

### CI/CD and deployment strategies

I'll be reviewing CodePipeline, CodeBuild, CodeDeploy, and the deployment options available for EC2, ECS, and Lambda.

I'm particularly interested in the behavior of these services during deployments and failures.

For example, when does a blue/green deployment make more sense than a rolling deployment? How does traffic shifting work for different workloads? Which CloudWatch alarms can be used to trigger a rollback?

There's also the question of what happens when a deployment completes successfully, but the application starts producing errors. A successful deployment doesn't necessarily mean a healthy application.

I'll also revisit artifact management, container images, and immutable deployment approaches.

### Infrastructure as code and configuration management

I've used Terraform extensively, so I'm comfortable with the principles of infrastructure as code. CloudFormation, however, has its own behavior and operational considerations.

I plan to review CloudFormation, AWS CDK, StackSets, and Systems Manager, paying particular attention to change sets, drift detection, stack failures, and multi-account automation.

One area I want to revisit is how AWS handles infrastructure changes that fail halfway through. Understand rollback behavior and recovery options is important.

### Monitoring, reliability, and incident response

I'll focus on CloudWatch, CloudTrail, AWS Config, EventBridge, and Systems Manager Automation, along with how these services can be combined for monitoring, troubleshooting, and automated recovery. I remember the first time I took this exam in 2023 that there was a big focus on EventBridge.

I've encountered situations where infrastructure automation didn't behave as expected. In one case, EC2 instances couldn't complete their initialization because the package repositories they depended on were unavailable during bootstrap.

That experience made me reconsider how much an instance should depend on external services just to become operational.

An Auto Scaling group can replace an unhealthy instance, but if every new instance depends on the same unavailable repository, replacing it won't solve anything. The group may continue launching instances without ever reaching the desired healthy capacity.

This is closely related to several topics covered by the exam, including immutable infrastructure, deployment reliability, monitoring, and recovery automation.

I find these connections useful because they help me relate AWS services to problems I've already encountered, rather than treating each service as an isolated subject to memorize. The question is to see how the exam approaches those real life situations.

### Security and multi-account governance

I'll revisit IAM policies, roles, permissions boundaries, service control policies (SCPs), cross-account access, KMS, and security monitoring.

When troubleshooting permissions, it's important to understand which policy is being evaluated, where it applies, and how it interacts with other controls.

For example, an SCP doesn't grant permissions. It establishes limits on what permissions can be exercised by principals within its applicable scope in AWS Organizations. Those are very basic concepts that we see everywhere but are very easy to miss or confuse on the test.

## Study resources and practice exams

For now, I'm keeping my list of resources relatively short.

- **[AWS DOP-C02 Exam Guide](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02.html):** My starting point for understanding the exam domains and identifying topics that need more attention.
- **[AWS Skill Builder](https://skillbuilder.aws/):** Official preparation material, practice questions, and hands-on learning resources.
- **[AWS Certified DevOps Engineer – Professional](https://aws.amazon.com/certification/certified-devops-engineer-professional/):** The certification page, including exam details and official preparation resources.
- **[AWS Documentation](https://docs.aws.amazon.com/):** My main reference whenever I need to understand a service's behavior, limitations, or integration with other AWS services.
- **Third-party practice exams:** I'll consider these for additional scenarios, but I want to make sure the material is current and that the explanations agree with AWS documentation. The ones I had from Udemy are still being updated:

Stephane Maarek & Abhishek Singh:
https://www.udemy.com/course/aws-certified-devops-engineer-professional-practice-exam-dop/

Jon Bonso:
https://www.udemy.com/course/aws-certified-devops-engineer-professional-practice-exams-amazon-dop-c02/

Good old ExamPrepper:
https://www.examprepper.co/exam/24/1

Daily Debian:
https://dailydebian.com/blogs/practice-questions/aws-certified-devops-engineer-professional-dop-c02-practice-questions

I've always found practice questions useful, especially when I take the time to understand why an answer is correct.

Sometimes a question presents several technically valid solutions, but only one satisfies all the requirements. The difference might be operational overhead, availability, security, cost, or a limitation of a particular service.

When I answer something incorrectly, I prefer to investigate the reasoning rather than memorize the correct option.

What did I miss in the question? Was there a requirement I didn't consider? Did I misunderstand how a service works?

Going back to the documentation to answer those questions is often where I learn the most.

After a few passes through the practice exams I start to gain speed and really incorporate the new knowledge, as long as I have previously seen, used or studied it. That is why i believe that they must be the last step of the preparation.

## What I want to do differently this time

One thing I'd like to change in my preparation is spending less time taking notes about individual services and more time experimenting with how they work together.

For example, I could build a deployment pipeline that updates an application running on an EC2 Auto Scaling group behind an Application Load Balancer.

I'd configure health checks, monitoring, and rollback conditions, then deliberately introduce a few problems to see how the deployment behaves.

An instance might fail during bootstrap. The application might start but fail its health checks. Or the deployment might complete while the application begins returning more errors than usual.

I want to understand what AWS detects automatically, what needs to be configured explicitly, and where manual intervention might still be necessary.

These exercises would also give me an opportunity to work more with AWS-native automation services.

In my daily work, I naturally gravitate toward tools I'm already familiar with. That's practical when there's a problem to solve and limited time available, but it also means I don't always explore the alternatives AWS provides.

Preparing for the exam gives me a reason to do that without the pressure of an immediate production requirement. It takes time, but can also help me not forget the concepts and also to grow my portfolio.

## Final thoughts

I'm approaching this recertification differently from how I would approach a certification for a platform I'm learning for the first time.

Most of the engineering concepts covered by DOP-C02 are familiar to me. I've worked with deployment automation, infrastructure provisioning, monitoring, incident response, and security for years.

What I need to refresh is how AWS implements those concepts, particularly the details that are easy to overlook when you don't use a service regularly, since I use mostly Gitlab at my current role.

I also expect to find a few things that have changed since I last took the exam, along with services or features I haven't had a reason to explore.

Passing the exam is the immediate objective, but I want the preparation to be useful beyond the certification itself. If I finish with a better understanding of AWS's deployment and automation capabilities, and a few new approaches I can apply to my work, the time spent studying will have been worthwhile.
