# Flink Practice Roadmap

This roadmap is intentionally phased:
- Phase 0: baseline setup and confidence check
- Phase 1+: progressively deeper engineering scenarios

## Phase 0 (Current): Baseline Working Setup

Scope:
- Kafka source to Flink SQL
- print sink validation
- local Docker runtime

Reference:
- `kafka-to-flink-local-setup.md`

Exit criteria:
- You can start stack, submit query, produce events, and observe output.
- You can diagnose slot and parsing errors quickly.

## Phase 1: Flink SQL Data Quality and Transformations

Scenarios:
- malformed JSON handling (`json.ignore-parse-errors`, dead-letter pattern)
- schema evolution (new fields, missing fields)
- event-time conversion and watermark basics
- deduplication and late-event behavior checks

Deliverables:
- SQL scripts for each scenario
- expected outputs and failure checks

## Phase 2: PyFlink Jobs (Code-Driven)

Scenarios:
- build a PyFlink streaming job using Table API
- implement filtering, enrichment, aggregation windows
- configurable checkpoints and restart settings

Deliverables:
- versioned Python jobs in a dedicated folder
- reproducible run commands (`flink run` or SQL client integration)

## Phase 3: Kafka + Flink Operational Patterns

Scenarios:
- partitioning strategy and key selection
- consumer group behavior and offset resets
- backpressure and throughput tuning
- checkpoint tuning and failure recovery tests

Deliverables:
- load scripts
- operational checklist (what to inspect in Flink UI and Kafka)

## Phase 4: Airflow-Orchestrated Flink Workloads

Scenarios:
- submit Flink SQL and PyFlink jobs from Airflow DAGs
- monitor job state and retries in DAGs
- parameterize topics/windows via Airflow variables

Deliverables:
- Airflow DAG examples
- rollback/retry playbook

## Phase 5: More Realistic Pipeline

Scenarios:
- source: Kafka events
- processing: Flink enrichment + aggregations
- sink: table/storage layer (e.g., Iceberg/warehouse path)
- observability: lag, checkpoint health, failure alerts

Deliverables:
- end-to-end architecture doc
- reproducible test dataset and acceptance checks

