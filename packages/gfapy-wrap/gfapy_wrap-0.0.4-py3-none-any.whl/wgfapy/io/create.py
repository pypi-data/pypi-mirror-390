"""GFA input output module."""

import gzip
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile

import gfapy  # type: ignore[import-untyped]

from wgfapy.lines import segment as s_lines
from wgfapy.utils import io as uio

from . import iter as io_iter


def from_file(gfa_path: Path) -> gfapy.Gfa:
    """Read a GFA file (compressed or not)."""
    if uio.is_gz_file(gfa_path):
        return from_gfa_gz(gfa_path)
    return gfapy.Gfa.from_file(gfa_path)


def from_gfa_gz(in_gfa_gz_path: Path) -> gfapy.Gfa:
    """Read a GFA gzip compressed file."""
    with (
        gzip.open(in_gfa_gz_path, "rb") as f_in,
        NamedTemporaryFile("wb") as f_out,
    ):
        shutil.copyfileobj(f_in, f_out)  # type: ignore[misc]
        f_out.flush()
        gfa = gfapy.Gfa.from_file(f_out.name, vlevel=0)
    gfa.validate()
    return gfa


def gfa_file_to_fasta_file(
    gfa_file: Path,
    fasta_path: Path,
    sep: str = s_lines.DEFAULT_ATTRIBUTE_STR_SEP,
) -> None:
    """Write a FASTA file from GFA file.

    Parameters
    ----------
    gfa_file : Path
        GFA graph file
    fasta_path : Path
        Path to FASTA file
    sep : str, optional
        string for separating GFA attributes, default is space

    """
    with fasta_path.open("w") as f_out:
        for seq_record in io_iter.sequence_records(gfa_file, sep=sep):
            f_out.write(seq_record.format("fasta"))


def to_file(graph: gfapy.Gfa, gfa_path: Path) -> None:
    """Write a GFA graph to a file."""
    with uio.open_file_write(gfa_path) as f_out:
        for line in graph.lines:
            f_out.write(f"{line}\n")
