from pyspark.sql import Window
from pyspark.sql.functions import col, sum as _sum, count as _count, row_number

from _spark import spark


def main() -> None:
    s = spark("07_aggs_windows")
    orders = s.read.csv("data/orders.csv", header=True, inferSchema=True)

    agg = orders.groupBy("customer_id").agg(
        _count("order_id").alias("orders"),
        _sum("amount").alias("total_amount"),
    )
    agg.show(truncate=False)

    # "keep latest" example with window
    w = Window.partitionBy("customer_id").orderBy(col("order_ts").desc())
    latest = orders.withColumn("rn", row_number().over(w)).filter(col("rn") == 1).drop("rn")
    latest.show(truncate=False)

    s.stop()


if __name__ == "__main__":
    main()
