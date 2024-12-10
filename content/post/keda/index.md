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

KEDA (Kubernetes Event-driven Autoscaling) is a powerful tool that extends Kubernetes' Horizontal Pod Autoscaler (HPA) capabilities by enabling autoscaling based on various external metrics and events, rather than solely relying on CPU utilization or memory consumption. This allows for more precise and cost-effective scaling of applications. Instead of maintaining constantly running resources, KEDA scales deployments up or down based on actual demand. Practical applications abound: a serverless function triggered by messages in a queue (like Azure Service Bus, SQS, Kafka, or RabbitMQ), a batch job processing data from a blob storage (Azure Blob Storage, AWS S3), or a website scaling based on concurrent users tracked by a custom metric in CloudWatch or Prometheus. This event-driven approach ensures optimal resource utilization, reduces costs by avoiding over-provisioning, and enables a more responsive and efficient application architecture.

KEDA (Kubernetes Event-driven Autoscaling) originated from a need for more flexible and efficient autoscaling within Kubernetes deployments. Recognizing the limitations of traditional Horizontal Pod Autoscalers (HPAs) which primarily relied on CPU and memory utilization, Microsoft engineers sought a solution that could scale based on a broader range of metrics and events. This led to the development of KEDA, initially within Microsoft, but quickly evolving into an open-source project. Its conception stemmed from the desire to create a truly event-driven autoscaling mechanism that could seamlessly integrate with various external systems and services, enabling developers to optimize resource allocation and cost based on actual application demands rather than arbitrary thresholds. This focus on event-driven scaling, rather than just resource utilization, became the core differentiating factor and driving force behind KEDA's design and subsequent growth.

Another important and useful application for KEDA is the possibility of scaling-from-zero and scaling-to-zero. KEDA excels at enabling both scale-to-zero and scale-from-zero capabilities, significantly improving resource efficiency. Scale-to-zero means that when no events are triggering your application (e.g., an empty queue, no new data in a storage container), KEDA reduces the number of pods to zero, eliminating idle resource consumption. Scale-from-zero refers to the ability to automatically spin up new pods when events reappear (e.g., new messages arrive in the queue). This dynamic scaling minimizes costs by only using resources when needed. For example, a KEDA ScaledObject configured with an SQS trigger and minReplicaCount: 0 will scale to zero when the queue is empty. When a new message enters the queue, KEDA detects this event and automatically scales the deployment from zero to the minReplicaCount (or higher, if the message load requires it), ensuring swift response to incoming requests without manual intervention. This contrasts sharply with deployments that maintain a minimum number of constantly running pods, which can lead to significant waste of resources.

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
Scaling with CPU utilization is a common and straightforward approach to autoscaling. KEDA leverages this by monitoring the average CPU usage of your application's pods. When the average CPU usage crosses a predefined threshold (e.g., 70%), KEDA automatically scales up the deployment by creating additional pods. Conversely, when CPU usage falls below another threshold (or a minimum number of pods is reached), KEDA scales down, terminating idle pods. This ensures that your application has sufficient resources during periods of high demand while minimizing resource consumption during low-traffic periods. The key advantage is its simplicity; CPU is readily available as a metric, requiring minimal configuration and setup. However, relying solely on CPU utilization might not always be sufficient for complex applications with other resource constraints or scaling requirements.

First, create a simple deployment with a CPU-consuming workload. `cpu-worker-deployment.yaml`:
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

Second, create a KEDA ScaledObject to configure scaling based on CPU utilization (e.g., 50% average). `cpu-worker-scaledobject.yaml`:

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

Scaling with a CloudWatch metric offers a highly flexible and customizable approach to autoscaling, going beyond basic CPU or memory metrics. KEDA integrates with CloudWatch, allowing you to define scaling rules based on virtually any custom metric your application publishes. This could be anything from the number of active users to latency, request throughput, or error rates. By configuring a KEDA ScaledObject to monitor a specific CloudWatch metric, you can precisely control scaling based on your application's specific performance characteristics and operational needs. This granular control enables optimized resource utilization and allows you to respond effectively to a wider range of operational conditions, ensuring high availability and performance while avoiding unnecessary costs associated with over-provisioning. However, it requires more upfront configuration, as you need to ensure your application correctly publishes the relevant metrics to CloudWatch.

First, create a simple deployment that generates a CloudWatch metric. `cw-worker-deployment.yaml`:

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

Then, create a KEDA ScaledObject that configures scaling based on a custom CloudWatch metric (*MyCustomMetric*). `cw-worker-scaledobject.yaml`:

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

Scaling with an SQS queue is particularly well-suited for event-driven architectures and microservices. KEDA monitors the number of messages waiting to be processed in an Amazon SQS queue. When the message count exceeds a specified threshold, KEDA automatically scales up your deployment, creating additional pods to handle the increased workload. As messages are processed and the queue empties, KEDA scales down, terminating unnecessary pods. This ensures that your application can handle message spikes efficiently without requiring constant high resource allocation. The key benefit is its responsiveness to real-time demand: resources are only consumed when there are messages to process, leading to significant cost savings and efficient resource utilization. This makes it ideal for applications that process asynchronous tasks or handle bursts of incoming events.

This example scales a Node.js application that processes messages from an AWS SQS queue.

First, create an AWS SQS Queue:

`aws sqs create-queue --queue-name MyQueue --region us-west-2`

Then, create a simple Node.js Application. `app.js`:

```javascript
const AWS = require('aws-sdk');
const sqs = new AWS.SQS({apiVersion: '2012-11-05'});
const queueURL = 'YOUR_SQS_QUEUE_URL'; // Replace with your queue URL

const receiveMessage = async () => {
  // ... (same as previous example)
};

setInterval(receiveMessage, 1000);
```

After that, dockerize the application:

```dockerfile
FROM node:16

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

CMD [ "node", "app.js" ]
```

Now build and push:
```bash
aws ecr get-login-password --region <aws_region> | docker login --username AWS --password-stdin <account_id>.dkr.ecr.<aws_region>.amazonaws.com
docker build -t <repo_name>:<tag> .
docker tag <repo_name>:<tag> <account_id>.dkr.ecr.<aws_region>.amazonaws.com/<repo_name>:<tag>
docker push <account_id>.dkr.ecr.<aws_region>.amazonaws.com/<repo_name>:<tag>
```

Then, create a kubernetes Deployment (sqs-worker-deployment.yaml):**

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

And a KEDA ScaledObject. `sqs-worker-scaledobject.yaml`:

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

Last, to test it, send messages to the SQS queue and observe the scaling behavior. This script uses the AWS CLI to send messages to a SQS queue:

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

This comprehensive tutorial demonstrates KEDA's capabilities across different scaling scenarios.  By mastering these techniques, you can significantly improve the efficiency and cost-effectiveness of your Kubernetes deployments.
