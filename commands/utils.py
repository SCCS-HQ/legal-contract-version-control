#!/usr/bin/env python3

import uuid
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable
from zipfile import ZipFile

import exceptions
from constants_classes import ErrorWrappers, SCCSConstants


def wrap_html(c: SCCSConstants, html: str, styles: str) -> str:

    return c.HTML_BOILERPLATE_TEMPLATE.format(styles=styles, html=html)


def entered_argument(
    c: SCCSConstants, argument: int, raise_on_not_provided: bool = True
) -> Any:

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

    error_wrappers = ErrorWrappers()
    try:
        main(SCCSConstants(), *args)

    except exceptions.SCCSException as e:
        print(error_wrappers.EXPECTED_ERROR_TEMPLATE.format(e=e))
        sys.exit(1)

    except Exception as e:
        print(
            error_wrappers.UNEXPECTED_ERROR_TEMPLATE.format(
                type_name=type(e).__name__, e=e
            )
        )
        sys.exit(2)


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



def promote_staging(staging_root: Path, final_root: Path) -> None:
    """Atomically promote a staging directory to its final location.

    final_root is assumed to already exist and be non-empty. True atomicity
    requires staging_root, final_root, and the temp swap path to all live on
    the same filesystem, since os.rename() is only atomic within one.

    Strategy: rename final_root aside (atomic), rename staging_root into its
    place (atomic), then delete the old contents. If the second rename fails,
    the original final_root is restored so callers never observe a missing
    final_root.
    """
    old_root = final_root.with_name(f"{final_root.name}.old-{uuid.uuid4().hex}")

    os.rename(final_root, old_root)
    try:
        os.rename(staging_root, final_root)
    except Exception:
        os.rename(old_root, final_root)  # roll back
        raise

    shutil.rmtree(old_root, ignore_errors=True)
