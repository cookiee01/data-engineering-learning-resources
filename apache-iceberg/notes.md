# Apache Iceberg — Interview Prep Notes

> Format: Senior DE (Alex) ↔ Staff DE (Sam) conversation series.
> Goal: Deep understanding for production use and senior/staff-level interviews.

---

## Table of Contents

1. [The Opening Question](#1-the-opening-question)
2. [Why Iceberg? (vs Hive Format)](#2-why-iceberg-vs-hive-format)
3. [Iceberg Metadata Architecture](#3-iceberg-metadata-architecture)
4. [Hidden Partitioning](#4-hidden-partitioning)
5. [Row-Level Updates: CoW vs MoR](#5-row-level-updates-cow-vs-mor)
6. [Time Travel & Snapshot Cleanup](#6-time-travel-snapshot-cleanup)
7. [ACID Commits & Concurrent Writers](#7-acid-commits-concurrent-writers)
8. [Schema Evolution & Field IDs](#8-schema-evolution-field-ids)
9. [Real Interview Questions](#9-real-interview-questions)
10. [Decision Trees](#10-decision-trees)
11. [Operational Maintenance Playbook](#11-operational-maintenance-playbook)
12. [Quick Reference — Interview Edition](#12-quick-reference--interview-edition)
13. [Resources](#13-resources)

---

## 1. The Opening Question

**Question:** *"Your company has 2 PB of data on S3 queried by Spark, Trino, and Snowflake. The Hive metastore is the bottleneck and a crashed job just corrupted a table again. Design the target state."*

```mermaid
flowchart LR
    subgraph Before["Before: Hive on S3"]
        H1["Directories = tables<br/>LIST calls on every query"]
        H2["No ACID: crashed job<br/>= partial files in place"]
        H3["Schema change =<br/>rewrite or corruption"]
        H4["dt column must be<br/>in every WHERE clause"]
    end

    subgraph After["After: Iceberg on S3"]
        I1["Catalog pointer → metadata JSON<br/>No LIST calls — file-level index"]
        I2["ACID: atomic pointer swap<br/>crashed job = orphan files, clean later"]
        I3["Schema evolution via field IDs<br/>rename/reorder = metadata-only"]
        I4["Hidden partitioning<br/>days(event_time) prunes automatically"]
    end

    Before -->|"migrate"| After

    subgraph Engines["Same table, three engines"]
        E1["Spark: batch ETL"]
        E2["Trino: interactive BI"]
        E3["Snowflake: external catalog<br/>(read Iceberg tables)"]
    end

    After --> Engines
```

**Answer structure:**
```
1. Table format (Iceberg) decouples the table from the engine and
   from the directory layout — the metadata tree is the table
2. One copy of data, three engines reading it, no format lock-in
3. ACID via catalog CAS — crashes leave orphans, never corruption
4. Migration path: shadow table + backfill + cutover (see Q6)
```

---

## 2. Why Iceberg? (vs Hive Format)

### The Core Problem with Hive

In Hive, **the directory IS the table**. Files are discovered by listing directories on S3/HDFS.

| Problem | Detail |
| :--- | :--- |
| **Slow metadata** | Listing files is `O(N)` on object storage — extremely slow at scale |
| **No ACID** | A crashed Spark job mid-write leaves partial/corrupt data in directories |
| **Fragile schema evolution** | Renaming a column breaks existing data or forces full rewrites |
| **Partition must be in query** | Users must know physical layout to get partition pruning |

### Iceberg's Core Insight

> **The table is defined by a canonical list of files, not a directory structure.**

Iceberg tracks every data file at the metadata layer. This enables:
- ✅ Full ACID transactions (atomic commits via snapshot isolation)
- ✅ Time travel (every write creates an immutable snapshot)
- ✅ Schema evolution (rename, reorder, add, drop columns safely)
- ✅ Hidden partitioning (automatic partition pruning, no user burden)
- ✅ Partition evolution (change partitioning strategy without rewriting data)

---

## 3. Iceberg Metadata Architecture

When Spark/Trino reads an Iceberg table, it traverses a **4-tier metadata tree**:

```mermaid
graph TD
    Catalog[Catalog<br/>Glue / Hive Metastore / Nessie]
    MJ[Metadata JSON<br/>.json file]
    ML[Manifest List<br/>.avro — one per snapshot]
    MF[Manifest File<br/>.avro — one per write batch]
    DF[Data Files<br/>.parquet / .orc]

    Catalog -->|pointer to current<br/>metadata pointer| MJ
    MJ -->|schema, partition spec,<br/>snapshot history| ML
    ML -->|partition min/max stats,<br/>list of manifests| MF
    MF -->|column-level stats,<br/>list of data + delete files| DF

    style Catalog fill:#f59e0b,color:#fff
    style MJ fill:#3b82f6,color:#fff
    style ML fill:#10b981,color:#fff
    style MF fill:#6b7280,color:#fff
    style DF fill:#8b5cf6,color:#fff
```

**Why this matters for query planning:**

A query engine uses the stats at each layer to **prune aggressively before reading any data**:
1. Manifest List stats → skip entire manifests whose partitions don't overlap the filter
2. Manifest File stats → skip individual Parquet files whose column ranges don't overlap

This is far more powerful than Hive's directory listing approach.

---

## 4. Hidden Partitioning

### Problems with Hive Partitioning

**Hive table creation forces a redundant column:**
```sql
CREATE TABLE events (
    user_id    BIGINT,
    event_type STRING,
    event_time TIMESTAMP,
    amount     DOUBLE
)
PARTITIONED BY (dt STRING);  -- redundant! event_time already contains the date
```

**Problem 1 — Data can go out of sync:**
```sql
-- Bad ETL writes row to wrong partition!
INSERT INTO events PARTITION (dt='2026-07-01')
VALUES (1, 'click', '2026-07-14 10:30:00', 5.0);
-- event_time says July 14, but it's in the July 1 partition. Silent data corruption.
```

**Problem 2 — Users must know physical layout:**
```sql
-- This causes a FULL TABLE SCAN because filter is on event_time, not dt
SELECT * FROM events WHERE event_time >= '2026-07-01';

-- Users MUST write this to get pruning:
SELECT * FROM events WHERE dt >= '2026-07-01' AND event_time >= '2026-07-01';
```

**Problem 3 — Changing partition strategy requires full data rewrite:**
- Daily → Hourly? Rewrite petabytes, swap table references, pray nothing breaks.

---

### Partition Transforms

Iceberg defines partitioning as a **transform applied to an existing column** — not a new column:

```sql
CREATE TABLE events (
    user_id    BIGINT,
    event_type STRING,
    event_time TIMESTAMP,   -- only ONE timestamp column, no 'dt'
    amount     DOUBLE
)
USING iceberg
PARTITIONED BY (days(event_time));  -- 'days()' is a transform, not a column
```

| Transform | Input | Output | Best For |
| :--- | :--- | :--- | :--- |
| `identity(col)` | Any | Exact value | Low-cardinality cols (e.g., country, status) |
| `days(col)` | Timestamp | Integer day since epoch | Day-level time-series |
| `hours(col)` | Timestamp | Integer hour since epoch | High-frequency streaming |
| `months(col)` | Timestamp | Integer month since epoch | Monthly reporting tables |
| `years(col)` | Timestamp | Integer year since epoch | Long-lived archival tables |
| `bucket(N, col)` | Any | Integer in `[0, N)` | High-cardinality join keys |
| `truncate(W, col)` | String/Int | Trimmed prefix/range | String prefix range scans |

---

### Write Path & Read Path

**Write Time** (row with `event_time = '2026-07-14 10:30:00'`):

```
1. Iceberg computes: days('2026-07-14 10:30:00') → 20284 (days since epoch)

2. Writes row to:
   s3://bucket/warehouse/events/data/event_time_day=20284/0001.parquet
   
   NOTE: The Parquet file contains the original 'event_time' column, NOT 'dt'.
         The partition value 20284 exists ONLY in the manifest metadata.

3. Manifest File records this file with partition value: 20284
```

**Read Time** (user queries `WHERE event_time >= '2026-07-01' AND event_time < '2026-07-08'`):

```
Query Engine:

1. Reads Manifest List → finds all Manifest Files
2. For each Manifest File, checks partition stats (using days() transform on filter bounds):
   - Manifest A: partition range [20266, 20273]  (July 1–7)  → INCLUDE ✅
   - Manifest B: partition range [20250, 20265]  (June 15–30) → SKIP   ❌
   - Manifest C: partition range [20274, 20284]  (July 9–14)  → SKIP   ❌

3. Reads only Manifest A → gets list of Parquet files

4. For each Parquet file, checks column-level stats:
   - File 001: event_time min=July1, max=July1  → INCLUDE ✅
   - File 002: event_time min=July3, max=July7  → INCLUDE ✅

5. Scans only 2 files. User wrote a normal WHERE clause. No awareness of partitioning needed.
```

---

### Partition Evolution

Change partitioning strategy with **zero data rewrites**:

```sql
-- Switch from daily to hourly partitioning
ALTER TABLE events
REPLACE PARTITION FIELD days(event_time) WITH hours(event_time);
```

**What happens internally:**

```
Before (Partition Spec ID: 1):         After (Partition Spec ID: 2):
  days(event_time)                       hours(event_time)

Old files (untouched):                 New files (going forward):
  data/event_time_day=20266/             data/event_time_hour=486384/
  data/event_time_day=20267/             data/event_time_hour=486385/
  ...                                    ...
```

Each Manifest File stores its **Spec ID**. At query time, Iceberg evaluates the filter against:
- Old manifests using Spec ID 1 (days transform) → correct pruning on old data
- New manifests using Spec ID 2 (hours transform) → correct pruning on new data

**Result: No downtime. No rewrite. No migration. Both old and new data queryable with the same SQL filter.**

---

### Buckets vs Identity

**Never use `identity()` on high-cardinality columns:**
```
identity(user_id) with 10 million users →
  data/user_id=1/
  data/user_id=2/
  ...
  data/user_id=10000000/    ← 10M tiny partitions, S3 listing explosion!
```

**Use `bucket(N, col)` instead:**
```
bucket(100, user_id):
  user_id=1   → hash(1)  % 100 = bucket 37
  user_id=2   → hash(2)  % 100 = bucket 91
  user_id=50  → hash(50) % 100 = bucket 37   (same bucket, different user)

  data/user_id_bucket=37/   ← only 100 partitions total, evenly distributed
  data/user_id_bucket=91/
```

**Bonus: Co-located Joins.** If two large tables are both bucketed by `bucket(100, user_id)`, the query engine can join bucket 37 from table A with bucket 37 from table B on each executor — **no full shuffle needed**.

---

### Common Mistakes

**Mistake 1 — Over-partitioning:**
```sql
-- BAD: 24 hours × 50 countries × 10 device_types = 12,000 partitions/day
PARTITIONED BY (hours(event_time), identity(country), identity(device_type))
```
- Each partition has tiny files → manifest overhead explodes
- **Rule of thumb:** Each partition file should be 128MB–512MB minimum

**Mistake 2 — Partition strategy misaligned with query patterns:**
```sql
-- You partition by user_id bucket, but 90% of queries filter by event_time
PARTITIONED BY (bucket(100, user_id))
-- Result: zero partition pruning for your most common queries!
```
Always ask: *"What does 90% of my WHERE clause look like?"* — partition for that.

---

## 5. Row-Level Updates: CoW vs MoR

Iceberg supports two strategies for `UPDATE` and `DELETE`. Choose based on read/write ratio.

| Feature | **Copy-on-Write (CoW)** | **Merge-on-Read (MoR)** |
| :--- | :--- | :--- |
| **How it works** | Rewrites entire data file containing affected rows immediately | Writes a separate Delete File; original data file untouched |
| **Write perf** | Slower (high write amplification) | Very fast (minimal write amplification) |
| **Read perf** | Fast (normal Parquet scan) | Slower (engine merges data + delete files at read time) |
| **Best for** | Read-heavy, infrequent updates (historical analytical tables) | Write-heavy, CDC pipelines, near-real-time streaming |

### Delete File Types

**Position Deletes:**
- Delete file contains: `(file_path, row_position)` pairs
- At read time: engine does an anti-join on row positions
- Fast to read, slightly slower to write (must look up positions)

**Equality Deletes:**
- Delete file contains: column-value pairs (e.g., `id = 123`)
- At read time: engine scans data files and filters out matching rows
- Extremely fast to write (ideal for high-throughput streaming), higher read cost

> **Production note:** With many MoR deletes accumulating over time, run **compaction** regularly
> to merge data files and delete files into clean, rewritten Parquet files (restores CoW-like read perf).

```sql
-- Spark compaction via Iceberg's rewrite procedure
CALL catalog.system.rewrite_data_files(
  table => 'my_db.events',
  strategy => 'binpack',
  options => map('min-file-size-bytes', '134217728')  -- 128MB
);
```

---

## 6. Time Travel & Snapshot Cleanup

Every write operation creates an immutable **Snapshot**. Old snapshots and their data files are retained until explicitly expired.

**Querying historical data:**
```sql
-- By timestamp
SELECT * FROM events FOR SYSTEM_AS_OF '2026-07-01 12:00:00';

-- By snapshot ID (from metadata history)
SELECT * FROM events FOR VERSION AS OF 8494399784576965614;

-- List all snapshots
SELECT * FROM events.snapshots;
```

**Expire old snapshots (run as a scheduled maintenance job):**
```sql
-- Expire snapshots older than 7 days, keep at least 5 recent ones
CALL catalog.system.expire_snapshots(
  table => 'my_db.events',
  older_than => TIMESTAMP '2026-07-07 00:00:00',
  retain_last => 5
);
```

This physically **deletes orphaned Parquet files from S3** that are no longer referenced by any active snapshot. Without this, storage costs compound indefinitely.

**Remove orphan files (safety net):**
```sql
-- Clean up files that exist on disk but are not tracked in any snapshot
CALL catalog.system.remove_orphan_files(table => 'my_db.events');
```

---

## 7. ACID Commits & Concurrent Writers

**Alex:** In interviews, people say Iceberg has ACID transactions on S3. But S3 does not support atomic directory rename like HDFS. What is actually atomic?

**Sam:** The atomic operation is not a file rename. It is the **catalog pointer swap** from the old metadata JSON to the new metadata JSON. Data files are written first, metadata is prepared next, and only then does the writer try to commit by updating the catalog pointer.

```mermaid
sequenceDiagram
    participant W as Writer Job
    participant S as Object Store
    participant C as Catalog

    W->>S: Write new data files
    W->>S: Write new manifest files
    W->>S: Write new metadata JSON
    W->>C: Compare-and-swap table pointer
    alt pointer unchanged
        C-->>W: Commit succeeds
    else another writer committed first
        C-->>W: Commit conflict
        W->>C: Refresh latest metadata and retry/abort
    end
```

**Alex:** So readers never see half-written files?

**Sam:** Correct. Readers start from the catalog's current metadata pointer. Until the pointer changes, new files are invisible even if they already exist in S3. If a job crashes before commit, those files are orphan files and can be cleaned later.

**Alex:** What conflicts are detected?

**Sam:** Iceberg uses optimistic concurrency. Two append-only writers can often both succeed after retry. But if one writer rewrites or deletes files that another writer also touched, Iceberg detects that the new snapshot is no longer based on the expected file set and rejects the unsafe commit.

---

## 8. Schema Evolution & Field IDs

**Alex:** Why is Iceberg safer than Hive for schema changes?

**Sam:** Iceberg tracks columns by stable **field IDs**, not just by column names or positions. That is why rename and reorder operations are metadata-only and do not corrupt old files.

```mermaid
flowchart LR
    A["Field ID 1<br/>user_id"] --> A2["Field ID 1<br/>customer_id"]
    B["Field ID 2<br/>event_time"] --> B2["Field ID 2<br/>event_time"]
    C["Field ID 3<br/>amount"] --> C2["Field ID 3<br/>amount"]
```

**Alex:** Give me the interview answer for rename.

**Sam:** In Hive-style tables, a rename can be ambiguous because readers may bind by name or position depending on file format and engine behavior. In Iceberg, `user_id` can be renamed to `customer_id` while keeping the same field ID. Old Parquet files do not need to be rewritten because the table metadata maps the current name to the same logical field.

**Safe evolution examples:**
```sql
ALTER TABLE events RENAME COLUMN user_id TO customer_id;
ALTER TABLE events ADD COLUMN device_type STRING;
ALTER TABLE events ALTER COLUMN amount TYPE DECIMAL(18, 2);
```

**Be careful with:**
- Dropping a column and later re-adding a column with the same name. It will get a new field ID, so it is a different logical column.
- Type changes that are not widening conversions. Validate engine support before production rollout.
- Nested struct changes. Iceberg supports them, but downstream engines and BI tools may lag.

---

## 9. Real Interview Questions

### Q1: "Iceberg vs Delta Lake vs Hudi — how do you choose?"

| Dimension | Iceberg | Delta Lake | Hudi |
|---|---|---|---|
| **Engine neutrality** | Best-in-class: Spark, Trino, Flink, Snowflake, BigQuery read the same table | Databricks-first; open-source Delta lags on non-Spark engines | Spark/Flink-first; Trino support weaker |
| **Metadata design** | Manifest tree (Avro) — engine-agnostic spec | Transaction log (`_delta_log` JSON) | Timeline-based metadata |
| **Partition evolution** | Yes, first-class (spec IDs) | No — change partitioning = rewrite | No |
| **Hidden partitioning** | Yes (transforms) | No (partition columns, but generated columns help) | No |
| **Streaming upserts** | Good (MoR + Flink) | Good (MERGE) | Best-in-class (built for CDC upserts) |
| **Vendor momentum** | Snowflake, Databricks (UniForm), Tabular, AWS | Databricks | Onehouse |

**Interview answer:** "Iceberg when engine neutrality matters — multiple
engines, avoiding lock-in, partition evolution. Delta when you're
all-in Databricks. Hudi when the primary workload is high-frequency
CDC upserts and the team already runs it. In 2026 the default for a
new multi-engine lakehouse is Iceberg."

### Q2: "Your Iceberg table has 50,000 small files after 3 months of streaming. Queries take 10 minutes. Diagnose and fix."

```mermaid
flowchart TD
    SLOW["10-minute queries"]
    SLOW --> D1["Diagnosis 1: planning slow?<br/>EXPLAIN shows minutes in<br/>'planning' phase → manifest<br/>explosion → rewrite_manifests"]
    SLOW --> D2["Diagnosis 2: scan slow?<br/>50K files × S3 GET latency<br/>→ rewrite_data_files (binpack)"]
    SLOW --> D3["Diagnosis 3: MoR deletes<br/>accumulated → merge cost at<br/>read → rewrite_data_files<br/>applies deletes"]

    D1 --> F["Fix chain:"]
    D2 --> F
    D3 --> F
    F --> F1["1. CALL system.rewrite_data_files<br/>(target 256-512 MB files)"]
    F1 --> F2["2. CALL system.rewrite_manifests<br/>(collapse manifest tree)"]
    F2 --> F3["3. Schedule BOTH as recurring jobs<br/>— streaming without scheduled<br/>compaction ALWAYS ends here"]
    F3 --> F4["4. Root-cause: reduce write<br/>frequency or increase<br/>write.batch.size upstream"]
```

### Q3: "Two Spark jobs write to the same Iceberg table at the same time. Job A appends, Job B deletes. What happens?"

```mermaid
sequenceDiagram
    participant A as Job A (append)
    participant B as Job B (delete)
    participant C as Catalog

    A->>A: Read snapshot S1, write files
    B->>B: Read snapshot S1, write delete files
    A->>C: CAS: S1 → S2 (append)
    C-->>A: ✓ Commit success
    B->>C: CAS: S1 → S2 (delete)
    C-->>B: ✗ Conflict — pointer is S2 now
    B->>B: Refresh to S2, re-validate:<br/>do my deletes still apply to<br/>files untouched by A's append?
    alt No overlap (A appended new files,<br/>B deleted old rows)
        B->>C: CAS: S2 → S3 (rebased)
        C-->>B: ✓ Commit success
    else Overlap (A rewrote files B targeted)
        B->>B: Retry whole write<br/>or fail after max retries
    end
```

**Key:** Iceberg's optimistic concurrency does **conflict detection at
the file level**, not row level. Non-overlapping writes can both
succeed after rebase; overlapping writes retry. No locks, no blocking —
which is why it scales on S3.

### Q4: "GDPR request: delete all data for customer 42 across your lake. Tables are Iceberg on S3. Walk through it."

```
1. Identify tables with customer data (data catalog / lineage scan)

2. Delete at the format level per table:
   DELETE FROM table WHERE customer_id = 42;
   → MoR: writes equality delete files (fast, logical delete)
   → CoW: rewrites affected data files (slow, physical delete)

3. GDPR requires PHYSICAL deletion — MoR delete files are not enough:
   → run rewrite_data_files to materialize deletes into clean files
   → run expire_snapshots with older_than < request_date
     (old snapshots still contain the customer's data!)
   → run remove_orphan_files to drop unreferenced files

4. Verify: query all snapshots history; confirm files physically gone
   (orphan check + S3 prefix audit)

5. Watch out: derived tables, cached query results, and
   BI extracts also contain the data — lineage matters
```

**Interview trap:** "We ran DELETE, we're compliant." — No. Snapshots
retain the data until expired. Time travel and GDPR are in tension:
**your snapshot retention window is your maximum deletion latency.**

### Q5: "A Flink job commits to Iceberg every 30 seconds. After 2 weeks, query planning takes 40 seconds. Why, and fix?"

```
Math:
  30s per commit × 2 commits/min × 60 × 24 × 14 days
  = 40,320 snapshots
  Each snapshot = 1 manifest list + manifests
  → 40K+ metadata files; planner walks the tree per query

Fix (in order):
1. expire_snapshots(older_than => 7 days, retain_last => 10)
   → drops old manifest lists; planning time collapses
2. rewrite_manifests → compact surviving manifests
3. Reduce commit cadence upstream:
   checkpoint interval 30s → 5min (600 snapshots/day not 2,880)
   (trade: recovery granularity)
4. Set table properties so retention is automatic:
   'history.expire.max-snapshot-age-ms' = '604800000'  -- 7 days
   'history.expire.min-snapshots-to-keep' = '10'
```

### Q6: "Migrate a 500 TB Hive table to Iceberg with zero downtime. Plan?"

```mermaid
flowchart TD
    P1["Phase 1: Shadow table<br/>CREATE TABLE events_iceberg<br/>USING iceberg AS SELECT from hive<br/>LIMIT 0 (schema only)"]
    P1 --> P2["Phase 2: Historical backfill<br/>Spark job copies 500 TB<br/>partition-by-partition, validating<br/>row counts + checksums"]
    P2 --> P3["Phase 3: Dual-write<br/>ETL writes to BOTH hive + iceberg<br/>for new data (1-2 weeks)"]
    P3 --> P4["Phase 4: Validation<br/>Compare query results hive vs iceberg<br/>(revenue queries first)"]
    P4 --> P5["Phase 5: Cutover<br/>Point BI/ETL readers to iceberg<br/>Keep hive read-only as fallback"]
    P5 --> P6["Phase 6: Decommission<br/>After 30 days clean, drop hive table<br/>(files still on S3 — delete via lifecycle)"]
```

**Alternative for brave teams:** in-place migration (`migrate` Spark
procedure converts Hive → Iceberg by registering existing files in
Iceberg metadata — no data copy). Fast but: no re-layout, old files
keep Hive partitioning semantics, and rollback is painful. Use shadow
migration for anything business-critical.

### Q7: "Same query runs slower on Iceberg than on the old Hive table. Both on S3, same files. Why?"

**Likely causes:**
1. **Planning overhead:** Hive's metastore partition pruning was fast
   because the table had few partitions; Iceberg's manifest tree walk
   (S3 GETs per manifest) is slower for tables with many manifests
   → `rewrite_manifests`
2. **Stats missing:** Iceberg relies on column metrics in manifests;
   if written without metrics (`write.metadata.metrics`), the engine
   can't prune → rewrite with metrics enabled
3. **File sizes:** the migration preserved 10 MB files from the Hive
   layout; Hive's input format amortized differently → `rewrite_data_files`
4. **Engine integration:** older Trino/Spark versions have weaker
   Iceberg pushdown than Hive pushdown → upgrade; review the engine's
   Iceberg connector tuning docs for planning-time parallelism options

### Q8: "CDC pipeline: source adds a column mid-stream. Downstream Iceberg table, Spark structured streaming job. What breaks?"

**Answer:**
```
Avro source (registry) + Iceberg sink — the good path:
1. Registry adds field with default → BACKWARD compatible ✓
2. Spark schema evolves on read (reader schema from catalog)
3. Iceberg: ALTER TABLE ADD COLUMN → new field ID, metadata-only
4. Old files: new column reads as NULL (or default) ✓
5. New files: written with the new column ✓
   → Zero downtime. This is why people choose this stack.

JSON source (schema-on-read) — the fragile path:
1. New field appears in some records
2. Spark infers schema from sample → inconsistent types
   (first seen as long, later as double → cast failures)
3. Iceberg rejects commit on schema mismatch (if not auto-evolving)
4. Job fails → manual ALTER TABLE → restart
   → The failure mode is silent schema inference, not Iceberg.
```

### Q9: "REST catalog vs Hive Metastore vs AWS Glue for Iceberg — which catalog and why?"

| Catalog | Pros | Cons | Best for |
|---|---|---|---|
| **Hive Metastore** | Works everywhere, battle-tested | HMS scaling limits, single point, versioned API friction | Existing Hive estates |
| **AWS Glue** | Managed, IAM integration, no ops | AWS-only, throttling at high TPS, slow metadata at scale | AWS-centric shops |
| **REST catalog** | Decoupled, versioned API, multi-engine clean | You run the service (or use Tabular/Polaris) | Multi-engine, multi-cloud |
| **Nessie** | Git-like branching of tables (!) | Extra infra, niche | Experiment isolation, data-as-code |
| **JDBC catalog** | Simple, any RDBMS | Row-level locking limits concurrency | Small deployments |

**Interview answer:** "The catalog is just the CAS pointer store.
Glue for AWS-only, REST (Polaris/Tabular/Gravitino) for multi-engine
futures, HMS only if you're already there. The important interview
point: **catalog choice doesn't change the data layout — you can swap
catalogs without touching files.**"

---

## 10. Decision Trees

### 10.1 CoW vs MoR Selection

```mermaid
flowchart TD
    START["Write pattern?"]
    START -->|"Batch, daily/hourly<br/>read-heavy analytics"| COW["Copy-on-Write<br/>(default)"]
    START -->|"Streaming CDC<br/>upserts every minute"| MOR["Merge-on-Read<br/>+ scheduled compaction"]
    START -->|"Mixed: bulk loads +<br/>occasional corrections"| COW2["CoW for loads,<br/>accept MoR delete files<br/>for corrections, compact weekly"]

    MOR --> DT{"Delete type?"}
    DT -->|"Streaming, high throughput<br/>(knows key values, not positions)"| EQ["Equality deletes<br/>(fast write, slower read)"]
    DT -->|"Batch deletes<br/>(positions resolvable)"| POS["Position deletes<br/>(fast read)"]
```

### 10.2 Partition Transform Selection

```mermaid
flowchart TD
    START["What does 90% of WHERE<br/>clauses filter on?"]
    START -->|"event_time / created_at"| TIME{"Query range?"}
    START -->|"join keys<br/>(user_id, order_id)"| BUCKET["bucket(N, key)<br/>N = 16-128 typical"]
    START -->|"low-cardinality dims<br/>(country, status, type)"| ID["identity(col)<br/>only if < ~100 distinct values"]

    TIME -->|"hours"| H["hours(ts)"]
    TIME -->|"days (most common)"| D["days(ts)"]
    TIME -->|"months (archive)"| M["months(ts)"]

    BUCKET --> SIZE{"File size check"}
    SIZE -->|"< 128 MB/file<br/>post-partition"| FEWER["Reduce N —<br/>tiny files hurt more<br/>than hot buckets"]
```

---

## 11. Operational Maintenance Playbook

**Alex:** What production jobs should I run for Iceberg tables?

**Sam:** Think of maintenance as keeping metadata, files, and delete files healthy. Iceberg avoids Hive's listing problem, but it still needs periodic cleanup and compaction.

```mermaid
flowchart TD
    A["Streaming / batch writes"] --> B["Many small data files"]
    A --> C["Many delete files"]
    B --> D["rewrite_data_files<br/>bin-pack small files"]
    C --> D
    D --> E["Fewer larger Parquet files<br/>faster scans"]
    E --> F["expire_snapshots"]
    F --> G["remove_orphan_files"]
```

| Symptom | Likely Cause | Maintenance Action |
| :--- | :--- | :--- |
| Query planning is slow | Too many manifests / metadata files | `rewrite_manifests` |
| Scan reads many tiny files | Streaming or frequent small batches | `rewrite_data_files` |
| Reads slow after CDC deletes | MoR delete files accumulated | `rewrite_data_files` to apply deletes |
| Storage keeps growing | Old snapshots retained | `expire_snapshots` |
| Untracked files in table path | Failed jobs before commit | `remove_orphan_files` |

**Alex:** What is the one-liner staff answer?

**Sam:** Iceberg makes writes atomic through metadata commits, but production performance comes from maintenance: compact small files, rewrite manifests when planning slows, expire old snapshots based on retention policy, and remove orphan files after failed writes.

---

## 12. Quick Reference — Interview Edition

| Question | Short Answer |
|---|---|
| **Iceberg in one line?** | Table = canonical list of files in metadata, not a directory — ACID, time travel, evolution on object storage |
| **Metadata tree?** | Catalog → metadata.json → manifest list → manifest files → data files |
| **What's atomic in a commit?** | Catalog pointer CAS swap to new metadata.json. Files written first, pointer last |
| **Crashed writer?** | Orphan files (invisible, pointer never moved) — clean with `remove_orphan_files` |
| **Concurrent writers?** | Optimistic: CAS fails → refresh → rebase → retry. File-level conflict detection |
| **Hidden partitioning?** | Transform on existing column (days/hours/bucket); pruning automatic; no redundant `dt` column |
| **Partition evolution?** | ALTER TABLE spec change; zero rewrite; old/new specs coexist via spec ID in manifests |
| **identity() on user_id?** | Never — high cardinality → partition explosion. Use `bucket(N, col)` |
| **CoW vs MoR?** | CoW: rewrite files (slow write, fast read). MoR: delete files (fast write, merge at read) — compact regularly |
| **Position vs equality deletes?** | Position: (file, row) pairs — fast read. Equality: (col=val) — fast write, ideal for streaming CDC |
| **Time travel?** | `FOR SYSTEM_TIME AS OF '...'` or `VERSION AS OF <snapshot_id>` |
| **Snapshot explosion?** | Streaming commits every 30s = 40K snapshots/2wks → planning crawls. `expire_snapshots` + longer checkpoint interval |
| **Small files after streaming?** | `rewrite_data_files` (binpack to 256-512 MB) + `rewrite_manifests` — schedule both |
| **Schema rename safe?** | Yes — field IDs, not names/positions. Re-added same-name column = NEW field ID |
| **GDPR delete on MoR?** | DELETE is logical until compaction. Physical deletion needs rewrite + expire_snapshots + remove_orphan_files |
| **Iceberg vs Delta vs Hudi?** | Iceberg: engine neutrality + partition evolution. Delta: Databricks. Hudi: CDC upsert-heavy |
| **Catalog swap cost?** | Low — catalog only stores the pointer; metadata.json lives with the data files |
| **Hive migration?** | Shadow table + backfill + dual-write + validate + cutover (safe) or in-place `migrate` (fast, keeps old layout) |

---

## 13. Resources

- [Apache Iceberg Official Docs](https://iceberg.apache.org/docs/latest/)
- [Iceberg Table Spec (deep internals)](https://iceberg.apache.org/spec/)
- [Iceberg Hidden Partitioning](https://iceberg.apache.org/docs/latest/partitioning/)
- [Hello Interview – Iceberg Deep Dive](https://www.hellointerview.com/learn/system-design/deep-dives/apache-iceberg)
- [Tabular Blog (Iceberg creators)](https://tabular.io/blog/)
- [Apache Iceberg Architecture Deep Dive (BigData Boutique)](https://bigdataboutique.com/blog/apache-iceberg-architecture-deep-dive) — layer-by-layer walkthrough of catalog, metadata files, manifest lists, manifests, data files; concrete example of what happens on disk when you create and write to a table
- [Deep Dive into Apache Iceberg Architecture: The Three Layers That Power Your Lakehouse (Snowflake Builders Blog)](https://medium.com/snowflake/deep-dive-into-apache-iceberg-architecture-the-three-layers-that-power-your-lakehouse-83c03403e503) — dissects catalog, metadata, and data layers with practical query trace example showing how hierarchical pruning narrows search from catalog → Parquet files
- [2025 Comprehensive Guide to Apache Iceberg (Alex Merced)](https://blog.datalakehouse.help/posts/2025-01-2025-comprehensive-apache-iceberg-guide/) — definitive yearly guide covering architecture, ecosystem, migration patterns, comparison with Delta Lake/Hudi
