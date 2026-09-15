#!/usr/bin/env python3

import contextlib
import os
import shutil
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any, Callable, Iterator
from zipfile import ZipFile

import exceptions
from constants_classes import ErrorWrappers, SCCSConstants


def wrap_html(c: SCCSConstants, html: str, styles: str) -> str:
    """
    Wrap the entered HTML with the HTML boilerplate, applying the entered styles.
    """

    return c.HTML_BOILERPLATE_TEMPLATE.format(styles=styles, html=html)


def entered_argument(
    c: SCCSConstants, argument: int, raise_on_not_provided: bool = True
) -> Any:
    """
    Return the stripped command line argument at the entered index. Raise an
    SCCSException if the argument was not provided and raise_on_not_provided is True,
    otherwise return None.
    """

    if not len(sys.argv) > argument:
        if raise_on_not_provided:
            raise exceptions.SCCSException(c.UTILS_ARGUMENT_ERROR_MESSAGE)
        else:
            return None

    return sys.argv[argument].strip()


def safe_extract_zip(
    c: SCCSConstants,
    zip_archive: ZipFile,
    member_path: str,
    destination_directory: Path,
) -> None:
    """
    Extract the entered zip archive member into the destination directory, validating
    that the member path stays inside the destination directory. Raise an SCCSException
    if the member path is absolute, contains a double period, or is not relative to the
    destination directory.
    """

    destination_resolved = Path(destination_directory).resolve()
    entry_path = Path(member_path)
    if entry_path.is_absolute() or c.DOUBLE_PERIOD in entry_path.parts:
        raise exceptions.SCCSException(
            c.PATH_IS_ABSOLUTE_OR_CONTAINS_DOUBLE_PERIOD_ERROR_MESSAGE.format(
                entry_path=entry_path
            )
        )
    target_path = Path(os.path.normpath(destination_directory / entry_path)).resolve()
    try:
        target_path.relative_to(destination_resolved)
    except ValueError as e:
        raise exceptions.SCCSException(
            c.TARGET_PATH_NOT_RELATIVE_TO_PARENT_DIRECTORY_ERROR_MESSAGE.format(
                target_path=target_path, destination_resolved=destination_resolved
            )
        ) from e
    if zip_archive.getinfo(member_path).is_dir():
        target_path.mkdir(parents=True, exist_ok=True)
    else:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with zip_archive.open(member_path) as source, open(target_path, "wb") as f:
            shutil.copyfileobj(source, f)


def run_command(main: Callable[..., None], *args: Any) -> None:
    """
    Run the entered command function with the constants and provided arguments, printing
    the wrapped error and exiting when the command raises an exception.
    """

    c = SCCSConstants()
    error_wrappers = ErrorWrappers()
    try:
        main(c, *args)

    except exceptions.SCCSException as e:
        print(error_wrappers.EXPECTED_ERROR_TEMPLATE.format(e=e))
        sys.exit(c.EXPECTED_ERROR_EXIT_CODE)

    except Exception as e:
        print(
            error_wrappers.UNEXPECTED_ERROR_TEMPLATE.format(
                type_name=type(e).__name__, e=e
            )
        )
        sys.exit(c.UNEXPECTED_ERROR_EXIT_CODE)


def create_staging_directory(
    c: SCCSConstants, sibling_of: Path, prefix: str | None = None
) -> Path:
    """Create a sibling-staging directory for atomic filesystem operations.

    Placement as a sibling of `sibling_of` guarantees same-filesystem
    placement so a subsequent rename is atomic on POSIX/macOS.
    """
    if prefix is None:
        prefix = c.TEMPORARY_DIRECTORY_PREFIX
    return Path(tempfile.mkdtemp(prefix=prefix, dir=sibling_of.parent))


def cleanup_staging(staging_root: Path | None) -> None:
    """Best-effort removal of a staging directory. Safe to call multiple times."""
    if staging_root is None:
        return
    shutil.rmtree(staging_root, ignore_errors=True)


def promote_staging(c: SCCSConstants, staging_root: Path, final_root: Path) -> None:
    """
    Promote the staging directory to the final root by renaming it into place. If the
    final root already exists, rename it to a temporary old root first and remove it
    after the staging directory is promoted.

    There is a small window where repository may be lost if the process is interrupted
    between two atomic renames. This is a known limitation of the current
    implementation, and will be addressed in a future version.
    """

    if not final_root.exists():
        os.rename(staging_root, final_root)
        return

    old_root = final_root.with_name(
        c.OLD_ROOT_TEMPLATE.format(repository_name=final_root.name)
    )

    os.rename(final_root, old_root)
    try:
        os.rename(staging_root, final_root)
    except Exception:
        os.rename(old_root, final_root)
        raise

    shutil.rmtree(old_root, ignore_errors=True)


@contextlib.contextmanager
def staged_repository(
    c: SCCSConstants,
    sibling_root: Path,
    final_root: Path,
    copy_from: Path | None = None,
) -> Iterator[Path]:
    """
    Create a staging directory as a sibling of `sibling_root`, optionally copying the
    repository at `copy_from` into it, and yield the staging root.

    Promote the staging directory to `final_root` when the enclosing block completes,
    or clean up the staging directory and re-raise if any exception is raised within
    the block or during promotion.
    """

    staging_root = create_staging_directory(c, sibling_root)

    try:
        if copy_from is not None:
            shutil.copytree(copy_from, staging_root, dirs_exist_ok=True)

        yield staging_root

        promote_staging(c, staging_root, final_root)
    except Exception:
        cleanup_staging(staging_root)
        raise


def print_remote_success_message(
    c: SCCSConstants, status_code: int, url: str, message_template: str
) -> None:
    """
    Print the status code and a success message after a successful remote operation,
    formatting the entered message template with the remote URL.
    """

    print(c.STATUS_CODE_MESSAGE_TEMPLATE.format(status_code=status_code))
    print(message_template.format(url=url))


def copy_latest_commit_document(
    rd: Any, branch: str, destination: Path, error_message: str
) -> None:
    """
    Copy the latest commit document of the entered branch to the destination path,
    temporarily setting the target branch of `rd` (a duck-typed RepositoryData-like
    object sharing a TargetBranch with the caller's status object) to the entered
    branch and restoring the original target afterwards.

    Raise an SCCSException with the entered error message if the commit document
    cannot be resolved or copied.
    """

    original_target = rd.target.get()
    rd.target.set(branch)

    try:
        shutil.copy2(
            rd.commit_identifier_to_full_path(
                rd.latest_commit_identifier(), rd.c.DOCUMENT_DIRECTORY
            ),
            destination,
        )
    except Exception as e:
        raise exceptions.SCCSException(error_message) from e
    finally:
        rd.target.set(original_target)
