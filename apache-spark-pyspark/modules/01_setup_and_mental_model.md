# Module 1 — Setup + Spark Mental Model

## Goal (in 5 minutes)
- Start a local SparkSession.
- Understand Spark’s mental model: transformations vs actions, lazy evaluation, DAG.
- Know where performance problems come from at a high level.

## First principles
Spark is a distributed compute engine.
- A **DataFrame** is a *logical plan* for how to compute a dataset.
- Transformations (e.g., `select`, `filter`, `join`) build a plan.
- Actions (e.g., `count`, `collect`, `write`) trigger execution.

## Key terms
- **Transformation**: builds the plan, lazy.
- **Action**: runs the plan, produces output.
- **Stage**: a set of tasks without shuffle boundaries.
- **Shuffle**: moving data across executors/partitions (expensive).

## Pitfalls
- Calling `collect()` on large data can OOM your driver.
- Repeated actions on the same DataFrame can recompute work unless cached.

## Exercises
1. Run `code/01_setup_and_mental_model.py`.
2. Identify which lines are transformations vs actions.
3. Run `df.explain(True)` and read:
   - Parsed/Analyzed/Optimized/Physical plans (don’t panic; look for joins/shuffles).
