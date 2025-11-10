# create-dump

[![PyPI Version](https://badge.fury.io/py/create-dump.svg)](https://badge.fury.io/py/create-dump)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/dhruv13x/create-dump/actions/workflows/ci.yml/badge.svg)](https://github.com/dhruv13x/create-dump/actions)
[![Coverage](https://codecov.io/gh/dhruv13x/create-dump/branch/main/graph/badge.svg)](https://codecov.io/gh/dhruv13x/create-dump)

**Enterprise-Grade Code Dump Utility for Monorepos**

`create-dump` is a production-ready CLI tool for automated code archival in large-scale monorepos.
It generates branded Markdown dumps with Git metadata, integrity checksums, flexible archiving,
retention policies, path safety, full concurrency, and SRE-grade observability.

Designed for SRE-heavy environments (Telegram bots, microservices, monorepos), it ensures
**reproducible snapshots for debugging, forensics, compliance audits, and CI/CD pipelines**.

Built for Python 3.11+, leveraging **AnyIO**, Pydantic, Typer, Rich, and Prometheus metrics.

-----

## 🚀 Quick Start

```bash
pip install create-dump

# Create an interactive config file
create-dump --init

# Single dump (current directory)
create-dump single --dest ./dumps/my-snapshot.md

# Batch dump (monorepo)
create-dump batch --root ./monorepo --archive --keep-last 5

# SRE / Git-only dump in watch mode with secret redaction
create-dump single --git-ls-files --watch --scan-secrets --hide-secrets

# Output example:
# dumps/my-snapshot_all_create_dump_20250101_121045.md
# dumps/my-snapshot_all_create_dump_20250101_121045.md.sha256
# archives/my-snapshot_20250101_121045.zip
```

-----

## ✨ Features

  * **Branded Markdown Generation**
    Auto TOC (list or tree), language-detected code blocks, Git metadata, timestamps.

  * **Async-First & Concurrent**
    Built on `anyio` for high-throughput, non-blocking I/O. Parallel file processing (16+ workers), timeouts, and progress bars (Rich).

  * **Flexible Archiving**
    Automatically archive old dumps into **ZIP, tar.gz, or tar.bz2** formats. Includes integrity validation and retention policies (e.g., "keep last N").

  * **Git-Native Collection**
    Use `git ls-files` for fast, accurate file discovery (`--git-ls-files`) or dump only changed files (`--diff-since <ref>`).

  * **Live Watch Mode**
    Run in a persistent state (`--watch`) that automatically re-runs the dump on any file change, perfect for live development.

  * **Secret Scanning**
    Integrates `detect-secrets` to scan files during processing. Can fail the dump (`--scan-secrets`) or redact secrets in-place (`--hide-secrets`).

  * **Safety & Integrity**
    SHA256 hashing, atomic writes, async-safe path guards (prevents Zip-Slip), and orphan quarantine.

  * **Observability**
    Prometheus metrics (e.g., `create_dump_duration_seconds`, `create_dump_files_total`).

| Feature | Single Mode | Batch Mode |
| :--- | :--- | :--- |
| **Scope** | Current dir/files | Recursive subdirs |
| **Archiving** | Optional | Enforced retention |
| **Concurrency** | Up to **16** workers | Parallel subdirs |
| **Git Metadata** | ✔️ | Per-subdir ✔️ |

-----

## 📦 Installation

### PyPI

```bash
pip install create-dump
```

### From Source

```bash
git clone https://github.com/dhruv/create-dump.git
cd create-dump
pip install -e .[dev]
```

### Docker

```bash
FROM python:3.12-slim
RUN pip install create-dump
ENTRYPOINT ["create-dump"]
```

-----

## ⚙️ Configuration

### 🚀 Interactive Setup (`--init`)

The easiest way to configure `create-dump` is to run the built-in interactive wizard:

```bash
create-dump --init
```

This will create a `create_dump.toml` file with your preferences. You can also add this configuration to your `pyproject.toml` file under the `[tool.create-dump]` section.

### Example (pyproject.toml)

```toml
[tool.create-dump]
# Default output destination (CLI --dest overrides)
dest = "/path/to/dumps"

# Enable .gitignore parsing
use_gitignore = true

# Include Git branch/commit in header
git_meta = true

# Max file size in KB (e.g., 5MB)
max_file_size_kb = 5000

# Canonical regex for dump artifacts
dump_pattern = ".*_all_create_dump_\\d{8}_\\d{6}\\.(md(\\.gz)?|sha256)$"

# Default excluded directories
excluded_dirs = ["__pycache__", ".git", ".venv", "node_modules"]

# Prometheus export port
metrics_port = 8000

# --- New v8 Feature Flags ---

# Use 'git ls-files' by default for collection
# git_ls_files = true

# Enable secret scanning by default
# scan_secrets = true

# Redact found secrets (requires scan_secrets=true)
# hide_secrets = true
```

Override any setting via CLI flags.

-----

## 📖 Usage

### Single Mode

```bash
# Dump all files matching .py, include git meta
create-dump single --include "*.py" --git-meta

# Dump only files changed since 'main' branch and watch for new changes
create-dump single --diff-since main --watch

# Dump using git, scan for secrets, and redact them
create-dump single --git-ls-files --scan-secrets --hide-secrets

# Dry run with verbose logging
create-dump single --dry-run --verbose
```

### Batch Mode

```bash
# Run dumps in 'src' and 'tests', then archive old dumps, keeping 10
create-dump batch --root ./monorepo --dirs "src,tests" --keep-last 10 --archive

# Run dumps and create grouped archives (e.g., src.zip, tests.zip)
create-dump batch --root ./monorepo --archive-all --archive-format tar.gz
```

-----

## 🗃️ Archiving Workflow

1.  Detect MD/SHA pairs
2.  Group by prefix (e.g., `src_`, `tests_`)
3.  Archive (ZIP/TAR) with verification
4.  Prune old dumps based on retention
5.  Cleanup + SHA generation

-----

## 🏗️ Architecture Overview

┌───────────────┐    ┌─────────────────┐    ┌───────────────────┐
│   CLI (Typer) │──▶ │  Orchestrator   │──▶ │   Single/Batch     │
└───────────────┘    └─────────────────┘    └───────────────────┘
│
▼
┌───────────────┐    ┌─────────────────┐    ┌───────────────────┐
│ Config (TOML) │◀──▶ │  Core (Models) │◀──▶ │ Logging/Utils     │
└───────────────┘    └─────────────────┘    └───────────────────┘
│
▼
┌───────────────┐    ┌─────────────────┐    ┌───────────────────┐
│   Collector   │──▶ │ Writer (MD/Zip) │──▶ │  Archiver (Zip)    │
└───────────────┘    └─────────────────┘    └───────────────────┘

-----

## 🧪 Testing & Development

Run the full test suite using `pytest`:

```bash
# Install dev dependencies
pip install -e .[dev]

# Run tests with coverage
pytest --cov=create_dump --cov-report=html
```

Run linters and formatters:

```bash
ruff check src/ tests/
black src/ tests/
mypy src/
```

-----

## 🔒 Security & Reliability

  * **Secret Scanning** & Redaction (`detect-secrets`)
  * **Async-Safe Path Guards** (Prevents traversal & Zip-Slip)
  * Archive Integrity + SHA256 Validation
  * `tenacity` Retries on I/O
  * Prometheus Metrics on `:8000/metrics`
  * Graceful `SIGINT`/`SIGTERM` Cleanup Handlers

### Limitations

  * No remote filesystem support (e.g., S3, GCS)

-----

## 🤝 Contributing

1.  Fork repo → create branch
2.  Follow Conventional Commits
3.  Run full CI suite (`pytest`, `ruff`, `mypy`)
4.  Add/Update any ADRs under `/ADRs`
5.  Follow the Code of Conduct

Security issues → `security@dhruv.io`

-----

## 📄 License

MIT License.
See LICENSE.

-----

## 🙏 Acknowledgments

Powered by Typer, Rich, Pydantic, Prometheus, and AnyIO.

Inspired by tooling from Nx, Bazel, and internal SRE practices.

-----

*Questions or ideas?*
*Open an issue or email `dhruv13x@gmail.com`.*