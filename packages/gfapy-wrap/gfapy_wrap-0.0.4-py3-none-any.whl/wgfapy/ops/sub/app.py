"""Sub operation applications."""

# Due to typer
# ruff: noqa: FBT002

import logging
from pathlib import Path
from typing import Annotated

import typer

from wgfapy import root_logging
from wgfapy.io import create as gfa_io
from wgfapy.utils import io as uio

from . import ops

APP = typer.Typer(rich_markup_mode="rich")

_LOGGER = logging.getLogger(__name__)


class SubRadiusArgs:
    """Argument for extracting subgraph with neighbor radius."""

    GFA_FILE = typer.Argument(
        help="GFA file path",
    )

    SEGMENTS_FILE = typer.Argument(
        help="Segments serving as centers",
    )

    RADIUS = typer.Argument(
        help="Radius",
    )

    SUB_GFA_FILE = typer.Argument(
        help="Output subgraph GFA file, must be different from input if provided",
    )


@APP.command()
def sub_radius(
    gfa_path: Annotated[Path, SubRadiusArgs.GFA_FILE],
    sub_gfa_path: Annotated[Path, SubRadiusArgs.SUB_GFA_FILE],
    radius: Annotated[int, SubRadiusArgs.RADIUS],
    segments_paths: Annotated[list[Path], SubRadiusArgs.SEGMENTS_FILE],
    debug: Annotated[bool, root_logging.OPT_DEBUG] = False,
) -> None:
    """Extract subgraph with neighbor radius."""
    root_logging.init_logger(
        _LOGGER,
        "Extracting subgraph with neighbor radius.",
        debug,
    )

    if not gfa_path.exists():
        _LOGGER.critical("Input GFA file does not exist: %s", gfa_path)
        raise typer.Exit(1)

    if radius < 0:
        _LOGGER.critical("Radius must be positive.")
        raise typer.Exit(1)

    for p in segments_paths:
        if not p.exists():
            _LOGGER.critical("Input segments file does not exist: %s", p)
            raise typer.Exit(1)

    gfa_graph = gfa_io.from_file(gfa_path)

    centers: list[str] = []
    for p in segments_paths:
        with p.open() as f_in:
            centers.extend([line.strip() for line in f_in])

    sub_graph = ops.sub_radius_graph(gfa_graph, centers, radius)

    gfa_io.to_file(sub_graph, sub_gfa_path)

    _LOGGER.info("Subgraph written to: %s", sub_gfa_path)


class RemoveSmallSequencesArgs:
    """Argument for removing small sequences."""

    ARG_IN_GFA = typer.Argument(
        help="Input GFA file",
    )

    ARG_OUT_GFA = typer.Argument(
        help="Output GFA file, must be different from input if provided",
    )


class RemoveSmallSequencesOpts:
    """Options for removing small sequences."""

    MIN_LENGTH_DEF = 100
    MIN_LENGTH = typer.Option(
        "--min-length",
        "-m",
        help="Minimum length threshold (threshold kept)",
    )

    REMOVED_SEGMENTS_LINES = typer.Option(
        "rm-segments-gfa",
        help="GFA file containing the removed segment lines",
    )


@APP.command("rm-small-seq")
def remove_small_sequences(
    in_gfa: Annotated[Path, RemoveSmallSequencesArgs.ARG_IN_GFA],
    out_gfa: Annotated[Path | None, RemoveSmallSequencesArgs.ARG_OUT_GFA] = None,
    min_length: Annotated[
        int,
        RemoveSmallSequencesOpts.MIN_LENGTH,
    ] = RemoveSmallSequencesOpts.MIN_LENGTH_DEF,
    removed_segments_gfa: Annotated[
        Path | None,
        RemoveSmallSequencesOpts.REMOVED_SEGMENTS_LINES,
    ] = None,
    debug: Annotated[bool, root_logging.OPT_DEBUG] = False,
) -> Path:
    """Remove small sequences by preserving the walks."""
    root_logging.init_logger(_LOGGER, "Removing small sequences in a GFA.", debug)

    if not in_gfa.exists():
        _LOGGER.critical("Input GFA file does not exist: %s", in_gfa)
        raise typer.Exit(1)

    if out_gfa is None:
        out_gfa = in_gfa
    elif out_gfa == in_gfa:
        _LOGGER.critical("Output GFA file must be different from input if provided.")
        raise typer.Exit(1)

    if removed_segments_gfa in (in_gfa, out_gfa):
        _LOGGER.critical(
            "Removed segments GFA file must be different from"
            " input and output if provided.",
        )
        raise typer.Exit(1)

    graph = gfa_io.from_file(in_gfa)

    rm_seg_lines = ops.transform_small_contigs_into_links(graph, min_length)

    _LOGGER.info("Removed %d small sequences", len(rm_seg_lines))

    gfa_io.to_file(graph, out_gfa)

    if out_gfa == in_gfa:
        _LOGGER.info("Inplace filtered GFA file: %s", out_gfa)
    else:
        _LOGGER.info("New filtered GFA file: %s", out_gfa)

    if removed_segments_gfa is not None:
        with uio.open_file_write(removed_segments_gfa) as f_out:
            for line in rm_seg_lines:
                f_out.write(f"{line}\n")

        _LOGGER.info("Removed segments GFA file: %s", removed_segments_gfa)

    return out_gfa


class ConnectedComponentsArgsOpts:
    """Options for connected components."""

    GFA_IN = typer.Argument(
        help="Input GFA file",
    )

    OUT_DIR = typer.Option(
        "-o",
        "--outdir",
        help="Output folder (by default, same as input GFA file)",
    )

    GFA_OUT_PREFIX = typer.Option(
        "-p",
        "--prefix",
        help=(
            "Prefix for output GFA files"
            " (by default, same as input GFA file separated with `_`)"
            " e.g. graph.gfa.gz -> graph_1.gfa, graph_2.gfa ..."
        ),
    )

    GZIPPED = typer.Option(
        "--gzipped",
        help="Output GFA files will be gzipped",
    )


@APP.command("ccomps")
def connected_components(
    gfa_in: Annotated[Path, ConnectedComponentsArgsOpts.GFA_IN],
    out_dir: Annotated[Path | None, ConnectedComponentsArgsOpts.OUT_DIR] = None,
    gfa_out_prefix: Annotated[
        str | None,
        ConnectedComponentsArgsOpts.GFA_OUT_PREFIX,
    ] = None,
    gzipped: Annotated[bool, ConnectedComponentsArgsOpts.GZIPPED] = False,
    debug: Annotated[bool, root_logging.OPT_DEBUG] = False,
) -> list[Path]:
    """Extract connected components (.gfa files)."""

    def ccomp_file_path(prefix: str, index: int | str) -> Path:
        if gzipped:
            return Path(f"{prefix}{index}.gfa.gz")
        return Path(f"{prefix}{index}.gfa")

    root_logging.init_logger(_LOGGER, "Extracting connected components.", debug)

    if not gfa_in.exists():
        _LOGGER.critical("Input GFA file does not exist: %s", gfa_in)
        raise typer.Exit(1)

    graph = gfa_io.from_file(gfa_in)

    sub_graphs = ops.connected_components(graph)

    _LOGGER.info("Extracted %d connected components", len(sub_graphs))

    if out_dir is None:
        out_dir = gfa_in.parent

    if gfa_out_prefix is None:
        gfa_out_prefix = gfa_in.name.partition(".")[0] + "_"

    ccomp_paths: list[Path] = []
    for k, sub_graph in enumerate(sub_graphs):
        ccomp_paths.append(out_dir / ccomp_file_path(gfa_out_prefix, k))
        gfa_io.to_file(sub_graph, ccomp_paths[-1])

    sub_gfa_template = out_dir / ccomp_file_path(gfa_out_prefix, "*")

    _LOGGER.info("New GFA files: `%s`", sub_gfa_template)

    return ccomp_paths
