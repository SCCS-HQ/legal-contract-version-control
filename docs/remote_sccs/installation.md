# Installation

## System Requirements

- Python 3.12 or later
- Sufficient disk space to store repositories (default: `./repos/` in the working directory)

## Install from PyPI

```bash
pip install remote-sccs
```

This installs the `remote-sccs` command-line tool and its dependencies.

## Verify Installation

```bash
remote-sccs help
```

This prints the list of available commands.

## Dependencies

`remote-sccs` installs the following Python package automatically:

| Package | Purpose |
|---------|---------|
| [fastapi[standard]](https://fastapi.tiangolo.com/) | Web framework and Uvicorn ASGI server |

The `[standard]` extra includes Uvicorn, which is required to run the server, along with Pydantic and other common FastAPI dependencies.

## Development Installation

To install from source for development:

```bash
git clone https://github.com/SCCS-HQ/legal-contract-version-control
cd legal-contract-version-control
pip install -e packages/remote_sccs
```

## Updating

To upgrade to the latest version:

```bash
pip install --upgrade remote-sccs
```

## Uninstalling

```bash
pip uninstall remote-sccs
```