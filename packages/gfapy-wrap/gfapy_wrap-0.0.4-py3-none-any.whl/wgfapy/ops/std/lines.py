"""Lines in the standardized GFA."""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from wgfapy.lines import header as h_lines
from wgfapy.lines import properties as line_props

if TYPE_CHECKING:
    import gfapy


class Status(enum.StrEnum):
    """Standardized status header tag values."""

    STANDARD = "Y"
    NOT_STANDARD = "N"


class HeaderTags(line_props.Tags[h_lines.Line]):
    """Segment common tags."""

    _TAG_BUILDER = line_props.TagBuilder.from_fields(None)

    class _StatusCharTag(line_props.TagBase[h_lines.Line, Status]):
        """Status char tag getter and setter."""

        GFA_TYPE = line_props.TagTypes.CHAR
        VALUE_PARSER = line_props.LeaveParser(Status)

    STANDARD_STATUS = _TAG_BUILDER.new("Sd", _StatusCharTag)

    @classmethod
    def standard_status(cls, graph: gfapy.Gfa) -> Status:
        """Get kmer coverage."""
        return cls.STANDARD_STATUS.from_line(h_lines.get_line(graph)).value_or(
            Status.NOT_STANDARD,
        )

    @classmethod
    def set_standard_status(cls, graph: gfapy.Gfa, status: Status) -> None:
        """Set kmer coverage."""
        cls.STANDARD_STATUS.set_for_line(h_lines.get_line(graph), status)
