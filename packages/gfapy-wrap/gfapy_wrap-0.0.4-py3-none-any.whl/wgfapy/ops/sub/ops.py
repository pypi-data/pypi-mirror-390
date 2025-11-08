"""Sub graph operations."""

from __future__ import annotations

import contextlib
import itertools
from typing import TYPE_CHECKING

import gfapy
import networkx as nx

from wgfapy import fragment as gfa_frag
from wgfapy import link as gfa_link
from wgfapy.lines import link as l_lines
from wgfapy.lines import path as p_lines
from wgfapy.lines import segment as s_lines

if TYPE_CHECKING:
    from collections.abc import Iterable


def connected_components(graph: gfapy.Gfa) -> list[gfapy.Gfa]:
    """Get connected GFA (GFA1) graphs.

    Warning
    -------
    If one sequence is null, it is replaced by a placeholder (*) is the resulting GFA.

    Only links are considered (not containments)

    Raises
    ------
    NotImplementedError
        If GFA version is not GFA1
    """
    if graph.version != "gfa1":
        raise NotImplementedError

    # Build naive nx graph
    nx_graph: nx.Graph = nx.Graph()
    for segment_line in s_lines.iter_lines(graph):
        nx_graph.add_node(s_lines.Fields.NAME.from_line(segment_line))

    for link_line in l_lines.iter_lines(graph):
        nx_graph.add_edge(
            l_lines.Fields.FROM_SEGMENT.from_line(link_line),
            l_lines.Fields.TO_SEGMENT.from_line(link_line),
        )

    # Get connected components on nx graph
    d_seg_cc: dict[str, int] = {}
    num_cc = 0
    for k, component in enumerate(nx.connected_components(nx_graph)):
        num_cc += 1
        for segment_name in component:
            d_seg_cc[segment_name] = k

    connected_graphs: list[gfapy.Gfa] = [
        gfapy.Gfa(version="gfa1") for _ in range(num_cc)
    ]

    # Segment lines
    for segment_line in s_lines.iter_lines(graph):
        if not s_lines.Fields.SEQUENCE.from_line(segment_line):
            s_lines.Fields.SEQUENCE.set_for_line(segment_line, str(gfapy.Placeholder()))
        connected_graphs[
            d_seg_cc[s_lines.Fields.NAME.from_line(segment_line)]
        ].add_line(
            str(segment_line),
        )

    # Link
    for link_line in l_lines.iter_lines(graph):
        from_name = l_lines.Fields.FROM_SEGMENT.from_line(link_line)
        connected_graphs[d_seg_cc[from_name]].add_line(str(link_line))

    # Path
    for path_line in graph.paths:
        first_orseg = p_lines.Fields.SEGMENT_NAMES.item_from_line(path_line, 0)
        connected_graphs[d_seg_cc[first_orseg.name()]].add_line(
            str(path_line),
        )

    return connected_graphs


def sub_radius_graph(
    gfa_graph: gfapy.Gfa,
    segment_names: Iterable[str],
    radius: int,
) -> gfapy.Gfa:
    """Get a subgraph of a GFA graph."""
    kept_segment_names: set[str] = set()

    lifo_distanced_segments: list[tuple[str, int]] = [
        (segment_name, 0) for segment_name in segment_names
    ]
    while lifo_distanced_segments:
        segment_name, distance = lifo_distanced_segments.pop()

        if distance == radius:
            kept_segment_names.add(segment_name)

        elif distance < radius and segment_name not in kept_segment_names:
            kept_segment_names.add(segment_name)

            for link_line in l_lines.segment_dovetail(
                s_lines.from_name(gfa_graph, segment_name),
            ):
                lifo_distanced_segments.extend(
                    (neighbor, distance + 1)
                    for neighbor in (
                        l_lines.Fields.FROM_SEGMENT.from_line(link_line),
                        l_lines.Fields.TO_SEGMENT.from_line(link_line),
                    )
                    if neighbor not in kept_segment_names
                )

    sub_graph = gfapy.Gfa()
    for line in gfa_graph.lines:
        sub_graph.add_line(str(line))

    #
    # Remove segments
    #
    for segment_to_remove in [
        s for s in sub_graph.segments if s.name not in kept_segment_names
    ]:
        with contextlib.suppress(gfapy.RuntimeError):
            sub_graph.rm(segment_to_remove)
    #
    # Remove remaining links
    #
    for links_to_remove in [
        link_line
        for link_line in l_lines.dovetails(sub_graph)
        if l_lines.Fields.FROM_SEGMENT.from_line(link_line) not in kept_segment_names
        or l_lines.Fields.TO_SEGMENT.from_line(link_line) not in kept_segment_names
    ]:
        with contextlib.suppress(gfapy.RuntimeError):
            sub_graph.rm(links_to_remove)

    #
    # Remove remaining paths
    #
    for path_to_remove in [
        path_line
        for path_line in sub_graph.paths
        if any(
            oriented_identifier.name() not in kept_segment_names
            for oriented_identifier in p_lines.Fields.SEGMENT_NAMES.from_line(path_line)
        )
    ]:
        with contextlib.suppress(gfapy.RuntimeError):
            sub_graph.rm(path_to_remove)

    return sub_graph


def transform_small_contigs_into_links(
    gfa: gfapy.Gfa,
    min_contig_length: int,
) -> list[s_lines.Line]:
    """Remove small contigs and transform them into links.

    Parameters
    ----------
    gfa : gfapy.Gfa
        GFA graph
    min_contig_length : int
        Minimum contig length

    Warnings
    --------
    This function mutates the GFA graph

    Returns
    -------
    list of segment lines
        Removed segment lines
    """
    segment_lines_to_remove: list[s_lines.Line] = []
    for segment_line in s_lines.iter_lines(gfa):
        if s_lines.Tags.LENGTH.from_line(segment_line) < min_contig_length:
            left_edge_lines = list(l_lines.left_dovetail(segment_line))
            right_edge_lines = list(l_lines.right_dovetail(segment_line))
            predecessors: list[gfa_frag.OrientedFragment] = []
            successors: list[gfa_frag.OrientedFragment] = []

            link_lines_to_remove: list[l_lines.Line] = []

            for left_link_line in left_edge_lines:
                pred = gfa_frag.FromDovetail.left(
                    left_link_line,
                    s_lines.Fields.NAME.from_line(segment_line),
                )
                if pred.identifier() != s_lines.Fields.NAME.from_line(segment_line):
                    predecessors.append(pred)
                    link_lines_to_remove.append(left_link_line)

            for right_link_line in right_edge_lines:
                succ = gfa_frag.FromDovetail.right(
                    right_link_line,
                    s_lines.Fields.NAME.from_line(segment_line),
                )
                if succ.identifier() != s_lines.Fields.NAME.from_line(segment_line):
                    successors.append(succ)
                    link_lines_to_remove.append(right_link_line)

            for link_line in link_lines_to_remove:
                gfa.rm(link_line)
            gfa.validate()

            segment_lines_to_remove.append(segment_line)

            for link in (
                gfa_link.Link(pred, succ)
                for pred, succ in itertools.product(predecessors, successors)
            ):
                with contextlib.suppress(gfapy.NotUniqueError):
                    # XXX the exception should not happen
                    gfa.add_line(gfa_link.LineConverter.to_line(link, "0M"))
            gfa.validate()

    for segment_line in segment_lines_to_remove:
        gfa.rm(segment_line)

    gfa.validate()

    return segment_lines_to_remove
