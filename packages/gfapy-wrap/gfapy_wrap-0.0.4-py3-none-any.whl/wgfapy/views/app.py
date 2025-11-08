"""Views applications."""

# Due to typer usage:
# ruff: noqa: TC003, FBT002

from __future__ import annotations

import logging
from pathlib import Path
from typing import Annotated

import rich
import typer

from wgfapy import root_logging
from wgfapy.lines import flag
from wgfapy.utils import io as uio

APP = typer.Typer(rich_markup_mode="rich")

_LOGGER = logging.getLogger(__name__)


class PrintStatsArgs:
    """Argument for printing GFA stats."""

    GFA_FILE = typer.Argument(
        help="GFA file path",
    )


@APP.command()
def stats(
    gfa_path: Annotated[Path, PrintStatsArgs.GFA_FILE],
    debug: Annotated[bool, root_logging.OPT_DEBUG] = False,
) -> None:
    """Print GFA stats."""
    root_logging.init_logger(_LOGGER, "Printing GFA stats.", debug)

    if not gfa_path.exists():
        _LOGGER.error("Input GFA file does not exist: %s", gfa_path)
        raise typer.Exit(1)

    number_of_segments = 0
    number_of_links = 0
    number_of_paths = 0
    with uio.open_file_read(gfa_path) as f_in:
        for line in f_in:
            if line[0] == flag.Type.SEGMENT:
                number_of_segments += 1
            elif line[0] == flag.Type.LINK:
                number_of_links += 1
            elif line[0] == flag.Type.PATH:
                number_of_paths += 1
    rich.print(f"Number of segments: {number_of_segments}")
    rich.print(f"Number of links: {number_of_links}")
    rich.print(f"Number of paths: {number_of_paths}")
