# PySpark Practice Journey (Q&A + Tasks + Code)

This is the **primary** PySpark practice track.

Style:
- Each section is a **question** you should be able to answer in an interview.
- Then a **task** you run locally.
- Then the **exact code** (copy/paste runnable).
- Then **expected output** + **gotchas**.

## Setup (one-time)
From:
`/Users/arpitsingh/MyWorkingDir/PycharmProjects/data-engineering-learning-resources/apache-spark-pyspark/`

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Practice Data
We use these small local files:
- `data/orders.csv`
- `data/users.json`
- `data/events_multiline.json`
- `data/items.xml` (XML demo)

---

## Q1) What is Spark actually doing when I write DataFrame code?
**Answer (mental model)**
- Most DataFrame operations are **transformations**: they build a *plan* (lazy).
- Spark only runs work when you call an **action** (`count`, `collect`, `write`, etc.).

**Task**
- Read a CSV.
- Filter rows.
- Print `explain()`.
- Trigger an action.

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
- `explain()` prints logical + physical plans.
- `count()` prints an integer.

**Gotchas**
- `collect()` pulls data to the driver; avoid on large datasets.

---

## Q2) How do I read CSV reliably (without schema surprises)?
**Answer**
- CSV is untyped. In production, prefer explicit schema.

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
- `inferSchema=True` is convenient but can mis-infer dates/ints.
- Use `mode=FAILFAST` when you want ingestion to fail on corrupt rows.

---

## Q3) How do I read JSONL and flatten nested JSON?
**Answer**
- Spark reads JSONL naturally (one JSON per line).
- Use dotted paths (`col("user.id")`) to flatten.

**Task**
- Read `data/users.json`.
- Flatten nested fields.

**Code**
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder.appName("q3_read_json_nested").master("local[*]").getOrCreate()

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
- If JSON has evolving schema, Spark may set fields to null for missing keys.

---

## Q4) How do I read multiline JSON (a JSON array file)?
**Answer**
- Use `option("multiLine", "true")`.

**Task**
- Read `data/events_multiline.json`.

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

## Q5) What are the core DataFrame operations I must be fluent in?
**Answer**
You should be fast with:
- `select`, `withColumn`, `filter`
- `when`, `cast`
- null handling: `coalesce`, `na.fill`, `na.drop`

**Task**
- Normalize status.
- Filter invalid amounts.

**Code**
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lit, coalesce

spark = SparkSession.builder.appName("q5_core_ops").master("local[*]").getOrCreate()

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

## Q6) Why are joins dangerous in Spark?
**Answer**
Because duplicates can multiply rows ("join explosion").

**Task**
- Join orders with users.

**Code**
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder.appName("q6_joins").master("local[*]").getOrCreate()

orders = spark.read.csv("data/orders.csv", header=True, inferSchema=True)
users = spark.read.json("data/users.json").select(
    col("user.id").alias("customer_id"),
    col("user.name").alias("name"),
    col("user.tier").alias("tier"),
)

joined = orders.join(users, on="customer_id", how="left")
joined.show(truncate=False)

spark.stop()
```

**Gotchas**
- If either side has duplicates on the join key, output rows multiply.

---

## Q7) How do I do aggregations and window functions?
**Answer**
- Aggregations: `groupBy().agg(...)`
- Windows: define partition + ordering, then compute per-row metrics.

**Task**
- Per-customer order count + total amount.
- Keep latest order per customer.

**Code**
```python
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import col, sum as _sum, count as _count, row_number

spark = SparkSession.builder.appName("q7_aggs_windows").master("local[*]").getOrCreate()

orders = spark.read.csv("data/orders.csv", header=True, inferSchema=True)

agg = orders.groupBy("customer_id").agg(
    _count("order_id").alias("orders"),
    _sum("amount").alias("total_amount"),
)
agg.show(truncate=False)

w = Window.partitionBy("customer_id").orderBy(col("order_ts").desc())
latest = orders.withColumn("rn", row_number().over(w)).filter(col("rn") == 1).drop("rn")
latest.show(truncate=False)

spark.stop()
```

---

## Q8) How should I write data (and avoid the small files problem)?
**Answer**
- For practice, `mode("overwrite")` gives idempotent runs.
- For tiny outputs, `coalesce(1)` can reduce file count.

**Task**
- Write a curated Parquet output.

**Code**
```python
import shutil
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder.appName("q8_write").master("local[*]").getOrCreate()

df = spark.read.csv("data/orders.csv", header=True, inferSchema=True)
curated = df.filter(col("status") != "CANCELLED")

out_dir = Path("output/orders_curated")
if out_dir.exists():
    shutil.rmtree(out_dir)

curated.write.mode("overwrite").parquet(str(out_dir))

out_dir2 = Path("output/orders_curated_single_file")
if out_dir2.exists():
    shutil.rmtree(out_dir2)

curated.coalesce(1).write.mode("overwrite").parquet(str(out_dir2))

print("Wrote", out_dir)
print("Wrote", out_dir2)

spark.stop()
```

**Gotchas**
- `coalesce(1)` is NOT for big data; it creates one task and can bottleneck.

---

## Q9) What are the 3 performance levers I should mention at interview level?
**Answer**
1. **Shuffles** (joins/groupBy) are expensive.
2. **Partitioning** controls parallelism.
3. **Caching** avoids recomputation when the same DF is reused.

**Task**
- Inspect partitions.
- Use `explain()`.
- Cache and show repeated actions.

**Code**
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder.appName("q9_perf").master("local[*]").getOrCreate()

df = spark.read.csv("data/orders.csv", header=True, inferSchema=True)
print("Default partitions:", df.rdd.getNumPartitions())

# shuffle example
by_country = df.groupBy("country").count()
by_country.explain(True)

# cache example
filtered = df.filter(col("status") == "DELIVERED").cache()
print("First count:", filtered.count())
print("Second count:", filtered.count())

spark.stop()
```

---

## Optional: XML + JDBC
XML and JDBC are common in DE work, but they require extra setup.

- XML: use `spark-xml` (external package)
- JDBC: requires a running database

If you want, we can add dedicated Q&A sections once you’re comfortable with CSV/JSON/Parquet.
