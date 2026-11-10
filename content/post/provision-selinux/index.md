+++
title = "Making EC2 Provisioning More Predictable Without Disabling SELinux"
description = "Revisiting an AlmaLinux provisioning script exposed practical lessons about golden images, package management, boot-time dependencies, and SELinux contexts across application deployments."
date = "2026-11-09"
draft = false
toc = false
tags = ["aws", "ec2", "almalinux", "selinux", "provisioning", "cloud-init", "automation"]
categories = ["aws", "linux", "sre"]
image = "banner.png"
author = "Fabio M. Lopes"
+++

# Rethinking EC2 Provisioning: Package Versions, Golden Images, and SELinux

I recently spent some time revisiting how we provision EC2 instances for a Laravel application running on AlmaLinux 9, Nginx, and PHP-FPM.

The initial goal was fairly straightforward: simplify an existing provisioning script by moving stable system configurations into a preconfigured machine image, while retaining some flexibility to manage runtime versions when new instances start.

As I worked through the scripts, though, I found a few things that deserved more attention than I had expected. Package versioning turned out to be more complicated than setting a few variables. Composer behaved differently when running without a conventional user environment. And enabling SELinux in Enforcing mode revealed a file-labeling issue that could affect every new application deployment.

Each problem was manageable on its own, but together they raised a broader question: how much work should an EC2 instance really be doing when it starts?

## What Belongs in the Image, and What Belongs at Boot?

The original provisioning script handled almost everything from scratch. It configured repositories, installed packages, created users and directories, set up PHP-FPM and Nginx, installed systemd services, and applied firewall and SELinux settings.

There's a certain convenience to this approach, especially when you're building an environment for the first time. Everything is in one place, and you can follow the entire setup process from beginning to end.

But I suggested to the team that we reconsider how much of that work needed to happen every time Auto Scaling launched a new instance.

Most of those configurations were already known and rarely changed. Repeating them at every startup added unnecessary work and introduced dependencies that could prevent an otherwise healthy instance from coming online.

My proposal was to move the stable parts into the machine image:

- Nginx and PHP-FPM configuration.
- Application directories and ownership.
- Systemd units for the Laravel scheduler and Horizon.
- Deployment-user permissions.
- Persistent SELinux configuration.
- Common operating-system settings.

The initialization script would then focus on runtime checks, selected configuration adjustments, and starting the application services.

During the transition, I kept the original provisioning commands commented out. That made it easier to review the changes with the team and explain which responsibilities had moved into the image. Once the new process is fully validated, those obsolete blocks can be removed.

### The image and the initialization script need to agree

One thing became clear while making these changes: moving a command out of the provisioning script doesn't make its responsibility disappear.

If the script no longer creates a directory, that directory must already exist in the image. The same applies to systemd units, permissions, and SELinux policies.

This means the machine image and its initialization script effectively become two parts of the same deployment contract.

They need to be versioned and tested together, even if they're maintained separately. Otherwise, a perfectly valid change to one could break the other.

## Package Versioning Wasn't as Straightforward as I Expected

Another improvement I wanted to make was controlling package versions more explicitly.

The original script relied on unversioned `dnf install` commands. In an Auto Scaling environment, that creates an interesting risk: an instance launched today might install different package versions from those running since last week.

For a fleet that's supposed to behave consistently, that's not ideal.

I introduced version variables for PHP, Nginx, Redis, ZIP, and Composer. PHP, for example, was targeted at version 8.4.27 from the Remi repository.

I also added a helper to compare the installed RPM version against the requested version and synchronize it when necessary.

The initial idea looked something like this:

```bash
installed="$(rpm -q --qf '%{VERSION}-%{RELEASE}' "$name")"

if [[ "$installed" != "$version" ]]; then
    dnf -y distro-sync "${name}-${version}"
fi
```

The intention was to avoid unnecessary package operations when the correct version was already installed.

It made sense at first, but reviewing the implementation exposed a problem with my assumptions.

Not every package associated with PHP follows PHP's version numbering.

For example, `php-pear` has its own independent version. In this environment, `php-zip` was a virtual package provided by `php-pecl-zip`. Treating both as ordinary PHP RPMs with the same version string would lead to incorrect package resolution.

I also realized that synchronizing individual PHP packages wasn't necessarily the safest approach. Extensions and runtime packages have dependencies on one another, and changing them separately can cause conflicts during a version transition.

A single DNF transaction that resolves the related packages together is generally a better approach.

### Version pinning is only part of the solution

There's another limitation worth mentioning.

Even if we specify the exact package versions correctly, those packages still need to be available in the repository when a new instance starts.

If an older version gets removed, the installation may fail. The same problem can affect a rollback if the required packages are no longer published.

This creates a trade-off.

Keeping runtime version management in the initialization script gives us flexibility. We can change a PHP version without necessarily rebuilding the entire image.

But it also means that launching a new instance still depends on external repositories being available and serving the expected packages.

For production workloads, particularly those managed by Auto Scaling, that's a dependency I'd rather minimize.

A controlled package repository could help. So could building and publishing new machine images whenever runtime versions change.

Neither approach is completely free of maintenance, but both provide more control over what actually gets deployed.

## Enabling SELinux Revealed Another Problem

The other major part of this work involved running the application with SELinux in Enforcing mode.

The Laravel application uses a release-based deployment structure:

```text
/var/www/application/
├── current -> releases/<release-id>
├── releases/
│   └── <release-id>/
│       └── public/index.php
└── storage/
```

Each deployment prepares a new release directory and, once everything is ready, updates the `current` symbolic link.

The application needs to read its code and write to specific locations, mainly `storage`.

From a traditional Linux permissions perspective, that's relatively easy to manage through ownership and permission bits.

SELinux adds another layer: every file also has a security context that determines how processes can interact with it.

### The issue was with file labels

During deployment, application files were prepared or extracted under `/tmp` before being moved into the release directory.

Some of those files retained the SELinux type from their original location: `tmp_t`.

That matters because moving a file doesn't necessarily update its SELinux context to match the destination directory.

So even when the ownership and Unix permissions look correct, Nginx or PHP-FPM may still be unable to access the file.

The solution was to correct the labels rather than disable SELinux or switch it to Permissive mode.

For this application, the relevant contexts were:

| Content | SELinux type | Purpose |
|---|---|---|
| Application code | `httpd_sys_content_t` | Read access |
| Writable storage | `httpd_sys_rw_content_t` | Authorized writes |
| Release symlink | Depends on path policy | Points to the active release |

During validation, the symbolic link appeared with `var_t`. That's an observation from this environment, not a general rule for how application files should be labeled.

What matters is having the appropriate persistent file-context rules and ensuring that deployed files actually receive those labels.

## The Fix Needed to Be Part of Deployment

Initially, it might seem sufficient to configure SELinux correctly when building the machine image.

But that only handles files that exist at image creation time.

Every application deployment introduces new files, and those files can arrive with contexts inherited from wherever they were prepared.

That's why the deployment process also needs to handle SELinux labeling.

After preparing a release, but before activating it, the script restores the expected contexts:

```bash
sudo -n /usr/sbin/restorecon -RF "$RELEASES_DIR"
sudo -n /usr/sbin/restorecon -RF "$ROOT_DIR/storage"
```

`restorecon` uses the configured SELinux file-context rules to apply the expected labels.

Because the deployment user doesn't have unrestricted privileges, this also required reviewing how the commands would run through `sudo`.

The intended approach was to allow only the necessary operations on the relevant application paths, rather than grant broad privileged access.

Using `sudo -n` was deliberate. If the command requires an interactive password, it fails instead of leaving the deployment waiting indefinitely.

More importantly, if context restoration fails, the deployment shouldn't activate the new release.

I'd rather have a deployment fail clearly than report success and leave the application unable to serve requests.

### Why not make the entire application directory writable?

One possible shortcut would be to assign `httpd_sys_rw_content_t` to the entire Laravel directory.

That would probably make several permission problems disappear, but it would also give the web application write access to locations where it doesn't need it.

Application code should remain read-only from the web process's perspective. Write permissions should be limited to directories that genuinely require them.

It's a relatively small distinction in configuration, but an important one for maintaining a sensible security boundary.

## Validating the Changes

After adjusting the deployment process, we checked the application in an AlmaLinux 9.8 environment with SELinux running in Enforcing mode.

Some of the commands used during validation were:

```bash
getenforce

matchpathcon -V /var/www/application/current/public/index.php

restorecon -nRFv /var/www/application/releases

ausearch -m AVC,USER_AVC -ts recent -i
```

The paths here have been anonymized. We also checked the release symlink and writable storage.

The results were encouraging:

- SELinux was running in `Enforcing` mode.
- The application health endpoint returned HTTP 200 with a successful JSON status.
- PHP-FPM and Laravel Horizon were active.
- The filesystem contexts we checked showed no mismatches.
- A dry run of `restorecon` reported no additional label changes.
- The recent AVC audit query returned no matches.

That gave us confidence that the tested release was working correctly under SELinux Enforcing.

Of course, these checks don't cover every possible application behavior. Background jobs, external integrations, less frequently used features, and future releases still need appropriate testing.

But they provided a useful baseline and confirmed that we didn't need to weaken SELinux to get the application running.

## What I'd Still Like to Improve

Although the changes made the provisioning process more manageable, I wouldn't consider the work finished yet.

Package management is the first area I'd revisit. The version-handling logic needs to account for RPMs with independent version numbers and resolve related PHP packages as a compatible set. I'd also want to verify the installed extensions after any runtime change.

The second area is dependency availability.

Moving stable configuration into a golden image reduces the amount of work required at startup, but the revised script still depends on external repositories for some packages.

That means a repository outage, missing package version, or temporary connectivity issue could still affect instance initialization.

I'd prefer to move more runtime preparation into tested, versioned images. It would mean rebuilding images more frequently, but it would also make instance startup more predictable.

Finally, I want to improve how we validate the complete provisioning lifecycle.

A representative test should launch an instance from the intended image, run the initialization script, verify package versions and services, deploy an application release, and check that everything works with SELinux Enforcing.

I'd also include a controlled runtime version change to see how the package-management logic behaves when the installed packages don't match the requested configuration.

And every deployment should continue restoring SELinux contexts before activating a release, stopping immediately if that operation fails.

## Final Thoughts

What started as an effort to simplify a provisioning script turned into a useful review of how we build, initialize, and deploy our application servers.

The most important lesson for me was how closely these responsibilities are connected.

A golden image can remove a lot of unnecessary startup work, but only if we clearly define what the image guarantees. Version pinning can improve consistency, but only if we can reliably retrieve the packages we've pinned. And enabling SELinux is only sustainable when the deployment process handles file contexts correctly.

For an application running behind an Auto Scaling Group, these details matter. New instances need to behave consistently whether they're launched during a planned deployment, a scale-out event, or recovery from a failure.

That's ultimately what I'm working toward: fewer surprises when an instance starts, fewer external dependencies during recovery, and a provisioning process we can test and trust.