+++
title = "Google Professional Cloud Architect - Helicopter Racing League Case Study"
description = "Helicopter Racing League Case Study - Aligning GCP services with the given requirements."
date =  "2024-12-22"
draft = false
toc = false
categories = ["gcp", "kubernetes"]
tags = ["gcp", "kubernetes"]
image = "helicopter.png"
author = "Fabio M. Lopes"
+++

### 1. Scenario Overview

**Helicopter Racing League (HRL)** is an emerging esports organization focused on competitive helicopter racing simulations. HRL streams live events globally and offers fans real-time stats, telemetry, and replays. The league is planning to move to Google Cloud to enhance scalability, improve user experience, and optimize costs. Their requirements span real-time data processing, low latency streaming, and robust analytics capabilities.

**Link**: [Helicopter Racing League Case Study](https://services.google.com/fh/files/blogs/master_case_study_helicopter_racing_league.pdf)

---

### 2. Summary of Core Solutions

| **Requirement**                       | **GCP Solution**                  |
|---------------------------------------|------------------------------------|
| Real-Time Data Processing             | Dataflow, Pub/Sub                 |
| Low Latency Streaming                 | Cloud CDN, Global Load Balancer   |
| User Analytics and Insights           | BigQuery, Looker                  |
| Scalable Infrastructure for Events    | Compute Engine, GKE               |
| AI/ML for Predictions and Highlights  | Vertex AI, BigQuery ML            |
| Security and Compliance               | IAM, Cloud Armor, SCC             |
| Continuous Integration and Deployment | Cloud Build, Artifact Registry    |
| Cost Optimization                     | Active Assist, Autoscaler         |

---

### 3. Question Breakdown by Subject

#### **A. Real-Time Data Processing**
- **Likely Exam Question**: *"Which GCP service processes real-time telemetry data from helicopters during live events?"*
- **Answer**: **Dataflow and Pub/Sub**  
- **Why**: Pub/Sub handles message ingestion and distribution, while Dataflow processes streaming data in real time for stats, leaderboards, and replays.

---

#### **B. Low Latency Streaming**
- **Likely Exam Question**: *"How can HRL deliver low-latency streams to fans globally?"*
- **Answer**: **Cloud CDN** and **Global HTTP(S) Load Balancer**  
- **Why**: These services ensure fast content delivery and efficient routing of streaming traffic to minimize latency for global audiences.

---

#### **C. User Analytics and Insights**
- **Likely Exam Question**: *"Which GCP service enables HRL to analyze fan engagement and event metrics?"*
- **Answer**: **BigQuery and Looker**  
- **Why**: BigQuery provides a scalable data warehouse for analyzing massive datasets, and Looker generates user-friendly reports and dashboards.

---

#### **D. Scalable Infrastructure for Events**
- **Likely Exam Question**: *"What is the best way to handle traffic spikes during HRL’s live-streamed events?"*
- **Answer**: **GKE or Compute Engine**  
- **Why**: GKE is ideal for containerized workloads and scaling services automatically, while Compute Engine offers flexibility for VM-based workloads.

---

#### **E. AI/ML for Predictions and Highlights**
- **Likely Exam Question**: *"Which GCP service can HRL use to generate AI-powered predictions and video highlights?"*
- **Answer**: **Vertex AI and BigQuery ML**  
- **Why**: Vertex AI trains and deploys custom models for predictions, while BigQuery ML enables lightweight machine learning directly within the data warehouse.

---

#### **F. Security and Compliance**
- **Likely Exam Question**: *"How can HRL secure its live-streaming platform and user data?"*
- **Answer**:  
  - **IAM**: Centralized access control.  
  - **Cloud Armor**: Protects against DDoS attacks.  
  - **Security Command Center (SCC)**: Identifies vulnerabilities and ensures compliance.

---

#### **G. Continuous Integration and Deployment**
- **Likely Exam Question**: *"Which GCP tools support automated build and deployment pipelines for HRL’s platform?"*
- **Answer**: **Cloud Build and Artifact Registry**  
- **Why**: Cloud Build automates CI/CD pipelines, and Artifact Registry securely stores container images and build artifacts.

---

#### **H. Cost Optimization**
- **Likely Exam Question**: *"Which GCP features can HRL use to optimize costs during non-peak times?"*
- **Answer**:  
  - **Active Assist**: Provides cost-saving recommendations.  
  - **Autoscaler**: Dynamically adjusts resources based on demand to avoid over-provisioning.

---