# Module 6 — Writing Data (and Idempotency)

## Goal
- Write Parquet safely.
- Understand overwrite vs append.
- Avoid small file problems.

## Idempotent write patterns
- Prefer writing to a deterministic output path with `mode("overwrite")` for practice.
- For production: versioned paths or transactional table formats (Iceberg/Delta).

Run:
- `code/08_write_patterns_and_small_files.py`
