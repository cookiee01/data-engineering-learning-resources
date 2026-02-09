from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType

from _spark import spark


def main() -> None:
    s = spark("02_read_csv")

    schema = StructType(
        [
            StructField("order_id", IntegerType(), True),
            StructField("customer_id", IntegerType(), True),
            StructField("order_ts", StringType(), True),
            StructField("status", StringType(), True),
            StructField("amount", DoubleType(), True),
            StructField("country", StringType(), True),
        ]
    )

    df = (
        s.read.format("csv")
        .option("header", "true")
        .option("mode", "PERMISSIVE")
        .schema(schema)
        .load("data/orders.csv")
    )

    df.show(truncate=False)
    s.stop()


if __name__ == "__main__":
    main()
