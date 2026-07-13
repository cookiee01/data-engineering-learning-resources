# Repository Guidelines

## Project Structure & Module Organization
This is a notes-first data engineering learning repository. Start with `README.md` for orientation and `INDEX.md` for the table of contents. Topic folders such as `apache-spark-pyspark/`, `apache-flink/`, `apache-kafka/`, `apache-iceberg/`, `emr/`, `foundations/`, and `system-design/` contain Markdown notes and curated resources. PySpark sample datasets live in `apache-spark-pyspark/data/`; generated Spark output belongs in `apache-spark-pyspark/output/` and should not be treated as source material.

## Build, Test, and Development Commands
Most contributions are Markdown-only and do not require a build. For PySpark practice work, use:

```bash
cd apache-spark-pyspark
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Use `rg "term"` from the repository root to find existing coverage before adding duplicate notes. Run `git diff --check` before committing to catch whitespace issues.

## Coding Style & Naming Conventions
Keep notes concise, production-oriented, and easy to scan. Prefer lowercase, hyphenated filenames such as `kafka-to-flink-local-setup.md` or clear conventional names like `notes.md` and `progress.md`. Use Markdown headings, short paragraphs, and focused bullets. When adding resources, include only the best links and explain what to read and why.

For Python or PySpark snippets, use 4-space indentation, descriptive snake_case names, and small examples that can run against files in `apache-spark-pyspark/data/`.

## Testing Guidelines
There is no central automated test suite. Validate Markdown changes by checking links, headings, and examples manually. For PySpark examples, run them locally inside the virtual environment and keep sample inputs small. If a command produces generated files, place them under an `output/` directory and avoid committing bulky or transient results.

## Commit & Pull Request Guidelines
Existing commits use short, imperative messages such as `Add Spark execution architecture concept note and video link` and `Clean up wording for public repo`. Follow that style: start with a verb, name the topic, and keep the subject specific.

Pull requests should summarize what changed, list added or removed resources, mention any commands run, and link related issues when available. Update `CHANGELOG.md` for notable additions, removals, or reorganizations.

## Security & Configuration Tips
Do not commit IDE files, OS files, credentials, private URLs, or local environment directories such as `.venv/`. Keep examples generic and avoid exposing account IDs, tokens, internal hostnames, or proprietary production details.
