#!/usr/bin/env python3
"""Module for utility functions used in SCCS."""

import re
from pathlib import Path
import sys

import exceptions
from constants_classes import SCCSConstants, ErrorWrappers
from repository_layout import RepositoryLayout


def clean_directory_name(name: str) -> str:
    """
    Return a filesystem-safe directory version of 'name' by replacing invalid
    characters.
    """
    return re.sub(r'^[. ]+|[\\/:*?"<>|]|[. ]+$', "-", name)


def wrap_html(c: SCCSConstants, html: str, styles: str) -> str:
    """
    Return a wrapped HTML content in a complete document template using 'styles'. This
    requires 'html' to already include proper 'class' attributes.
    """
    return (
        c.HTML_BOILERPLATE_TEMPLATE.format(styles=styles, html=html)
    )


def entered_argument(argument: int) -> str | None:
    """Return the entered command-line argument at the specified index if provided, else None."""

    arg_value = sys.argv[argument].strip() if len(sys.argv) > argument else None
    return arg_value.strip() if isinstance(arg_value, str) else None

def run_command(main, *args_indices, use_RepositoryLayout: bool = True,):
    try:
        c = SCCSConstants()
        repository = RepositoryLayout(Path.cwd(), c)
        error_wrappers = ErrorWrappers()
        args = [entered_argument(i) for i in args_indices]

        if not use_RepositoryLayout:
            main(c, *args)

        main(c, repository, *args)


    except exceptions.SCCSException as e:
        print(error_wrappers.EXPECTED_ERROR_TEMPLATE.format(e=e))
        sys.exit(1)

    except Exception as e:
        print(error_wrappers.UNEXPECTED_ERROR_TEMPLATE.format(type_name=type(e).__name__, e=e))
        sys.exit(2)
