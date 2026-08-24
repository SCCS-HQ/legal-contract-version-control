#!/usr/bin/env python3

import re
import sys
from typing import Any, Callable

import os
from pathlib import Path

import exceptions
from constants_classes import ErrorWrappers, SCCSConstants


def clean_directory_name(name: str) -> str:
    return re.sub(r"^[. ]+|[\\\/:*?\"\'<>|]|[. ]+$", "-", name)


def wrap_html(c: SCCSConstants, html: str, styles: str) -> str:
    return c.HTML_BOILERPLATE_TEMPLATE.format(styles=styles, html=html)


def entered_argument(argument: int, raise_on_not_provided: bool = True) -> Any:

    if not len(sys.argv) > argument:
        if raise_on_not_provided:
            raise exceptions.InvalidArgumentError()
        else:
            return None

    return sys.argv[argument].strip()


def safe_extract_zip(zf, member, dest):
    entry_path = Path(member)
    if entry_path.is_absolute() or ".." in entry_path.parts:
        raise exceptions.ZippingFileError("Invalid file path in zip")
    target_path = Path(os.path.normpath(dest / entry_path))
    try:
        target_path.relative_to(Path(dest).resolve())
    except ValueError:
        raise exceptions.ZippingFileError("Invalid file path in zip")
    if zf.getinfo(member).is_dir():
        target_path.mkdir(parents=True, exist_ok=True)
    else:
        target_path.parent.mkdir(parents=True, exist_ok=True)
    zf.extract(member, path=dest)


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
