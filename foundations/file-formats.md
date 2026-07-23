# File Formats for Data Engineers

Row-oriented vs column-oriented, compression, schema evolution, and
when to pick each format.

---

## 1. Classification

| Format | Orientation | Type | Human Readable | Schema Evolution | Best For |
|---|---|---|---|---|---|
| **Parquet** | Columnar | Binary | No | Yes (add/drop columns) | Analytics, OLAP, query engines |
| **ORC** | Columnar | Binary | No | Yes | Hive/ACID workloads, large scans |
| **Avro** | Row-oriented | Binary/JSON | Partial (JSON header) | Yes (default values, readers/writers schemas) | Streaming, Kafka, ingest pipelines |
| **JSON** | Row-oriented | Text | Yes | Very flexible | APIs, schema-on-read, semi-structured |
| **CSV** | Row-oriented | Text | Yes | No | Simple exchange, legacy sources |

---

## 2. Deep Dive: Parquet

**How it stores data:**
```
File ──► Row Group 1 ──► Column Chunk "amount" ──► Page 1 (dict)
       │                │                        └── Page 2 (data)
       │                └── Column Chunk "status" ──► ...
       └── Row Group 2 ──► ...
```

**Key features:**
- **Column pruning**: Query engines read only the columns needed
- **Predicate pushdown**: Min/max statistics per row group (aka row group
  pruning) skip irrelevant row groups without reading them
- **Encoding**: Dictionary encoding, run-length encoding (RLE), delta
  encoding — chosen automatically based on data
- **Compression**: Snappy (default), Zstd, Gzip, LZ4 — applied per page
- **Schema**: Stored in the file footer as Thrift metadata

**How row group pruning works (critical for performance):**
```sql
SELECT SUM(amount) FROM orders WHERE status = 'DELIVERED'
--                                └─────────┬──────────┘
--                                           ▼
-- Engine checks each row group's min/max for 'status'
-- Skips row groups where 'DELIVERED' doesn't appear
```

---

## 3. Deep Dive: Avro

**How it stores data:**
```
File ──► Header (schema JSON) ──► Block 1 ──► Block 2 ──► ...
                                   │
                                   └── sync marker + objects
```

**Key features:**
- **Schema with the data** — the file is self-describing
- **Reader/writer schema resolution**: Writer schema can differ from
  reader schema (missing fields filled with defaults)
- **Splittable** (with container file format) but less efficient at
  column pruning than Parquet
- **Preferred format for Kafka**: Schema Registry stores the Avro schema,
  messages are tiny binary payloads

---

## 4. Deep Dive: ORC

Similar to Parquet with some differences:
- **Stripe** instead of Row Group
- **Built-in indexes** (min/max, bloom filters per stripe) for more
  aggressive predicate pushdown
- **ACID support** in Hive (INSERT/UPDATE/DELETE on ORC tables)
- Less portable than Parquet — mostly used in Hive/Hadoop ecosystems

---

## 5. Compression Codecs for DE

| Codec | Speed | Ratio | Splittable | Use Case |
|---|---|---|---|---|
| **Snappy** | Fastest | Low | No* | Default for Parquet — balance of speed and size |
| **LZ4** | Fastest | Low | No | When speed is the only priority (Spark shuffle) |
| **Zstd** | Fast | Medium | No | Better ratio than Snappy at similar speed (newer, becoming default) |
| **Gzip** | Slow | High | No | Archival, cold storage, rare access |
| **Brotli** | Slow | High | No | Web/HTTP, less common in DE |

*\*Splittable at file level when the container format is splittable
(Parquet/ORC/Avro splits on boundaries, codec compression is per-block).*

**DE interview rule:** Default to **Snappy** for Parquet (performance),
**Zstd** if you need better compression without much speed loss.

---

## 6. Format Decision Matrix

| Scenario | Recommended Format | Why |
|---|---|---|
| Analytics on 100 TB | Parquet | Column pruning, predicate pushdown |
| Kafka message payload | Avro | Schema evolution, Schema Registry |
| Quick data exploration | JSON or Parquet | Human readability vs performance |
| Legacy source export | CSV | Universal compatibility |
| Hive ACID transactions | ORC | Only format with full ACID in Hive |
| ML feature store | Parquet | Columnar, fast reads |
| Data lake raw zone (bronze) | JSON/Avro | Schema-on-read, flexible |
| Data lake analytics zone (silver/gold) | Parquet | Optimized for query engines |

---

## 7. Schema Evolution Comparison

| Operation | Parquet | Avro | ORC |
|---|---|---|---|
| Add column | Yes (default null) | Yes (reader default) | Yes |
| Drop column | Yes (reader ignores) | Yes (writer still writes) | Yes |
| Rename column | Via metadata | Via aliases | Complex |
| Change type | Limited (upcast) | Limited (promotion rules) | Limited |
| Reorder columns | No impact | No impact (by name) | No impact |

---

## Quick Reference

| Question | Answer |
|---|---|
| What format for analytics? | **Parquet** — default for any DE interview |
| What format for Kafka? | **Avro** — schema registry + small payloads |
| What compression for Parquet? | **Snappy** or **Zstd** |
| Column pruning? | Parquet reads only needed columns |
| Predicate pushdown? | Parquet/ORC skip row groups based on stats |
| Schema evolution? | **Avro** is most flexible, **Parquet** is good enough |
| ORC vs Parquet? | Parquet unless you need Hive ACID |

>

---

> [!NOTE]
> The Parquet vs Avro question is one of the most common DE interview
> questions. The standard answer: Parquet for analytics (columnar),
> Avro for streaming/writes (row-oriented, schema evolution).
