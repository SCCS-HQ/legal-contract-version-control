# SCCS — Simple Contracts Communication System

SCCS is a version-control system purpose-built for legal contracts. It tracks changes to `.docx` documents through a Git-like workflow — branches, commits, logs, diffs, and merges — without requiring users to leave their word processor.

## Overview

The project is split into two packages:

- **`local_sccs`** — the command-line client used to initialize repositories, commit changes, branch, merge, and push/pull from a remote host.
- **`remote_sccs`** — a self-hosted FastAPI server that stores repositories and serves them over HTTP so multiple users can clone, push, and pull.

## Features

- Initialize a new contract repository from a `.docx` file (`sccs init`)
- Commit changes with descriptive messages
- Branch, merge, and switch between branches
- View commit history (`sccs log`) and diffs (`sccs diff`)
- Revert a document to any past commit
- Reset uncommitted changes
- Push and pull repositories to/from a self-hosted remote server
- Publish a local repository for others to clone

## Packages

### local_sccs

The local command-line tool. Install from PyPI with:

```bash
pip install sccs
```

Once installed, the `sccs` command is available. Run `sccs help` for the full list of commands.

**Commands:** `init`, `commit`, `branch`, `merge`, `switch`, `clone`, `push`, `pull`, `publish`, `log`, `diff`, `open`, `revert`, `reset`, `status`, `config`, `help`

### remote_sccs

The self-hosted server. Install from PyPI with:

```bash
pip install remote-sccs
```

Start a server with:

```bash
remote-sccs serve
```

The server exposes endpoints for cloning, pushing, pulling, and publishing repositories. By default it serves from the current directory and stores repositories under `repos/`.

## Quick Start

### Initialize a local repository

```bash
sccs init contract.docx
cd contract
```

### Make and commit changes

```bash
sccs commit -m "Updated liability section"
```

### Host a remote server

```bash
remote-sccs serve
```

### Clone from a remote

```bash
sccs clone http://<server-ip>/repos/my-repo/clone
```

## Repository Layout

Each initialized SCCS repository contains a `.sccs/` directory with:

- `metadata.json` — branch information, current branch, and commit order
- `config.json` — repository configuration (remote URL, author name/email)
- `branches/` — one commit file per branch
- `objects/` — stored document versions keyed by byte hash
- `history/` — per-branch commit logs

## Documentation

Full documentation is available at [SCCS Documentation](https://sccs-hq.github.io/legal-contract-version-control/).

## Dependencies

- **local_sccs** — depends on `mammoth`, `requests`, and `beautifulsoup4`
- **remote_sccs** — depends on `fastapi[standard]`

## License

This project is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html).
