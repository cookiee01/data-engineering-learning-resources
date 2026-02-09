from pyspark.sql.functions import col, when, coalesce, lit

from _spark import spark


def main() -> None:
    s = spark("05_transforms")
    df = s.read.csv("data/orders.csv", header=True, inferSchema=True)

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
    s.stop()


if __name__ == "__main__":
    main()
