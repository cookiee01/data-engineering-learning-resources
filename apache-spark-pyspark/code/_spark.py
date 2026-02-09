from __future__ import annotations

from pyspark.sql import SparkSession


def spark(app_name: str) -> SparkSession:
    return (
        SparkSession.builder.appName(app_name)
        .master("local[*]")
        # keep logs quieter for learning
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
    )
