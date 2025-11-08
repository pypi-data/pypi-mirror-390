"""GFA segment API wrapper."""

from __future__ import annotations

from .lines import link as l_lines
from .lines import segment as s_lines

Orientation = s_lines.Orientation


class OrientedFragment:
    """Oriented fragment."""

    def __init__(self, identifier: str, orientation: Orientation) -> None:
        """Initialize object."""
        self.__identifier = identifier
        self.__orientation = orientation

    def identifier(self) -> str:
        """Get identifier."""
        return self.__identifier

    def orientation(self) -> Orientation:
        """Get orientation."""
        return self.__orientation

    def is_forward(self) -> bool:
        """Check if fragment is forward."""
        return self.__orientation == Orientation.FORWARD

    def is_reverse(self) -> bool:
        """Check if fragment is reverse."""
        return self.__orientation == Orientation.REVERSE

    def to_reverse(self) -> OrientedFragment:
        """Get the reverse fragment.

        * `frag+` -> `frag-`
        * `frag-` -> `frag+`
        """
        return OrientedFragment(self.__identifier, self.__orientation.reverse())


class FromLine:
    """Convert a gfapy segment line to an oriented fragment."""

    @classmethod
    def new(
        cls,
        segment_line: s_lines.Line,
        orientation: Orientation,
    ) -> OrientedFragment:
        """Get oriented fragment from segment line."""
        return OrientedFragment(
            s_lines.Fields.name(segment_line),
            orientation,
        )

    @classmethod
    def forward(cls, segment_line: s_lines.Line) -> OrientedFragment:
        """Get forward fragment from segment line."""
        return cls.new(segment_line, Orientation.FORWARD)

    @classmethod
    def reverse(cls, segment_line: s_lines.Line) -> OrientedFragment:
        """Get reverse fragment from segment line."""
        return cls.new(segment_line, Orientation.REVERSE)


def from_oriented_identifier(orient_id: s_lines.OrientedLine) -> OrientedFragment:
    """Convert an oriented identifier to an oriented fragment.

    Oriented identifiers are for example found in path lines.
    """
    return OrientedFragment(orient_id.name(), orient_id.orient())


class FromDovetail:
    """Convert a gfapy dovetail line to an oriented fragment."""

    @classmethod
    def left(
        cls,
        link_line: l_lines.Line,
        segment_name: str,
    ) -> OrientedFragment:
        """Get fragment from left dovetail line."""
        if l_lines.Fields.to_segment(link_line) == segment_name:
            return OrientedFragment(
                l_lines.Fields.from_segment(link_line),
                l_lines.Fields.from_orient(link_line),
            )
        return OrientedFragment(
            l_lines.Fields.to_segment(link_line),
            l_lines.Fields.to_orient(link_line).reverse(),
        )

    @classmethod
    def right(
        cls,
        link_line: l_lines.Line,
        segment_name: str,
    ) -> OrientedFragment:
        """Get fragment from right dovetail line."""
        if l_lines.Fields.from_segment(link_line) == segment_name:
            return OrientedFragment(
                l_lines.Fields.to_segment(link_line),
                l_lines.Fields.to_orient(link_line),
            )
        return OrientedFragment(
            l_lines.Fields.from_segment(link_line),
            l_lines.Fields.from_orient(link_line).reverse(),
        )
