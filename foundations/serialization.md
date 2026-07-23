# Serialization & Data Encoding

Serialization converts in-memory data structures to bytes (and back).
In data engineering, serialization choices affect **storage efficiency**,
**query speed**, **schema evolution flexibility**, and **interoperability**.

> [!TIP]
> For Spark-specific serialization (Kryo vs Java, Tungsten UnsafeRow),
> see [`apache-spark-pyspark/serialization.md`](../apache-spark-pyspark/serialization.md).

---

## The Core Problem

| Concern | Why It Matters |
|---|---|
| Size | Smaller payloads → less storage cost, faster I/O, faster network transfer |
| Speed | Fast encode/decode → lower CPU overhead per row |
| Schema evolution | Can readers handle new fields? Can writers drop old fields? |
| Language support | Does your consumer ecosystem (Python, Java, Go, Rust) have good bindings? |
| Splittability | Can you read a subset of a file without parsing all of it? |

---

## Common Data Format Families

### 1. Row-Oriented Formats

Write row by row — good for full-row reads, poor for column subset scans.

| Format | Encoding | Schema | Compression | Best For |
|---|---|---|---|---|
| **JSON** | Text, self-describing | Optional | Moderate | APIs, logs, Kafka events |
| **CSV** | Text, delimiter-separated | None | Moderate (per file) | Legacy systems, spreadsheets |
| **Avro** | Binary + optional JSON schema | Required (embedded or registry) | Good (codec per block) | Kafka messages, row-level streaming, cross-language |
| **Protobuf** | Binary | Required (`.proto` files) | Good (wire format) | Low-latency services, strongly typed pipelines |
| **Thrift** | Binary / compact / dense | Required (`.thrift` files) | Good | Cross-service RPC, legacy Hadoop ecosystem |

### 2. Column-Oriented Formats

Store column values together — enables projection pushdown, better compression for low-cardinality columns.

| Format | Schema | Compression | Best For |
|---|---|---|---|
| **Parquet** | Required (embedded in footer) | Excellent (column stats, dictionary, run-length, Snappy/Zstd) | Analytical queries, Spark/Presto/Trino workloads |
| **ORC** | Required (embedded) | Excellent (similar to Parquet + optional bloom filters) | Hive-heavy workloads, ACID transactions on Hive |

> [!NOTE]
> **Avro vs Parquet is not a competition — they are complementary.**
> Use Avro for **streaming / messaging** (row-level writes, schema registry).
> Use Parquet for **analytical storage** (column pruning, predicate pushdown).

---

## Avro Deep Dive

### Schema Storage

Avro schemas are JSON. Two storage modes:

- **Embedded schema:** Schema stored in the file header → self-describing but bloated for many small files
- **Schema Registry:** Schema stored externally (Confluent Schema Registry, Apicurio) → stores only a 4-byte schema ID in each record

### Schema Evolution Rules (Avro)

| Change | Backward Compatible? | Forward Compatible? |
|---|---|---|
| Add field with default | Yes | Yes |
| Remove field with default | Yes (reader has default) | Yes |
| Rename field (alias) | Yes (with alias) | Yes (with alias) |
| Change type (int → long) | Yes (widening) | Yes |
| Change type (long → int) | No | No |
| Remove a type from union | Yes | No |

### Avro in Kafka

```json
{
  "type": "record",
  "name": "OrderEvent",
  "fields": [
    {"name": "order_id", "type": "string"},
    {"name": "amount", "type": "double"},
    {"name": "customer_id", "type": "int"},
    {"name": "discount", "type": ["null", "double"], "default": null}
  ]
}
```

Flink consumer config:
```sql
CREATE TABLE orders (
  order_id STRING, amount DOUBLE, customer_id INT, discount DOUBLE
) WITH (
  'connector' = 'kafka',
  'format' = 'avro-confluent',
  'avro-confluent.schema-registry.url' = 'http://schema-registry:8081'
);
```

---

## Protobuf Deep Dive

### Key Differences from Avro

| Avro | Protobuf |
|---|---|
| Schema = JSON | Schema = `.proto` file |
| Dynamic typing (schemas at read time) | Static typing (generated classes at compile time) |
| Union types with `[type1, type2]` | `oneof` keyword |
| No field numbers assigned by user | Field numbers matter (wire format) |
| Easier for schema-on-read / ad-hoc queries | Better for strongly typed RPC / gRPC |

### Schema Evolution Rules (Protobuf)

- Never change field numbers
- New field: assign new number, must be optional or have default
- Remove field: use reserved keyword to prevent reuse
- Rename: change name in `.proto`, wire format unchanged (uses field numbers)

> [!WARNING]
> In Protobuf, reusing a field number with a different type causes
> silent data corruption. Use `reserved` for deleted fields.

---

## Parquet Deep Dive

### File Structure

```
Parquet File
├── Magic bytes (PAR1)
├── Row groups (horizontal partitions of rows)
│   ├── Column chunks (one per column per row group)
│   │   ├── Data pages
│   │   └── Dictionary pages (optional)
│   └── Column metadata (encoding, stats, offsets)
├── Footer metadata
│   ├── Schema
│   ├── Row group metadata
│   └── Column statistics (min, max, null count)
└── Footer length (4 bytes) + magic (PAR1)
```

### Why Parquet is Fast for Analytics

1. **Column projection:** Read only requested columns (skip entire column chunks)
2. **Statistics-based pruning:** Min/max/null counts skip entire row groups
3. **Dictionary encoding:** Repeated values stored once → tiny reads
4. **Predicate pushdown:** `WHERE date = '2024-01-01'` skips incompatible row groups at file level
5. **Compression per page:** Zstd, Snappy, LZ4, Gzip — choose based on CPU vs size tradeoff

### Parquet + Spark

```python
df.write \
  .mode("overwrite") \
  .format("parquet") \
  .option("compression", "zstd") \
  .option("parquet.block.size", 256 * 1024 * 1024) \
  .save("s3://warehouse/orders/")
```

```python
spark.conf.set("spark.sql.parquet.filterPushdown", "true")
spark.conf.set("spark.sql.parquet.columnarReaderBatchSize", 4096)
```

---

## Compression Comparison

| Codec | Speed | Ratio | Splittable | Best For |
|---|---|---|---|---|
| Snappy | Very fast | Low | In container format | Balanced throughput |
| Zstd | Fast | Medium | In container format | Best overall for Parquet/ORC |
| Gzip | Slow | High | No (unless container-level) | Cold storage, archival |
| LZ4 | Fastest | Low | In container format | Latency-sensitive, Spark shuffle |
| Bzip2 | Very slow | Highest | Yes | Archival, rarely used |

---

## Quick Decision Framework

| Use Case | Format |
|---|---|
| Kafka messages / CDC streams | Avro + Schema Registry |
| Inter-service gRPC | Protobuf |
| Analytical queries on S3/ADLS/GCS | Parquet + Zstd |
| Hive ACID / LLAP | ORC |
| Real-time dashboards (ClickHouse) | Native columnar (not Parquet) |
| Quick ad-hoc data exchange | JSON |
| ML training data | Parquet (for structured), TFRecord (for features) |

---

## Key Interview Questions

### "Why not store everything as JSON?"
- Larger on disk (text, repeated key names)
- No schema enforcement → silent data corruption
- Slow parsing (no column pruning, no predicate pushdown)
- Example: 1 TB of JSON → ~300 GB as Parquet with Snappy

### "Avro vs Parquet — when to use which?"
- **Avro:** Row-level write path, streaming, Kafka, Schema Registry
- **Parquet:** Batch reads, analytical queries, column pruning, predicate pushdown
- Use both in a lakehouse: Avro in Kafka → Iceberg with Parquet files

### "What makes Parquet fast?"
- Column pruning (read subset of columns)
- Statistics-based min/max row group pruning
- Dictionary encoding + run-length encoding
- Predicate pushdown at storage layer

### "What is schema registry?"
- Central store for Avro/Protobuf schemas
- Stores a schema under a subject (`topic-value`)
- Producer embeds 4-byte schema ID, consumer fetches schema by ID
- Enforces compatibility checks on publish

---

## References

- [Avro Specification](https://avro.apache.org/docs/current/spec.html)
- [Protobuf Language Guide](https://protobuf.dev/programming-guides/proto3/)
- [Parquet Format](https://parquet.apache.org/docs/file-format/)
- [Confluent Schema Registry docs](https://docs.confluent.io/platform/current/schema-registry/)
