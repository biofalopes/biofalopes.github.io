+++
title = "KEDA: Kubernetes Event-driven Autoscaling - Multiple Strategies on EKS"
description = "A comprehensive tutorial demonstrating KEDA's versatility with EKS: setting up a cluster, scaling with CPU, CloudWatch, and SQS."
date = "2024-12-10"
draft = false
toc = false
categories = ["kubernetes", "keda", "aws"]
tags = ["kubernetes", "keda", "aws"]
image = "keda.webp"
author = "Fabio M. Lopes"
+++

This tutorial demonstrates the power and versatility of Kubernetes Event-driven Autoscaling (KEDA) on Amazon EKS, covering multiple scaling strategies. We'll start by creating an EKS cluster, then explore scaling based on CPU utilization, a CloudWatch metric, and finally, revisiting the SQS queue example.

**Prerequisites:**

* An AWS account with appropriate permissions.
* The AWS CLI installed and configured.
* The `kubectl` command-line tool.
* Basic familiarity with Kubernetes concepts.


#### 1. Creating an EKS Cluster:

Before deploying KEDA, we'll create a basic EKS cluster using the AWS CLI.  Replace placeholders with your desired values:

```bash
# Create a Kubernetes network
aws eks create-cluster --name my-eks-cluster --region us-west-2 --role-arn <YOUR_IAM_ROLE_ARN> --resources-vpc-config subnetIds=<SUBNET_ID_1>,<SUBNET_ID_2>,<SUBNET_ID_3> --kubernetes-network-config ipFamily=ipv4

# Wait for the cluster to be created
aws eks wait cluster-active --name my-eks-cluster --region us-west-2

# Get the kubeconfig
aws eks update-kubeconfig --name my-eks-cluster --region us-west-2
```

Replace `<YOUR_IAM_ROLE_ARN>`, `<SUBNET_ID_1>`, `<SUBNET_ID_2>`, and `<SUBNET_ID_3>` with your actual values.  Ensure your IAM role has the necessary permissions to create and manage EKS resources. The subnet IDs should be from the same VPC and availability zones.  After this, your `kubectl` should be configured to connect to the new cluster.

#### 2. Installing KEDA on EKS:

1. Add the KEDA Helm repository:
   ```bash
   helm repo add kedacore https://kedacore.github.io/keda/helm-charts/
   helm repo update
   ```

2. Install KEDA:
   ```bash
   helm install keda kedacore/keda --create-namespace
   ```

For more detailed information on KEDA deployment, visit https://keda.sh/docs/2.16/deploy/.

#### 3. Scaling with CPU Utilization:

1. **Create a Deployment:** (`cpu-worker-deployment.yaml`) A simple deployment with a CPU-consuming workload.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cpu-worker
spec:
  replicas: 0 # KEDA will manage replicas
  selector:
    matchLabels:
      app: cpu-worker
  template:
    metadata:
      labels:
        app: cpu-worker
    spec:
      containers:
      - name: cpu-worker
        image: busybox
        imagePullPolicy: Always
        command: ["sh", "-c", "while true; do sleep 1; done"] # Simple CPU consuming task
        resources:
          requests:
            cpu: 100m
```

2. **Create a KEDA ScaledObject:** (`cpu-worker-scaledobject.yaml`) Configure scaling based on CPU utilization (e.g., 50% average).

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: cpu-worker-scaledobject
spec:
  scaleTargetRef:
    name: cpu-worker
  pollingInterval: 10
  minReplicaCount: 0
  maxReplicaCount: 5
  triggers:
  - type: cpu
    metadata:
      targetAverageUtilization: 50 # Scale when CPU utilization exceeds 50%
```

#### 4. Scaling with a CloudWatch Metric:

1. **Create a Deployment:** (`cw-worker-deployment.yaml`) A deployment that generates a CloudWatch metric.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cw-worker
spec:
  replicas: 0
  selector:
    matchLabels:
      app: cw-worker
  template:
    metadata:
      labels:
        app: cw-worker
    spec:
      containers:
      - name: cw-worker
        image: busybox
        command: ["sh", "-c", "while true; do sleep 1; done"]
```

1. **Create a KEDA ScaledObject:** (`cw-worker-scaledobject.yaml`) Configure scaling based on a custom CloudWatch metric (`MyCustomMetric`).

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: cw-worker-scaledobject
spec:
  scaleTargetRef:
    name: cw-worker
  pollingInterval: 30
  minReplicaCount: 0
  maxReplicaCount: 5
  triggers:
  - type: cloudwatch
    metadata:
      metricName: MyCustomMetric # Replace with your metric name
      namespace: MyNamespace   # Replace with your CloudWatch namespace.  Sometimes this is omitted
      region: YOUR_AWS_REGION #Replace with your AWS region
      statistic: Average      # Statistic type
      threshold: 10           # Scale when above 10
      awsAccessKeyId: YOUR_AWS_ACCESS_KEY_ID #Replace with your AWS access key
      awsSecretAccessKey: YOUR_AWS_SECRET_ACCESS_KEY #Replace with your AWS secret key
```

#### 5. Scaling with an SQS Queue:

This example scales a Node.js application that processes messages from an AWS SQS queue.

**5.1. Create an AWS SQS Queue:**

`aws sqs create-queue --queue-name MyQueue --region us-west-2`

**5.2. Node.js Application (app.js):**

```javascript
const AWS = require('aws-sdk');
const sqs = new AWS.SQS({apiVersion: '2012-11-05'});
const queueURL = 'YOUR_SQS_QUEUE_URL'; // Replace with your queue URL

const receiveMessage = async () => {
  // ... (same as previous example)
};

setInterval(receiveMessage, 1000);
```

**5.3. Dockerize the Application:**

```dockerfile
FROM node:16

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

CMD [ "node", "app.js" ]
```

Build and push:
```bash
aws ecr get-login-password --region <aws_region> | docker login --username AWS --password-stdin <account_id>.dkr.ecr.<aws_region>.amazonaws.com
docker build -t <repo_name>:<tag> .
docker tag <repo_name>:<tag> <account_id>.dkr.ecr.<aws_region>.amazonaws.com/<repo_name>:<tag>
docker push <account_id>.dkr.ecr.<aws_region>.amazonaws.com/<repo_name>:<tag>
```

**5.4. Kubernetes Deployment (sqs-worker-deployment.yaml):**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sqs-worker
spec:
  replicas: 0
  selector:
    matchLabels:
      app: sqs-worker
  template:
    metadata:
      labels:
        app: sqs-worker
    spec:
      containers:
      - name: sqs-worker
        image: your-ecr-repo/sqs-worker:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 3000
```

**5.5. KEDA ScaledObject (sqs-worker-scaledobject.yaml):**

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: sqs-worker-scaledobject
spec:
  scaleTargetRef:
    name: sqs-worker
  pollingInterval: 30
  minReplicaCount: 0
  maxReplicaCount: 10
  triggers:
  - type: sqs
    metadata:
      queueURL: YOUR_SQS_QUEUE_URL
      awsAccessKeyId: YOUR_AWS_ACCESS_KEY_ID
      awsSecretAccessKey: YOUR_AWS_SECRET_ACCESS_KEY
      region: YOUR_AWS_REGION
```

**5.6. Send messages to the SQS queue to observe the scaling behavior**

This script uses the AWS CLI to send messages to a SQS queue:

```bash
#!/bin/bash

# Set the SQS queue URL
queue_url="YOUR_SQS_QUEUE_URL"

# Set the number of messages to send
num_messages=10

# Set the message body (you can customize this)
message_body="Hello from KEDA scaling test!"

# Send messages to the SQS queue
for i in $(seq 1 $num_messages); do
  aws sqs send-message --queue-url "$queue_url" --message-body "$message_body"
  echo "Sent message $i to queue $queue_url"
  sleep 1 # Add a small delay to avoid overwhelming the queue
done

echo "Sent all messages."
```

Give the script run permissions with `chmod +x` and run it using `./send_messages.sh`. While this script runs, monitor your KEDA scaled object to see the number of replicas increase as messages accumulate in the queue. After the script finishes, you may want to delete the messages from the queue to observe the scaling down. You can do this using the AWS console or another script. For example:

`aws sqs purge-queue --queue-url "$queue_url"`

This comprehensive tutorial demonstrates KEDA's capabilities across different scaling scenarios.  Remember to replace placeholders with your specific AWS credentials and resource names.  By mastering these techniques, you can significantly improve the efficiency and cost-effectiveness of your Kubernetes deployments.
