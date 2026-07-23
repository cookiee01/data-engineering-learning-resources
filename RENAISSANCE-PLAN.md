# Renaissance Plan — File-by-File Rewrite

Every foundations and topic file gets converted to the interview-centric
deep-dive format proven in `foundations/file-formats.md`:
- True internals (ASCII/Mermaid diagrams of physical structures)
- Worked examples with byte counts, row counts, actual numbers
- Real interview questions (from FAANG/GCC candidate reports)
- Decision trees (Mermaid, whiteboard-ready)
- Quick reference interview edition at the end

---

## Template

Every file follows this structure:

```markdown
# Topic — Interview Deep Dive

## 1. Big Picture / Opening Question
  - Most common interview framing question
  - Mermaid diagram or decision tree
  - Answer structure

## 2. Core Concepts (with diagrams)
  - Physical layout diagrams (Mermaid)
  - Worked examples with numbers
  - Comparison tables

## 3-N. Topic-specific sections
  - Each section framed around an interview question
  - Mermaid flow/sequence/architecture diagrams
  - Concrete examples with calculations

## N+1. Real Interview Questions
  - 5-7 questions from actual interviews
  - Full diagnosis + fix walkthrough
  - Mermaid diagrams for each

## N+2. Decision Trees (Whiteboard-ready)
  - Mermaid flowcharts

## N+3. Quick Reference — Interview Edition
  - Table: Question → Short Answer
```

---

## File Assessment & Order

### Phase 1: Foundations (high impact, fast wins)

| # | File | Lines | Problem | Solution |
|---|------|-------|---------|----------|
| 1 | `foundations/olap-vs-oltp.md` | 125 | Thin, ASCII diagrams, shallow Q&A | Full interview rewrite: columnar internals, Mermaid architecture, 5 real Qs |
| 2 | `foundations/data-modeling.md` | 171 | Good content, no interview Q&A, no Mermaid, no real questions | Add: SCD walkthrough with type-2 implementation, star vs snowflake decision tree, normal forms with examples, medallion diagram, 5-7 real Qs |
| 3 | `foundations/distributed-systems.md` | 180 | CAP is ASCII, thin on DE-specific scenarios | Add: Mermaid CAP diagram, Raft leader election sequence, quorum math, consistency in practice table, 5-7 real Qs |
| 4 | `foundations/containerization.md` | 215 | Docker + K8s covered but ASCII diagrams, needs more interview depth | Add: Multi-stage build walkthrough, K8s scheduling flow, pod lifecycle with failure scenarios, 5-7 real Qs |
| 5 | `foundations/serialization.md` | 231 | Created recently — verify depth | Review against file-formats.md standard; add interview Q&A if missing |

### Phase 2: Topic Files (higher effort, higher value)

| # | File | Lines | Problem | Solution |
|---|------|-------|---------|----------|
| 6 | `apache-kafka/notes.md` | 437 | Reference notes, not interview-focused | Convert to interview format: ISR diagram, rebalancing sequence, partition assignment decision tree, tiered storage workflow, 7-10 real Qs |
| 7 | `apache-flink/notes.md` | 502 | Reference notes, not interview-focused | Convert: watermark propagation diagram, checkpoint alignment sequence, state backend decision tree, Flink 2.0 materialized tables, 7-10 real Qs |
| 8 | `apache-iceberg/notes.md` | 488 | Reference notes, not interview-focused | Convert: Catalog→Metadata→Manifest→Data flow diagram, snapshot isolation sequence, CoW vs MoR decision tree, compaction strategy, 7-10 real Qs |
| 9 | `system-design/notes.md` | 569 | Broad reference, needs interview framing | Restructure as 6 design scenarios with Mermaid architecture diagrams, 2 evaluation criteria, drill questions |

### Phase 3: Spark & EMR (largest files, maintain as reference + add interview sections)

| # | File | Lines | Problem | Solution |
|---|------|-------|---------|----------|
| 10 | `apache-spark-pyspark/notes.md` | 941 | Already comprehensive reference | Add interview-centric sections at the end of each major topic: Catalyst phases with diagram, shuffle internals with diagram, AQE decision tree, Spark 4.x changes, RAPIDS GPU flow |
| 11 | `emr/notes.md` | 1347 | Very long reference doc | Keep as-is; add interview quick reference section at the end |

---

## Accuracy Verification Checklist (every file)

Before committing, verify:

- [ ] **All hex byte sequences**: Manually verify value decoding matches claim
- [ ] **All config names**: Check against actual Spark/Kafka/Flink docs — no invented configs
- [ ] **All percentages/speedups**: Add caveats like "varies with data" or "approximately"
- [ ] **All S3 latency / pricing**: Use realistic numbers (S3 LIST ~100ms for 1000 keys, not 500ms each)
- [ ] **All format-specific claims**: Check against official spec (Parquet: row group default 128MB, Avro: sync marker 16 bytes, etc.)
- [ ] **All Mermaid diagrams**: Render without syntax errors
- [ ] **All code examples**: Syntax-check Python/SQL/Scala/Java
- [ ] **All cross-references**: `grep` file links to ensure they exist
- [ ] **No vague claims**: No "~15%" or "~20-40%" without caveat
- [ ] **No invented configs**: Every Spark/Kafka/Flink config must exist

---

## Execution Protocol

Each rewrite follows the same workflow:

1. **Read original file** in full
2. **Check cross-references** from other files (grep for filename)
3. **Rewrite** using the template, ensuring every diagram is Mermaid
4. **Self-verify** against checklist
5. **Read final file** once more end-to-end
6. **Commit** with message format:
   ```
   Rewrite TOPIC as interview deep-dive
   
   - Added Mermaid diagrams: [list]
   - Added real interview questions: [list]
   - Added decision trees, worked examples
   - Fixed inaccuracies: [if any found]
   ```
7. **Proceed to next file** without asking for approval

---

## Validation After Each File

After each rewrite, these commands verify integrity:

```bash
# Check cross-references still work
rg "filename-without-ext" --type md | grep -v "file-to-verify"

# Check Mermaid blocks parse (basic count)
grep -c '```mermaid' file.md && grep -c '^```$' file.md

# Check all hex values are referenced correctly
grep -o '0x[0-9A-Fa-f ]*0x[0-9A-Fa-f ]*' file.md
```

---

## File Order Summary

1. `foundations/olap-vs-oltp.md` — quickest win, most common interview opener
2. `foundations/data-modeling.md` — central topic, heavy interview weight
3. `foundations/distributed-systems.md` — good content needs interview framing
4. `foundations/containerization.md` — good content needs depth + diagrams
5. `foundations/serialization.md` — verify depth against standard
6. `apache-kafka/notes.md` — major topic, high interview value
7. `apache-flink/notes.md` — major topic, high interview value
8. `apache-iceberg/notes.md` — growing topic, high value
9. `system-design/notes.md` — restructure as interview scenarios
10. `apache-spark-pyspark/notes.md` — add interview sections
11. `emr/notes.md` — add interview quick reference
