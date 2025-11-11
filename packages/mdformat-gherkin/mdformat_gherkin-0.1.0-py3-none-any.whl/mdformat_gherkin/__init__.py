"""Mdformat plugin to format Gherkin code blocks using reformat-gherkin."""

from reformat_gherkin.core import Options, format_str
from reformat_gherkin.options import (
    AlignmentMode,
    NewlineMode,
    TagLineMode,
    WriteBackMode,
)

__version__ = "0.1.0"  # DO NOT EDIT THIS LINE MANUALLY. LET bump2version UTILITY DO IT


def format_gherkin(unformatted: str, _info_str: str) -> str:
    # Create options for reformat-gherkin
    options = Options(
        write_back=WriteBackMode.INPLACE,
        step_keyword_alignment=AlignmentMode.LEFT,
        newline=NewlineMode.LF,
        tag_line_mode=TagLineMode.SINGLELINE,
        fast=False,
        indent="  ",  # Use 2 spaces for indentation
    )

    # Format the Gherkin content using reformat-gherkin
    return format_str(unformatted, options=options)
