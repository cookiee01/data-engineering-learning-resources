# Changelog

All notable changes to this learning repository are documented here.

The format is based on Keep a Changelog.

## [Unreleased]
### Added
- Added `sql/notes.md` — SQL deep-dive for data engineering (query execution order, window functions with frame specs, JOIN strategies and algorithms, CTEs and recursive CTEs, aggregation nuances, execution plan reading, anti-patterns, partitioning/clustering, interview cheatsheet)
- Added `data-modeling/notes.md` — data modeling for senior/staff DE (star schema, snowflake schema, three fact types, dimension tables including conformed/degenerate/junk, SCD Type 0-6 with decision matrix, Kimball vs Inmon vs Data Vault, grain declaration, fan traps)
- Added `dbt/notes.md` — dbt fundamentals (models/sources/tests, materializations, Jinja macros, incremental models with lookback window, CI/CD patterns, Snowflake/Databricks-specific configs, selection syntax)
- Added `snowflake/notes.md` — Snowflake for data engineering (storage-compute separation, virtual warehouse sizing and multi-cluster, micro-partitions and clustering keys, time travel and fail-safe, zero-copy cloning, query profiles, cost management with resource monitors, Snowpipe, streams and tasks)
- Added `aws-data-engineering/notes.md` — AWS data services (S3 storage classes and lifecycle policies, Glue ETL and Data Catalog, EMR with instance fleets and spot pricing, Redshift diststyle and sort keys, Lambda/Step Functions for serverless orchestration, Kinesis vs MSK, IAM patterns, cost optimization strategies, architecture patterns)
- Added `python/notes.md` — enterprise Python knowledge in dialogue format: pyproject.toml (PEP 621), sdist vs wheel, pip/uv/Poetry comparison, dependency pinning and lock files, SemVer and PEP 440, Docker multi-stage builds for Python, code quality stack (Ruff, Mypy, Pytest, Pre-commit), runtime management (pyenv, uv python), enterprise private PyPI proxies (Artifactory, CodeArtifact, devpi), security scanning, quick-reference cheatsheet with 3 Mermaid diagrams
- Added Mermaid architecture diagrams to three core notes files: Kafka (broker/partition layout, producer write path sequence), Flink (JobManager/TaskManager architecture, aligned checkpoint flow, watermark mechanism), System Design (CDC pipeline, real-time metrics pipeline, medallion architecture, incremental batch pipeline) — replaces ASCII diagrams with rendered Mermaid flowcharts and sequence diagrams
- Added GitHub-flavored admonition callouts: `> [!WARNING]` (Kafka acks+min.insync.replicas trap), `> [!TIP]` (Flink idle partition watermark fix), `> [!NOTE]` (lakehouse storage-layer convergence insight) for visual emphasis
- Enabled Mermaid rendering in MkDocs via `pymdownx.superfences` custom fence config
- Documented visual content guidelines in `AGENTS.md` (Mermaid syntax, diagram formatting rules, admonition usage)
- Rewrote `apache-kafka/notes.md` from link stub into full interview-prep notes — log abstraction, KRaft architecture, ISR/high watermark, producer acks and idempotence, consumer groups and rebalancing, delivery semantics and exactly-once, retention and compaction, storage internals, operational playbook, quick-reference cheatsheet (Senior DE ↔ Staff DE dialogue format)
- Rewrote `apache-flink/notes.md` from 43-word pointer into full interview-prep notes — streaming-first vs Spark, architecture (JobManager/TaskManager/slots), state backends (heap vs RocksDB), checkpoints and savepoints (aligned/unaligned/incremental), watermarks and event time (idle partitions, late events), windowing (tumbling/sliding/session, state amplification), backpressure (credit-based flow control), exactly-once sinks (2PC, S3 limitations), restart strategies, operational playbook (Senior DE ↔ Staff DE dialogue format, aligned with practice-roadmap phases)
- Rewrote `system-design/notes.md` from link stub into full DE system design interview-prep notes — four scenarios (CDC pipeline with Debezium+Kafka+Iceberg, real-time metrics with Flink+Druid, data lakehouse with medallion architecture, incremental batch with Iceberg MERGE INTO), each with architecture diagrams, trade-off tables, failure recovery walkthroughs, and a decision framework (Senior DE ↔ Staff DE dialogue format)
- Expanded quiz app from 25 to 69 questions: added 16 Kafka questions (ISR, idempotence, rebalancing, compaction, partitioning, static membership, KRaft, watermark, backpressure), 18 Flink questions (state backends, checkpoints, watermarks, windowing, exactly-once sinks, backpressure, ops), 6 system-design questions (CDC, schema registry, medallion architecture, Druid vs ClickHouse, streaming vs batch, Iceberg sink), and 4 Iceberg questions (metadata tree, schema evolution, concurrent commits, partition evolution)

### Changed
- Updated cross-references to sibling repo: renamed from `data-engineering-staff-learning-plan` → `data-engineering-learning-lab` in Flink setup guide and notes
- Sibling repo (`data-engineering-learning-lab`): complete cleanup for public sharing — git history rewritten, personal info removed, "staff" language replaced, .env extraction, language fixes

### Changed
- Cleaned up repo structure: removed 5 empty directories (`athena/`, `aws-glue/`, `python/`, `data-structures-and-algorithms/`, `redshift/`)
- Standardized topic entry points: renamed `apache-flink/README.md` → `apache-flink/notes.md`
- Moved `foundations/progress.md` → `interview-prep/foundations-progress.md`
- Consolidated PySpark scripts under `apache-spark-pyspark/code/`
- Moved `mkdocs.yml` from `docs/` to repo root; run `mkdocs serve` (no flag needed)
- Created `docs/setup-symlinks.sh` for rebuilding MkDocs symlinks on Windows
- Tracked `docs/content/` symlinks in git so MkDocs works out of the box on macOS/Linux
- Updated `README.md` with Getting Started section, prerequisites, and clone instructions
- Fixed stale AWS references and orphaned bullet in `INDEX.md`
- Removed empty/placeholder references from `README.md` and `INDEX.md`

### Added
- Added `interview-prep/2-month-sprint-plan.md` — 8-week daily study schedule covering SQL → Spark → Python/DSA → Kafka/Flink → System Design → Cloud → Behavioral → Mocks
- Added `interview-prep/progress-checklist.md` — granular subtopic checklist (100+ items) organized by category to track interview readiness
- Added `interview-prep/quiz-app/index.html` — standalone interactive web app with flashcards, multiple-choice quiz, XP tracking, and progress dashboard (data sourced from the repo's topics)
- Added MkDocs site config (`docs/mkdocs.yml`) with Material theme — browse all notes with search, dark mode, navigation, and code copy. Run with `mkdocs serve -f docs/mkdocs.yml`
- Rewrote `apache-spark-pyspark/notes.md` — comprehensive deep dive: Catalyst, Tungsten, memory architecture, AQE, shuffle internals, join strategies, skew handling, output committers, Spark UI, performance debugging, streaming, cloud-specific considerations, Spark 4 changes, and 15 curated resources

### Changed
- Updated `INDEX.md` to link interview-prep files, quiz app, and updated PySpark notes
- Updated `apache-spark-pyspark/learning-path.md` to reference new notes.md as primary source
- Updated `README.md` with MkDocs usage instructions
- Updated `.gitignore` to exclude `site/` directory
- Added Apache Iceberg interview prep notes in `apache-iceberg/notes.md` — covers Iceberg vs Hive format, 4-tier metadata architecture (Catalog → Metadata JSON → Manifest List → Manifest Files → Data Files), hidden partitioning with all transforms (days/hours/months/years/bucket/truncate/identity), partition evolution, write + read path internals, Copy-on-Write vs Merge-on-Read strategies, delete file types (Position vs Equality), time travel queries, and snapshot/orphan file cleanup
- Added Spark/PySpark revision channel in `apache-spark-pyspark/notes.md` (Afaque Ahmad YouTube)
- Added Kafka resources in `apache-kafka/notes.md` (YouTube crash course and Hello Interview deep dive)
- Added Flink setup notes: local Kafka -> Flink runbook in `apache-flink/kafka-to-flink-local-setup.md` (Docker-based initial setup, SQL, produce/verify, troubleshooting)
- Added phased Flink progression plan in `apache-flink/practice-roadmap.md` (from setup to PyFlink, operations, and Airflow orchestration)
- Added `apache-flink/README.md` as the entry point for setup vs deep-practice tracks
- Added PySpark practice track in `apache-spark-pyspark/PYSPARK_QA_JOURNEY.md` (Q&A format with tasks + code), covering file reads (CSV/JSON/XML), schema drift, timestamps/timezones, conditional aggregations, pivot, JSON parsing + explode, window functions (rank/dense_rank/row_number), sessionization, join performance (broadcast + skew handling), partition pruning, and JDBC reads
- Added practice datasets under `apache-spark-pyspark/data/` (includes `orders_extended.csv` for window/ranking examples)
- Added Spark serialization notes (JavaSerializer vs KryoSerializer) under PySpark, with links to Spark SQL internals (UnsafeRow / ExpressionEncoder)
- Added Hive-on-Tez reducer count tuning notes under EMR
- Added EMR/Hadoop notes link: Hadoop splits vs blocks article (Jerome Rajan)

### Changed
- Cleaned up PySpark Q&A journey (removed future-work section; fixed code snippet formatting)

### Removed
- Removed older PySpark module layout to keep only the current practice track

---

## [2026-02-09]
### Added
- Added `INDEX.md` as a repo navigation hub (includes DataEngineering.wiki learning resources link)
- Added `CONTRIBUTING.md` with note-writing guidelines

### Changed
- Improved `README.md` to help new contributors navigate the repo
- Expanded `.gitignore` to cover common OS/Python files

---

## [2026-02-07]
### Added
- Repository initialized with topic folders and `README.md`
- Added PySpark notes with cheat sheet link
- Added foundations folder and networking notes
- Added foundations progress log with networking playlist progress
- Added system design resources notes (including karanpratapsingh/system-design)
- Added AWS-focused caching system design note
