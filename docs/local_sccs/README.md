# local_sccs — Simple Contracts Communication System

`local_sccs` is the command-line client for SCCS (Simple Contracts Communication System), a version-control system purpose-built for legal contracts. It tracks changes to `.docx` documents through a Git-like workflow — branches, commits, logs, diffs, and merges — without requiring users to leave their word processor.

## Features

- Initialize a new contract repository from a `.docx` file
- Commit changes with descriptive messages
- Branch, merge, and switch between branches
- View commit history and diffs
- Revert a document to any past commit
- Reset uncommitted changes
- Push and pull repositories to/from a self-hosted remote server
- Publish a local repository for others to clone

## Quick Reference

The `sccs` command provides 17 subcommands covering the full version-control lifecycle:

`init`, `commit`, `branch`, `merge`, `switch`, `clone`, `push`, `pull`, `publish`, `log`, `diff`, `open`, `revert`, `reset`, `status`, `config`, `help`

## Dependencies

- [mammoth](https://github.com/mammoth-js/mammoth) — converts `.docx` to HTML for diffing
- [requests](https://docs.python-requests.org/) — HTTP client for remote operations
- [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/) — parses HTML diff output

## Documentation

- [Installation](installation.md) — how to install `sccs` and set up your environment
- [Usage](usage.md) — command reference, examples, and workflows
- [SCCS Documentation](https://sccs-hq.github.io/legal-contract-version-control/) — full project documentation

## License

This project is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html).