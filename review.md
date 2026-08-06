# Review: `commands/` Folder

## Scope

Every file in `commands/` was reviewed for consistency, readability, maintainability, and testability. Issues are grouped below.

---

## 1. `commands/config.py` — Line 77

**Category:** Consistency
`main(c, key, value, rp, rd, rs, rw)` places `rp` before `rd`, but every other multi-repo-object `main` orders them as `rd, rs, rp, rw/ri`.
**Preferred pattern:** `commands/publish.py:102` — `def main(c, rd, rs, rp, rw)`.
**Why it matters:** Inconsistent ordering increases the risk of argument mismatches.
**Recommended change:** Reorder to `def main(c, key, value, rd, rs, rp, rw)`.

---

## 2f. `commands/diff.py` — Line 28

**Category:** Readability
`for i in enumerate(soup.find_all()):` then accesses `i[1]` and `i[0]`.
**Preferred pattern:** `commands/branch.py:121` iterates directly over values.
**Why it matters:** Tuple-indexing obscures intent.
**Recommended change:** Unpack as `for idx, tag in enumerate(soup.find_all()):`.

---

## 3f. `commands/merge.py` — Line 40

**Category:** Consistency
`raise exceptions.FileCopyError` is missing `from e`, while `copy_repo_document` at line 54 uses `raise exceptions.FileCopyError from e`.
**Preferred pattern:** `commands/branch.py:74,89`, `commands/open.py:39`, `commands/revert.py:32`, `commands/switch.py:58`.
**Why it matters:** Loses the original traceback.
**Recommended change:** Change to `raise exceptions.FileCopyError(...) from e`.

---

## 4nf. `commands/commit.py` — Lines 17–23

**Category:** Consistency / Testability
`print_commit_confirmation_message` wraps `print()` in `try/except`, which no other `print_*` function does.
**Preferred pattern:** `commands/branch.py:147-156`, `commands/status.py:15-20`, `commands/pull.py:45-49` call `print()` directly.
**Why it matters:** `print()` rarely raises; extra `try/except` adds dead weight.
**Recommended change:** Remove the `try/except` and call `print()` directly.

---

## 5f. `commands/push.py` — Lines 27, 56

**Category:** Consistency
`get_matching_file_paths` and `compare_hash_lists` return untyped `list`.
**Preferred pattern:** `commands/diff.py:53` — `def tags_to_list(soup: BeautifulSoup) -> list[str]:`.
**Why it matters:** Missing type hints reduce IDE support.
**Recommended change:** Add return type annotations.

---

## 6f. `commands/publish.py` — Line 68 / `commands/push.py` — Line 150

**Category:** Consistency
`post_repo` validates the URL using `Path.cwd().name`, but `push_POST` uses `rp.repo_name`.
**Preferred pattern:** `commands/push.py:150` — `rp.repo_name`.
**Why it matters:** Two sources of truth can diverge.
**Recommended change:** Pass `rp` into `post_repo` and use `rp.repo_name`.

---

## 7nf. `commands/publish.py` — Lines 37–40

**Category:** Readability
`try: buffer = io.BytesIO()` is wrapped in `except Exception`, but `io.BytesIO()` never raises.
**Preferred pattern:** `commands/diff.py:119` creates `BeautifulSoup(...)` directly.
**Why it matters:** Dead error-handling obscures actual failure points.
**Recommended change:** Remove the `try/except` around `io.BytesIO()`.

---

## 8nf. `commands/config.py` — Line 17

**Category:** Consistency
`from urllib.parse import urlsplit, urljoin` is placed after local imports.
**Preferred pattern:** `commands/publish.py:8` places stdlib imports before local imports.
**Why it matters:** Inconsistent ordering reduces scannability.
**Recommended change:** Move the `urllib.parse` import above the local imports.

---

## 9nf. `commands/clone.py` — Lines 41–47

**Category:** Consistency
`request_repo` catches `requests.RequestException`, while every other HTTP wrapper in `commands/` catches `Exception`.
**Preferred pattern:** `commands/pull.py:25-28`.
**Why it matters:** Inconsistent exception granularity.
**Recommended change:** Either catch `Exception` for consistency, or update all HTTP wrappers to catch `requests.RequestException`.

---

## 10nf. `commands/diff.py` — Lines 83–170

**Category:** Maintainability / Readability
`delete_tag`, `replace_tag`, and `insert_tag` duplicate the same logic for decomposing `style` tags and appending CSS classes.
**Preferred pattern:** `commands/branch.py:94-111` extracts shared rollback logic into a helper.
**Why it matters:** Duplicated logic must be updated in three places.
**Recommended change:** Extract a helper like `_add_class(tag, class_name)` and `_remove_style_tags(soup)`.

---

## 11f. `commands/config.py` — Lines 40–43

**Category:** Readability / Maintainability
`validate_entered_value` contains `if repo_name is None: raise ...` after `repo_name = utils.clean_directory_name(repo_name)`, but `clean_directory_name` always returns a string.
**Preferred pattern:** No equivalent dead-code pattern exists in other validators.
**Why it matters:** Dead branches mislead readers.
**Recommended change:** Remove the `if repo_name is None` check.

---

## 12f. `commands/commit.py` — Line 41 / `commands/revert.py` — Lines 52–54

**Category:** Testability / Readability
`print_commit_confirmation_message(c, rw.commit_changes(...))` and `print_revert_confirmation_message(c, commit_hash, rw.commit_changes(...))` nest a mutating call inside a print argument.
**Preferred pattern:** `commands/branch.py:76` computes values first, then calls the print function.
**Why it matters:** Side effects in argument lists are harder to stub/mock.
**Recommended change:** Assign the result of `rw.commit_changes(...)` to a variable before printing.

---

## 13.f `commands/push.py` — Line 34

**Category:** Testability
`assert updated_branches is not None` uses `assert` for runtime validation. Python's `-O` flag disables asserts.
**Preferred pattern:** `commands/merge.py:184-186` uses explicit `if data is None:` checks.
**Why it matters:** Assertions can be stripped, causing non-deterministic behavior.
**Recommended change:** Replace with `if updated_branches is None: raise exceptions.InvalidMetadataError(...)`.

---

## 14f. `commands/diff.py` — Lines 64–80

**Category:** Readability / Maintainability
`get_data_number` includes `parsed_tag = i if hasattr(i, "attrs") else ...`, but `tag_list` is typed as `list[str]`. The `hasattr` branch is dead code.
**Preferred pattern:** `commands/diff.py:47-50` (`strip_number_attribute`) iterates directly over `soup.find_all()` without type branching.
**Why it matters:** Dead conditional logic obscures the function's actual behavior.
**Recommended change:** Parse every element with `BeautifulSoup(i, c.HTML_PARSER).find()` and remove the `hasattr` check.

---

## 15f. `commands/revert.py` — Lines 22, 53

**Category:** Readability / Maintainability
`rd.hash_to_full_path(commit_hash, c.DOCX_DIR)` is called twice: once in `revert()` and again inside the commit message template.
**Preferred pattern:** `commands/switch.py:78` resolves the path once and reuses it.
**Why it matters:** Duplicated resolution is wasteful and risks inconsistency.
**Recommended change:** Resolve the path once in `main` and pass the result to both `revert` and `print_revert_confirmation_message`.
