# Changelog

All notable changes to Avora are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.2.0.dev1](https://github.com/Avora-Docx/Avora-Docx/releases/tag/v0-2-0-dev1) - 2026-11-23

### Security

- Fixed denial-of-service vulnerability in `push_upload` endpoint: added upload size bounding (100 MB limit) via `_read_upload_bounded` to prevent memory exhaustion from arbitrarily large uploads.

## [v0.1.2](https://github.com/Avora-Docx/Avora-Docx/releases/tag/v0-1-2-alpha) - 2026-11-20

### Changed

- Updated documentation links in `avora` and `remote_avora` READMEs to point to the new [Avora-Docx](https://avora-docx.github.io/Avora-Docx/) site.

## [v0.1.1](https://github.com/Avora-Docx/Avora-Docx/releases/tag/v0-1-1-alpha) - 2026-11-20

### Changed

- Updated documentation links and `site_url` to point to the new [Avora-Docx](https://avora-docx.github.io/Avora-Docx/) site.

## [v0.1.0](https://github.com/Avora-Docx/Avora-Docx/releases/tag/v0-1-0-alpha) - 2026-11-15

### Added

- Initial project scaffolding for the `avora` CLI and `remote_avora` server packages.
