# Usage

## Command Reference

All commands are run from within an SCCS repository directory (the directory created by `sccs init`).

### `sccs init <document_path>`

Initialize a new SCCS repository from a `.docx` file. The original document is copied into the repository and the first commit is created automatically. You will be prompted for your name and email.

```bash
sccs init contract.docx
cd contract
```

### `sccs commit -m <message>`

Commit uncommitted changes to the current branch with a descriptive message.

```bash
sccs commit -m "Updated liability section"
```

### `sccs branch <subcommand> [branch_name]`

Manage branches. Three subcommands:

```bash
# Create a new branch from the current branch
sccs branch create feature-x

# Delete an existing branch (cannot delete the current branch or 'main')
sccs branch delete feature-x

# List all branches (current branch is marked with *)
sccs branch list
```

### `sccs switch <branch_name>`

Switch the working document to a different branch.

```bash
sccs switch feature-x
```

### `sccs merge <branch_name>`

Merge the specified branch into the current branch. Cannot merge a branch into itself.

```bash
sccs merge feature-x
```

### `sccs log`

Print the commit history of the current branch, including commit identifier, author, date, and message for each commit.

```bash
sccs log
```

### `sccs diff <commit_identifier>`

Show differences between the current document and a past commit. The diff is rendered as HTML and opened in a browser. Accepts a 10-character short identifier or a full 64-character hash.

```bash
sccs diff a1b2c3d4e5
```

### `sccs open <commit_identifier>`

Open a past commit as a separate `.docx` file. The original commit is not modified; a new file is created for editing.

```bash
sccs open a1b2c3d4e5
```

### `sccs revert <commit_identifier>`

Revert the current document to the specified commit, creating a new commit with the reverted content.

```bash
sccs revert a1b2c3d4e5
```

### `sccs reset`

Delete all uncommitted changes and restore the document to the latest commit.

```bash
sccs reset
```

### `sccs status`

Check the status of the current document for uncommitted changes.

```bash
sccs status
```

### `sccs config <key> <value>`

Configure repository settings. Accepted keys:

| Key | Description |
|-----|-------------|
| `remote` | The base URL of the remote SCCS server |
| `name` | The author name for commits |
| `email` | The author email for commits |

```bash
sccs config name "Jane Doe"
sccs config email "jane@example.com"
sccs config remote "http://192.168.1.10"
```

The remote URL must use `http` or `https` and will be automatically appended with `/repos/<repository-name>/`.

### `sccs clone <url>`

Clone a hosted SCCS repository. The URL must end with `/repos/<repository-name>/clone`.

```bash
sccs clone http://192.168.1.10/repos/my-repo/clone
```

### `sccs push`

Push local changes to the configured remote repository. Fails if the remote has commits the local repository is missing.

```bash
sccs push
```

### `sccs pull`

Pull changes from the configured remote repository and merge them into the local repository.

```bash
sccs pull
```

### `sccs publish`

Publish a local repository to the configured remote server so others can clone it.

```bash
sccs publish
```

### `sccs help`

Print the list of available commands and flags.

```bash
sccs help
```

## Flags

| Flag | Description |
|------|-------------|
| `-d`, `--debug` | Run in debug mode; does not catch exceptions or `SCCSException` |

## Commit Identifiers

Commit identifiers are SHA-256 hashes derived from the commit timestamp, message, and author. Two forms are accepted:

- **Short** — the first 10 characters, sufficient for most commands
- **Full** — the complete 64-character hash, required when short identifiers are ambiguous

## Repository Layout

Each SCCS repository contains a `.sccs/` directory:

- `metadata.json` — branch information, current branch, and commit order
- `config.json` — repository configuration (remote URL, author name/email)
- `branches/` — one commit file per branch
- `objects/docx/` — stored document versions keyed by commit identifier
- `objects/html/` — HTML versions for diffing
- `objects/view_html/` — standalone HTML pages for viewing commits
- `history/` — per-branch commit logs

## Workflow Example

```bash
# Initialize
sccs init contract.docx
cd contract

# Configure author
sccs config name "Jane Doe"
sccs config email "jane@example.com"

# Make edits and commit
sccs commit -m "Initial draft"

# Create a revision branch
sccs branch create revisions
sccs switch revisions

# Make more edits
sccs commit -m "Added exhibits"

# Merge back to main
sccs switch main
sccs merge revisions

# View history
sccs log

# Push to remote
sccs push
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Expected error (invalid command, missing file, etc.) |
| 2 | Unexpected error (only when running without `--debug`) |