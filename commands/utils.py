#!/usr/bin/env python3

import re
import sys

import exceptions
from constants_classes import SCCSConstants, ErrorWrappers
from typing import Any, Callable


def clean_directory_name(name: str) -> str:
    return re.sub(r'^[. ]+|[\\/:*?"<>|]|[. ]+$', "-", name)


def wrap_html(c: SCCSConstants, html: str, styles: str) -> str:
    return (
        c.HTML_BOILERPLATE_TEMPLATE.format(styles=styles, html=html)
    )


def entered_argument(argument: int) -> str:

    arg_value = sys.argv[argument].strip() if len(sys.argv) > argument else None

    if arg_value:
        return arg_value
    else:
        raise exceptions.InvalidArgumentError()


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
