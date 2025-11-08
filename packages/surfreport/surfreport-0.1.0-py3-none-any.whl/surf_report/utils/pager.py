"""Utilities for paging long CLI output."""

import os
import sys
from pydoc import pager as pydoc_pager


ENV_DISABLE_PAGER = "SURFREPORT_NO_PAGER"


def should_use_pager() -> bool:
    """
    Determine whether output should be routed through a pager.

    Returns:
        bool: True if stdout is a TTY and the pager is not disabled.
    """
    if os.environ.get(ENV_DISABLE_PAGER, "").strip() in {"1", "true", "True"}:
        return False
    return sys.stdout.isatty()


def page_output(text: str) -> None:
    """
    Display text using the user's pager. Falls back to printing on failures.

    Args:
        text (str): The text to display.
    """
    if not text:
        return
    try:
        pydoc_pager(text)
    except OSError:
        sys.stdout.write(text)
