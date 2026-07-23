# Data Engineering Learning Resources

A curated, notes-first repository for learning and interview preparation.

## Getting Started

```bash
git clone https://github.com/anomalyco/data-engineering-learning-resources.git
cd data-engineering-learning-resources
```

**View all notes in a browsable site** (search, dark mode, code copy, quiz app):

```bash
pip install mkdocs-material
mkdocs serve
# Open http://localhost:8000
```

**Or just read the markdown files directly** — start at `INDEX.md`.

## Prerequisites
- Python 3.8+ and `pip` (only needed for the MkDocs site)
- No other dependencies required

## How To Navigate
- Start at `INDEX.md` for the table of contents.
- Each topic folder contains short, clarity-first notes and links.
- Use `CHANGELOG.md` to see what changed recently.

### Interactive Mode
The MkDocs site includes flashcards and a multiple-choice quiz that tracks XP and progress via localStorage — no backend needed.

## Repo Structure
- `apache-flink/` — notes, setup guide, practice roadmap
- `apache-spark-pyspark/` — deep notes, Q&A journey, practice code
- `apache-kafka/` — notes and resources
- `apache-iceberg/` — architecture and interview notes
- `emr/` — EMR/Hadoop notes
- `foundations/` — networking and distributed systems fundamentals
- `system-design/` — system design notes
- `interview-prep/` — roadmap, sprint plan, quiz app, progress tracking

## Contributing
See `CONTRIBUTING.md` for:
- how to add resources/notes
- note-writing guidelines (clear + production-oriented)
- how to update the changelog
