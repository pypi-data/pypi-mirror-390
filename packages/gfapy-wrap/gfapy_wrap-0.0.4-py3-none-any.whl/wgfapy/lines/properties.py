"""GFA line properties interface."""

from __future__ import annotations

import abc
import enum
from typing import TYPE_CHECKING, Protocol

import gfapy
from returns.maybe import Maybe, Nothing, Some

if TYPE_CHECKING:
    from collections.abc import Iterable


class TagTypes(enum.StrEnum):
    """GFA tag types."""

    CHAR = "A"
    SIGNED_INT = "i"
    FLOAT = "f"
    STRING = "Z"
    JSON = "J"
    BYTE_ARRAY = "H"
    INT_OR_FLOAT_ARRAY = "B"


class IntOrFloatArrayTypes(enum.StrEnum):
    """Type letter for array of integers or floats."""

    INT8_T = "c"
    UINT8_T = "C"
    INT16_T = "s"
    UINT16_T = "S"
    INT32_T = "i"
    UINT32_T = "I"
    FLOAT = "f"


class CanConvert(Protocol):
    """A type convertor."""

    def __init__(self, *args: object) -> None: ...


class ValueParser[T: CanConvert](abc.ABC):
    """Value parser."""

    @abc.abstractmethod
    def value_type(self) -> type[T]:
        """Get value type."""
        raise NotImplementedError

    @abc.abstractmethod
    def from_str(self, value_str: str) -> T:
        """Convert value string to value."""
        raise NotImplementedError

    @abc.abstractmethod
    def to_str(self, value: T) -> str:
        """Convert value to string."""
        raise NotImplementedError


class Leave(Protocol):
    """A eave type."""

    def __init__(self, *args: object) -> None:
        pass


class LeaveParser[T: Leave](ValueParser[T]):
    """Leave value parser."""

    def __init__(self, value_type: type[T]) -> None:
        self._value_type = value_type

    def value_type(self) -> type[T]:
        """Get value type."""
        return self._value_type

    def from_str(self, value_str: str) -> T:
        """Convert value string to value."""
        return self._value_type(value_str)

    def to_str(self, value: T) -> str:
        """Convert value to string."""
        return str(value)


STRING_PARSER = LeaveParser(str)
CHAR_PARSER = LeaveParser(str)
INTEGER_PARSER = LeaveParser(int)
FLOAT_PARSER = LeaveParser(float)


class ListLikeParser[T: CanConvert](ValueParser[list[T]]):
    """List-like value parser."""

    def __init__(self, item_type: type[T]) -> None:
        self._item_type = item_type

    def value_type(self) -> type[list[T]]:
        """Get value type."""
        return list[T]

    def item_type(self) -> type[T]:
        """Get value type."""
        return self._item_type


class ListParser[T: CanConvert](ListLikeParser[T]):
    """List value parser."""

    def from_str(self, list_string: str) -> list[T]:
        """Convert a string to a list."""
        return list[T](map(self._item_type, list_string.split(",")))

    def to_str(self, items: Iterable[T]) -> str:
        """Convert a list to a string."""
        return ",".join(map(str, items))


class NumericArrayParser[T: int | float](ListLikeParser[T]):
    """Numeric array value parser."""

    @classmethod
    def compute_subtype(cls, array: list[T]) -> IntOrFloatArrayTypes:
        """Compute numeric array type."""
        return gfapy.NumericArray(array).compute_subtype()

    def from_str(self, array_string: str) -> list[T]:
        """Convert a string to an array."""
        return list[T](
            map(self._item_type, gfapy.NumericArray(array_string)),
        )

    def to_str(self, array: Iterable[T]) -> str:
        """Convert an array to a string."""
        return str(gfapy.NumericArray(array))


INTEGER_NUMERIC_ARRAY_PARSER = NumericArrayParser(int)
FLOAT_NUMERIC_ARRAY_PARSER = NumericArrayParser(float)


class Field:
    """GFA field."""

    def __init__(self, name: str, position: int) -> None:
        self._name = name
        self._position = position

    def name(self) -> str:
        """Get name."""
        return self._name

    def position(self) -> int:
        """Get field position."""
        return self._position


class FieldBase[L: gfapy.Line, T: CanConvert](abc.ABC):
    """Field getter and setter."""

    VALUE_PARSER: ValueParser[T]

    def __init__(self, field: Field) -> None:
        self._field = field

    def field(self) -> Field:
        """Get field."""
        return self._field

    def from_line_str(self, line_str: str) -> T:
        """Get field from line string."""
        return self.from_split_line_str(line_str.split())

    def from_split_line_str(self, split_line_str: list[str]) -> T:
        """Get field from split line string."""
        return self.VALUE_PARSER.from_str(split_line_str[self.field().position()])

    def from_line(self, line: L) -> T:
        """Get field from line."""
        return self.VALUE_PARSER.value_type()(line.get(self.field().name()))

    def set_for_line_str(self, line_str: str, value: T) -> str:
        """Set field value."""
        split_line_str = line_str.split()
        self.set_for_split_line_str(split_line_str, value)
        return "\t".join(split_line_str)

    def set_for_split_line_str(self, split_line_str: list[str], value: T) -> None:
        """Set field value."""
        split_line_str[self.field().position()] = self.VALUE_PARSER.to_str(value)

    def set_for_line(self, line: L, value: T) -> None:
        """Set field value."""
        line.set(self.field().name(), value)


class FieldLeave[L: gfapy.Line, T: Leave](FieldBase[L, T]):
    """Field getter and setter."""

    VALUE_PARSER: LeaveParser[T]


class StringField[L: gfapy.Line](FieldLeave[L, str]):
    """String field getter and setter."""

    VALUE_PARSER = LeaveParser(str)


class CharField[L: gfapy.Line](FieldLeave[L, str]):
    """Char field getter and setter."""

    VALUE_PARSER = LeaveParser(str)


class IntegerField[L: gfapy.Line](FieldLeave[L, int]):
    """Integer field getter and setter."""

    VALUE_PARSER = LeaveParser(int)


class FloatField[L: gfapy.Line](FieldLeave[L, float]):
    """Float field getter and setter."""

    VALUE_PARSER = LeaveParser(float)


class ListLikeField[L: gfapy.Line, T: CanConvert](FieldBase[L, list[T]]):
    """List-like field getter and setter."""

    VALUE_PARSER: ListLikeParser[T]

    def item_from_line_str(self, line_str: str, index: int) -> T:
        """Get item from line string."""
        return self.from_line_str(line_str)[index]

    def item_from_split_line_str(self, split_line_str: list[str], index: int) -> T:
        """Get item from split line string."""
        return self.from_split_line_str(split_line_str)[index]

    def item_from_line(self, line: L, index: int) -> T:
        """Get item from line."""
        return self.from_line(line)[index]

    def set_item_for_line_str(self, line_str: str, index: int, value: T) -> str:
        """Set field value."""
        split_line_str = line_str.split()
        self.set_item_for_split_line_str(split_line_str, index, value)
        return "\t".join(split_line_str)

    def set_item_for_split_line_str(
        self,
        split_line_str: list[str],
        index: int,
        value: T,
    ) -> None:
        """Set field value."""
        field_pos = self.field().position()
        full_list = self.VALUE_PARSER.from_str(split_line_str[field_pos])
        full_list[index] = value
        split_line_str[field_pos] = self.VALUE_PARSER.to_str(full_list)

    def set_item_for_line(self, line: L, index: int, value: T) -> None:
        """Set field value."""
        full_list = self.VALUE_PARSER.value_type()(line.get(self.field().name()))
        full_list[index] = value
        self.set_for_line(line, full_list)


class IntegerNumericArrayField[L: gfapy.Line](ListLikeField[L, int]):
    """Integer numeric array field getter and setter."""

    VALUE_PARSER = INTEGER_NUMERIC_ARRAY_PARSER


class FloatNumericArrayField[L: gfapy.Line](ListLikeField[L, float]):
    """Float numeric array field getter and setter."""

    VALUE_PARSER = FLOAT_NUMERIC_ARRAY_PARSER


class ListField[L: gfapy.Line, T: CanConvert](ListLikeField[L, T]):
    """List field getter and setter."""

    VALUE_PARSER: ListParser[T]


# FEATURE JSON and byte array for fields
class FieldBuilder[L: gfapy.Line]:
    """GFA line field builder.

    Example
    -------
    >>> SEGMENT_FIELD_BUILDER = FieldBuilder()
    >>> SEGMENT_NAME_FIELD = SEGMENT_FIELD_BUILDER.new_string_field("name")
    >>> SEGMENT_SEQUENCE_FIELD = SEGMENT_FIELD_BUILDER.new_string_field("sequence")
    >>> print(SEGMENT_NAME_FIELD.position())
    1
    >>> print(SEGMENT_SEQUENCE_FIELD.position())
    2
    >>> print(SEGMENT_FIELD_BUILDER.names())
    ('name', 'sequence')
    """

    def __init__(self) -> None:
        self.__names: list[str] = []

    def names(self) -> tuple[str, ...]:
        """Get names."""
        return tuple(self.__names)

    def new[T: FieldBase](self, name: str, field_type: type[T]) -> T:
        """Create a new field."""
        self.__names.append(name)
        return field_type(Field(name, len(self.__names)))

    def new_string_field(self, name: str) -> StringField[L]:
        """Create a new string field."""
        return self.new(name, StringField[L])

    def new_char_field(self, name: str) -> CharField[L]:
        """Create a new char field."""
        return self.new(name, CharField[L])

    def new_integer_field(self, name: str) -> IntegerField[L]:
        """Create a new integer field."""
        return self.new(name, IntegerField[L])

    def new_float_field(self, name: str) -> FloatField[L]:
        """Create a new float field."""
        return self.new(name, FloatField[L])

    def new_integer_numeric_array_field(self, name: str) -> IntegerNumericArrayField[L]:
        """Create a new integer numeric array field."""
        return self.new(name, IntegerNumericArrayField[L])

    def new_float_numeric_array_field(self, name: str) -> FloatNumericArrayField[L]:
        """Create a new float numeric array field."""
        return self.new(name, FloatNumericArrayField[L])


class Fields[L: gfapy.Line]:
    """GFA line fields."""

    _FIELD_BUILDER: FieldBuilder[L]

    @classmethod
    def number_of_fields(cls) -> int:
        """Get number of fields."""
        return len(cls._FIELD_BUILDER.names())


class TagString:
    """Tag string convertor."""

    @classmethod
    def value(cls, tag_id_type_value: str) -> str:
        """Extract tag value (str)."""
        return tag_id_type_value[5:]

    @classmethod
    def to_str(cls, tag_id: str, type_str: str, value: str) -> str:
        """Compose tag name and value."""
        return f"{tag_id}:{type_str}:{value}"


class TagBase[L: gfapy.Line, T: CanConvert](abc.ABC):
    """Tag getter and setter."""

    # TODO delete tag    # line.delete(tag_id)

    GFA_TYPE: TagTypes
    VALUE_PARSER: ValueParser[T]

    def __init__(self, identifier: str, first_tag_position: int) -> None:
        self._identifier = identifier
        self._first_tag_position = first_tag_position

    def is_defined(self, line: L) -> Maybe[TagTypes]:
        """Check if tag is defined."""
        return Maybe.from_optional(line.get_datatype(self._identifier)).map(
            lambda data_type: TagTypes(data_type),
        )

    def define(self, line: L) -> None:
        """Define tag."""
        line.set_datatype(self._identifier, self.GFA_TYPE)

    def identifier(self) -> str:
        """Get tag ID."""
        return self._identifier

    def in_line(self, line: L) -> bool:
        """Check if line has tag."""
        return self.from_line(line) is Some

    def in_line_str(self, line_str: str) -> bool:
        """Check if line string has tag."""
        return self.in_line_split_str(line_str.split()) is not Nothing

    def in_line_split_str(self, split_line_str: list[str]) -> Maybe[int]:
        """Search tag in line."""
        for i, item in enumerate(split_line_str[self._first_tag_position :]):
            if item.startswith(self.identifier()):
                return Some(self._first_tag_position + i)
        return Nothing

    def from_line_str(self, line_str: str) -> Maybe[T]:
        """Get tag from line string."""
        return self.from_split_line_str(line_str.split())

    def from_split_line_str(self, split_line_str: list[str]) -> Maybe[T]:
        """Get tag from split line string."""
        return self.in_line_split_str(split_line_str).map(
            lambda pos: self.VALUE_PARSER.from_str(
                TagString.value(split_line_str[pos]),
            ),
        )

    def from_line(self, line: L) -> Maybe[T]:
        """Get tag from line."""
        return Maybe.from_optional(line.get(self.identifier())).map(
            lambda value: self.VALUE_PARSER.value_type()(value),
        )

    def set_for_line_str(self, line_str: str, value: T) -> str:
        """Return the new string line with the tag updated."""
        split_line_str = line_str.split()
        self.set_for_split_line_str(split_line_str, value)
        return "\t".join(split_line_str)

    def set_for_split_line_str(self, split_line_str: list[str], value: T) -> None:
        """Set tag value."""
        match self.in_line_split_str(split_line_str):
            case Some(pos):
                split_line_str[pos] = TagString.to_str(
                    self.identifier(),
                    self.GFA_TYPE.value,
                    self.VALUE_PARSER.to_str(value),
                )
            case Maybe.empty:
                split_line_str.append(
                    TagString.to_str(
                        self.identifier(),
                        self.GFA_TYPE.value,
                        self.VALUE_PARSER.to_str(value),
                    ),
                )

    def set_for_line(self, line: L, value: T) -> None:
        """Set tag value."""
        line.set(self.identifier(), value)


class TagLeave[L: gfapy.Line, T: Leave](TagBase[L, T]):
    """Tag getter and setter."""

    VALUE_PARSER: LeaveParser[T]


class StringTag[L: gfapy.Line](TagBase[L, str]):
    """String tag getter and setter."""

    GFA_TYPE = TagTypes.STRING
    VALUE_PARSER = STRING_PARSER


class CharTag[L: gfapy.Line](TagBase[L, str]):
    """Char tag getter and setter."""

    GFA_TYPE = TagTypes.CHAR
    VALUE_PARSER = CHAR_PARSER


class IntegerTag[L: gfapy.Line](TagBase[L, int]):
    """Integer tag getter and setter."""

    GFA_TYPE = TagTypes.SIGNED_INT
    VALUE_PARSER = INTEGER_PARSER


class FloatTag[L: gfapy.Line](TagBase[L, float]):
    """Float tag getter and setter."""

    GFA_TYPE = TagTypes.FLOAT
    VALUE_PARSER = FLOAT_PARSER


class NumericArrayTag[L: gfapy.Line, T: Leave](
    TagBase[L, list[T]],
):
    """Numeric array tag getter and setter."""

    GFA_TYPE = TagTypes.INT_OR_FLOAT_ARRAY


class IntegerNumericArrayTag[L: gfapy.Line](
    NumericArrayTag[L, int],
):
    """Integer numeric array tag getter and setter."""

    VALUE_PARSER = INTEGER_NUMERIC_ARRAY_PARSER


class FloatNumericArrayTag[L: gfapy.Line](
    NumericArrayTag[L, float],
):
    """Float numeric array tag getter and setter."""

    VALUE_PARSER = FLOAT_NUMERIC_ARRAY_PARSER


class SelfTagBase[L: gfapy.Line, T: CanConvert](abc.ABC):
    """A tag which can be get or set thanks to fields or other tags."""

    # TODO delete tag    # line.delete(tag_id)

    GFA_TYPE: TagTypes
    VALUE_PARSER: ValueParser[T]

    def __init__(self, identifier: str, first_tag_position: int) -> None:
        self._identifier = identifier
        self._first_tag_position = first_tag_position

    def is_defined(self, line: L) -> Maybe[TagTypes]:
        """Check if tag is defined."""
        return Maybe.from_optional(line.get(self.identifier())).map(
            lambda data_type: TagTypes(data_type),
        )

    def define(self, line: L) -> None:
        """Define tag."""
        line.set_datatype(self._identifier, self.GFA_TYPE)

    def identifier(self) -> str:
        """Get tag ID."""
        return self._identifier

    def in_line(self, line: L) -> bool:
        """Check if line has tag."""
        return line.get(self.identifier()) is not None

    def in_line_str(self, line_str: str) -> bool:
        """Check if line string has tag."""
        return self.in_line_split_str(line_str.split()) is not Nothing

    def in_line_split_str(self, split_line_str: list[str]) -> Maybe[int]:
        """Search tag in line."""
        for i, item in enumerate(split_line_str[self._first_tag_position :]):
            if item.startswith(self.identifier()):
                return Some(self._first_tag_position + i)
        return Nothing

    @abc.abstractmethod
    def compute_value_from_split_line_str(self, split_line_str: list[str]) -> T:
        """Compute value from split line string."""
        raise NotImplementedError

    @abc.abstractmethod
    def compute_value_from_line(self, line: L) -> T:
        """Compute value from line."""
        raise NotImplementedError

    def from_line_str(self, line_str: str) -> T:
        """Get tag from line string."""
        return self.from_split_line_str(line_str.split())

    def from_split_line_str(self, split_line_str: list[str]) -> T:
        """Get tag from split line string."""
        match self.in_line_split_str(split_line_str):
            case Some(pos):
                return self.VALUE_PARSER.from_str(
                    TagString.value(split_line_str[pos]),
                )
            case _:
                return self.compute_value_from_split_line_str(split_line_str)

    def from_line(self, line: L) -> T:
        """Get tag from line."""
        value = line.get(self.identifier())
        if value is None:
            return self.compute_value_from_line(line)
        return self.VALUE_PARSER.value_type()(value)

    def set_for_line_str(self, line_str: str) -> str:
        """Return the new string line with the tag updated."""
        split_line_str = line_str.split()
        self.set_for_split_line_str(split_line_str)
        return "\t".join(split_line_str)

    def set_for_split_line_str(self, split_line_str: list[str]) -> None:
        """Set tag value."""
        match self.in_line_split_str(split_line_str):
            case Some(pos):
                split_line_str[pos] = TagString.to_str(
                    self.identifier(),
                    self.GFA_TYPE.value,
                    self.VALUE_PARSER.to_str(
                        self.compute_value_from_split_line_str(split_line_str),
                    ),
                )
            case _:
                split_line_str.append(
                    TagString.to_str(
                        self.identifier(),
                        self.GFA_TYPE.value,
                        self.VALUE_PARSER.to_str(
                            self.compute_value_from_split_line_str(split_line_str),
                        ),
                    ),
                )

    def set_for_line(self, line: L) -> None:
        """Set tag value."""
        line.set(self.identifier(), self.compute_value_from_line(line))


class SelfTagLeave[L: gfapy.Line, T: Leave](SelfTagBase[L, T]):
    """Self tag getter and setter for leaves."""

    VALUE_PARSER: LeaveParser[T]


class SelfStringTag[L: gfapy.Line](SelfTagLeave[L, str]):
    """A string tag which can be get or set thanks to fields or other tags."""

    GFA_TYPE = TagTypes.STRING
    VALUE_PARSER: LeaveParser[str]


class SelfCharTag[L: gfapy.Line](SelfTagLeave[L, str]):
    """A char tag which can be get or set thanks to fields or other tags."""

    GFA_TYPE = TagTypes.CHAR
    VALUE_PARSER: LeaveParser[str]


class SelfIntegerTag[L: gfapy.Line](SelfTagLeave[L, int]):
    """An integer tag which can be get or set thanks to fields or other tags."""

    GFA_TYPE = TagTypes.SIGNED_INT
    VALUE_PARSER: LeaveParser[int]


class SelfFloatTag[L: gfapy.Line](SelfTagLeave[L, float]):
    """A float tag which can be get or set thanks to fields or other tags."""

    GFA_TYPE = TagTypes.FLOAT
    VALUE_PARSER: LeaveParser[float]


class SelfNumericArrayTag[L: gfapy.Line, T: Leave](
    SelfTagBase[L, list[T]],
):
    """Numeric array tag getter and setter."""

    GFA_TYPE = TagTypes.INT_OR_FLOAT_ARRAY


class SelfIntegerNumericArrayTag[L: gfapy.Line](
    SelfNumericArrayTag[L, int],
):
    """Integer numeric array tag getter and setter."""

    VALUE_PARSER = INTEGER_NUMERIC_ARRAY_PARSER


class SelfFloatNumericArrayTag[L: gfapy.Line](
    SelfNumericArrayTag[L, float],
):
    """Float numeric array tag getter and setter."""

    VALUE_PARSER = FLOAT_NUMERIC_ARRAY_PARSER


class TagBuilder[L: gfapy.Line]:
    """GFA line tag builder.

    Example
    -------
    >>> SEGMENT_TAG_BUILDER = TagBuilder()
    >>> NORMALIZED_COVERAGE_TAG = SEGMENT_TAG_BUILDER.new_float_tag("dp")
    >>> print(SEGMENT_TAG_BUILDER.identifiers())
    ('dp',)
    """

    @classmethod
    def from_fields(cls, fields_type: type[Fields[L]] | None) -> TagBuilder[L]:
        """Create a tag builder from fields type."""
        return cls(fields_type.number_of_fields() if fields_type is not None else 0)

    def __init__(self, first_tag_position: int) -> None:
        self.__identifiers: list[str] = []
        self._first_tag_position = first_tag_position

    def identifiers(self) -> tuple[str, ...]:
        """Get identifiers."""
        return tuple(self.__identifiers)

    def new[T: TagBase](self, name: str, tag_base: type[T]) -> T:
        """Create a new field."""
        self.__identifiers.append(name)
        return tag_base(name, self._first_tag_position)

    def new_string_tag(self, name: str) -> StringTag[L]:
        """Create a new string field."""
        return self.new(name, StringTag[L])

    def new_char_tag(self, name: str) -> CharTag[L]:
        """Create a new char field."""
        return self.new(name, CharTag[L])

    def new_integer_tag(self, name: str) -> IntegerTag[L]:
        """Create a new integer field."""
        return self.new(name, IntegerTag[L])

    def new_float_tag(self, name: str) -> FloatTag[L]:
        """Create a new float field."""
        return self.new(name, FloatTag[L])

    def new_integer_numeric_array_tag(self, name: str) -> IntegerNumericArrayTag[L]:
        """Create a new integer numeric array field."""
        return self.new(name, IntegerNumericArrayTag[L])

    def new_float_numeric_array_tag(self, name: str) -> FloatNumericArrayTag[L]:
        """Create a new float numeric array field."""
        return self.new(name, FloatNumericArrayTag[L])

    def new_self_tag[T: SelfTagBase](self, name: str, self_tag_base: type[T]) -> T:
        """Create a new self tag."""
        self.__identifiers.append(name)
        return self_tag_base(name, self._first_tag_position)


class Tags[L: gfapy.Line]:
    """GFA line tags."""

    _TAG_BUILDER: TagBuilder[L]
