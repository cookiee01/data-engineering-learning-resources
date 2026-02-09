# PySpark Practice Journey (Q&A + Tasks + Code)

This is a structured PySpark practice path designed to feel like a guided lesson.

Rules of this document:
- Every section is in **Q&A** format.
- You always get: **Task → Code → Expected output → Gotchas**.
- Prefer Spark built-ins. Avoid UDFs unless required.

## Setup (one-time)
From:
`/Users/arpitsingh/MyWorkingDir/PycharmProjects/data-engineering-learning-resources/apache-spark-pyspark/`

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Data used
- `data/orders.csv` (small)
- `data/orders_extended.csv` (for ranking/windows/ties)
- `data/users.json` (nested JSON)
- `data/events_multiline.json` (multiline JSON array)
- `data/items.xml` (XML demo; requires extra package)

---

# Part A — Reading Data (CSV / JSON / Parquet / XML / JDBC)

## Q1) What is Spark doing when I write DataFrame code?
**Answer (mental model)**
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

**Gotchas**
- `collect()` brings all rows to the driver.

---

## Q2) How do I read CSV reliably (schema + corrupt rows)?
**Answer**
CSV is untyped. Prefer explicit schema and a corrupt-record strategy.

**Task**
- Read CSV with explicit schema.

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
- `inferSchema=True` can misread columns (especially timestamps).
- In production, set `mode=FAILFAST` when you want ingestion to stop on bad lines.

---

## Q3) How do I read JSONL and flatten nested JSON?
**Answer**
- JSONL is easiest: one JSON object per line.
- Flatten nested fields using dotted paths.

**Task**
- Read `users.json`.
- Flatten fields.

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

---

## Q4) How do I read multiline JSON (a JSON array file)?
**Answer**
Use `multiLine=True`.

**Task**
- Read `events_multiline.json`.

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
Parquet is columnar, typed, and typically faster/cheaper for analytics.

**Task**
- Write Parquet.
- Read back.

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

---

## Q6) How do I read XML in Spark?
**Answer**
Spark doesn’t support XML by default. You commonly use `spark-xml`.

**Task**
- Read `items.xml` with spark-xml.

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
- Package download requires network access and can be flaky behind proxies.

---

# Part B — Core Operations (select/filter/withColumn/nulls)

## Q7) What are the core DataFrame operations I must be fluent in?
**Answer**
You should be fast with:
- `select`, `withColumn`, `filter`, `when`, `cast`
- null handling (`coalesce`, `na.fill`, `na.drop`)

**Task**
- Normalize status.
- Filter invalid amounts.

**Code**
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lit, coalesce

spark = SparkSession.builder.appName("q7_core_ops").master("local[*]").getOrCreate()

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

# Part C — Aggregations (sum/avg/count) + Ranking/Windows

## Q8) How do I compute sum/avg/count per group?
**Answer**
Use `groupBy(...).agg(...)`.

**Task**
Compute per-country metrics.

**Code**
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, avg as _avg, count as _count

spark = (
    SparkSession.builder.appName("q8_aggs")
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
- Aggregations create shuffles.

---

## Q9) How do I rank things using dense_rank (and why dense_rank vs rank)?
**Answer**
- `rank()` leaves gaps when there are ties.
- `dense_rank()` does not leave gaps.

**Task**
Rank customers by total spend within each country.

**Code**
```python
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import col, sum as _sum, dense_rank

spark = SparkSession.builder.appName("q9_dense_rank").master("local[*]").getOrCreate()

orders = spark.read.csv("data/orders_extended.csv", header=True, inferSchema=True)

spend = orders.groupBy("country", "customer_id").agg(_sum("amount").alias("total_spend"))

w = Window.partitionBy("country").orderBy(col("total_spend").desc())
ranked = spend.withColumn("dense_rank", dense_rank().over(w)).orderBy("country", "dense_rank")

ranked.show(truncate=False)

spark.stop()
```

**Expected output**
- You should see ties share the same `dense_rank`.

---

## Q10) How do I do “keep latest record per key” correctly?
**Answer**
Use window + `row_number()`.

**Task**
Keep the latest order per customer.

**Code**
```python
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import col, row_number

spark = SparkSession.builder.appName("q10_latest_per_key").master("local[*]").getOrCreate()

orders = spark.read.csv("data/orders_extended.csv", header=True, inferSchema=True)

w = Window.partitionBy("customer_id").orderBy(col("order_ts").desc())
latest = orders.withColumn("rn", row_number().over(w)).filter(col("rn") == 1).drop("rn")

latest.orderBy("customer_id").show(truncate=False)

spark.stop()
```

---

# Part D — Joins

## Q11) Why are joins dangerous in Spark and how do I avoid surprises?
**Answer**
- If join keys aren’t unique, outputs multiply.
- Large joins shuffle; small dimension can be broadcast.

**Task**
Join orders with users.

**Code**
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder.appName("q11_joins").master("local[*]").getOrCreate()

orders = spark.read.csv("data/orders_extended.csv", header=True, inferSchema=True)
users = spark.read.json("data/users.json").select(
    col("user.id").alias("customer_id"),
    col("user.name").alias("name"),
    col("user.tier").alias("tier"),
)

joined = orders.join(users, on="customer_id", how="left")
joined.select("order_id", "customer_id", "name", "tier", "amount", "country").show(truncate=False)

spark.stop()
```

---

# Part E — Writing + Performance Basics

## Q12) How do I write outputs in an idempotent way for practice?
**Answer**
- Use deterministic output paths.
- Use `mode("overwrite")` for practice.

**Task**
Write curated orders excluding cancelled.

**Code**
```python
import shutil
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder.appName("q12_write_idempotent").master("local[*]").getOrCreate()

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

## Q13) What are the 3 performance levers I must mention in interviews?
**Answer**
1. Shuffles are expensive.
2. Partitioning controls parallelism.
3. Caching avoids recomputation.

**Task**
- Inspect partitions.
- `explain()` for a shuffle.
- Cache and run 2 actions.

**Code**
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = (
    SparkSession.builder.appName("q13_perf")
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
