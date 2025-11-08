"""Assembly GFA graph operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

import wgfapy.lines.segment as s_lines

if TYPE_CHECKING:
    from collections.abc import Iterator

    import gfapy
    from returns.maybe import Maybe


def contig_normalized_coverages(graph: gfapy.Gfa) -> Iterator[tuple[str, Maybe[float]]]:
    """Iterate over the contigs and their normalized coverages."""
    return (
        (
            s_lines.Fields.NAME.from_line(segment_line),
            s_lines.Tags.NORMALIZED_COVERAGE.from_line(segment_line),
        )
        for segment_line in s_lines.iter_lines(graph)
    )


def contigs_lengths(graph: gfapy.Gfa) -> Iterator[tuple[str, int]]:
    """Iterate over the contigs and their lengths."""
    return (
        (
            s_lines.Fields.NAME.from_line(segment_line),
            s_lines.Tags.LENGTH.from_line(segment_line),
        )
        for segment_line in s_lines.iter_lines(graph)
    )


def set_segment_length_tags(graph: gfapy.Gfa) -> None:
    """Set the segment length attribute in a GFA graph.

    Parameters
    ----------
    graph : gfapy.Gfa
        GFA graph

    Warnings
    --------
    This function mutates the GFA graph

    """
    for segment in s_lines.iter_lines(graph):
        s_lines.Tags.LENGTH.define(segment)
        s_lines.Tags.set_length(segment)


def rename_segments(
    graph: gfapy.Gfa,
    prefix_name: str,
) -> None:
    """Rename segments in a GFA graph (base 1).

    Name will be set to `{prefix_name}{1..n}`

    Parameters
    ----------
    graph : gfapy.Gfa
        GFA graph
    segment_prefix_name : str
        Prefix for segment names

    Warnings
    --------
    This function mutates the GFA graph

    """
    for counter, segment in enumerate(s_lines.iter_lines(graph)):
        s_lines.Fields.set_name(
            segment,
            f"{prefix_name}{counter + 1}",
        )


def convert_kmer_coverage_to_normalized_coverage(
    graph: gfapy.Gfa,
) -> None:
    """Convert k-mer coverage to normalized coverage.

    Parameters
    ----------
    graph : gfapy.Gfa
        GFA graph

    Warnings
    --------
    This function mutates the GFA graph

    """
    total_coverage = sum(
        (coverage.value_or(0) for _, coverage in contig_normalized_coverages(graph)),
    )
    total_length = sum(c_len[1] for c_len in contigs_lengths(graph))

    for seg in s_lines.iter_lines(graph):
        s_lines.Tags.NORMALIZED_COVERAGE.define(seg)
        s_lines.Tags.set_normalized_coverage(
            seg,
            float(
                (s_lines.Tags.kmer_coverage(seg).unwrap() * total_length)
                / (s_lines.Tags.length(seg) * total_coverage),
            ),
        )
