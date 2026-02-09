import shutil
from pathlib import Path

from pyspark.sql.functions import col

from _spark import spark


def main() -> None:
    base = Path("output/parquet_partitioned")
    if base.exists():
        shutil.rmtree(base)

    s = spark("04_parquet")
    df = s.read.csv("data/orders.csv", header=True, inferSchema=True)

    (
        df.withColumn("country", col("country"))
        .write.mode("overwrite")
        .partitionBy("country")
        .parquet(str(base))
    )

    read_back = s.read.parquet(str(base))
    read_back.show(truncate=False)

    s.stop()


if __name__ == "__main__":
    main()
