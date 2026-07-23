# GCC Data Engineering Interview Questions by Company

Curated questions from real interview experiences at top Global
Capability Centers (GCCs) with strong data engineering teams. Sourced
from Glassdoor, AmbitionBox, LeetCode Discuss, and candidate blogs.

---

## LSEG (London Stock Exchange Group)

### Interview Process
- **Rounds:** HR screen → Technical assessment (SQL + coding) → 2-3
  technical rounds → Managerial/behavioral
- **Focus areas:** SQL, Python, cloud (AWS/Azure), data pipelines,
  financial domain knowledge is a plus

### Common Questions

**SQL & Data Modeling**
- Write a query to find the 2nd highest salary in each department.
- Explain SQL vs NoSQL databases — when would you choose one over the
  other?
- What is data normalization? Why is it important?
- Design a data model for a financial trading system (orders, trades,
  settlements).

**Data Pipelines & ETL**
- Describe a data pipeline you have built. What technologies did you
  use?
- Explain ETL and its importance in a financial data context.
- How do you ensure data quality in your pipelines?
- How do you handle data security and GDPR compliance?

**Cloud & Tools**
- What is your experience with AWS or Azure?
- How would you migrate an on-premises data warehouse to the cloud?
- Explain your approach to optimizing a slow-running query.

**Behavioral**
- Tell me about a data project that did not go as expected.
- How do you handle cross-team stakeholder requirements?

> [!NOTE]
> DE roles at LSEG focus on pipeline architecture, Python/SQL, and cloud
> migration experience. Financial domain knowledge (market data, trading
> systems) is a strong plus.

---

## Tesco

### Interview Process
- **Rounds:** HR screen → Coding assessment → 2-3 technical rounds →
  Managerial → HR
- **Focus areas:** SQL, Python, Spark, cloud (GCP/AWS), retail domain
  knowledge

### Common Questions

**SQL & Analytics**
- Write a query to find the top 3 products by revenue per category in
  the last quarter.
- Given a transactions table, calculate month-over-month sales growth
  for each store.
- Explain window functions — how would you use `LAG`/`LEAD` for
  retention analysis?

**Data Engineering**
- How would you design a data pipeline for real-time inventory updates
  across 1000+ stores?
- Explain batch vs stream processing. When would you use Kafka vs
  batch ETL?
- How do you handle schema evolution in a data lake?
- Describe your experience with Spark optimizations (shuffle, joins,
  partitioning).

**System Design**
- Design a system to process and analyze customer clickstream data for
  personalization.
- How would you architect a data platform for a retail business with
  multiple sales channels?

**Behavioral**
- How have you contributed to cost optimization in cloud data
  infrastructure?
- Describe a time you resolved a data quality issue that was affecting
  business decisions.

> [!NOTE]
> Retail domain understanding — supply chain, inventory, pricing — is a
> strong differentiator. Tesco's tech hub is one of the largest retail
> technology centers globally.

---

## Flipkart

### Interview Process
- **Rounds:** Initial screen → Technical assessment (SQL + logical
  reasoning) → 3-4 technical rounds → Hiring manager → HR
- **Focus areas:** SQL, Spark, Kafka, data modeling, DSA, system
  design at petabyte scale

### Real Questions from Candidate Experiences

**Round 1 — Spark / Machine Coding**
- Given 4 nested JSON files representing tables, write a Spark program
  to join them and produce a denormalized result.
- Explain Spark optimizations: caching, broadcast join, OOM error
  handling.
- Write PySpark code to handle skewed joins.

**Round 2 — Data Modeling & SQL**
- Design a comprehensive data model for a cricket tournament (teams,
  players, matches, scores, stadiums, multiple leagues).
- Derive cumulative score of a player across all matches.
- Write complex SQL queries on the data model (window functions,
  aggregations, self-joins).
- Explain OLAP vs OLTP systems and when each is appropriate.

**Round 3 — Data Pipelines & Architecture**
- How would you process real-time order data from Kafka topics?
- Explain Spark dynamic allocation, caching strategies, join
  optimizations.
- Walk through your approach to designing a scalable data pipeline for
  an e-commerce platform.
- How do you handle late-arriving data in streaming pipelines?

**Round 4 — Behavioral**
- Tell me about a challenging data problem you faced and how you
  solved it.
- How do you work with cross-functional teams (data science, product,
  engineering)?
- Describe a time you proposed an innovative data solution that was
  adopted.

> [!TIP]
> Flipkart DE interviews have a strong system design component with
> e-commerce context. Practice designing for petabyte-scale data,
> real-time personalization, and supply chain analytics.

### Resources
- [Flipkart Data Engineer II experience (LeetCode)](https://leetcode.com/discuss/interview-experience/5147858/Flipkart-or-Data-Engineer-II-or-Bangalore-or-Offer)

---

## Walmart Global Tech

### Interview Process
- **Rounds:** Screening call → Technical 1 (DSA + SQL) → Technical 2
  (Data Modeling/System Design) → Techno-Managerial → Director round →
  HR
- **Focus areas:** DSA, Spark, SQL, Kafka, Java/Python, system design,
  cloud (Azure/AWS/GCP)

### Real Questions from Candidate Experience (DE-3 / Senior Level)

**Round 1 — Screening (45 min)**
- Walk through your projects and tech stack.
- Why do you want to work at Walmart?
- Discuss experience with Kafka, Spark, ETL, data lineage.

**Round 2 — DSA + SQL + Big Data (90 min)**
- **DSA:** Minimum number of coins to make change (greedy/DP).
- **DSA:** Partition a linked list around a value `x`.
- **SQL:** Find nth highest salary per department using `DENSE_RANK`.
  Why `DENSE_RANK` over `RANK`?
- **Spark:** How Airflow Kubernetes works (pod concepts, scheduler,
  worker).
- **Spark:** Troubleshoot a slow Spark job — what steps would you
  take?
- **Cloud:** Write Python code using boto3 to upload Parquet files to
  S3.

**Round 3 — System Design + Data Modeling (105 min)**
- **System Design:** Design Mixpanel (event-driven analytics platform)
  — load balancer, request handling, event capture from web/iOS/Android
  apps.
- **Spark Coding:** Read data from Delta Lake (S3) and perform upsert
  based on primary key.
- **Optimization:** Skewed join, broadcast join, CBO, `repartition` vs
  `coalesce`.
- **Optimization:** Spark Tungsten & Catalyst Optimizer internals.
- **Java:** Write garbage collection using GC collector thread.
- **Java:** Multithreading — write synchronization using semaphores.
- **Java:** Serialization vs deserialization, `transient` keyword.
- **Data Modeling:** Snowflake vs Star schema, normalize concepts,
  SCD Type 2.
- **Agile:** Why is Agile preferred over Waterfall?

**Round 4 — Techno-Managerial (70 min)**
- Explain your project on data lineage (Datahub + Spark Lineage).
- Batch vs stream processing with Spark.
- Cost optimization strategies in the cloud.
- Spark monitoring and performance management.
- How do you manage multiple tasks using Agile/Scrum?

**Round 5 — Director (45 min)**
- Core Walmart principles and values.
- Tell me about a challenging situation and how you handled it.
- Presto vs Spark architecture differences.
- Can Presto work with near-real-time (streaming) data?
- What is Avro format and its significance in Delta tables?
- What do you think about data uncertainty?

**Round 6 — HR (30 min)**
- Strengths and weaknesses.
- Why should we hire you?
- What inspires you to join Walmart?
- Salary discussion.

> [!TIP]
> Walmart DE interviews are thorough — expect 5-6 rounds. Java/Python
> proficiency, deep Spark internals knowledge, and system design
> (event-driven platforms) are heavily tested.

### Resources
- [Detailed Walmart DE interview experience (Preplaced)](https://www.preplaced.in/blog/data-engineer-interview-experience-walmart)
- [Walmart DE questions on DataEngPrep](https://www.dataengprep.tech/interview/walmart-data-engineer-interview-questions)

---

## Target

### Interview Process
- **Rounds:** Initial HR screen → Technical assessment (DSA + SQL) →
  2-3 technical rounds (design-lite, project deep dive) → Behavioral
- **Focus areas:** SQL, Python/Java, data modeling, retail metrics,
  pipelines (batch + streaming)

### Common Questions

**SQL & Data Modeling**
- Write a query to find the top 5 products by revenue in the last 30
  days.
- Explain fact tables vs dimension tables with a retail example
  (orders, inventory, promotions).
- How do you model a slowly changing dimension for product prices?
- Design a star schema for an e-commerce analytics dashboard.

**Data Engineering**
- Complete end-to-end flow design for data integration from multiple
  sources (on-prem, cloud, event-based).
- How do you handle schema evolution in a data lake?
- Batch vs streaming — when would you use each for retail data?
- How do you ensure idempotency in your data pipelines?

**Python & Coding**
- Write a Python function to calculate a 7-day moving average from a
  time series.
- Given a dataset with 20% missing values in a key column, how would
  you handle it?
- Implement a solution for the 3-sum problem.

**System Design (Design-Lite)**
- Design a data platform for inventory availability tracking across
  thousands of stores.
- How would you build a real-time promotion effectiveness dashboard?

**Behavioral**
- Tell me about a data project that had significant business impact.
- How do you prioritize between data quality, latency, and cost?

> [!NOTE]
> Target's GCC focuses on retail-tech — supply chain, pricing,
> promotions, personalization, and search. DSA may screen you, but
> project depth and retail context carry equal weight. Prepare retail
> metrics (conversion, inventory availability, order fulfillment).

---

## Lowe's

### Interview Process
- **Rounds:** HR screen → Technical assessment → 2-3 technical rounds
  (coding, data pipelines, system design) → Managerial
- **Focus areas:** Spark, SQL, Python/Java, cloud (GCP), data formats
  (Parquet/Avro), Kafka

### Common Questions

**SQL & Data Modeling**
- Write a query to calculate cohort retention for online vs in-store
  customers.
- Given clickstream data, design a schema for a two-year analytics
  retention period at 600M events/day.
- What are the differences between Parquet and Avro file formats?
- Explain Snowflake vs Star schema with a home-improvement retail
  example.

**Spark & Big Data**
- Explain the difference between `DataFrame` and `Dataset` APIs. When
  would you use each?
- What is the role of Kafka in a data pipeline? How do you handle
  reprocessing?
- How do you handle schema evolution in Avro-based pipelines?
- Explain caching vs persisting in Spark — when would you use each?
- Compare Spark's `repartition` vs `coalesce` with real use cases.

**System Design**
- Design a clickstream analytics solution storing raw data for 2 years
  at 600M events/day — keep costs in mind.
- Design a data pipeline for real-time omnichannel order tracking.

**Python & Coding**
- Implement the longest increasing subsequence (LeetCode medium).
- Write a Python function to clean and deduplicate a customer dataset.

**Behavioral**
- Describe a time you optimized a data pipeline that reduced cost or
  runtime.
- How do you communicate technical tradeoffs to non-technical
  stakeholders?

> [!TIP]
> Lowe's interviews emphasize Spark internals and file format tradeoffs
> (Parquet vs Avro). Expect at least one system design question around
> clickstream or omnichannel retail data at scale.

### Resources
- [Lowe's DE interview guide (InterviewQuery)](https://www.interviewquery.com/interview-guides/lowes-data-engineer)

---

## Boeing

### Interview Process
- **Rounds:** HR screen → Technical assessment → 2-3 technical rounds
  (SQL, Python, data architecture) → Managerial/Leadership
- **Focus areas:** SQL, Python, data pipelines, data warehousing,
  aerospace domain is a plus but not required

### Common Questions

**SQL & Data Warehousing**
- Write a query to find employees with the highest salary in each
  department.
- Explain ETL vs ELT — when would you choose one approach over the
  other?
- How do you design a data warehouse from scratch for a manufacturing
  domain?
- What is the difference between a data lake and a data warehouse?

**Data Engineering**
- Describe a complex ETL pipeline you built from scratch. What
  challenges did you face?
- How do you ensure data quality in mission-critical pipelines?
- Explain your approach to handling slowly changing dimensions.
- How do you manage data lineage and governance?

**Python & Coding**
- Write a script to parse and transform a large CSV/JSON dataset for
  loading into a warehouse.
- Given telemetry data from sensors, design a processing pipeline.

**System Design**
- Design a data platform for aggregating and analyzing aircraft
  telemetry data from thousands of flights.
- How would you handle real-time vs batch data from disparate
  manufacturing systems?

**Behavioral**
- Tell me about a time you had to debug a production data issue under
  time pressure.
- Why do you want to work in the aerospace industry?

> [!NOTE]
> Boeing's GCC work spans manufacturing analytics, supply chain
> optimization, and flight telemetry processing. Safety and data quality
> are paramount — always mention error handling, monitoring, and
> compliance in your answers.

### Resources
- [Boeing DE interview guide (InterviewQuery)](https://www.interviewquery.com/interview-guides/boeing-data-engineer)

---

## Airbus

### Interview Process
- **Rounds:** HR screen → Technical round (SQL, Python, data modeling)
  → Managerial round → (sometimes) Take-home assignment
- **Focus areas:** SQL, Python, data pipelines, cloud deployment,
  aerospace/manufacturing context

### Common Questions

**SQL & Data Modeling**
- Write a query to find the top 5 customers by revenue in the last
  quarter.
- Explain data normalization with an aerospace example (e.g., parts
  catalog).
- Design a data model for a global supply chain tracking aircraft part
  inventory across multiple factories.
- What is the difference between a LEFT JOIN and INNER JOIN? Give a
  real-world example.

**Data Engineering**
- How would you design a data pipeline to ingest and process sensor
  data from aircraft engines?
- Explain your approach to data quality monitoring in a production
  pipeline.
- How do you handle late-arriving or out-of-order data in streaming
  pipelines?
- What is your experience with cloud data platforms (AWS/GCP/Azure)?

**Python & Tools**
- Write a Python function using Pandas to calculate a rolling
  aggregate (e.g., 7-day moving average).
- Describe your experience with Airflow or similar orchestrators.
- How would you build a BI dashboard for tracking manufacturing KPIs?

**System Design**
- Design a Skywise-like platform (Airbus's open data platform) for
  airline operational data sharing.
- How would you architect a real-time telemetry processing system for
  aircraft in flight?

**Behavioral**
- How do you approach a problem when requirements are ambiguous?
- Tell me about a time you collaborated with cross-functional teams
  (engineering, manufacturing, analytics).

> [!TIP]
> Airbus' Skywise platform is central to their data strategy. The
> interview emphasizes data quality, safety, and handling large-scale
> telemetry. Mention how you'd monitor pipeline health and ensure
> compliance.

### Resources
- [Airbus DE interview guide (InterviewQuery)](https://www.interviewquery.com/interview-guides/airbusgroup-data-engineer)

---

## Quick Topic Comparison

| Topic | LSEG | Tesco | Flipkart | Walmart | Target | Lowe's | Boeing | Airbus |
|---|---|---|---|---|---|---|---|---|
| SQL / Window Functions | High | High | High | High | High | High | High | High |
| Python / PySpark | Medium | High | High | High | High | High | Medium | Medium |
| DSA (LeetCode medium) | Low | Medium | Medium | High | Medium | Medium | Low | Low |
| Data Modeling | Medium | Medium | High | High | High | High | Medium | Medium |
| System Design | Low | Medium | High | High | Medium | High | Medium | Medium |
| Cloud (AWS/Azure/GCP) | High | High | Medium | High | High | High | Medium | Medium |
| Kafka / Streaming | Medium | Medium | High | High | Medium | High | Low | Low |
| Domain Knowledge | Finance | Retail | E-com. | Retail | Retail | Home Imp. | Aerospace | Aerospace |
| Rounds | 3-4 | 3-4 | 4-5 | 5-6 | 3-4 | 3-4 | 3-4 | 3 |
| Difficulty | Moderate | Moderate | Hard | Hard | Moderate | Moderate | Moderate | Moderate |

---

> [!WARNING]
> Questions are sourced from public candidate reports and may not
> reflect current interview cycles. Always cross-check with recent
> Glassdoor/LeetCode posts closer to your interview date.
