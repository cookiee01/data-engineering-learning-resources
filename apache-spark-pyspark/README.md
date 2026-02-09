# PySpark Practice Track (Local macOS)

This folder contains a structured, modules-first PySpark journey:
- `modules/`: trainee-friendly notes + exercises
- `code/`: runnable scripts for each module
- `data/`: small local datasets for practice
- `output/`: generated outputs (safe to delete)

## Prerequisites (macOS)
- Python 3.9+
- Java (recommended: Temurin/OpenJDK 17). Verify: `java -version`

## Setup
```bash
cd /Users/arpitsingh/MyWorkingDir/PycharmProjects/data-engineering-learning-resources/apache-spark-pyspark
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
source .venv/bin/activate
python code/01_setup_and_mental_model.py
python code/02_read_csv.py
python code/03_read_json_nested.py
python code/04_read_parquet_partitioned.py
python code/05_core_transforms.py
python code/06_joins.py
python code/07_aggs_and_windows.py
python code/08_write_patterns_and_small_files.py
python code/09_perf_basics_explain_cache_partitions.py
```

## Notes
- XML support requires an extra Spark package. See `modules/02_reading_sources.md` and `code/02e_read_xml_spark_xml.py`.
- JDBC examples require a running database. See `code/02f_read_jdbc_postgres.py`.
