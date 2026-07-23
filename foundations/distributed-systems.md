# Distributed Systems for Data Engineers

Core concepts every DE needs to reason about data pipelines, storage,
and compute at scale.

---

## 1. CAP Theorem

A distributed system can provide at most **two** of three guarantees:

```
          Consistency (C)
              │
              ├── All nodes see the same data at the same time
              │
    CP ───────┼────── AP
    (Consistent +   (Available +
    Partition-       Partition-
    tolerant)        tolerant)
              │
              ├── CA (impossible in real systems — network
              │    partitions always happen)
              │
          Availability (A) ←────────────────── Partition Tolerance (P)
              Every request gets          System works despite
              a response (not             network failures
              necessarily latest)

```

**Real-world examples:**
| System | Category | Tradeoff |
|---|---|---|
| HDFS | CP | Blocks writes during NameNode failover |
| Cassandra | AP | Eventually consistent reads (tunable) |
| DynamoDB (default) | AP | Eventually consistent reads (opt-in strong) |
| S3 (current) | CP | Strong consistency since Dec 2020 |
| Kafka | CP | Consistent with min.insync.replicas |
| EMRFS (historical) | CP | Used DynamoDB for consistency (now deprecated) |

> [!WARNING]
> CAP is a simplification. Real systems are **PA/EL** (available during
> partition, eventually consistent) or **PC/EC** (consistent during
> partition, tolerate unavailability). Always ask: *What happens during
> a network partition?*

---

## 2. Consistency Models

| Model | Guarantee | Example |
|---|---|---|
| **Strong (linearizable)** | Read returns the latest write | Single-node DB, ZooKeeper |
| **Read-after-write** | Client reads its own writes | S3 (since 2020) |
| **Eventual** | Reads eventually converge | DNS, S3 pre-2020 |
| **Causal** | Causally related ops are ordered | CRDTs, DynamoDB session tracking |
| **Read-your-writes** | After write, subsequent reads by same client see it | Many distributed caches |

**DE relevance:** Understanding consistency helps you choose between
batch (strong) and streaming (eventual) patterns, and debug data
discrepancies.

---

## 3. Partitioning / Sharding

### Horizontal Partitioning (Sharding)

Rows distributed across nodes by a **partition key**.

| Strategy | How It Works | Example | Gotcha |
|---|---|---|---|
| Hash | `hash(key) % N` | Kafka partition by `user_id` | Adding nodes reshuffles data |
| Range | Sort key into ranges | HBase/Presto table scans | Hot spots on skewed keys |
| List | Predefined buckets | `country IN ('IN', 'US')` | Uneven data distribution |
| Directory | Date-based prefixes | `s3://bucket/dt=2026-01-01/` | Requires partition pruning |

**Skew (hot spots):**
```python
# Bad: popular customer_id causes one partition to handle 90% of traffic
partition_id = hash(customer_id) % 8

# Better: salting spreads the load
salted_key = f"{customer_id}_{random.randint(0, 10)}"
partition_id = hash(salted_key) % 8
```

### Partitioning in Distributed Query Engines

| Engine | Shuffle Mechanism | Partition Control |
|---|---|---|
| Spark | Hash-based shuffle | `repartition(n)`, `coalesce(n)`, `partitionBy` |
| Trino/Presto | Hash distributed via exchange operator | `PARTITION BY` in window, `DISTRIBUTE BY` |
| Flink | KeyBy → hash partitioning | `keyBy()`, `partitionCustom()` |
| Kafka | Topic partitions | Producer key, partitioner class |

---

## 4. Replication

| Strategy | How | Durability | Consistency | Example |
|---|---|---|---|---|
| **Leader-follower** | Writes to leader, reads from followers | High | Strong on leader, eventual on followers | PostgreSQL, Kafka (per partition) |
| **Leaderless** | Writes to all replicas, read quorum | Very high | Tunable (quorum) | Cassandra, DynamoDB |
| **Single-leader** | One leader, async/sync followers | Configurable | Strong if sync | MySQL, HDFS |

### Quorum

```
W + R > N    where N = number of replicas
                  W = write quorum (nodes that must acknowledge write)
                  R = read quorum (nodes that must respond to read)

Example: N=3, W=2, R=2 → strong consistency (2+2 > 3)
Example: N=3, W=1, R=1 → eventual consistency (1+1 < 3)
```

---

## 5. Consensus Algorithms

### Paxos vs Raft

| Aspect | Paxos | Raft |
|---|---|---|
| Understandability | Notorious (hard to implement correctly) | Designed for teachability |
| Leader election | Not built-in (mechanism) | Explicit leader election |
| Log replication | Yes | Yes |
| Production use | Google Chubby, Spanner | etcd, Consul, Kafka KRaft |

**DE relevance:** Kafka KRaft replaces ZooKeeper with a Raft-based
consensus. Understanding Raft helps with Kafka/Kafka Connect
operations.

### Raft simplified

```
1. Leader Election: Nodes vote; one becomes leader
2. Log Replication: Leader appends entries, replicates to followers
3. Commitment: Entry is committed when majority acknowledges
4. Safety: Only leader with latest term can become leader
```

---

## 6. Consistency in Data Engineering Practice

| DE Component | What It Guarantees | What Can Go Wrong |
|---|---|---|
| S3 | Strong since Dec 2020 | Eventually consistent pre-2020 (legacy docs mention this) |
| Kafka | Per-partition ordered, strongly consistent with `acks=all` + `min.insync.replicas` | Out-of-order across partitions |
| Spark | Fault-tolerant via lineage + checkpoint | Output commit issues (committer choice matters) |
| Snowflake | Strong consistency within warehouse | Cross-region replication is asynchronous |
| Iceberg | Snapshot isolation (read consistent snapshot) | Concurrent writers need retry (optimistic concurrency) |
| Flink | Exactly-once with checkpointing + 2PC | Sink must support idempotent writes |

---

## Quick Reference

| Concept | Key Takeaway |
|---|---|
| CAP | You can't have all three; know what your system gives up |
| Consistency | Strong vs eventual — each has a use case |
| Partitioning | Hash for even distribution, range for efficient scans |
| Skew (hot spots) | Salt your keys, monitor partition sizes |
| Replication | W+R > N for strong consistency (quorum) |
| Consensus | Raft is the modern default (KRaft, etcd) |
| Practical DE | Batch prefers strong consistency, streaming prefers eventual |

>

---

> [!TIP]
> The most common DE interview question on distributed systems: "Your
> pipeline produces duplicate records. Why?" — The answer is almost
> always about an inconsistency between write and read paths
> (at-least-once delivery + non-idempotent sink).
