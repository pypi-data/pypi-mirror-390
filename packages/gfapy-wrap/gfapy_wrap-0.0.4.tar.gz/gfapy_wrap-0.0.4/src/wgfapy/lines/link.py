"""Link GFA API wrapper."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gfapy.line import edge as _edge

from . import flag, properties
from . import segment as s_lines

if TYPE_CHECKING:
    from collections.abc import Iterator

    import gfapy

FLAG = flag.Type.LINK

Line = _edge.Link


class Fields(properties.Fields[Line]):
    """Link fields."""

    _FIELD_BUILDER = properties.FieldBuilder[Line]()

    class _OrientField(properties.FieldBase[Line, s_lines.Orientation]):
        """Orient field getter and setter."""

        VALUE_PARSER = properties.LeaveParser(s_lines.Orientation)

    FROM_SEGMENT = _FIELD_BUILDER.new_string_field("from_segment")
    FROM_ORIENT = _FIELD_BUILDER.new("from_orient", _OrientField)
    TO_SEGMENT = _FIELD_BUILDER.new_string_field("to_segment")
    TO_ORIENT = _FIELD_BUILDER.new("to_orient", _OrientField)
    OVERLAP = _FIELD_BUILDER.new_string_field("overlap")

    @classmethod
    def from_segment(cls, line: Line) -> str:
        """Get from segment."""
        return cls.FROM_SEGMENT.from_line(line)

    @classmethod
    def from_orient(cls, line: Line) -> s_lines.Orientation:
        """Get from orient."""
        return cls.FROM_ORIENT.from_line(line)

    @classmethod
    def to_segment(cls, line: Line) -> str:
        """Get to segment."""
        return cls.TO_SEGMENT.from_line(line)

    @classmethod
    def to_orient(cls, line: Line) -> s_lines.Orientation:
        """Get to orient."""
        return cls.TO_ORIENT.from_line(line)

    @classmethod
    def overlap(cls, line: Line) -> str:
        """Get overlap."""
        return cls.OVERLAP.from_line(line)


def dovetails(gfa: gfapy.Gfa) -> Iterator[Line]:
    """Wrap of gfapy dovetails backreference."""
    yield from gfa.dovetails


def iter_lines(gfa: gfapy.Gfa) -> Iterator[Line]:
    """Iterate over links in a GFA graph."""
    yield from map(Line, dovetails(gfa))


def left_dovetail(segment_line: s_lines.Line) -> Iterator[Line]:
    """Wrap of gfapy dovetail_L backreference."""
    yield from segment_line.dovetail_L


def right_dovetail(segment_line: s_lines.Line) -> Iterator[Line]:
    """Wrap of gfapy dovetail_R backreference."""
    yield from segment_line.dovetail_R


def segment_dovetail(segment_line: s_lines.Line) -> Iterator[Line]:
    """Wrap of gfapy dovetail_S backreference."""
    yield from segment_line.dovetail
