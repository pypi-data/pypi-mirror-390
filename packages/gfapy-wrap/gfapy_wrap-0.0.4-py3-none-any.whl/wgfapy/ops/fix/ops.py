"""Fixing operations."""

from __future__ import annotations

import enum
import logging
from typing import TYPE_CHECKING

from wgfapy.lines import flag, properties
from wgfapy.utils import io as uio

if TYPE_CHECKING:
    from pathlib import Path

    import gfapy


_LOGGER = logging.getLogger(__name__)


# REFACTOR whole module
class Tag(enum.StrEnum):
    """GFA header tag types."""

    SKESA_FIX = "FX"
    UNICYCLER_FIX = "FX"
    STANDARDIZED = "Sd"
    PANASSEMBLY_TYPE = "PA"


class TagType(enum.StrEnum):
    """GFA header tag types."""

    SKESA_FIX = properties.TagTypes.CHAR
    UNICYCLER_FIX = properties.TagTypes.CHAR
    STANDARDIZED = properties.TagTypes.CHAR
    PANASSEMBLY_TYPE = properties.TagTypes.STRING

    @classmethod
    def from_tag(cls, tag: Tag) -> TagType:
        """Get field type from tag."""
        return cls(tag.name)


class SKESAFixTagValue(enum.StrEnum):
    """SKESA fix header tag values."""

    YES = "Y"
    NO = "N"

    @classmethod
    def from_bool(
        cls,
        is_fixed: bool,  # noqa: FBT001
    ) -> SKESAFixTagValue:
        """Initialize from bool."""
        return cls.YES if is_fixed else cls.NO


def is_skesa_fixed(gfa: gfapy.Gfa) -> bool:
    """Check if a GFA graph is fixed."""
    return gfa.header.get(Tag.SKESA_FIX) == SKESAFixTagValue.YES


def set_skesa_fixed_header_tag(
    gfa: gfapy.Gfa,
    is_fixed: bool,  # noqa: FBT001
) -> None:
    """Set the SKESA fixed header tag in the GFA graph."""
    gfa.header.add(Tag.SKESA_FIX, SKESAFixTagValue.from_bool(is_fixed))


def is_skesa_gfa_fixed(gfa_path: Path) -> bool:
    """Check ig the SKESA GFA file is fixed."""
    yes_fix_tag = f"{Tag.SKESA_FIX}:{TagType.SKESA_FIX}:{SKESAFixTagValue.YES}"
    with uio.open_file_read(gfa_path) as f_in:
        for line in f_in:
            if line.startswith(str(flag.Type.HEADER)) and yes_fix_tag in line.split():
                _LOGGER.debug("SKESA GFA file is fixed.")
                return True
    _LOGGER.debug("SKESA GFA file is not fixed.")
    return False


def fix_skesa_gfa(
    in_gfa_path: Path,
    out_gfa_path: Path | None = None,
) -> Path:
    """Fix a SKESA GFA file.

    Parameters
    ----------
    in_gfa_path : Path
        Path to input GFA file
    out_gfa_path : Path | None, optional
        Path to output GFA file, must be different from input if used, by default None

    Returns
    -------
    Path
        Path to output GFA file

    Warnings
    --------
    This function modifies the input GFA file if out_gfa_path is None.

    Raises
    ------
    ValueError
        If input and output files are the same

    """
    if out_gfa_path is None:
        _LOGGER.debug("Fixing SKESA GFA file %s", in_gfa_path)
    else:
        _LOGGER.debug("Fixing SKESA GFA file %s to %s.", in_gfa_path, out_gfa_path)

    yes_fix_tag = f"{Tag.SKESA_FIX}:{TagType.SKESA_FIX}:{SKESAFixTagValue.YES}"
    with (
        uio.possible_tmp_file(in_gfa_path, out_gfa_path) as (
            use_in_path,
            use_out_path,
        ),
        uio.open_file_read(use_in_path) as f_in,
        uio.open_file_write(use_out_path) as f_out,
    ):
        f_out.write(f"{flag.Type.HEADER}\t{yes_fix_tag}\n")
        for line in f_in:
            if line.startswith(flag.Type.SEGMENT):
                split_line = line.split()
                f_out.write(split_line[0])  # S
                f_out.write("\t")
                f_out.write(split_line[1])  # segment name
                f_out.write("\t")
                f_out.write(split_line[2])  # sequence
                for optional_field in split_line[3:]:
                    tag_name, tag_type, value = optional_field.split(":")
                    if tag_type == properties.TagTypes.SIGNED_INT:
                        f_out.write(f"\t{tag_name}:{tag_type}:{int(float(value))}")
                    else:
                        f_out.write(f"\t{tag_name}:{tag_type}:{value}")
                f_out.write("\n")
            else:
                f_out.write(line)

    return use_out_path
