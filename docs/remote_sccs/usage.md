# Usage

## Starting the Server

```bash
remote-sccs serve
```

The server binds to all network interfaces (`0.0.0.0`) on port `8000`. On startup it prints the local IP address so other users on your network can reach it.

Repositories are stored under `./repos/` in the current working directory. This directory is created automatically on first start.

## Commands

### `remote-sccs serve`

Start the FastAPI server. Creates the `repos/` directory if needed, prints the accessible URL, and starts Uvicorn.

### `remote-sccs help`

Print the list of available commands.

## HTTP Endpoints

All endpoints are relative to the server base URL (e.g. `http://<host>:8000`).

### `GET /`

Easter egg endpoint. Returns `{"message": "Boo!"}`.

### `POST /repos/{repository_name}/publish`

Publish a new repository. Accepts a multipart form with:

| Field | Description |
|-------|-------------|
| `repository_name` | Name of the repository to create |
| `file` | A zip archive of the repository contents, named `<repository_name>.zip` |
| `data` | A JSON string containing `{"remote": "<url>"}` — the URL where the repository is hosted |

The repository is extracted into a staging directory with zip-slip protection, then atomically moved into place. Returns `{"message": "File published successfully", "repository_url": "<url>"}`.

**Limits:**
- Maximum 1000 files per zip
- Maximum 100 MB total upload size
- Maximum 10 MB per individual file

### `GET /repos/{repository_name}/clone`

Download a repository as a zip archive. The response includes a `Content-Disposition` header for browser download.

### `GET /repos/{repository_name}/push`

Returns the set of object identifiers currently stored in the remote repository. The local client uses this to determine which objects need to be uploaded.

### `POST /repos/{repository_name}/push`

Upload new objects to an existing repository. Accepts a zip archive named `<repository_name>.zip` containing only the changed objects. The archive is extracted into a staging copy of the repository, the metadata's `updated_branches` list is cleared, and the staging copy replaces the original atomically.

On failure the original repository is left untouched.

### `POST /repos/{repository_name}/pull`

Download missing objects and metadata. The request body is a JSON object:

```json
{ "objects": ["<commit_hash>", ...] }
```

 listing the object identifiers the local repository already has. The server responds with a zip archive containing only the objects the local is missing, plus the current `metadata.json`.

## Repository Name Validation

Repository names must match the pattern `^[A-Za-z0-9._-]+$` and cannot be `.` or `..`. This prevents path traversal and zip-slip attacks.

## Size and Count Limits

| Limit | Value |
|-------|-------|
| Max files per zip | 1000 |
| Max total upload size | 100 MB |
| Max individual file size | 10 MB |

| Constant | Default | Description |
|----------|---------|-------------|
| `REPOSITORIES_BASE_DIRECTORY` | `./repos` | Directory where repositories are stored |
| `NETWORK_IP` | `0.0.0.0` | Bind address |
| `PORT_8000` | `8000` | Listen port |
| `MAX_FILES_IN_ZIP` | `1000` | Max files per zip archive |
| `MAX_TOTAL_UPLOAD_SIZE` | `100 MB` | Max total upload size |
| `MAX_INDIVIDUAL_FILE_SIZE` | `10 MB` | Max individual file size |

## Client Configuration

On the client side, configure the remote URL with:

```bash
sccs config remote http://<server-ip>:8000
```

The client automatically appends `/repos/<repository-name>/` to construct full endpoint URLs.

## Workflow Example

```bash
# On the server host
remote-sccs serve
# Server prints: Your Remote-SCCS server will be accessible on your internet network at http://192.168.1.10:8000

# On the server host, publish a repository
sccs init contract.docx
cd contract
sccs config remote http://192.168.1.10:8000
sccs publish

# On a client machine, clone the repository
sccs clone http://192.168.1.10:8000/repos/contract/clone
cd contract

# Make changes and push
sccs commit -m "Client edits"
sccs push

# On the server host, pull changes
cd contract
sccs pull
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 2 | Unexpected error |