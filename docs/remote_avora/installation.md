# Installation

## System Requirements

- Python 3.12 or later
- Sufficient disk space to store repositories (default: `./repos/` in the working directory)

## Install from PyPI

```bash
pip install remote-avora
```

This installs the `remote-avora` command-line tool and its dependencies.

## Verify Installation

```bash
remote-avora help
```

This prints the list of available commands.

## Dependencies

`remote-avora` installs the following Python package automatically:

| Package | Purpose |
|---------|---------|
| [fastapi[standard]](https://fastapi.tiangolo.com/) | Web framework and Uvicorn ASGI server |

The `[standard]` extra includes Uvicorn, which is required to run the server, along with Pydantic and other common FastAPI dependencies.

## Development Installation

To install from source for development:

```bash
git clone https://github.com/SCCS-HQ/legal-contract-version-control
cd legal-contract-version-control
pip install -e packages/remote_avora
```

## Updating

To upgrade to the latest version:

```bash
pip install --upgrade remote-avora
```

## Uninstalling

```bash
pip uninstall remote-avora
```