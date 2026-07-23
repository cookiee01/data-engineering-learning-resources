# Changelog

All notable changes to this learning repository are documented here.

The format is based on Keep a Changelog.

## [Unreleased]
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
