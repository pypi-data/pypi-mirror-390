"""Link GFA API wrapper."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import fragment
from .lines import link as l_lines
from .lines import segment as s_lines

if TYPE_CHECKING:
    from collections.abc import Iterator

    import gfapy


class Link:
    """Link."""

    def __init__(
        self,
        predecessor: fragment.OrientedFragment,
        successor: fragment.OrientedFragment,
    ) -> None:
        """Initialize object."""
        self.__predecessor = predecessor
        self.__successor = successor

    def predecessor(self) -> fragment.OrientedFragment:
        """Get predecessor."""
        return self.__predecessor

    def successor(self) -> fragment.OrientedFragment:
        """Get successor."""
        return self.__successor

    def reverse(self) -> None:
        """Reverse link."""
        self.__predecessor = self.__successor.to_reverse()
        self.__successor = self.__predecessor.to_reverse()

    def to_reverse(self) -> Link:
        """Get reverse link."""
        return Link(
            self.__successor.to_reverse(),
            self.__predecessor.to_reverse(),
        )

    def simplify(self) -> None:
        """Humanly simplify the link.

        Just in the case the two orientations are reversed.
        """
        if self.__predecessor.is_reverse() and self.__successor.is_reverse():
            self.reverse()


class LineConverter:
    """Link from or to gfapy line converter."""

    @classmethod
    def from_line(cls, link_line: l_lines.Line) -> Link:
        """Get link from link line."""
        return Link(
            fragment.OrientedFragment(
                l_lines.Fields.from_segment(link_line),
                l_lines.Fields.from_orient(link_line),
            ),
            fragment.OrientedFragment(
                l_lines.Fields.to_segment(link_line),
                l_lines.Fields.to_orient(link_line),
            ),
        )

    @classmethod
    def to_line(cls, link: Link, overlap: str) -> l_lines.Line:
        """Get GFA link line."""
        return l_lines.Line(
            (
                f"{l_lines.FLAG}"
                f"\t{link.predecessor().identifier()}"
                f"\t{link.predecessor().orientation().value}"
                f"\t{link.successor().identifier()}"
                f"\t{link.successor().orientation().value}"
                f"\t{overlap}"
            ),
        )


class FoundLink:
    """Found link line in graph corresponding to the given Link."""

    def __init__(
        self,
        link_line: l_lines.Line,
        orientation: fragment.Orientation,
    ) -> None:
        self.__link_line = link_line
        self.__orientation = orientation

    def link_line(self) -> l_lines.Line:
        """Get link line."""
        return self.__link_line

    def orientation(self) -> fragment.Orientation:
        """Get orientation."""
        return self.__orientation


def find(gfa: gfapy.Gfa, link: Link) -> FoundLink | None:
    """Check if link or its reversed exists.

    Returns
    -------
    FoundLink
        The corresponding gfa link line
        and if it corresponds to the forward or the reverse of the given link
    None
        If the link or its reversed does not exist in the graph

    """
    pred = link.predecessor()
    if pred.is_forward():
        succ = link.successor()
        r_link_line_iter = iter(
            l_lines.right_dovetail(s_lines.from_name(gfa, pred.identifier())),
        )
        link_line = next(r_link_line_iter, None)
        while link_line is not None:
            if fragment.FromDovetail.right(link_line, pred.identifier()) == succ:
                return FoundLink(link_line, fragment.Orientation.FORWARD)
            link_line = next(r_link_line_iter, None)
    else:
        succ_rev = link.successor().to_reverse()
        l_link_line_iter = iter(
            l_lines.left_dovetail(s_lines.from_name(gfa, pred.identifier())),
        )
        link_line = next(l_link_line_iter, None)
        while link_line is not None:
            if fragment.FromDovetail.left(link_line, pred.identifier()) == succ_rev:
                return FoundLink(link_line, fragment.Orientation.REVERSE)
            link_line = next(l_link_line_iter, None)
    return None


def gfa_links(gfa: gfapy.Gfa) -> Iterator[Link]:
    """Iterate over only one version of each link."""
    for link_line in l_lines.dovetails(gfa):
        yield LineConverter.from_line(link_line)


def predecessors(
    gfa: gfapy.Gfa,
    oriented_fragment: fragment.OrientedFragment,
) -> Iterator[fragment.OrientedFragment]:
    """Iterate over all predecessors."""
    if oriented_fragment.is_forward():
        return (
            fragment.FromDovetail.left(
                link_line,
                oriented_fragment.identifier(),
            )
            for link_line in l_lines.left_dovetail(
                s_lines.from_name(
                    gfa,
                    oriented_fragment.identifier(),
                ),
            )
        )
    return (
        fragment.FromDovetail.right(
            link_line,
            oriented_fragment.identifier(),
        ).to_reverse()
        for link_line in l_lines.right_dovetail(
            s_lines.from_name(
                gfa,
                oriented_fragment.identifier(),
            ),
        )
    )


def incoming_links(
    gfa: gfapy.Gfa,
    oriented_fragment: fragment.OrientedFragment,
) -> Iterator[Link]:
    """Get incoming links.

    Iterate over only one version of the link.
    """
    return (
        Link(predecessor, oriented_fragment)
        for predecessor in predecessors(gfa, oriented_fragment)
    )


def successors(
    gfa: gfapy.Gfa,
    oriented_fragment: fragment.OrientedFragment,
) -> Iterator[fragment.OrientedFragment]:
    """Iterate over all successors."""
    if oriented_fragment.is_forward():
        return (
            fragment.FromDovetail.right(
                link_line,
                oriented_fragment.identifier(),
            )
            for link_line in l_lines.right_dovetail(
                s_lines.from_name(
                    gfa,
                    oriented_fragment.identifier(),
                ),
            )
        )
    return (
        fragment.FromDovetail.left(
            link_line,
            oriented_fragment.identifier(),
        ).to_reverse()
        for link_line in l_lines.left_dovetail(
            s_lines.from_name(
                gfa,
                oriented_fragment.identifier(),
            ),
        )
    )


def outgoing_links(
    gfa: gfapy.Gfa,
    oriented_fragment: fragment.OrientedFragment,
) -> Iterator[Link]:
    """Get outgoing links.

    Iterate over only one version of the link.
    """
    return (
        Link(oriented_fragment, successor)
        for successor in successors(gfa, oriented_fragment)
    )
