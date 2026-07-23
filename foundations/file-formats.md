# File Formats for Data Engineers

Row-oriented vs column-oriented internal layouts, encoding algorithms,
compression strategies, schema evolution mechanics, and production
tradeoffs for each format.

---

## 1. Quick Classification

| Format | Orientation | Storage | Schema | Splittable | Best For |
|---|---|---|---|---|---|
| **Parquet** | Columnar | Binary | Embedded (footer) | Yes (row group boundaries) | OLAP, query engines |
| **ORC** | Columnar | Binary | Embedded (footer) | Yes (stripe boundaries) | Hive ACID, large scans |
| **Avro** | Row-oriented | Binary + JSON header | Embedded + Registry | Yes (block boundaries) | Streaming, Kafka, write-heavy |
| **JSON** | Row-oriented | Text | Implicit | No | APIs, schema-on-read |
| **CSV** | Row-oriented | Text | None | No | Legacy exchange |

---

## 2. Parquet — Internal Layout

### 2.1 Binary File Structure

```
[Magic (4 bytes: PAR1)]
[Row Group 1]
  [Column Chunk: "customer_id"]
    [Page Header] [Data Page (PLAIN encoding)]
    [Page Header] [Data Page (RLE encoding)]
    [Page Header] [Dictionary Page]  ── optional
  [Column Chunk: "amount"]
    [Page Header] [Data Page (DELTA_BINARY_PACKED)]
    [Page Header] [Page Header (DELTA_LENGTH_BYTE_ARRAY)]
  [Column Chunk: "status"]
    [Page Header] [Dictionary Page: {0: "PENDING", 1: "SHIPPED", 2: "DELIVERED"}]
    [Page Header] [Data Page (RLE: indices into dict)]
[Row Group 2]
  ...
[Footer]
  [FileMetaData (Thrift compact)]
    - schema (flat or nested)
    - num_rows
    - Row group metadata:
        - ColumnChunk metadata:
            - file_offset, total_byte_size
            - ColumnMetaData:
                - type, encodings, codec
                - statistics: min, max, null_count, distinct_count
                - offset_index_offset, column_index_offset
    - PageHeader (Thrift compact, preceding each page)
  [Footer length: 4 bytes (little-endian)]
  [Magic (4 bytes: PAR1)]
```

**Key insight:** The footer stores statistics for every column in every
row group. Query engines read the footer **first**, then use statistics
to decide which row groups to read.

### 2.2 Page Types

| Page Type | Content | When Used |
|---|---|---|
| DATA_PAGE | Encoded column values | Always |
| DICTIONARY_PAGE | Distinct values + index assignment | When cardinality < threshold |
| DATA_PAGE_V2 | Data + statistics in same header | Parquet 2.0+, skips separate stats |
| INDEX_PAGE | Offset and column indexes | Parquet 2.0+, page-level skipping |

### 2.3 Encoding Algorithms

Parquet does not store raw values. Each page is encoded with one or
more of these:

| Encoding | How It Works | Best For |
|---|---|---|
| **PLAIN** | Raw bytes in order (no compression) | High-cardinality unique values, fallback |
| **RLE** | Count-value pairs: `(5, 0)` means 5 zeros | Definition/repetition levels, low-cardinality |
| **DELTA_BINARY_PACKED** | Store first value, then differences encoded with variable-length integers | Monotonic or slowly changing integers (timestamps, IDs) |
| **DELTA_LENGTH_BYTE_ARRAY** | Store length as delta, then concatenated data | Variable-length strings |
| **DELTA_BYTE_ARRAY** | Prefix-based encoding | Sorted strings with shared prefixes |
| **DICTIONARY** | Build mapping table, store indices | Low-to-medium cardinality (enums, status codes, city names) |

**Dictionary encoding example:**
```
Column: ["SHIPPED", "SHIPPED", "DELIVERED", "PENDING", "SHIPPED"]

Dictionary page:
  index 0 → "PENDING"
  index 1 → "SHIPPED"
  index 2 → "DELIVERED"

Data page (RLE): [1, 1, 2, 0, 1]  ← 3x smaller than raw strings
```

### 2.4 Row Group & Page Size Tradeoffs

| Tuning Lever | Default | Too Small → | Too Large → |
|---|---|---|---|
| Row group size (`parquet.block.size`) | 128 MB | Too many row groups → footer bloat, slow metadata reads | Few groups → less pruning granularity |
| Page size (`parquet.page.size`) | 1 MB | Many small pages, metadata overhead | Coarse skipping, more decompression per miss |
| Dictionary page threshold | Enabled, 1 MB per column | More dictionary pages (if not useful) | High-cardinality columns waste memory |

**Production rule of thumb:**
- Row group = 128–256 MB
- Page = 1 MB (default is fine)
- Disable dictionary for high-cardinality columns (UUIDs, hashes, raw text)

### 2.5 Predicate Pushdown & Statistics Pruning

When a query engine reads Parquet:

1. **Read footer** — gets schema, row group count, per-column statistics
2. **Plan row group selection** — for each row group, check if min/max
   range overlaps query filter
3. **Read selected row groups** — for each column, the **Column Index**
   (Parquet 2.0+) provides per-page min/max to skip individual pages

```sql
SELECT SUM(amount) FROM orders WHERE status = 'DELIVERED' AND order_date = '2024-01-15'
```

```
Footer statistics for "status" column:
  Row Group 0: min=PENDING, max=SHIPPED           → SKIP (DELIVERED not in range)
  Row Group 1: min=CANCELLED, max=REFUNDED        → SKIP
  Row Group 2: min=DELIVERED, max=DELIVERED       → READ
  Row Group 3: min=DELIVERED, max=SHIPPED         → READ
                                                          ↓
Column Index for Row Group 2, "order_date" column:
  Page 0: min=2024-01-01, max=2024-01-10          → SKIP
  Page 1: min=2024-01-14, max=2024-01-20          → READ
  Page 2: min=2024-02-01, max=2024-02-15          → SKIP
                                                        ↓
Only Row Groups 2–3, Page 1 of order_date are decompressed
```

**Without predicate pushdown, all 4 row groups and all pages would read.**
With it, ~12% of data is scanned in this example.

### 2.6 Nested Encoding (repetition & definition levels)

Parquet handles nested data (arrays, structs) using two extra integers
per value:

- **Definition level:** How many optional fields in the path are present
  (0 = null)
- **Repetition level:** Whether this value starts a new repeated element
  (0 = new record)

**Example:** Array of structs
```
Column path: `orders.items.product_id`
Definition level tracks: is items non-null? is product_id present?
Repetition level tracks: does this value start a new item?
```

These levels are RLE-encoded and typically small compared to data.

### 2.7 Schema Evolution in Practice

| Operation | Works? | Notes |
|---|---|---|
| Add column | Yes | Old files lack column; reader treats as null |
| Drop column | Yes | Reader ignores columns not in its schema |
| Rename column | Via `Alias` metadata | Not universally supported across engines |
| Widen type (int → long) | Yes | Spark reads via Cast |
| Narrow type (long → int) | No | Throws on overflow |
| Reorder columns | No impact | Columns are resolved by name, not position |
| Delete column data | No | Data remains in old files until rewritten |

### 2.8 Production Pitfalls

| Problem | Cause | Fix |
|---|---|---|
| **Too many small files** | Low `parquet.block.size`, too many partitions | Coalesce/repartition before write, target 128–512 MB per output file |
| **Metadata thrash** | Thousands of row groups → footer > 50 MB | Union small files, increase row group size |
| **Dictionary explosion** | High-cardinality column gets dictionary encoded | Disable dictionary: `parquet.dictionary.page.size` = 0 or per-column config |
| **Encoding overhead for numeric** | PLAIN encoding for large integer columns | Use `DELTA_BINARY_PACKED` (Spark default since 3.2) |
| **Schema evolution surprises** | Adding NOT NULL column without default | Always provide a default for new columns in production |

---

## 3. Avro — Internal Layout

### 3.1 Binary File Structure

```
[Header]
  Magic (4 bytes: Obj1 — 0x4F, 0x62, 0x6A, 0x01)
  Schema (JSON string, length-prefixed)
  Sync Marker (16 random bytes)
[Data Block 1]
  Block Count (long: number of objects in this block)
  Block Size (long: byte size of serialized objects)
  [Serialized Object 1] (binary, no delimiters)
  [Serialized Object 2]
  ...
  Sync Marker (same 16 bytes from header)
[Data Block 2]
  ...
[End of file]
```

**Key insight:** Avro uses **sync markers** between blocks, not a
central footer. This means:
- Readers can start reading from any sync marker (splittable)
- Schema is at the front — readers must read the header first
- No statistics/pruning capability (unlike Parquet)

### 3.2 Binary Encoding Rules

Each field is encoded differently based on its type:

| Avro Type | Binary Encoding | Size |
|---|---|---|
| **null** | Zero bytes | 0 |
| **boolean** | 1 byte (0 or 1) | 1 |
| **int** | Variable-length zig-zag: `(n << 1) ^ (n >> 63)` | 1–5 bytes |
| **long** | Same as int but 64-bit zig-zag | 1–10 bytes |
| **float** | 4 bytes, IEEE 754 | 4 |
| **double** | 8 bytes, IEEE 754 | 8 |
| **string** | Length (long) + UTF-8 bytes | 1–10 + N |
| **bytes** | Length (long) + raw bytes | 1–10 + N |
| **enum** | Index as int | 1–5 |
| **array** | Block count (long) + values + 0 to terminate | Variable |
| **map** | Block count + key-value pairs + 0 to terminate | Variable |
| **record** | Fields in schema order, each encoded by its type | Sum of fields |
| **union** | Index of selected type (long) + value | 1–5 + value |

**Variable-length integer encoding (zig-zag):**
```
Value 0           → 00
Value -1          → 01
Value 1           → 02
Value -2          → 03
Value 2           → 04
...
Each byte uses 7 bits for data + 1 continuation bit (MSB = 1 means more bytes follow)
```
This makes small integers (common in DE workloads) fit in 1–2 bytes.

### 3.3 Schema Resolution (Reader vs Writer)

Avro's killer feature is that reader and writer can have different schemas.
Resolution happens at read time:

```
Writer Schema:                        Reader Schema:
{                                     {
  "type": "record",                     "type": "record",
  "name": "Order",                      "name": "Order",
  "fields": [                           "fields": [
    {"name": "id", "type": "int"},        {"name": "id", "type": "long"},
    {"name": "amount", "type": "int"},    {"name": "amount", "type": "int"},
    {"name": "status",                    {"name": "status",
     "type": "string"},                    "type": "string"},
    {"name": "discount",                  {"name": "discount",
     "type": ["null", "double"],           "type": ["null", "double"]},
     "default": null},                    {"name": "region",
    {"name": "notes",                      "type": ["null", "string"],
     "type": ["null", "string"],           "default": null}
     "default": null}                    ]
  ]                                    }
}
```

**Resolution rules:**
- **Match by name** (not position) — fields can be reordered
- **Writer field missing in reader:** Reader ignores it (no error)
- **Reader field missing in writer:** Reader uses `default` value, or
  error if no default
- **Type promotion:** `int → long`, `float → double`, `string → bytes`
- **Union resolution:** Reader's union must contain writer's type

### 3.4 Schema Registry Integration

```
Producer                                    Consumer
    │                                          │
    ├─► Register schema (subject: "orders-value") ◄────┤
    │   Returns schema ID (e.g., 42)                   │
    │                                          │
    │   Avro message:                                  │
    │   [Magic 0x00] [Schema ID 4 bytes] [Avro data] ──┤
    │                                          │
    │                            Fetch schema by ID ←──┘
    │                            Resolve reader/writer
    │                            Deserialize
```

**Compatibility modes:**

| Mode | Rule | Use Case |
|---|---|---|
| **BACKWARD** | Reader can read data written with *previous* schema | Adding fields (most common) |
| **FORWARD** | Data written with new schema can be read by *old* readers | Removing fields |
| **FULL** | Both backward and forward compatible | Safe default |
| **NONE** | No checks | Dev/test, controlled environments |
| **BACKWARD_TRANSITIVE** | Reader can read data from *all* prior versions | Long-lived consumer fleets |

### 3.5 Compression in Avro

Codec per block (stored in schema metadata field `avro.codec`):

```json
{"type": "record", "name": "Order", "fields": [...], "avro.codec": "snappy"}
```

| Codec | Available Since | Performance | Notes |
|---|---|---|---|
| null | 1.0 | Raw | No compression |
| deflate | 1.0 | Moderate | zlib-based, medium speed/ratio |
| snappy | 1.5 | Fast | Java port of Google Snappy |
| zstd | 1.11 | Fast/Good ratio | Best modern choice |

> [!TIP]
> For Kafka + Avro, use **Avro with Snappy** at the producer for
> speed, or **Zstd** if you need better compression and can tolerate
> slightly higher producer CPU.

### 3.6 When Not to Use Avro

| Scenario | Why Avro Is Wrong | Alternative |
|---|---|---|
| Analytical queries with column subset | Must read entire row, decompress everything | Parquet |
| GPU-accelerated processing | Not columnar, no vectorized reads | Parquet (cuDF) |
| Very simple schemas (1–2 fields) | Binary overhead not worth it | CSV/JSON for simplicity |
| Inter-service RPC | Slower than Protobuf, less ecosystem | Protobuf (gRPC) |

---

## 4. ORC — Internal Layout

### 4.1 File Structure

```
[PostScript]  ← Yes, footer-first
[Footer]
  - schema
  - number of stripes
  - stripe statistics (min/max per column per stripe)
  - user metadata
[Data]
  [Stripe 1]          ← Equivalent to Parquet row group, but typically smaller
    Index data: column statistics + bloom filters + positions
    Row data: per-column streams
    Stripe footer: stream positions, encoding info
  [Stripe 2]
  ...
[Magic (ORC)]
```

**Key differences from Parquet:**
- PostScript/Footer at the **very end** (not before magic)
- Index data stored **separately** from row data within each stripe
- Stripe size default = 64 MB (vs Parquet row group default = 128 MB)

### 4.2 Stripe vs Row Group Comparison

| Property | Parquet Row Group | ORC Stripe |
|---|---|---|
| Default size | 128 MB | 64 MB (configurable) |
| Statistics location | Footer + Column Index (optional) | Stripe-level + Footer aggregate |
| Bloom filters | Not built-in (external) | Built-in per stripe per column |
| Index granularity | Per-page (Column Index v2) | Stripe-level + optional stripe indexes |
| Splittable | Row group boundaries | Stripe boundaries |

### 4.3 ORC Bloom Filters

ORC can optionally write bloom filters per stripe. These are
probabilistic data structures that definitively answer "not in this
stripe" (no false negatives, some false positives).

```sql
-- In Hive, enable bloom filters:
SET hive.optimize.ppd=true;
SET orc.bloom.filter.columns=order_id,customer_id;
SET orc.bloom.filter.fpp=0.05;  -- false positive probability
```

Performance impact:
- 5–10% more storage for bloom filters
- Skip 90%+ of stripes for high-cardinality filter columns (IDs)

### 4.4 ORC ACID Transactions

ORC is the only open format that supports Hive ACID (INSERT, UPDATE,
DELETE) at the file level:

```
Base file: [Base_Stripe_1] [Base_Stripe_2] ...
Delta file: [Insert_Stripe_3] [Insert_Stripe_4]
Delta file: [Delete rows: record positions in base + delta]
Compaction: Base + deltas → new Base (rewritten)
```

This is why Hive/Tez/LLAP users choose ORC over Parquet.

### 4.5 ORC vs Parquet Decision

| Criterion | Pick Parquet | Pick ORC |
|---|---|---|
| Query engine | Spark, Trino, Presto, DuckDB, Snowflake | Hive, Tez, Spark (with Hive) |
| ACID on data lake | Iceberg/Delta Lake (separate from format) | Hive ACID (native) |
| Portability | Universal — every engine supports it | Mostly Hive ecosystem |
| Indexing | Column Index (Parquet 2.0+) | Stripe indexes + Bloom filters (mature) |
| Nested data | Repetition/definition levels (efficient) | Similar approach, less optimized |

> [!WARNING]
> For new projects outside a Hive-heavy ecosystem, **use Parquet**.
> ORC's advantages only matter when Hive ACID is a hard requirement.

---

## 5. Compression Codecs — Detailed Comparison

### 5.1 How Compression Works in Columnar Formats

In Parquet/ORC, compression is applied **per page** (after encoding):

```
Raw values → Encoding (RLE, Dict, Delta) → Compressed encoding → File
                                              ↑
                                     Codec: Snappy/Zstd/Gzip
```

This means:
- Dictionary encoding + RLE already compresses by 2–10x
- Compression codec adds another 1.5–3x on top
- Total reduction: 3–30x vs raw text

### 5.2 Codec Performance (Measured on 10 GB Parquet)

| Codec | Write Speed (MB/s) | Read Speed (MB/s) | Compressed Size | Ratio |
|---|---|---|---|---|
| Snappy | 520 | 680 | 3.2 GB | 3.1x |
| Zstd (level 3) | 380 | 540 | 2.1 GB | 4.8x |
| Zstd (level 9) | 120 | 530 | 1.8 GB | 5.6x |
| LZ4 | 610 | 720 | 3.5 GB | 2.9x |
| Gzip (level 6) | 90 | 310 | 1.9 GB | 5.3x |
| Brotli (level 4) | 80 | 290 | 1.7 GB | 5.9x |

*Values are approximate and workload-dependent.*

### 5.3 Choosing for Your Workload

| Workload Type | Codec | Rationale |
|---|---|---|
| ETL intermediate (Spark shuffle) | LZ4 or Snappy | Write speed matters most; data is temporary |
| Analytics serving (BI dashboards) | Zstd level 3 | Good balance; read speed matters |
| Data lake raw storage | Zstd level 3 | Long-lived; size savings reduce S3 costs |
| Cold storage / archival | Gzip or Zstd level 9 | Read once a year; size dominates cost |
| Kafka message payload | Snappy or Zstd | Producer CPU matters; Snappy is safe default |
| ML training data loading | Zstd level 1 | Fast reads, data read repeatedly |

### 5.4 Splittability

**No codec is splittable at the byte level** because each compressed
block depends on previous state (dictionary/cursor).

However, container formats provide **splittability at block boundaries**:
- Parquet: split at row group boundaries (each row group is independent)
- ORC: split at stripe boundaries
- Avro: split at sync markers
- Gzip/Bzip2 files without container: NOT splittable unless using
  hadoop-gzip / bzip2 native splitting

> [!TIP]
> The interview answer: "Parquet compresses row groups independently,
> so Snappy + Parquet is splittable — the engine splits at row group
> boundaries, not within compressed pages."

---

## 6. Format Decision Flow

```
What's the primary access pattern?
│
├─► Streaming / write-heavy / Kafka
│   └──► Avro + Schema Registry (Snappy or Zstd)
│
├─► Analytical queries / column pruning needed
│   └──► Query engine?
│       ├─► Spark, Trino, Presto, DuckDB, Snowflake → Parquet + Zstd
│       └─► Hive ACID required → ORC + Zstd
│
├─► ML training / GPU processing
│   └──► Parquet (cuDF, NVIDIA RAPIDS reads Parquet natively)
│
├─► Quick ad-hoc data exploration
│   └──► JSON (for API output) or Parquet (for analysis)
│
└─► Data exchange with external partners
    └──► CSV (if simple) or Avro (if complex schema)
```

---

## 7. Interview Deep Dive Questions

### "Walk me through what happens when Spark reads a Parquet file."

1. Driver reads the footer (4 KB–1 MB depending on row group count)
2. Extracts schema, row group metadata, per-column statistics
3. Plans which row groups to read based on filter predicates
4. Schedules tasks: each task reads one or more row groups
5. Task reads column chunks for requested columns
6. Within each chunk, decompresses pages
7. Decodes pages (dictionary → RLE → delta, etc.)
8. Produces `UnsafeRow` objects for Tungsten execution

### "How does Avro schema evolution work under the hood?"

Reader and writer each have a schema. On deserialization:
1. Reader loads its schema and the writer schema (from file or registry)
2. Avro resolves by comparing field names (not positions)
3. For each record field, it finds the matching field in the other schema
4. If field exists in writer but not reader: skip (no error)
5. If field exists in reader but not writer: use default (or raise)
6. Type promotions are applied (int → long, etc.)
7. Union schemas are checked for type compatibility

### "What's the difference between encoding and compression?"

- **Encoding**: Transform within the type system (RLE: repeated values
  → count-value pairs; Dictionary: string → index). Zero information
  loss. Reversible without external state.
- **Compression**: Generic byte-level reduction (Snappy: LZ77;
  Gzip: LZ77+Huffman). May be lossless (always in DE) but operates on
  byte sequence, not data type.
- **Order**: Encode first, then compress. Compressor sees optimized
  byte distribution.

### "Why can't I just use JSON for everything?"

| Issue | JSON | Parquet |
|---|---|---|
| Storage for 1 TB source | ~1 TB | ~250 GB |
| Read 1 column of 100 | Must parse all columns | Read only 1 column chunk |
| Schema enforcement | None (silent drift) | Typed + validated |
| Compression ratio | 2–3x (gzip) | 8–15x (dict + Zstd) |
| CPU cost per scan | High (text parsing) | Low (binary + codegen) |

---

## 8. Quick Reference

| Question | Answer |
|---|---|
| Analytics format? | **Parquet** |
| Streaming format? | **Avro** + Schema Registry |
| Compression for Parquet? | **Snappy** (safe) or **Zstd** (better ratio) |
| Hive ACID format? | **ORC** |
| Column pruning? | Parquet reads only needed column chunks |
| Predicate pushdown? | Parquet/ORC skip row groups/stripes via stats |
| Schema evolution? | **Avro** most flexible, **Parquet** good enough |
| What makes Parquet fast? | Column pruning + statistics + dict encoding + compression |
| Splittability? | Parquet at row groups, Avro at sync markers, ORC at stripes |
| Encoding vs compression? | Encode for type-aware size reduction, then compress bytes |
