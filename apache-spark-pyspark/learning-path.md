# PySpark Learning Path (Core → Internals → Optimization)

This is a structured list of topics to learn in a sensible order for production-grade PySpark work.

## 0) Setup and Mental Model
- What Spark is: driver, executors, tasks, stages, jobs
- Lazy evaluation: transformations vs actions
- Narrow vs wide transformations (and why wide ones are expensive)
- DataFrame vs RDD: why DataFrames are the default choice for most pipelines

## 1) DataFrames You Should Be Fluent In
- Columns and expressions: `select`, `withColumn`, `when/otherwise`, `coalesce`, `lit`, `expr`
- Nulls: `isNull/isNotNull`, null-safe equality, `na.fill/na.drop`
- Types: `StructType`, `ArrayType`, `MapType`, `DecimalType` (avoid accidental `double`)
- Nested data: `from_json`, `to_json`, `explode`, `explode_outer`
- Common patterns:
  - dedup: `dropDuplicates`, `row_number`-based de-dupe
  - data quality checks: counts, null-rate, distinct-rate, min/max, referential checks
  - “latest per key” and “top-N per group” with windows

## 2) Reading and Writing Data (Real-World I/O)
- CSV: headers, delimiter, quotes/escape, corrupt records handling
- JSON:
  - multiline JSON
  - schema-on-read (explicit schema vs inference)
  - schema drift handling (new columns, missing fields, type changes)
- XML (when you must): record tags, attributes, nested elements, schema choices
- Parquet/ORC:
  - schema evolution basics
  - predicate pushdown + projection pruning (why column selection matters)
- Partitioned datasets:
  - partition columns vs physical layout
  - partition pruning (including why filters must be on partition columns)
  - “small files” problem and compaction strategy
- Output modes:
  - overwrite vs append
  - dynamic partition overwrite (and why it matters)

## 3) Aggregations (Beyond `avg` and `sum`)
- Standard aggregations: `count`, `countDistinct`, `approx_count_distinct`, `collect_set/list`
- Conditional aggregations:
  - `sum(when(cond, 1).otherwise(0))` patterns
  - multi-metric aggregations in one pass
- Pivot: when it’s appropriate, when it explodes cardinality
- Percentiles: `percentile_approx` and tradeoffs
- Grouped map patterns to avoid (Python UDFs that cause massive slowdowns)

## 4) Window Functions (Ranking, Sessionization, Time-Series)
- Ranking:
  - `row_number` vs `rank` vs `dense_rank` (and when each is correct)
  - tie-handling and deterministic ordering
- Time-based windows:
  - `lag/lead` for deltas
  - rolling windows using window frames
- Sessionization fundamentals:
  - define session boundaries
  - compute session id, session start/end, session metrics

## 5) Joins (Correctness + Performance)
- Join types: inner/left/right/full/semi/anti
- Correctness topics:
  - duplicate amplification (many-to-many)
  - null-handling in join keys
  - pre-aggregation vs post-join aggregation
- Performance topics:
  - broadcast join: why it’s fast, how Spark decides it, how to control it
  - sort-merge join: why it appears, what it implies (shuffle + sort)
  - skew: how to recognize, why it hurts, common mitigation patterns

## 6) Optimization You Should Know Without Guessing
- Partitioning:
  - `repartition` vs `coalesce`
  - `spark.sql.shuffle.partitions` (and how to size it)
  - “too few tasks” vs “too many tiny tasks”
- Caching/persistence:
  - when caching helps vs hurts
  - storage levels (`MEMORY_ONLY`, `MEMORY_AND_DISK`, `*_SER`)
  - cache lifecycle (unpersist; avoid caching huge intermediates)
- Avoiding Python slow paths:
  - prefer built-in functions (Catalyst-optimizable)
  - Python UDF vs pandas UDF vs SQL expressions
  - Arrow: what it accelerates, what it doesn’t
- Adaptive Query Execution (AQE):
  - what it changes (join strategies, skew handling, coalesced shuffle partitions)
  - how to verify it’s helping (Spark UI / explain plans)

## 7) Spark UI and Explain Plans (The Debugging Toolkit)
- `df.explain()` / `explain(mode="formatted")`: what to look for
  - `Exchange` operators (shuffle boundaries)
  - join operators (broadcast hash join vs sort-merge)
  - `WholeStageCodegen`
- Spark UI:
  - stages and tasks (stragglers, skewed tasks)
  - shuffle read/write size, spill (memory pressure), GC time
  - input size vs output size sanity checks

## 8) Spark SQL Internals (What “Binary Row Format” Means)
You don’t need to memorize code, but you should understand the concepts behind the words:
- Catalyst: logical plan → optimized plan → physical plan
- Encoders and row conversion:
  - why Spark uses encoders for Datasets / typed rows (Scala) and when they matter
  - how DataFrames often avoid creating lots of JVM objects by using internal formats
- `UnsafeRow`:
  - what it represents (compact, binary row format)
  - why it improves CPU and memory usage (less object allocation)

Good references:
- Spark SQL Internals: ExpressionEncoder: https://books.japila.pl/spark-sql-internals/ExpressionEncoder/
- Spark SQL Internals: UnsafeRow: https://books.japila.pl/spark-sql-internals/UnsafeRow/
- Spark SQL Internals: Encoders: https://books.japila.pl/spark-sql-internals/Encoders/

## 9) Serialization (Where Kryo Fits)
- What serialization is in Spark: data/code becomes bytes when it crosses boundaries (network/disk/cache)
- Where it happens:
  - shuffle, spill, broadcast, returning results to driver
  - (Scala/Java) closure shipping
- Kryo vs JavaSerializer:
  - why Kryo often helps JVM-object-heavy workloads
  - why DataFrame-heavy pipelines may see smaller gains (Spark SQL internals already use efficient formats)

In this repo:
- Notes: `serialization.md`

## 10) Streaming (Only If Your Role Needs It)
- Structured Streaming basics: micro-batches, state, watermarks, output modes
- Kafka integration: offsets, backpressure, checkpointing, failure modes
- Exactly-once: what it means in practice (idempotency, sinks, replay)

## Suggested Order in This Repo
- Start: `PYSPARK_QA_JOURNEY.md`
- Then: `serialization.md`
- Use this file as the topic checklist.

