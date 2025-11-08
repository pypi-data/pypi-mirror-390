"""Input/output applications."""

# Due to typer usage:
# ruff: noqa: TC003, FBT002

from __future__ import annotations

import logging
from pathlib import Path
from typing import Annotated

import typer

from wgfapy import root_logging
from wgfapy.io import iter as io_iter
from wgfapy.lines import segment as s_lines
from wgfapy.ops.fix import app as fix_app
from wgfapy.ops.sub import app as sub_app
from wgfapy.utils import io as uio

APP = typer.Typer(rich_markup_mode="rich")

_LOGGER = logging.getLogger(__name__)

APP.add_typer(sub_app.APP, name="sub")
APP.add_typer(fix_app.APP, name="fix")


class ToFASTAArguments:
    """GFA to FASTA arguments."""

    ARG_IN_GFA = typer.Argument(
        help="Input GFA file",
    )

    ARG_OUT_FASTA = typer.Argument(
        help="Output FASTA file, must be different from input if provided",
    )


class ToFASTAOptions:
    """GFA to FASTA options."""

    __RICH_HELP_PANEL = "GFA to FASTA options"

    OPT_ATTRIBUTE_STRING_SEPARATOR = typer.Option(
        help="String separator for attributes",
        rich_help_panel=__RICH_HELP_PANEL,
    )


@APP.command()
def to_fasta(
    gfa_path: Annotated[Path, ToFASTAArguments.ARG_IN_GFA],
    fasta_path: Annotated[Path, ToFASTAArguments.ARG_OUT_FASTA],
    attribute_string_separator: Annotated[
        str,
        ToFASTAOptions.OPT_ATTRIBUTE_STRING_SEPARATOR,
    ] = s_lines.DEFAULT_ATTRIBUTE_STR_SEP,
    debug: Annotated[bool, root_logging.OPT_DEBUG] = False,
) -> None:
    """Convert GFA to FASTA (write to stdout)."""
    root_logging.init_logger(_LOGGER, "Converting GFA to FASTA.", debug)

    if not gfa_path.exists():
        _LOGGER.error("Input GFA file does not exist: %s", gfa_path)
        raise typer.Exit(1)

    with uio.open_file_write(fasta_path) as f_out:
        for seq_record in io_iter.sequence_records(
            gfa_path,
            sep=attribute_string_separator,
        ):
            f_out.write(seq_record.format("fasta"))

    _LOGGER.info("Resulting FASTA file: %s", fasta_path)
