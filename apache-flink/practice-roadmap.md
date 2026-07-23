# Flink Practice Roadmap

Phased progression from zero to production Flink. Each phase has
concrete exercises, not just topic lists.

---

## Setup

```bash
# Local dev environment
docker-compose -f kafka-to-flink-local-setup.yml up -d
# Or use Flink Kubernetes Operator on a local K8s cluster
```

---

## Phase 0: Baseline Working Setup

**Goal:** Submit your first Flink SQL job end-to-end.

### Exercises
1. Start Kafka + Flink stack locally (see `kafka-to-flink-local-setup.md`)
2. Create a Kafka topic `test_events` with 3 partitions
3. Start Flink SQL client and run:
   ```sql
   CREATE TABLE source (
     event_id STRING, user_id INT, event_ts TIMESTAMP(3)
   ) WITH (
     'connector' = 'kafka',
     'topic' = 'test_events',
     'properties.bootstrap.servers' = 'localhost:9092',
     'format' = 'json',
     'scan.startup.mode' = 'earliest-offset'
   );
   ```
4. Produce 5 JSON events using `kafka-console-producer`, verify with
   `SELECT * FROM source` in Flink SQL Client
5. File-sink to a local dir and verify output files

**Exit criteria:**
- Stack starts, query submits, events flow end-to-end
- You can diagnose slot and parsing errors

**References:** `kafka-to-flink-local-setup.md`, Flink SQL Client docs

---

## Phase 1: Flink SQL Core Patterns

**Goal:** Master the SQL patterns that cover 80% of DE use cases.

### Exercises
1. **Watermarks + tumble window:**
   ```sql
   CREATE TABLE pageviews (
     user_id INT, page STRING, view_ts TIMESTAMP(3),
     WATERMARK FOR view_ts AS view_ts - INTERVAL '5' SECOND
   ) WITH (...);
   ```
   Write a query counting pageviews per 1-minute tumbling window.

2. **Hop window (sliding):** Same source, count per 5-minute hop
   every 1 minute.

3. **Cumulative window:** Count per 30-minute cumulative window
   (Flink 1.15+).

4. **Session window:** Group events with a 10-minute gap timeout.

5. **Deduplication:**
   ```sql
   SELECT * FROM (
     SELECT *, ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY proc_time) AS rn
     FROM source
   ) WHERE rn = 1;
   ```

6. **Lookup join with a MySQL dimension table (Temporal Join):**
   ```sql
   CREATE TABLE customers (
     customer_id INT, tier STRING, created_ts TIMESTAMP(3)
   ) WITH (
     'connector' = 'jdbc',
     'url' = 'jdbc:mysql://localhost:3306/dimensions',
     'table-name' = 'customers'
   );
   SELECT o.*, c.tier
   FROM orders AS o
   LEFT JOIN customers FOR SYSTEM_TIME AS OF o.proc_time AS c
   ON o.customer_id = c.customer_id;
   ```

**Exit criteria:**
- All 6 queries run correctly
- You understand window type tradeoffs (tumble vs hop vs session)
- You can explain why `ROW_NUMBER` dedup is preferred

---

## Phase 2: PyFlink (DataStream API)

**Goal:** Programmatic Flink jobs beyond SQL.

### Exercises
1. **Basic DataStream pipeline:**
   ```python
   from pyflink.datastream import StreamExecutionEnvironment
   from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
   from pyflink.common import WatermarkStrategy, Duration

   env = StreamExecutionEnvironment.get_execution_environment()
   # ... build source, transformations, sink
   env.execute("my-job")
   ```

2. **Implement a ProcessFunction** for custom per-key state:
   - Track running count per user
   - Emit alert when count > threshold in a 10-minute window

3. **Side outputs:** Route valid events to main output, malformed
   events to dead-letter side output.

4. **RichMapFunction with state:**
   ```python
   class EnrichFunction(RichMapFunction):
       def open(self, runtime_context):
           self.state = runtime_context.get_state(
               ValueStateDescriptor("tier", Types.STRING())
           )
   ```

5. **Checkpoint config + restart strategy:**
   ```python
   env.enable_checkpointing(30_000)  # 30 seconds
   env.set_restart_strategy(
       RestartStrategies.fixed_delay_restart(3, 10_000)
   )
   ```

6. **Flink + Iceberg sink:**
   ```python
   from pyflink.datastream.connectors.file_system import FileSink
   from pyflink.common.types import RowTypeInfo, Types
   table_env.execute_sql("""
       CREATE CATALOG iceberg_cat WITH (
           'type'='iceberg', 'catalog-type'='hadoop',
           'warehouse'='s3://my-bucket/warehouse'
       )
   """)
   ```

**Exit criteria:**
- 6 PyFlink jobs running and tested
- You can explain checkpoint alignment and what happens during recovery

---

## Phase 3: Kafka Integration Patterns

**Goal:** Production Kafka + Flink patterns.

### Exercises
1. **Partition-aware processing:**
   - Produce events with customer_id as key
   - Consumer with `scan.startup.mode` = `group-offsets`
   - Verify partition assignment in Flink UI

2. **Schema Registry integration:**
   - Produce Avro/Protobuf events to Kafka with Schema Registry
   - Consume in Flink with `'format' = 'avro-confluent'`
   - Handle schema evolution (add field with default, verify compatibility)

3. **Idempotent sink to Kafka:**
   ```sql
   CREATE TABLE output (
     ... PRIMARY KEY (order_id) NOT ENFORCED
   ) WITH ('connector' = 'upsert-kafka', ...);
   ```

4. **Timezone-aware event-time handling:**
   - Source emits UTC timestamps
   - Flink processes in IST (UTC+5:30)
   - Output correctly anchored to local date boundaries

5. **Rescale / parallelism tuning:**
   - Start with 1 parallelism, scale to 4
   - Measure throughput change, observe watermark propagation

6. **Dead-letter queue pattern:**
   - Source with `json.ignore-parse-errors = true`
   - Side-output malformed rows to a separate Kafka DLQ topic

**Exit criteria:**
- You can handle Avro schema evolution without job restart
- Dead-letter queue catches and logs bad events without blocking the main pipeline

---

## Phase 4: Operational Patterns

**Goal:** Make Flink production-resilient.

### Exercises
1. **Checkpoint tuning:**
   - Set checkpoint interval to 10s, 30s, 60s — observe recovery time
   - Enable unaligned checkpoints, compare alignment delay
   - Set `minPauseBetweenCheckpoints` and measure throughput impact

2. **Backpressure simulation:**
   - Slow down a sink (e.g., `Thread.sleep(100)`)
   - Observe backpressure in Flink UI (backpressure tab)
   - Fix with buffer debloating (`taskmanager.network.memory.buffer-debloat.enabled`)

3. **Savepoint-based deployment:**
   - Run a job, take savepoint: `flink savepoint <job-id> /tmp/savepoints`
   - Modify the SQL (add a column), restart from savepoint
   - Verify state compatibility (should work with supported changes)

4. **Kubernetes deployment:**
   - Package job as a Docker image
   - Deploy using Flink Kubernetes Operator (`FlinkDeployment` CRD)
   ```yaml
   apiVersion: flink.apache.org/v1beta1
   kind: FlinkDeployment
   spec:
     image: my-registry/flink-job:latest
     flinkVersion: v2_0
     flinkConfiguration:
       taskmanager.numberOfTaskSlots: "4"
   ```
   - Test rolling upgrade with savepoint

5. **Airflow orchestration:**
   - DAG that submits a Flink job via SQL Gateway or REST API
   - DAG that monitors job health and alerts on failure
   - Parameterize topic names and window durations via Airflow variables

**Exit criteria:**
- Job survives worker pod restart (checkpoint recovery works)
- You can roll back a bad deployment using savepoints
- Airflow DAG manages full lifecycle: submit → monitor → alert

---

## Phase 5: End-to-End Streaming Pipeline

**Goal:** Build a production-grade streaming lakehouse pipeline.

### Architecture

```
Kafka (orders, events)
    │
    ▼
Flink SQL / PyFlink
    │
    ├──► Iceberg (silver layer — clean, enriched, deduplicated)
    │
    └──► Kafka (aggregations for real-time dashboards)
            │
            ▼
        ClickHouse / Druid (serving layer)
```

### Exercises
1. **Ingest** order events from Kafka into Iceberg (Parquet, Snappy)
   - Handle late arrivals (allow 1-minute lateness)
   - Deduplicate by `order_id`
   - Enrich with customer tier (Temporal Join to MySQL)

2. **Compute** real-time metrics:
   - 5-minute revenue per product category → Kafka output
   - Running 7-day average order value per customer → Iceberg gold
   - Top 10 products by revenue (sliding window) → Kafka

3. **Operationalize:**
   - Monitoring dashboard (Flink UI + Prometheus/Grafana)
   - Checkpoint health alerts (stuck checkpoints)
   - Lag monitoring (consumer lag per Kafka partition)
   - Schema change plan (add nullable column, verify backward compatibility)

### Deliverables
- End-to-end architecture diagram (Mermaid)
- All Flink SQL scripts and PyFlink jobs in `apache-flink/practice/`
- Runbook: start, stop, upgrade, rollback, scale
- Test dataset with expected outputs

---

## Phase 6: Flink 2.0 Features

**Goal:** Leverage Flink 2.0-specific capabilities.

1. **Materialized tables** — continuous SQL pipeline declared as a
   continuously updated table
2. **Adaptive batch scheduler** — run batch jobs that auto-scale based
   on data size
3. **Multi-version state access** — query state as it existed at a
   previous checkpoint

---

## Quick Reference

| Phase | Focus | Estimated Time |
|---|---|---|
| 0 | Setup + first SQL job | 1 session |
| 1 | Core SQL patterns (windows, dedup, joins) | 2-3 sessions |
| 2 | PyFlink DataStream API | 2-3 sessions |
| 3 | Kafka integration (schema registry, DLQ, partitions) | 2 sessions |
| 4 | Operations (checkpoints, K8s, Airflow, backpressure) | 3 sessions |
| 5 | End-to-end streaming lakehouse project | 4-5 sessions |
| 6 | Flink 2.0 features | 1 session |
