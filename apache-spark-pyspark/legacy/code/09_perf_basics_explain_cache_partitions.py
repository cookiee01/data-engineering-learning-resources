from pyspark.sql.functions import col

from _spark import spark


def main() -> None:
    s = spark("09_perf")
    df = s.read.csv("data/orders.csv", header=True, inferSchema=True)

    print("Default partitions:", df.rdd.getNumPartitions())

    # A shuffle operation (groupBy)
    gb = df.groupBy("country").count()
    gb.explain(True)

    # Cache if reused
    filtered = df.filter(col("status") == "DELIVERED").cache()
    print("First count (executes + caches):", filtered.count())
    print("Second count (should reuse cache):", filtered.count())

    # Repartition vs coalesce
    rp = df.repartition(4)
    print("Repartition(4):", rp.rdd.getNumPartitions())
    co = rp.coalesce(2)
    print("Coalesce(2):", co.rdd.getNumPartitions())

    s.stop()


if __name__ == "__main__":
    main()
