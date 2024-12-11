+++
title = "Preparation for Google Cloud: Professional Cloud Architect (PCA) Exam"
description = "My journey on how I prepared for the Google PCA exam, resources I used, insights and practical tips."
date =  "2024-12-11"
draft = false
toc = true
categories = ["gcp", "kubernetes"]
tags = ["gcp", "kubernetes"]
image = "gcp_pca.png"
author = "Fabio M. Lopes"
+++

If you're considering a career in cloud computing, particularly with Google Cloud Platform (GCP), pursuing the Google Cloud Professional Cloud Architect (PCA) certification is a demanding yet rewarding path. By adopting the right learning approach and training plan, you can master key elements of GCP, including enterprise cloud strategies, solution design, and architectural best practices to achieve impactful business results. In this article, I’ll share my journey, insights, and practical tips to help you succeed. All the links mentioned are referred at the end of the post.


## Required Experience and Skills

While there are no formal prerequisites for the Google Professional Cloud Architect exam, Google recommends significant experience. Specifically, candidates should possess:

* **Extensive Cloud and Networking Experience:** At least three years of industry experience designing and developing networks, coupled with at least one year specifically designing and managing solutions using Google Cloud Platform (GCP).
* **Cloud Architecture Design Proficiency:**  Experience designing and planning cloud architectures from the ground up, either through real-world projects or extensive practice.  This includes understanding the technical implementation of managing and provisioning cloud infrastructure.
* **Security and Governance Expertise:**  While not requiring a dedicated cybersecurity certification, candidates must demonstrate strong familiarity with designing secure and governance-compliant architectures.
* **Solution Analysis and Optimization:**  The ability to analyze and optimize technical and business solutions, considering both technical and business needs.
* **Real-World Implementation and Reliability:**  Successful candidates will have managed the implementation of cloud architectures in a real-world setting and demonstrate a strong understanding of how to ensure solution and operations reliability.


## Ideal Candidates

The Google Professional Cloud Architect certification is an advanced credential best suited for IT professionals with substantial experience.  Ideal candidates include:

* Network and Cloud Administrators
* Network Solutions Architects
* Network and Cloud Architects

These roles typically require several years of experience to develop the necessary skills and knowledge.


## Is the Certification Worth It?

For most administrators and network architects, the Google Professional Cloud Architect certification offers significant value.  Its benefits extend beyond career advancement:

* **Advanced Skill Validation:**  The certification validates critical skills such as creative problem-solving, critical thinking regarding network operations, and the ability to quickly adapt and find solutions.
* **Career Advancement:** It's particularly valuable for IT professionals aiming for senior roles, demonstrating a mastery of GCP.  Even early-career professionals can benefit, using it as a roadmap for skill development.


## Using the Certification for Skill Development and Validation

The Google Professional Cloud Architect certification serves two key purposes:

**1. Skill Development:** The certification acts as a benchmark, highlighting the skills necessary to become a proficient cloud architect.  It provides a structured learning path, guiding individuals to master the skills required to leverage GCP's capabilities effectively and solve complex business problems.  This includes analyzing business objectives, understanding existing technological infrastructure, and designing cost-effective, reliable network architectures.

**2. Skill Validation:** For experienced professionals already proficient in GCP, the certification serves as validation of their existing expertise.  It provides formal recognition of their ability to design, implement, and manage complex cloud solutions.  This is beneficial for career progression and demonstrating competency to potential employers.


## My Starting Point
**Experience**: 20 years of commercial IT experience — network, sysadmin, ops, architecture, project management; 2 years with AWS and Azure as an architect; 2 months of GCP experience.

**Certifications**: AWS Certified Solutions Architect Professional (1 year ago), Microsoft Certified Azure Solutions Architect Expert (2 years ago), Certified Kubernetes Administator (3 years ago).


## Learning Process

> ### TL;DR
> - Used Skills Boost Cloud Architect Path
> - Prioritized Labs and Quizzes
> - Familiarized with the 4 case studies
> - Complemented with Ranga Karanam's Udemy Course
> - Familiarized with Google Service Comparison Chart
> - Reviewed with Sebastian Hooker's Exam Guide
> - Did many practice exams

I studied for about three months, although not every day, with some gaps that lasted more than a week. I started with **Google Cloud Skills Boost**, since it was a prerequisite for an exam voucher, provided due to a partnership between my company and Google. I did the Cloud Architect Learning Path, comprised of 18 courses. My study style is very practical, so I skipped most of the videos from the courses and focused on the labs and quizzes. I also have previous experience with AWS and Azure, so many of the concepts are the same between those cloud providers. What I noticed was that, between the 18 required courses for completing the learning path, there is a lot of overlapping. Many of the labs were almost the same, or even too basic. The evaluation system was also a hassle, I had problems on some of them, wasting time trying to figure out what was different to make it recognize the task as completed instead of effectively learning anything. From what I read, that is a common issue that many people encounter with the platform.

One crucial takeaway from the exam guide is the importance of the case studies. Before the test, I thoroughly reviewed all four case studies to save time during the exam itself. With only 2 hours to complete the test and potentially lengthy questions, it’s essential to be well-prepared. I strongly recommend leveraging the information in the case studies to optimize your efficiency and make the most of your time during the exam.

After that, I went on to Ranga Karanam's Udemy Course. It had a good rating on the platform, and I personally like Udemy as it is easy to use. Since this was already my second take on all of the content, I listened to the material while doing other stuff, without focusing completely on it. To help me trace a parallel between GCP's services and the equivalent ones on AWS and Azure, I spent some time studying the comparison chart, provided by Google itself.

Next, I started to review the content and found an excellent summary from Sebastian Hooker, which I read completely and looked deeply on subjects I felt I didn't know very well. I also went through some excellent prep notes I found online, provided freely by [Ammett Williams](https://www.linkedin.com/in/ammett).

Then it was time to do some practice tests. I started with Ditectrev's ACE Practice Test, since PCA and ACE have a great deal of overlap and it was free. Then i went to ExamPrepper, which also has some free content, and on the last stretch I used Skillcertpro. I felt very confident after doing so many practice questions, but that strategy always worked for me on my previous certifications. PCA will be my 20th so far. The exam is scheduled for next month, but I wanted to write this guide before, since it also helped me organize everything I needed to cover for the exam. The only paid resources were the Udemy course and Skillcertpro.


## Key Skills for PCA

- Design and plan a cloud solution architecture
- Manage and provision the cloud solution infrastructure
- Design for security and compliance
- Analyze and optimize technical and business processes
- Manage implementations of cloud architecture
- Ensure solution and operations reliability 


## Minimum Services to Know

- **Infra & Ops**: [Cloud Operations](https://cloud.google.com/products/operations), [Google Kubernetes Engine](https://cloud.google.com/kubernetes-engine/docs/concepts/kubernetes-engine-overview), [Cloud Logging](https://cloud.google.com/logging/docs/overview), [Persistent Disks](https://cloud.google.com/compute/docs/disks/persistent-disks), [Managed Instance Group](https://cloud.google.com/compute/docs/instance-groups), [Cloud KMS](https://cloud.google.com/kms/docs/key-management-service), [Organization Policies](https://cloud.google.com/resource-manager/docs/organization-policy/overview), [Cloud Storage](https://cloud.google.com/storage/docs), [Google Compute Engine](https://cloud.google.com/compute/docs/instances), [Cloud IAM](https://cloud.google.com/iam/docs/concepts)
- **Network**: [VPC](https://cloud.google.com/vpc/docs/overview), [Shared VPC](https://cloud.google.com/vpc/docs/shared-vpc), [VPC Peering](https://cloud.google.com/vpc/docs/vpc-peering), [VPC Flow Logging](https://cloud.google.com/vpc/docs/using-flow-logs), [Serverless VPC Access](https://cloud.google.com/vpc/docs/serverless-vpc-access), [Cloud NAT](https://cloud.google.com/nat/docs/overview#:~:text=Cloud%20NAT%20is%20a%20distributed,VMs%20without%20external%20IP%20addresses.), [Cloud VPN](https://cloud.google.com/network-connectivity/docs/vpn/concepts/overview#:~:text=Cloud%20VPN%20securely%20connects%20your,it%20travels%20over%20the%20internet.), [Cloud Interconnect](https://cloud.google.com/network-connectivity/docs/interconnect/concepts/overview)
- **Apps/Dev**: [App Engine](https://cloud.google.com/appengine/docs), [Cloud Build](https://cloud.google.com/build/docs/overview), [Cloud Scheduler](https://cloud.google.com/scheduler/docs/overview), [Cloud Functions](https://cloud.google.com/functions), [Cloud Run](https://cloud.google.com/run/docs/overview/what-is-cloud-run), [Firebase](https://firebase.google.com/docs), [Cloud Pub/Sub](https://cloud.google.com/pubsub/docs/overview)
- **Data**: [BigQuery](https://cloud.google.com/bigquery/docs/introduction), [Cloud Bigtable](https://cloud.google.com/bigtable/docs/overview), [Cloud Dataproc](https://cloud.google.com/dataproc/docs/concepts/overview), [Cloud Firestore](https://cloud.google.com/firestore), [Cloud SQL](https://cloud.google.com/sql/docs/?utm_source=ext&utm_medium=partner&utm_campaign=CDR_pve_gcp_4words_4words_&utm_content=-), [Cloud Spanner](https://cloud.google.com/spanner/docs/?utm_source=ext&utm_medium=partner&utm_campaign=CDR_pve_gcp_4words_4words_&utm_content=-)
- **Processes**: [Organization Best practices](https://cloud.google.com/architecture/identity/best-practices-for-planning), [GKE Best Practices](https://cloud.google.com/kubernetes-engine/docs/best-practices/networking), [IAM Best practices](https://cloud.google.com/iam/docs/using-iam-securely), [Troubleshooting GKE](https://cloud.google.com/kubernetes-engine/docs/troubleshooting), [Cloud Storage Best practices](https://cloud.google.com/storage/docs/best-practices)


## Case Studies

The exam will probably have two case studies that might take a lot of time and comprise most of the questions, so it is crucial to study them before the exam, and the official guide provides the description of each scenario:

- [EHR Healthcare](https://services.google.com/fh/files/blogs/master_case_study_ehr_healthcare.pdf)
- [Helicopter Racing League](https://services.google.com/fh/files/blogs/master_case_study_helicopter_racing_league.pdf)
- [Mountkirk Games](https://services.google.com/fh/files/blogs/master_case_study_mountkirk_games.pdf)
- [TerramEarth](https://services.google.com/fh/files/blogs/master_case_study_terramearth.pdf)


## Opinion About the Exam
The exam is challenging, requiring both a deep understanding of low-level details—such as command-line parameters for tools like gcloud and gsutil—and a solid grasp of high-level concepts across many GCP products.

Having previously passed the Kubernetes CKA exam, which is an “open book” format, I can draw some comparisons. For the CKA, you’re allowed to refer to documentation on kubernetes.io, which makes the exam focused more on practical problem-solving than rote memorization. Although the CKA was difficult, I was well-prepared and finished it significantly faster than the allotted time. There’s little opportunity to rely heavily on documentation during the test, so it’s crucial to have a strong foundational knowledge. The documentation is best used for quick lookups or copying manifest templates to save time. Overall, the CKA was an enjoyable experience because it emphasized real-world tasks. Working directly in the command line to solve problems provided a sense of accomplishment, and it avoided requiring you to memorize information that’s readily available online.

In contrast, the GCP PCA exam is very different. That is also true for all other AWS and Azure exams I took. It requires memorization of details you'd typically copy/paste in your daily work rather than hands-on problem-solving. Without practical, scenario-based tasks, it’s harder to gauge whether you're fully equipped to handle real challenges on GCP. This difference makes you feel less confident about how well the exam aligns with practical skills needed for day-to-day work in the cloud. 


## Summary

In short, my journey to prepare for the Google Cloud Professional Cloud Architect certification involved a focused, three-month study plan leveraging a blend of free and paid resources. I prioritized hands-on labs and quizzes from Google Cloud Skills Boost, supplemented by Ranga Karanam's Udemy course for broader conceptual understanding and Sebastian Hooker's concise exam guide for focused review. Mastering the four official case studies proved invaluable, as did extensive practice exams. While the exam itself demands significant memorization, my prior cloud experience and targeted approach helped me feel confident going in. I hope this detailed account of my preparation, including the resources and strategies I used, provides a helpful roadmap for your own PCA journey. Remember to prioritize hands-on experience and a deep understanding of the case studies – they are key to success.


## Resources

Google Cloud Skills Boost - Cloud Architect Learning Path: https://www.cloudskillsboost.google/paths/12/

Exam Guide: https://cloud.google.com/learn/certification/guides/professional-cloud-architect/

Ranga Karanam's Udemy Google PCA Course: https://www.udemy.com/course/google-cloud-professional-cloud-architect-certification

Service Comparison Chart: https://cloud.google.com/docs/get-started/aws-azure-gcp-service-comparison

Sebastian Hooker's Full Exam Guide: https://www.sebhook.com/2024/08/28/google-cloud-professional-cloud-architect-pca-full-exam-guide/

Ditectrev's ACE Practice Test: https://github.com/Ditectrev/Google-Cloud-Platform-GCP-Associate-Cloud-Engineer-Practice-Tests-Exams-Questions-Answers

ExamPrepper: https://www.examprepper.co/exam/3/1

Skillcertpro practice test: https://skillcertpro.com/product/google-cloud-certified-professional-cloud-architect-practice-exam-test/

Prep Notes by Ammett Williams: https://drive.google.com/file/d/1_UfKnzxodTTk5CuwT0ScSmXegtmgpV5v/view