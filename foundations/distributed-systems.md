# Distributed Systems for Data Engineers — Interview Deep Dive

Every data pipeline is a distributed system. Understanding CAP,
consistency models, replication, and consensus is essential for
debugging production failures and designing reliable pipelines.

---

## 1. The Opening Question

**Question:** *"Your pipeline produced duplicate records today. How would you diagnose and fix it?"*

```mermaid
flowchart TD
    DUP["Duplicate records detected"]
    DUP --> SOURCE{"Source delivery<br/>semantics?"}

    SOURCE -->|"At-most-once"| AT_MOST["Source may drop but never<br/>duplicate → duplicates come<br/>from downstream"]
    SOURCE -->|"At-least-once"| AT_LEAST["Source may retry on failure<br/>→ duplicates possible"]
    SOURCE -->|"Exactly-once"| EXACTLY["Source guarantees no dupes<br/>→ look at sink or transform"]

    AT_LEAST --> SINK{"Sink idempotent?"}
    SINK -->|"No (INSERT without dedup)"| FIX1["Fix: Make sink idempotent<br/>UPSERT instead of INSERT<br/>or dedup downstream"]
    SINK -->|"Yes (dedup by PK)"| FIX2["Fix: Check transform logic<br/>for accidental double-emit"]

    EXACTLY --> PROBE{"Checkpoint/transactional<br/>sink correctly configured?"}
    PROBE -->|"No"| FIX3["Fix: Enable checkpoints,<br/>use 2PC sink, idempotent writes"]
    PROBE -->|"Yes"| FIX4["Fix: Look at source replay<br/>on different offset/snapshot"]
```

**Answer structure (DE interview version):**
```
1. Duplicates come from at-least-once delivery + non-idempotent sink
2. Fix the sink: UPSERT instead of INSERT, or deduplicate in staging
3. Long-term: use exactly-once sinks (2PC for Flink, idempotent for Kafka)
4. Monitor: track dedup ratio as a data quality metric
```

---

## 2. CAP Theorem

### 2.1 The Diagram

**Question:** *"Explain CAP theorem. Where does your pipeline's storage system fall?"*

```mermaid
flowchart TD
    CAP["CAP Theorem<br/>Pick at most 2 of 3"]
    CAP --> C["Consistency<br/>All nodes see<br/>same data at once"]
    CAP --> A["Availability<br/>Every request gets<br/>a response"]
    CAP --> P["Partition Tolerance<br/>System works despite<br/>network failures"]

    C <--> CP["CP Systems:<br/>HDFS, Kafka, ZooKeeper<br/>(sacrifice availability<br/>during partition)"]
    A <--> AP["AP Systems:<br/>Cassandra, DynamoDB<br/>(eventual consistency)"]

    C -.-> CA["CA: impossible in practice<br/>(partitions always happen)"]
    P -.-> CP
    P -.-> AP
```

**Real-world DE examples:**

| System | Category | What It Sacrifices | What Happens in a Partition |
|---|---|---|---|
| **HDFS** | CP | Availability (NameNode failover blocks all writes) | Metadata operations blocked until new NameNode elected |
| **Kafka** | CP | Availability (lose one replica + ISR requirement → partition unavailable) | Partition unavailable until ISR restored |
| **S3 (current)** | CP | Availability (very rare, strongly consistent) | 5xx errors for writes during severe partition |
| **Cassandra** | AP | Consistency (eventual reads) | Reads continue, stale data possible |
| **DynamoDB (default)** | AP | Consistency (eventual reads, opt-in strong) | Reads always succeed, may return stale |

> [!WARNING]
> CAP is a simplification for interviews. Real systems are **PA/EL**
> (Available during partition + Eventually Consistent) or **PC/EC**
> (Consistent during partition + tolerate unavailability). Always
> ask: *What happens during a network partition?*

### 2.2 CAP in Pipeline Design

**Question:** *"You're designing a payment reconciliation pipeline. Which CAP tradeoff do you make?"*

```
Payment pipeline: Must be consistent (no double-charge, no missing credit)
→ CP system: Kafka with acks=all + min.insync.replicas=2
→ If broker fails, partition is unavailable until ISR restored
→ Accept temporary unavailability over incorrect balance

Real-time dashboard: Must be available (show something on screen)
→ AP system: Cassandra or DynamoDB
→ If partition, show stale data (eventual consistency)
→ Accept stale data over blank dashboard
```

---

## 3. Consistency Models

### 3.1 Spectrum

**Question:** *"Explain the difference between eventual, causal, and strong consistency in terms of what a user sees."*

```mermaid
flowchart LR
    WEAK["Weaker consistency<br/>(lower latency,<br/> higher availability)"]
    STRONG["Stronger consistency<br/>(higher latency,<br/> lower availability)"]

    WEAK --> EV["Eventual<br/>Replicas converge eventually<br/>DNS, S3 pre-2020<br/>No ordering guarantees"]
    EV --> RW["Read-your-writes<br/>Client sees its own writes<br/>Session consistency<br/>Many distributed caches"]
    RW --> CA["Causal<br/>Causally related ops ordered<br/>CRDTs, DynamoDB sessions<br/>'Bob sees Alice's post after she wrote it'"]
    CA --> STR["Strong / Linearizable<br/>All nodes same state at once<br/>Single-node DB, ZooKeeper<br/>'Read returns latest write'"]

    STRONG --> note1["Cost: 2x-5x latency vs eventual<br/>due to quorum coordination"]
```

### 3.2 Consistency in DE Components

| Component | Model | Interview Answer |
|---|---|---|
| **S3 (since Dec 2020)** | Strong (read-after-write) | "Before Dec 2020, we had to write to a new key, then rename. Now we can overwrite safely." |
| **Kafka** | Strong per partition | "Within a partition, messages are totally ordered. Across partitions, no ordering guarantee." |
| **Snowflake** | Strong within warehouse | "Query always reads committed state. Cross-region replication is async." |
| **Iceberg** | Snapshot isolation | "Reader sees a consistent snapshot. Writer commits atomically via catalog CAS." |
| **Spark lineage** | Strong on recompute | "Lost partition is deterministically recomputed from lineage (if transformations are pure)." |
| **Flink checkpoint** | Exactly-once | "Checkpoint + 2PC commit: source offsets, operator state, sink writes are atomic." |

---

## 4. Partitioning / Sharding

### 4.1 Strategies

**Question:** *"A Kafka topic with 12 partitions has one partition receiving 80% of the traffic. What's wrong and how do you fix it?"*

```mermaid
flowchart TD
    subgraph "Hot Partition Problem"
        K1["Partition 0<br/>80% load<br/>key = customer_id<br/>hash(customer_id) % 12"]
        K2["Partition 1-11<br/>~20% load"]
    end

    K1 --> SKEW["Root cause: Skewed key distribution<br/>One customer generates 80% of events<br/>Hash partitioning maps same customer → same partition"]
    SKEW --> FIX{"Fix?"}

    FIX -->|"If you need ordering per customer"| FIX1["Fixed: Accept skew or<br/>over-partition (more partitions<br/>= less relative skew)"]
    FIX -->|"If ordering not critical"| FIX2["Better: Salt the key<br/>salted_key = customer_id + random(0..10)<br/>hash(salted_key) % 12"]
    FIX -->|"Application-level"| FIX3["Alternative: Custom partitioner<br/>based on content-aware routing"]
```

### 4.2 Partitioning in Data Systems

| System | Mechanism | Control | Rebalancing |
|---|---|---|---|
| **Kafka** | Hash of key % partition count | Producer key, custom partitioner | Partition reassignment (cluster admin) |
| **Spark** | Hash shuffle via `repartition(n)` | `repartition()`, `coalesce()`, `partitionBy()` | On every shuffle (AQE auto-tunes) |
| **Flink** | `keyBy()` → hash partitioning | `keyBy()`, `partitionCustom()` | On savepoint-based rescaling |
| **HDFS** | Block-based (128 MB blocks) | `dfs.block.size` | Namenode manages block locations |
| **Trino/Presto** | Hash distributed via exchange | `DISTRIBUTE BY`, `PARTITION BY` | Per-query |

### 4.3 Skew Mitigation

| Technique | How | When |
|---|---|---|
| **Salting** | Append random prefix to key before hash | High-cardinality natural key with single hot value |
| **Over-partitioning** | Use more partitions than nodes | Skew is diffuse (many slight hot spots) |
| **Range partitioning** | Split data by value range | Naturally ordered data (dates, IDs) with uniform distribution |
| **Adaptive (AQE)** | Spark coalesces small partitions at runtime | Post-shuffle skew detected from runtime stats |
| **Two-phase aggregation** | Partial agg with salt → remove salt → final agg | Aggregation on skewed keys |

---

## 5. Replication

### 5.1 Strategies

**Question:** *"How does Kafka replicate data across brokers? What's the minimum configuration for durability?"*

```mermaid
sequenceDiagram
    participant P as Producer
    participant L as Leader (Broker 1)
    participant F1 as Follower (Broker 2)
    participant F2 as Follower (Broker 3)

    P->>L: Produce message
    L->>L: Append to local log (leader epoch + offset)
    L->>F1: Fetch request (replicate)
    L->>F2: Fetch request (replicate)
    F1-->>L: Acknowledged
    F2-->>L: Acknowledged
    Note over L: min.insync.replicas=2 → wait for<br/>at least 1 follower ACK
    L-->>P: ACK (acks=all)
```

**Durability configuration:**
```ini
# Kafka broker config
min.insync.replicas=2        # Minimum replicas that must ACK
default.replication.factor=3 # Total replicas

# Producer config
acks=all                     # Wait for all in-sync replicas
```

**What happens during broker failure:**
- Leader fails → one follower with latest LEO (Log End Offset) becomes leader
- Un-acked messages from old leader are lost if they weren't replicated
- `min.insync.replicas=2` means if 2 of 3 brokers are up, writes succeed
- If only 1 broker is up, writes fail (unavailable) — CP tradeoff

### 5.2 Quorum Math

**Question:** *"You have 5 Cassandra nodes with RF=3. Set W and R for strong consistency vs eventual consistency."*

```
N = number of replicas = 3
W = write quorum (nodes that must ACK write)
R = read quorum (nodes that must respond to read)

Strong consistency: W + R > N
  Example: W=2, R=2 → 2+2=4 > 3 ✓

Eventual consistency: W + R <= N
  Example: W=1, R=1 → 1+1=2 < 3 (reads may miss latest write)

Typical production: W=2, R=2 (3-way replication, strong)
Fast reads: W=2, R=1 (stale reads possible)
Fast writes: W=1, R=3 (write may not be seen by all readers)
```

---

## 6. Coordination Protocols — Consensus and Distributed Transactions

### 6.1 Raft Consensus

**Question:** *"Explain how Kafka KRaft works. How does it differ from ZooKeeper-based consensus?"*

```mermaid
sequenceDiagram
    participant N1 as Node 1 (Candidate)
    participant N2 as Node 2 (Follower)
    participant N3 as Node 3 (Follower)

    Note over N1,N3: Term 1 — Election
    N1->>N2: RequestVote (term=1, lastLogIndex=0)
    N1->>N3: RequestVote (term=1, lastLogIndex=0)
    N2-->>N1: Vote granted
    N3-->>N1: Vote granted
    Note over N1: Majority (2/3) → N1 becomes Leader

    Note over N1,N3: Term 1 — Log Replication
    N1->>N1: Append entry to local log
    N1->>N2: AppendEntries (term=1, entries=[...])
    N1->>N3: AppendEntries (term=1, entries=[...])
    N2-->>N1: ACK
    N3-->>N1: ACK
    Note over N1: Entry committed (majority ACK'd)
```

| Aspect | ZooKeeper (Zab) | KRaft (Raft) |
|---|---|---|
| Metadata storage | External ZK cluster | Internal topic `__cluster_metadata` |
| Controller election | ZK leader election | Raft-based within controller quorum |
| Scalability limit | ~100K partitions | 1M+ partitions (no ZK bottleneck) |
| Operational complexity | Two systems to manage (ZK + Kafka) | Single system |
| Availability during ZK outage | Kafka unavailable | No single point of failure |

> [!TIP]
> KRaft (KIP-500) is production-ready since Kafka 3.5+ and the default
> in Kafka 4.0. Interview answer: "KRaft removes the ZooKeeper dependency
> by using Raft consensus directly in Kafka controllers, improving
> scalability and operational simplicity."

### 6.2 Two-Phase Commit (2PC) — Deep Dive

**Question:** *"Explain 2PC. Why do people say it doesn't scale?"*

```mermaid
sequenceDiagram
    participant C as Coordinator
    participant P1 as Participant 1 (Kafka)
    participant P2 as Participant 2 (Postgres)

    Note over C,P2: Phase 1: PREPARE
    C->>P1: prepare(tx)
    C->>P2: prepare(tx)
    P1->>P1: Write to WAL, lock resources<br/>reply YES/NO
    P2->>P2: Write to WAL, lock resources<br/>reply YES/NO
    P1-->>C: YES
    P2-->>C: YES

    Note over C,P2: Phase 2: COMMIT
    C->>C: Decision logged to WAL<br/>(durable before notifying)
    C->>P1: commit
    C->>P2: commit
    P1-->>C: ACK
    P2-->>C: ACK
```

**Why it's correct:** The decision is durable at the coordinator before
phase 2, so a coordinator crash mid-commit can be recovered — participants
that voted YES stay locked and ask the coordinator for the outcome.

**Why it struggles at scale:**

| Problem | Impact |
|---|---|
| **Blocking** | Participants hold locks from PREPARE to COMMIT. A slow coordinator = every participant stalls |
| **Coordinator = single point** | If the coordinator dies between phases, participants block until recovery (heuristic decisions risk inconsistency) |
| **Latency multiplication** | 2 extra network round trips per transaction, across the slowest participant |
| **Not all systems speak XA** | S3 has no prepare/commit. SaaS APIs don't. 2PC needs every participant to support the protocol |

**Where DE actually uses it:** Flink's exactly-once sinks implement 2PC
internally (Kafka sink, JDBC sink). Iceberg avoids 2PC entirely with
optimistic concurrency + atomic catalog swap — the modern preference.

---

## 7. Failure Handling in Data Pipelines

### 7.1 Failure Scenarios by System

| System | Failure Type | Recovery Mechanism | Data Loss Risk |
|---|---|---|---|
| **Spark** | Executor loss | Rerun lost tasks from lineage (recomputation) | None (if deterministic) |
| **Flink** | TaskManager loss | Restart from checkpoint (operator state + source offsets) | None (with exactly-once sink) |
| **Kafka** | Broker loss | Follower → leader election, ISR adjustment | Acknowledged data safe; in-flight data lost |
| **Iceberg** | Writer failure | Optimistic concurrency → retry commit; partial files cleaned up | None (atomic commits) |
| **S3** | Regional outage | Cross-region replication (CRR) | Asynchronous; recent objects may be lost |

### 7.2 Pipeline Design for Failure

**Question:** *"Design a data pipeline that survives a Spark executor failure, a Kafka broker failure, and a warehouse outage — all at the same time."*

```mermaid
flowchart TD
    SRC["Source: Kafka<br/>retention=7 days"] --> SPARK["Spark Streaming<br/>checkpoint=S3<br/>idempotent transforms"]
    SPARK --> SINK["Sink: Iceberg<br/>on S3<br/>atomic commits"]

    subgraph "Failure 1: Executor dies"
        SPARK --> E1["Driver detects loss<br/>via heartbeat timeout"]
        E1 --> E2["Reschedules lost tasks<br/>on remaining executors"]
        E2 --> E3["Lineage + checkpoint<br/>recomputes lost partitions"]
    end

    subgraph "Failure 2: Kafka broker dies"
        SRC --> K1["Leader election<br/>among in-sync replicas"]
        K1 --> K2["Producer retries<br/>with idempotent flag"]
        K2 --> K3["min.insync.replicas=2<br/>ensures no data loss"]
    end

    subgraph "Failure 3: Warehouse unavailable"
        SINK --> W1["Spark retries commit<br/>configurable retries + backoff"]
        W1 --> W2["Iceberg retry on conflict<br/>(optimistic concurrency)"]
        W2 --> W3["Sink writes to temp dir<br/>rename on success"]
    end
```

**Key design principles:**
1. **Idempotent transforms**: Rerunning a task produces the same output
2. **Checkpoint durable state**: Store checkpoints where they survive node loss (S3, not local disk)
3. **Retry with backoff**: Every component must retry transient failures
4. **Dead letter queue**: Captures records that fail beyond retry limit
5. **Alert on retry exhaustion**: Don't silently lose data

---

## 8. Real Interview Questions

### Q1: "Explain how Spark's lineage provides fault tolerance without replication."

**Answer:** Spark does NOT replicate data in memory. If an executor dies,
its in-memory data is lost. Recovery:
1. The driver detects executor loss via heartbeat timeout
2. It identifies which partitions were lost
3. It re-runs the **lineage graph** (the DAG of transformations) from
   the last checkpoint or source data for those partitions
4. New tasks are scheduled on surviving executors

**Cost:** Recomputation time. Mitigated by checkpointing at shuffle
boundaries (truncating lineage).

### Q2: "Your Kafka consumer reads from 12 partitions. One partition has higher lag than the others. What's the root cause?"

```mermaid
flowchart TD
    LAG["High lag on partition 3"]
    LAG --> CAUSES{"Possible causes"}

    CAUSES --> HOT["Hot key: one customer<br/>produces 90% of events<br/>for partition 3"]
    CAUSES --> SLOW["Slow consumer: partition 3<br/>processing takes longer<br/>(CPU, I/O, blocking call)"]
    CAUSES --> ASSIGN["Sticky assignment: all high-traffic<br/>partitions assigned to same<br/>consumer in the group"]

    HOT --> FIX1["Fix: Salt the key or<br/>over-partition the topic"]
    SLOW --> FIX2["Fix: Inspect processing logic,<br/>distribute load evenly"]
    ASSIGN --> FIX3["Fix: Use cooperative rebalancing<br/>or range assignor"]
```

### Q3: "Does exactly-once semantics exist in distributed systems?"

**Answer:** Exactly-once is achievable end-to-end, but it requires
coordination at every stage:

```
Source:      Kafka with idempotent producer + transactions
                    ↓    (read_committed isolation)
Transform:   Flink checkpointing or Spark Structured Streaming
           (transactional state backend, e.g., RocksDB)
                    ↓
Sink:        Two-phase commit (Kafka, Iceberg, JDBC with XA)
```

**What can break it:**
- Inconsistencies in the 2PC coordinator (rare, but possible)
- Sink that doesn't support idempotent writes
- Custom non-deterministic transforms (e.g., `random()`, current timestamp)

**Interview answer:** "Exactly-once is theoretically possible but
requires every component in the pipeline to support it. In practice,
most pipelines run at-least-once with idempotent sinks, which gives
the same result as exactly-once."

### Q4: "How did S3 strong consistency (Dec 2020) change pipeline design?"

**Before Dec 2020 (eventual consistency):**
```python
# Had to use this pattern to avoid reading stale data:
obj = s3.put_object(Bucket='bucket', Key='tmp/data.parquet')
s3.copy_object(Bucket='bucket', CopySource='bucket/tmp/data.parquet', Key='data.parquet')
s3.delete_object(Bucket='bucket', Key='tmp/data.parquet')
# Because a LIST after the PUT might not show the object, and
# a GET after the overwrite might return the old version
```

**After Dec 2020 (strong consistency):**
```python
# Simple overwrite works:
s3.put_object(Bucket='bucket', Key='data.parquet', Body=data)
# Immediately readable. LIST shows it. No stale reads.
```

**Impact:** Simplified pipeline code: no write-then-rename patterns,
no eventual consistency delays in athena/EMR. Most documentation
written pre-2020 contains workarounds that are no longer needed.

### Q5: "Design a fault-tolerant CDC pipeline from PostgreSQL to Snowflake."

```mermaid
flowchart LR
    PG["PostgreSQL<br/>WAL via Debezium"] --> K["Kafka<br/>retention=7d<br/>replication=3"]
    K --> F["Flink<br/>checkpoint=S3<br/>2PC sink"]
    F --> SF["Snowflake<br/>MERGE into fact"]

    subgraph "Failure scenarios"
        PG_FAIL["PG fails → Kafka has 7d of data; replay on restart"]
        K_FAIL["Broker fails → ISR re-election; min.insync ensures durability"]
        F_FAIL["Flink fails → restart from checkpoint; sink rolls back uncommitted"]
        SF_FAIL["Snowflake transient error → Flink retries; idempotent MERGE"]
    end
```

### Q6: "You have 100 TB of data across 1,000 partitions in Hive. One partition is 50 TB (skew). How do you fix it?"

**Diagnosis:**
```
Partition by date (yyyy-mm-dd):
  2024-01-01: 50 TB  ← 50% of all data, probably a backfill or bulk load
  2024-01-02: 20 GB
  2024-01-03: 15 GB
  ... 997 other partitions: 50 TB
```

**Fixes (in priority order):**
1. **Re-partition by a higher-cardinality key** (e.g., `customer_id % 1000 + date`)
   to distribute the large partition
2. **Sub-partition** the hot partition by an additional dimension (e.g.,
   `dt=2024-01-01/country=US/`)
3. **Use a bucketed table** in Hive: hash the key into N buckets within
   each partition
4. **If the skew is temporary** (one-time backfill): create a separate
   table for the large partition, union queries across both

### Q7: "Your Spark job writes the same events to S3 (for the lake) and Kafka (for real-time consumers). A failure mid-write leaves them inconsistent. How do you design for this?"

**The dual-write problem:** There is no atomic commit across S3 and
Kafka — no shared transaction coordinator exists.

```mermaid
flowchart TD
    DW["Dual-write inconsistency"]
    DW --> A["Option A: Single write + derive<br/>Write to Kafka ONLY.<br/>Lake populated by a consumer<br/>(Kafka→S3 connector or Flink).<br/>Kafka is the source of truth."]
    DW --> B["Option B: Single write + CDC<br/>Write to the lake (Iceberg) ONLY.<br/>Iceberg commit triggers<br/>downstream publish to Kafka.<br/>Lake is the source of truth."]
    DW --> C["Option C: Accept eventual consistency<br/>Write both, reconcile:<br/>hourly job compares S3 vs Kafka<br/>counts, backfills gaps.<br/>Cheap, but dashboards can<br/>disagree briefly."]
```

**Interview answer:** "Never dual-write to two systems you don't own
transactions for. Pick one system as the commit point and derive the
other. Option A (Kafka first) is the standard for streaming-first
architectures; Option B (lake first) for analytics-first."

### Q8: "Why can't you just use timestamps to order events in a distributed pipeline?"

| Approach | Problem |
|---|---|
| **Wall-clock timestamps** | Clock skew between machines (typically 10-250ms without tight NTP); two events can get identical or inverted timestamps |
| **NTP-disciplined clocks** | Better, but leap seconds + slew adjustments can move clocks backward |
| **TrueTime-style (Google Spanner)** | GPS/atomic clocks give bounded uncertainty (~7ms) — not available on commodity cloud VMs |

**What systems actually use:**
- **Lamport clocks / vector clocks:** logical ordering of causally
  related events (DynamoDB, Cassandra conflict resolution)
- **Single-writer sequencing:** one partition/leader assigns order
  (Kafka partition offsets) — sidesteps clock trust entirely
- **Hybrid logical clocks:** physical time + logical counter
  (CockroachDB, MongoDB cluster time)

**DE takeaway:** For event ordering, trust **partition assignment +
offset** (Kafka) or **sequence numbers from one authority**, not event
timestamps. Use timestamps for windowing (with watermarks for
lateness), never for correctness.

### Q9: "Cassandra cluster: RF=3, and you must survive 1 node failure with strong consistency on reads AND writes. Set W and R."

```
N = 3 replicas
Survive 1 failure → at least 2 nodes must serve every operation

Strong consistency requires W + R > N:
  W=2, R=2 → 4 > 3 ✓

Failure tolerance check (1 node down → N=2 available):
  Write needs W=2 → 2 available ✓ succeeds
  Read needs R=2 → 2 available ✓ succeeds

So W=2, R=2, RF=3 survives exactly 1 node failure with strong
consistency. A 2nd node failure makes BOTH reads and writes fail —
that's the CP trade.
```

**Follow-up interviewers ask:** "What if you need to survive 2 node
failures?" → RF must be 5 (W=3, R=3 → 6 > 5; with 2 down, 3 available
still satisfies both). **Replication factor is set by failure-tolerance
requirements, quorum by consistency requirements.**

---

## 9. Decision Trees — Whiteboard for Interview

### 9.1 Consistency Model Selection

```mermaid
flowchart TD
    Q["Strong or eventual consistency<br/>for this use case?"]
    Q --> REQ{"System requirement?"}

    REQ -->|"Financial transaction<br/>inventory, leader election"| STRONG["Strong consistency<br/>Cost: 2-5x latency<br/>W+R > N, RF = f(tolerance)"]
    REQ -->|"Dashboard, recommendations<br/>logs, analytics"| EVENTUAL["Eventual consistency<br/>Low latency, high avail<br/>W=1, R=1, tolerate partitions"]

    STRONG --> CP{"Can system tolerate<br/>unavailability during<br/>partition?"}
    CP -->|"Yes"| CP_OK["CP system: Kafka,<br/>ZooKeeper, etcd,<br/>Spanner, HBase"]
    CP -->|"No"| CA_WARN["CA is impossible in<br/>distributed systems<br/>— network partitions happen"]

    EVENTUAL --> AP{"Need conflict<br/>resolution?"}
    AP -->|"Yes"| LWW["Last-write-wins (DynamoDB)<br/>or CRDTs (Riako)"]
    AP -->|"No"| SIMPLE["Simple eventually consistent<br/>cache/CDN: just serve<br/>stale data"]
```

### 9.2 Exactly-Once Semantics Decision

```mermaid
flowchart TD
    Q["Exactly-once semantics needed?"]
    Q --> SOURCE{"Source supports<br/>idempotent replay?"}

    SOURCE -->|"No (e.g., webhook,<br/>UDP, flaky API)"| AT_LEAST["At-least-once +<br/>dedup in sink or staging<br/>— the practical default"]

    SOURCE -->|"Yes (Kafka with<br/>offset tracking)"| SINK{"Sink supports<br/>idempotent writes?"}

    SINK -->|"No (append-only<br/>log, no UPSERT)"| SINK_AT_LEAST["At-least-once +<br/>dedup downstream<br/>when reading"]

    SINK -->|"Yes (UPSERT,<br/>transactional DB)"| EXACTLY{"Checkpoint/transaction<br/>coordinator available?"}

    EXACTLY -->|"Flink + 2PC sink"| E1["Flink exactly-once<br/>checkpoint + 2PC commit"]
    EXACTLY -->|"Kafka producer<br/>idempotence"| E2["Kafka exactly-once<br/>enable.enable.idempotence=true<br/>+ acks=all"]
    EXACTLY -->|"Spark + transactional<br/>sink"| E3["Spark Structured Streaming<br/>end-to-end exactly-once<br/>(checkpoint + idempotent)"]
```

---

## 10. Quick Reference — Interview Edition

| Question | Answer |
|---|---|
| **Deduplicate pipeline?** | At-least-once + non-idempotent sink. Fix: UPSERT or dedup in staging |
| **CAP for Kafka?** | CP — consistent during partition, unavailable if ISR drops below min.insync |
| **CAP for Cassandra?** | AP — available during partition, eventually consistent |
| **S3 consistency?** | Strong since Dec 2020 (read-after-write). Legacy write-then-rename no longer needed |
| **Exactly-once real?** | Requires every component to support it. Most production: at-least-once + idempotent sink |
| **Skew fix?** | Salt the key (add random prefix before hash) or over-partition |
| **Kafka durability?** | `acks=all`, `min.insync.replicas=2`, `replication.factor=3` |
| **Spark fault tolerance?** | Lineage recomputation (no replication). Checkpoint truncates lineage |
| **Flink fault tolerance?** | Checkpoint + 2PC commit to sink. Restart rolls back uncommitted |
| **ZooKeeper vs KRaft?** | KRaft (Raft) replaces ZK: no external system, scales to 1M+ partitions |
| **Strong vs eventual?** | Cost: 2-5x latency for strong. Use strong for money, eventual for dashboards |
| **Hot partition fix?** | Salt the key, over-partition, or custom partitioner |
| **2PC in one line?** | Prepare (vote + lock) → commit (decision durable first); blocking, coordinator SPOF, rarely crosses system boundaries |
| **Dual-write S3+Kafka?** | Never. Write to one commit point, derive the other (Kafka-first or lake-first) |
| **Timestamps for ordering?** | No — clock skew. Use partition offsets, sequence numbers, or vector clocks |
| **RF vs quorum?** | RF set by failure tolerance, quorum (W+R>N) by consistency requirement |
| **2PC alternative?** | Optimistic concurrency + atomic swap (Iceberg), or idempotent at-least-once (Flink sinks) |
