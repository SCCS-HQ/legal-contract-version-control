# Contributing to Avora

> **Pre-Alpha.** Avora is still in early development and likely has many bugs or missing features. If you discover a bug or would like to suggest a feature, please open an issue with the relevant label. Contributions of all kinds — code, documentation, bug reports, and ideas — are greatly appreciated!

Thank you for your interest in contributing to Avora, a version-control system purpose-built for legal contracts. This guide explains how to set up a development environment, the conventions we follow, and how to submit changes.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Repository Layout](#repository-layout)
- [Requirements](#requirements)
- [Project Setup](#project-setup)
- [Running the CLI](#running-the-cli)
- [Testing](#testing)
- [Code Style & Formatting](#code-style-formatting)
- [Find Something to Do](#find-something-to-do)
- [Development Workflow](#development-workflow)
- [Commit Guidelines](#commit-guidelines)
- [Pull Requests](#pull-requests)
- [Reporting Bugs & Suggesting Features](#reporting-bugs-suggesting-features)
- [Need Help?](#need-help)

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please be respectful, welcoming, and constructive in all interactions.

## Repository Layout

Avora is a Python monorepo. Each package is independently buildable and published to PyPI.

```
legal-contract-version-control/
├── packages/
│   ├── avora/      # `avora` CLI — distributed as the `avora` package
│   │   ├── src/avora/
│   │   ├── tests/
│   │   └── pyproject.toml
│   └── remote_avora/     # `remote-avora` FastAPI server — distributed as `remote-avora`
│       ├── src/remote_avora/
│       ├── tests/
│       └── pyproject.toml
├── docs/                # MkDocs (Material) documentation source
├── mkdocs.yml           # Documentation site config
└── dev_requirements.txt # Shared development/test dependencies
```

- **`avora`** — the command-line client used to initialize repositories, commit changes, branch, merge, and push/pull from a remote host. Entry point: `avora.avora_entrypoint:main`.
- **`remote_avora`** — a self-hosted FastAPI server that stores repositories and serves them over HTTP so multiple users can clone, push, and pull. Entry point: `remote_avora.remote_avora_entrypoint:main`.

## Requirements

- **Python 3.12 or higher.** Avora uses modern typing syntax (e.g. PEP 695 generics); older versions will not run. Download from [python.org](https://www.python.org/downloads/).
- **Git** — for version control and submitting changes.
- A **GitHub account** — to open issues and submit pull requests.

## Project Setup

1. **Fork** the repository on GitHub, then **clone** your fork:

   ```bash
   git clone https://github.com/<your-username>/legal-contract-version-control.git
   cd legal-contract-version-control
   ```

2. **Create and activate a virtual environment** (recommended, keeps dependencies isolated):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install the shared development dependencies** (pytest, formatters, and runtime deps for both packages):

   ```bash
   pip install -r dev_requirements.txt
   ```

4. **Install the packages in editable mode** so your changes are reflected without reinstalling:

   ```bash
   pip install -e packages/avora
   pip install -e packages/remote_avora
   ```

## Running the CLI

With the packages installed (editable or otherwise), the console scripts are available on your `PATH`:

```bash
avora help              # list all avora commands
remote-avora serve      # start the remote server (serves from the current directory)
```

`avora` provides 17 subcommands covering the full version-control lifecycle: `init`, `commit`, `branch`, `merge`, `switch`, `clone`, `push`, `pull`, `publish`, `log`, `diff`, `open`, `revert`, `reset`, `status`, `config`, `help`.

`remote-avora` provides `serve` and `help`.

## Testing

Tests use [pytest](https://docs.pytest.org/) and live alongside each package under `packages/<package>/tests/`. `pytest-asyncio` is used for the async FastAPI server tests.

Run the full suite from the repository root:

```bash
pytest
```

Run a single package's tests:

```bash
# avora (CLI)
pytest packages/avora/tests

# remote_avora (server)
pytest packages/remote_avora/tests
```

Run a single test file or test:

```bash
pytest packages/avora/tests/test_commit.py
pytest packages/avora/tests/test_commit.py::test_commit_main_raises_if_commit_message_is_empty
```

Generate a coverage report:

```bash
pytest --cov=avora --cov=remote_avora
```

When working in `packages/avora/tests`, note that `conftest.py` imports shared test constants via `from test_constants import ...`. Run tests with that directory on the path (the default `pytest` invocation from the repo root handles this) if you hit import errors.

## Code Style & Formatting

Code is formatted with **[black](https://black.readthedocs.io/)** and **[isort](https://pycqa.github.io/isort/)** using the black profile. A CI workflow (`.github/workflows/format.yml`) automatically runs both on pull requests that touch `.py` files and commits the formatting back to same-repo branches.

To format locally before pushing:

```bash
pip install black isort
isort --profile black .
black .
```

Keep changes consistent with the surrounding code, use descriptive names, and include docstrings on new functions/classes as the existing code does.

## Find Something to Do

The easiest way to get started is to browse the [Issues](https://github.com/Avora-Docx/Avora-Docx/issues) tab:

- Look for issues labeled **good first issue** if you're new to the project.
- Check for issues labeled **help wanted** for tasks we'd love community help with.
- If you have an idea that isn't already tracked, open a new issue to discuss it before starting work.

## Development Workflow

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally (see [Project Setup](#project-setup)).
3. **Create a branch** for your work (see [Commit Guidelines](#commit-guidelines) for naming):

   ```bash
   git checkout -b feature/my-new-feature
   ```

4. **Make your changes**, keeping them focused and well-tested.
5. **Format and test** your changes (see [Code Style & Formatting](#code-style-formatting) and [Testing](#testing)).
6. **Commit** your changes following the guidelines below.
7. **Push** your branch to your fork:

   ```bash
   git push origin feature/my-new-feature
   ```

8. **Open a Pull Request** against the `main` branch of the upstream repository.

## Commit Guidelines

Avora uses the [Conventional Commits](https://www.conventionalcommits.org/) format. A commit message template is provided in `.git_commit_template` — enable it locally with:

```bash
git config commit.template .git_commit_template
```

Format:

```
<type>(<scope>): <short description>

[optional body: explain WHY the change was made]

[optional footer: e.g. Closes #42]
```

### Commit Types

| Type       | Purpose                                            |
|------------|----------------------------------------------------|
| `feat`     | New feature                                        |
| `fix`      | Bug fix                                            |
| `refactor` | Restructure code without changing behavior         |
| `perf`     | Performance improvement                            |
| `style`    | Formatting only (whitespace, formatting)           |
| `docs`     | Documentation changes                              |
| `test`     | Add or modify tests                                |
| `chore`    | Maintenance tasks (configs, dependencies)          |
| `build`    | Build system changes                               |
| `ci`       | CI/CD configuration changes                        |
| `revert`   | Revert a previous commit                           |
| `wip`      | Work in progress                                   |
| `debug`    | Debugging changes                                  |

### Examples

```
feat(commit): add diff command for tracked files
fix(config): handle empty config on first read
tests(push): update push tests for new remote layout
docs(readme): document remote_avora setup
```

Guidelines:

- Use the imperative mood (`Add ...`, not `Added ...`).
- Keep commits focused — one logical change per commit is easier to review.
- Reference the related issue where applicable (e.g. `Closes #42`).

### Branch Naming

Use a short, descriptive prefix:

| Prefix      | Purpose                                  |
|-------------|------------------------------------------|
| `feature/`  | New features or enhancements             |
| `fix/`      | Bug fixes                                |
| `docs/`     | Documentation changes                    |
| `test/`     | Adding or updating tests                 |
| `refactor/` | Code changes that don't change behavior  |

## Pull Requests

- Target the `main` branch of the upstream repository.
- Fill out the PR template (`docs/pull_request_template.md`) and describe **what** changed and **why**.
- Link any related issues (e.g. `Closes #42`).
- Ensure your code is formatted (`black` + `isort`) and that the test suite passes.
- Ensure the CLI commands still work as expected for any behavior you touched.
- Be responsive to review feedback. An automated AI reviewer (`.github/workflows/pr-review.yml`, prompt in `docs/PR_REVIEWER.md`) runs on PRs and posts findings; address or discuss them as part of the review.

## Reporting Bugs & Suggesting Features

Before opening a new issue, please search existing issues to avoid duplicates. Use the provided templates under `.github/ISSUE_TEMPLATE/`:

- **Bugs** (`bug_report.md`) — include steps to reproduce, expected vs. actual behavior, your OS + version, and Python version.
- **Features** (`feature_request.md`) — describe the problem you're trying to solve and propose a solution if you have one.

Apply the appropriate label (`bug` or `enhancement`) when creating the issue.

## Need Help?

If you get stuck or have questions, feel free to open an issue or reach out. We're happy to help you get your contribution merged!

Thank you for helping make Avora better!