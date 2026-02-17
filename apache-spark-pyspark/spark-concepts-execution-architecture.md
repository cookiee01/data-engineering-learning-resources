# Spark Concepts and Execution Architecture

Video reference:
- [Apache Spark Concepts and Execution Architecture](https://www.youtube.com/watch?v=z4Owc8RRApg)

## Summary

This video covers practical Apache Spark concepts needed for writing, tuning, and troubleshooting Spark applications. It contrasts Spark with the MapReduce execution model and explains Spark execution in a cluster environment.

## Key Concepts Covered

### Limitations of MapReduce
- MapReduce often suffers from performance bottlenecks because intermediate data between map and reduce phases is persisted to disk multiple times.
- It has a rigid map -> reduce programming structure, which makes multi-step pipelines (filters, joins, aggregations, iterative workflows) harder to express and optimize.

### Spark Innovations Over MapReduce
- In-memory processing: Spark can keep intermediate working sets in memory (with spill when needed), reducing repeated disk I/O.
- DAG execution model: Spark builds a DAG from transformations and actions, then optimizes and executes it as jobs, stages, and tasks.
- Spark can be significantly faster for many workloads, but speedup depends on workload shape, data layout, cluster sizing, and shuffle behavior (not a guaranteed fixed multiplier).

## Spark Cluster Architecture and Job Execution

| Component | Description |
|---|---|
| Cluster | A group of machines providing aggregate compute and memory resources. |
| Cluster Manager | Resource allocator/scheduler (Standalone, YARN, Kubernetes, Mesos). |
| Driver | Process running application logic, DAG planning, task scheduling, and result coordination. |
| Worker Nodes | Machines that host executor processes/containers. |
| Executors | Per-application worker processes that execute tasks and store cached/shuffle data. |
| ApplicationMaster (YARN-specific) | YARN component for app lifecycle management; driver may run inside it in cluster mode. |

- User submits a Spark app (`spark-submit`).
- Cluster manager launches/allocates driver and executors based on deploy mode and manager type.
- Driver constructs logical/physical plans, splits work into stages/tasks, and schedules tasks to executors.
- Executors run tasks, perform shuffle reads/writes, cache data, and report status/results to driver.

### Deployment Modes
- Cluster mode: Driver runs inside the cluster.
- Client mode: Driver runs on the submit machine.
- Network stability between driver and executors is especially important in client mode.

## Spark Programming Model: Transformations and Actions

- Transformations: Lazy operations that build lineage/plans.
- Examples: `filter()`, `select()`, `withColumn()`, `join()`, `groupBy()`, `repartition()`
- Actions: Trigger execution and materialize results or side effects.
- Examples: `count()`, `collect()`, `show()`, `take()`, `foreach()`
- Writes such as `df.write...save(...)` also trigger execution, even though they use writer APIs.

Transformations can be thought of as:

| Type | Description | Shuffle Requirement |
|---|---|---|
| Narrow | Each output partition depends on a small/local subset of input partitions. Examples: `filter`, many projections, map-like operations. | Usually No |
| Wide | Output partitions depend on data across multiple input partitions. Examples: `groupBy`, `distinct`, `repartition`, many joins. | Usually Yes |

- Shuffle redistributes records across partitions (for example by key) so operations like grouped aggregations and many joins can proceed correctly.

## Job, Stage, and Task Breakdown

- A Job is created when an action is invoked.
- Jobs are divided into Stages primarily at shuffle/exchange boundaries in the physical plan.
- Each stage has multiple Tasks, typically one task per partition for that stage.
- Tasks execute in parallel across executors, constrained by available slots/cores/resources.

Important correction:
- "Number of stages = number of wide transformations + 1" is a useful intuition, but not a strict rule. Physical planning can create additional exchanges/stages, and one logical wide operation may map into multiple physical steps.

Illustrative flow (conceptual):

| Step | Type | Description | Stage tendency |
|---|---|---|---|
| Read file | Narrow-like source scan | Read data partitions | Early stage |
| Filter rows | Narrow | Filter within partitions | Same stage unless exchange needed |
| Repartition(3) | Wide | Shuffle to new partitioning | New stage boundary |
| Select columns | Narrow | Project required columns | Usually same stage as downstream narrow ops |
| Add computed column | Narrow | Expression evaluation per row | Same stage |
| GroupBy region + Sum | Wide aggregate pipeline | Partial aggregate -> shuffle -> final aggregate | Includes shuffle boundary and downstream stage |
| Add timestamp column | Narrow | Post-aggregation projection | Same stage as post-agg ops |
| Collect / Write | Action | Trigger and materialize output | Job completion trigger |

## Spark Executor Memory Architecture

| Memory Region | Purpose |
|---|---|
| On-heap memory | JVM-managed memory for execution/storage/user objects. |
| Execution memory | Shuffles, joins, sorts, aggregations. |
| Storage memory | Cached/persisted blocks, broadcast data references. |
| User memory | User data structures and metadata outside Spark-managed unified pool. |
| Reserved memory | Internal safety reserve (often discussed as ~300 MB baseline in many contexts). |
| Off-heap memory | Optional Spark-managed memory outside JVM heap (`spark.memory.offHeap.enabled`). |
| Overhead memory | Non-heap/container overhead (native libs, Python worker process memory, JVM overhead). |

- Unified memory model: Execution and storage share a common pool (`spark.memory.fraction`).
- Execution can evict storage blocks when necessary; storage does not evict execution demand.
- Off-heap can reduce GC pressure in some workloads, but benefits depend on workload and tuning.
- Spark-managed memory is managed by Spark runtime; manual cleanup concerns are mainly for custom native/user-managed resources.

## Optimization and Execution Planning

Spark SQL/DataFrame flow:
1. Parse into an unresolved logical plan.
2. Analyze/resolve against catalog and schemas.
3. Apply Catalyst rule-based optimizations (for example constant folding, predicate pushdown opportunities, projection pruning).
4. Generate physical plan alternatives for major operators.
5. Choose executable plan using strategy rules and available stats.
6. Execute, with runtime adaptation possible via AQE (Adaptive Query Execution).

Common optimizations:
- Predicate pushdown: apply filters at source when supported.
- Projection pruning: read only needed columns.
- Join strategy selection: broadcast hash join, sort-merge join, shuffle hash join, etc.
- AQE: can change join strategy and shuffle partitioning at runtime based on observed stats.

Important correction:
- Catalyst is heavily rule-driven; cost-based decisions exist but are not universal across all operators and situations. AQE further refines plans during execution.

## Key Takeaways

- Spark addresses MapReduce constraints with DAG-based execution and memory-aware processing.
- Understanding driver/executor/cluster-manager roles is essential for debugging and tuning.
- Transformations are lazy; actions trigger execution.
- Shuffle boundaries strongly influence stage creation and runtime cost.
- Job -> stage -> task is the core execution mental model, but stage count depends on physical plan boundaries, not only logical wide ops.
- Memory tuning requires understanding execution vs storage competition, overhead, and spill behavior.
- Catalyst + physical planning + AQE drive practical performance outcomes.

This foundation helps you write better Spark code, reason about performance regressions, and troubleshoot production failures faster.

## Not Specified / Uncertain

- Precise benchmark multipliers for Spark vs MapReduce on your workload.
- Exact memory fractions that are universally optimal in production.
- Full internals of all Catalyst rules and cost heuristics.
- Runtime differences across all cluster managers in every deployment topology.

