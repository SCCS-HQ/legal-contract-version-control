# Functions Using Global Variables (Not as Parameters)

| File      | Function                                        | Global Variable(s) Used                                                                                           | Line(s)  |
| --------- | ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | -------- |
| help.py   | `print_help()`                                | `MESSAGES_TO_PRINT` (fixed)                                                                                     | 19       |
| commit.py | `convert_docx_to_html()`                      | `utils.current_file_docx_path` (no default passed)                                                              | 14       |
| commit.py | `write_diff_html()`                           | `utils.default_html_styles` (default param)                                                                     | 106      |
| commit.py | `write_view_html()`                           | `utils.working_directory_path` (no default passed)                                                              | 109      |
| commit.py | `update_commit_log_history()`                 | calls `get_history_path()` w/o args → uses `utils.current_branch`                                            | 115      |
| commit.py | `update_commit_binary_hash_history()`         | calls `get_history_path()` w/o args → uses `utils.current_branch`                                            | 151      |
| diff.py   | `write_redline_html_file()`                   | `utils.wrap_html()` called directly (function uses `default_html_styles`)(ignore)                             | 131      |
| init.py   | `copy_document_to_objects_as_docx_and_html()` | `utils.default_html_styles`, `utils.wrap_html()`(fixed)                                                       | 125, 131 |
| log.py    | `print_log()`                                 | calls `get_log_data()` w/o args → uses `utils.working_directory_path`, `utils.current_branch` (fake issue) | 16       |
| open.py   | `confirm_before_proceeding()`                 | `utils.current_file_docx_path`, `utils.working_directory_path`  (fixed)                                      | 19       |
| open.py   | `check_changes()`                             | `utils.current_file_docx_path ` (fixed)                                                                                | 24       |
| open.py   | `copy_file_commit()`                          | `utils.current_file_docx_path` (fixed)                                                                                  | 31       |
| open.py   | `print_rewrite_confirmation_message()`        | `utils.current_file_docx_path` (fixed)                                                                                  | 39       |
| status.py | `print_changes_message_and_exit()`            | calls functions w/o args → uses `utils.current_branch`, `utils.hash_current_docx_binary()`                   | 40       |
| switch.py | `get_latest_commit_binary_hash()`             | `utils.working_directory_path`                                                                                  | 38       |
| switch.py | `get_latest_commit()`                         | `utils.working_directory_path`                                                                                  | 53       |
| switch.py | `check_commit()`                              | `utils.working_directory_path`                                                                                  | 67       |
| switch.py | `copy_commit_to_main()`                       | `utils.working_directory_path`                                                                                  | 71       |
| utils.py  | `wrap_html()`                                 | `default_html_styles` (default param)                                                                           | 173      |
| utils.py  | `hash_current_docx_binary()`                  | `current_file_docx_path` (default param)                                                                        | 176      |
| utils.py  | `get_current_branch()`                        | `current_branch_path` (default param)                                                                           | 189      |
| utils.py  | `get_branch_data()`                           | `current_branch_path` (default param)                                                                           | 202      |
| utils.py  | (module level)                                  | `current_branch`, `branch_data`                                                                               | 228, 230 |

## Summary

**Functions using globals without being passed as arguments:**

- **Direct variable references**: 10+ functions accessing `utils.working_directory_path`, `utils.current_file_docx_path`, etc.
- **Default parameters using globals**: 4 functions in `utils.py` use module-level globals as defaults
- **Indirect via function calls**: Functions calling others w/o arguments trigger globals (e.g., `get_log_data()` called w/o args uses `utils.current_branch`)
- **Module-level globals**: `current_branch` and `branch_data` are assigned at module level using function calls
