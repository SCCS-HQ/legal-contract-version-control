# 📜 SCCS Commands Documentation

This documentation covers all available commands in the **SCCS (Specialized Contract Control System)** — a version control and diffing tool designed specifically for `.docx` legal contracts and documents.

---

## 📋 Table of Contents

1. [Branch](#-branch) — Create, delete, and manage branches
2. [Clone](#-clone) — Clone a hosted repository
3. [Commit](#-commit) — Commit changes to the repository
4. [Config](#-config) — Configure repository settings
5. [Diff](#-diff) — Display differences between commits
6. [Help](#-help) — Display help information
7. [Init](#-init) — Initialize a new repository
8. [Log](#-log) — View commit history
9. [Merge](#-merge) — Merge branches together
10. [Open](#-open) — Open a historical commit
11. [Publish](#-publish) — Publish repository to a hosting service
12. [Pull](#-pull) — Pull changes from remote repository
13. [Push](#-push) — Push changes to remote repository
14. [Reset](#-reset) — Discard uncommitted changes
15. [Revert](#-revert) — Revert to a previous commit
16. [Status](#-status) — Check for uncommitted changes
17. [Switch](#-switch) — Switch between branches

---

## 🌿 Branch

**Create, delete, and list branches within your repository.**

### Usage

```bash
sccs branch <subcommand> [branch-name]
```

### Subcommands

#### create

Creates a new branch based on the current branch.

**Usage:** `sccs branch create <branch-name>`

**Arguments:**

- `<branch-name>` — The name of the new branch to create

**Behavior:**

- The new branch inherits all commits and history from the current branch
- The newly created branch becomes the current branch
- Branch names are sanitized to be valid directory names
- Fails if a branch with the same name already exists

**Example:**

```bash
sccs branch create feature-update
```

#### delete

Deletes an existing branch.

**Usage:** `sccs branch delete <branch-name>`

**Arguments:**

- `<branch-name>` — The name of the branch to delete

**Behavior:**

- Cannot delete the current branch (switch branches first)
- Removes the branch from all metadata files
- Fails if the branch does not exist
- Changes are rolled back if deletion fails partway through

**Example:**

```bash
sccs branch delete old-version
```

#### list

Displays all branches in the repository, marking the current branch with an asterisk.

**Usage:** `sccs branch list`

**Arguments:** None

**Behavior:**

- Lists all branches in alphabetical order
- Marks the current branch with `*` (current)
- Other branches are prefixed with spaces

**Example Output:**

```
Branches:

  backup-branch
  feature-update
* main (current)
```

---

## 📥 Clone

Download a hosted SCCS repository to your local machine.

### Usage

```bash
sccs clone <url>
```

### Arguments

- `<url>` — The hosted repository URL (must be a valid HTTP/HTTPS URL)

### Behavior

- Automatically appends `/clone` to the URL if not present
- Downloads and extracts the repository as a zip file
- Creates a folder named after the repository in the current directory
- Requires internet connectivity

### Example

```bash
sccs clone https://api.example.com/legal-contracts
```

---

## ✅ Commit

Save the current document changes as a new commit in the repository.

### Usage

```bash
sccs commit "<commit-message>"
```

### Arguments

- `<commit-message>` — A descriptive message describing the changes (required, cannot be empty)

### Behavior

- Creates a snapshot of the current document state
- Generates a unique SHA-256 commit hash
- Stores both `.docx` and `.html` versions
- Commits are immutable once created
- Records the author name and email (from config) and timestamp

### Example

```bash
sccs commit "Updated Section 3 terms and conditions"
```

---

## ⚙️ Config

Configure repository-specific settings.

### Usage

```bash
sccs config <key> <value>
```

### Arguments

- `<key>` — The configuration key to set (see valid keys below)
- `<value>` — The value to assign to the key

### Valid Configuration Keys

#### name

Your name, used to identify commits you make.

**Example:**

```bash
sccs config name "John Doe"
```

#### email

Your email address, used alongside your name in commit metadata.

**Example:**

```bash
sccs config email "john.doe@example.com"
```

#### remote

The URL of the remote hosting service for push/pull operations.

**Example:**

```bash
sccs config remote https://api.example.com/repos
```

### Behavior

- The remote value is automatically formatted to end with `/repos/<repository-name>`
- Remote URLs must start with `http://` or `https://`
- Configuration values are stored in `.sccs/config/config.json`

---

## 🔍 Diff

Generate an HTML redline document showing differences between two commits.

### Usage

```bash
sccs diff <commit-hash>
```

### Arguments

- `<commit-hash>` — The commit SHA hash (or first 10 characters) to compare against the current document

### Behavior

- Compares the historical commit with the current document
- Creates an HTML file named `redline.html` in the current directory
- Color-codes changes:
  - Deleted content appears with a `"deleted"` class (typically red strikethrough)
  - Inserted content appears with an `"inserted"` class (typically green highlight)
- Removes inline formatting tags to avoid duplication in the diff
- Can be opened in any web browser

### Example

```bash
sccs diff 5a3b2c1d9e
```

---

## ❓ Help

Display a list of all available SCCS commands.

### Usage

```bash
sccs help
```

### Arguments

None

### Behavior

- Prints a summary of all available commands with brief descriptions
- Useful as a quick reference guide

---

## 🚀 Init

Initialize a new SCCS repository for a `.docx` document.

### Usage

```bash
sccs init <file-path>
```

### Arguments

- `<file-path>` — The path to the `.docx` file to initialize

### Behavior

- Creates the `.sccs` directory structure
- Prompts for your name and email (used for commits)
- Moves the document into a repository directory
- Creates an initial commit with the document's current state
- Initializes the main branch
- Fails if the file has already been initialized or is not a `.docx` file

### Prompted Inputs

- `name` — Your full name
- `email` — Your email address

### Example

```bash
sccs init contract.docx
```

### Output

```
Enter your name: Jane Smith
Enter your email: jane.smith@example.com
SCCS initialization complete.
```

---

## 📖 Log

Display the commit history for the current branch.

### Usage

```bash
sccs log
```

### Arguments

None

### Behavior

- Shows all commits in the current branch in reverse chronological order
- Displays for each commit:
  - First 10 characters of the SHA hash
  - Commit author
  - Timestamp (ISO 8601 format)
  - Commit message
- Each commit entry is separated by a dashed line

### Example Output

```
------------------------------
Commit File: 5a3b2c1d9e
Author: John Doe <john.doe@example.com>
Date: 2025-01-15T14:30:45.123456
Message: Updated liability clause
------------------------------
```

---

## 🔗 Merge

Merge another branch into the current branch.

### Usage

```bash
sccs merge <branch-name>
```

### Arguments

- `<branch-name>` — The name of the branch to merge into the current branch

### Behavior

- Copies all commit history from the source branch to the current branch
- Overwrites the current document with the source branch's latest version
- Creates an automatic commit with a merge message
- Cannot merge a branch into itself
- Fails if the target branch does not exist
- Requires no uncommitted changes

### Example

```bash
sccs merge feature-update
```

### Output

```
Successfully merged branch 'feature-update' into branch 'main'.
```

---

## 🗂️ Open

Open a historical commit and update the current document to that version.

### Usage

```bash
sccs open <commit-hash>
```

### Arguments

- `<commit-hash>` — The SHA hash (or first 10 characters) of the commit to open

### Behavior

- Displays a confirmation prompt before overwriting the current document
- Replaces the current document with the selected historical version
- Does not create a new commit (use after this if you want to save changes)
- Fails if the commit does not exist
- Requires no uncommitted changes

### Example

```bash
sccs open 5a3b2c1d9e
```

### Confirmation Prompt

```
Are you sure you want to overwrite './contract.docx' with the contents of 'commit_5a3b2c1d9e'?
This action will replace the current content of the .docx file. (Y/N):
```

---

## 📤 Publish

Publish the repository to a remote hosting service.

### Usage

```bash
sccs publish
```

### Arguments

None

### Behavior

- Requires a remote URL configured via `sccs config remote`
- Compresses the entire repository into a zip file
- Sends the zip to the remote server via HTTP POST
- Resets the current branch to main before publishing
- Provides status code and confirmation message

### Example

```bash
sccs publish
```

### Output

```
Publishing repository to https://api.example.com/repos/contract...

Status Code: 200

Repository published successfully to https://api.example.com/repos/contract
```

---

## 📥 Pull

Fetch and merge changes from a remote repository.

### Usage

```bash
sccs pull
```

### Arguments

None

### Behavior

- Requires a remote URL configured via `sccs config remote`
- Compares local commits with remote commits
- Downloads only the missing commit objects
- Merges remote history into the local repository
- Updates the current document to match the remote

### Example

```bash
sccs pull
```

### Output

```
Pulling repository from https://api.example.com/repos/contract...

Status Code: 200

Repository pulled successfully from https://api.example.com/repos/contract
```

---

## 📤 Push

Send local changes to a remote repository.

### Usage

```bash
sccs push
```

### Arguments

None

### Behavior

- Requires a remote URL configured via `sccs config remote`
- Compares local and remote commit objects
- Uploads only commits that the remote is missing
- Fails if the local repository is missing commits from the remote
- Clears the `updated_branches` list after successful push

### Example

```bash
sccs push
```

### Output

```
Pushing changes to remote repository at https://api.example.com/repos/contract...

Status code: 200

Changes pushed successfully to https://api.example.com/repos/contract/push
```

---

## 🔄 Reset

Discard all uncommitted changes and restore the document to the latest commit.

### Usage

```bash
sccs reset
```

### Arguments

None

### Behavior

- Replaces the current document with the latest commit on the current branch
- Fails if there are no uncommitted changes to reset
- Irreversible operation (use with caution)

### Example

```bash
sccs reset
```

### Output

```
All uncommitted changes have been deleted. The document has been reset to the latest commit.
```

---

## ⏮️ Revert

Create a new commit that reverts the document to a previous commit state.

### Usage

```bash
sccs revert <commit-hash>
```

### Arguments

- `<commit-hash>` — The SHA hash (or first 10 characters) of the commit to revert to

### Behavior

- Reverts the document to the state of the specified commit
- Automatically creates a new commit with message `Revert to commit '<hash>'`
- The revert is saved as a new commit in the history
- Different from reset because it preserves history (creates a new commit)
- Fails if the specified commit does not exist
- Requires no uncommitted changes

### Example

```bash
sccs revert 5a3b2c1d9e
```

### Output

```
Document successfully reverted to commit '5a3b2c1d' on commit '8f4e9d2c1b'.
```

---

## 📊 Status

Check for uncommitted changes in the current document.

### Usage

```bash
sccs status
```

### Arguments

None

### Behavior

- Compares the current document with the latest commit
- Uses binary hash comparison (detects any changes, no matter how small)
- Prints one of two messages:
  - `"Uncommitted changes detected."` — if the document has been modified
  - `"No uncommitted changes detected."` — if the document matches the latest commit

### Example

```bash
sccs status
```

### Output

```
Uncommitted changes detected.
```

---

## 🔀 Switch

Switch between branches.

### Usage

```bash
sccs switch <branch-name>
```

### Arguments

- `<branch-name>` — The name of the branch to switch to

### Behavior

- Updates metadata to mark the specified branch as current
- Replaces the current document with the latest commit from the target branch
- Fails if the target branch does not exist
- Fails if there are uncommitted changes (commit or reset first)
- The switched branch becomes the active branch for all future operations

### Example

```bash
sccs switch feature-update
```

### Output

```
Successfully switched to branch 'feature-update'.
```

---

## 🎯 Quick Start Guide

### 1. Initialize a New Repository

```bash
sccs init my_contract.docx
```

### 2. Configure Your Identity

```bash
sccs config name "Your Name"
sccs config email "your.email@example.com"
```

### 3. Create Your First Commit

```bash
sccs commit "Initial version of contract"
```

### 4. Check Status

```bash
sccs status
```

### 5. View Commit History

```bash
sccs log
```

### 6. Create and Switch to a New Branch

```bash
sccs branch create revision-v2
sccs switch revision-v2
```

### 7. Make Changes and Commit

```bash
# (Edit your document)
sccs commit "Updated payment terms"
```

### 8. View Differences

```bash
sccs diff <previous-commit-hash>
```

### 9. Merge Back to Main

```bash
sccs switch main
sccs merge revision-v2
```

### 10. Configure Remote and Push

```bash
sccs config remote https://api.example.com
sccs push
```

---

## 📝 Notes

- All commit hashes are SHA-256 hexadecimal strings; only the first 10 characters are typically needed
- Document `.docx` files are automatically converted to `.html` for diffing purposes
- All timestamps are stored in ISO 8601 format
- Branch names and document names are sanitized to be valid directory names
- The `.sccs` folder contains all version control metadata and should not be manually edited
