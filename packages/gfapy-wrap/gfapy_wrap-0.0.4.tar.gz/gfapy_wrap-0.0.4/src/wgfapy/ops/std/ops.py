"""Standardize assembly GFA graph operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

import wgfapy.lines.header as h_lines

from . import lines

if TYPE_CHECKING:
    import gfapy


def set_standardized_header_tag(gfa: gfapy.Gfa) -> None:
    """Set the standardized header tag in the GFA graph."""
    lines.HeaderTags.STANDARD_STATUS.define(h_lines.get_line(gfa))
    lines.HeaderTags.set_standard_status(gfa, lines.Status.STANDARD)
