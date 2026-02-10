# PySpark Practice Journey (Q&A + Tasks + Code)

This is a structured PySpark practice path designed to feel like a guided lesson.

Rules of this document:
- Every section is in Q&A format.
- Each section includes: Task → Code → Expected output → Gotchas.
- Prefer Spark built-ins. Avoid Python UDFs unless required.

## Setup (one-time)
From:
`/Users/arpitsingh/MyWorkingDir/PycharmProjects/data-engineering-learning-resources/apache-spark-pyspark/`

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Data used
- `data/orders.csv`
- `data/orders_extended.csv`
- `data/users.json`
- `data/events_multiline.json`
- `data/items.xml` (XML demo)
- `data/schema_drift_v1.jsonl`, `data/schema_drift_v2.jsonl`
- `data/events_sessions.csv`
- `data/payloads.csv` (JSON string column)

---

# Part A — Spark Mental Model

## Q1) What is Spark actually doing when I write DataFrame code?
**Answer**
- Transformations build a plan (lazy).
- Actions execute the plan.

**Task**
- Read CSV.
- Filter.
- `explain()`.
- Trigger `count()`.

**Code**
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = (
    SparkSession.builder
    .appName("q1_mental_model")
    .master("local[*]")
    .config("spark.ui.showConsoleProgress", "false")
    .getOrCreate()
)

df = spark.read.csv("data/orders.csv", header=True, inferSchema=True)

delivered = df.filter(col("status") == "DELIVERED").select("order_id", "customer_id", "amount")

print("=== explain (plan) ===")
delivered.explain(True)

print("=== count (action) ===")
print(delivered.count())

spark.stop()
```

**Expected output**
- `explain()` prints logical and physical plans.
- `count()` prints an integer.

**Gotchas**
- `collect()` brings all rows to the driver; avoid on big datasets.

---

# Part B — Reading Data (CSV / JSON / Parquet / XML / JDBC)

## Q2) How do I read CSV reliably (schema + corrupt rows strategy)?
**Answer**
CSV is untyped. For stable pipelines, provide an explicit schema.

**Task**
Read `orders.csv` with a schema.

**Code**
```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType

spark = SparkSession.builder.appName("q2_read_csv").master("local[*]").getOrCreate()

schema = StructType([
    StructField("order_id", IntegerType(), True),
    StructField("customer_id", IntegerType(), True),
    StructField("order_ts", StringType(), True),
    StructField("status", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("country", StringType(), True),
])

df = (
    spark.read.format("csv")
    .option("header", "true")
    .option("mode", "PERMISSIVE")
    .schema(schema)
    .load("data/orders.csv")
)

df.printSchema()
df.show(truncate=False)

spark.stop()
```

**Gotchas**
- `inferSchema=True` is convenient but can silently change types.
- Use `mode=FAILFAST` when you want ingestion to stop on corrupt rows.

---

## Q3) How do I read JSONL and flatten nested JSON?
**Answer**
- JSONL is one JSON object per line.
- Flatten nested fields using dotted paths: `col("user.id")`.

**Task**
Read `users.json` and flatten it.

**Code**
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder.appName("q3_json_nested").master("local[*]").getOrCreate()

df = spark.read.json("data/users.json")

flat = df.select(
    col("user.id").alias("user_id"),
    col("user.name").alias("name"),
    col("user.tier").alias("tier"),
    col("geo.country").alias("country"),
    col("geo.city").alias("city"),
)

flat.show(truncate=False)

spark.stop()
```

**Gotchas**
- If nested fields are missing in some records, Spark fills nulls.

---

## Q4) How do I read multiline JSON (a JSON array file)?
**Answer**
Use `multiLine=True`.

**Task**
Read `events_multiline.json`.

**Code**
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("q4_multiline_json").master("local[*]").getOrCreate()

df = spark.read.option("multiLine", "true").json("data/events_multiline.json")

df.printSchema()
df.show(truncate=False)

spark.stop()
```

---

## Q5) How do I write Parquet and read it back (and why Parquet)?
**Answer**
Parquet is columnar and typed. It enables predicate pushdown and is usually faster/cheaper for analytics.

**Task**
Write Parquet to `output/` and read it back.

**Code**
```python
import shutil
from pathlib import Path

from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("q5_parquet_write_read").master("local[*]").getOrCreate()

df = spark.read.csv("data/orders.csv", header=True, inferSchema=True)

out = Path("output/orders_parquet")
if out.exists():
    shutil.rmtree(out)

df.write.mode("overwrite").parquet(str(out))

back = spark.read.parquet(str(out))
back.printSchema()
back.show(truncate=False)

spark.stop()
```

**Gotchas**
- Writing many tiny Parquet files hurts performance.

---

## Q6) How do I read XML in Spark (spark-xml)?
**Answer**
Spark doesn’t support XML out of the box. A common approach is `spark-xml`.

**Task**
Read `items.xml` with `rowTag=item`.

**Code**
```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder.appName("q6_xml")
    .master("local[*]")
    .config("spark.jars.packages", "com.databricks:spark-xml_2.12:0.17.0")
    .config("spark.ui.showConsoleProgress", "false")
    .getOrCreate()
)

df = spark.read.format("xml").option("rowTag", "item").load("data/items.xml")
df.show(truncate=False)

spark.stop()
```

**Gotchas**
- Package download can be slow behind proxies.
- XML types are often strings; you will need explicit casting.

---

## Q7) How do I handle schema drift when reading JSON?
**Answer**
Schema drift shows up as:
- New columns appearing
- Columns disappearing
- Type changes (hardest)

Spark behavior:
- Reading multiple JSON files together often yields a superset schema.
- Missing fields become null.

Production rule:
- Don’t rely on inference for important pipelines. Use explicit schema + validation.

**Task**
Read two JSONL files with different fields.

**Code**
```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder.appName("q7_schema_drift_json")
    .master("local[*]")
    .getOrCreate()
)

df = spark.read.json(["data/schema_drift_v1.jsonl", "data/schema_drift_v2.jsonl"])

df.printSchema()
df.orderBy("id").show(truncate=False)

spark.stop()
```

**Expected output**
- `email` exists in the schema.
- v1 rows have `email = null`.

**Gotchas**
- Type drift can break downstream consumers. Add casts + rejects.

---

## Q8) How do I read from JDBC efficiently (partitioned reads)?
**Answer**
JDBC reads become a bottleneck if you read with a single partition.

To parallelize, use:
- `partitionColumn`
- `lowerBound`, `upperBound`
- `numPartitions`

**Task**
Read a Postgres table (requires Postgres running locally).

**Code**
```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder.appName("q8_jdbc")
    .master("local[*]")
    .config("spark.jars.packages", "org.postgresql:postgresql:42.7.3")
    .getOrCreate()
)

df = (
    spark.read.format("jdbc")
    .option("url", "jdbc:postgresql://localhost:5432/demo")
    .option("dbtable", "public.some_table")
    .option("user", "postgres")
    .option("password", "postgres")
    .option("driver", "org.postgresql.Driver")
    .option("partitionColumn", "id")
    .option("lowerBound", 1)
    .option("upperBound", 1000000)
    .option("numPartitions", 8)
    .load()
)

df.show()

spark.stop()
```

**Gotchas**
- Partitioned reads only help if the column is numeric and well-distributed.
- Too many partitions can overload the DB.

---

# Part C — Core Operations (select/filter/withColumn/nulls)

## Q9) What are the core DataFrame operations I must be fluent in?
**Answer**
You should be fast with:
- `select`, `withColumn`, `filter`, `when`, `cast`
- null handling: `coalesce`, `na.fill`, `na.drop`

**Task**
Normalize status and filter invalid amounts.

**Code**
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lit, coalesce

spark = SparkSession.builder.appName("q9_core_ops").master("local[*]").getOrCreate()

df = spark.read.csv("data/orders.csv", header=True, inferSchema=True)

out = (
    df.withColumn("amount", col("amount").cast("double"))
    .withColumn(
        "status_norm",
        when(col("status") == "DELIVERED", lit("DONE"))
        .when(col("status") == "SHIPPED", lit("IN_FLIGHT"))
        .otherwise(lit("OTHER")),
    )
    .withColumn("country", coalesce(col("country"), lit("UNKNOWN")))
    .filter(col("amount") > 0)
    .select("order_id", "customer_id", "status_norm", "amount", "country")
)

out.show(truncate=False)

spark.stop()
```

---

# Part D — Aggregations (sum/avg/count) + Pivot

## Q10) How do I compute sum/avg/count per group?
**Answer**
Use `groupBy(...).agg(...)`.

**Task**
Compute per-country metrics.

**Code**
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, avg as _avg, count as _count

spark = (
    SparkSession.builder.appName("q10_aggs")
    .master("local[*]")
    .getOrCreate()
)

orders = spark.read.csv("data/orders_extended.csv", header=True, inferSchema=True)

by_country = (
    orders.groupBy("country")
    .agg(
        _count("order_id").alias("orders"),
        _sum("amount").alias("total_amount"),
        _avg("amount").alias("avg_amount"),
    )
    .orderBy(col("total_amount").desc())
)

by_country.show(truncate=False)

spark.stop()
```

**Gotchas**
- groupBy creates a shuffle.

---

## Q11) How do I do conditional aggregations (delivered revenue, cancelled count)?
**Answer**
Conditional aggs are `sum(when(condition, value).otherwise(default))`.

**Task**
Compute per-country totals and delivered/cancelled breakdown.

**Code**
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum as _sum, when, lit

spark = (
    SparkSession.builder.appName("q11_conditional_aggs")
    .master("local[*]")
    .getOrCreate()
)

orders = spark.read.csv("data/orders_extended.csv", header=True, inferSchema=True)

by_country = (
    orders.groupBy("country")
    .agg(
        count(lit(1)).alias("orders_total"),
        _sum(when(col("status") == "DELIVERED", 1).otherwise(0)).alias("orders_delivered"),
        _sum(when(col("status") == "CANCELLED", 1).otherwise(0)).alias("orders_cancelled"),
        _sum(when(col("status") == "DELIVERED", col("amount")).otherwise(0.0)).alias("revenue_delivered"),
    )
    .orderBy(col("revenue_delivered").desc())
)

by_country.show(truncate=False)

spark.stop()
```

**Gotchas**
- If you forget `otherwise(0)`, sums can become null.

---

## Q12) How do I pivot in PySpark (and when should I avoid it)?
**Answer**
Pivot turns row values into columns.

**Task**
Pivot status counts by country.

**Code**
```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder.appName("q12_pivot")
    .master("local[*]")
    .getOrCreate()
)

orders = spark.read.csv("data/orders_extended.csv", header=True, inferSchema=True)

pivoted = orders.groupBy("country").pivot("status").count().na.fill(0)

pivoted.show(truncate=False)

spark.stop()
```

**Gotchas**
- Pivot on high-cardinality columns can explode into thousands of columns.

---

# Part E — JSON String Parsing + explode

## Q13) How do I parse a JSON string column using from_json (and explode arrays)?
**Answer**
Common in Kafka/CSV ingestion: a column contains JSON as string.

Safe pattern:
- Define schema
- Parse with `from_json`
- Flatten arrays with `explode`

**Task**
Parse `payloads.csv` and explode items.

**Code**
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, explode
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, ArrayType

spark = (
    SparkSession.builder.appName("q13_from_json_explode")
    .master("local[*]")
    .getOrCreate()
)

payload_schema = StructType([
    StructField("order_id", IntegerType(), True),
    StructField(
        "items",
        ArrayType(
            StructType([
                StructField("sku", StringType(), True),
                StructField("qty", IntegerType(), True),
            ])
        ),
        True,
    ),
    StructField(
        "meta",
        StructType([
            StructField("source", StringType(), True),
        ]),
        True,
    ),
])

raw = spark.read.csv("data/payloads.csv", header=True, inferSchema=True)
parsed = raw.withColumn("payload_struct", from_json(col("payload"), payload_schema))

items = (
    parsed.select(
        col("id"),
        col("payload_struct.order_id").alias("order_id"),
        col("payload_struct.meta.source").alias("source"),
        explode(col("payload_struct.items")).alias("item"),
    )
    .select(
        "id",
        "order_id",
        "source",
        col("item.sku").alias("sku"),
        col("item.qty").alias("qty"),
    )
)

items.show(truncate=False)

spark.stop()
```

**Gotchas**
- `from_json` returns null on corrupt JSON; validate.

---

# Part F — Window Functions (rank/dense_rank/ntile) + Sessionization

## Q14) How do I pick between row_number / rank / dense_rank / ntile?
**Answer**
- `row_number`: unique numbering (ties get different numbers)
- `rank`: ties share rank, but gaps occur
- `dense_rank`: ties share rank, no gaps
- `ntile(n)`: buckets rows into n groups

**Task**
Rank customers by spend within each country.

**Code**
```python
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import col, sum as _sum, row_number, rank, dense_rank, ntile

spark = (
    SparkSession.builder.appName("q14_ranking")
    .master("local[*]")
    .getOrCreate()
)

orders = spark.read.csv("data/orders_extended.csv", header=True, inferSchema=True)
spend = orders.groupBy("country", "customer_id").agg(_sum("amount").alias("total_spend"))

w = Window.partitionBy("country").orderBy(col("total_spend").desc())

ranked = (
    spend
    .withColumn("row_number", row_number().over(w))
    .withColumn("rank", rank().over(w))
    .withColumn("dense_rank", dense_rank().over(w))
    .withColumn("ntile_3", ntile(3).over(w))
    .orderBy("country", "row_number")
)

ranked.show(truncate=False)

spark.stop()
```

---

## Q15) How do I do “keep latest record per key” correctly?
**Answer**
Use `row_number()` with a window ordered by timestamp desc.

**Task**
Keep the latest order per customer.

**Code**
```python
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import col, row_number

spark = (
    SparkSession.builder.appName("q15_latest_per_key")
    .master("local[*]")
    .getOrCreate()
)

orders = spark.read.csv("data/orders_extended.csv", header=True, inferSchema=True)

w = Window.partitionBy("customer_id").orderBy(col("order_ts").desc())
latest = orders.withColumn("rn", row_number().over(w)).filter(col("rn") == 1).drop("rn")

latest.orderBy("customer_id").show(truncate=False)

spark.stop()
```

---

## Q16) How do I parse timestamps and avoid timezone bugs?
**Answer**
- Parse strings using `to_timestamp`.
- Control timezone with `spark.sql.session.timeZone`.
- Prefer storing timestamps in UTC.

**Task**
Parse events and convert to IST.

**Code**
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, from_utc_timestamp

spark = (
    SparkSession.builder.appName("q16_timestamps")
    .master("local[*]")
    .getOrCreate()
)

spark.conf.set("spark.sql.session.timeZone", "UTC")

df = spark.read.csv("data/events_sessions.csv", header=True, inferSchema=True)
parsed = df.withColumn("ts_parsed", to_timestamp(col("ts")))

as_ist = parsed.withColumn("ts_ist", from_utc_timestamp(col("ts_parsed"), "Asia/Kolkata"))

as_ist.select("user_id", "ts", "ts_parsed", "ts_ist", "event").show(truncate=False)

spark.stop()
```

---

## Q17) How do I do sessionization (session-like windows) in batch Spark?
**Answer**
Sessionization groups events into sessions based on an inactivity gap.

Algorithm:
- sort by user + timestamp
- compute gap from previous event
- new session if gap > threshold
- cumulative sum of boundaries is session_id

**Task**
Sessionize events with a 30-minute gap.

**Code**
```python
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import col, to_timestamp, lag, unix_timestamp, when, sum as _sum

spark = (
    SparkSession.builder.appName("q17_sessionization")
    .master("local[*]")
    .getOrCreate()
)

spark.conf.set("spark.sql.session.timeZone", "UTC")

events = (
    spark.read.csv("data/events_sessions.csv", header=True, inferSchema=True)
    .withColumn("ts_parsed", to_timestamp(col("ts")))
)

w = Window.partitionBy("user_id").orderBy(col("ts_parsed").asc())

events2 = events.withColumn("prev_ts", lag("ts_parsed").over(w))

events3 = events2.withColumn(
    "gap_minutes",
    (unix_timestamp(col("ts_parsed")) - unix_timestamp(col("prev_ts"))) / 60.0,
)

events4 = events3.withColumn(
    "is_new_session",
    when(col("prev_ts").isNull() | (col("gap_minutes") > 30), 1).otherwise(0),
)

events5 = events4.withColumn(
    "session_id",
    _sum(col("is_new_session")).over(w),
)

events5.select("user_id", "ts_parsed", "event", "gap_minutes", "session_id").orderBy("user_id", "ts_parsed").show(truncate=False)

spark.stop()
```

**Gotchas**
- Sessionization is sensitive to timestamp parsing and timezone.

---

# Part G — Join Performance (broadcast + skew)

## Q18) How do I use broadcast joins to avoid shuffles?
**Answer**
If one side is small (dimension), broadcasting it can avoid shuffle.

**Task**
Join orders with a small dimension using broadcast and inspect the plan.

**Code**
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import broadcast

spark = (
    SparkSession.builder.appName("q18_broadcast_join")
    .master("local[*]")
    .getOrCreate()
)

dim = spark.createDataFrame([(101, "gold"), (102, "bronze"), (103, "silver")], ["customer_id", "tier"])
fact = spark.read.csv("data/orders_extended.csv", header=True, inferSchema=True)

joined = fact.join(broadcast(dim), on="customer_id", how="left")
joined.explain(True)

spark.stop()
```

**Gotchas**
- Broadcast only if the dimension fits comfortably in memory.

---

## Q19) What is join skew and how do I mitigate it (AQE + salting)?
**Answer**
Skew = one key dominates, one task runs forever.

Mitigations you should know:
- AQE skew join handling:
  - `spark.sql.adaptive.enabled=true`
  - `spark.sql.adaptive.skewJoin.enabled=true`
- Salting the hot key:
  - Split a hot key into N sub-keys on the big side
  - Duplicate the small side across the same salts

**Task**
Run a skew join baseline and a salted join.

**Code**
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, rand, floor, concat

spark = (
    SparkSession.builder.appName("q19_skew_join")
    .master("local[*]")
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.sql.adaptive.skewJoin.enabled", "true")
    .getOrCreate()
)

salt_buckets = 8

big = spark.range(0, 5000).select(lit("HOT").alias("key"), col("id").alias("v"))
small = spark.createDataFrame([("HOT", "meaning")], ["key", "label"])

# Baseline skewed join
baseline = big.join(small, on="key", how="left")
baseline.explain(True)

# Salt the big side
big_s = (
    big.withColumn("salt", floor(rand(seed=7) * salt_buckets).cast("int"))
    .withColumn("key_s", concat(col("key"), lit("#"), col("salt")))
)

# Duplicate the small side across all salts
salts = spark.range(0, salt_buckets).select(col("id").cast("int").alias("salt"))
small_s = (
    small.crossJoin(salts)
    .withColumn("key_s", concat(col("key"), lit("#"), col("salt")))
    .select("key_s", "label")
)

salted = big_s.join(small_s, on="key_s", how="left")
salted.explain(True)

spark.stop()
```

**Gotchas**
- Salting increases data size because you duplicate the small side.
- Try AQE before salting.

---

# Part H — Writing + Performance Basics

## Q20) How should I write outputs in an idempotent way for practice?
**Answer**
Use deterministic output paths and `mode("overwrite")` for practice.

**Task**
Write curated orders excluding cancelled.

**Code**
```python
import shutil
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = (
    SparkSession.builder.appName("q20_write_idempotent")
    .master("local[*]")
    .getOrCreate()
)

orders = spark.read.csv("data/orders_extended.csv", header=True, inferSchema=True)
curated = orders.filter(col("status") != "CANCELLED")

out = Path("output/orders_curated")
if out.exists():
    shutil.rmtree(out)

curated.write.mode("overwrite").parquet(str(out))
print("Wrote", out)

spark.stop()
```

---

## Q21) What are the 3 performance levers I must mention in interviews?
**Answer**
1. Shuffles are expensive.
2. Partitioning controls parallelism.
3. Caching avoids recomputation.

**Task**
- Inspect partitions.
- Use `explain()`.
- Cache and run 2 actions.

**Code**
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = (
    SparkSession.builder.appName("q21_perf")
    .master("local[*]")
    .getOrCreate()
)

orders = spark.read.csv("data/orders_extended.csv", header=True, inferSchema=True)
print("Default partitions:", orders.rdd.getNumPartitions())

by_country = orders.groupBy("country").count()
by_country.explain(True)

filtered = orders.filter(col("status") == "DELIVERED").cache()
print("First count:", filtered.count())
print("Second count:", filtered.count())

spark.stop()
```

---

## Q22) How do I verify partition pruning on partitioned Parquet reads?
**Answer**
Partition pruning means Spark skips partitions that cannot match your filter.

**Task**
- Write Parquet partitioned by country.
- Filter by one country.
- Inspect `explain()`.

**Code**
```python
import shutil
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = (
    SparkSession.builder.appName("q22_partition_pruning")
    .master("local[*]")
    .getOrCreate()
)

orders = spark.read.csv("data/orders_extended.csv", header=True, inferSchema=True)

out = Path("output/orders_part_by_country")
if out.exists():
    shutil.rmtree(out)

orders.write.mode("overwrite").partitionBy("country").parquet(str(out))

read_back = spark.read.parquet(str(out))
filtered = read_back.filter(col("country") == "IN")

filtered.explain(True)
filtered.show(truncate=False)

spark.stop()
```
