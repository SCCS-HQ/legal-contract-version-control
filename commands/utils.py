#!/usr/bin/env python3
"""Module for utility functions used in SCCS."""

import hashlib
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
import sys

import exceptions
from repository_layout import RepositoryLayout

Repository = RepositoryLayout(Path.cwd())


default_html_styles = (
    "<style>\n* {\nfont-family: Arial, Helvetica, sans-serif;\n}\n\n"
    ".inserted {\nbackground-color: #d4fcbc;\ndisplay: block;\nwidth: fit-content;\n}\n"
    "\n"
    ".deleted {\nbackground-color: #fbb6c2;\ndisplay: block;\nwidth: fit-content;\n}\n"
    "\n"
    ".center {\ndisplay: flex;\njustify-content: center;\n}\n</style>"
)


def clean_directory_name(name: str) -> str:
    """
    Return a filesystem-safe directory version of 'name' by replacing invalid
    characters.
    """
    return re.sub(r'[\\/:*?"<>|]', "-", name).strip(". ")


def wrap_html(html: str, styles: str = default_html_styles) -> str:
    """
    Return a wrapped HTML content in a complete document template using 'styles'. This
    requires 'html' to already include proper 'class' attributes.
    """
    return (
        f"<!DOCTYPE html><html><head><meta charset='UTF-8'>{styles}</head>"
        f"<body><div class='center'><div id='target'>{html}</div></div></body></html>"
    )


def entered_arguement(argument: int) -> str | None:
    """Return the entered command-line argument at the specified index if provided, else None."""
    
    arg_value = sys.argv[argument] if len(sys.argv) > argument else None
    return arg_value.strip() if isinstance(arg_value, str) else None