"""gfapy segment line."""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING, final

import gfapy
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from gfapy.line import segment as _segment

from . import flag, properties

if TYPE_CHECKING:
    from collections.abc import Iterator

    from returns.maybe import Maybe

FLAG = flag.Type.SEGMENT

Line = _segment.Segment


class Fields(properties.Fields[Line]):
    """Segment fields."""

    _FIELD_BUILDER = properties.FieldBuilder[Line]()

    NAME = _FIELD_BUILDER.new_string_field("name")
    SEQUENCE = _FIELD_BUILDER.new_string_field("sequence")

    @classmethod
    def name(cls, line: Line) -> str:
        """Get name."""
        return cls.NAME.from_line(line)

    @classmethod
    def set_name(cls, line: Line, name: str) -> None:
        """Set name."""
        cls.NAME.set_for_line(line, name)

    @classmethod
    def sequence(cls, line: Line) -> str:
        """Get sequence."""
        return cls.SEQUENCE.from_line(line)

    @classmethod
    def set_sequence(cls, line: Line, sequence: str) -> None:
        """Set sequence."""
        cls.SEQUENCE.set_for_line(line, sequence)


def is_placeholder(segment: Line) -> bool:
    """Check if segment is a placeholder.

    Parameters
    ----------
    segment : Line
        GFA segment line

    Returns
    -------
    bool
        True if segment is a placeholder, False otherwise

    """
    return Fields.sequence(segment) == gfapy.Placeholder()


class Tags(properties.Tags[Line]):
    """Segment common tags."""

    _TAG_BUILDER = properties.TagBuilder.from_fields(Fields)

    @final
    class SelfLengthTag(properties.SelfIntegerTag[Line]):
        """Length tag."""

        def compute_value_from_split_line_str(self, split_line_str: list[str]) -> int:
            """Compute value from split line string."""
            sequence = Fields.SEQUENCE.from_split_line_str(split_line_str)
            if sequence == gfapy.Placeholder():
                return 0
            return len(sequence)

        def compute_value_from_line(self, line: Line) -> int:
            """Compute value from line."""
            return len(Fields.SEQUENCE.from_line(line))

    LENGTH = _TAG_BUILDER.new_self_tag("LN", SelfLengthTag)
    KMER_COVERAGE = _TAG_BUILDER.new_integer_tag("KC")
    NORMALIZED_COVERAGE = _TAG_BUILDER.new_float_tag("dp")

    @classmethod
    def length(cls, line: Line) -> int:
        """Get length."""
        return cls.LENGTH.from_line(line)

    @classmethod
    def set_length(cls, line: Line) -> None:
        """Set length."""
        cls.LENGTH.set_for_line(line)

    @classmethod
    def kmer_coverage(cls, line: Line) -> Maybe[int]:
        """Get kmer coverage."""
        return cls.KMER_COVERAGE.from_line(line)

    @classmethod
    def set_kmer_coverage(cls, line: Line, kmer_coverage: int) -> None:
        """Set kmer coverage."""
        cls.KMER_COVERAGE.set_for_line(line, kmer_coverage)

    @classmethod
    def normalized_coverage(cls, line: Line) -> Maybe[float]:
        """Get normalized coverage."""
        return cls.NORMALIZED_COVERAGE.from_line(line)

    @classmethod
    def set_normalized_coverage(cls, line: Line, normalized_coverage: float) -> None:
        """Set normalized coverage."""
        cls.NORMALIZED_COVERAGE.set_for_line(line, normalized_coverage)


def iter_lines(gfa: gfapy.Gfa) -> Iterator[Line]:
    """Iterate over segments in a GFA graph."""
    yield from gfa.segments


class Orientation(enum.StrEnum):
    """Orientation of a fragment."""

    FORWARD = "+"
    REVERSE = "-"

    @classmethod
    def from_reverse_char(cls, reverse_char: str) -> Orientation:
        """Get orientation from reverse character.

        Raises
        ------
        ValueError
            If reverse character is neither `+` (forward) nor `-` (reverse).
        """
        match reverse_char:
            case "+":
                return cls.REVERSE
            case "-":
                return cls.FORWARD
            case _:
                _err_msg = f"Invalid orientation character: {reverse_char}"
                raise ValueError(_err_msg)

    def reverse(self) -> Orientation:
        """Get reverse orientation."""
        match self:
            case Orientation.FORWARD:
                return Orientation.REVERSE
            case Orientation.REVERSE:
                return Orientation.FORWARD


class OrientedLine:
    """Oriented line gfapy wrapper."""

    def __init__(self, line: gfapy.OrientedLine) -> None:
        self.__line = line

    def name(self) -> str:
        """Get name."""
        return str(self.__line.name)

    def orient(self) -> Orientation:
        """Get orientation."""
        return Orientation(self.__line.orient)

    def invert(self) -> None:
        """Get reverted line."""
        self.__line.invert()

    def line(self) -> Line:
        """Get line."""
        return Line(self.__line.line)


class NoSegmentNameError(Exception):
    """No segment name error."""

    def __init__(self, name: str) -> None:
        self._name = name

    def name(self) -> str:
        """Get name."""
        return self._name


def from_name(gfa: gfapy.Gfa, name: str) -> Line:
    """Get segment by name.

    Parameters
    ----------
    gfa : gfapy.Gfa
        GFA graph
    name : str
        Segment name

    Returns
    -------
    Line
        GFA segment line

    Raises
    ------
    NoSegmentNameError
        Invalid segment name error

    """
    line: Line | None = gfa.segment(str(name))
    if line is None:
        raise NoSegmentNameError(name)
    return Line(line)


DEFAULT_ATTRIBUTE_STR_SEP = " "


def to_sequence_record(
    segment: Line,
    sep: str = DEFAULT_ATTRIBUTE_STR_SEP,
) -> SeqRecord:
    """Convert a GFA segment line to a sequence record.

    Parameters
    ----------
    segment: Line
        GFA segment line
    sep: str, optional
        string for separating GFA attributes, default is space

    Return
    ------
    SeqRecord
        Sequence record

    """
    return SeqRecord(
        Seq(Fields.sequence(segment)),
        id=Fields.name(segment),
        name=Fields.name(segment),
        description=f"{__format_attributes_string(segment, sep=sep)}",
    )


def __format_attributes_string(
    segment: Line,
    sep: str = DEFAULT_ATTRIBUTE_STR_SEP,
) -> str:
    """Format GFA segment attributes as a string.

    Parameters
    ----------
    segment: Line
        GFA segment
    sep: str, optional
        string for separating GFA attributes, default is space

    Returns
    -------
    str
        GFA segment attributes in format `key:value<sep>key:value<sep>...`

    """
    return sep.join(
        [f"{tag_name}:{segment.get(tag_name)}" for tag_name in segment.tagnames],
    )
