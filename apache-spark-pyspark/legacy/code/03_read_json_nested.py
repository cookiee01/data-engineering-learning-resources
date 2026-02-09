from pyspark.sql.functions import col

from _spark import spark


def main() -> None:
    s = spark("03_read_json")

    df = s.read.json("data/users.json")

    # Nested fields
    flat = df.select(
        col("user.id").alias("user_id"),
        col("user.name").alias("name"),
        col("user.tier").alias("tier"),
        col("geo.country").alias("country"),
        col("geo.city").alias("city"),
    )

    flat.show(truncate=False)

    # Multiline JSON array example
    events = s.read.option("multiLine", "true").json("data/events_multiline.json")
    events.printSchema()
    events.show(truncate=False)

    s.stop()


if __name__ == "__main__":
    main()
