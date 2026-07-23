# Data Engineering Learning Resources

A curated, notes-first repository for learning and interview preparation.

## Day 1 Quick-Start (Practice, Don't Just Read)

### 1. Run real PySpark code against sample data

```bash
# Set up the environment (one-time)
cd apache-spark-pyspark
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run your first PySpark job
python code/00_getting_started.py
```

This script reads `data/orders.csv`, does aggregations, window functions, Spark SQL, and writes output to `output/`. Open `index.html` in the output folder to see the results.

### 2. Test yourself with the quiz app

```bash
# Browse all notes + use the interactive quiz
pip install mkdocs-material
mkdocs serve
# Open http://localhost:8000
```

The site includes flashcards and a multiple-choice quiz across 14 topics with XP tracking — all in your browser, no backend needed.

### 3. What to do next

| Day | Activity |
|-----|----------|
| **1** | Run the PySpark script above, explore the output, take a quiz round |
| **2** | Read `sql/notes.md`, then practice the 5 SQL exercises in the interview cheatsheet section |
| **3** | Read `apache-spark-pyspark/notes.md` (Spark internals), modify the PySpark script to use a different join type |
| **Week 1** | Follow the 8-week sprint plan in `interview-prep/2-month-sprint-plan.md` |

## Read All Notes

**Browse online** — `mkdocs serve` gives you search, dark mode, and diagrams:
```bash
pip install mkdocs-material
mkdocs serve
```

**Or read markdown files directly** — start at `INDEX.md` for the full table of contents.

## Repo Structure

| Topic | What's here |
|-------|-------------|
| **SQL** | `sql/notes.md` — window functions, joins, query optimization, anti-patterns |
| **PySpark / Databricks** | `apache-spark-pyspark/` — execution model, tuning, runnable code, sample data |
| **Kafka** | `apache-kafka/notes.md` — ISR, acks, exactly-once, compaction, ops |
| **Flink** | `apache-flink/notes.md` — state, watermarks, checkpoints, backpressure |
| **Iceberg** | `apache-iceberg/notes.md` — hidden partitioning, CoW vs MoR, time travel |
| **Data Modeling** | `data-modeling/notes.md` — star schema, SCD, grain, Kimball vs Data Vault |
| **dbt** | `dbt/notes.md` — models, incremental, tests, CI/CD, Jinja |
| **Snowflake** | `snowflake/notes.md` — architecture, micro-partitions, cost, streams/tasks |
| **AWS Data Engineering** | `aws-data-engineering/notes.md` — Glue, EMR, Redshift, Kinesis, IAM, cost |
| **Data Governance** | `data-governance/notes.md` — catalog, lineage, quality, contracts, observability |
| **Python** | `python/notes.md` — packaging, pyproject.toml, wheels, uv, Docker |
| **System Design** | `system-design/notes.md` — CDC pipelines, lakehouse, real-time metrics |
| **EMR** | `emr/notes.md` — Hadoop/Tez sizing, reducer tuning |
| **Foundations** | `foundations/networking.md` — distributed systems fundamentals |
| **Interview Prep** | `interview-prep/` — roadmap, 8-week sprint plan, quiz app, progress tracking |

## Changelog & Contributing
- See `CHANGELOG.md` for what changed recently
- See `CONTRIBUTING.md` for how to add notes and curation guidelines
