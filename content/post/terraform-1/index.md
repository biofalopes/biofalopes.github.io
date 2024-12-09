+++
title = "Basic Dev Environment on AWS using Terraform"
description = "Using Terraform to deploy a basic dev environment on AWS"
date = "2022-07-30"
draft = false
toc = false
categories = ["terraform", "aws"]
tags = ["terraform", "aws"]
image = "terraform-aws-dark.jpg"
+++

It's good to have a basic terraform code that deploys a basic environment on AWS whenever you need to run some quick tests on a free tier account. 
<!--more--->  

We'll have the following resources deployed with this procedure:

- 1 VPC
- 1 Subnet
- 1 Internet Gateway
- 1 Route Table (with a default route and an association)
- 1 Security group
- 1 Key Pair
- 1 EC2 Instance

It's a very simple and you can build on top of it according to your needs, like adding a RDS instance or more EC2 instances, changing the instance type and so on. The code will be organized in the following structure:

- __main.tf__: resource declaration
- __providers.tf__: aws provider configuration
- __outputs.tf__: output declaration
- __datasources.tf__: we'll get the AMI information here
- __variables.tf__: only to inform our OS
- __terraform.tfvars__: same as previous
- __userdata.tpl__: script to be executed on first boot
- __linux-ssh-config.tpl__: SSH config for Linux
- __windows-ssh-config.tpl__: SSH config for Windows

I added a local-exec provisioner that adds the host information in the ssh configuration, and with that we can then use it with VS Code and Remote SSH extension to connect directly to it and run our code.

I'll put the code first and then explain the most important parts. Let's start with `providers.tf`:

```
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  shared_credentials_file = "/home/mando/.aws/credentials"
  profile                 = "mando"
  region                  = "us-east-1"
}
```

Terraform requires credentials to access your account on AWS. You can choose different approaches for that, like putting the keys directly instad of pointing to a credentials file. Although that works and might even be easier, you'll probably have your code pushed into a git repository which would then expose the keys. More information on how to configure the provider can be found here -> [Docs overview | hashicorp/aws](https://registry.terraform.io/providers/hashicorp/aws/latest/).

Now for the `main.tf`:
```
resource "aws_vpc" "mando_vpc" {
  cidr_block           = "10.10.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "dev"
  }

}

resource "aws_subnet" "mando_public_subnet" {
  vpc_id                  = aws_vpc.mando_vpc.id
  cidr_block              = "10.10.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "us-east-1b"

  tags = {
    Name = "dev-public"
  }
}

resource "aws_internet_gateway" "mando_internet_gw" {
  vpc_id = aws_vpc.mando_vpc.id

  tags = {
    Name = "dev-igw"
  }
}

resource "aws_route_table" "mando_public_rt" {
  vpc_id = aws_vpc.mando_vpc.id

  tags = {
    Name = "dev-public-rt"
  }
}

resource "aws_route" "mando_default_route" {
  route_table_id         = aws_route_table.mando_public_rt.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.mando_internet_gw.id

}

resource "aws_main_route_table_association" "mando_public_assoc" {
  vpc_id         = aws_vpc.mando_vpc.id
  route_table_id = aws_route_table.mando_public_rt.id
}

resource "aws_security_group" "mando_sg" {
  name        = "mando-sg"
  description = "mando Security Group"
  vpc_id      = aws_vpc.mando_vpc.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["200.199.198.197/32"] # Replace with your public IP
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "mando-sg"
  }
}

resource "aws_key_pair" "mando_key" {
  key_name   = "mando-key"
  public_key = "ssh-rsa AAAABACH3L0Lc2EAAAADAQAPNCDAgQDELie/jIMM8uno12enId2YTmTjK1OGZJtTJFoSPdXIwn79qpZYQ3WXL8PlI/8dqFyGXvQj5bGJbgEydjSYVHFXFhPr4sdKcjguWbu895EjK2DgalcYuC1+6jBbFxiodoObsc+84m81+BACH3L0LQU3cm/rNKufrh6d21jIe4sQVul+WzJ9E8aPk34rPmRPgjYvh1T/P2hdgiUyJmKqOtDYwpokDRad+3W+iwGfoBACH3L0LoCWJ2rYzz6j80FKoiHm9cnSXvErezT7aAdenVzY3nEE4ylnHWVUdmzXN7IbCSLsDV3sdn0+c5E6oDX2/k1VwtSQ8TrUblM7AdpuB4ADniUSYvLqjd/NBIiHODzV6qZxXqoltVTsrTpbCWf1A063PBACH3L0L/F3mxBihWRAKfD1iqqfMXmYvAPosOkJ3u1yuwy/eCi6Q3SmA5n0vBSVKmYdUB9yQdAimWcUqabRzXLz+g8BrUxCBHwOf4+IZAp2AseJeoDQs0aqMwybr/k= mando" # replace with your key
}

resource "aws_instance" "mando_node" {
  ami                    = data.aws_ami.server_ami.id
  instance_type          = "t2.micro"
  key_name               = aws_key_pair.mando_key.id
  vpc_security_group_ids = [aws_security_group.mando_sg.id]
  subnet_id              = aws_subnet.mando_public_subnet.id
  user_data              = file("userdata.tpl")

  root_block_device {
    volume_size = 10
  }

  provisioner "local-exec" {
    command = templatefile("${var.host_os}-ssh-config.tpl", {
      hostname     = self.public_ip,
      user         = "ubuntu",
      identityfile = "~/.ssh/id_rsa"
    })
    interpreter = var.host_os == "windows" ? ["powershell", "-Command"] : ["bash", "-c"]

  }

  tags = {
    Name = "mando-node"
  }
}
```
We'll not be using the default VPC or any other that was previously deployed, so we start by creating a VPC, a subnet and an Internet Gateway. We then have to create the route table, the default route and associate it with our VPC. 

After that, we create a security group and configure it to allow TCP access from our public IP. This of course can be adjusted according to specific needs, so I used a simple example that is not restrictive regarding what can be accessed, but very restrictive in the source IP. This prevents any access from outside, but might stop you from working with more people or from different places, and you'll have to adjust the SG whenever your public ip changes.

Then we create a key pair, and here you can use an existing one or generate a specific for this case, and you can also point to a file instead of pasting the key on the code. 

And last, but not least important, we specify an EC2 instance. The instance type is one that falls into free tier, and the __root_block_device__ block is used to change the default size to 10. This can also be changed accordingly.

`datasources.tf`:
```
data "aws_ami" "server_ami" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }
}
```
We use a data block to determine the AMI ID, since it changes between regions. We also use a filter block with a __*__ at the end of the name, so we always pick the latest version. This can be changed when you want to lock in a specific version, which would be a best practice in production environments. Since we're just testing, we might use the updated image with the latest security fixes.

`variables.tf`:
```
variable "host_os" {
  type = string
}
```

`terraform.tfvars`:
```
host_os = "linux"
```
A single variable is declared and are used just for informing which OS we use (Windows or Linux).

`outputs.tf`:
```
output "dev_ip" {
  value = aws_instance.mando_node.public_ip
}
```
The only output we have is the public IP address of the EC2 instance, which we'll need to access it.

`userdata.tpl`:
```
#!/bin/bash

sudo apt -y update &&
sudo apt -y install \
    apt-transport-https \
    software-properties-common  \
    ca-certificates \
    curl \
    gnupg \
    lsb-release &&

sudo mkdir -p /etc/apt/keyrings &&
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg &&

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null &&

sudo apt -y update &&
sudo apt -y install docker-ce docker-ce-cli containerd.io docker-compose-plugin &&
sudo groupadd docker &&
newgrp docker &&
sudo usermod -aG docker ubuntu
```
This userdata will install docker on the EC2 instance.

`windows-ssh-config.tpl`:
```
add-content -path c:/users/fabio/.ssh/config -value @'

Host ${hostname}
    HostName ${hostname}
    User ${user}
    IdentityFile ${identityfile}
'@
```

`linux-ssh-config.tpl`:
```
cat << EOF >> ~/.ssh/config

Host ${hostname}
    HostName ${hostname}
    User ${user}
    IdentityFile ${identityfile}
EOF
```
These two template files - __windows-ssh-config.tpl__ and __linux-ssh-config.tpl__ - are used by the local-exec provisioner to add the host information in our ssh configuration. This will make it easier to access it from VS Code.

After you apply this code, you can then proceed to configure Remote SSH on VS Code and use it as a remote dev node. I'll not cover here how to do this since the focus is the Terraform itself, and because it is easily done.