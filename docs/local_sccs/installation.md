# Installation

## System Requirements

- Python 3.12 or later
- A `.docx` file (Microsoft Word or compatible) for initializing repositories

## Install from PyPI

```bash
pip install sccs
```

This installs the `sccs` command-line tool and its dependencies.

## Verify Installation

```bash
sccs help
```

This prints the list of available commands and flags.

## Dependencies

`sccs` installs the following Python packages automatically:

| Package | Purpose |
|---------|---------|
| [mammoth](https://github.com/mammoth-js/mammoth) | Converts `.docx` to HTML for diffing |
| [requests](https://docs.python-requests.org/) | HTTP client for remote operations (push, pull, clone, publish) |
| [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/) | Parses HTML diff output |

## Development Installation

To install from source for development:

```bash
git clone https://github.com/SCCS-HQ/legal-contract-version-control
cd legal-contract-version-control
pip install -e packages/local_sccs
```

## Updating

To upgrade to the latest version:

```bash
pip install --upgrade sccs
```

## Uninstalling

```bash
pip uninstall sccs
```