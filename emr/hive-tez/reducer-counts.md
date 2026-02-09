# Hive on Tez: Determining Reducer Counts (Tuning Notes)

Source article: https://community.cloudera.com/t5/Community-Articles/Hive-on-Tez-Performance-Tuning-Determining-Reducer-Counts/ta-p/245680

## Goal (in 2 minutes)
You should be able to:
- Explain what reducers do in Hive-on-Tez and why reducer count matters.
- Identify “too few reducers” symptoms.
- Know the main Hive/Tez knobs that influence reducer parallelism.
- Apply a safe tuning workflow (measure → adjust → validate).

---

## 1) First Principles: What a Reducer Stage Actually Is
A reducer stage is where data is **shuffled** (grouped/partitioned) and processed in parallel tasks.

Why reducers are expensive:
- They read shuffled data over the network.
- They may sort/merge.
- Skew causes stragglers (long tail).

Mental model:
- **Mappers**: “scan + pre-aggregate/filter”
- **Reducers**: “shuffle + group/sort + final aggregate/order”

---

## 2) The Problem This Article Targets
You run a Hive query on Tez and see:
- Lots of map tasks finish quickly
- Then the job crawls at the end

Typical root cause:
- **Too few reducers** → each reducer handles a huge partition → long tail.

Also possible:
- Skew (one key dominates)
- Too many reducers (task overhead dominates)
- Extra reducer stage(s) introduced by query shape

---

## 3) How Hive-on-Tez Chooses Reducer Parallelism (High Level)
Hive tries to auto-compute reducers based on an **estimate** of how much data will be processed in the reduce stage.

You can think of it like:
- “How many reducers do I need if I want ~X MB per reducer?”
- Then it applies caps/factors and Tez may further adjust at runtime.

Key takeaway:
- Reducer parallelism is **estimation-driven**.
- If Hive estimates the reduce-stage data is small (even when input data is huge), you might end up with **very few reducers**.

---

## 4) The Knobs You Must Know (Interview + Production)

### Hive reducer sizing knobs
- `hive.exec.reducers.bytes.per.reducer`
  - Target bytes per reducer.
  - Lower value → **more reducers**.
  - Higher value → **fewer reducers**.

- `hive.exec.reducers.max`
  - Upper bound on reducer count.

### Tez reducer auto-parallelism knobs
- `hive.tez.auto.reducer.parallelism`
  - Should typically be enabled for Tez.

- `hive.tez.min.partition.factor` / `hive.tez.max.partition.factor`
  - Factors used to scale reducer parallelism.
  - Increase max factor to allow more reducers when needed.

### “Don’t do this first” knob
- `mapreduce.job.reduces` / `mapred.reduce.tasks`
  - Forcing reducers can work, but it’s often brittle.
  - Prefer tuning the auto-parallelism knobs unless you have a strong reason.

---

## 5) A Safe Tuning Workflow (What I’d do on-call)

1. Validate the bottleneck
- Is the last stage reduce-heavy?
- Are reducers running near 100% CPU? Or blocked on shuffle/sort?
- Are there stragglers (one reducer far behind)?

2. Check if reducer count is obviously wrong
- Example smell: 1–2 reducers for a big aggregation over large input.

3. Adjust *one knob at a time*
- Start by lowering `hive.exec.reducers.bytes.per.reducer` (e.g., 256MB → 64MB or 32MB)
- Keep `hive.exec.reducers.max` reasonable (avoid thousands unless you have the cluster/resources)

4. Re-run and compare
- Total runtime
- Reduce stage runtime distribution
- Shuffle bytes / spills
- Cluster utilization

5. Stop when overhead starts to dominate
- “More reducers” is not always better.
- Too many reducers increases task startup + shuffle overhead.

---

## 6) Another Staff-Level Insight: Sometimes Reduce *Stages* Are the Problem
For queries with both `GROUP BY` and `ORDER BY`, Hive may introduce multiple reduce stages.

Sometimes the biggest win is:
- Reducing the number of reduce stages
- Avoiding unnecessary sorts
- Pushing aggregations earlier

If there is a `LIMIT`, the plan can often be optimized so you don’t fully sort/aggregate more than necessary.

---

## 7) Common Failure Modes & Fixes

### Symptom: still slow after adding reducers
Likely causes:
- Data skew (one key dominates)
- Spill to disk due to low memory
- Sorting dominates (ORDER BY)

Mitigations:
- Skew handling strategies (salting keys, map-side aggregation)
- Increase container memory / tune Tez memory settings
- Revisit query plan (can we avoid global sort?)

### Symptom: reducers increased but runtime got worse
Likely causes:
- Too many reducers (overhead)
- Too many small partitions

Mitigation:
- Increase `hive.exec.reducers.bytes.per.reducer` slightly
- Set reasonable `hive.exec.reducers.max`

---

## 8) Interview-Ready Answers

### “How do reducers get decided in Hive on Tez?”
Hive estimates reduce-stage bytes and uses `hive.exec.reducers.bytes.per.reducer` to pick a reducer count, bounded by max reducers and partition factors; Tez may further adapt at runtime.

### “What do you do when a Hive-on-Tez query is slow at the end?”
Check if the bottleneck is the reduce stage, validate reducer count and skew, then tune reducer sizing (`hive.exec.reducers.bytes.per.reducer`, max reducers, partition factors) and re-measure.

---

## 9) Mini Checklist (Don’t Forget)
- Too few reducers → long tail, low cluster utilization
- Tune *auto parallelism* knobs before forcing reducers
- Watch for skew and ORDER BY global sort costs
- Always measure: stage times + shuffle bytes + spills
