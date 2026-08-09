# Contributing to SCCS

> **Pre-Alpha.** SCCS is still in early development and likely has many bugs or missing features. If you discover a bug or would like to suggest a feature, please open an issue with the relevant label. Contributions of all kinds — code, documentation, bug reports, and ideas — are greatly appreciated!

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Project Setup](#project-setup)
- [Find Something to Do](#find-something-to-do)
- [Development Workflow](#development-workflow)
- [Commit Guidelines](#commit-guidelines)
- [Pull Requests](#pull-requests)
- [Reporting Bugs & Suggesting Features](#reporting-bugs--suggesting-features)
- [Need Help?](#need-help)

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please be respectful, welcoming, and constructive in all interactions.

## Requirements

- **Python 3.12 or higher.** Download [here](https://www.python.org/downloads/).
- All dependencies defined in [`requirements.txt`](requirements.txt). Install with `pip install -r requirements.txt`.
- **Git** — for version control and submitting changes.
- A GitHub account — to open issues and submit pull requests.

## Quick Start

```bash
# Clone the Git Repository
git clone https://github.com/SCCS-HQ/legal-contract-version-control.git

# Move into the project directory
cd legal-contract-version-control

# Install all required dependencies
pip install -r requirements.txt
```

## Project Setup

SCCS is a CLI tool. After cloning and installing dependencies, make the commands available on your system:

### macOS / Linux

```bash
# Copy all repo CLI files to /usr/local/bin/
sudo cp commands/* /usr/local/bin/

# Make the SCCS entrypoint executable
sudo chmod +x /usr/local/bin/sccs
```

### Windows

Setup instructions for Windows are still **TBA**. If you get SCCS running on Windows, please consider opening a PR to document the steps!

> **Note:** Repositories or clones created with older SCCS versions cannot currently be migrated to newer SCCS versions. Please re-clone the repository or re-initialize SCCS instead.

## Find Something to Do

The easiest way to get started is to browse the [Issues](https://github.com/SCCS-HQ/legal-contract-version-control/issues) tab:

- Look for issues labeled **good first issue** if you're new to the project.
- Check for issues labeled **help wanted** for tasks we'd love community help with.
- If you have an idea that isn't already tracked, open a new issue to discuss it before starting work.

## Development Workflow

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/legal-contract-version-control.git
   cd legal-contract-version-control
   ```
3. **Create a branch** for your work (see [Commit Guidelines](#commit-guidelines) for naming):
   ```bash
   git checkout -b feature/my-new-feature
   ```
4. **Make your changes**, keeping them focused and well-tested.
5. **Commit** your changes following the guidelines below.
6. **Push** your branch to your fork:
   ```bash
   git push origin feature/my-new-feature
   ```
7. **Open a Pull Request** against the `main` branch of the upstream repository.

## Commit Guidelines

- Write clear, descriptive commit messages in the imperative mood (e.g., `Add diff command for tracked files`, not `Added diff command`).
- Keep commits focused — one logical change per commit is easier to review.
- Reference the related issue where applicable (e.g., `Fix #42: handle empty document on commit`).

### Branch Naming

Use a short, descriptive prefix:

| Prefix      | Purpose                              |
|-------------|--------------------------------------|
| `feature/`  | New features or enhancements         |
| `fix/`      | Bug fixes                            |
| `docs/`     | Documentation changes                |
| `test/`     | Adding or updating tests             |
| `refactor/` | Code changes that don't change behavior |

## Pull Requests

- Target the `main` branch of the upstream repository.
- Fill out the PR template and describe **what** changed and **why**.
- Link any related issues (e.g., `Closes #42`).
- Ensure your code follows the existing style and that the CLI commands still work as expected.
- Be responsive to review feedback — reviews are how we keep the codebase healthy.

## Reporting Bugs & Suggesting Features

Before opening a new issue, please search existing issues to avoid duplicates.

- **Bugs:** Include steps to reproduce, expected behavior, actual behavior, your OS, and Python version.
- **Features:** Describe the problem you're trying to solve and propose a solution if you have one.

Use the appropriate issue label (`bug` or `enhancement`) when creating the issue.

## Need Help?

If you get stuck or have questions, feel free to open an issue or reach out. We're happy to help you get your contribution merged!

Thank you for helping make SCCS better!
