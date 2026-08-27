#!/usr/bin/env python3

import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Callable

import exceptions
from constants_classes import ErrorWrappers, SCCSConstants


def wrap_html(c: SCCSConstants, html: str, styles: str) -> str:
    return c.HTML_BOILERPLATE_TEMPLATE.format(styles=styles, html=html)


def entered_argument(argument: int, raise_on_not_provided: bool = True) -> Any:

    if not len(sys.argv) > argument:
        if raise_on_not_provided:
            raise exceptions.SCCSException()
        else:
            return None

    return sys.argv[argument].strip()


def safe_extract_zip(zip_archive, member_path, destination_directory):
    destination_resolved = Path(destination_directory).resolve()
    entry_path = Path(member_path)
    if entry_path.is_absolute() or ".." in entry_path.parts:
        raise exceptions.SCCSException("Invalid file path in zip")
    target_path = Path(os.path.normpath(destination_directory / entry_path)).resolve()
    try:
        target_path.relative_to(destination_resolved)
    except ValueError as e:
        raise exceptions.SCCSException("Invalid file path in zip") from e
    if zip_archive.getinfo(member_path).is_dir():
        target_path.mkdir(parents=True, exist_ok=True)
    else:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with zip_archive.open(member_path) as source, open(target_path, "wb") as f:
            shutil.copyfileobj(source, f)


def run_command(main: Callable[..., None], *args: Any) -> None:
    error_wrappers = ErrorWrappers()
    c = SCCSConstants()
    try:
        main(c, *args)

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
