# Module 3 — Core DataFrame Operations

## Goal
Be fluent with the operations that cover ~80% of interview and job tasks:
- `select`, `withColumn`, `filter`, `when`, `cast`
- null handling
- dedup patterns

## Must-know patterns
- Column expressions are built with `pyspark.sql.functions` and `col()`.
- Prefer built-in functions over Python UDFs.

## Nulls
- `isNull`, `isNotNull`
- `coalesce` to pick first non-null
- `na.fill`, `na.drop`

## Dedup
- Simple: `dropDuplicates([keys])`
- Correct (keep latest): window + `row_number()`

Run:
- `code/05_core_transforms.py`
