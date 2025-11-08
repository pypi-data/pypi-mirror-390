"""Header GFA line."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from gfapy.line import header as _header

from . import flag

if TYPE_CHECKING:
    import gfapy

FLAG = flag.Type.HEADER

Line = _header.Header


def get_line(graph: gfapy.Gfa) -> Line:
    """Get header line from a GFA graph."""
    return cast("Line", graph.header)
