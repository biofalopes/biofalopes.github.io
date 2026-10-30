+++
title = "Google Cloud Professional Data Engineer: A Practical Study Guide and Service Reference"
description = "A companion reference for the Professional Data Engineer exam, covering service selection, BigQuery, pipelines, streaming, security, operations, and exam-style scenarios."
date = "2026-10-30"
draft = false
toc = true
categories = ["gcp", "data"]
tags = ["gcp", "data-engineering", "certification", "study-guide"]
author = "Fabio M. Lopes"
+++

The [Google Cloud Professional Data Engineer (PDE) certification](https://cloud.google.com/learn/certification/data-engineer) covers a broad range of subjects: data storage, batch and streaming processing, orchestration, security, governance, machine learning, and operating data systems over time.

When I first put together my PDE preparation notes, I wanted a single place where I could compare services, review concepts, and revisit scenarios that could appear in the exam. The notes eventually became too long for the article about my personal preparation experience.

This companion guide keeps that original objective while making the reference easier to scan. It is organized around the decisions a data engineer might need to make, rather than a long sequence of product descriptions. It combines topics from my original 2025 notes with terminology and documentation updates reviewed in October 2026. **It is an independent study aid, not an official exam guide or a guarantee of exam coverage.**

For my personal preparation process and the learning resources I used, see my companion article: [Preparing for the Google Cloud Professional Data Engineer Exam: My Study Approach and Resources]({{< relref "/post/google-pde-prep" >}}).

> **How to use this guide:** Start with the [official exam guide](https://cloud.google.com/learn/certification/data-engineer), then use the sections below to identify areas you cannot yet explain in your own words. Try a lab or small experiment, and finally practice answering *why* one service might fit a given scenario better than another.

## 1. Start with the exam objectives

The official certification page is the source of truth for the current exam format, languages, eligibility, and links to the standard and renewal exam guides. Exam objectives and services change, so I would not treat any static checklist as exhaustive.

The main areas I would organize my study around are:

- Designing data processing architectures, including batch and streaming.
- Ingesting, storing, and processing data with appropriate services.
- Maintaining reliable pipelines and orchestrating dependent workloads.
- Security, governance, data quality, and access management.
- Monitoring, troubleshooting, performance, and cost optimization.
- Understanding where machine learning fits into data engineering workflows.

As a study exercise, take any architecture question and identify its workload volume, latency requirements, consistency expectations, operational constraints, security requirements, and cost priorities **before** picking a product.

## 2. A quick service-selection map

| Requirement | Services worth evaluating | Main question |
| --- | --- | --- |
| Analytical SQL over large datasets | BigQuery | Is the primary workload analytical rather than transactional? |
| Large-scale key-based, low-latency access | Bigtable | Are access patterns known and row-key design appropriate? |
| Globally distributed relational transactions | Spanner | Are strong consistency and horizontal scale requirements sufficient to justify the complexity and cost? |
| Managed relational database | Cloud SQL | Does a conventional relational engine satisfy the workload? |
| Object storage and data lake inputs | Cloud Storage | Which storage class, lifecycle, and file format fit the access pattern? |
| Event ingestion and fan-out | Pub/Sub | How will consumers handle duplicates, ordering, and backpressure? |
| Managed batch or streaming transformations | Dataflow / Apache Beam | Are event-time processing, windows, and autoscaling relevant? |
| Managed Spark or Hadoop workloads | Dataproc | Is there existing Spark/Hadoop code or ecosystem compatibility to preserve? |
| Scheduled, dependent workflows | Cloud Composer / Apache Airflow | Do dependencies, retries, and operational visibility justify orchestration? |
| Model training and inference | Vertex AI | Is the requirement feature preparation, training, evaluation, or prediction serving? |
| SQL-based ML on warehouse data | BigQuery ML | Can the model workflow stay close to the data in BigQuery? |
| Metadata, discovery, governance | BigQuery universal catalog | How will data assets be discovered, classified, and governed? |

These are starting points, not one-to-one equivalents. For example, Pub/Sub can replace some messaging patterns associated with Kafka or RabbitMQ, but the products do not offer identical execution or operational semantics.

## 3. Data storage and analytical systems

### BigQuery: analytical workloads

BigQuery is central to many PDE scenarios. I would spend time on **how data is modeled, loaded, queried, secured, and paid for**, rather than memorizing individual SQL examples.

**Modeling.** Know the trade-offs between star and snowflake schemas, denormalization, nested and repeated fields, and how those choices influence analytical query patterns. A star schema can simplify common dimensional queries; further normalization can reduce duplication but require additional joins.

**Partitioning and clustering.** Partitioning can reduce scanned data when queries filter on a supported partition key. Clustering can further help organize data for filters and aggregation. Neither feature is a universal optimization: examine real query predicates and data distribution before choosing keys.

**Execution and query tuning.** Study query execution details through the BigQuery query plan and execution graph, along with bytes processed, shuffle behavior, joins, and partition pruning. My original notes referred to generic `EXPLAIN` and index-based scans; that is not a useful mental model for BigQuery's execution engine. [BigQuery query plan documentation](https://cloud.google.com/bigquery/docs/query-plan-explanation) is a better reference.

**Derived results.** Views, materialized views, and scheduled queries solve different needs. Materialized views can accelerate supported repeated aggregations, but their refresh behavior, eligibility, and maintenance costs matter.

**Pricing.** Compare on-demand query pricing with capacity-based compute pricing using BigQuery editions, reservations, and slots. The older “flat-rate versus on-demand” distinction in my initial notes is outdated. Storage, streaming, and other charges also need consideration. [Current pricing](https://cloud.google.com/bigquery/pricing).

**Data ingestion.** Know batch loads from Cloud Storage, managed transfers through BigQuery Data Transfer Service, and ingestion using the Storage Write API. Think about latency, at-least-once versus exactly-once semantics where applicable, cost, and operational complexity.

**Security.** Understand project, dataset, table, row, and column access patterns; authorized views; policy tags; data masking; IAM; and customer-managed encryption keys (CMEK). A view that exposes selected fields is useful, but simply creating a view is not the same as enforcing all row- and column-level security requirements.

**Other capabilities.** Understand BigQuery ML for SQL-centric model workflows and BigQuery Omni for certain cross-cloud analytics patterns. They are worth knowing conceptually, but always check their current limits and supported regions.

**Scenario to reason through:** A dashboard repeatedly aggregates sales by date and product category. What are the relative benefits of partitioning, clustering, a materialized view, and a capacity reservation? What evidence would you collect before choosing?

### Cloud Storage: objects and analytical file formats

Cloud Storage is often the landing zone for files before a processing or analytics stage.

Know Standard, Nearline, Coldline, and Archive classes, together with minimum storage durations, retrieval costs, and lifecycle policies. Infrequent access alone does not determine the optimal class; retrieval patterns and retention matter.

Review object versioning, retention controls, lifecycle management, signed URLs, IAM, Storage Transfer Service, and the `gcloud storage` command family. Older materials may still use `gsutil`; recognize it, but learn the current tooling as well.

**File formats matter:** CSV and JSON are common interchange formats; Avro is row-oriented and supports schemas; Parquet and ORC are columnar formats that can be efficient for analytical scanning. My original notes incorrectly grouped Avro with columnar formats. Compression and schema evolution support vary by format and integration.

**Scenario:** You ingest large daily event files and query only a few columns. Would you transform the files into Parquet before analysis, and how would that interact with your downstream BigQuery loading strategy?

### Cloud SQL: managed relational engines

Review MySQL, PostgreSQL, and SQL Server deployment options; backups; point-in-time recovery; high availability; read replicas; connection management; IAM-related access; networking; and the Cloud SQL Auth Proxy.

High availability and read replication serve different purposes. A read replica is not automatically equivalent to a high-availability failover configuration. For a latency-sensitive application, connection pooling and database limits may be as important as instance size.

**Scenario:** A transactional application needs automatic failover and recovery from accidental deletion. Explain why failover, backups, and point-in-time recovery address different failure modes.

### Spanner: relational consistency at scale

Study primary-key design, interleaving or table locality concepts, secondary indexes, transactions, replication, and the cost/performance implications of data distribution. Monotonically increasing keys may create hotspots, depending on the schema and workload.

Do not assume Spanner is preferable whenever a relational database must scale. Its value depends on geographic distribution, consistency requirements, write patterns, and the organization's tolerance for operational and financial complexity.

### Bigtable: low-latency, wide-column access

Know row-key design, access patterns, hotspots, column families, replication, and why a key-value or wide-column workload differs from an analytical SQL warehouse.

A useful comparison: **Bigtable** can fit high-throughput key-oriented lookups; **BigQuery** can fit large analytical scans; **Spanner** can fit relational transactions at distributed scale. They solve overlapping but materially different problems.

### Firestore in Datastore mode

Review entity kinds, keys, indexes, transactions, consistency behavior, namespaces, and query limitations. The original notes described Datastore as uniformly “eventually consistent,” which is too broad for an exam reference. Look at the guarantees of the specific database mode and operation in the [current Firestore documentation](https://cloud.google.com/firestore/docs).

## 4. Data processing: batch, streaming, and orchestration

### Dataflow and Apache Beam

Dataflow runs Apache Beam pipelines in a managed environment. Understand how `PCollection`, `PTransform`, and pipeline definitions relate to the processing graph.

The more challenging concepts usually involve **event time, processing time, watermarks, windows, triggers, late data, and state**.

| Concept | Questions to ask |
| --- | --- |
| Fixed window | Is grouping by nonoverlapping intervals acceptable? |
| Sliding window | Does a rolling view justify overlapping computations? |
| Session window | Is activity separated by gaps, for example user inactivity? |
| Watermark | How does the system estimate event-time completeness? |
| Trigger | When should partial or final results be emitted? |
| Allowed lateness | What happens when data arrives after the watermark? |
| Deduplication | Can sources and retries produce duplicate events? |

Batch and streaming pipelines have different resource, latency, and operational characteristics. Review autoscaling, worker failures, shuffle, stateful processing, and templates. Automatic worker recovery does not mean application code is free from side effects or duplicate-processing risk.

**Scenario:** You must detect an abandoned shopping cart after a user becomes inactive. A session window may help represent inactivity, but you also need to define which events indicate checkout and how late events affect the decision.

### Dataproc, Spark, and Hadoop

Dataproc is especially relevant when an organization already uses Spark, Hadoop, Hive, or related ecosystem components.

Know Spark DataFrames, Spark SQL, RDDs, and the basics of execution graphs and partitioning. For Hadoop, understand HDFS and MapReduce at a conceptual level. Spark's model can be advantageous for iterative computation, but performance depends on workload and configuration.

Operational topics from my notes worth reviewing include cluster sizing, autoscaling policies, worker decommissioning, job submission (`gcloud dataproc jobs submit spark`), initialization actions, image versions, the component gateway, and integrations with Cloud Storage, BigQuery, and Cloud Logging.

Be careful with simplistic autoscaling statements: Dataproc autoscaling behavior depends on configuration, supported components, and relevant YARN metrics; a generic CPU-threshold example is not a reliable description of its autoscaling policy mechanism.

**Scenario:** Your company has existing Spark jobs and libraries. What would be gained or lost by moving them to Dataflow rather than running them on Dataproc?

### Pub/Sub: messaging and asynchronous processing

Review topics, subscriptions, publishers, pull versus push, filters, retention, dead-letter topics, retry policies, acknowledgment deadlines, and subscriber observability.

**Default delivery is at least once, with no general ordering guarantee.** Ordering keys can provide ordering for messages with the same key under documented constraints. Exactly-once delivery is a configurable feature of pull subscriptions, scoped to a region and subject to its documented semantics. It does not automatically guarantee that arbitrary downstream business operations happen exactly once. [Subscription behavior](https://cloud.google.com/pubsub/docs/subscription-overview) and [exactly-once delivery](https://cloud.google.com/pubsub/docs/exactly-once-delivery).

Build consumers to handle duplicate delivery, delayed events, backpressure, and dead-letter processing. Know when idempotency should be enforced in application logic.

**Scenario:** A payment event triggers fulfillment. How can the consumer avoid duplicate fulfillment when messages are redelivered? How would you monitor unacknowledged message backlog and oldest message age?

### Cloud Composer and Apache Airflow

Composer provides a managed Airflow environment for orchestrating dependent workloads. Learn DAGs, tasks, operators, scheduling, retries, connections, variables, XCom, idempotency, backfills, catchup, and operational logs.

I would focus on the distinction between an orchestrator and a processing engine. Airflow can coordinate BigQuery and Dataflow jobs without executing all their computation inside Airflow workers.

Operator names and providers evolve, so avoid memorizing older classes such as `BigQueryOperator` without checking the current provider package. Prefer understanding what the operator does and how authentication, retries, and data dependencies are modeled.

**Scenario:** A daily pipeline loads Cloud Storage files, transforms data in BigQuery, validates results, and publishes a report. What happens when the transformation fails after the load has already succeeded? How will reruns avoid duplicate output?

### Event-driven compute

Cloud Functions, now commonly discussed within the Cloud Run functions product family, can run event-triggered and HTTP-triggered code without managing servers directly. Study event sources, service accounts, memory and timeout configuration, concurrency where supported, cold starts, retries, and observability.

Understand the distinction between using a function to process a lightweight event and using Dataflow or Dataproc for sustained large-scale processing. Service names, generation-specific capabilities, and limits need checking against the current documentation.

## 5. Machine learning from the data engineer's perspective

The PDE exam is not primarily an ML research exam. The practical concern is often whether data is reliable, properly transformed, governed, and ready for training or inference.

### Vertex AI

Know the roles of managed datasets, custom training, AutoML approaches, pipelines, model registry, endpoints, batch prediction, online prediction, monitoring, and feature management.

Concepts worth understanding include training versus serving, evaluation metrics (precision, recall, AUC where appropriate), hyperparameter tuning, distributed training, and data drift. Model and feature capabilities evolve frequently, so validate specific current product names before relying on old diagrams.

### BigQuery ML

Understand when SQL-based model building close to warehouse data makes sense. Practice recognizing supported workflows and the implications for data movement, model evaluation, and operationalization.

### TensorFlow, PyTorch, GPUs, and TPUs

Know these as ecosystem and compute choices rather than attempting to memorize every training API. Be able to explain why the size of a model or dataset, framework requirements, accelerators, and distributed training strategy might influence a Vertex AI workload design.

**Scenario:** Most features already live in BigQuery, and the goal is a straightforward regression model. Would BigQuery ML simplify the workflow? What would push you toward custom training on Vertex AI instead?

## 6. Security, privacy, and data governance

### IAM and resource hierarchy

Review organizations, folders, projects, policies, inheritance, principal types, groups, service accounts, predefined roles, custom roles, and least privilege.

Remember that broad grants at higher levels in the resource hierarchy can affect downstream resources. IAM policies generally combine applicable permissions; a lower-level grant does not simply override a higher-level grant. Deny policies and other controls introduce additional rules.

Service account keys create long-lived credential risks. Prefer appropriately scoped workload identities and keyless authentication where suitable rather than treating periodic key rotation as the complete answer.

### Data classification, discovery, and governance

My original notes included **Data Catalog**, which was deprecated in 2025 with a discontinuation date of January 30, 2026. Study the [BigQuery universal catalog](https://cloud.google.com/dataplex/docs/catalog-overview) direction instead, while recognizing older names when reading historical practice material.

Understand discovery, metadata, lineage, classification, policy tags, data quality, and auditability at the architectural level.

### Sensitive data and Cloud KMS

Review Sensitive Data Protection (formerly Cloud DLP) concepts such as inspection, infoTypes, masking, redaction, de-identification, and tokenization. Understand when to use templates and how sensitive data may appear in Cloud Storage, BigQuery, and streams.

For Cloud KMS, learn key rings, key versions, rotation, IAM roles, CMEK, envelope encryption, and operational implications of key unavailability. Rotation policies depend on compliance requirements and how keys are consumed; they are not a substitute for authorization controls.

**Scenario:** Multiple customers share a data platform but should not see each other's data. Evaluate dataset separation, row-level policies, service identities, and audit logging. Which controls enforce isolation and which only help detect violations?

## 7. Operations, reliability, and cost

### Monitoring and troubleshooting

Distinguish metrics, logs, traces, and audit logs. Review Cloud Monitoring dashboards and alerting, Cloud Logging queries and structured entries, log-based metrics, and log sinks to Cloud Storage, BigQuery, or Pub/Sub.

For data pipelines, useful signals might include throughput, error rates, processing latency, consumer backlog, failed jobs, duplicate events, late data, and end-to-end freshness. A pipeline can be technically running while the delivered data is stale or incorrect.

### Reliability patterns worth recognizing

- Idempotent processing and repeatable backfills.
- Controlled retries with backoff and clear terminal-failure behavior.
- Dead-letter handling and reprocessing workflows.
- Checkpoints, recovery, and replay behavior.
- Data validation at ingestion and transformation stages.
- Service quotas, capacity constraints, and autoscaling limits.
- Separation of source-system failures from downstream consumer failures.

### Cost and performance

Understand how query scans, slots, storage classes, data transfer, streaming ingestion, worker capacity, and regional placement can affect costs. For each optimization, look at the workload before assuming the change is beneficial.

## 8. Exam-style reasoning exercises

These are **original study prompts**, not official or recalled exam questions. Instead of treating answers as fixed product-name mappings, write down assumptions and explain your choice.

**1. Analytical queries are getting expensive.** A large date-partitioned BigQuery table is scanned repeatedly for weekly reporting. Which evidence would you inspect before adjusting the partition key, clustering fields, query design, or reservation configuration?

**2. Events arrive out of order.** A Dataflow pipeline aggregates user activity. How do event time, watermarks, windows, and triggers interact? What happens to late events?

**3. Duplicate messages cause side effects.** A Pub/Sub subscriber sends notifications and may receive messages more than once. Where should idempotency be enforced, and what does enabling exactly-once delivery change?

**4. A database needs business continuity.** A Cloud SQL application requires automatic failover and the ability to recover from an accidental destructive update. Why are high availability and point-in-time recovery both relevant?

**5. A Spark migration has operational constraints.** A team needs to move existing Hadoop/Spark jobs to Google Cloud. What determines whether Dataproc or a redesigned Beam/Dataflow pipeline is a more reasonable first approach?

**6. Customer data requires isolation.** A shared analytical platform serves multiple tenants. How do datasets, IAM, row-level security, and audit logging address different aspects of the problem?

**7. A pipeline claims success but data is stale.** What metrics and validation checks would you add beyond worker health and job completion status?

**8. A model needs daily training.** What roles could Cloud Composer, BigQuery, Vertex AI, and Cloud Storage play? Which component owns orchestration, preparation, training, and artifacts?

**9. Global relational consistency is required.** Which workload characteristics justify evaluating Spanner rather than Cloud SQL or Bigtable?

**10. An archive is rarely accessed.** How would you choose a Cloud Storage class after accounting for retrieval charges, minimum durations, and operational recovery requirements?

## 9. Practice questions, labs, and references

**Start with the official material:**

- [Google Cloud Professional Data Engineer certification and exam guide](https://cloud.google.com/learn/certification/data-engineer)
- [Google Cloud Data Engineer learning path](https://www.cloudskillsboost.google/paths/16/)
- [Google Cloud sample questions](https://cloud.google.com/learn/certification/data-engineer)
- [BigQuery documentation](https://cloud.google.com/bigquery/docs)
- [Dataflow documentation](https://cloud.google.com/dataflow/docs)
- [Dataproc documentation](https://cloud.google.com/dataproc/docs)
- [Pub/Sub documentation](https://cloud.google.com/pubsub/docs)

**Supplementary practice resources:**

- [DailyDebian free PDE practice questions](https://dailydebian.com/blogs/practice-questions/google-professional-data-engineer-practice-questions). Added during the October 2026 revision. The site advertises 87 free questions with explanations, alongside optional larger collections.

- [ExamPrepper PDE questions](https://www.examprepper.co/exam/10/1). This was among the community resources in my original notes; verify question freshness and explanations.

- [Udemy PDE practice tests](https://www.udemy.com/). Course offerings, names, and quality change, so prefer a current listing over an expired coupon or a dated exam-version claim.

Third-party question banks can help reveal knowledge gaps, but they can also contain outdated or oversimplified answers. I would use them to practice reasoning, then verify disputed details in the official documentation.

## 10. A final study checklist

Before considering myself ready, I would want to be comfortable explaining, without looking at notes:

- When to choose BigQuery, Cloud SQL, Spanner, Bigtable, and Cloud Storage.
- Why partitioning, clustering, and query design influence BigQuery cost and performance.
- How Dataflow event-time processing handles windows, triggers, watermarks, and late data.
- How Pub/Sub delivery, ordering, retries, and idempotency fit together.
- When Dataproc is a good fit for existing Spark or Hadoop workloads.
- How to orchestrate dependable pipelines using Cloud Composer.
- How data engineers use BigQuery ML and Vertex AI without confusing training with serving.
- How IAM, row/column controls, metadata, classification, and key management protect data.
- How to investigate a pipeline that is available but producing incorrect or stale results.
- How service selection changes when latency, scale, cost, governance, and operational maturity differ.

This is the reference I wanted when assembling my initial study notes: broad enough to orient a full preparation plan, but organized so individual topics are easy to revisit. It is not a replacement for hands-on labs, official objectives, or experience with production data systems. The most useful preparation, in my view, is being able to explain a decision and its limitations rather than recalling a product name in isolation.
