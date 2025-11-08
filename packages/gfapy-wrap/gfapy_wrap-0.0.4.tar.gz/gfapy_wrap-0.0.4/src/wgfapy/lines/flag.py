"""Line flages."""

import enum


class Type(enum.StrEnum):
    """GFA line types."""

    COMMENT = "#"
    HEADER = "H"
    SEGMENT = "S"
    LINK = "L"
    JUMP = "J"
    CONTAINMENT = "C"
    PATH = "P"
    WALK = "W"
