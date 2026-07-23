# OLAP vs OLTP

The most common opening question in DE interviews. Defines the
fundamental divide in data systems.

---

## The Spectrum

```
OLTP (Transactional) ←──────────────────────→ OLAP (Analytical)
     │                                                  │
Operational systems                              Analytics / BI
Row-oriented storage                            Columnar storage
High concurrency, low latency                   Large scans, aggregations
Millions of small writes                        Periodic bulk loads
Normalized schema                               Denormalized star/snowflake
ACID compliance                                 Read-optimized, eventual
```

---

## Side-by-Side

| Dimension | OLTP | OLAP |
|---|---|---|
| **Primary purpose** | Run business operations | Analyze business performance |
| **Users** | Cashiers, clerks, customers | Analysts, data scientists, executives |
| **Query type** | Simple CRUD: `SELECT ... WHERE id=X` | Complex aggregations: `SELECT SUM(...) GROUP BY ...` |
| **Rows per query** | Tens | Millions to billions |
| **Concurrency** | Thousands of concurrent users | Tens of concurrent queries |
| **Latency requirement** | Milliseconds | Seconds to minutes (acceptable) |
| **Write pattern** | Frequent, small inserts/updates | Periodic bulk loads (batch or micro-batch) |
| **Storage** | Row-oriented (fast single-row access) | Columnar (fast column scans) |
| **Schema** | Normalized 3NF (reduce redundancy) | Denormalized star/snowflake (reduce joins) |
| **ACID** | Required (money, inventory) | Not critical (read-isolated is enough) |
| **Example systems** | PostgreSQL, MySQL, Oracle, SQL Server | Snowflake, Redshift, BigQuery, ClickHouse |
| **Index strategy** | B-tree, hash indexes | Zone maps, min/max, bloom filters |

---

## Why OLAP Uses Columnar Storage

```
ROW-ORIENTED (OLTP):
Row 1: [101, Asha, IN, 120.50, DELIVERED, keyboard]
Row 2: [102, Ravi, IN, 15.00, CANCELLED, mouse]
Row 3: [103, Maya, US, 200.00, SHIPPED, monitor]
                    │
To compute AVG(amount), the engine must read
ALL columns of ALL rows — wasteful.

COLUMN-ORIENTED (OLAP):
Column 1: [101, 102, 103, ...]     │  order_id
Column 2: [Asha, Ravi, Maya, ...]  │  name
Column 3: [IN, IN, US, ...]        │  country
Column 4: [120.50, 15.00, 200.00]  │  amount  ◄─── Engine reads only this column
Column 5: [DELIVERED, CANCELLED, ...]│ status
Column 6: [keyboard, mouse, ...]   │  product
```

Columnar storage reads **only the columns needed** for a query.
For `AVG(amount)`:
- OLTP storage: reads all columns of all rows → I/O per byte is high
- OLAP storage: reads only the `amount` column → I/O per byte is low

Columnar also compresses better (similar values adjacent → better
dictionary/RLE encoding).

---

## Common DE Interview Questions

**Q: Can you run analytics on an OLTP database?**
Yes, for small scale. For large scale: analytics queries will compete
with transactional workloads (lock contention, IO bandwidth), and
columnar scans will be slow on row storage. Solution: replicate to a
read replica or an OLAP system.

**Q: What's the hybrid approach?**
HTAP (Hybrid Transactional/Analytical Processing) — systems that handle
both workloads:
- **SingleStore (MemSQL)** — rowstore + columnstore in the same DB
- **ClickHouse** — optimized for OLAP but supports point lookups
- **PostgreSQL + Citus** — row-oriented with parallel query
- **MySQL HeatWave** — separate analytical engine on the same data

**Q: When would you use a columnar format on an OLTP system?**
Rarely. Row-oriented is better for point lookups, frequent updates, and
range scans on primary key. Columnar excels when scanning large subsets
of rows but few columns.

**Q: Can OLAP replace OLTP?**
No. They serve different purposes. OLAP systems sacrifice write
performance and transactional guarantees for read/scan performance.
Most architectures: OLTP → CDC/ETL → OLAP.

---

## Architecture Pattern

```
┌──────────┐     CDC / Batch      ┌──────────┐
│  OLTP     │ ──────────────────► │  OLAP     │
│ (App DB)  │                     │ (Warehouse)│
└──────────┘                     └──────────┘
    │                                  │
    │                                  │
    ▼                                  ▼
Point lookups                    Complex aggregations
Row inserts                       Large scans
ACID transactions                 Dashboards / Reports
```

---

## Quick Reference

| Question | Answer |
|---|---|
| Default for OLTP? | Row-oriented, 3NF, ACID |
| Default for OLAP? | Columnar, star schema, read-optimized |
| Replace one with the other? | No — they serve different purposes |
| Interview answer | Start with the purpose (analyze vs transact), then explain the design differences |
| Modern compromise? | HTAP — but still rare in practice |
