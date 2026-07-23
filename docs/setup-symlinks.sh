#!/usr/bin/env bash
set -euo pipefail

# Re-create MkDocs symlinks under docs/content/
# Run this from the repo root if symlinks are missing (e.g., on Windows).
# On macOS/Linux, symlinks are tracked in git and should already exist.

DIR="docs/content"
mkdir -p "$DIR"

ln -sf ../../AGENTS.md             "$DIR/AGENTS.md"
ln -sf ../../CHANGELOG.md          "$DIR/CHANGELOG.md"
ln -sf ../../CONTRIBUTING.md       "$DIR/CONTRIBUTING.md"
ln -sf ../../INDEX.md              "$DIR/INDEX.md"
ln -sf ../../README.md             "$DIR/README.md"

mkdir -p "$DIR/apache-flink"
ln -sf ../../../apache-flink/notes.md               "$DIR/apache-flink/notes.md"
ln -sf ../../../apache-flink/kafka-to-flink-local-setup.md "$DIR/apache-flink/kafka-to-flink-local-setup.md"
ln -sf ../../../apache-flink/practice-roadmap.md    "$DIR/apache-flink/practice-roadmap.md"

mkdir -p "$DIR/apache-iceberg"
ln -sf ../../../apache-iceberg/notes.md             "$DIR/apache-iceberg/notes.md"

mkdir -p "$DIR/apache-kafka"
ln -sf ../../../apache-kafka/notes.md               "$DIR/apache-kafka/notes.md"

mkdir -p "$DIR/apache-spark-pyspark"
ln -sf ../../../apache-spark-pyspark/notes.md                               "$DIR/apache-spark-pyspark/notes.md"
ln -sf ../../../apache-spark-pyspark/learning-path.md                       "$DIR/apache-spark-pyspark/learning-path.md"
ln -sf ../../../apache-spark-pyspark/PYSPARK_QA_JOURNEY.md                  "$DIR/apache-spark-pyspark/PYSPARK_QA_JOURNEY.md"
ln -sf ../../../apache-spark-pyspark/serialization.md                       "$DIR/apache-spark-pyspark/serialization.md"
ln -sf ../../../apache-spark-pyspark/spark-concepts-execution-architecture.md "$DIR/apache-spark-pyspark/spark-concepts-execution-architecture.md"

mkdir -p "$DIR/emr/hive-tez"
ln -sf ../../../emr/notes.md                        "$DIR/emr/notes.md"
ln -sf ../../../../emr/hive-tez/reducer-counts.md   "$DIR/emr/hive-tez/reducer-counts.md"

mkdir -p "$DIR/foundations"
ln -sf ../../../foundations/networking.md           "$DIR/foundations/networking.md"

mkdir -p "$DIR/interview-prep"
ln -sf ../../../interview-prep/roadmap.md            "$DIR/interview-prep/roadmap.md"
ln -sf ../../../interview-prep/2-month-sprint-plan.md "$DIR/interview-prep/2-month-sprint-plan.md"
ln -sf ../../../interview-prep/progress-checklist.md "$DIR/interview-prep/progress-checklist.md"
ln -sf ../../../interview-prep/foundations-progress.md "$DIR/interview-prep/foundations-progress.md"

mkdir -p "$DIR/system-design"
ln -sf ../../../system-design/notes.md              "$DIR/system-design/notes.md"
ln -sf ../../../system-design/caching.md            "$DIR/system-design/caching.md"

# quiz-app is a directory symlink (contains index.html + assets)
ln -sf ../../interview-prep/quiz-app                "$DIR/quiz-app"

echo "Symlinks created in $DIR"
