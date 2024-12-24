+++
title = "Google Professional Cloud Architect - TerramEarth Case Study"
description = "TerramEa!h Case Study - Aligning GCP services with the given requirements."
date =  "2024-12-20"
draft = false
toc = false
categories = ["gcp", "kubernetes"]
tags = ["gcp", "kubernetes"]
image = "DALL-E.webp"
author = "Fabio M. Lopes"
+++

### 1. Scenario Overview

**TerramEarth** is a global manufacturer of heavy machinery for mining and agricultural industries. They aim to improve fleet management and equipment maintenance by migrating to Google Cloud. Their requirements include real-time telemetry processing, predictive analytics, and high availability to support global operations.

**Link**: [TerramEarth Case Study](https://services.google.com/fh/files/blogs/master_case_study_terramearth.pdf)

---

### 2. Summary of Core Solutions

| **Requirement**                       | **GCP Solution**                  |
|---------------------------------------|------------------------------------|
| Real-Time Telemetry Ingestion         | Pub/Sub, Dataflow                 |
| Predictive Maintenance                | BigQuery, BigQuery ML             |
| High Availability for APIs            | Global HTTP(S) Load Balancer      |
| Scalable Processing of Batch Data     | Dataflow, Cloud Storage           |
| User Analytics and Reporting          | Looker, BigQuery                  |
| Secure Fleet Data                     | IAM, Cloud Armor, SCC             |
| Cost Optimization                     | Active Assist, Autoscaler         |

---

### 3. Question Breakdown by Subject

#### **A. Real-Time Telemetry Ingestion**
- **Likely Exam Question**: *"Which GCP services should TerramEarth use to ingest and process real-time equipment telemetry data?"*
- **Answer**: **Pub/Sub and Dataflow**  
- **Why**: Pub/Sub handles reliable ingestion of telemetry events, while Dataflow processes and transforms the data for downstream use in real time.

---

#### **B. Predictive Maintenance**
- **Likely Exam Question**: *"How can TerramEarth predict when machinery will require maintenance?"*
- **Answer**: **BigQuery and BigQuery ML**  
- **Why**: BigQuery stores historical and real-time data, while BigQuery ML trains and runs predictive maintenance models directly on the data.

---

#### **C. High Availability for APIs**
- **Likely Exam Question**: *"What GCP service ensures global availability of TerramEarth’s APIs for fleet management?"*
- **Answer**: **Global HTTP(S) Load Balancer**  
- **Why**: It distributes traffic globally, ensuring low latency and high availability for APIs.

---

#### **D. Scalable Processing of Batch Data**
- **Likely Exam Question**: *"Which services can process large-scale historical telemetry data for analysis?"*
- **Answer**: **Dataflow and Cloud Storage**  
- **Why**: Cloud Storage stores batch data, and Dataflow processes it efficiently for analysis.

---

#### **E. User Analytics and Reporting**
- **Likely Exam Question**: *"Which GCP services provide actionable insights and reporting for TerramEarth’s operations?"*
- **Answer**: **BigQuery and Looker**  
- **Why**: BigQuery performs data analysis at scale, and Looker provides user-friendly dashboards and reports.

---

#### **F. Security**
- **Likely Exam Question**: *"How can TerramEarth secure sensitive telemetry data and APIs?"*
- **Answer**:  
  - **IAM**: Manages access control.  
  - **Cloud Armor**: Protects APIs against DDoS attacks.  
  - **Security Command Center (SCC)**: Identifies vulnerabilities and ensures compliance.

---

#### **G. Cost Optimization**
- **Likely Exam Question**: *"How can TerramEarth optimize costs while scaling resources?"*
- **Answer**:  
  - **Active Assist**: Recommends cost-saving measures.  
  - **Autoscaler**: Adjusts resources dynamically based on demand.

---