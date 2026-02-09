from pyspark.sql.functions import col

from _spark import spark


def main() -> None:
    s = spark("06_joins")

    orders = s.read.csv("data/orders.csv", header=True, inferSchema=True)
    users = s.read.json("data/users.json").select(
        col("user.id").alias("customer_id"),
        col("user.name").alias("name"),
        col("user.tier").alias("tier"),
    )

    joined = orders.join(users, on="customer_id", how="left")
    joined.show(truncate=False)

    s.stop()


if __name__ == "__main__":
    main()
