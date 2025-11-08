"""GFA header API wrapper."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from wgfapy.lines import properties

if TYPE_CHECKING:
    import gfapy  # type: ignore[import-untyped]


# REFACTOR all this module
class Tag(StrEnum):
    """GFA header tag types."""

    PANASSEMBLY_TYPE = "PA"


class TagType(StrEnum):
    """GFA header tag types."""

    PANASSEMBLY_TYPE = properties.TagTypes.STRING

    @classmethod
    def from_tag(cls, tag: Tag) -> TagType:
        """Get field type from tag."""
        return cls(tag.name)


class PanAssemblyTypeTagValue(StrEnum):
    """PanAssemblyType header tag values."""

    BASE = "panassembly"
    WITH_CONTIGS = "panassembly_with_contigs"


def panassembly_type(gfa: gfapy.Gfa) -> PanAssemblyTypeTagValue:
    """Get PanAssemblyType header tag value."""
    return PanAssemblyTypeTagValue(gfa.header.get(Tag.PANASSEMBLY_TYPE))


def set_panassembly_type(gfa: gfapy.Gfa, value: PanAssemblyTypeTagValue) -> None:
    """Set PanAssemblyType header tag value."""
    gfa.header.add(Tag.PANASSEMBLY_TYPE, value)
