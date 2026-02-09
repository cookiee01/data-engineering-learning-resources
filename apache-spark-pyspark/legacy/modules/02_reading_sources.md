# Module 2 — Reading Data (CSV, JSON, Parquet, XML, JDBC)

## Goal
- Read from common sources you’ll see in interviews and production.
- Know *what to specify* (schema, options) to avoid silent bugs.

## CSV
Common options:
- `header=True`
- `inferSchema=True` (ok for small dev work; avoid in prod)
- `mode=PERMISSIVE|DROPMALFORMED|FAILFAST`
- `columnNameOfCorruptRecord` to capture corrupt lines

Gotcha:
- CSV has no native types. Schema inference can mis-read dates/ints.

## JSON
Two formats you’ll see:
- **JSONL** (one JSON object per line) — easiest.
- **Multiline JSON** (a JSON array across many lines) — requires `multiLine=True`.

Gotcha:
- Nested structs/arrays are common; learn `col("a.b")` and `explode`.

## Parquet
Why it matters:
- Columnar + typed + supports predicate pushdown.

Gotcha:
- Writing too many small files hurts performance.
- Partitioned datasets require consistent partition columns.

## XML
Spark doesn’t support XML out of the box.
- Use `spark-xml` package.

How to run:
- Option A: set `spark.jars.packages` in SparkSession builder.
- Option B: run with `spark-submit --packages ...`.

Gotcha:
- XML is schema-poor; you’ll fight type conversions.

## JDBC
Used for reading from operational DBs.

Must-know options:
- `url`, `dbtable`, `user`, `password`, `driver`
- Partitioned reads: `partitionColumn`, `lowerBound`, `upperBound`, `numPartitions`

Gotcha:
- Without partitioned reads you get a single slow JDBC partition.

## Scripts to run
- `code/02_read_csv.py`
- `code/03_read_json_nested.py`
- `code/04_read_parquet_partitioned.py`
- `code/02e_read_xml_spark_xml.py`
- `code/02f_read_jdbc_postgres.py`
