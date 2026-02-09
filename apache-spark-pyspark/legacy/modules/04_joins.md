# Module 4 — Joins

## Goal
- Understand join types.
- Avoid “duplicate explosion”.
- Know when broadcast joins help.

## The big gotcha: duplicates explosion
If your join key isn’t unique on one side:
- 1 row joining to N rows produces N outputs.
- If both sides have duplicates, it multiplies.

## Broadcast join intuition
If one side is small, Spark can broadcast it to all executors to avoid shuffle.

Run:
- `code/06_joins.py`
