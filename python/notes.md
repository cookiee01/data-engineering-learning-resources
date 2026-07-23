# Python for the Enterprise

> Staff DE Sam and Senior DE Alex discuss everything a data engineer should know about Python beyond syntax — packaging, deployment, versioning, tooling, and production hygiene.

## Contents

1. [Why This Matters](#1-why-this-matters)
2. [Project Packaging — pyproject.toml and Friends](#2-project-packaging-pyprojecttoml-and-friends)
3. [Package Managers — pip, Poetry, uv, and the Rest](#3-package-managers-pip-poetry-uv-and-the-rest)
4. [Dependency Management Purgatory](#4-dependency-management-purgatory)
5. [Versioning — SemVer, PEP 440, and CalVer](#5-versioning-semver-pep-440-and-calver)
6. [Build and Deploy](#6-build-and-deploy)
7. [Code Quality — Ruff, Mypy, Pytest, Pre-Commit](#7-code-quality-ruff-mypy-pytest-pre-commit)
8. [Python Runtime — Which Python, Where, and How](#8-python-runtime-which-python-where-and-how)
9. [Enterprise Tooling — Private PyPI, Scanning, Caching](#9-enterprise-tooling-private-pypi-scanning-caching)
10. [Quick-Reference Cheatsheet](#10-quick-reference-cheatsheet)

---

## 1. Why This Matters

**Alex:** I can write Python code. Why do I need to know about wheels and pyproject.toml?

**Sam:** Because in a real team, your Python code is not a script — it is a **shippable artifact**. Someone else (or an automated pipeline) needs to build it, deploy it, run tests against it, and know which version is in production. The ecosystem of packaging, dependency management, and deployment is not bureaucracy — it is the difference between "works on my machine" and "works in production."

**Alex:** Give me the map. What should I know?

**Sam:** Start with the packaging standard (pyproject.toml), understand what a wheel is and why it exists, know when to use Poetry vs pip vs uv, pin dependencies and understand lock files, use SemVer, build Docker images with multi-stage, and run code quality checks automatically. Walk through each one.

---

## 2. Project Packaging — pyproject.toml and Friends

### The Evolution

```
setup.py          ← the old way (executable, implicit, hard to parse)
  └── setup.cfg   ← declarative metadata, still tied to setuptools
       └── pyproject.toml  ← PEP 517/518/621, the standard (PEP 621 since 2020)
```

**Sam:** `pyproject.toml` is the single-source-of-truth for Python projects as of PEP 621. It declares build system requirements, project metadata, dependencies, and tool configurations — all in one TOML file that any tool can parse without executing code.

```toml
[build-system]
requires = ["setuptools>=64", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "data-engineering-toolkit"
version = "0.1.0"
description = "Internal tools for data pipeline monitoring"
requires-python = ">=3.11"
dependencies = [
    "click>=8.0",
    "rich>=13.0",
    "requests>=2.28",
]

[project.optional-dependencies]
dev = [
    "pytest>=7",
    "ruff>=0.1",
    "mypy>=1.0",
]
test = [
    "pytest>=7",
    "pytest-cov>=4",
]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
```

### sdist vs wheel

```mermaid
flowchart LR
    S[Source<br/>*.py, pyproject.toml] -->|"python -m build"| SD[sdist<br/>.tar.gz]
    S -->|"python -m build"| WH[wheel<br/>.whl]
    SD -->|pip install| I1[Install: build + compile<br/>Slower, needs toolchain]
    WH -->|pip install| I2[Install: unzip + copy<br/>Fast, no compile]
    style WH fill:#10b981,color:#fff
    style SD fill:#f59e0b,color:#fff
```

| Format | Extension | Contains | Install speed | When to use |
| :--- | :--- | :--- | :--- | :--- |
| **sdist** (source distribution) | `.tar.gz` | Source files + `pyproject.toml` | Slow (build step) | When publishing libraries for other platforms (the builder creates the wheel) |
| **wheel** (built distribution) | `.whl` | Pre-built `.pyc` / `.so` / metadata | Fast (unzip + copy) | What most users install — the build artifact |

**Alex:** So I should push wheels to production?

**Sam:** Exactly. Your CI builds a wheel, publishes it to a private package index (Artifactory / CodeArtifact / devpi), and your Dockerfile installs from that index. No build step at deploy time. No `gcc` or build toolchain needed in the production image.

> [!TIP]
> A wheel is just a zip file. Run `unzip -l somepackage.whl` to peek inside. The key file is `METADATA` — it records dependencies, which is how pip resolves the dependency tree at install time.

---

## 3. Package Managers — pip, Poetry, uv, and the Rest

```mermaid
flowchart LR
    subgraph Tools
        PIP[pip]
        UV[uv]
        PO[Poetry]
        PDM[PDM / Hatch]
    end
    subgraph Resolver
        R1[pip: legacy resolver pre-2020<br/>now dependency-graph-based]
        R2[uv: Rust-based, 10-100x faster]
        R3[Poetry: SAT solver, lock-first]
    end
    subgraph Output
        O1[requirements.txt]
        O2[requirements.lock]
        O3[poetry.lock]
        O4[pdm.lock]
    end

    PIP --> R1 --> O1
    UV --> R2 --> O2
    PO --> R3 --> O3
    PDM --> R4 --> O4
```

**Alex:** There are too many. What should I actually use in 2026?

**Sam:** Three tiers:

| Tool | When | Why |
| :--- | :--- | :--- |
| **pip + venv** | Always available, good for Docker images, quick experiments | Ships with Python. No lock file by default — use `pip-tools` to compile `requirements.in` → `requirements.txt` |
| **uv** | Best for speed (10–100x faster pip), growing ecosystem | Rust-based. Replaces pip, venv, pip-tools in one binary. Lock files, project management, Python version management built-in. The 2025–2026 trend. |
| **Poetry** | Best for publishing libraries to PyPI | Full-featured: lock file, build, publish. Heavier dependency resolver. Good if you maintain open-source packages. |

**Alex:** What about conda?

**Sam:** Conda is for data science environments where you need non-Python dependencies (CUDA, HDF5, GDAL). For pure Python services in enterprise data engineering, venv + pip (or uv) is simpler. Conda's environment solver is slow and its lock mechanism is weaker. If your team already uses conda, keep it; do not add it for a new Python project unless you need compiled C extensions that pip cannot easily resolve.

**Alex:** Walk me through the pip + pip-tools workflow.

**Sam:**

```bash
# 1. Declare top-level deps
echo "requests>=2.28" > requirements.in
echo "click>=8.0" >> requirements.in

# 2. Compile into pinned lock file
pip-compile requirements.in  # produces requirements.txt with hashes

# 3. Install from lock
pip install -r requirements.txt --require-hashes

# 4. Add a dep
echo "rich>=13" >> requirements.in
pip-compile --upgrade requirements.in
```

This gives you deterministic installs without Poetry's overhead. For even faster, use `uv pip compile` and `uv pip sync`.

**Alex:** And uv?

**Sam:** uv replaces pip, venv, pip-compile, and pip-sync:

```bash
uv venv                # create venv
uv pip install -r requirements.txt   # install (fast)
uv pip compile pyproject.toml -o requirements.lock   # lock
uv pip sync requirements.lock        # sync venv to lock exactly
uv tool install ruff   # install tools (replaces pipx)
```

> [!TIP]
> uv can install Python versions too: `uv python install 3.12`. This replaces pyenv for most users. Check if your team allows external Rust binaries in CI before adopting — some security policies require pure-Python tooling.

---

## 4. Dependency Management Purgatory

**Alex:** Why not just pin everything to exact versions?

**Sam:** Because you want **security updates without a source change**. Pinning exact versions (`requests==2.28.1`) means you must edit `requirements.in` and recompile to get a patch fix. Ranged deps (`requests>=2.28`) let the resolver pick latest compatible — but without a lock file, builds are non-deterministic (different installs = different behavior).

The compromise:

| Strategy | Lock file | CI behavior | Prod behavior |
| :--- | :--- | :--- | :--- |
| **Ranged + lock** | Yes (pip-tools / uv) | `pip-compile --upgrade` weekly; test with new deps | Install from lock = exact versions |
| **Ranged, no lock** | No | Uses latest matching each time | Builds can break if a dep releases a breaking change |
| **Exact pin** | Not needed | Versions in `requirements.txt` | Stable but manual updates |

**Alex:** What about hashes?

**Sam:** Hash-pinned lock files (`--generate-hashes` in pip-compile) prevent **supply-chain attacks** where a malicious version replaces a legitimate one on PyPI. In enterprise environments with a private PyPI proxy, hashes are less critical (you control what goes in). For open-source projects or pulling directly from PyPI, hashes are a best practice.

**Alex:** Constraint files?

**Sam:** Constraints (`-c constraints.txt`) let you override a transitive dependency's version without changing the direct dependency specification. Common use case: force `urllib3<2` because your internal proxy library has not been updated:

```bash
# constraints.txt
urllib3<2
```

Install: `pip install -r requirements.txt -c constraints.txt`

---

## 5. Versioning — SemVer, PEP 440, and CalVer

```mermaid
flowchart LR
    V["1.4.2"]
    V --> MAJ["1 = MAJOR<br/>Breaking change"]
    V --> MIN["4 = MINOR<br/>New feature, backward-compatible"]
    V --> PAT["2 = PATCH<br/>Bug fix, backward-compatible"]
    MAJ --> E1["SemVer: bump when you break API"]
    MIN --> E2["SemVer: bump for new functionality"]
    PAT --> E3["SemVer: bump for bug fixes"]

    style MAJ fill:#ef4444,color:#fff
    style MIN fill:#f59e0b,color:#fff
    style PAT fill:#10b981,color:#fff
```

### PEP 440 (Python's version specifier)

Python follows PEP 440, which is SemVer-like but with extras for pre-release and post-release:

```
1.2.3           ← final release
1.2.3.dev4      ← development release
1.2.3a1         ← alpha
1.2.3b2         ← beta
1.2.3rc3        ← release candidate
1.2.3.post1     ← post-release (e.g., packaging fix)
1.2.3+sha.abc   ← local version identifier (not for PyPI)
```

**Alex:** When should I use what?

**Sam:**

- **0.x.y** — internal-only, pre-stable. Breaking changes expected.
- **1.x.y** — stable API. Breaking changes only in MAJOR.
- **Pre-releases** (`a1`, `b2`, `rc3`) — publish to private index for integration testing before a stable release.
- **Post-releases** (`.post1`) — avoid. It usually means your CI published without bumping the version. Fix the automation.
- **Local versions** (`+sha.abc`) — useful for internal builds where you want to trace a build to a git commit. PyPI rejects them; your private index may allow them.

> [!WARNING]
> Never use `-` (hyphen) in a Python version string. PEP 440 parses `1.0.0-beta` differently than you expect — it becomes `1.0.0 post beta`, which is not what you meant. Use `1.0.0b1` for beta, `1.0.0rc1` for release candidate.

### CalVer

Some projects (e.g., Ubuntu, pip itself) use date-based versions:

```
24.1          ← year.minor
2025.3.2      ← year.month.patch
```

CalVer is useful when you release frequently and SemVer "bump MAJOR" creates unnecessary ceremony. But for library dependencies that consumers need to reason about, SemVer is the standard.

---

## 6. Build and Deploy

### Building a Wheel

```bash
# Modern (PEP 517)
python -m build    # produces dist/*.whl and dist/*.tar.gz

# Or with uv
uv build
```

### Publishing to a Private Index

```bash
# Using twine (the standard publish tool)
twine upload --repository-url https://private-pypi.example.com/simple dist/*

# Or with Poetry
poetry publish --repository my-private-repo
```

### Docker Multi-Stage for Python

This is the standard production pattern:

```dockerfile
# Stage 1: Build the wheel
FROM python:3.12-slim AS builder
WORKDIR /build
COPY pyproject.toml .
RUN pip install build && python -m build --wheel

# Stage 2: Install from wheel
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /build/dist/*.whl /app/
RUN pip install --no-cache-dir *.whl && rm *.whl
COPY src/ /app/src/
CMD ["python", "-m", "my_package"]
```

Key points:
- **Build stage** has build tools, compilers, headers. It never runs in prod.
- **Runtime stage** has only what is needed to run. Smaller, fewer CVEs.
- `--no-cache-dir` keeps the image lean.
- Copy the wheel, install it, delete it — no source code in the final image (except your application code).

**Alex:** What about not building a wheel at all? Just `pip install -r requirements.txt` in the Dockerfile?

**Sam:** That works and is simpler. You trade:
- **Without wheel**: Docker build time is longer (pip compiles every install), and you need build deps (`gcc`, Python headers) in the build stage.
- **With wheel**: You build once in CI, cache the wheel, and Docker installs from it in seconds. Better for teams shipping to multiple environments (dev, staging, prod) because the exact same wheel goes everywhere.

**Alex:** How does this work with Airflow?

**Sam:** Airflow workers typically use a `requirements.txt` that Airflow installs into the scheduler's Python environment. For Airflow in Docker (or Kubernetes), you build a custom image:

```dockerfile
FROM apache/airflow:2.9.0-python3.11
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
COPY dags/ /opt/airflow/dags/
```

The key is to pin versions in `requirements.txt` (or use a lock file) so that every Airflow deployment is deterministic.

---

## 7. Code Quality — Ruff, Mypy, Pytest, Pre-Commit

**Alex:** What is the modern Python quality stack?

**Sam:** Four tools, one config file (pyproject.toml):

```toml
[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "F", "I", "N", "W", "UP", "B", "SIM", "ARG"]
ignore = ["E501"]  # line length handled by formatter

[tool.ruff.format]
quote-style = "double"

[tool.mypy]
python_version = "3.11"
strict = false
warn_unused_configs = true
ignore_missing_imports = true

[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
addopts = "-ra -q --strict-config"
```

### The Stack

| Tool | Job | Why |
| :--- | :--- | :--- |
| **Ruff** | Linter + formatter (replaces flake8, isort, black, pyupgrade) | Written in Rust, 100–1000x faster than flake8. Single binary, no dependencies. |
| **Mypy** | Static type checker | Catches bugs that tests miss. Start with `strict=false`, then enable checks per-module. |
| **Pytest** | Test runner | Simple fixtures, powerful assertions, great plugins (pytest-cov, pytest-xdist). |
| **Pre-commit** | Git hook runner | Runs ruff, mypy, trailing-whitespace, end-of-file-fixer on every commit. Blocks bad code before review. |

### Pre-commit Config

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.5.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

**Alex:** Do I need tox or nox?

**Sam:** Tox/nox run tests across multiple Python versions. In data engineering, your production Python version is fixed (3.11 or 3.12). Unless you maintain a library that must support Python 3.9 through 3.12, skip tox. Use GitHub Actions matrix builds instead:

```yaml
test:
  strategy:
    matrix:
      python-version: ["3.11", "3.12"]
  steps:
    - uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    - run: pip install -e ".[dev]" && pytest
```

---

## 8. Python Runtime — Which Python, Where, and How

### Managing Python Versions

| Tool | Job | Notes |
| :--- | :--- | :--- |
| **pyenv** | Install multiple Python versions, switch per-directory | Standard choice. Write `.python-version` file for the team. |
| **uv python** | uv's built-in Python management | Simpler, faster. `uv python install 3.12` → `uv python pin 3.12`. |
| **conda** | Python + non-Python envs | Heavy. Avoid for pure Python services. |
| **system Python** | macOS/Linux built-in | Do not use for development. macOS has Python 3.9 from 2021; never the version you need. Always use a version manager. |

### Which Python Version?

- **2025–2026 target**: Python 3.12 or 3.13 in production.
- **Minimum**: 3.11 (end-of-life 2027). Anything below 3.9 is unsupported and insecure.
- **Docker images**: Use `python:3.12-slim` (Debian-based, small) or `python:3.12-alpine` (even smaller, but missing common C libraries).

### The GIL and Free-threaded Python

Python 3.13 introduced an **experimental free-threaded build** (no GIL). For 2026 production use, the GIL still exists by default. Free-threaded Python is promising for CPU-bound data processing but not yet standard in enterprise data engineering (Spark handles parallelism at the JVM level; Python UDFs are single-threaded either way).

### uvloop and Async

For I/O-bound Python services (API gateways, streaming event processors), replace `asyncio`'s event loop with uvloop for 2–4x throughput:

```python
import uvloop
import asyncio
uvloop.install()  # call once at process start
```

Most data engineering is not I/O-bound in Python — it runs in Spark (JVM) or Flink (JVM). Async Python matters for lightweight ingestion services or health-check APIs.

---

## 9. Enterprise Tooling — Private PyPI, Scanning, Caching

### Private Package Index

Enterprises do not pull directly from PyPI (risk of typosquatting, availability, license compliance). Instead:

```mermaid
flowchart LR
    dev[Developer] -->|pip install| proxy[Private PyPI Proxy<br/>Artifactory / devpi / CodeArtifact]
    proxy -->|cache + proxy| pypi[Public PyPI]
    proxy -->|publish| wheel[Internal Wheels<br/>Team packages]
    proxy -->|audit| scan[Vulnerability Scanner<br/>Safety / Snyk / Trivy]
```

**Common tools:**

| Tool | Type | Notes |
| :--- | :--- | :--- |
| **JFrog Artifactory** | Commercial | PyPI proxy, caching, RPM/deb/npm too. Standard in large enterprises. |
| **AWS CodeArtifact** | Managed AWS | PyPI proxy with IAM auth. Use if your infra is AWS. |
| **devpi** | Open source | Self-hosted PyPI proxy + index. Lighter than Artifactory. |
| **Gemfury** | SaaS | Simple private index. Good for smaller teams. |

### Security Scanning

```bash
# Scan requirements for known vulnerabilities
pip-audit -r requirements.txt     # Python Foundation tool
safety check -r requirements.txt  # Commercial, broader DB
trivy filesystem --scanners vuln .  # Container + filesystem scanning
```

**Alex:** How do I set up pip to use a private index?

**Sam:** Three ways:

```bash
# 1. Permanently (in every pip command)
export PIP_INDEX_URL=https://user:pass@private-pypi.example.com/simple
export PIP_TRUSTED_HOST=private-pypi.example.com

# 2. Per-command
pip install --index-url https://private-pypi.example.com/simple mypackage

# 3. In pip.conf (~/.config/pip/pip.conf or /etc/pip.conf)
[global]
index-url = https://private-pypi.example.com/simple
trusted-host = private-pypi.example.com
```

> [!WARNING]
> Do not hardcode credentials in `pip.conf`. Use environment variables or a credential manager. In CI/CD, use `--index-url https://token@private-pypi.example.com/simple` with a short-lived token from your artifact store.

---

## 10. Quick-Reference Cheatsheet

```mermaid
flowchart TD
    START([New Python Project]) --> PYPRO[Create pyproject.toml]
    PYPRO --> PS[Choose package manager]
    PS --> |"pip + pip-tools"| PM1["uv pip compile / pip-compile"]
    PS --> |"uv"| PM2["uv sync / uv lock"]
    PS --> |"Poetry"| PM3["poetry lock / poetry install"]
    PM1 --> CI[Set up CI]
    PM2 --> CI
    PM3 --> CI
    CI --> CODE[lint: ruff]
    CODE --> TYPES[type check: mypy]
    TYPES --> TEST[test: pytest]
    TEST --> BUILD[build: python -m build]
    BUILD --> PUB[publish to private index]
    PUB --> DEPLOY[deploy: Docker multi-stage]

    style START fill:#3b82f6,color:#fff
    style DEPLOY fill:#10b981,color:#fff
```

### Commands

| Task | Command |
| :--- | :--- |
| Create project | `uv init my_project` or `poetry new my_project` |
| Add dependency | `uv add requests` or `poetry add requests` |
| Install from lock | `uv sync` or `poetry install` |
| Build wheel | `python -m build` or `uv build` |
| Run tests | `pytest` |
| Lint | `ruff check . && ruff format --check .` |
| Typecheck | `mypy src/` |
| Create venv | `uv venv` or `python -m venv .venv` |
| Publish to PyPI | `twine upload dist/*` or `poetry publish` |
| Scan vulns | `pip-audit -r requirements.txt` |
| Start Docker | `docker build -t my-app . && docker run my-app` |

### Common File Locations

| File | Purpose |
| :--- | :--- |
| `pyproject.toml` | Project metadata, deps, tool configs |
| `requirements.txt` | Pinned deps (for pip install) |
| `requirements.in` | Top-level deps (input to pip-compile) |
| `requirements.lock` | Hashed lock file (uv) |
| `poetry.lock` | Lock file (Poetry) |
| `.python-version` | Python version pin (pyenv / uv) |
| `.pre-commit-config.yaml` | Git hook definitions |
| `Dockerfile` | Container build |
| `dist/*.whl` | Built wheel artifact |
| `dist/*.tar.gz` | Built sdist artifact |

### Recommended PyPI Packages for Data Engineering

| Package | Use |
| :--- | :--- |
| `click` | CLI argument parsing |
| `rich` | Pretty terminal output, tracebacks |
| `pydantic` | Configuration validation, schema definitions |
| `httpx` | Async HTTP client (replaces requests for async) |
| `ruff` | Linting + formatting |
| `mypy` | Static type checking |
| `pytest` + `pytest-cov` | Testing |
| `pre-commit` | Git hooks |
| `pip-audit` | Dependency vulnerability scanning |
| `pendulum` | Timezone-aware datetime (better than stdlib) |
| `tenacity` | Retry logic (API calls, DB connections) |

---

### Key Interview Answer

> Python packaging moved from `setup.py` (executable, implicit) to `pyproject.toml` (declarative, tool-agnostic) per PEP 621. A wheel (`.whl`) is a pre-built distribution that installs by unzip + copy — no compile step. Use `pip-tools` or `uv` for deterministic dependency resolution with lock files. For deployment, build the wheel in CI and install it in a Docker multi-stage build — the runtime image needs no build toolchain. Version with SemVer (`MAJOR.MINOR.PATCH`); use pre-release tags (`a1`, `b2`, `rc3`) for integration testing. Quality stack: Ruff (lint/format), Mypy (types), Pytest (tests), Pre-commit (gates). In enterprises, route all `pip install` through a private PyPI proxy (Artifactory / devpi / CodeArtifact) for caching, license compliance, and vulnerability scanning.

---

### Resources

- [PEP 621 — Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/)
- [PEP 517 / 518 — Build system independence](https://peps.python.org/pep-0517/)
- [Python Packaging User Guide](https://packaging.python.org/en/latest/)
- [uv documentation](https://docs.astral.sh/uv/)
- [Poetry documentation](https://python-poetry.org/docs/)
- [Ruff documentation](https://docs.astral.sh/ruff/)
- [pip-tools documentation](https://pip-tools.readthedocs.io/en/latest/)
- [Multi-stage Docker builds for Python](https://docs.docker.com/build/building/multi-stage/)
