"""Fix application."""

# Due to typer
# ruff: noqa: FBT002

import logging
from pathlib import Path
from typing import Annotated

import typer

from wgfapy import root_logging

from . import ops

_LOGGER = logging.getLogger(__name__)

APP = typer.Typer(rich_markup_mode="rich")


class CheckSKESAGFAArgs:
    """Check Skeza GFA arguments."""

    ARG_IN_GFA = typer.Argument(
        help="Input GFA file",
    )


@APP.command()
def check_skesa(
    in_gfa: Annotated[Path, CheckSKESAGFAArgs.ARG_IN_GFA],
    debug: Annotated[bool, root_logging.OPT_DEBUG] = False,
) -> bool:
    """Check a Skeza GFA file."""
    root_logging.init_logger(_LOGGER, "Checking Skeza GFA file.", debug)

    if not in_gfa.exists():
        _LOGGER.error("Input GFA file does not exist: %s", in_gfa)
        raise typer.Exit(1)

    if ops.is_skesa_gfa_fixed(in_gfa):
        _LOGGER.info("SKESA GFA file is already fixed.")
        return True
    _LOGGER.info("SKESA GFA file is not fixed.")
    return False


class FixSKESAGFAArgs:
    """Fix SKESA GFA arguments."""

    ARG_IN_GFA = typer.Argument(
        help="Input GFA file",
    )

    ARG_OUT_GFA = typer.Argument(
        help="Output GFA file, must be different from input if provided",
    )


@APP.command()
def fix_skesa(
    in_gfa: Annotated[Path, FixSKESAGFAArgs.ARG_IN_GFA],
    out_gfa: Annotated[Path | None, FixSKESAGFAArgs.ARG_OUT_GFA] = None,
    debug: Annotated[bool, root_logging.OPT_DEBUG] = False,
) -> None:
    """Fix a SKESA GFA file."""
    root_logging.init_logger(_LOGGER, "Fixing SKESA GFA file.", debug)

    if not in_gfa.exists():
        _LOGGER.error("Input GFA file does not exist: %s", in_gfa)
        raise typer.Exit(1)

    if ops.is_skesa_gfa_fixed(in_gfa):
        _LOGGER.info("SKESA GFA file is already fixed.")
        return
    try:
        out_gfa = ops.fix_skesa_gfa(in_gfa, out_gfa_path=out_gfa)
    except ValueError as e:
        raise typer.Exit(1) from e

    _LOGGER.info("Fixed SKESA GFA file: %s", out_gfa)
