# Foundations Progress

Track core knowledge areas, resource links, and completion status. Update dates as you progress.
Reference `interview-prep/progress-checklist.md` for granular checklist items under each topic.

---

## Networking
- **Playlist:** [Networking Fundamentals](https://www.youtube.com/playlist?list=PLDQaRcbiSnqF5U8ffMgZzS7fq1rHUI3Q8) — covers OSI model, TCP/IP, DNS, proxies
- **Last updated:** 2026-02-07
- **Notes:** `foundations/networking.md` — covers forward/reverse proxy on AWS, ALB/CloudFront patterns, TLS termination, debugging playbook
- **Status:** ██░░░░░░░░ 20%

## Serialization & Data Encoding
- **Resources:** `foundations/serialization.md`, `apache-spark-pyspark/serialization.md`
- **Topics:** Avro vs Protobuf vs Thrift, Parquet/ORC columnar format, schema evolution (Avro rules, Protobuf reserved fields), compression codecs (Snappy/Zstd/Gzip/LZ4), row vs column orientation
- **Status:** ░░░░░░░░░░ 0%

## File Formats & Storage
- **Resources:** `foundations/file-formats.md`
- **Topics:** Parquet (row groups, column chunks, statistics, predicate pushdown), ORC vs Parquet, Avro for streaming, Iceberg table format layering, Delta Lake transaction log
- **Status:** ░░░░░░░░░░ 0%

## Containerization
- **Resources:** `foundations/containerization.md`
- **Topics:** Dockerfile best practices for DE (multi-stage builds, layer caching), Docker Compose for local Kafka/Flink clusters, Kubernetes basics (pods, deployments, services, configmaps), K8s operators (Flink Operator, Spark-on-K8s)
- **Status:** ░░░░░░░░░░ 0%

## Distributed Systems
- **Resources:** `foundations/distributed-systems.md`
- **Topics:** CAP theorem, consistency models (eventual, causal, strong), consensus (Paxos/Raft), distributed join strategies, failure detection and isolation
- **Status:** ░░░░░░░░░░ 0%

## OLAP vs OLTP
- **Resources:** `foundations/olap-vs-oltp.md`
- **Topics:** Workload characteristics (row vs column stores), storage orientation tradeoffs, MPP architecture, columnar compression, query patterns, real-world separation patterns
- **Status:** ░░░░░░░░░░ 0%

---

## SQL & Data Modeling
- **Resources:** LeetCode (database section), StrataScratch, `progress-checklist.md` §1, `foundations/data-modeling.md`
- **Topics:** Window functions, CTEs (recursive), joins (anti/semi), query optimization (EXPLAIN ANALYZE, partitioning, indexing), data modeling (star/snowflake, SCD Type 1/2/3, fact/dimension tables)
- **Status:** ░░░░░░░░░░ 0%

---

## Apache Spark / PySpark
- **Resources:** `apache-spark-pyspark/notes.md`, `apache-spark-pyspark/spark-concepts-execution-architecture.md`
- **Topics:** Lazy transforms vs actions, Catalyst optimizer, Tungsten, shuffle & partitioning, broadcast vs sort-merge joins, skew handling (salting), memory management, checkpointing, Structured Streaming
- **Status:** ░░░░░░░░░░ 0%

---

## Apache Kafka
- **Resources:** `apache-kafka/notes.md`
- **Topics:** Topics/partitions/offsets, consumer groups & rebalancing, delivery semantics, ISR & acks, topic design (partition count, replication, retention, compaction), Kafka Connect, Kafka Streams, Schema Registry, DLQ
- **Status:** ░░░░░░░░░░ 0%

---

## Apache Flink
- **Resources:** `apache-flink/notes.md`, `apache-flink/kafka-to-flink-local-setup.md`, `apache-flink/practice-roadmap.md`
- **Topics:** Windowing (tumbling/sliding/session), event-time vs processing-time, watermarks & late data, keyed/operator state, state backends, checkpointing & 2PC, CEP, backpressure
- **Status:** ░░░░░░░░░░ 0%

---

## Apache Iceberg
- **Resources:** `apache-iceberg/notes.md`
- **Topics:** Catalog → metadata → manifest → data files, snapshot isolation, hidden partitioning & partition evolution, schema evolution, time travel, CoW vs MoR, compaction, position vs equality deletes, optimistic concurrency
- **Status:** ░░░░░░░░░░ 0%

---

## AWS Cloud Stack
- **Resources:** `emr/notes.md`
- **Topics:**
  - **Compute & ETL:** Glue (crawlers, jobs, bookmarks), EMR (instance fleets, spot, serverless), EMR vs Glue tradeoffs
  - **Storage & Query:** S3 (storage classes, lifecycle, partition layout), Athena (CTAS, UNLOAD, bytes-scanned billing), Redshift (dist styles, sort keys, Spectrum, WLM, RA3)
- **Status:** ░░░░░░░░░░ 0%

---

## Streaming & Real-Time Concepts
- **Topics:** Batch vs streaming tradeoffs, Lambda vs Kappa architecture, event-time vs processing-time vs ingestion-time, watermarks & late data, exactly-once semantics (idempotent sinks, 2PC), CDC (Debezium, WAL), schema evolution in streaming, backpressure patterns
- **Status:** ░░░░░░░░░░ 0%

---

## Modern Data Stack
- **Topics:**
  - **dbt:** Models, materializations (table/view/incremental/ephemeral), incremental models under the hood, testing, docs & lineage
  - **Orchestration:** Airflow DAGs, idempotency, backfills, SLA handling, sensors vs operators, XComs
  - **Data Quality:** Great Expectations/Soda, data contracts, OpenLineage/Marquez, SLOs (freshness/completeness/accuracy), PII detection
- **Status:** ░░░░░░░░░░ 0%

---

## Python for Data Engineering
- **Resources:** `progress-checklist.md` §9
- **Topics:** Generators/yield, context managers, decorators (logging/timing/retry), file I/O (CSV/JSON/Parquet/Avro), pandas (groupby/merge/pivot), pytest & mocking, type hints, virtual environments
- **Status:** ░░░░░░░░░░ 0%

---

## DSA — Data Engineer Priority
- **Resources:** LeetCode, NeetCode.io, StrataScratch
- **Topics by pattern:** Arrays (two pointers, sliding window, prefix sums, Kadane's), Hashing (frequency maps, grouping), Linked Lists (fast/slow, reversal, merging), Trees (DFS/BFS, BST, LCA), Graphs (BFS/DFS, topological sort, union-find), DP (1D/2D, knapsack), Sorting & Searching (binary search, intervals, heap)
- **DE-specific flavor:** Merge K sorted lists, Top K with heaps, running median, interval merging, matrix BFS/DFS for partitioning, string parsing (CSV/log)
- **Status:** ░░░░░░░░░░ 0%

---

## System Design
- **Resources:** `system-design/notes.md`, `system-design/caching.md`
- **Framework:** Clarify (throughput/latency/correctness/volume) → Choose (batch vs streaming vs micro-batch) → Design (storage/compute/partitioning) → Drill (bottlenecks, failures) → Cost
- **Scenarios:** Real-time analytics pipeline, data platform (batch + streaming), log aggregation, feature store, legacy migration, petabyte-scale recovery
- **Status:** ░░░░░░░░░░ 0%

---

## Behavioral
- **Resources:** `progress-checklist.md` §12, `2-month-sprint-plan.md` Week 8
- **STAR stories to draft (3):** Pipeline break — detection → mitigation → RCA → long-term fix; Technical decision explained to non-technical stakeholder; Conflict or pushback on requirements
- **Common questions:** What makes a pipeline production-ready? Prioritization under fire? First 90 days on a new team? Handling quality vs deadlines?
- **Status:** ░░░░░░░░░░ 0%

---

## GCC Company-Specific Prep

DE interview questions and experiences at top Global Capability Centers
with high data engineering pay:

- **Full guide:** `interview-prep/gcc-company-questions.md`
- **Companies covered:** LSEG, Tesco, Flipkart, Walmart Global Tech,
  Target, Lowe's, Boeing, Airbus
- **Includes:** Real questions from candidate reports, interview
  process details per company, topic frequency comparison matrix

---

## Hour Log

| Date | Hours | Topic | Notes |
|------|-------|-------|-------|
| 2026-02-07 | 1.0 | Networking | OSI model up to Part 3 |
| 2026-07-24 | 3.0 | Foundations expansion | Created data-modeling, file-formats, distributed-systems, olap-vs-oltp, containerization, serialization |
| 2026-07-24 | 1.0 | Cross-cutting topics | Added Data Contracts, Data Mesh, Reverse ETL, Data Observability to system-design + roadmap |
| 2026-07-24 | 1.5 | Version-specific updates | Flink 2.0, Kafka 4.0, Spark RAPIDS, EMRFS deprecation |
| 2026-07-24 | 1.0 | Thicken thin files | Expanded flink-practice-roadmap (78→350 lines), serialization foundations |
| 2026-07-24 | 0.5 | Checklist updates | Added Flink 2.0, Kafka 4.0, RAPIDS, Reverse ETL, Data Mesh, Observability to progress-checklist |

---

## Best Articles by Topic

The single highest-signal article for each core topic. These are the ones interviewers reference and peers cite.

### Spark
- [On Spark, Hive, and Small Files (Airbnb Engineering)](https://medium.com/airbnb-engineering/on-spark-hive-and-small-files-an-in-depth-look-at-spark-partitioning-strategies-a9a364f908) — the definitive guide to Spark partitioning strategies at production scale; explains coalesce vs repartition, dynamic partition writing, file count management
- [Understanding Apache Spark Shuffle (Philipp Brunenberg)](https://medium.com/@philipp.brunenberg/understanding-apache-spark-shuffle-85644d90c8c6) — detailed internals: map side write, reduce side read, SortShuffleManager, performance analysis

### Kafka
- [Exactly-Once Semantics Are Possible: Here's How Kafka Does It (Confluent)](https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/) — the canonical explanation of idempotent producers, transactions, and EOS from Kafka's creators
- [Demystifying Kafka Exactly Once Semantics (HelloFresh Engineering)](https://engineering.hellofresh.com/demystifying-kafka-exactly-once-semantics-eos-390ae1c32bba) — practical production perspective on EOS boundaries, what it does and doesn't guarantee

### Flink
- [Streaming 101 (Tyler Akidau)](https://www.oreilly.com/radar/the-world-beyond-batch-streaming-101/) — the seminal article on event-time, watermarks, windows; the foundation every streaming engineer must understand
- [Flink Watermarks and Event Time (Streamkap)](https://streamkap.com/resources-and-guides/flink-watermarks-event-time) — production-focused: watermark strategies, idle source problem, multi-stream propagation, monitoring

### Iceberg
- [Apache Iceberg Architecture Deep Dive (BigData Boutique)](https://bigdataboutique.com/blog/apache-iceberg-architecture-deep-dive) — layer-by-layer walkthrough of catalog → metadata → manifest list → manifest → data files with concrete disk layout example
- [The Three Layers That Power Your Lakehouse (Snowflake Blog)](https://medium.com/snowflake/deep-dive-into-apache-iceberg-architecture-the-three-layers-that-power-your-lakehouse-83c03403e503) — dissects catalog, metadata, and data layers with query trace showing hierarchical pruning

### System Design for DE
- [System Design for Data Engineers (Akanksha Singh)](https://medium.com/@akanksha_singh/system-design-for-data-engineers-65cf66abf325) — explains how DE system design differs from SWE design, data-specific tradeoffs
- [Data Engineering System Design Framework (dataskew)](https://dataskew.io/blog/data-engineer-interview-system-design) — 5-step framework with 3 example scenarios and drill questions

---

## Week-by-Week Sprint Mapping

Refer to `interview-prep/2-month-sprint-plan.md` for the daily schedule. General cadence:

| Phase | Weeks | Focus |
|-------|-------|-------|
| Month 1 | 1–2 | SQL & Data Modeling → Spark/PySpark |
| Month 1 | 3–4 | Python + DSA (arrays/hashing/trees/linked lists) |
| Month 2 | 5–6 | Kafka, Flink, Streaming → System Design |
| Month 2 | 7–8 | Cloud + Modern Stack → Mocks & Behavioral |

