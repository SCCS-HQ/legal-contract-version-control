# Avora — Avora Version Control System

Avora is a version-control system purpose-built for legal contracts. It tracks changes to `.docx` documents through a Git-like workflow — branches, commits, logs, diffs, and merges — without requiring users to leave their word processor.

## Overview

The project is split into two packages:

- **`avora`** — the command-line client used to initialize repositories, commit changes, branch, merge, and push/pull from a remote host.
- **`remote_avora`** — a self-hosted FastAPI server that stores repositories and serves them over HTTP so multiple users can clone, push, and pull.

## Features

- Initialize a new contract repository from a `.docx` file (`avora init`)
- Commit changes with descriptive messages
- Branch, merge, and switch between branches
- View commit history (`avora log`) and diffs (`avora diff`)
- Revert a document to any past commit
- Reset uncommitted changes
- Push and pull repositories to/from a self-hosted remote server
- Publish a local repository for others to clone

## Packages

### avora

The local command-line tool. Install from PyPI with:

```bash
pip install avora
```

Once installed, the `avora` command is available. Run `avora help` for the full list of commands.

**Commands:** `init`, `commit`, `branch`, `merge`, `switch`, `clone`, `push`, `pull`, `publish`, `log`, `diff`, `open`, `revert`, `reset`, `status`, `config`, `help`

### remote_avora

The self-hosted server. Install from PyPI with:

```bash
pip install remote-avora
```

Start a server with:

```bash
remote-avora serve
```

The server exposes endpoints for cloning, pushing, pulling, and publishing repositories. By default it serves from the current directory and stores repositories under `repos/`.

## Quick Start

### Initialize a local repository

```bash
avora init contract.docx
cd contract
```

### Make and commit changes

```bash
avora commit -m "Updated liability section"
```

### Host a remote server

```bash
remote-avora serve
```

### Clone from a remote

```bash
avora clone http://<server-ip>/repos/my-repo/clone
```

## Repository Layout

Each initialized Avora repository contains a `.avora/` directory with:

- `metadata.json` — branch information, current branch, and commit order
- `objects/docx/` — stored document versions keyed by commit identifier
- `objects/html/` — HTML versions for diffing
- `objects/view_html/` — standalone HTML pages for viewing commits

## Documentation

Full documentation is available at [Avora Documentation](https://sccs-hq.github.io/legal-contract-version-control/).

## Dependencies

- **avora** — depends on `mammoth`, `requests`, and `beautifulsoup4`
- **remote_avora** — depends on `fastapi[standard]`

## License

This project is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html).