# Installation

## System Requirements

- Python 3.12 or later
- A `.docx` file (Microsoft Word or compatible) for initializing repositories

## Install from PyPI

```bash
pip install avora
```

This installs the `avora` command-line tool and its dependencies.

## Verify Installation

```bash
avora help
```

This prints the list of available commands and flags.

## Dependencies

`avora` installs the following Python packages automatically:

| Package | Purpose |
|---------|---------|
| [mammoth](https://github.com/mammoth-js/mammoth) | Converts `.docx` to HTML for diffing |
| [requests](https://docs.python-requests.org/) | HTTP client for remote operations (push, pull, clone, publish) |
| [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/) | Parses HTML diff output |

## Development Installation

To install from source for development:

```bash
git clone https://github.com/Avora-Docx/Avora-Docx
cd legal-contract-version-control
pip install -e packages/avora
```

## Updating

To upgrade to the latest version:

```bash
pip install --upgrade avora
```

## Uninstalling

```bash
pip uninstall avora
```