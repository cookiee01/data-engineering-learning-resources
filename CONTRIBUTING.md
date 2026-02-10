# Contributing Guide

This repo is “notes-first”: we prefer short, high-signal notes and curated resources over copying large official docs.

## What To Add
- A short note (`notes.md` or topic-specific `*.md`) that teaches the concept.
- 1–5 external links that reinforce the note (cheat sheets, blogs, playlists).
- Optional: a `progress.md` entry if it tracks your learning.

## Note Quality Bar (Clear, Production-Oriented)
Use this structure when writing new notes:

1. Goal (in 1 minute)
2. First principles (start without the component)
3. Build-up in layers (baseline → production → scale → failure modes)
4. Mental models / analogies
5. On-the-wire details (headers, retries, timeouts, ordering, consistency)
6. AWS mapping (if relevant)
7. Debugging playbook (symptom → likely cause → what to check)
8. Practical tradeoffs (cost, reliability, security, operability)
9. Interview section (30-sec + 2-min answers + common follow-ups)

## Resource Curation Rules
- Prefer resources that are widely used, succinct, and actionable.
- Avoid adding 20+ links for one topic. Start with the best 3–7.
- If you add a long/official doc link, explain *exactly what to read* and *why*.

## Changelog
When adding/removing anything notable:
- Update `CHANGELOG.md`
- Add a short bullet under the latest date section

## Repository Hygiene
- Don’t commit IDE files (`.idea/`) or OS files (`.DS_Store`).
- Keep filenames consistent: lowercase with hyphens is preferred.
