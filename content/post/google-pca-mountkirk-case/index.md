+++
title = "Google Professional Cloud Architect - Mountkirk Games Case Study"
description = "Mountkirk Games Case Study - Aligning GCP services with the given requirements."
date =  "2024-12-21"
draft = false
toc = false
categories = ["gcp", "kubernetes"]
tags = ["gcp", "kubernetes"]
image = "mountkirk.png"
author = "Fabio M. Lopes"
+++

### 1. Scenario Overview

**Mountkirk Games** is a gaming company focused on building highly engaging multiplayer mobile games. They aim to migrate their backend infrastructure to Google Cloud to scale with demand, improve deployment agility, and enhance game performance. Their requirements focus on real-time data processing, scalable backends, global availability, and analytics.

**Link**: [Mountkirk Games Case Study](https://services.google.com/fh/files/blogs/master_case_study_mountkirk_games.pdf)

---

### 2. Summary of Core Solutions

| **Requirement**                       | **GCP Solution**                  |
|---------------------------------------|------------------------------------|
| Real-Time Data Processing             | Pub/Sub, Dataflow                 |
| Scalable Backend                      | GKE, App Engine                   |
| Global Availability                   | Global HTTP(S) Load Balancer      |
| Game Analytics and Insights           | BigQuery, Dataflow                |
| CI/CD for Game Updates                | Cloud Build, Artifact Registry    |
| Security                              | IAM, Cloud Armor, SCC             |

---

### 3. Question Breakdown by Subject

#### **A. Real-Time Data Processing**
- **Likely Exam Question**: *"Which GCP services can Mountkirk Games use to handle in-game event streams in real time?"*
- **Answer**: **Pub/Sub and Dataflow**  
- **Why**: Pub/Sub ingests and delivers events reliably, while Dataflow processes and transforms streaming data in real time.

---

#### **B. Scalable Backend**
- **Likely Exam Question**: *"What is the best way to handle a rapidly growing player base for Mountkirk’s games?"*
- **Answer**: **GKE or App Engine**  
- **Why**: GKE supports containerized microservices, while App Engine provides a fully managed PaaS solution for scaling backend services automatically.

---

#### **C. Global Availability**
- **Likely Exam Question**: *"How can Mountkirk Games ensure low-latency access for players worldwide?"*
- **Answer**: **Global HTTP(S) Load Balancer**  
- **Why**: It routes player traffic to the nearest healthy backend, minimizing latency and ensuring high availability.

---

#### **D. Game Analytics and Insights**
- **Likely Exam Question**: *"Which GCP services enable Mountkirk Games to analyze player data and generate insights?"*
- **Answer**: **BigQuery and Dataflow**  
- **Why**: BigQuery handles large-scale analytics, while Dataflow processes real-time player telemetry data.

---

#### **E. CI/CD for Game Updates**
- **Likely Exam Question**: *"Which GCP tools can automate Mountkirk’s game deployment pipeline?"*
- **Answer**: **Cloud Build and Artifact Registry**  
- **Why**: Cloud Build automates the CI/CD process, while Artifact Registry stores container images and build artifacts securely.

---

#### **F. Security**
- **Likely Exam Question**: *"How can Mountkirk Games secure their platform against attacks and unauthorized access?"*
- **Answer**:  
  - **IAM**: Centralized access control.  
  - **Cloud Armor**: Protects against DDoS attacks.  
  - **Security Command Center (SCC)**: Identifies vulnerabilities and ensures compliance.

---