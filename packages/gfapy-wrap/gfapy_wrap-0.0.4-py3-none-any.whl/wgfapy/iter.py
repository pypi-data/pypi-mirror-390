"""Graph iteration method."""

from __future__ import annotations

from typing import TYPE_CHECKING

from wgfapy import fragment as gfa_frag

if TYPE_CHECKING:
    from collections.abc import Iterator

    import gfapy


def forward_fragments(gfa: gfapy.Gfa) -> Iterator[gfa_frag.OrientedFragment]:
    """Iterate over GFA (forward) fragments.

    Yields
    ------
    OrientedFragment
        Fragment (in forward orientation)
    """
    for segment_line in gfa.segments:
        yield gfa_frag.FromLine.forward(segment_line)
