# Changelog

All notable changes to this learning repository are documented here.

The format is based on Keep a Changelog.

## [Unreleased]
### Added
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
