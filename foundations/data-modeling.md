# Data Modeling for Data Engineers

The foundation of every data platform. Covers dimensional modeling,
normalization, slowly changing dimensions, and modern alternatives.

---

## 1. Conceptual, Logical, Physical Models

| Level | Audience | What It Describes |
|---|---|---|
| **Conceptual** | Stakeholders | Business entities and relationships (no attributes, no keys) |
| **Logical** | Analysts, architects | Entities, attributes, relationships, keys, constraints (technology-agnostic) |
| **Physical** | Engineers | Tables, columns, types, indexes, partitions, distribution (technology-specific) |

---

## 2. Dimensional Modeling (Kimball)

The most widely adopted approach for data warehouses. Organizes data
into **facts** (measurements) and **dimensions** (context).

### Fact Tables

| Type | Description | Example | Grain |
|---|---|---|---|
| **Transactional** | One row per event | Sales transaction | Individual line item |
| **Periodic Snapshot** | One row per period | Monthly inventory snapshot | Month + product |
| **Accumulating Snapshot** | One row per process with milestones | Order fulfillment pipeline | Order lifecycle |

**Fact table design principles:**
- Grain must be declared before design (finest level of measurement)
- Facts should be additive (`amount`, `qty`) — semi-additive (`balance`) and non-additive (`ratio`) need special handling
- Foreign keys point to dimensions (snowflaking facts is rare)
- Date/time represented as **surrogate date keys** joining to a date dimension

### Dimension Tables

| Attribute | Wide, denormalized, text-heavy |
|---|---|
| **Conformed dimensions** | Shared across fact tables (e.g., `dim_date`, `dim_customer`) make the warehouse an enterprise asset |
| **Degenerate dimension** | A fact-table attribute that has no separate dimension (e.g., `order_number`) |
| **Junk dimension** | A single dimension combining low-cardinality flags/codes (e.g., `promo_flag`, `return_reason`) |
| **Role-playing dimension** | Same dimension used for different purposes (e.g., `order_date` vs `ship_date` both using `dim_date`) |

>

---

### Star Schema vs Snowflake

| Aspect | Star | Snowflake |
|---|---|---|
| Structure | Facts + flat dimensions | Facts + normalized dimensions |
| Join depth | 1 level | Multiple levels |
| Query performance | Faster (fewer joins) | Slower (more joins) |
| Storage | More (denormalized) | Less (normalized) |
| Maintenance | Redundancy across dims | Single source of truth per attribute |
| DE interview answer | **Default to star** — explain snowflake only if asked about storage optimization |

---

### Slowly Changing Dimensions (SCD)

SCDs track how dimension attributes change over time.

| Type | Behavior | Use Case |
|---|---|---|
| **Type 0** | Never change | Immutable audit fields |
| **Type 1** | Overwrite old value | Correcting data entry errors |
| **Type 2** | Add new row with version/date range | Tracking customer address history |
| **Type 3** | Add separate column for previous value | Limited history (e.g., "previous territory") |
| **Type 4** | Mini-dimension for rapidly changing attributes | Age/gender band separate from customer |
| **Type 6** | Hybrid of 1+2+3 | Current + history in same row |

**Type 2 implementation (the most common):**
```sql
CREATE TABLE dim_customer (
    customer_sk   INT PRIMARY KEY,       -- surrogate key
    customer_id   INT,                    -- natural/business key
    full_name     VARCHAR(100),
    city          VARCHAR(50),
    effective_dt  DATE NOT NULL,
    end_dt        DATE,                   -- NULL = current
    is_current    BOOLEAN DEFAULT TRUE
);
```
- `INSERT` a new row when an attribute changes
- Update `end_dt` and `is_current` on the previous row
- Queries filter by `effective_dt <= query_date AND (end_dt IS NULL OR end_dt > query_date)`

---

## 3. Normalization (Inmon / 3NF)

| Normal Form | Rule | Violation Example |
|---|---|---|
| **1NF** | One value per cell, no repeated columns | `phone_numbers: "555-0100,555-0200"` |
| **2NF** | 1NF + all non-key columns depend on the full primary key | Composite key where one column only depends on part of it |
| **3NF** | 2NF + no transitive dependencies | `employee → department_id → department_name` (move department_name to its own table) |

**When to normalize:** Operational databases (OLTP), data vault modeling, compliance-heavy domains.

**When to denormalize:** Analytics/OLAP, wide tables for BI tools, star schemas.

---

## 4. Data Vault Modeling (Dan Linstedt)

A hybrid between 3NF and dimensional modeling. Designed for
auditability, scalability, and handling source system changes.

| Component | Purpose | Example |
|---|---|---|
| **Hub** | Business keys (natural keys) | `hub_customer` with `customer_code` |
| **Satellite** | Descriptive attributes with timestamps | `sat_customer_details` with `name`, `address`, `load_dt`, `source` |
| **Link** | Relationships between hubs | `link_order_customer` connecting `hub_order` and `hub_customer` |

**Pros:** Fully auditable (every attribute change tracked), parallel
loading, resilient to source schema changes.
**Cons:** High join complexity, more tables, steeper learning curve.

---

## 5. Modern / Lakehouse Data Modeling

### Medallion Architecture (Databricks)

```
Bronze ──► Silver ──► Gold
 │            │            │
Raw ingest    Cleaned      Aggregated
(schema-on-   (deduped,    (business
read)         validated)   metrics)
```

### One Big Table (OBT)

A wide denormalized table containing all facts + dimensions for a
business process. Popular in modern data stacks (dbt, BigQuery).

**Pros:** Trivial BI queries (no joins), fast for dashboards.
**Cons:** Data redundancy, schema evolution is expensive, large
storage footprint.

> [!TIP]
> OBT is a delivery mechanism for BI, not a storage format. Build a
> Kimball star schema in your warehouse, then materialize OBT views
> for high-velocity dashboards.

---

## Quick Reference

| Concept | Default / Recommendation |
|---|---|
| Warehouse approach | **Kimball (dimensional)** — most widely used in DE interviews |
| Schema | **Star** — simpler, faster, interview default |
| Changing attributes | **SCD Type 2** — full history, standard answer |
| Modern landing zone | **Medallion** — Bronze/Silver/Gold |
| Keys | **Surrogate** in warehouse, **natural** in source systems |
| Date handling | **Date dimension** with date key, never raw timestamps in fact rows |

>

---

> [!NOTE]
> This covers what you need for DE interviews. For deeper reading:
> *The Data Warehouse Toolkit* by Ralph Kimball (the definitive guide
> on dimensional modeling).
