# Index

This is the navigation hub for the repo.

## Start Here (Suggested Order)
1. `foundations/networking.md`
2. `system-design/caching.md`
3. `apache-kafka/`
4. `apache-flink/`
5. `apache-spark-pyspark/`
6. `apache-iceberg/`
7. `sql/` — SQL deep-dive for data engineers
8. `data-modeling/` — star schema, Kimball, SCD
9. `dbt/` — modern data stack transformation
10. `snowflake/` — warehouse architecture and tuning
11. `data-governance/` — catalog, lineage, quality, contracts, observability
12. `aws-data-engineering/` — AWS services, patterns, cost
12. `python/` — packaging, deployment, versioning, tooling
8. AWS analytics stack: `emr/`

## General Resource Hubs
- [DataEngineering.wiki – Learning Resources](https://dataengineering.wiki/Learning+Resources)

## Topics
- SQL
  - `sql/notes.md` (query execution order, window functions, joins, CTEs, performance, anti-patterns, partitioning)
- Data Modeling
  - `data-modeling/notes.md` (star schema, fact types, dimension types, SCD 0–6, Kimball vs Inmon vs Data Vault, grain)
- dbt
  - `dbt/notes.md` (models, sources, tests, materializations, Jinja, incremental, CI/CD, Snowflake/Databricks patterns)
- Snowflake
  - `snowflake/notes.md` (architecture, virtual warehouses, micro-partitions, clustering, time travel, zero-copy clone, cost management, Snowpipe, streams/tasks)
- AWS Data Engineering
  - `aws-data-engineering/notes.md` (S3, Glue, EMR, Redshift, Lambda, Step Functions, Kinesis, IAM, cost optimization, architecture patterns)
- Data Governance & Quality
  - `data-governance/notes.md` (catalog, lineage, quality frameworks, data contracts, observability, SLOs, access control, PII)
- Python
  - `python/notes.md` (packaging, pyproject.toml, wheels, Poetry/uv, SemVer, deployment, code quality, enterprise tooling)
- Foundations
  - `foundations/networking.md`
  - `interview-prep/foundations-progress.md`
- System Design
  - `system-design/notes.md` (CDC pipeline, real-time metrics, lakehouse, incremental batch, decision framework)
  - `system-design/caching.md`
- Flink
  - `apache-flink/notes.md` (streaming-first model, state backends, checkpoints, watermarks, backpressure, exactly-once sinks, ops playbook)
  - `apache-flink/kafka-to-flink-local-setup.md`
  - `apache-flink/practice-roadmap.md`
- Kafka
  - `apache-kafka/notes.md` (log abstraction, ISR, acks, rebalancing, exactly-once, compaction, ops playbook)
- Iceberg
  - `apache-iceberg/notes.md` (architecture, hidden partitioning, CoW vs MoR, time travel)
- Spark / PySpark
  - `apache-spark-pyspark/notes.md` (Catalyst, Tungsten, AQE, shuffle, joins, skew, committers, Spark UI, streaming, cloud)
  - `apache-spark-pyspark/serialization.md` (Java vs Kryo, when it matters)
  - `apache-spark-pyspark/spark-concepts-execution-architecture.md` (DAG, stages, memory architecture)
  - `apache-spark-pyspark/PYSPARK_QA_JOURNEY.md` (22 Q&A with runnable code)
  - `apache-spark-pyspark/learning-path.md` (topic checklist)

## Interview Prep
- `interview-prep/roadmap.md` — full 2026 topic list: SQL, Spark, Kafka, Flink, Iceberg, cloud, DSA, system design
- `interview-prep/2-month-sprint-plan.md` — week-by-week 8-week study schedule with daily activities
- `interview-prep/progress-checklist.md` — granular subtopic checklist to track readiness per topic area

## Progress Tracking
- Foundations progress: `interview-prep/foundations-progress.md`
- Interview prep progress: `interview-prep/progress-checklist.md`

## Interactive Site
Run `mkdocs serve` (from repo root) for a browsable site with search, dark mode, and a built-in quiz app with flashcards and XP tracking (`interview-prep/quiz-app/index.html`).

If you add new notes/resources, please also:
- link them from this `INDEX.md` when it helps discoverability
- record the addition in `CHANGELOG.md`


