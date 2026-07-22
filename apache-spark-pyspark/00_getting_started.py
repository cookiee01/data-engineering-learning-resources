"""
PySpark Refresher - Run this file to warm up.
  cd apache-spark-pyspark
  source .venv/bin/activate
  python 00_getting_started.py
"""

import os, pathlib

# resolve data/ and output/ relative to this script's directory
BASE = pathlib.Path(__file__).resolve().parent
DATA = str(BASE / "data")
OUT  = str(BASE / "output")

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, DoubleType, TimestampType,
)

# ──────────────────────────────────────────────
# 1. CREATE A SPARK SESSION (entry point for everything)
# ──────────────────────────────────────────────
spark = (
    SparkSession.builder
    .master("local[*]")                    # use all local cores
    .appName("getting-started")
    .config("spark.ui.showConsoleProgress", "false")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")     # quieter logs

# ──────────────────────────────────────────────
# 2. READ A CSV FILE
# ──────────────────────────────────────────────
df = (
    spark.read
    .option("header", "true")             # first row is column names
    .option("inferSchema", "true")        # guess types (fine for practice)
    .csv(f"{DATA}/orders.csv")
)

print("=== SCHEMA ===")
df.printSchema()

print("=== FIRST 20 ROWS ===")
df.show()

print("=== BASIC INFO ===")
print(f"Row count : {df.count()}")
print(f"Columns   : {df.columns}")
print(f"Partition : {df.rdd.getNumPartitions()}")

# ──────────────────────────────────────────────
# 3. SELECT, FILTER, WITH COLUMN  (core DataFrame ops)
# ──────────────────────────────────────────────
print("=== SELECT a few columns ===")
df.select("order_id", "customer_id", "status").show()

print("=== FILTER cancelled orders ===")
df.filter(F.col("status") == "CANCELLED").show()

print("=== ADD a column: amount * 100 (cents) ===")
df.withColumn("amount_cents", F.col("amount") * 100).show()

print("=== CHAIN operations ===")
(
    df
    .filter(F.col("amount") > 50)
    .withColumn("tax", F.col("amount") * 0.18)
    .select("order_id", "status", "amount", "tax")
    .show()
)

# ──────────────────────────────────────────────
# 4. AGGREGATIONS
# ──────────────────────────────────────────────
print("=== COUNT per status ===")
df.groupBy("status").count().show()

print("=== SUM of amount per country ===")
df.groupBy("country").agg(
    F.sum("amount").alias("total_amount"),
    F.round(F.avg("amount"), 2).alias("avg_amount"),
    F.count("*").alias("num_orders"),
).show()

# ──────────────────────────────────────────────
# 5. NULL HANDLING
# ──────────────────────────────────────────────
print("=== NULL-safe operations ===")
(
    df
    .withColumn("amount_or_zero", F.coalesce(F.col("amount"), F.lit(0.0)))
    .select("order_id", "amount", "amount_or_zero")
    .show()
)

# ──────────────────────────────────────────────
# 6. READ JSON  (nested data)
# ──────────────────────────────────────────────
json_df = spark.read.json(f"{DATA}/users.json")

print("=== JSON SCHEMA (nested!) ===")
json_df.printSchema()

print("=== FLATTEN nested fields ===")
(
    json_df
    .select(
        F.col("user.id").alias("user_id"),
        F.col("user.name").alias("name"),
        F.col("user.tier").alias("tier"),
        F.col("geo.country").alias("country"),
        F.col("geo.city").alias("city"),
    )
    .show()
)

# ──────────────────────────────────────────────
# 7. EXPLODE (turn array/struct into rows)
# ──────────────────────────────────────────────
print("=== EXPLODE example ===")
exploded = (
    json_df
    .select(
        F.col("user.id").alias("user_id"),
        F.explode_outer(F.lit(["a", "b", "c"])).alias("tag"),
    )
)
exploded.show()

# ──────────────────────────────────────────────
# 8. WINDOW FUNCTIONS  (rank within groups)
# ──────────────────────────────────────────────
from pyspark.sql.window import Window

print("=== RANK orders by amount per country ===")
w = Window.partitionBy("country").orderBy(F.col("amount").desc())
(
    df
    .withColumn("rank", F.rank().over(w))
    .withColumn("dense_rank", F.dense_rank().over(w))
    .select("order_id", "country", "amount", "rank", "dense_rank")
    .show()
)

# ──────────────────────────────────────────────
# 9. SQL on DATAFRAMES  (create temp view then query)
# ──────────────────────────────────────────────
df.createOrReplaceTempView("orders")

print("=== SPARK SQL ===")
spark.sql("""
    SELECT country, status, COUNT(*) AS cnt
    FROM orders
    GROUP BY country, status
    ORDER BY country, cnt DESC
""").show()

# ──────────────────────────────────────────────
# 10. WRITE OUTPUT
# ──────────────────────────────────────────────
(
    df.groupBy("country", "status")
    .count()
    .coalesce(1)                           # single file for practice
    .write
    .mode("overwrite")
    .option("header", "true")
    .csv(f"{OUT}/country_status_counts")
)

print("=== Wrote output/country_status_counts/ ===")

# ──────────────────────────────────────────────
# CLEANUP
# ──────────────────────────────────────────────
spark.stop()
print("\nDone! Edit this file, re-run, and experiment.")
