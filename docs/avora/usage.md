# Usage

## Command Reference

All commands are run within an Avora repository directory (the directory created by `avora init`).

### `avora init <document_path>`

Initialize a new Avora repository from a `.docx` file. The original document is copied into the repository and the first commit is created automatically with the message "Initial commit (This is a default commit message for the initial version)". You will be prompted for your name and email.

```bash
avora init contract.docx
cd contract
```

### `avora commit -m <message>`

Commit uncommitted changes to the current branch with a descriptive message.

```bash
avora commit -m "Updated liability section"
```

### `avora branch <subcommand> [branch_name]`

Manage branches. Three subcommands:

```bash
# Create a new branch from the current branch
avora branch create feature-x

# Delete an existing branch (cannot delete the current branch or 'main')
avora branch delete feature-x

# List all branches (current branch is marked with *)
avora branch list
```

### `avora switch <branch_name>`

Switch the working document to a different branch.

```bash
avora switch feature-x
```

### `avora merge <branch_name>`

Merge the specified branch into the current branch. Cannot merge a branch into itself.

```bash
avora merge feature-x
```

### `avora log`

Print the commit history of the current branch, including commit identifier, author, date, and message for each commit.

```bash
avora log
```

### `avora diff <commit_identifier>`

Show differences between the current document and a past commit. The diff is rendered as HTML and written to `diff.html` in the repository root. Accepts a 10-character short identifier or a full 64-character hash.

```bash
avora diff a1b2c3d4e5
```

### `avora open <commit_identifier>`

Open a past commit as a separate `.docx` file. The original commit is not modified; a new file is created for editing.

```bash
avora open a1b2c3d4e5
```

### `avora revert <commit_identifier>`

Revert the current document to the specified commit, creating a new commit with the reverted content.

```bash
avora revert a1b2c3d4e5
```

### `avora reset`

Delete all uncommitted changes and restore the document to the latest commit.

```bash
avora reset
```

### `avora status`

Check the status of the current document for uncommitted changes.

```bash
avora status
```

### `avora config <key> <value>`

Configure repository settings. Accepted keys:

| Key | Description |
|-----|-------------|
| `remote` | The base URL of the remote Avora server (stored per-repository) |
| `name` | The author name for commits (stored globally in `~/.config/avora/config.json`) |
| `email` | The author email for commits (stored globally in `~/.config/avora/config.json`) |

```bash
avora config name "Jane Doe"
avora config email "jane@example.com"
avora config remote "http://192.168.1.10"
```

The remote URL must use `http` or `https` and will be automatically appended with `/repos/<repository-name>/`. The `name` and `email` values are stored globally and shared across all repositories.

### `avora clone <url>`

Clone a hosted Avora repository. The URL must end with `/clone` (e.g., `http://host:8000/repos/<repository-name>/clone`).

```bash
avora clone http://192.168.1.10/repos/my-repo/clone
```

### `avora push`

Push local changes to the configured remote repository. Fails if the remote has commits the local repository is missing.

```bash
avora push
```

### `avora pull`

Pull changes from the configured remote repository and merge them into the local repository. Fails if there are uncommitted changes in the working tree.

```bash
avora pull
```

### `avora publish`

Publish a local repository to the configured remote server so others can clone it.

```bash
avora publish
```

### `avora help`

Print the list of available commands and flags.

```bash
avora help
```

## Flags

| Flag | Description |
|------|-------------|
| `-d`, `--debug` | Run in debug mode; does not catch exceptions or `AvoraException` |

## Commit Identifiers

Commit identifiers are SHA-256 hashes derived from the program start timestamp, commit message, and author. Two forms are accepted:

- **Short** — the first 10 characters, sufficient for most commands
- **Full** — the complete 64-character hash, required when short identifiers are ambiguous

Note: The timestamp component is the program start time (when the `avora` command was invoked), not the individual commit time.

## Repository Layout

Each Avora repository contains a `.avora/` directory:

- `metadata.json` — branch information, current branch, and commit order
- `objects/docx/` — stored document versions keyed by commit identifier
- `objects/html/` — HTML versions for diffing
- `objects/view_html/` — standalone HTML pages for viewing commits

## Workflow Example

```bash
# Initialize
avora init contract.docx
cd contract

# Configure author
avora config name "Jane Doe"
avora config email "jane@example.com"

# Make edits and commit
avora commit -m "Initial draft"

# Create a revision branch
avora branch create revisions
avora switch revisions

# Make more edits
avora commit -m "Added exhibits"

# Merge back to main
avora switch main
avora merge revisions

# View history
avora log

# Push to remote
avora push
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Expected error (invalid command, missing file, etc.) |
| 2 | Unexpected error (also occurs without `--debug`) |