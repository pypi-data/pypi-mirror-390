"""Iteration from files."""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

from wgfapy import fragment as frags
from wgfapy.lines import flag as line_flags
from wgfapy.lines import link as l_lines
from wgfapy.lines import path as p_lines
from wgfapy.lines import segment as s_lines
from wgfapy.utils import io as uio

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

    import gfapy
    from Bio.SeqRecord import SeqRecord


def _filter_lines[T: gfapy.Line](
    gfa_file: Path,
    record_type: line_flags.Type,
    line_type: type[T],
) -> Iterator[T]:
    """Iterate over the lines of the given record type."""
    with uio.open_file_read(gfa_file) as f_in:
        yield from (line_type(line) for line in f_in if line[0] == record_type)


def forward_fragments(gfa_file: Path) -> Iterator[frags.OrientedFragment]:
    """Iterate over GFA (forward) fragments."""
    for segment in _filter_lines(gfa_file, s_lines.FLAG, s_lines.Line):
        yield frags.FromLine.forward(segment)


def segment_names(gfa_file: Path) -> Iterator[str]:
    """Iterate over the segment names."""
    for segment in _filter_lines(gfa_file, s_lines.FLAG, s_lines.Line):
        yield s_lines.Fields.NAME.from_line(segment)


def segment_lines(gfa_file: Path) -> Iterator[s_lines.Line]:
    """Iterate over the segment lines."""
    yield from _filter_lines(gfa_file, s_lines.FLAG, s_lines.Line)


def sequence_records(gfa_file: Path, sep: str = " ") -> Iterator[SeqRecord]:
    """Iterate over sequence records corresponding to GFA segment lines.

    Parameters
    ----------
    gfa_file: Path
        GFA file
    sep: str, optional
        string for separating GFA attributes, default is space

    Yields
    ------
    SeqRecord
        Sequence record

    """
    for segment_line in segment_lines(gfa_file):
        yield s_lines.to_sequence_record(segment_line, sep=sep)


def link_lines(gfa_file: Path) -> Iterator[l_lines.Line]:
    """Iterate over the link lines."""
    yield from _filter_lines(gfa_file, l_lines.FLAG, l_lines.Line)


def path_lines(gfa_file: Path) -> Iterator[p_lines.Line]:
    """Iterate over the path lines."""
    yield from _filter_lines(gfa_file, p_lines.FLAG, p_lines.Line)
