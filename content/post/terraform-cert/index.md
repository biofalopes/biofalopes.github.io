+++
title = "HashiCorp Certified: Terraform Associate Exam"
description = "My Study Guide for the HashiCorp Certified: Terraform Associate Exam"
date = "2022-08-07"
draft = false
toc = false
categories = ["terraform"]
tags = ["terraform"]
image = "terraform-cert.png"
+++

In order to pass the Terraform Associate Exam I followed the Official guide as a baseline for my studies, as I usually do for certification exams and it always works out well for me. 
<!--more--->  

The HashiCorp Terraform Associate is considered a __foundational level__ certification, so you can expect to have essential knowledge and skills on the concepts and not necessarily lots of hands-on practice. If you already work with Terraform you probably be able to go very quicky over the topics but it is important to know some details and also some commands that might not be very common for you. You must also know the features that exist on Terraform Enterprise packages and Terraform Cloud.

Important notes about the test: it is 57 questions long and is a proctored exam. You get 60 minutes to complete and you can mark questions for later review. the certification is valid for two years. Since Terraform is quickly and constantly evolving, it makes sense that it has a shorter validity than most certifications, which is three years.

My personal tips for this and any other certification exam: do lots of practice tests, go over every subject at least once even if you know it already from previous experience, make notes and don't just study for the test, apply the knowledge in labs or personal projects. I would say that practicing is at least 2x more efficient in making the knowledge permanent than reading or watching videos. 

Official Exam Information from Hashicorp can be found here: [HashiCorp Certified: Terraform Associate (002)](https://www.hashicorp.com/certification/terraform-associate?_gl=1*f0bstl*_ga*NjM4NzQ3OTYxLjE2NTA5MDk2Njg.*_ga_P7S46ZYEKW*MTY1OTg2ODY2NC4zMS4xLjE2NTk4Njk0NzQuMA..)

| Objective | Description |
| - | - |
| 1 | Understand Infrastructure as Code (IaC) concepts |
| 2 | Understand Terraform's purpose (vs other IaC) |
| 3 | Understand Terraform basics |
| 4 | Use the Terraform CLI (outside of core workflow) |
| 5 | Interact with Terraform modules |
| 6 | Navigate Terraform workflow |
| 7 | Implement and maintain state |
| 8 | Read, generate, and modify configuration |
| 9 | Understand Terraform Cloud and Enterprise capabilities |

What I'm gonna do here is go over each of the objectives and cover (almost) everything required to know in order to pass the exam. Most of the contents are provided on the official [study guide](https://learn.hashicorp.com/tutorials/terraform/associate-study) and the [exam review](https://learn.hashicorp.com/tutorials/terraform/associate-review?in=terraform/certification), so I'll be using it as a reference. It's probably be a long read, but I rather have it all in one place than making several posts and split the content.

### 1:	Understand Infrastructure as Code (IaC) concepts
##### 1a:	Explain what IaC is
Infrastructure as code (IaC) tools allow you to manage infrastructure with configuration files rather than through a graphical user interface. IaC allows you to build, change, and manage your infrastructure in a safe, consistent, and repeatable way by defining resource configurations that you can version, reuse, and share.
##### 1b	Describe advantages of IaC patterns
IaC makes it easy to provision and apply infrastructure configurations by standardizing the workflow. This is accomplished by using a common syntax across a number of different infrastructure providers (e.g. AWS, GCP). Some key advantages of using IaC patterns are:
- Reusability: you can write or use modules to reuse code that are common between different projects;
- Consistency: managing infrastructure manually are prone to errors;
- Idempotency: no matter how many times you run your IaC and, what your starting state is, you will end up with the same end state. This simplifies the provisioning of Infrastructure and reduces the chances of inconsistent results;
- Versioning and Source Control: by using a VCS like Git you can get visibility and security on your infrastructure.

### 2	Understand Terraform's purpose (vs other IaC)
##### 2a	Explain multi-cloud and provider-agnostic benefits
Terraform is cloud-agnostic and allows a single configuration to be used to manage multiple providers, and to even handle cross-cloud dependencies. With Terraform, users can manage a heterogeneous environment with the same workflow by creating a configuration file to fit the needs of that platform or project.
Terraform plugins called providers let Terraform interact with cloud platforms and other services via their application programming interfaces (APIs). HashiCorp and the Terraform community have written over 1,000 providers to manage resources on Amazon Web Services (AWS), Azure, Google Cloud Platform (GCP), Kubernetes, Helm, GitHub, Splunk, and DataDog, just to name a few. 
##### 2b	Explain the benefits of state
Terraform keeps track of your real infrastructure in a state file, which acts as a source of truth for your environment. Terraform uses the state file to determine the changes to make to your infrastructure so that it will match your configuration.
### 3	Understand Terraform basics
##### 3a	Handle Terraform and provider installation and versioning

Terraform can be installed using the user’s terminal: \
https://learn.hashicorp.com/tutorials/terraform/install-cli

```
## Mac OS
brew install terraform

## Windows
choco install terraform

## Linux
sudo apt install terraform
```

Alternatively, Terraform can be manually installed by downloading the binary to your computer.

##### 3b	Describe plug-in based architecture
Terraform uses a plugin-based architecture to support hundreds of infrastructure and service providers. Initializing a configuration directory downloads and installs providers used in the configuration. Terraform plugins are compiled for a specific operating system and architecture, and any plugins in the root of the user’s plugins directory must be compiled for the current system. A provider is a plugin that Terraform uses to translate the API interactions with that platform or service.

Terraform must initialize a provider before it can be used. The initialization process downloads and installs the provider's plugin so that it can later be executed. Terraform knows which provider(s) to download based on what is declared in the configuration files. For example: 

```
provider "aws" {
 region  = "us-west-2"
}
```

The provider block can contain the following meta-arguments:

*   `version` - constrains which provider versions are allowed
    *   Note: HashiCorp recommends using [provider requirements](https://www.terraform.io/docs/configuration/provider-requirements.html) instead
*   `alias` - enables using the same provider with different configurations (e.g. provisioning resources in multiple AWS regions)

By default, a plugin is downloaded into a subdirectory of the working directory so that each working directory is self-contained. As a consequence, if there are multiple configurations that use the same provider then a separate copy of its plugin will be downloaded for each configuration. To manually install a provider, move it to:

```
## MacOS / Linux
~/.terraform.d/plugins

## Windows
%APPDATA%\terraform.d\plugins
```

Given that provider plugins can be quite large, users can optionally use a local directory as a shared plugin cache. This is enabled through using the `plugin_cache_dir` setting in[ the CLI configuration file](https://www.terraform.io/docs/commands/cli-config.html).

```
plugin_cache_dir = "$HOME/.terraform.d/plugin-cache"
```

This configuration ensures each plugin binary is downloaded only once.

##### 3c	Demonstrate using multiple providers
To instantiate the same provider for multiple configurations, use the `alias` argument. For example, the AWS provider requires specifying the region argument. The following code block demonstrates how `alias` can be used to provision resources across multiple regions using the same configuration files. 

```
provider "aws" {
	region = "us-east-1"
}

provider "aws" {
	region = "us-west-1"
	alias = "pncda"
}

resource "aws_vpc" "vpc-pncda" {
	cidr_block = "10.0.0.0/16"
	provider   = "aws.pncda"
}
```

##### 3d	Describe how Terraform finds and fetches providers
Providers are released on a separate rhythm from Terraform itself, and so each provider has its own version number. For production use, consider constraining the acceptable provider versions in the configuration to ensure that new versions with breaking changes will not be automatically installed by `terraform init` in future.

Any non-certified or third-party providers must be manually installed, since `terraform init` cannot automatically download them.

The `required_version` setting can be used to constrain which versions of Terraform can be used with the configuration.

```
terraform {
  required_version = ">= 0.14.3"
}
```

The value for `required_version` is a string containing a comma-delimited list of constraints. Each constraint is an operator followed by a version number. The following operators are allowed:

<table>
  <tr>
   <td><strong>Operator</strong>
   </td>
   <td><strong>Usage</strong>
   </td>
   <td><strong>Example</strong>
   </td>
  </tr>
  <tr>
   <td><code>=</code> (or no operator)
   </td>
   <td>Use exact version
   </td>
   <td><code>"= 0.14.3"</code>
<p>
Must use v0.14.3 
   </td>
  </tr>
  <tr>
   <td><code>!=</code>
   </td>
   <td>Version not equal
   </td>
   <td><code>"!=0.14.3"</code>
<p>
Must not use v0.14.3 
   </td>
  </tr>
  <tr>
   <td><code>></code> or <code>>=</code> or <code>&lt;</code> or <code>&lt;=</code>
   </td>
   <td>Version comparison
   </td>
   <td><code>">= 0.14.3"</code>
<p>
Must use a version greater than or equal to v0.14.3
   </td>
  </tr>
  <tr>
   <td><code>~></code>
   </td>
   <td>Pessimistic constraint operator that both both the oldest and newest version allowed
   </td>
   <td><code>"~>= 0.14"</code>
<p>
Must use a version greater than or equal to v0.14 but less than v0.15 (which includes v0.14.3)
   </td>
  </tr>
</table>

Similarly, a provider version requirement can be specified. The following is an example limited the version of AWS provider:

```
provider "aws" {
	region = "us-west-2"
	version = ">=3.1.0"
}
```

It is recommended to use these operators in production to ensure the correct version is being used and avoid accidental upgrades that might have breaking changes. 

##### 3e	Explain when to use and not use provisioners and when to use local-exec or remote-exec
Provisioners can be used to model specific actions on the local machine or on a remote machine. For example, a provisioner can enable uploading files, running shell scripts, or installing or triggering other software (e.g. configuration management) to conduct initial setup on an instance. Provisioners are defined within a resource block:

```
resource "aws_instance" "example" {
 ami           = "ami-b374d5a5"
 instance_type = "t2.micro"

 provisioner "local-exec" {
   command = "echo hello > hello.txt"
 }
}
```

Multiple provisioner blocks can be used to define multiple provisioning steps.

```
Note: HashiCorp recommends that provisioners should only be used as a last resort. 
```

###### Types of Provisioners

This section will cover the various types of generic provisioners. There are also vendor specific provisioners for configuration management tools (e.g. Salt, Puppet). 

###### 1. File

The file provisioner is used to copy files or directories from the machine executing Terraform to the newly created resource. 

```
resource "aws_instance" "web" {
  # ...

  provisioner "file" {
    source      = "conf/myapp.conf"
    destination = "/etc/myapp.conf"
  }
}
```

The file provisioner supports both ssh and winrm type connections.

###### 2. `local-exec` 

The `local-exec` provisioner runs by invoking a process local to the user’s machine running Terraform. This is used to do something on the machine running Terraform, not the resource provisioned. For example, a user may want to create an SSH key on the local machine. 


```
resource "null_resource" "generate-sshkey" {
    provisioner "local-exec" {
        command = "yes y | ssh-keygen -b 4096 -t rsa -C 'terraform-kubernetes' -N '' -f ${var.kubernetes_controller.["private_key"]}"
    }
}
```

###### 3. `remote-exec`

Comparatively, `remote-exec` which invokes a script or process on a remote resource after it is created. For example, this may be used to bootstrap a newly provisioned cluster or to run a script. 

```
resource "aws_instance" "example" {
 key_name      = aws_key_pair.example.key_name
 ami           = "ami-04590e7389a6e577c"
 instance_type = "t2.micro"

connection {
   type        = "ssh"
   user        = "ec2-user"
   private_key = file("~/.ssh/terraform")
   host        = self.public_ip
 }

provisioner "remote-exec" {
   inline = [
     "sudo amazon-linux-extras enable nginx1.12",
     "sudo yum -y install nginx",
     "sudo systemctl start nginx"
   ]
 }
}
```

Both SSH and winrm connections are supported.

By default, provisioners are executed when the defined resource is created and during updates or other parts of the lifecycle. It is intended to be used for bootstrapping a system. If a provisioner fails at creation time, the resource is marked as tainted. Terraform will plan to destroy and recreate the tainted resource at the next `terraform apply` command. 

By default, when a provisioner fails, it will also cause the `terraform apply` command to fail. The `on_failure` parameter can be used to specify different behavior. 

```
resource "aws_instance" "web" {
 # ...

 provisioner "local-exec" {
   command  = "echo The server's IP address is ${self.private_ip}"
   on_failure = "continue"
 }
}

```
Note: Expressions in provisioner blocks cannot refer to the parent resource by name. Use the self object to represent the provisioner's parent resource (see previous example). 

Additionally, provisioners can also be configured to run when the defined resource is destroyed. This is configured by specifying when = “destroy” within the provisioner block. 

```
resource "aws_instance" "web" {
  # ...

  provisioner "local-exec" {
    when    = "destroy"
    command = "echo 'Destroy-time provisioner'"
  }
}
```

By default, a provisioner only runs at creation. To run a provisioned at deletion, it must be explicitly defined. 

### 4	Use the Terraform CLI (outside of core workflow)
##### 4a	Given a scenario: choose when to use `terraform fmt` to format code
##### 4b	Given a scenario: choose when to use `terraform taint` to taint Terraform resources	
##### 4c	Given a scenario: choose when to use `terraform import` to import existing infrastructure into your Terraform state
##### 4d	Given a scenario: choose when to use `terraform workspace` to create workspaces
##### 4e	Given a scenario: choose when to use `terraform state` to view Terraform state
##### 4f	Given a scenario: choose when to enable verbose logging and what the outcome/value is
### 5	Interact with Terraform modules
##### 5a	Contrast module source options
##### 5b	Interact with module inputs and outputs
##### 5c	Describe variable scope within modules/child modules
##### 5d	Discover modules from the public Terraform Module Registry
##### 5e	Defining module version
### 6	Navigate Terraform workflow
##### 6a	Describe Terraform workflow ( Write -> Plan -> Create )
##### 6b	Initialize a Terraform working directory (`terraform init`)
##### 6c	Validate a Terraform configuration (`terraform validate`)
##### 6d	Generate and review an execution plan for Terraform (`terraform plan`)
##### 6e	Execute changes to infrastructure with Terraform (`terraform apply`)
##### 6f	Destroy Terraform managed infrastructure (`terraform destroy`)
### 7	Implement and maintain state
##### 7a	Describe default local backend
##### 7b	Outline state locking
##### 7c	Handle backend authentication methods
##### 7d	Describe remote state storage mechanisms and supported standard backends
##### 7e	Describe effect of Terraform refresh on state
##### 7f	Describe backend block in configuration and best practices for partial configurations
##### 7g	Understand secret management in state files
### 8	Read, generate, and modify configuration
##### 8a	Demonstrate use of variables and outputs
##### 8b	Describe secure secret injection best practice
##### 8c	Understand the use of collection and structural types
##### 8d	Create and differentiate resource and data configuration
##### 8e	Use resource addressing and resource parameters to connect resources together
##### 8f	Use Terraform built-in functions to write configuration
##### 8g	Configure resource using a dynamic block
##### 8h	Describe built-in dependency management (order of execution based)
### 9	Understand Terraform Cloud and Enterprise capabilities
##### 9a	Describe the benefits of Sentinel, registry, and workspaces
##### 9b	Differentiate OSS and Terraform Cloud workspaces
##### 9c	Summarize features of Terraform Cloud