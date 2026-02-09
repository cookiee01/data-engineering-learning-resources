"""XML reading requires spark-xml package.

This script configures Spark to download the package via Ivy.
If it fails (network/proxy), install/run using spark-submit --packages.

Package coordinates (Spark 3.5 / Scala 2.12):
  com.databricks:spark-xml_2.12:0.17.0
"""

from pyspark.sql import SparkSession


def main() -> None:
    s = (
        SparkSession.builder.appName("02e_read_xml")
        .master("local[*]")
        .config("spark.jars.packages", "com.databricks:spark-xml_2.12:0.17.0")
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
    )

    df = (
        s.read.format("xml")
        .option("rowTag", "item")
        .load("data/items.xml")
    )

    df.show(truncate=False)
    s.stop()


if __name__ == "__main__":
    main()
