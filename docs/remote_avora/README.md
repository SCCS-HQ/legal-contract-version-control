# remote_avora — Self-Hosted Avora Server

`remote_avora` is a self-hosted FastAPI server that stores Avora repositories and serves them over HTTP. It enables multiple users to clone, push, pull, and publish contract repositories, turning the local `avora` CLI into a collaborative version-control system.

## Features

- **Clone** — download a repository as a zip archive
- **Push** — upload new objects to a repository incrementally
- **Pull** — download missing objects and metadata from a remote
- **Publish** — upload a full repository for others to clone
- **Zip-slip protection** — all archive extractions are path-safe
- **Size limits** — per-file, total upload, and file count limits enforced

## Quick Reference

The `remote-avora` command provides 2 subcommands:

`serve`, `help`

## Dependencies

- [fastapi[standard]](https://fastapi.tiangolo.com/) — web framework including Uvicorn server

## Documentation

- [Installation](installation.md) — how to install `remote-avora` and start a server
- [Usage](usage.md) — endpoints, configuration, and operational details
- [Avora Documentation](https://avora-docx.github.io/Avora-Docx/) — full project documentation

## License

This project is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html).