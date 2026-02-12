# Kafka to Flink Local Setup (Initial)

This is the baseline local setup to confirm end-to-end streaming:
- Kafka topic source
- Flink SQL job
- print sink verification

## Source Infra

Use this compose as the runnable lab:
- `/Users/arpitsingh/MyWorkingDir/PycharmProjects/data-engineering-staff-learning-plan/docker-compose.yml`

Do not duplicate compose files across repos. Keep one infra source and document usage here.

## Services and Ports

- Kafka broker: `localhost:9092` (from host), `kafka:29092` (inside Docker network)
- Flink UI: `http://localhost:8087`
- Kafka UI: `http://localhost:8086`

## Start Services

```bash
cd /Users/arpitsingh/MyWorkingDir/PycharmProjects/data-engineering-staff-learning-plan
./apache-flink/download-connectors.sh
docker compose up -d zookeeper kafka schema-registry flink-jobmanager flink-taskmanager kafka-ui
```

## Create Topic

```bash
docker exec -it de-kafka kafka-topics --bootstrap-server localhost:9092 --create --topic flink-events --partitions 1 --replication-factor 1
docker exec -it de-kafka kafka-topics --bootstrap-server localhost:9092 --list
```

## Flink SQL Job

Open SQL client:

```bash
docker exec -it de-flink-jobmanager /opt/flink/bin/sql-client.sh
```

Run:

```sql
CREATE TABLE kafka_events (
  user_id INT,
  event STRING,
  ts STRING
) WITH (
  'connector' = 'kafka',
  'topic' = 'flink-events',
  'properties.bootstrap.servers' = 'kafka:29092',
  'properties.group.id' = 'flink-dev',
  'scan.startup.mode' = 'earliest-offset',
  'format' = 'json',
  'json.ignore-parse-errors' = 'true'
);

CREATE TABLE out_sink (
  user_id INT,
  event STRING,
  ts STRING
) WITH ('connector' = 'print');

SET 'parallelism.default' = '1';
INSERT INTO out_sink
SELECT * FROM kafka_events;
```

## Produce Messages

In another terminal:

```bash
docker exec -it de-kafka kafka-console-producer --bootstrap-server localhost:9092 --topic flink-events
```

Send JSON lines:

```json
{"user_id":1,"event":"view","ts":"2026-02-12T18:10:00Z"}
{"user_id":1,"event":"click","ts":"2026-02-12T18:10:05Z"}
{"user_id":2,"event":"purchase","ts":"2026-02-12T18:10:10Z"}
```

## Verify Output

`print` sink output appears in TaskManager logs:

```bash
docker logs -f de-flink-taskmanager
```

Expected pattern:

```text
+I[1, view, 2026-02-12T18:10:00Z]
```

## Common Issues

1. Parse error at `out`
- Cause: `out` can conflict with SQL parser keywords.
- Fix: use `out_sink` or quote as `` `out` ``.

2. `NoResourceAvailableException`
- Cause: all slots already in use by another running job.
- Check:
```bash
curl -s http://localhost:8087/overview
docker exec -it de-flink-jobmanager /opt/flink/bin/flink list
```
- Fix: cancel old job and re-run:
```bash
docker exec -it de-flink-jobmanager /opt/flink/bin/flink cancel <job-id>
```

3. No output visible in SQL prompt
- `print` sink writes to TaskManager logs, not always to SQL shell.
- Use `docker logs -f de-flink-taskmanager`.

4. Wrong bootstrap server
- Inside Docker: use `kafka:29092`.
- From host: use `localhost:9092`.

