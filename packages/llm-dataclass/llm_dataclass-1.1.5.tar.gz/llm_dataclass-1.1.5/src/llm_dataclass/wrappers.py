"""Simple wrapper dataclasses for basic data types.

These wrapper classes are useful for scenarios where you need to work with
primitive types (str, int, float, bool) in XML schemas that require a root
element wrapping the value.
"""

from dataclasses import dataclass


@dataclass
class StrWrapper:
    """A dataclass wrapper for string values."""

    value: str


@dataclass
class IntWrapper:
    """A dataclass wrapper for integer values."""

    value: int


@dataclass
class FloatWrapper:
    """A dataclass wrapper for float values."""

    value: float


@dataclass
class BoolWrapper:
    """A dataclass wrapper for boolean values."""

    value: bool
