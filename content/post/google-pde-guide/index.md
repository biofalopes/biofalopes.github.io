+++
title = "Preparation for Google Cloud: Professional Data Engineer (PDE) Exam"
description = "My journey on how I prepared for the Google PDE exam, resources I used, insights, and practical tips."
date = "2025-04-02"
draft = false
toc = true
categories = ["gcp", "data"]
tags = ["gcp", "data-engineering"]
image = "dall-e.webp"
author = "Fabio M. Lopes"
+++

I recently passed the Google Cloud Professional Cloud Architect (PCA) exam. With multiple cloud certifications under my belt, I have decided to shift my career towards data engineering and machine learning. This transition aligns with my growing interest in moving away from infrastructure and focusing more on Data and AI. Most of the time, I worked on provisioning, architecting, and maintaining solutions for other teams. Now, I want to be on the other side a bit more. As part of this journey, I'm pursuing the Google Cloud Professional Data Engineer (PDE) certification, and in this article, I’ll share my preparation journey, useful resources, and key takeaways to help you navigate your own study path. All referenced links are listed at the end of the post.

## Learning Process

> ### TL;DR
> - Followed **Google Cloud Skills Boost** Data Engineer Path
> - Focused on **BigQuery, Dataflow, Dataproc, Pub/Sub**
> - Practiced with **ExamPrepper** mock tests
> - Did some Practice Exams I found on **Udemy**

### Google Cloud Skills Boost

I started with **Google Cloud Skills Boost**, specifically the **Data Engineer Learning Path**, which consists of various hands-on labs. I focused on:

- **BigQuery**: Optimizing queries, partitioning, and clustering.
- **Dataflow**: Streaming and batch processing.
- **Dataproc**: Running Hadoop/Spark jobs on GCP.
- **Pub/Sub**: Event-driven architectures and message queues.
- **ML/AI**: Using Vertex AI, AI Platform, and AutoML.

While Skills Boost provided a solid foundation, in my opinion it lacks in-depth content. The videos are too short, so if you want to follow that format I recommend finding a good course at Udemy or Coursera. I tried to make the best of the labs, tinkering outside the tasks to leverage the free credits. Each module has a Quiz at the end, which also serves as a practice test.

### Practice Tests

- **ExamPrepper**: There are currently 319 questions available for free and with comments from members. Extremely useful.
- **Google’s Official Sample Questions**: 21 questions, straight from the source. Not enough to prepare, but good to get a feel for the exam.

## Key Skills for PDE

- Designing Data Processing Systems: Architecting batch and streaming data processing solutions using GCP tools such as Dataflow, Dataproc, and Pub/Sub.

- Operationalizing Machine Learning Models: Deploying and managing ML models using Vertex AI, AI Platform, and AutoML.

- Building and Maintaining Data Pipelines: Implementing reliable and efficient ETL workflows with Cloud Composer and Dataflow.

- Ensuring Solution Quality: Applying best practices for data governance, security, and compliance using IAM, Data Catalog, and encryption techniques.

- Optimizing Data Solutions: Performance tuning and cost optimization for BigQuery, Cloud Storage, and other GCP data services.

- Monitoring and Troubleshooting Data Pipelines: Implementing observability with Cloud Logging, Cloud Monitoring, and error handling strategies.

## Minimum Services to Know

### Data Storage
- **BigQuery**
- **Bigtable**
- **Cloud Storage**
- **Cloud Spanner**
- **Cloud SQL**

### Data Processing
- **Dataflow**
- **Dataproc**
- **Pub/Sub**
- **Cloud Composer (Airflow)**

### ML & AI
- **Vertex AI**
- **AI Platform**
- **AutoML**

### Security & Governance
- **Cloud IAM**
- **Data Catalog**
- **Encryption & Key Management**

## Understand open source versus Google Cloud managed services

Many powerful open-source tools support modern data engineering workflows. To streamline operations at scale, Google Cloud often provides fully managed counterparts to these tools. The table below maps essential open-source technologies to their Google Cloud equivalents, highlighting key services.

| Open source | Google Cloud managed service |
| ------ | ------ |
| Hadoop, Spark, Hive | Dataproc |
| Beam | Dataflow |
| Airflow | Cloud Composer |
| Kafka, RabbitMQ | Pub/Sub |
| Cassandra | Cloud Bigtable |

## Summary

My preparation involved structured learning through **Google Cloud Skills Boost**, deep dive with labs and extensive **practice exams**. Understanding **data storage, processing, security, architecture and use cases** is critical. If you plan to take the PDE exam, ensure hands-on experience with **BigQuery, Dataflow, and Dataproc**, and be ready to evaluate real-world scenarios involving data engineering.

## Resources

- **Google Cloud Skills Boost - Data Engineer Learning Path**: https://www.cloudskillsboost.google/paths/16/
- **Exam Guide**: https://services.google.com/fh/files/misc/professional_data_engineer_exam_guide_english.pdf
- **Sample Questions**: https://docs.google.com/forms/d/e/1FAIpQLSfkWEzBCP0wQ09ZuFm7G2_4qtkYbfmk_0getojdnPdCYmq37Q/viewform
- **Google Cloud Community Guide**: https://www.googlecloudcommunity.com/gc/Community-Blogs/Your-guide-to-preparing-for-the-Google-Cloud-Professional-Data/ba-p/543105
- **Practice Tests on Udemy**: https://www.udemy.com/course/gcp-professional-data-engineer-exam-practice-tests-2024/?couponCode=ST5MT020225
- **Practice Tests on ExamPrepper**: https://www.examprepper.co/exam/10/1

Good luck with your PDE journey!