from pyspark.sql.functions import col

from _spark import spark


def main() -> None:
    s = spark("01_setup")

    df = s.read.csv("data/orders.csv", header=True, inferSchema=True)

    # Transformations (lazy)
    delivered = df.filter(col("status") == "DELIVERED").select("order_id", "customer_id", "amount")

    print("=== Schema ===")
    delivered.printSchema()

    print("=== Plan (look for Filter/Project) ===")
    delivered.explain(True)

    # Action (executes)
    print("=== Count (action) ===")
    print(delivered.count())

    s.stop()


if __name__ == "__main__":
    main()
