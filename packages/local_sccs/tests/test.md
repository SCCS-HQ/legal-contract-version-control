#4 — tests that pass even after you delete the behaviour
16 separate behaviours in utils.py and repository_layout.py are claimed by test names but never actually checked. I proved each one by deleting it from production and re-running: all 16 stayed green. A test that cannot fail is not protecting anything.

The 16, by area:

copy_latest_commit_document never restores the target branch (repository_layout.py:194)
mutate_updated_branches writes even when the mutation said "no change"
add_branch_metadata shares one dict instead of copying it
base_repository_url doesn't strip the trailing /
remove_branch_metadata doesn't fall back to main
commit_changes appends to updated_branches instead of de-duplicating
five .lower() calls for branch names — branch_exists, is_current_branch, add_branch_metadata, set_current_branch, remove_from_branches_list
working_directory doesn't chdir, and doesn't check that $PWD exists
entered_argument doesn't .strip()
two f.truncate() calls that can't be observed
Every one of them is one of three mistakes:

(a) The assertion checks a value when it needed to check a side effect. test_repository_io_mutate_updated_branches_does_not_write_if_mutation_returns_false (test_repository_layout.py:656) compares metadata.json before and after. If the code writes anyway, it re-saves identical data, so both dicts match and the test passes — even though the whole point of the test is that it must not write. You cannot detect a write by looking at the result of the write; you have to watch the write happen (a spy, or an mtime check).

(b) The test data never reaches the branch in the code. Every test passes "main" and "test" — already lowercase — so the five .lower() calls never matter. But branch names reach production raw from the command line (branch.py:30 reads sys.argv), so a user typing sccs branch create MyBranch hits exactly that code, untested. Same pattern: the remote URL has no trailing /, updated_branches starts empty, entered_argument is never given padded spaces.

(c) The assertion is vacuous — it confirms something already true. test_repository_layout.py:1758 removes main while main is current, then asserts current_branch == "main". It was "main" before the call, so the assertion holds whether or not the fallback works.

The two f.truncate() calls are different: they are dead code, not untested code. Both files are opened with mode "w", which already truncates, so the extra call does nothing. Delete it rather than test it.

#5 — one test depends on your shell's $PWD
test_working_directory_sets_cwd_to_pwd_if_cwd_raises (test_utils.py:123) patches Path.cwd to fail, then checks that working_directory recovers using $PWD. It never sets $PWD itself, so it uses whatever value your shell exported. Line 141-142 then compare against that inherited value.

So the same test file gives different results depending on how you launched it:

normal run36 passed
env -u PWD              1 failed
PWD=/no/such/dir        1 failed
There is a second, quieter problem. working_directory calls os.chdir for real (utils.py:84), so this test moves the cwd of the entire pytest process. That is invisible today only because the inherited $PWD happens to equal pytest's cwd. If they ever differ, the session's directory silently moves and every later test touching a relative path runs in the wrong place.

The fix is two lines — monkeypatch.setenv(PWD, <a real directory you created>) and monkeypatch.chdir(<another real directory>). The first makes the test independent of your shell; the second makes pytest restore the cwd afterwards so the production chdir cannot leak.

#7 — 43 constants are copied, and nothing checks the copies
test_constants.py re-declares 43 values that already exist in constants_classes.py, including multi-line blobs:

DEFAULT_HTML_STYLES (24 lines)
HTML_BOILERPLATE_TEMPLATE
INIT_COMMIT_MESSAGE
MAIN_BRANCH_NAME, JSON_INDENT, DOCUMENT_EXTENSION, METADATA_JSON, SCCS_DIRECTORY, UPDATED_BRANCHES_DICT_KEY, …
I checked all 43 today: every one matches production exactly, and I confirmed the derived fixtures (TEST_INITIALIZATION_METADATA, SECOND_COMMIT_TEST_METADATA, TEST_COMMIT_HASH) are byte-identical to what real init and commit_changes produce. So nothing is wrong right now.

The problem is that nothing keeps them equal. If someone edits MAIN_BRANCH_NAME in production, test_constants.TEST_INITIALIZATION_METADATA still says "main", and instead of a clear failure you get dozens of confusing ones — or, worse, tests that quietly stop testing anything.

One test closes that hole permanently:

def _shared_names(c: SCCSConstants, tc: SCCSTestConstants) -> list[str]:
    return sorted(
        name
        for name in set(dir(tc)) & set(dir(c))
        if not name.startswith("_")
        and not callable(getattr(tc, name))
        and not callable(getattr(c, name))
    )

@pytest.mark.parametrize("name", _shared_names(SCCSConstants(), SCCSTestConstants()))
def test_test_constants_match_production_constants(
    c: SCCSConstants, tc: SCCSTestConstants, name: str
) -> None:
    assert getattr(tc, name) == getattr(c, name)
Verified: 43 passed. Then I changed MAIN_BRANCH_NAME = "main" to "trunk" in production and it failed with FAILED ... [MAIN_BRANCH_NAME]. dir() rather than vars() matters here — vars() on an instance returns the empty instance dict, which silently guards nothing.