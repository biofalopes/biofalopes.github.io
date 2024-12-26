+++
title = "Google Professional Cloud Architect - EHR Healthcare Case Study"
description = "EHR Healthcare Case Study - Aligning GCP services with the given requirements."
date =  "2024-12-23"
draft = false
toc = false
categories = ["gcp", "kubernetes"]
tags = ["gcp", "kubernetes"]
image = "DALL-E.webp"
author = "Fabio M. Lopes"
+++

### 1. Scenario Overview

EHR Healthcare is migrating from colocation data centers to Google Cloud to improve scalability, availability, and cost efficiency while maintaining legacy systems. Their requirements span modern application management, hybrid connectivity, analytics, compliance, and automation.

Link: https://services.google.com/fh/files/blogs/master_case_study_ehr_healthcare.pdf

### 2. Summary of Core Solutions

| Requirement	| GCP Solution |
| ---- | --- |
| Container Management |	Anthos / GKE |
| Hybrid Connectivity |	Cloud Interconnect, VPN |
| Monitoring & Logging |	Cloud Operations Suite |
| Availability and Latency |	Load Balancer, Multi-Region GKE |
| Managed Databases |	Cloud SQL, Memorystore, MongoDB |
| Analytics and Trends |	BigQuery, Dataflow, Looker |
| Legacy Integration |	Apigee API Management, Pub/Sub |
| Security and Compliance |	IAM, SCC, DLP, Workload Identity |
| CI/CD |	Cloud Build, Artifact Registry |
| AD FS | Google Cloud Directory Sync |

### 3. Question Breakdown by Subject

#### **A. Application Modernization (Container-Based Apps)**  
- **Likely Exam Question**: *"Which GCP service provides a consistent way to manage container-based applications?"*  
- **Answer**: **Google Kubernetes Engine (GKE)**  
- **Why**: It’s fully managed, scales automatically, and is designed for containerized workloads. Choose Anthos if on-premises or hybrid environment is a required.

---

#### **B. Hybrid Connectivity**  
- **Likely Exam Question**: *"What’s the most secure and high-performance connection between on-premises systems and Google Cloud?"*  
- **Answer**: **Cloud Interconnect** (if they need high bandwidth) or **Cloud VPN** (if security over lower bandwidth is enough).  
- **Elimination Tip**: If an option mentions “public internet” or generic connectivity, it’s likely incorrect.

---

#### **C. Logging and Monitoring**  
- **Likely Exam Question**: *"How can EHR centrally monitor and take proactive action on system performance?"*  
- **Answer**: **Google Cloud Operations Suite**.  
- **Why**: It provides consistent monitoring, logging, and alerting across cloud and hybrid environments.  

**Key Tools to Recognize**:  
- **Cloud Logging**: Centralized log collection.  
- **Cloud Monitoring**: Performance metrics and uptime monitoring.  
- **Cloud Alerting**: Configurable alerts.

---

#### **D. Scalability and Availability**  
- **Likely Exam Question**: *"How can EHR ensure 99.9% availability for customer-facing systems?"*  
- **Answer**: **Global HTTP(S) Load Balancer** + **Multi-region GKE deployment**.  
- **Why**: Load Balancer reduces latency and routes traffic globally, while regional deployments ensure redundancy.  

---

#### **E. Managed Databases**  
- **Likely Exam Question**: *"Which service can EHR use to migrate their MySQL and SQL Server databases to a managed solution?"*  
- **Answer**: **Cloud SQL**  
- **Why**: It’s a managed database service supporting MySQL and SQL Server.  

For Redis: **Memorystore**.  
For MongoDB: Likely **MongoDB Atlas** (third-party but hosted on GCP).  

---

#### **F. Analytics and Insights**  
- **Likely Exam Question**: *"Which GCP service can analyze large datasets and provide insights into healthcare trends?"*  
- **Answer**: **BigQuery**  
- **Why**: It’s a serverless data warehouse built for analyzing massive datasets.  

If real-time ingestion is involved: **Dataflow**.  
If reporting is mentioned: **Looker**.

---

#### **G. CI/CD and Deployment Automation**  
- **Likely Exam Question**: *"Which services enable automated builds and deployments for EHR’s containerized applications?"*  
- **Answer**: **Cloud Build** and **Artifact Registry**  
- **Why**: Cloud Build automates CI/CD pipelines, and Artifact Registry manages container images securely.

---

#### **H. Security and Compliance**  
- **Likely Exam Question**: *"How can EHR meet regulatory compliance while securing sensitive healthcare data?"*  
- **Answer**:  
  - **Cloud IAM**: Centralized access control.  
  - **Workload Identity**: Integrates GKE workloads with Active Directory.  
  - **Security Command Center (SCC)**: Visibility into security vulnerabilities.  
  - **Data Loss Prevention (DLP)**: Identifies and protects sensitive data.  

#### **I. Active Directory Federation Services**  
- **Likely Exam Question**: *"How can EHR sync local AD users with the cloud?"*  
- **Answer**:  
  - **Google Cloud Directory Sync**: Synchronize users and group from local AD to Cloud Identity.  

---