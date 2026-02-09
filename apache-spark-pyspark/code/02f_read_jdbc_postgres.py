"""JDBC practice script.

Requires a running Postgres and the correct driver.

Example (Docker):
  docker run --rm -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=demo postgres:15

Then create a table and load a few rows.

For local learning, this file documents the key options:
- partitionColumn/lowerBound/upperBound/numPartitions
"""

from pyspark.sql import SparkSession


def main() -> None:
    s = (
        SparkSession.builder.appName("02f_read_jdbc")
        .master("local[*]")
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
    )

    url = "jdbc:postgresql://localhost:5432/demo"

    df = (
        s.read.format("jdbc")
        .option("url", url)
        .option("dbtable", "public.some_table")
        .option("user", "postgres")
        .option("password", "postgres")
        .option("driver", "org.postgresql.Driver")
        # partitioned read (example)
        # .option("partitionColumn", "id")
        # .option("lowerBound", 1)
        # .option("upperBound", 1000000)
        # .option("numPartitions", 8)
        .load()
    )

    df.show()
    s.stop()


if __name__ == "__main__":
    main()
