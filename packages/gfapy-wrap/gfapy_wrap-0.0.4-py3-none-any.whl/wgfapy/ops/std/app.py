"""Standardize applications."""

# Due to typer usage:
# ruff: noqa: TC003, FBT002

from __future__ import annotations

import logging
from pathlib import Path
from typing import Annotated, assert_never

import typer

from wgfapy import root_logging
from wgfapy.io import create as gfa_io

from . import lines as std_lines

APP = typer.Typer(rich_markup_mode="rich")

_LOGGER = logging.getLogger(__name__)


class ISGFAStandardizeArgs:
    """Argument for checking if a GFA is standardized."""

    ARG_IN_GFA = typer.Argument(
        help="Input GFA file",
    )


@APP.command()
def check(
    gfa_path: Annotated[Path, ISGFAStandardizeArgs.ARG_IN_GFA],
    debug: Annotated[bool, root_logging.OPT_DEBUG] = False,
) -> None:
    """Check if a GFA is standardized."""
    root_logging.init_logger(_LOGGER, "Checking if GFA is standardized.", debug)

    if not gfa_path.exists():
        _LOGGER.error("Input GFA file does not exist: %s", gfa_path)
        raise typer.Exit(1)

    gfa = gfa_io.from_file(gfa_path)

    match std_lines.HeaderTags.standard_status(gfa):
        case std_lines.Status.STANDARD:
            _LOGGER.info("GFA is standardized.")
        case std_lines.Status.NOT_STANDARD:
            _LOGGER.info("GFA is not standardized.")
        case never:
            assert_never(never)
