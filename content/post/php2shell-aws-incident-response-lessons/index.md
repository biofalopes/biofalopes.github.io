---
title: "PHP2Shell on AWS: Incident Response and the Limits of Boot-Time Patching"
slug: php2shell-aws-incident-response-lessons
date: 2026-10-27
draft: false
description: "Lessons from a multi-application PHP2Shell response involving lightweight discovery, AWS WAF containment, Amazon ECS image rebuilds, and EC2 bootstrap reliability."
author: Fabio M. Lopes
toc: true
categories: ["AWS", "SRE", "Security"]
tags: ["AWS", "SRE", "Incident Response", "PHP", "ECS", "EC2", "Auto Scaling", "Security", "Reliability"]
---

*How a critical PHP advisory became a cross-application incident response, and why the hardest lesson was about the way new servers are built.*

{{< callout type="note" title="Scope of this account" >}}
This is a sanitized account of an operational response. Application names, customer identities, internal addresses, hostnames, and infrastructure identifiers have been omitted. The examples describe engineering patterns rather than a complete internal runbook. Observed actions are distinguished from future improvements.
{{< /callout >}}

## The advisory was only the beginning

On October 21, 2026, the PHP project announced security releases addressing **CVE-2026-109618** and **CVE-2026-109619**, two critical vulnerabilities commonly referred to as **PHP2Shell**. The vulnerabilities could enable unauthenticated remote code execution in affected deployments. The security updates included PHP **8.4.27**, **8.3.36**, **8.2.35**, and **8.5.12**. The PHP project warned that temporary mitigations were incomplete and updating was essential. See the [PHP announcement](https://www.php.net/archive/2026.php) and [NCSC-NL operational information](https://github.com/NCSC-NL/php2shell).

{{< callout type="note" title="Advisory status as of October 27, 2026" >}}
These are the fixed releases for the two original CVEs, not a guarantee against every PHP issue. On October 23, PHP also reported a conditional session-upload-progress RCE path, **CVE-2026-115560**, and recommended `session.upload_progress.enabled=0` pending a further fix. Review the [updated PHP guidance](https://www.php.net/archive/2026.php) for applicability. This account does not establish whether that setting was changed during our response.
{{< /callout >}}

Our team supported multiple applications, not one isolated PHP installation. Their deployment models differed: some ran directly on **Amazon EC2** instances in an **Auto Scaling Group (ASG)**, while others ran as containers on **Amazon Elastic Container Service (ECS)** backed by EC2 capacity. We also encountered a legacy application module running **PHP 7.4**, which could not be upgraded within the emergency response window.

That made the incident a portfolio-wide coordination problem. We had to identify likely PHP endpoints, reduce exposure, verify actual deployed runtimes, work with application owners, and choose remediation paths appropriate to each workload.

One issue turned out to be bigger than PHP2Shell itself: in an EC2-based application, **User Data installed the latest available packages at boot**, making scaling and replacement dependent on live external package repositories. During the emergency, those repository requests repeatedly timed out.

The incident highlighted two linked concerns: **how quickly we could remediate exposed workloads**, and **whether our infrastructure could reliably reproduce a patched state under pressure**.

## 1. Start wide: identify potential exposure across applications

We began with a lightweight Python utility that requested a list of application URLs and searched the responses for hints that PHP might be in use. The checks included:

- `X-Powered-By` response headers that mention PHP.
- Cookies such as `PHPSESSID`.
- `.php` in a final URL path or links and form actions in HTML.
- PHP-related error patterns in the response body.

The utility produced an initial set of investigation targets, not a definitive vulnerability inventory. A PHP application can conceal all of those indicators behind a proxy or application framework; a PHP-looking URL can also exist without an affected PHP runtime. The HTTP response cannot reliably establish a deployed runtime version or whether either CVE is exploitable.

We used the scan for **triage**, then followed it with infrastructure-level checks. A negative or inconclusive scan result could not safely clear an application. This distinction matters in a rapidly moving incident: a discovery shortcut becomes dangerous if it is mistaken for proof of safety.

The discovery scripts are not included in this article. A separate, sanitized repository would need documentation, example input, and clear restrictions to systems the operator is authorized to test. Their purpose is **technology-discovery assistance**, not exploit testing or vulnerability confirmation.

## 2. Contain exposure while remediation is prepared

As we identified potentially affected entry points, we applied temporary access restrictions at the traffic-control layer, including load-balancer-level controls. This reduced reachability while the teams investigated deployments and prepared updates.

Containment decisions required care. Blocking an endpoint can protect it from untrusted traffic but can also interrupt legitimate users. Access restrictions therefore had to be coordinated with the teams responsible for each application and treated as temporary risk reduction, not as evidence that the underlying code was safe.

### A legacy PHP 7.4 module required a different decision

During the inventory, we found **one module of an application still running PHP 7.4**. That branch had long been out of upstream support, and a compatible upgrade could not be delivered during the emergency response window.

For this exceptional release, PHP also published minimal source backports for 7.4 and other unsupported branches. Those do not restore upstream support or automatically provide deployable vendor packages. Evaluating and validating such a build is separate work; this account does not claim that we did so.

The organization's direction was to **restrict access to components that could not be patched promptly**. For this module, the selected control was an **AWS WAF web ACL rule**: requests to the specific affected URL were restricted to an **allowlist of authorized client IP addresses**.

This maintained access for the intended clients while reducing the public attack surface. It did **not** repair PHP 7.4, remove the possibility of attacks from allowed networks, or substitute for a supported runtime. Long-term work remains necessary to upgrade, replace, or retire the module.

{{< callout type="constraint" >}}
An IP allowlist only provides the intended containment when the protected path rejects non-allowed clients, rule ordering preserves that restriction, and alternate routes cannot bypass the control. An allow rule alone is insufficient if unmatched traffic is otherwise accepted. This is a validation requirement, not a claim that every possible bypass was tested during the response. See the [AWS WAF documentation](https://docs.aws.amazon.com/waf/latest/developerguide/web-acl.html).
{{< /callout >}}

The legacy finding also exposed an inventory problem: **a runtime reaching end of life should be visible before an emergency forces a decision about it**.

## 3. Verify runtimes in ECS workloads, not just on their EC2 hosts

A second part of the response concerned containerized applications running on **Amazon ECS with EC2 capacity**.

I used an additional script to assist the investigation across the EC2 infrastructure associated with the ECS clusters and their projects. The goal was to locate relevant workloads, help determine their PHP versions, and direct follow-up to the appropriate application owners.

There is an important technical distinction here: **the PHP version installed on an ECS container host is not necessarily the PHP version running in an application container**. For a containerized workload, the relevant evidence is the runtime inside the deployed container or the exact application image that the active ECS task runs. Host-level discovery alone cannot establish that.

The defensible validation path is therefore:

1. Identify the running ECS services and tasks associated with the application.
2. Record their deployed task definitions and container image references.
3. Inspect the relevant container runtime or independently verify the packages in the exact image artifact.
4. Compare the findings against the vendor's affected and fixed builds.
5. Recheck the **running tasks after deployment**, not merely the image intended for release.

An ECS task definition identifies the container configuration, including its image reference. The investigation must connect that definition to the tasks actually serving traffic; see [Amazon ECS task definitions](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definitions.html).

The description above is the verification standard I would apply. It should not be read as a claim that every one of these steps was automated by the investigation script during the incident.

### Rebuilding corrected container images

Once the affected application teams had been notified, some remediation paths were relatively straightforward. Corrected PHP base images were already available by the time those workloads were handled, so the teams could rebuild the application images and deploy the new artifacts through ECS.

```text
Security advisory
        |
        v
Portfolio triage and application ownership
        |
        v
Identify ECS workloads and check deployed PHP runtime
        |
        v
Responsible team rebuilds application image
with corrected PHP base image
        |
        v
Publish and deploy updated artifact through ECS
        |
        v
Verify new tasks and their PHP runtime
```

Rebuilding against a newly fixed base image is useful, but it is not sufficient proof by itself. A build may reuse stale layers, a mutable image tag may still point to an unexpected artifact, or an ECS service may continue running older tasks during a rollout. A stronger process uses immutable image digests where practical, records artifact provenance, confirms deployment convergence, and checks the version actually executing.

This episode reinforced the advantage of having a repeatable build-and-deploy path for application dependencies. **The image is the remediation unit**, and validation must follow that artifact into production.

## 4. A different remediation path: PHP directly on EC2

Another production application ran PHP directly on EC2 instances managed by an **Auto Scaling Group**. Its operating system packages, including PHP, were installed using an external RPM repository during instance initialization.

We first checked the PHP CLI version on the instances:

```bash
php --version
```

{{< callout type="constraint" title="CLI evidence is not web-runtime evidence" >}}
`php --version` identifies the CLI executable selected by the current shell. PHP-FPM or an Apache module can use a different installation, and existing workers can retain the old runtime until restarted or replaced. Record the installed package build and verify the web-serving processes separately. The CLI checks below are evidence of the reported version, not complete proof of the runtime handling HTTP requests.
{{< /callout >}}

The checked instances reported **PHP 8.4.26**, an upstream release affected by the advisory. Distribution and LTS vendors can backport security fixes without adopting the newest upstream version number, so package provenance and the vendor's advisory also matter. We traced this installation to the **Remi repository** and checked whether its corrected **8.4.27** packages were available:

```bash
sudo dnf clean expire-cache
sudo dnf --showduplicates list php-cli
```

These commands refreshed package metadata and displayed available PHP CLI package versions. They were **diagnostic steps**; by themselves they did not apply or verify an update.

The package names are specific to that installation. Parallel PHP installations and repository-specific package families can use different names; checking only `php-cli` does not account for every installed runtime or SAPI.

We confirmed that the corrected version was available. However, requests to the repository repeatedly timed out. We suspected that elevated demand after the public disclosure might be contributing, but **the cause of the timeouts was not established**. Network routing, mirror availability, and other causes remained possible.

After further attempts, we succeeded in updating one running instance. We then used the **Auto Scaling Group to replace instances**, checking the version on the newly started machines and repeating the replacement process until the checked instances reported:

```text
PHP 8.4.27
```

This met the immediate version-update objective **for the instances we verified**. Patching one host would not have been enough: in an ASG, any new instance must also receive the corrected runtime. Likewise, a verified package version is not proof that exploitation never occurred; compromise assessment requires relevant logs, telemetry, and a separate security investigation. We did not establish evidence of successful exploitation from the incident information available for this account.

This describes the replacement work performed, not a recommendation to terminate production instances without a rollout plan. A planned refresh should account for healthy capacity, warm-up, application readiness and rollback. See [EC2 Auto Scaling Instance Refresh](https://docs.aws.amazon.com/autoscaling/ec2/userguide/asg-instance-refresh.html).

## 5. The deeper issue: new EC2 instances depended on a live repository

The difficulty with package downloads revealed a broader infrastructure weakness.

The application's **EC2 User Data** script installed required packages at instance startup and generally requested their **latest available versions**. Essential runtime state was therefore assembled during boot rather than embedded in a previously built and tested machine image.

For Linux instances, user-data scripts normally run on the first boot unless configured otherwise; an ordinary reboot is not the same as launching a replacement instance. The dependency here was the initialization of **new ASG instances**. See [EC2 User Data](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html).

A simplified version of the dependency looked like this:

```text
Auto Scaling Group requests capacity
                 |
                 v
           Launch new EC2
                 |
                 v
           Execute User Data
                 |
                 v
       Reach external RPM repositories
                 |
          +------+------+
          |             |
       Available      Timeout/failure
          |             |
          v             v
   Install packages   Bootstrap may fail
          |           or be incomplete
          v
   Start application
          |
          v
   Pass readiness checks
```

Even when two instances launch from the same AMI and Launch Template, this model can produce different outcomes:

- A repository may publish new package builds between launches, yielding different runtimes.
- An upstream package change may introduce an untested regression or incompatible configuration.
- Repository or network failures may prevent a replacement instance from starting the application.
- Unless bootstrap errors are propagated and health checks test the application, an instance may appear healthy at the EC2 layer without being ready to serve requests.

The last point is a **possible failure mode**, not a claim that all instances in this incident passed health checks while misconfigured.

An ASG can launch replacement compute capacity. It cannot, by itself, make external repositories available or guarantee that an application's initialization script succeeded. In a bad failure sequence, repeated instance replacement can amplify the dependency rather than resolve it.

I did not originally design this bootstrap script. The purpose of documenting the finding is not to assign blame to its author: a previously workable provisioning choice had become a measurable reliability risk, and the incident exposed it under particularly unfavorable conditions.

### Why “install latest at boot” is not a patching strategy

Fetching the newest packages might sound like a way to keep servers secure. It also means that the exact software released to production is not fully known until the machine starts. Under normal scaling this reduces reproducibility; during an incident it makes rollback, troubleshooting, and capacity recovery more uncertain.

{{< callout type="decision" title="Separate patch delivery from capacity recovery" >}}
Pinning a package version helps with reproducibility but **does not solve availability** if every new instance still depends on a remote repository. Baking packages into an AMI reduces boot-time dependencies but requires an image lifecycle capable of handling security releases quickly. A sound design needs both controlled artifacts **and** a prompt, testable patching pipeline.
{{< /callout >}}

## 6. Follow-up engineering work: identified, not yet completed

The emergency work focused on containment and verified runtime remediation. The bootstrap redesign and the improvements below are **follow-up proposals**, not actions already completed during the incident.

This builds on the ownership and lifecycle questions in [Beyond Day-1 Terraform]({{< relref "/post/terraform-3" >}}): a declared infrastructure configuration is only part of what determines the software that ultimately serves traffic.

### Build and validate versioned AMIs

A stronger approach for the EC2-based application would put essential runtime packages into a tested AMI, using **EC2 Image Builder**, **Packer**, or equivalent automation.

```text
Source-controlled image configuration
                 |
                 v
Build AMI with approved PHP/packages
                 |
                 v
Security and application smoke tests
                 |
                 v
Publish immutable, versioned AMI
                 |
                 v
Update ASG Launch Template version
                 |
                 v
Controlled instance refresh / rollout
                 |
                 v
Validate running application + rollback readiness
```

This would make instance launches less dependent on third-party repositories and align the deployment lifecycle with a known runtime baseline. The trade-off is additional image-build and update automation. Without a disciplined rebuild process, an immutable image can just as easily become an immutable vulnerability.

### Make remaining bootstrap tasks failure-aware

Some configuration may still need to happen at boot. For those tasks, the desired properties are:

- Explicit failure on a missing critical dependency, rather than silently continuing.
- Bounded retries with exponential backoff and jitter for transient failures.
- Centralized bootstrap logs and actionable failure signals.
- Startup and health checks that only mark the application ready after essential steps succeed.
- A defined way to replace unhealthy instances without inducing uncontrolled replacement loops.

### Strengthen inventory and deployment evidence

Across both EC2 and ECS, the next response should not require rebuilding the runtime inventory from scratch. Useful records would connect **application owner, endpoint, deployment model, runtime version, artifact digest or AMI ID, support status, and deployment date**.

For ECS, the inventory must lead from service to running task and immutable application image. For direct EC2 deployments, it must lead from ASG and Launch Template to the actual installed runtime. Periodic checks should alert on end-of-life branches before an urgent advisory turns them into a containment problem.

### Rehearse dependency failures

A controlled test should deliberately make repositories unavailable, slow down package retrieval, cause an installation step to fail, and prevent an application service from starting. The outcome to measure is not just whether EC2 launches, but whether the system maintains or regains **healthy application capacity** and whether operators can see why recovery failed.

## 7. What the different outcomes taught us

This was not a single patch applied the same way everywhere. It was one security event with several operational responses:

| Situation | Action during the response | What remains important |
| --- | --- | --- |
| Broad application portfolio | Used HTTP-based discovery as initial triage, followed by infrastructure investigation | Avoid treating a negative heuristic scan as proof of safety |
| Potentially exposed endpoints | Restricted access through traffic controls while remediation proceeded | Account for legitimate traffic and remove temporary restrictions only when appropriate |
| ECS applications | Coordinated with owners to rebuild and redeploy images using corrected PHP bases | Verify the **deployed container runtime**, not the host PHP version or build intention |
| EC2 application in an ASG | Retrieved PHP 8.4.27 from Remi, replaced instances, and checked resulting PHP versions | Make the patched state reproducible for every future replacement |
| Legacy PHP 7.4 module | Restricted its URL through an AWS WAF IP allowlist | Migrate or retire the unsupported runtime; WAF is containment, not a patch |
| EC2 bootstrap design | Identified repository timeouts and nondeterministic boot-time package installation | Move toward versioned images, resilient bootstrap, and application-level readiness checks |

There are two practical lessons I would carry into the next incident.

**First, security response begins with trustworthy deployment visibility.** A URL, an EC2 host, an ECS service, a container image, and a PHP process are different objects. They must be connected carefully before declaring exposure or remediation complete.

**Second, recovery is only as reliable as the artifacts and dependencies needed to rebuild capacity.** Autoscaling solves part of the compute lifecycle, while image management, bootstrap behavior, repository availability, and readiness checks determine whether that new capacity is useful.

## Final thoughts

The most revealing part of this incident was not the command used to display a PHP version. It was the contrast between two delivery models under time pressure.

For ECS workloads, a corrected runtime could be packaged into a new application image and deployed through established workflows. For one traditional EC2 application, replacement capacity still depended on external package downloads at boot. That dependency repeatedly got in the way of emergency maintenance and remains a candidate for architectural improvement.

The legacy PHP 7.4 module added another dimension: sometimes an upgrade is not available within the response window, and disciplined containment is necessary while a longer-term migration is planned.

We verified the corrected PHP version on the EC2 instances reviewed, coordinated container-image remediation with application teams, and reduced exposure where immediate patching was not feasible. Those are concrete outcomes. The next engineering challenge is to make inventory, build artifacts, and infrastructure replacement more predictable, so that the next critical advisory requires less discovery and less improvisation.

---

## References

1. [PHP Project, security release announcements, October 21, 2026](https://www.php.net/archive/2026.php)
2. [NCSC-NL, PHP2Shell operational information (CVE-2026-109618 and CVE-2026-109619)](https://github.com/NCSC-NL/php2shell)
3. [PHP 8.4.27 release announcement](https://www.php.net/releases/8_4_27.php)
4. [AWS, Run commands on your Linux instance at launch (User Data)](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html)
5. [AWS, EC2 Auto Scaling Instance Refresh](https://docs.aws.amazon.com/autoscaling/ec2/userguide/asg-instance-refresh.html)
6. [AWS, AWS WAF web ACLs](https://docs.aws.amazon.com/waf/latest/developerguide/web-acl.html)
7. [AWS, Amazon ECS task definitions](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definitions.html)
