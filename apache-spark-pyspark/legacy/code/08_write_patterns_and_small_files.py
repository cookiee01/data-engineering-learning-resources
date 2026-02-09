import shutil
from pathlib import Path

from pyspark.sql.functions import col

from _spark import spark


def main() -> None:
    s = spark("08_write")
    df = s.read.csv("data/orders.csv", header=True, inferSchema=True)

    out_dir = Path("output/orders_curated")
    if out_dir.exists():
        shutil.rmtree(out_dir)

    curated = df.filter(col("status") != "CANCELLED")

    # Practice: overwrite to be idempotent.
    curated.write.mode("overwrite").parquet(str(out_dir))

    # Small-file demo: coalesce to fewer files for tiny outputs.
    out_dir2 = Path("output/orders_curated_single_file")
    if out_dir2.exists():
        shutil.rmtree(out_dir2)
    curated.coalesce(1).write.mode("overwrite").parquet(str(out_dir2))

    print("Wrote:", out_dir)
    print("Wrote:", out_dir2)

    s.stop()


if __name__ == "__main__":
    main()
