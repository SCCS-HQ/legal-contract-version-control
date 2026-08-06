# Hash Consistency Review: `commands/`

## Scope

All 21 Python files under `commands/` were reviewed: `branch.py`, `clone.py`, `commit.py`, `config.py`, `constants_classes.py`, `diff.py`, `exceptions.py`, `help.py`, `init.py`, `log.py`, `merge.py`, `open.py`, `publish.py`, `pull.py`, `push.py`, `repository_layout.py`, `reset.py`, `revert.py`, `status.py`, `switch.py`, `utils.py`.

---

## Summary of Findings

| # | File                              | Severity           | Category                                               |
| - | --------------------------------- | ------------------ | ------------------------------------------------------ |
| 1 | `revert.py:52`                  | **Critical** | Runtime bug — undefined variable                      |
| 2 | `revert.py:19`                  | Medium             | Misleading parameter type/name                         |
| 3 | `revert.py:47–55`              | High               | Short hash used in internal logic; wrong arg order     |
| 4 | `open.py:63–67`                | Medium             | Short hash used in output filename before conversion   |
| 5 | `diff.py:254–269`              | Medium             | Downstream function accepts unvalidated short hash     |
| 6 | `repository_layout.py:343–400` | Low (design)       | No dedicated full-hash-string resolver at the boundary |

---

## Preferred Convention

- Internal code should always use either the full 64-character hash, or the full path to the corresponding commit file.
- Short hashes should only be accepted as direct user input or displayed to the user.
- After a user supplies a short hash, it should be converted to the corresponding full 64-character hash as early as possible. All subsequent logic should use the full hash.
- Any function or method that returns a hash should return the full 64-character hash.
- Any function or method that accepts a hash parameter should expect a full 64-character hash rather than a shortened version.
- Functions should not repeatedly convert between short and full hashes throughout the codebase. Conversion should occur at the boundary where user input is received.
- Short hashes should only be generated when presenting information to the user (CLI output, logs intended for users, status displays, etc.).

---

## Issue 1 — Runtime Bug: Undefined Variable

**File:** `commands/revert.py`
**Line:** 52

**Current behavior:**

```python
new_commit_hash = rw.commit_changes(
    c.REVERT_COMMIT_MESSAGE_TEMPLATE.format(commit_hash=hash)
)
```

The name `hash` is not defined anywhere in scope. This raises a `NameError` at runtime every time `sccs revert` is executed.

**Preferred behavior:**
The commit message should be formatted using a defined variable — specifically the full 64-character hash of the commit being reverted to, obtained after the early conversion from the user's short input.

**Why it matters:**
The command is completely broken. It cannot succeed regardless of hash-length conventions.

**Recommended change:**
After converting the user-supplied short hash to its full path, extract the full hash string (e.g., `full_hash_path.stem`) and use that variable in the template:

```python
commit_path = rd.hash_to_full_path(commit_hash, c.DOCX_DIR)
full_commit_hash = commit_path.stem
# ...
new_commit_hash = rw.commit_changes(
    c.REVERT_COMMIT_MESSAGE_TEMPLATE.format(commit_hash=full_commit_hash)
)
```

---

### Issue 2 — Misleading Parameter Type and Name

**File:** `commands/revert.py`
**Line:** 19

**Current behavior:**

```python
def revert(c: SCCSConstants, commit_hash: Path, rp: RepositoryPaths) -> None:
```

The parameter is named `commit_hash` but its type is `Path`. Inside the function it is used purely as a filesystem path (`commit_hash.is_file()`, `shutil.copy2(commit_hash, ...)`).

**Preferred behavior:**
A parameter representing a filesystem path should be named to reflect that (e.g., `commit_path` or `commit_file`). The name `commit_hash` implies a string hash value, which is misleading.

**Why it matters:**
Misleading naming makes the code harder to read and increases the risk of passing the wrong type to the function. It also obscures the distinction between a hash string and a file path, which is exactly the boundary that the hash-conversion convention is meant to clarify.

**Recommended change:**
Rename the parameter to `commit_path` (or `source_path`):

```python
def revert(c: SCCSConstants, commit_path: Path, rp: RepositoryPaths) -> None:
```

---

### Issue 3 — Short Hash Propagates into Internal Logic; Arguments Swapped

**File:** `commands/revert.py`
**Lines:** 47–55

**Current behavior:**

```python
def main(c: SCCSConstants, commit_hash: str, ...):
    # commit_hash is raw user input — may be a 10-char short hash
    full_hash = rd.hash_to_full_path(commit_hash, c.DOCX_DIR)   # returns a Path, not a hash string
    revert(c, full_hash, rp)

    new_commit_hash = rw.commit_changes(
        c.REVERT_COMMIT_MESSAGE_TEMPLATE.format(commit_hash=hash)   # BUG: also see Issue 1
    )

    print_revert_confirmation_message(c, new_commit_hash, commit_hash)
```

Three problems exist here:

1. **Short hash used in the revert commit message.** The `REVERT_COMMIT_MESSAGE_TEMPLATE` embeds `commit_hash` into the message stored in history metadata. If the user entered a short hash, a truncated value is permanently written into commit metadata.
2. **Variable named `full_hash` is actually a `Path`.** After calling `hash_to_full_path`, the result is a filesystem path, not a hash string. The name `full_hash` is misleading.
3. **Arguments to `print_revert_confirmation_message` are swapped.** The function signature is:

   ```python
   def print_revert_confirmation_message(c, commit_hash: str, new_commit_hash: str)
   ```

   and the template is `"Document successfully reverted to commit '{commit_hash}' on commit '{new_commit_hash}'."`
   But the call passes `(c, new_commit_hash, commit_hash)` — i.e., the new revert-commit hash is passed where the old (target) commit hash should be, and the user's raw input is passed where the new hash should be. The displayed message is semantically inverted.

**Preferred behavior:**

- Convert the user-supplied hash to its full 64-character form immediately upon entry.
- Use the full hash in all internal logic: commit messages, metadata writes, confirmation output.
- Pass arguments to `print_revert_confirmation_message` in the correct order.

**Why it matters:**
The convention states that short hashes should be accepted only at the user-input boundary and converted to full hashes immediately. Using a short hash in commit metadata corrupts the historical record with a value that is ambiguous. Swapped arguments produce a misleading CLI message.

**Recommended change:**
In `revert.py` `main`:

```python
def main(c: SCCSConstants, commit_hash: str, rd, rs, rp, rw):
    rs.target.set(rd.current_branch())
    rs.check_repository_layout()

    commit_path = rd.hash_to_full_path(commit_hash, c.DOCX_DIR)
    full_commit_hash = commit_path.stem           # 64-char string

    revert(c, commit_path, rp)

    new_commit_hash = rw.commit_changes(
        c.REVERT_COMMIT_MESSAGE_TEMPLATE.format(commit_hash=full_commit_hash)
    )

    print_revert_confirmation_message(c, full_commit_hash, new_commit_hash)
    rs.target.reset()
```

---

### Issue 4 — Short Hash Used in Output Filename Before Conversion

**File:** `commands/open.py`
**Lines:** 63–67

**Current behavior:**

```python
def main(c: SCCSConstants, commit_hash: str, rd: RepositoryData, rs: RepositoryStatus) -> None:
    # ...
    output_file_name = Path(c.OPEN_OUTPUT_FILE_NAME_TEMPLATE.format(commit_hash=commit_hash)).with_suffix(c.DOCX_EXTENSION)
    validate_commit_hash(c, commit_hash)
    copy_file_commit(rd.hash_to_full_path(commit_hash, c.DOCX_DIR), output_file_name)
    print_rewrite_confirmation_message(c, commit_hash, output_file_name)
```

The output filename `Opened_DOCX_Commit_{commit_hash}.docx` is constructed on line 63 using the raw user-supplied `commit_hash` **before** validation and conversion on line 65. If the user enters a short hash, the generated filename contains the truncated hash, not the full hash.

**Preferred behavior:**
Validate and convert the hash first, then use the full hash for any internal artifact (including output filenames). The short hash should only appear in user-facing display strings.

**Why it matters:**
Output filenames are artifacts produced by the tool. Embedding a short hash in a filename means the filename is ambiguous and non-canonical. If a user later tries to reference that file using its stem as a commit identifier, the short hash may be ambiguous.

**Recommended change:**
Move validation and conversion before filename construction, and use the full hash:

```python
def main(c: SCCSConstants, commit_hash: str, rd: RepositoryData, rs: RepositoryStatus) -> None:
    rs.target.set(rd.current_branch())
    rs.check_repository_layout()
    rs.raise_for_uncommitted_changes()

    validate_commit_hash(c, commit_hash)
    commit_path = rd.hash_to_full_path(commit_hash, c.DOCX_DIR)
    full_commit_hash = commit_path.stem

    output_file_name = Path(c.OPEN_OUTPUT_FILE_NAME_TEMPLATE.format(commit_hash=full_commit_hash)).with_suffix(c.DOCX_EXTENSION)
    copy_file_commit(commit_path, output_file_name)
    print_rewrite_confirmation_message(c, full_commit_hash, output_file_name)
    rs.target.reset()
```

---

### Issue 5 — Downstream Function Accepts Unvalidated Short Hash

**File:** `commands/diff.py`
**Lines:** 254–269

**Current behavior:**

```python
def generate_diff_output(c: SCCSConstants, commit_hash: str, ri: RepositoryIO, rd: RepositoryData):
    commit_soup = convert_html_to_soup(c, rd.commit_file_bytes(commit_hash, c.HTML_DIR))
    # ...
```

And in `main`:

```python
def main(c, commit_hash: str, rd, rs, ri):
    # ...
    ri.write_diff_output(
        utils.wrap_html(c, str(strip_number_attribute(c, generate_diff_output(c, commit_hash, ri, rd))), ...)
    )
```

`commit_hash` is passed straight from user input into `generate_diff_output` without any early conversion. The underlying `commit_file_bytes` in `repository_layout.py` does accept both short and full hashes, but the convention states that any function accepting a hash parameter should expect a full 64-character hash. The conversion should happen at the boundary in `main`, not be deferred into a downstream helper.

**Preferred behavior:**
`main` should resolve the short hash to a full hash string immediately, then pass only the full hash to `generate_diff_output` and any further internal functions.

**Why it matters:**
If `generate_diff_output` is ever reused or tested independently, callers must know that it silently accepts short hashes. This leaks the user-input boundary concern into internal logic and makes the function contract unclear.

**Recommended change:**
In `diff.py` `main`, resolve the hash before calling `generate_diff_output`:

```python
def main(c: SCCSConstants, commit_hash: str, rd: RepositoryData, rs: RepositoryStatus, ri: RepositoryIO) -> None:
    rs.target.set(rd.current_branch())
    rs.check_repository_layout()
    rs.raise_for_uncommitted_changes()

    commit_path = rd.hash_to_full_path(commit_hash, c.HTML_DIR)
    full_commit_hash = commit_path.stem

    ri.write_diff_output(
        utils.wrap_html(c, str(strip_number_attribute(c, generate_diff_output(c, full_commit_hash, ri, rd))), c.DEFAULT_HTML_STYLES)
    )
    print_diff_success_message(c)
    rs.target.reset()
```

---

### Issue 6 — No Dedicated Full-Hash-String Resolver at the Boundary

**File:** `commands/repository_layout.py`
**Lines:** 343–370 (`hash_to_full_path`), 373–400 (`commit_file_bytes`)

**Current behavior:**
The two methods that resolve a user-supplied short hash to a canonical object both return non-hash types:

- `hash_to_full_path(commit, folder)` → `Path`
- `commit_file_bytes(commit, folder)` → `bytes`

Callers that need the full 64-character hash string must manually extract it via `.stem` on the returned `Path`. This logic is duplicated (or omitted) across commands and is error-prone — as evidenced by the `revert.py` bug where `full_hash` was treated as a hash string when it was actually a `Path`.

**Preferred behavior:**
Introduce a method on `RepositoryData` that resolves a short-or-full hash input to the canonical full 64-character hash string. This becomes the single boundary conversion point. All command `main` functions call it immediately after receiving user input.

**Why it matters:**
Without a single, well-defined boundary helper, every command that accepts a user-supplied hash must reimplement the same `Path` → stem extraction logic. This is exactly where the `revert.py` bug originated.

**Recommended change:**
Add to `RepositoryData` in `repository_layout.py`:

```python
def resolve_full_hash(self, commit: str, folder: str) -> str:
    """
    Accept a short or full commit hash from user input, resolve it to the
    canonical 64-character hash string, and return it.
    """
    path = self.hash_to_full_path(commit, folder)
    return path.stem
```

Then update all `main` functions that accept user-supplied hashes to call `resolve_full_hash` immediately:

- `revert.py:main` — call after receiving `commit_hash`
- `open.py:main` — call after receiving `commit_hash`
- `diff.py:main` — call after receiving `commit_hash`

This eliminates the repeated `path.stem` extraction scattered across commands and makes the conversion boundary explicit and centralized.

---

## Consistent Patterns (No Issues Found)

The following files handle hashes consistently:

- **`commit.py`** — `commit_changes()` returns a full 64-char hash; `print_commit_confirmation_message` truncates only for display (`sha_hash[:c.COMMIT_HASH_DISPLAY_LENGTH]`).
- **`log.py`** — History keys are full hashes from metadata; truncation to 10 chars happens only in `print_log` for CLI output.
- **`init.py`** — `create_commit_sha_hash` returns a full SHA-256 hex digest; all downstream functions (`write_history_data`, `write_commit_message_data`, `write_hashed_file_commit_data`, `copy_document_to_objects_as_docx_and_html`) consume the full hash string.
- **`switch.py`**, **`reset.py`**, **`merge.py`** — Use `rd.latest_commit()` which returns a full hash from history metadata; no user-supplied hash involved.
- **`push.py`**, **`pull.py`**, **`publish.py`**, **`clone.py`** — No direct commit-hash user input; operate on repository objects or URLs.
- **`branch.py`** — No commit hash parameters.
- **`repository_layout.py: RepositoryWrite.commit_changes`** — Generates and returns a full 64-char hash; all metadata writes use the full hash.

---

## Recommended Shared Helper

Introduce `RepositoryData.resolve_full_hash(commit: str, folder: str) -> str` in `commands/repository_layout.py` (around line 370, near `hash_to_full_path`). Use it at the user-input boundary in:

- `commands/revert.py:main`
- `commands/open.py:main`
- `commands/diff.py:main`

This enforces the convention that the conversion from short to full happens once, at the boundary, and all subsequent internal logic works exclusively with full 64-character hashes.
