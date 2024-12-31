+++  
title = "Connecting Clouds: Building a Multi-Cloud Infrastructure with AWS and Azure"  
description = "Exploring how to set up secure, scalable, and high-performance multi-cloud networking between AWS and Azure in a sample test environment."  
date = "2024-09-13"  
draft = true  
toc = false  
categories = ["aws", "azure", "kubernetes", "terraform"]  
tags = ["aws", "azure", "kubernetes", "terraform"]  
image = "DALL-E.webp" 
+++  

Multi-cloud setups often come with high stakes and complex challenges, but in this case, the focus was purely on learning. I built a sample environment to dive into AWS and Azure solutions, test their capabilities, and explore how to approach real-world scenarios in a safe, controlled space.

The goal was to test how Kubernetes clusters in AWS and Azure could communicate seamlessly, securely, and efficiently.

### 1. **Requirements**

To replicate this setup, you’ll need:  
a. **AWS Account**: Permissions to create VPCs, VPN Gateways, and associated resources.  
b. **Azure Account**: Permissions to create VNets, Virtual Network Gateways, and route tables.  
c. **Terraform Installed**: Infrastructure as Code for managing cloud resources.  
d. **Basic Kubernetes Setup**: Clusters on AWS (EKS) and Azure (AKS) for testing connectivity.  
e. **Tools for Testing**: Access to `kubectl`, `iperf`, and monitoring dashboards like CloudWatch and Azure Monitor.  

### 2. **Terraform Project Structure**

Here’s how I structured my Terraform project to manage the resources:

```css
terraform/
├── modules/
│   ├── aws/
│   │   ├── vpc/
│   │   │   ├── main.tf
│   │   │   ├── outputs.tf
│   │   │   ├── variables.tf
│   │   ├── vpn/
│   │   │   ├── main.tf
│   │   │   ├── outputs.tf
│   │   │   ├── variables.tf
│   │   ├── customer_gateway/
│   │       ├── main.tf
│   │       ├── outputs.tf
│   │       ├── variables.tf
│   ├── azure/
│   │   ├── vnet/
│   │   │   ├── main.tf
│   │   │   ├── outputs.tf
│   │   │   ├── variables.tf
│   │   ├── vpn_gateway/
│   │       ├── main.tf
│   │       ├── outputs.tf
│   │       ├── variables.tf
├── envs/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── terraform.tfvars
│   ├── prod/
│       ├── main.tf
│       ├── terraform.tfvars
├── providers.tf
├── backend.tf
├── variables.tf
├── outputs.tf
```


#### 2.1 **Explanation of the Structure**:

- `modules/` folder: Contains reusable Terraform modules for AWS and Azure.
Each module focuses on a specific resource group, such as VPCs, VPNs, and gateways.
- `envs/` folder: Contains environment-specific configurations. For example, `dev/` and `prod/` hold the `main.tf` and `terraform.tfvars` files, which reference the modules and define environment-specific variables (e.g., CIDR ranges, resource names).

#### 2.2 **Root Files:**

- `providers.tf`: defines the AWS and Azure providers.
- `backend.tf`: configures the remote backend for Terraform state.
- `variables.tf`: global variables shared across all environments.
- `outputs.tf`: centralizes outputs to provide high-level information after applying changes.


#### 2.3 **Core Files and Configurations**

Here’s a closer look at some of the key Terraform files:

a. **`providers.tf`:**
   ```hcl
   terraform {
     required_providers {
       aws = {
         source  = "hashicorp/aws"
         version = "~> 4.0"
       }
       azurerm = {
         source  = "hashicorp/azurerm"
         version = "~> 3.0"
       }
     }
   }

   provider "aws" {
     region = var.aws_region
   }

   provider "azurerm" {
     features {}
   }
   ```

b. **`backend.tf`:**
   ```hcl
   terraform {
     backend "s3" {
       bucket         = "terraform-state-m34ok2m2"
       key            = "multi-cloud/infrastructure.tfstate"
       region         = "us-east-1"
       encrypt        = true
       dynamodb_table = "terraform-locks"
     }
   }
   ```

c. **Module for vpc (`modules/aws/vpc/main.tf`):**
   ```hcl
   resource "aws_vpc" "main" {
     cidr_block = var.cidr_block
     enable_dns_support = true
     enable_dns_hostnames = true
     tags = {
       Name = var.vpc_name
     }
   }

   output "vpc_id" {
     value = aws_vpc.main.id
   }
   ```

d. **Environment-Specific Configuration (`envs/dev/main.tf`):**
   ```hcl
   module "aws_vpc" {
     source = "../../modules/aws/vpc"
     cidr_block = var.aws_cidr_block
     vpc_name   = "dev-vpc"
   }

   module "azure_vnet" {
     source = "../../modules/azure/vnet"
     vnet_name       = "dev-vnet"
     address_space   = var.azure_address_space
     location        = var.azure_location
     resource_group_name = var.azure_resource_group_name
   }
   ```

e. **Variable Definition (`variables.tf`):**
   ```hcl
   variable "aws_region" {
     description = "AWS region"
     default     = "us-west-2"
   }

   variable "azure_location" {
     description = "Azure region"
     default     = "East US"
   }
   ```

#### 2.4 **Initializing the Terraform Project**
```bash
terraform init
```

**Expected Output:**
```plaintext
Initializing modules...
Initializing the backend...
Initializing provider plugins...
Terraform has been successfully initialized!
```

#### 2.5 **Validating the Configuration**
```bash
terraform validate
```

**Expected Output:**
```plaintext
Success! The configuration is valid.
```

#### 2.6 **Applying the Configuration**
```bash
terraform apply -var-file=envs/dev/terraform.tfvars
```

### **3. Networking Design**

For this test setup, I aimed to simulate requirements similar to those found in production systems:  
- **Encrypted Communication**: Simulating secure data transit between clouds.  
- **Reliable Connectivity**: Avoiding single points of failure using redundancy.  
- **Minimal Latency**: Optimizing performance for Kubernetes workloads.  

The tools I worked with:  
- AWS Virtual Private Gateway (VPG) and Azure Virtual Network Gateway (VNet Gateway) for cross-cloud communication;
- IPsec VPN tunnels to encrypt traffic;
- Custom route tables for connectivity.

### **4. AWS Configuration**

AWS was my starting point. Here’s how I set up the Virtual Private Gateway and established the connection to Azure.  

**Step 1: Create a Virtual Private Gateway (VPG):**  
```hcl
resource "aws_vpn_gateway" "main" {
  vpc_id = aws_vpc.main.id
}
```

**Step 2: Attach the VPG to the VPC:**  
```hcl
resource "aws_vpn_gateway_attachment" "main" {
  vpc_id        = aws_vpc.main.id
  vpn_gateway_id = aws_vpn_gateway.main.id
}
```

**Step 3: Define a Customer Gateway for Azure:**  
This represents Azure’s Virtual Network Gateway in AWS.  
```hcl
resource "aws_customer_gateway" "azure" {
  bgp_asn    = 65000
  ip_address = "Azure-Gateway-Public-IP"
  type       = "ipsec.1"
}
```

**Step 4: Establish the VPN Connection:**  
```hcl
resource "aws_vpn_connection" "main" {
  vpn_gateway_id      = aws_vpn_gateway.main.id
  customer_gateway_id = aws_customer_gateway.azure.id
  type                = "ipsec.1"
  static_routes_only = true
}
```

**Step 5: Confirm the AWS Configuration:**  
```bash
aws ec2 describe-vpn-gateways --filters "Name=attachment.state,Values=attached"
aws ec2 describe-vpn-connections --filters "Name=state,Values=available"
```

**Expected Output:**  
```json
{
  "VpnGateways": [
    {
      "State": "attached",
      "VpcId": "vpc-xxxxxxx",
      ...
    }
  ]
}
{
  "VpnConnections": [
    {
      "State": "available",
      "VpnGatewayId": "vgw-xxxxxxx",
      ...
    }
  ]
}
```

### **5. Azure Configuration**

On Azure, the setup is the equivalent to AWS to create the other side of the VPN. Obviously, the names are different but the components are very similar.

**Step 1: Create the Virtual Network Gateway:**  
```hcl
resource "azurerm_virtual_network_gateway" "main" {
  name                = "aws-azure-vnet-gateway"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  type     = "Vpn"
  vpn_type = "RouteBased"

  ip_configuration {
    name                          = "vnetGatewayConfig"
    public_ip_address_id          = azurerm_public_ip.main.id
    private_ip_allocation_method  = "Dynamic"
    subnet_id                     = azurerm_subnet.gateway_subnet.id
  }
}
```

**Step 2: Configure the Connection to AWS:**  
```hcl
resource "azurerm_virtual_network_gateway_connection" "aws" {
  name                           = "aws-connection"
  location                       = azurerm_resource_group.main.location
  resource_group_name            = azurerm_resource_group.main.name
  virtual_network_gateway_id     = azurerm_virtual_network_gateway.main.id
  type                           = "IPsec"
  shared_key                     = "PreSharedKeyForConnection"
  remote_vpn_site_public_address = "AWS-VPG-Public-IP"
}
```

**Step 3: Confirm the Azure Configuration:**  
```bash
az network vpn-gateway show --name aws-azure-vnet-gateway --resource-group <resource-group>
az network vpn-connection show --name aws-connection --resource-group <resource-group>
```

**Expected Output:**  
```json
{
  "provisioningState": "Succeeded",
  ...
}
{
  "connectionStatus": "Connected",
  ...
}
```

### **6. Routing Configuration**

Testing route tables was another important step in the learning process. Here’s how I configured the routes to allow cross-cloud communication.  

**On AWS:**  
```hcl
resource "aws_route" "to_azure" {
  route_table_id         = aws_vpc.main.route_table_id
  destination_cidr_block = "Azure-VNet-CIDR"
  gateway_id             = aws_vpn_gateway.main.id
}
```

**On Azure:**  
```hcl
resource "azurerm_route" "to_aws" {
  name                 = "route-to-aws"
  resource_group_name  = azurerm_resource_group.main.name
  route_table_name     = azurerm_route_table.main.name
  address_prefix       = "AWS-VPC-CIDR"
  next_hop_type        = "VirtualNetworkGateway"
}
```

**Confirm Routing Configuration:**  
```bash
aws ec2 describe-route-tables --filters "Name=state,Values=active"
az network route-table list --resource-group <resource-group>
```

**Expected Output:**  
- AWS: Route with `DestinationCidrBlock: "Azure-VNet-CIDR"` is active.  
- Azure: Route with `AddressPrefix: "AWS-VPC-CIDR"` points to the Virtual Network Gateway.

### **7. Testing the Connection**

The final step is to validate the configuration. We can use `ping` for basic connectivity test and `iperf` to measure bandwidth and latency.  

1. **Ping Test:**  
   ```bash
   kubectl exec -it test-pod -- ping Azure-Service-IP
   kubectl exec -it test-pod -- ping AWS-Service-IP
   ```

2. **iperf:**  

   ```bash
   kubectl exec -it test-pod -- iperf -c <destination-IP>
   ```

3. **Monitoring:**  
   To Do

### **8. High Availability**

To test redundancy, I configured additional tunnels and simulated failovers: 

**AWS Redundant Tunnel:**  
```hcl
resource "aws_vpn_connection" "redundant" {
  vpn_gateway_id      = aws_vpn_gateway.main.id
  customer_gateway_id = aws_customer_gateway.azure.id
  type                = "ipsec.1"
  static_routes_only = true
}
```

**Confirm:**  
```bash
aws ec2 describe-vpn-connections --filters "Name=state,Values=available"
```

**Expected Output:**  
To Do

### 9. **Final Thoughts**

This environmen* was a fantastic way to experiment with multi-cloud setups and learn the nuances of AWS and Azure networking. By the end, I had:  
- **Secure Connections:** All traffic encrypted with IPsec VPNs;
- **Resilient Design:** Redundant tunnels for reliability;
- **Optimized Performance:** Low latency between Kubernetes clusters;
- **Multi-Cloud Kubernetes Deployment:** Application deployed in two cloud providers simultaneously and automated.

This exercise not only improved my understanding of cross-cloud networking but also provided insights into how to design resilient and scalable multi-cloud architectures. If you’re exploring a similar setup, I’d love to hear your thoughts or share more about the process! 