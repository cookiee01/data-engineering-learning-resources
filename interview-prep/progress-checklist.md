# Data Engineering Interview — Progress Checklist

Mark each item `[x]` when you can explain it clearly **and** solve a related problem without help.

---

## 1. SQL & Data Modeling

### SQL Core
- [ ] Window functions: `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `NTILE`
- [ ] Window functions: `LEAD`/`LAG`, `FIRST_VALUE`/`LAST_VALUE`
- [ ] Window frames: `ROWS BETWEEN`, `RANGE BETWEEN`, default frame
- [ ] CTEs — non-recursive (with multiple CTEs in one query)
- [ ] Recursive CTEs — org chart, date spine, graph traversal
- [ ] INNER, LEFT, RIGHT, FULL OUTER joins — semantics and row counts
- [ ] Anti-joins: `LEFT JOIN ... WHERE ... IS NULL`, `NOT EXISTS`, `NOT IN`
- [ ] Semi-joins: `EXISTS`, `IN`
- [ ] Dedup: `ROW_NUMBER() OVER(PARTITION BY ...)`, self-join, aggregation
- [ ] `WHERE` vs `HAVING` — filtering before vs after aggregation
- [ ] NULL handling: `COALESCE`, `NULLIF`, three-valued logic in `WHERE` clauses
- [ ] Set operations: `UNION` vs `UNION ALL`, `INTERSECT`, `EXCEPT`

### Query Optimization
- [ ] Read `EXPLAIN ANALYZE` — spot full table scans, hash joins, sorts
- [ ] Partition pruning — when it works, when it doesn't
- [ ] Indexing strategy — B-tree, bitmap, covering indexes
- [ ] Materialized views — when to use, refresh strategies
- [ ] `SELECT *` and its cost in distributed engines
- [ ] Common pitfalls: implicit type conversion, function-wrapped columns in WHERE

### Data Modeling
- [ ] Normal forms: 1NF, 2NF, 3NF — identify violations
- [ ] Star schema vs snowflake schema — tradeoffs
- [ ] Fact tables: transactional, periodic snapshot, accumulating snapshot
- [ ] Dimension tables: conformed, degenerate, junk, role-playing
- [ ] SCD Type 1 (overwrite), Type 2 (versioning), Type 3 (limited history)
- [ ] SCD Type 2 implementation with effective dates + current flag
- [ ] Data Vault: hubs, links, satellites — when to use
- [ ] Grain declaration — "one row per X" before building any model
- [ ] Bridge tables for many-to-many relationships

### SQL Practice (LeetCode / StrataScratch)
- [ ] 2nd highest salary per department
- [ ] Running total and moving average
- [ ] Find duplicates and return full rows
- [ ] Consecutive records (self-join or window)
- [ ] Gap-and-island problems
- [ ] Median calculation (percentile or offset-based)

---

## 2. Apache Spark / PySpark

### Execution Model
- [ ] Lazy transformations vs actions — which trigger execution?
- [ ] Catalyst optimizer — phases: analysis, logical optimization, physical planning, codegen
- [ ] Tungsten — whole-stage codegen, cache-aware computation
- [ ] DAG — stages, tasks, narrow vs wide dependencies
- [ ] Job → Stage → Task pipeline breakdown

### Shuffle & Partitioning
- [ ] What triggers a shuffle (`groupBy`, `join`, `repartition`, `distinct`)
- [ ] `repartition(n)` vs `coalesce(n)` — when to use each
- [ ] Partition pruning with partitioned data sources
- [ ] `spark.sql.shuffle.partitions` — tuning
- [ ] AQE (Adaptive Query Execution) — coalescing, skew join, switching join strategies

### Joins & Skew Handling
- [ ] Broadcast hash join — threshold, when to force
- [ ] Sort-merge join — when it's used
- [ ] Skew join — salting technique (add random prefix, explode on join key)
- [ ] AQE skew join optimization

### Memory & Performance
- [ ] Execution vs storage memory — `spark.memory.fraction`, `spark.memory.storageFraction`
- [ ] Kryo serialization — register classes, what to use it for
- [ ] `spark.sql.adaptive.enabled` and related configs
- [ ] Checkpointing — truncating lineage, use cases

### Spark SQL & DataFrames
- [ ] DataFrame API vs Spark SQL vs RDD — tradeoffs
- [ ] UDFs vs built-in functions — performance cost of UDFs
- [ ] Pandas UDFs (vectorized UDFs) — when they help
- [ ] `cache()` vs `persist()` — storage levels

### Streaming (Structured Streaming)
- [ ] Micro-batch vs continuous processing
- [ ] Output modes: append, update, complete
- [ ] Watermarking — handling late data
- [ ] Sinks: foreachBatch, console, memory, file
- [ ] Checkpoint location for fault tolerance

---

## 3. Apache Kafka

### Fundamentals
- [ ] Topics, partitions, offsets — physical layout
- [ ] Consumer groups — group coordination, rebalancing
- [ ] Partition assignment strategies: range, round-robin, sticky, cooperative
- [ ] At-least-once, at-most-once, exactly-once semantics
- [ ] In-sync replicas (ISR) and `acks` setting
- [ ] `min.insync.replicas` + replication factor tradeoffs

### Topic Design
- [ ] Partition count — throughput vs ordering vs rebalance time
- [ ] Replication factor — durability vs storage cost
- [ ] Retention — time-based vs size-based, compacted topics (log compaction)
- [ ] Key-based partitioning — ordering guarantees per key

### Operations
- [ ] Kafka Connect — source/sink connectors, single message transforms (SMTs)
- [ ] Kafka Streams — exactly-once, state stores, KTables
- [ ] Schema Registry — Avro/Protobuf/JSON Schema, compatibility modes
- [ ] Dead letter queue — handling poison pills
- [ ] Rebalancing — what happens, how to minimize impact (static group membership)

---

## 4. Apache Flink

### Windowing
- [ ] Tumbling, sliding, session windows — when to use each
- [ ] Event-time vs processing-time vs ingestion-time
- [ ] Watermarks — idle sources, late data handling, allowed lateness
- [ ] Triggering and eviction

### State & Fault Tolerance
- [ ] Keyed state vs operator state — value, list, map state
- [ ] State backends: HashMap, RocksDB — tradeoffs
- [ ] Checkpointing — exactly-once via checkpoint + 2PC (two-phase commit)
- [ ] Savepoints — versioned state snapshots for upgrades
- [ ] End-to-end exactly-once with Flink + Kafka sink

### Advanced
- [ ] Flink SQL vs DataStream API — when to use each
- [ ] CEP (Complex Event Processing) — pattern matching on streams
- [ ] Backpressure — how Flink handles it, how to monitor
- [ ] Operator chaining — reducing network overhead

---

## 5. Apache Iceberg

### Architecture
- [ ] Catalog → Metadata JSON → Manifest List → Manifest Files → Data Files
- [ ] Catalog types: Hive, HDFS, JDBC, REST, Glue
- [ ] Snapshot isolation — how reads see consistent state

### Table Features
- [ ] Hidden partitioning — month/day/hour transforms, partition evolution
- [ ] Schema evolution — add, rename, drop, reorder columns
- [ ] Time travel — `FOR SYSTEM_TIME AS OF` and snapshot IDs
- [ ] Incremental reads — reading only new data since a snapshot
- [ ] Compaction — bin-pack, sort, how it works with MoR

### Write Strategies
- [ ] Copy-on-Write (CoW) — write amplification vs read efficiency
- [ ] Merge-on-Read (MoR) — delete files, compaction overhead
- [ ] Position deletes vs equality deletes — which to use when
- [ ] Optimistic concurrency — retry on conflicts via catalog CAS

---

## 6. AWS Cloud Stack

### Compute & ETL
- [ ] Glue: Crawlers, Data Catalog, ETL jobs (PySpark), job bookmarks
- [ ] Glue Studio vs notebooks vs scripts
- [ ] EMR: instance groups, instance fleets, spot instances
- [ ] EMR Serverless — when it makes sense
- [ ] EMR vs Glue — decision criteria

### Storage & Query
- [ ] S3: storage classes, lifecycle policies, partition layout best practices
- [ ] Athena: serverless querying, CTAS, UNLOAD, bytes-scanned billing
- [ ] Redshift: distribution styles (KEY/EVEN/ALL/AUTO), sort keys (compound/interleaved)
- [ ] Redshift Spectrum — querying S3 directly from Redshift
- [ ] Redshift: VACUUM, ANALYZE, WLM, concurrency scaling, RA3/managed storage
- [ ] Athena vs Redshift Spectrum vs Redshift — when to use each

---

## 7. Streaming & Real-Time Concepts

- [ ] Batch vs streaming — tradeoffs for latency, throughput, correctness
- [ ] Lambda architecture (batch + speed + serving) vs Kappa (stream-only)
- [ ] Event-time vs processing-time vs ingestion-time
- [ ] Watermarks — how they work, handling late/out-of-order data
- [ ] Exactly-once in streaming: idempotent sinks, transactional writes, 2PC
- [ ] CDC — Debezium, logical replication, WAL-based capture
- [ ] Schema evolution in streaming — Avro/Protobuf + Schema Registry
- [ ] Backpressure — definition, detection, mitigation
- [ ] Window types: tumbling, sliding, session, global — semantics and tradeoffs

---

## 8. Modern Data Stack

### ELT & dbt
- [ ] ELT vs ETL — why ELT dominates, when ETL is still necessary
- [ ] dbt: models, materializations (table, view, incremental, ephemeral)
- [ ] dbt incremental models — how they work under the hood
- [ ] dbt tests: singular, generic (unique, not-null, accepted values, relationships)
- [ ] dbt docs and lineage graphs

### Orchestration
- [ ] Airflow: DAGs, operators, sensors, TaskFlow API
- [ ] Idempotency — "what happens if I rerun this DAG?"
- [ ] Backfill strategies — date-partitioned runs, catchup
- [ ] SLA management — timeouts, retries, alerting
- [ ] Sensors vs operators — polling vs event-driven
- [ ] XComs — lightweight inter-task communication, limitations

### Data Quality & Governance
- [ ] Great Expectations / Soda — expectations, suite, data docs
- [ ] Data contracts — schema agreement between producer and consumer
- [ ] Data lineage — OpenLineage, Marquez, why it matters
- [ ] SLOs — freshness, completeness, accuracy for pipelines
- [ ] PII detection and masking

---

## 9. Python for Data Engineering

### Coding Patterns
- [ ] Generators and `yield` — memory-efficient iteration
- [ ] Context managers (`with` statements) — custom `__enter__`/`__exit__`
- [ ] Decorators — logging, timing, retry patterns
- [ ] Exception handling — try/except/finally, custom exceptions
- [ ] Logging — structured logging, log levels, handlers

### Data Processing
- [ ] File I/O — CSV, JSON, Parquet, Avro in Python
- [ ] `pandas`: groupby, merge, pivot, melt, apply
- [ ] Understanding pandas vs PySpark — single-node vs distributed
- [ ] Regex for log parsing, data cleaning

### Testing & Best Practices
- [ ] pytest — fixtures, parametrize, conftest.py
- [ ] Mocking — `unittest.mock`, patching external calls
- [ ] Type hints — typing module, mypy basics
- [ ] Virtual environments — venv, requirements.txt, pyproject.toml
- [ ] CI/CD for pipelines — GitHub Actions basics

---

## 10. DSA — Data Engineer Priority

### Arrays & Strings
- [ ] Two Pointers: Container With Most Water, 3Sum, Valid Palindrome
- [ ] Sliding Window (fixed): Max Sum Subarray of Size K
- [ ] Sliding Window (variable): Longest Substring Without Repeating Chars, Min Window Substring
- [ ] Prefix Sums: Product of Array Except Self, Range Sum Query
- [ ] Kadane's Algorithm: Maximum Subarray

### Hashing
- [ ] Frequency Maps: Top K Frequent Elements, Word Frequency
- [ ] Grouping: Group Anagrams, Valid Anagram
- [ ] Two Sum + variants (Three Sum, Four Sum, Subarray Sum Equals K)

### Linked Lists
- [ ] Fast/Slow Pointer: Detect Cycle, Find Middle
- [ ] Reversal: Reverse Linked List
- [ ] Merging: Merge Two Sorted Lists, Merge K Sorted Lists
- [ ] LRU Cache design (HashMap + Doubly Linked List)

### Trees & BSTs
- [ ] DFS: Maximum Depth, Invert Binary Tree, Validate BST
- [ ] BFS: Level Order Traversal, Right Side View
- [ ] LCA: Lowest Common Ancestor of BST / Binary Tree
- [ ] Construct from Preorder + Inorder

### Graphs
- [ ] BFS/DFS: Number of Islands, Clone Graph, Number of Provinces
- [ ] Topological Sort: Course Schedule, Alien Dictionary
- [ ] Union-Find: Accounts Merge, Number of Connected Components
- [ ] Shortest Path: Dijkstra basics, Network Delay Time

### Dynamic Programming
- [ ] 1D DP: Climbing Stairs, House Robber, Coin Change
- [ ] 2D DP: Longest Common Subsequence, Edit Distance
- [ ] Knapsack: 0/1 Knapsack, Partition Equal Subset Sum

### Sorting & Searching
- [ ] Binary Search: Search in Rotated Sorted Array, Find Min in Rotated
- [ ] Merge Sort / Intervals: Merge Intervals, Insert Interval
- [ ] Heap: Kth Largest Element, Find Median from Data Stream

### DE-Specific Flavors
- [ ] Merge K sorted lists — relates to partition merging in Spark
- [ ] Top K with heaps — frequent items, log analysis, `takeOrdered`
- [ ] Running median / streaming stats — windowed aggregations
- [ ] Interval merging — log time ranges, scheduling pipeline runs
- [ ] String parsing — CSV/JSON tokenization, log parsing
- [ ] Matrix BFS/DFS — grid-based partitioning, connected components

---

## 11. System Design

### Framework
- [ ] Clarify — throughput, latency, correctness, data volume, consistency
- [ ] Choose — batch vs streaming vs micro-batch, justify tradeoffs
- [ ] Design — storage format, partitioning, compute engine, orchestration
- [ ] Drill — bottlenecks (shuffle, skew, storage), failure scenarios
- [ ] Cost — compute, storage, data transfer estimates

### Scenarios
- [ ] Real-time analytics pipeline (e.g., e-commerce clickstream)
- [ ] Data platform supporting batch + streaming (unified vs separate)
- [ ] Log aggregation / observability system (ELK-alike)
- [ ] Feature store for ML (offline + online serving)
- [ ] Data migration from legacy ETL to modern stack

### Failure & Recovery Drills
- [ ] Pipeline produces duplicate records — how to dedup downstream
- [ ] Dashboard shows wrong numbers — debugging process
- [ ] Downstream needs data in 5 min but pipeline takes 30 — what do you do?
- [ ] Schema change breaks downstream — prevention + recovery
- [ ] Petabyte-scale data recovery under SLA pressure

---

## 12. Behavioral

### STAR Stories (draft 3)
- [ ] Story 1: Pipeline broke — detection, mitigation, root cause, long-term fix
- [ ] Story 2: Technical decision to non-technical stakeholder
- [ ] Story 3: Conflict with a teammate or pushing back on a requirement

### Common Questions
- [ ] What makes a pipeline "production-ready" vs a prototype?
- [ ] How do you prioritize when multiple pipelines are failing?
- [ ] Describe your approach to the first 90 days on a new team
- [ ] How do you handle strict deadlines when quality might be compromised?

---

## 13. Logistics & Offer Stage

- [ ] Know what questions to ask the interviewer (signal seniority)
- [ ] Know how to handle "I don't know" gracefully
- [ ] Understand RSU vs base salary vs sign-on vs refresher policy
- [ ] Know how to evaluate team fit (on-call, tech stack, data maturity)
- [ ] Prepare a "close me" statement — why you and why now

---

## How to Use This Checklist

- **Start of prep:** Skim everything, mark which items you already know.
- **Each week:** Focus on the relevant section from the 2-month sprint plan. Mark items as you can explain + demonstrate them.
- **Week 8:** Any unchecked item is a weak spot. Prioritize those in your final mocks.
- **Revisit:** Markings should be honest — "I've heard of it" ≠ "I can explain it clearly under pressure."
