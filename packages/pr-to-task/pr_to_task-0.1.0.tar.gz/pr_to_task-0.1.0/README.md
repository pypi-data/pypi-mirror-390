<p align="center">
  <a href="https://github.com/astral-sh/uv" target="blank"><img src="https://github.com/astral-sh/uv/blob/8674968a17e5f2ee0dda01d17aaf609f162939ca/docs/assets/logo-letter.svg" height="100" alt="uv logo" /></a>
  <a href="https://pre-commit.com/" target="blank"><img src="https://pre-commit.com/logo.svg" height="100" alt="pre-commit logo" /></a>
  <a href="https://github.com/astral-sh/ruff" target="blank"><img src="https://raw.githubusercontent.com/astral-sh/ruff/8c20f14e62ddaf7b6d62674f300f5d19cbdc5acb/docs/assets/bolt.svg" height="100" alt="ruff logo" style="background-color: #ef5552" /></a>
  <a href="https://bandit.readthedocs.io/" target="blank"><img src="https://raw.githubusercontent.com/pycqa/bandit/main/logo/logo.svg" height="100" alt="bandit logo" /></a>
  <a href="https://docs.pytest.org/" target="blank"><img src="https://raw.githubusercontent.com/pytest-dev/pytest/main/doc/en/img/pytest_logo_curves.svg" height="100" alt="pytest logo" /></a>
</p>

<p align="center">
  <a href="https://docs.docker.com/" target="blank"><img src="https://www.docker.com/wp-content/uploads/2022/03/Moby-logo.png" height="60" alt="Docker logo" /></a>
  <a href="https://github.com/features/actions" target="blank"><img src="https://avatars.githubusercontent.com/u/44036562" height="60" alt="GitHub Actions logo" /></a>
</p>

# GitHub PR Comments Fetcher

A Python CLI tool to fetch GitHub PR comments and optionally generate Claude Code hooks for processing them.

[![CodeQL](https://github.com/arthrod/pr_to_task/workflows/codeql/badge.svg)](https://github.com/arthrod/pr_to_task/actions/workflows/codeql.yml)
[![GitHub CI](https://github.com/arthrod/pr_to_task/workflows/ci/badge.svg)](https://github.com/arthrod/pr_to_task/actions/workflows/ci.yml)
[![GitHub license](https://img.shields.io/github/license/arthrod/pr_to_task)](https://github.com/arthrod/pr_to_task)

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [With Claude Code Hooks](#with-claude-code-hooks)
  - [Examples](#examples)
- [What's in the box ?](#whats-in-the-box-)
- [Testing](#testing)
- [Docker](#docker)

---

## Prerequisites

- [Python](https://www.python.org/downloads/) **>=3.11.0** (_tested with 3.11.14 and 3.13.7_)
- [pre-commit](https://pre-commit.com/#install) **>=3.2.0 <5.0.0** (_tested with 4.3.0_)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) **>=0.8.17** (_tested with 0.8.24_)
- [docker](https://docs.docker.com/get-docker/) (_optional_)

---

## Installation

1. Clone the git repository

   ```bash
   git clone https://github.com/arthrod/pr_to_task.git
   ```

2. Go into the project directory

   ```bash
   cd python-boilerplate/
   ```

3. Checkout working branch

   ```bash
   git checkout <branch>
   ```

4. Enable pre-commit hooks

   ```bash
   pre-commit install
   ```

5. Configure Python environment

   ```bash
   uv python install
   uv venv
   source .venv/bin/activate
   uv sync
   ```

---

## Usage

The `get-pr-comments` CLI tool fetches GitHub PR comments and generates a JSONL file. It can optionally generate Claude Code hooks for processing comments one at a time.

### Basic Usage

```bash
# Activate virtual environment
source .venv/bin/activate

# Fetch comments from a public repository
uv run get-pr-comments --project owner/repo --pr 123

# With authentication (for private repos or higher rate limits)
export GITHUB_TOKEN=your_token_here
uv run get-pr-comments --project owner/repo --pr 123

# Or provide token directly
uv run get-pr-comments --project owner/repo --pr 123 --token your_token_here
```

### Command Options

- `--user TEXT`: GitHub username (default: "arthrod")
- `--token TEXT`: GitHub personal access token (optional for public repos)
- `--project TEXT`: GitHub repository in format "owner/repo" (required)
- `--pr INTEGER`: Pull request number (required)
- `--since TEXT`: Filter comments since date in ISO 8601 format (optional)
- `--quantity INTEGER`: Number of comments to fetch from most recent (optional)
- `--output PATH`: Output JSONL file path (default: "pr_comments.jsonl")
- `--hooks`: Generate Claude Code hooks configuration (default: false)

### With Claude Code Hooks

Generate hooks to process comments automatically in Claude Code:

```bash
uv run get-pr-comments --project owner/repo --pr 123 --hooks
```

This creates:
- `.claude/settings.json`: Claude Code hooks configuration
- `process_comments.py`: Script to process comments one at a time

The SessionStart hook will automatically present comments to Claude one line at a time.

### Examples

```bash
# Fetch last 10 comments from a PR
uv run get-pr-comments --project arthrod/my-repo --pr 42 --quantity 10

# Fetch comments since a specific date
uv run get-pr-comments --project arthrod/my-repo --pr 42 --since "2024-01-01T00:00:00Z"

# Generate hooks and custom output file
uv run get-pr-comments --project arthrod/my-repo --pr 42 --output my_comments.jsonl --hooks

# Get help
uv run get-pr-comments --help
```

### Output Format

The tool generates a JSONL file where each line is a JSON object representing one complete comment:

```json
{
  "comment_id": 123456,
  "comment_url": "https://github.com/owner/repo/pull/42#discussion_r123456",
  "author": "username",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "comment_type": "review",
  "path": "src/file.py",
  "position": 10,
  "line": 42,
  "text": "This is the full comment text.\nIt can contain multiple lines.\nAll preserved in a single JSON object."
}
```

---

## What's in the box ?

### uv

[uv](https://github.com/astral-sh/uv) is an extremely fast Python package and project manager, written in Rust.

**pyproject.toml file** ([`pyproject.toml`](pyproject.toml)): orchestrate your project and its dependencies
**uv.lock file** ([`uv.lock`](uv.lock)): ensure that the package versions are consistent for everyone
working on your project

For more configuration options and details, see the [configuration docs](https://docs.astral.sh/uv/).

### pre-commit

[pre-commit](https://pre-commit.com/) is a framework for managing and maintaining multi-language pre-commit hooks.

**.pre-commit-config.yaml file** ([`.pre-commit-config.yaml`](.pre-commit-config.yaml)): describes what repositories and
hooks are installed

For more configuration options and details, see the [configuration docs](https://pre-commit.com/).

### ruff

[ruff](https://github.com/astral-sh/ruff) is an extremely fast Python linter, written in Rust.

Rules are defined in the [`pyproject.toml`](pyproject.toml).

For more configuration options and details, see the [configuration docs](https://github.com/astral-sh/ruff#configuration).

### mypy

[mypy](http://mypy-lang.org/) is an optional static type checker for Python that aims to combine the benefits of
dynamic (or "duck") typing and static typing.

Rules are defined in the [`pyproject.toml`](pyproject.toml).

For more configuration options and details, see the [configuration docs](https://mypy.readthedocs.io/).

### bandit

[bandit](https://bandit.readthedocs.io/) is a tool designed to find common security issues in Python code.

Rules are defined in the [`pyproject.toml`](pyproject.toml).

For more configuration options and details, see the [configuration docs](https://bandit.readthedocs.io/).

### docformatter

[docformatter](https://github.com/PyCQA/docformatter) is a tool designed to format docstrings to
follow [PEP 257](https://peps.python.org/pep-0257/).

Options are defined in the [`.pre-commit-config.yaml`](.pre-commit-config.yaml).

---

## Testing

We are using [pytest](https://docs.pytest.org/) & [pytest-cov](https://github.com/pytest-dev/pytest-cov) to write tests.

To run tests:

```bash
uv run pytest tests
```

<details>

<summary>Output</summary>

```text
collected 1 item

tests/test_python_boilerplate.py::test_hello_world PASSED
```

</details>

To run tests with coverage:

```bash
uv run pytest tests --cov=src
```

<details>

<summary>Output</summary>

```text
collected 1 item

tests/test_python_boilerplate.py::test_hello_world PASSED

---------- coverage: platform linux, python 3.13.7-final-0 -----------
Name                                 Stmts   Miss  Cover
--------------------------------------------------------
src/python_boilerplate/__init__.py       1      0   100%
src/python_boilerplate/main.py           6      2    67%
--------------------------------------------------------
TOTAL                                    7      2    71%
```

</details>

---

## Docker

### Build

To build the docker `production` image using [`Dockerfile`](Dockerfile):

```bash
docker build . -t my-python-application:latest
```

To build the docker `development` image using [`Dockerfile`](Dockerfile):

```bash
docker build . --target development -t my-python-application:dev
```

### Run

To run the python app example inside Docker:

```bash
docker run -it --rm my-python-application:latest # or :dev for development
```

<details>

<summary>Output</summary>

```text
Hello World
```

</details>

### Execute command inside container

```bash
docker run -it --rm my-python-application:latest bash
```

---
