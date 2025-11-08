"""Path GFA API wrapper."""

from __future__ import annotations

from typing import TYPE_CHECKING, final

from gfapy.line.group.path import path as _path

from . import flag, properties
from . import segment as s_lines

if TYPE_CHECKING:
    from collections.abc import Iterator

    import gfapy


FLAG = flag.Type.PATH

Line = _path.Path


@final
class Fields(properties.Fields[Line]):
    """Segment fields."""

    _FIELD_BUILDER = properties.FieldBuilder[Line]()

    @final
    class _SegmentNamesField(properties.ListField[Line, s_lines.OrientedLine]):
        """Path segment names field."""

        VALUE_PARSER = properties.ListParser(s_lines.OrientedLine)

    NAME = _FIELD_BUILDER.new_string_field("path_name")
    SEGMENT_NAMES = _FIELD_BUILDER.new("segment_names", _SegmentNamesField)
    # REFACTOR use gfapy.Alignment
    OVERLAPS = _FIELD_BUILDER.new_string_field("overlaps")

    @classmethod
    def name(cls, line: Line) -> str:
        """Get name."""
        return cls.NAME.from_line(line)

    @classmethod
    def segment_names(cls, line: Line) -> list[s_lines.OrientedLine]:
        """Get segment names."""
        return cls.SEGMENT_NAMES.from_line(line)

    @classmethod
    def overlaps(cls, line: Line) -> str:
        """Get overlaps."""
        return cls.OVERLAPS.from_line(line)


class NoPathNameError(Exception):
    """No path name error."""

    def __init__(self, name: str) -> None:
        self._name = name

    def name(self) -> str:
        """Get name."""
        return self._name


def from_name(gfa: gfapy.Gfa, name: str) -> Line:
    """Get path by name.

    Parameters
    ----------
    gfa : gfapy.Gfa
        GFA graph
    name : str
        Path name

    Returns
    -------
    Line
        GFA path line

    Raises
    ------
    NoPathNameError
        Invalid path name error

    """
    line: gfapy.Line | None = gfa.line(str(name))
    if line is None or line.record_type != FLAG:
        raise NoPathNameError(name)
    return Line(line)


def iter_lines(gfa: gfapy.Gfa) -> Iterator[Line]:
    """Iterate over paths in a GFA graph."""
    yield from map(Line, gfa.paths)
