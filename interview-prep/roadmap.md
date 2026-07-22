# Data Engineering Interview Prep Roadmap (2026)

A structured topic list covering repo technologies, current industry trends, and commonly asked DSA questions for data engineers.

---

## 1. SQL & Data Modeling

Appears in **every** data engineering interview. Most tested skill across all companies.

### SQL Core
- Window functions vs GROUP BY — `ROW_NUMBER`, `RANK`, `LEAD`/`LAG`, `SUM() OVER(PARTITION BY ...)`
- CTEs and recursive queries (org charts, graph traversal)
- Joins: INNER, LEFT, RIGHT, FULL OUTER, anti-joins (`LEFT ... WHERE ... IS NULL`)
- Dedup patterns: `ROW_NUMBER()`, `DISTINCT ON`, self-joins
- `WHERE` vs `HAVING`, subqueries vs joins
- NULL handling: `COALESCE`, `NULLIF`, three-valued logic

### Query Optimization
- `EXPLAIN ANALYZE` — identify full table scans, hash joins, spills to disk
- Partitioning strategy (date-based, cardinality considerations)
- Targeted indexing vs over-indexing
- Materialized views and pre-aggregation
- Avoiding `SELECT *`, limiting shuffle in distributed engines

### Data Modeling
- Normalization (1NF, 2NF, 3NF) vs denormalization
- Star schema vs snowflake schema — when to use which
- Fact tables (transactional, snapshot, accumulating) vs dimension tables
- Slowly Changing Dimensions: Type 1 (overwrite), Type 2 (versioned rows), Type 3 (limited history)
- Data Vault modeling (hubs, links, satellites) for enterprise warehouses
- Grain definition — "one row per what?"

### Practice Questions
- Find the second highest salary per department
- Find duplicates and return full rows
- Calculate running totals and moving averages
- Self-join to find consecutive records
- Gap-and-island problems

---

## 2. Core Repo Technologies

### Apache Spark / PySpark
- Transformations (lazy) vs actions (trigger execution)
- Catalyst optimizer and Tungsten execution engine
- Shuffle — what triggers it, how to minimize it
- Partitioning: `repartition()` vs `coalesce()`, partition pruning
- Broadcast joins vs sort-merge joins
- Skew handling: salting, repartitioning
- Accumulators and broadcast variables
- Spark SQL vs DataFrame API trade-offs
- Memory management: execution vs storage memory, `spark.memory.fraction`
- Serialization: Kryo vs Java
- Checkpointing for lineage truncation
- **Resources**: `apache-spark-pyspark/notes.md`, `spark-concepts-execution-architecture.md`

### Apache Kafka
- Partitions, offsets, consumer groups, rebalancing
- At-least-once vs exactly-once vs at-most-once semantics
- Kafka Connect (source/sink connectors)
- Kafka Streams vs external consumers
- Topic design: partition count, replication factor, retention
- Key-based partitioning for ordering guarantees
- Dead letter queues for poison messages
- **Resources**: `apache-kafka/notes.md`

### Apache Flink
- Windowing: tumbling, sliding, session windows
- Watermarks — event-time vs processing-time, late data handling
- State: keyed state, operator state, state backends
- Exactly-once with checkpointing and 2PC sinks
- CEP (Complex Event Processing)
- Flink SQL vs DataStream API
- **Resources**: `apache-flink/notes.md`, `kafka-to-flink-local-setup.md`

### Apache Iceberg
- Architecture: catalog, metadata, manifest files
- CoW (Copy-on-Write) vs MoR (Merge-on-Read) — trade-offs
- Hidden partitioning and partition evolution
- Time travel and snapshot isolation
- Schema evolution (add, rename, drop columns safely)
- Compaction: bin-packing, sort compaction
- Equality deletes vs position deletes
- **Resources**: `apache-iceberg/notes.md`

### AWS Glue
- Crawlers and data catalog
- ETL jobs: PySpark extensions, custom transforms
- Job bookmarks (incremental processing)
- Blueprints and workflows
- Glue DataBrew for data preparation

### Athena
- Serverless query engine on S3
- Partitioning strategy for cost and performance
- CTAS (Create Table As Select) and UNLOAD
- Columnar formats (Parquet, ORC) for performance
- Query execution: bytes scanned billing model

### Redshift
- Distribution styles: KEY, EVEN, ALL, AUTO
- Sort keys: compound vs interleaved
- Redshift Spectrum for querying external data
- VACUUM and ANALYZE for maintenance
- Concurrency scaling and workload management (WLM)
- RA3 nodes and managed storage

### EMR
- Cluster management: instance groups, instance fleets
- Spot instances for cost optimization
- EMR Serverless
- EMR Notebooks vs Jupyter
- Integration with Hive, Spark, Presto/Trino

---

## 3. Modern Data Stack (Trending 2026)

### ELT over ETL
- ELT is dominant: raw data lands first, transform in warehouse
- ETL still used for PII scrubbing, compliance, very large volumes
- Preserve raw data for reprocessing and audit

### dbt (data build tool)
- SQL-based transformation logic
- Incremental models, materializations (table, view, incremental, ephemeral)
- Testing: unique, not-null, accepted values, custom tests
- Documentation and lineage graphs
- Packages and macros

### Orchestration (Airflow / Dagster)
- DAG design patterns, task dependencies
- Idempotency — "what happens if this job runs twice?"
- Backfills and date-partitioned runs
- SLA handling, retries, alerting
- Sensor vs operator
- XCom for lightweight inter-task data

### Data Quality & Observability
- Great Expectations / Soda for data validation
- Data contracts — schema agreements between producers and consumers
- Data freshness, completeness, accuracy checks
- Lineage tracking (OpenLineage, Marquez)
- SLOs for data pipelines (freshness, correctness)

### Lakehouse Architecture
- Unifying data lakes and warehouses
- Table formats: Iceberg, Delta Lake, Hudi
- Cost benefits: open formats, compute-storage separation
- Schema enforcement on read vs write

### Data Governance
- Data catalogs (AWS Glue, DataHub, Amundsen)
- PII detection and masking
- Access control and column-level security
- Retention policies and GDPR compliance

---

## 4. Cloud & Infrastructure

### Cloud Data Platforms
- **AWS**: S3, Glue, Athena, Redshift, EMR, Kinesis, MSK
- **GCP**: BigQuery, Dataflow, Dataproc, Pub/Sub, Cloud Storage
- **Azure**: Synapse, Data Factory, Databricks, Event Hubs, ADLS
- Know at least one cloud platform in depth

### Cost Optimization
- Compute right-sizing and autoscaling
- Spot/preemptible instances for batch workloads
- Storage tiering (hot/warm/cold)
- Query optimization to reduce bytes scanned
- Reserved capacity vs on-demand

### Infrastructure Basics
- Docker for data pipeline containerization
- Terraform basics for infrastructure as code
- CI/CD for data pipelines (GitHub Actions, GitLab CI)
- Monitoring: CloudWatch, Datadog, Prometheus + Grafana

---

## 5. Streaming & Real-Time

- Batch vs streaming trade-offs and when to use each
- Lambda architecture (batch + speed layers) vs Kappa (stream-only)
- Event-time vs processing-time vs ingestion-time
- Watermarks and late data handling
- Exactly-once in streaming: idempotent sinks, transactional writes
- CDC (Change Data Capture): Debezium, logical replication
- Schema evolution in streaming systems
- Backpressure handling
- Window types: tumbling, sliding, session, global

---

## 6. System Design

Required for senior roles, common for mid-level. Tests architectural thinking.

### Key Design Patterns
- Design a real-time analytics pipeline for an e-commerce platform
- Design a data platform supporting both batch and streaming
- Design a log aggregation system (think: company-wide observability)
- Design a feature store for ML models
- Design a data migration from legacy ETL to modern stack

### Decision Framework
1. Clarify requirements and constraints (throughput, latency, correctness)
2. Choose batch vs streaming vs micro-batch
3. Storage format and partitioning strategy
4. Compute engine selection
5. Orchestration and scheduling
6. Monitoring, alerting, and failure recovery
7. Cost estimation

### Common Scenarios
- Pipeline produces duplicate records — how do you handle it?
- Dashboard shows incorrect numbers — debugging process
- Downstream consumer needs data in 5 minutes but pipeline takes 30 — what do you do?
- Schema change breaks downstream — prevention and recovery
- Handling petabyte-scale data recovery under SLA pressure

---

## 7. Python

### Coding Round Preparation
- DataFrame operations: groupby, merge, pivot, melt, apply
- File I/O: reading/writing CSV, JSON, Parquet, Avro
- String manipulation and regex
- Generators and iterators (memory-efficient processing)
- Decorators and context managers
- Exception handling patterns
- Logging and debugging

### Testing & Best Practices
- pytest for unit testing pipeline logic
- Mocking external dependencies
- Type hints and mypy
- Virtual environments and dependency management

---

## 8. DSA Topics for Data Engineers

Data engineer DSA rounds are typically easier than pure SWE rounds but focus on **practical patterns** relevant to data processing.

### Priority Order by Frequency

#### Arrays & Strings (Highest frequency)
| Pattern | Key Problems |
|---|---|
| Two Pointers | Container With Most Water, 3Sum, Valid Palindrome |
| Sliding Window | Longest Substring Without Repeating Chars, Min Window Substring, Max Sum Subarray of Size K |
| Prefix Sums | Product of Array Except Self, Range Sum Query |
| Kadane's Algorithm | Maximum Subarray (very common) |

#### Hashing
| Pattern | Key Problems |
|---|---|
| Frequency Maps | Top K Frequent Elements, Word Frequency Count |
| Grouping | Group Anagrams, Valid Anagram |
| Two Sum Variants | Two Sum, Three Sum, Four Sum, Subarray Sum Equals K |

#### Linked Lists
| Pattern | Key Problems |
|---|---|
| Fast/Slow Pointers | Detect Cycle, Find Middle of Linked List |
| Reversal | Reverse Linked List, Reverse Pairs |
| Merging | Merge Two Sorted Lists, Merge K Sorted Lists |
| LRU Cache | Design LRU Cache (very common for data eng) |

#### Trees & BST
| Pattern | Key Problems |
|---|---|
| DFS | Maximum Depth, Invert Binary Tree, Validate BST |
| BFS | Level Order Traversal, Binary Tree Right Side View |
| BST Operations | Lowest Common Ancestor, Kth Smallest in BST |
| Construction | Construct from Preorder + Inorder Traversal |

#### Graphs
| Pattern | Key Problems |
|---|---|
| BFS/DFS | Number of Islands, Clone Graph, Number of Provinces |
| Topological Sort | Course Schedule, Alien Dictionary |
| Shortest Path | Dijkstra basics, Network Delay Time |
| Union-Find | Accounts Merge, Number of Connected Components |

#### Dynamic Programming
| Pattern | Key Problems |
|---|---|
| 1D DP | Climbing Stairs, House Robber, Coin Change |
| 2D DP | Longest Common Subsequence, Edit Distance |
| Knapsack | 0/1 Knapsack, Partition Equal Subset Sum |

#### Sorting & Searching
| Pattern | Key Problems |
|---|---|
| Binary Search | Search in Rotated Sorted Array, Find Min in Rotated |
| Merge Sort Logic | Merge Intervals, Insert Interval |
| Heap | Kth Largest Element, Find Median from Data Stream |

### Data-Engineer-Specific DSA Flavors
These problems mirror real data engineering scenarios:

- **Merge K sorted lists/arrays** — relates to partition merging in distributed systems
- **Top K elements with heaps** — frequent items, log analysis, Spark's takeOrdered
- **Running median / streaming statistics** — windowed aggregations
- **Interval merging** — log time ranges, scheduling pipeline runs, merging partitions
- **Matrix BFS/DFS** — grid-based partitioning, connected components
- **String parsing** — log parsing, CSV/JSON tokenization
- **Frequency counting at scale** — distributed counting, MapReduce patterns
- **Deduplication** — finding duplicates in streams or large datasets

### Practice Platforms
- LeetCode (filter by "Top Interview Questions")
- StrataScratch (SQL-specific, real company questions)
- HackerRank (Python + SQL)
- NeetCode.io (curated problem sets by pattern)

---

## 9. Behavioral

Prepare 2-3 stories using the STAR method (Situation, Task, Action, Result).

### Must-Have Stories
- A pipeline that broke — detection, mitigation, root cause, long-term fix
- Explaining a technical decision to a non-technical stakeholder
- Handling conflict with a teammate
- Learning a new technology quickly to meet a deadline
- Pushing back on a requirements change that would compromise data quality

### Common Questions
- What makes a pipeline "production-ready" vs a prototype?
- How do you prioritize when multiple pipelines are failing?
- Describe your approach to the first 90 days on a new team
- How do you handle strict deadlines when quality might be compromised?

---

## Suggested Priority Order

| Phase | Topics | Time |
|---|---|---|
| **1** | SQL + Data Modeling | 1-2 weeks |
| **2** | Spark/PySpark + Kafka | 2 weeks |
| **3** | Python coding + DSA (Arrays, Hashing, Trees) | 2-3 weeks |
| **4** | System Design + Streaming concepts | 1 week |
| **5** | Cloud stack (pick one: AWS/GCP/Azure) | 1 week |
| **6** | Modern stack (dbt, Airflow, data contracts) | 1 week |
| **7** | DSA (Graphs, DP, advanced patterns) | Ongoing |
| **8** | Behavioral prep (2-3 stories) | 2-3 days |

---

## Quick Reference: Repo Navigation

| Topic | File |
|---|---|
| Spark concepts | `apache-spark-pyspark/notes.md` |
| Spark execution architecture | `apache-spark-pyspark/spark-concepts-execution-architecture.md` |
| Kafka fundamentals | `apache-kafka/notes.md` |
| Flink overview | `apache-flink/README.md` |
| Flink + Kafka setup | `apache-flink/kafka-to-flink-local-setup.md` |
| Flink practice roadmap | `apache-flink/practice-roadmap.md` |
| Iceberg architecture | `apache-iceberg/notes.md` |
| Networking basics | `foundations/networking.md` |
| System design & caching | `system-design/notes.md`, `system-design/caching.md` |
| EMR | `emr/notes.md` |
| DSA (to be built) | `data-structures-and-algorithms/` |
