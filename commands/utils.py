#!/usr/bin/env python3

import os
import shutil
import sys
import tempfile
import uuid
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
    sibling_of.parent.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=prefix, dir=sibling_of.parent))


def cleanup_staging(staging_root: Path | None) -> None:
    """Best-effort removal of a staging directory. Safe to call multiple times."""
    if staging_root is None:
        return
    shutil.rmtree(staging_root, ignore_errors=True)


def current_symlink_path(c: SCCSConstants, repository_name: str) -> Path:

    return (
        Path.home()
        / c.SCCS_DIRECTORY
        / c.REPOSITORIES_PATH_SEGMENT
        / repository_name
        / c.VERSIONS_PATH_SEGMENT
        / c.CURRENT_PATH_SEGMENT
    )


def repository_path(c: SCCSConstants, repository_name: str) -> Path:

    return (
        Path.home() / c.SCCS_DIRECTORY / c.REPOSITORIES_PATH_SEGMENT / repository_name
    )


def promote_versioned(
    c: SCCSConstants, staging_root: Path, repository_name: str
) -> Path:

    current_symlink = current_symlink_path(c, repository_name)

    versions = (
        Path.home()
        / c.SCCS_DIRECTORY
        / c.REPOSITORIES_PATH_SEGMENT
        / repository_name
        / c.VERSIONS_PATH_SEGMENT
    )

    latest_version_number = 0

    if versions.is_dir():
        for i in versions.iterdir():
            if not i.name.startswith(
                c.VERSION_PATH_SEGMENT_TEMPLATE.format(version_number=c.EMPTY_STRING)
            ):
                continue
            try:
                latest_version_number = max(
                    latest_version_number,
                    int(
                        i.name[
                            len(
                                c.VERSION_PATH_SEGMENT_TEMPLATE.format(
                                    version_number=c.EMPTY_STRING
                                )
                            ) :
                        ]
                    ),
                )
            except ValueError:
                continue

    new_version_path = versions / c.VERSION_PATH_SEGMENT_TEMPLATE.format(
        version_number=latest_version_number + 1
    )

    promote_staging(c, staging_root, new_version_path)
    temporary_root = current_symlink.with_name(
        c.TEMPORARY_DIRECTORY_PREFIX + current_symlink.name
    )
    try:
        temporary_root.symlink_to(new_version_path, target_is_directory=True)
        os.replace(temporary_root, current_symlink)
    except Exception:
        cleanup_staging(new_version_path)
        cleanup_staging(temporary_root)
        raise

    return new_version_path


def promote_staging(c: SCCSConstants, staging_root: Path, final_root: Path) -> None:

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
