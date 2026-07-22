# 2-Month Data Engineering Interview Sprint Plan

**Assumes ~2 hours/day on weekdays + 4-5 hours/day on weekends (~20-25 hrs/week).**
Adjust up/down based on your schedule — keep the weekly topic boundaries, compress depth.

---

## Phase 1: Core Foundations — Month 1

### Week 1 — SQL & Data Modeling

| Day | Focus | Activity |
|---|---|---|
| Mon | Window functions | `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `LEAD/LAG`, `SUM() OVER(...)` — write 5 queries |
| Tue | CTEs & Recursive queries | Org chart traversal, date spine generation |
| Wed | Joins & Anti-joins | INNER/LEFT/RIGHT/FULL, dedup with `LEFT JOIN ... IS NULL` |
| Thu | Query optimization | `EXPLAIN ANALYZE`, partition pruning, indexing, materialized views |
| Fri | Data modeling | Star vs snowflake, fact types, SCD Type 1/2/3, grain definition |
| Sat | SQL practice | 4-5 LeetCode/StrataScratch problems (medium/hard) |
| Sun | Data modeling drill | Design a dimensional model for an e-commerce or streaming event system |

**Checkpoint:** Can you write a recursive CTE, a moving average window query, and explain star vs snowflake tradeoffs in 2 minutes?

---

### Week 2 — PySpark & Spark Internals

| Day | Focus | Activity |
|---|---|---|
| Mon | Execution model | Lazy transforms vs actions, Catalyst optimizer, Tungsten |
| Tue | Shuffle & partitioning | `repartition()` vs `coalesce()`, partition pruning, shuffle triggers |
| Wed | Joins | Broadcast vs sort-merge, skew handling (salting) |
| Thu | Memory & serialization | Execution vs storage memory, Kryo vs Java, checkpointing |
| Fri | Spark SQL vs DataFrame API | Read `notes.md` + write 3 examples of each |
| Sat | PySpark coding | Run 3-4 exercises from `apache-spark-pyspark/` against local data |
| Sun | Review & weak spots | Re-read any Spark topic you couldn't explain clearly |

**Checkpoint:** Can you explain what happens from `df.filter(...).groupBy(...).agg(...).show()` through to output — covering Catalyst, shuffle, and memory?

---

### Week 3 — Python for DE + DSA (Arrays, Hashing, Two Pointers)

| Day | Focus | Activity |
|---|---|---|
| Mon | Python review | Generators, context managers, decorators, file I/O (Parquet/CSV/JSON) |
| Tue | DSA: Arrays | Two pointers, prefix sums — solve 2 LeetCode problems |
| Wed | DSA: Hashing | Frequency maps, grouping — solve 2 LeetCode problems |
| Thu | DSA: Sliding Window | Fixed + variable window — solve 2 problems |
| Fri | DSA: Kadane + Practice | Maximum subarray, mix of 2-3 easy/medium problems |
| Sat | Python + DSA mixed | Groupby/merge/pivot in pandas, 1 DSA problem |
| Sun | Review | Redo any problem you found hard; re-read Python patterns |

**Checkpoint:** Can you implement a sliding window max sum and a two-sum variant in 15 minutes with correct edge cases?

---

### Week 4 — DSA (Linked Lists, Trees, Stacks/Queues)

| Day | Focus | Activity |
|---|---|---|
| Mon | Linked Lists | Fast/slow pointer, reversal, merge two sorted lists |
| Tue | Trees (DFS) | Max depth, invert, validate BST |
| Wed | Trees (BFS) | Level order, right side view |
| Thu | Stacks & Queues | Valid parentheses, min stack, LRU cache design |
| Fri | DSA mixed practice | 3 LeetCode mediums mixing all week's topics |
| Sat | Timed mock | 2 LeetCode mediums in 45 min (simulate interview) |
| Sun | Review & weak spots | Revisit patterns you struggled with |

**Checkpoint:** Can you detect a cycle in a linked list, invert a binary tree, and design an LRU cache from scratch?

---

## Phase 2: Systems & Polish — Month 2

### Week 5 — Kafka, Flink & Streaming

| Day | Focus | Activity |
|---|---|---|
| Mon | Kafka fundamentals | Partitions, offsets, consumer groups, rebalancing, semantics |
| Tue | Kafka deep | Topic design, key-based partitioning, DLQs, Kafka Connect |
| Wed | Flink fundamentals | Windowing types, watermarks, event-time vs processing-time |
| Thu | Flink state & checkpointing | Keyed state, operator state, exactly-once with 2PC |
| Fri | Streaming concepts | Lambda vs Kappa, CDC (Debezium), backpressure, schema evolution |
| Sat | Read + annotate | Go through `apache-kafka/notes.md` + `apache-flink/` notes |
| Sun | Mock Q&A | Answer 5 streaming questions aloud (record yourself if helpful) |

**Checkpoint:** Can you explain exactly-once semantics in Kafka + Flink, including what 2PC means and where failures can occur?

---

### Week 6 — System Design

| Day | Focus | Activity |
|---|---|---|
| Mon | Framework | Practice the CDPF structure: Clarify → Design → Potholes → Finalize |
| Tue | Design: real-time pipeline | E-commerce analytics, clarify throughput/latency/correctness |
| Wed | Design: batch + streaming | Data platform supporting both, how does storage work? |
| Thu | Design: log aggregation | Company-wide observability, think about scale + cost |
| Fri | Design: feature store | ML feature serving, offline vs online, freshness requirements |
| Sat | Deep drill: failure scenarios | Duplicate records, schema changes, petabyte recovery under SLA |
| Sun | Mock design session | Pick a new scenario, timebox 45 min, present aloud |

**Checkpoint:** Can you walk through a real-time pipeline design end-to-end, making explicit tradeoffs at each decision point?

---

### Week 7 — Cloud (AWS) & Modern Stack

| Day | Focus | Activity |
|---|---|---|
| Mon | AWS compute | EMR (instance fleets, spot), Glue (crawlers, jobs, bookmarks) |
| Tue | AWS storage & query | S3 + Athena (partitioning, CTAS, billing), Redshift (dist/sort keys, Spectrum) |
| Wed | dbt | Materializations, incremental models, testing, docs |
| Thu | Airflow / Dagster | DAG patterns, idempotency, backfills, SLA handling, sensors vs operators |
| Fri | Data quality & governance | Great Expectations, data contracts, lineage, SLOs |
| Sat | Cost optimization | Spot instances, storage tiering, query cost reduction, reserved vs on-demand |
| Sun | Review & compare | Map each technology to a use case — know *why* not just *what* |

**Checkpoint:** Can you explain when you'd choose EMR over Glue, Redshift over Athena, and how dbt incremental models work under the hood?

---

### Week 8 — Behavioral, Mocks & Final Polish

| Day | Focus | Activity |
|---|---|---|
| Mon | STAR stories | Draft 3 stories: pipeline break/fix, technical decision to non-tech stakeholder, conflict |
| Tue | Refine stories | Cut each to 90 seconds, emphasize your specific contribution + metric |
| Wed | Full mock interview 1 | SQL + DSA + System Design (use a friend or self-record) |
| Thu | Full mock interview 2 | Behavioral + PySpark + Streaming |
| Fri | Weak spot review | Re-read any section where you stumbled in mocks |
| Sat | DSA quick review | 1 problem per pattern (arrays, hashing, trees, linked lists) |
| Sun | Rest + logistics | Confirm setup (coderpad/zoom, camera, water), review company-specific rubric |

**Checkpoint:** Can you deliver all 3 STAR stories smoothly, solve a medium LeetCode in 20 min, and walk through a system design end-to-end without notes?

---

## Daily Commitment Reference

| Time Available | Recommended Intensity |
|---|---|
| 1 hr/day | Drop DSA from weeks 3-4, spread across 12 weeks instead |
| 2-3 hrs/day | Stick to plan as-is |
| 4+ hrs/day | Add a second DSA problem daily + extra system design drill on weekends |

## How to Use This Plan

1. **Adjust, don't abandon.** If a topic takes longer, shift it. Don't skip the checkpoint at week end.
2. **Mock early, mock often.** Start speaking answers aloud by week 2. Week 1 SQL answers count.
3. **Track your progress.** Use `interview-prep/progress-checklist.md` alongside this plan.
4. **Week 8 is not optional.** The polish week is where recall becomes fluent. Don't skip mocks.
