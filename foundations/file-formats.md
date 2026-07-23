# File Formats for Data Engineers — Interview Deep Dive

The format question comes in every DE interview at some angle: sizing,
compression, evolution, performance. This file covers the internals
**through the lens of real interview questions** with diagrams, worked
examples, and decision frameworks.

---

## 1. The Big Picture — When to Pick What

> [!NOTE]
> This is the most common opening question in DE interviews.

**Question:** *"Design a storage strategy for a new data platform. What format do you use for each zone?"*

```mermaid
flowchart LR
    A["Raw / Bronze<br/>(APIs, logs, CDC)"] --> B{"Format?"}
    B -->|Schema-on-read<br/>Flexible| C["JSON / Avro"]
    B -->|Strong schema<br/>Streaming| D["Avro + Schema Registry"]
    C --> E["Silver / Cleansed<br/>(ETL output)"]
    D --> E
    E --> F{"Format?"}
    F -->|Analytics| G["Parquet + Zstd"]
    F -->|Hive ACID| H["ORC + Zstd"]
    G --> I["Gold / Aggregated"]
    H --> I
    I --> J["Parquet (BI, ML)"]
```

**Answer structure:**
```
Bronze (raw):   JSON (schema-on-read, flexible) or Avro (if you have a registry)
Silver (clean): Parquet (column pruning, predicate pushdown, Snappy/Zstd)
Gold (agg):     Parquet (same — optimized for BI tools)
Kafka messages: Avro (schema evolution, compact binary)
```

---

## 2. Parquet — The Analytics Workhorse

### 2.1 Physical Layout (Draw This on the Whiteboard)

**Question:** *"Draw the internal structure of a Parquet file and explain how Spark uses it to skip data."*

```mermaid
flowchart TD
    subgraph "Parquet File"
        M1["Magic: PAR1"]
        RG1["Row Group 1 (128 MB)"]
        CC1["Column Chunk: customer_id"]
        CC2["Column Chunk: amount"]
        CC3["Column Chunk: order_date"]
        RG2["Row Group 2"]
        CC4["..."]
        FT["Footer"]
        S["Schema (Thrift)"]
        RM["Row Group 1 Metadata<br/>- num_rows: 1M<br/>- total_bytes: 128 MB"]
        CM["Column 'amount' Metadata<br/>- type: DOUBLE<br/>- encoding: DELTA_BINARY_PACKED<br/>- codec: ZSTD<br/>- statistics: min=5.0, max=999.0<br/>  null_count=0"]
        CI["Column Index (v2)<br/>Page 0: min=5.0, max=120.0<br/>Page 1: min=130.0, max=999.0"]
        FL4["Length: 4 bytes"]
        M2["Magic: PAR1"]
    end

    M1 --> RG1
    RG1 --> CC1
    RG1 --> CC2
    RG1 --> CC3
    CC2 --> CI
    RG1 --> RG2
    RG2 --> CC4
    RG2 --> FT
    FT --> S
    FT --> RM
    FT --> CM
    FT --> CI
    FT --> FL4
    FL4 --> M2
```

**Key insight for interviews:** The footer is read FIRST. It contains
statistics for every column in every row group. Spark decides which
row groups to read without touching any data.

### 2.2 Predicate Pushdown Walkthrough

**Question:** *"You have a 1 TB Parquet table with 50 columns. Your query is:*
```sql
SELECT SUM(amount) FROM orders WHERE status = 'DELIVERED' AND order_date = '2024-01-15'
```
*How does Spark decide what to read?"*

**Step-by-step:**

1. **Read footer** (cost: ~5 ms, < 1 MB) — contains statistics for all 50 columns
2. **Plan row group selection** — for each row group, check:
   - `status` column stats: does `min..max` include `'DELIVERED'`?
   - `order_date` stats: does `min..max` include `2024-01-15`?
3. **Read only matching row groups** — for those RGs, read only `amount` column

```mermaid
flowchart TD
    Q["Query: SUM(amount) WHERE status='DELIVERED' AND order_date='2024-01-15'"]
    RF["Read Footer"]
    Q --> RF
    RF --> RG1["RG 0<br/>status: PENDING..SHIPPED<br/>date: 2024-01-01..2024-01-10"]
    RF --> RG2["RG 1<br/>status: CANCELLED..REFUNDED<br/>date: 2024-01-05..2024-01-20"]
    RF --> RG3["RG 2<br/>status: DELIVERED..DELIVERED<br/>date: 2024-01-15..2024-01-15"]
    RF --> RG4["RG 3<br/>status: DELIVERED..SHIPPED<br/>date: 2024-01-14..2024-01-31"]

    RG1 --> SKIP1["SKIP<br/>No DELIVERED in range"]
    RG2 --> SKIP2["SKIP<br/>No DELIVERED in range"]
    RG3 --> READ["READ amount column"]
    RG4 --> READ2["READ amount column<br/>(page-level index skips more)"]

    SKIP1 -.-> NODATA["0 bytes read"]
    SKIP2 -.-> NODATA
    READ -.-> D1["+50 MB decompressed"]
    READ2 -.-> D2["Column Index:<br/>Page 0: date 2024-01-14..2024-01-20 → READ<br/>Page 1: date 2024-02-01..2024-02-15 → SKIP"]

    D1 --> RESULT["SUM(amount)"]
    D2 --> RESULT
```

**Interview answer:** "Out of 1 TB, Spark reads < 100 MB because:
1. Row group statistics skip 50% of groups
2. Column pruning reads only `amount` (2% of columns)
3. Page-level index skips non-matching pages within the group
Total reduction: ~10,000x fewer bytes touched"

### 2.3 Encoding Example — Dictionary

**Question:** *"A column 'status' has 3 distinct values across 10 million rows. How does Parquet store it efficiently?"*

**Worked example:**

```
Raw column (10M rows, 7 bytes avg string):
"SHIPPED", "SHIPPED", "DELIVERED", "PENDING", "SHIPPED", ...

Step 1 — Dictionary encoding builds a mapping:
  index 0 → "PENDING"
  index 1 → "SHIPPED"
  index 2 → "DELIVERED"

Step 2 — Data page stores indices via RLE:
  [1, 1, 2, 0, 1, 2, 2, 1, 0, ...]  ← 10M shorts (2 bytes each)

Step 3 — RLE compresses runs:
  5,1  → five rows of index 1
  4,2  → four rows of index 2
  ...

Storage comparison:
  Raw strings:      70 MB  (10M × 7 bytes)
  Dictionary + RLE:  2 MB  (10M × 2 bytes × 0.1 after RLE)
  After Zstd:       ~0.5 MB

Reduction: ~140x
```

### 2.4 Small File Problem

**Question:** *"My Spark job writing to S3 creates 10,000 tiny Parquet files (each 10 MB). Query performance is terrible. Why and how do I fix it?"*

```mermaid
flowchart LR
    subgraph "Bad: 10,000 files × 10 MB"
        A1["File 1<br/>Footer: 50 KB"]
        A2["File 2<br/>Footer: 50 KB"]
        A3["..."]
        A10000["File 10000<br/>Footer: 50 KB"]
    end

    subgraph "Good: 100 files × 1 GB"
        B1["File 1<br/>Footer: 50 KB<br/>Row groups: 8 × 128 MB"]
        B2["File 2<br/>Footer: 50 KB"]
        B100["File 100<br/>Footer: 50 KB"]
    end

    A1 -.-> COST1["Problem: 10,000 metadata operations<br/>S3 LIST = 500 ms each → 5000 seconds"]
    B1 -.-> COST2["100 metadata operations → 50 seconds"]
```

**Fix:**
```python
# Before writing: adjust output size
df.coalesce(100) \
  .write \
  .option("parquet.block.size", 256 * 1024 * 1024) \
  .parquet("s3://warehouse/orders/")
# Target: 256 MB - 1 GB per file
```

### 2.5 Schema Evolution Question

**Question:** *"You add a column `discount` to your Parquet schema. Old files don't have it. What happens when Spark reads them?"*

```sql
-- V1 schema: id INT, amount DOUBLE, status STRING
-- V2 schema: id INT, amount DOUBLE, status STRING, discount DOUBLE

SELECT id, discount FROM orders
```

**Answer:** Spark reads the schema from each Parquet file's footer.
Old files lack `discount` → Spark fills NULL for every row. No
rewrite needed. This works because:
- Parquet resolves columns by **name** (not position)
- Missing columns = NULL
- Type promotion works if compatible (INT → LONG, not reverse)

**Gotcha:** If the new column is marked NOT NULL in Spark, the query
fails. Always add nullable columns to existing tables.

---

## 3. Avro — The Streaming Standard

### 3.1 Why Avro for Kafka?

**Question:** *"You're designing a Kafka pipeline with 100+ event types. Why Avro over JSON?"*

```mermaid
sequenceDiagram
    participant P as Producer
    participant SR as Schema Registry
    participant K as Kafka
    participant C as Consumer

    P->>SR: Register schema (subject: order-value)
    SR-->>P: Schema ID = 42
    P->>K: Send [0x00][ID:42][binary Avro data]
    Note over P,K: Message size = 5 bytes overhead + data (no schema string)

    C->>K: Poll message
    C->>SR: Fetch schema by ID 42
    SR-->>C: Schema JSON
    Note over C: Reader schema resolves against writer schema
    C->>C: Deserialize
```

**Comparison (100-byte message, 10-field schema):**
```
JSON:   100 + 150 bytes overhead (key names) = 250 bytes
Avro:   100 + 5 bytes overhead = 105 bytes (no key names in data)
Ratio:  Avro is 2.4x smaller, plus Schema Registry gives evolution
```

### 3.2 Schema Resolution with Example

**Question:** *"Walk me through what happens when a consumer with a different schema reads an Avro message."*

**Writer produces with this schema:**
```json
{
  "type": "record", "name": "Order",
  "fields": [
    {"name": "id", "type": "int"},
    {"name": "amount", "type": "double"},
    {"name": "status", "type": "string"},
    {"name": "discount", "type": ["null", "double"], "default": null}
  ]
}
```

**Consumer reads with this schema:**
```json
{
  "type": "record", "name": "Order",
  "fields": [
    {"name": "id", "type": "long"},
    {"name": "status", "type": "string"},
    {"name": "region", "type": "string", "default": "UNKNOWN"}
  ]
}
```

```mermaid
flowchart TD
    M["Avro Message (Schema ID 42)"]
    R["Reader Schema"]
    W["Writer Schema (fetched by ID)"]

    M --> RES["Schema Resolution"]
    R --> RES
    W --> RES

    RES --> F1["id: int → long<br/>✓ Promotion allowed"]
    RES --> F2["amount: not in reader<br/>✓ Skipped (writer-only)"]
    RES --> F3["status: in both<br/>✓ Direct match"]
    RES --> F4["discount: not in reader<br/>✓ Skipped (writer-only)"]
    RES --> F5["region: in reader only<br/>✓ Use default: 'UNKNOWN'"]

    F1 --> OUT["Result: id=42 (as long),<br/>status='SHIPPED',<br/>region='UNKNOWN'"]
    F2 --> OUT
    F3 --> OUT
    F4 --> OUT
    F5 --> OUT
```

**Rules used:**
1. `id INT→LONG`: Widening promotion allowed
2. `amount` not in reader: Writer field is silently dropped
3. `discount` not in reader: Same — silent drop
4. `region` not in writer: Use `default: "UNKNOWN"` (required for safe evolution)

### 3.3 Binary Encoding Example

**Question:** *"How does Avro encode an int value of 42 vs -1 vs 1,000,000?"*

Avro uses **zig-zag variable-length integer encoding**:

```
Encoding formula: (n << 1) ^ (n >> 63)   for signed 64-bit

Value   Zig-Zag     Bytes (binary)
 42     (84)  →     0x54                                    → 1 byte
 -1     (1)   →     0x01                                    → 1 byte
 1000   (2000) →    0x90 0x0F                               → 2 bytes
1000000 (2000000) → 0x80 0x84 0x7A                          → 3 bytes
```

Each byte uses 7 bits for data + 1 continuation bit (MSB).
Small integers (most DE values) fit in 1–2 bytes instead of 4–8.

---

## 4. ORC — When It Matters

**Question:** *"When would you pick ORC over Parquet?"*

```mermaid
flowchart TD
    Q["OLAP format?"]
    Q -->|"Engine = Hive/Tez"| H["Hive ACID needed?"]
    Q -->|"Engine = Spark/Trino"| P["Parquet"]

    H -->|"Yes"| O["ORC<br/>Native ACID via delta files<br/>INSERT/UPDATE/DELETE"]
    H -->|"No"| O2["ORC or Parquet<br/>(bloom filters favor ORC)"]

    O --> D["Delta files track row-level changes<br/>Compaction merges base + deltas"]
```

**ORC's unique feature — built-in bloom filters:**
```ini
-- Hive config for ORC bloom filters
SET orc.bloom.filter.columns=order_id,customer_id;
SET orc.bloom.filter.fpp=0.05;
```
Bloom filters definitively answer "this stripe definitely doesn't
contain this ID" — useful for point lookups on high-cardinality keys.

**Tradeoff:** ORC is ~15% faster for Hive scans (thanks to stripe-level
indexes), but Parquet has universal engine support.

---

## 5. Compression Decision Scenarios

**Question:** *"Your data lake costs $10,000/month in S3. You want to reduce storage cost without hurting query performance. What do you do?"*

```mermaid
flowchart LR
    subgraph "Before: Snappy"
        S["100 TB → 35 TB<br/>Snappy ratio: 2.9x"]
    end
    subgraph "After: Zstd level 3"
        Z["100 TB → 21 TB<br/>Zstd ratio: 4.8x<br/>Read speed: -20%"]
    end
    S -->|"Switch codec"| Z
    Z -->|"Saving: 14 TB × $23/TB/mo<br/>= $322/mo"| MONEY["-$3,864/yr"]
```

**Scenarios from real interviews:**
```
Q: "ETL intermediate data that gets deleted after 24 hours?"
A: LZ4 — write speed matters, not size

Q: "BI dashboard base table, queried every 30 seconds?"
A: Zstd level 3 — best read speed/size tradeoff

Q: "Cold data accessed once per year for audit?"
A: Gzip or Zstd level 9 — size dominates, read speed irrelevant

Q: "Kafka topic retention = 7 days, 500 MB/s throughput?"
A: Snappy — producer CPU is the bottleneck
```

---

## 6. Decision Trees — Whiteboard for Interview

### 6.1 Format Selection Flow

```mermaid
flowchart TD
    START["Primary access pattern?"]

    START -->|"Streaming / Kafka / writes"| STREAM["Avro"]
    START -->|"Analytics / BI / reads"| ANALYTICS{"Query engine?"}
    START -->|"ML / GPU / feature store"| ML["Parquet"]

    ANALYTICS -->|"Spark, Presto,<br/>Trino, DuckDB"| PARQUET["Parquet + Zstd"]
    ANALYTICS -->|"Hive with ACID"| ORC["ORC + Zstd"]
    ANALYTICS -->|"Ad-hoc / exploration"| ANY["Parquet or JSON"]
```

### 6.2 Compression Selection Flow

```mermaid
flowchart TD
    Q["Compression priority?"]
    Q -->|"Write speed"| LZ4["LZ4"]
    Q -->|"Read speed"| Z3["Zstd level 3"]
    Q -->|"Storage cost"| GZIP["Gzip or Zstd level 9"]
    Q -->|"Balanced"| SNAPPY["Snappy"]

    LZ4 -->|"Spark shuffle,<br/>transient data"| LZ4U
    Z3 -->|"Analytics tables,<br/>BI dashboards"| Z3U
    GZIP -->|"Cold storage,<br/>archival"| GZIPU
    SNAPPY -->|"Default if unsure,<br/>Kafka producers"| SNAPPYU
```

---

## 7. Real Interview Questions (from FAANG + GCC)

### Q1: "Your Spark job reads 1000 small Parquet files on S3. It's slow. Diagnose and fix."

**Diagnosis:**
- S3 LIST for 1000 files = ~0.5s each → 500s metadata overhead
- Each file has its own footer → Spark reads 1000 footers instead of 10
- No row group pruning benefit (1 row group per file)

```mermaid
flowchart LR
    IN["10 GB data<br/>1000 files × 10 MB"] --> READ["Spark reads 1000 footers<br/>(500 ms each)"]
    READ --> TASK["1000 tasks created<br/>Task scheduling overhead"]
    TASK --> SLOW["Total: ~15 minutes"]
    SLOW --> FIX

    subgraph FIX["Fix: Consolidate"]
        C["df.coalesce(10)<br/>.write<br/>.option('parquet.block.size', '256MB')"]
    end
    FIX --> OUT["10 files × 1 GB<br/>with 8 row groups each<br/>Total: ~2 minutes"]
```

**Expected answer:**
1. Root cause: **small file problem** — too many metadata operations
2. Fix: Coalesce/repartition before write, target 256 MB–1 GB per file
3. Bonus: Enable AQE which auto-coalesces shuffle partitions

### Q2: "Explain how Parquet's column pruning and predicate pushdown differ."

| Mechanism | What It Skips | How | Granularity |
|---|---|---|---|
| **Column pruning** | Entire columns | Spark reads only column chunks for selected columns | File-level |
| **Predicate pushdown** | Row groups (and pages) | Footer statistics + column index to skip non-matching data | Row group / page |

**Example:** `SELECT amount FROM orders WHERE status = 'DELIVERED'`
- Column pruning: Reads only `amount` and `status` column chunks (not all 50 columns)
- Predicate pushdown: For each row group, checks `status.min..max`. If no `DELIVERED`, skip entire row group (30–100 MB saved per skip)

### Q3: "A column has 5 million unique UUIDs. Dictionary encoding is hurting performance. Why?"

```mermaid
flowchart LR
    SUB1["Dictionary page<br/>5M UUIDs × 36 chars<br/>= 180 MB"]
    SUB2["Data page<br/>5M indices × 4 bytes<br/>= 20 MB"]
    SUB3["Dictionary lookups<br/>during decompression<br/>= extra CPU"]
    TOTAL["Total: 200 MB<br/>CPU: encoding + decoding"]

    SUB1 --> TOTAL
    SUB2 --> TOTAL
    SUB3 --> TOTAL

    WITHOUT["Without dictionary<br/>5M UUIDs × 36 bytes<br/>= 180 MB (PLAIN)"]
    TOTAL --> COMPARE["Dictionary made it WORSE<br/>200 MB vs 180 MB<br/>+ CPU overhead"]

    COMPARE --> FIX["Fix:<br/>spark.conf.set('spark.sql.parquet.dictionaryFilter', true)<br/>- or write with parquet.dictionary.page.size per-column"]
```

**Answer:** Dictionary encoding stores every distinct value once + index per row. For high-cardinality columns (UUIDs, hashes, timestamps), the dictionary page is nearly as large as the data, and both encode and decode add CPU. **Dictionary helps low-cardinality columns only.** Disable it per-column for UUIDs.

### Q4: "A Hive table uses ORC. You need to update 0.1% of rows daily. Write strategy?"

**Answer:** ORC supports ACID via delta files:

```mermaid
flowchart LR
    subgraph "Initial State"
        B["Base file (ORC)<br/>100M rows, 5 GB"]
    end
    subgraph "Day 1 Update"
        D1["Delta file 1<br/>100K INSERTs<br/>50K DELETEs"]
    end
    subgraph "Day 2 Update"
        D2["Delta file 2<br/>200K INSERTs"]
    end
    subgraph "After Compaction"
        NB["New Base file<br/>100.25M rows, 5.1 GB"]
    end

    B --> D1
    D1 --> D2
    D2 --> NB
```

**Tradeoff:** Reads must merge base + all delta files (slower).
Compaction (bin-pack or sort) merges them periodically.
Use `hive.compactor.worker.threads` to schedule compaction.

### Q5: "Design a file format strategy for a new data lake. Consider cost, performance, query patterns."

| Zone | Format | Partitioning | Compression | Reasoning |
|---|---|---|---|---|
| **Bronze (raw)** | Avro (if registry) or JSON | Date/hour | Snappy | Schema flexibility, fast writes |
| **Silver (cleaned)** | Parquet | `year/month/day` | Zstd level 3 | Column pruning, predicate pushdown |
| **Gold (aggregated)** | Parquet | `year/month` | Zstd level 3 | BI tool compatibility, fast scans |
| **Kafka topics** | Avro | N/A | Snappy | Schema Registry, small payloads |
| **ML features** | Parquet | `dataset_name/version` | Zstd level 1 | GPU reads via RAPIDS |
| **Archive (< 1 query/yr)** | Gzip'd JSON | Single prefix | Gzip | Minimal cost, schema unknown |

### Q6: "Your 2-hour Spark ETL processes 50 columns but downstream only needs 5. How do you optimize?"

**The 2-minute fix:**
```python
# Before: reads all 50 columns through entire pipeline
df = spark.read.parquet("s3://bronze/orders/")
df.createOrReplaceTempView("orders")
result = spark.sql("""
    SELECT id, customer_id, amount, status, order_date
    FROM orders
    WHERE status = 'ACTIVE'
""")

# After: project early
df = spark.read.parquet("s3://bronze/orders/") \
    .select("id", "customer_id", "amount", "status", "order_date") \
    .filter(col("status") == "ACTIVE")
```

**Why it works:** Parquet reads only the 5 selected column chunks
from disk. Filter pushes to row group statistics. Before: 50 column
chunks decompressed. After: 5 chunks. **~90% less I/O.**

### Q7: "What happens to compression ratio if I sort data before writing Parquet?"

**Answer:** Sorting improves compression significantly for columns
with low cardinality or natural ordering:

```
Unsorted:  "SHIPPED", "DELIVERED", "PENDING", "SHIPPED", "CANCELLED"
            → dictionary has 4 entries, RLE gets no long runs
Sorted:    "CANCELLED", "CANCELLED", ..., "DELIVERED", ..., "PENDING", ..., "SHIPPED"
            → still 4 dictionary entries, but RLE produces
              long runs → 200,1 (200 of same index = 4 bytes vs 200 entries × 2 bytes each)
```

**Measured effect:** Sorting by `order_date` before writing Parquet
can improve overall compression by 20–40% because adjacent rows have
similar values, making RLE + delta encoding more effective.

> [!TIP]
> Production pattern: sort by high-cardinality date column + one
> low-cardinality filter column (e.g., `ORDER BY order_date, status`).
> Improves both compression and predicate pushdown effectiveness.

---

## 8. Quick Reference — Interview Edition

| Question | Short Answer |
|---|---|
| **Format for analytics?** | Parquet — column pruning, predicate pushdown, universal support |
| **Format for Kafka?** | Avro + Schema Registry — binary size, schema evolution, compatibility enforcement |
| **Compression for Parquet?** | Zstd level 3 (best ratio/speed); Snappy (safe default); LZ4 (transient) |
| **How does Spark skip data?** | Footer stats → row group pruning → column index → page-level skipping |
| **Why is Avro smaller than JSON?** | No key names in payload, binary encoding (variable-length ints, zig-zag) |
| **Small file problem?** | Too many metadata ops → coalesce before write → target 256 MB–1 GB per file |
| **Schema evolution in Parquet?** | Add = NULL for old, drop = reader ignores, rename = alias metadata |
| **Schema evolution in Avro?** | Reader/writer resolution by name, defaults, promotion rules |
| **ORC vs Parquet?** | Parquet unless Hive ACID or bloom filters are required |
| **Dictionary encoding wins?** | Low cardinality (status, category, boolean); loses on UUIDs/hashes |
| **Sort before write?** | 20–40% better compression, better stats pruning, more CPU on write |
| **First thing to check for slow Parquet reads?** | File size distribution, number of row groups, column projection |
