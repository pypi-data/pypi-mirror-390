#!/usr/bin/env python3

import dataclasses
from typing import List, Optional

import pytest

from llm_dataclass import Schema

# Test cases for forbidden type constructions


@dataclasses.dataclass
class ValidSimple:
    name: str
    age: int


@dataclasses.dataclass
class ValidOptional:
    name: Optional[str]
    age: int


@dataclasses.dataclass
class ValidList:
    names: List[str]
    age: int


@dataclasses.dataclass
class InvalidOptionalList:
    # This should be forbidden: Optional[List[T]]
    names: Optional[List[str]]


@dataclasses.dataclass
class InvalidListOptional:
    # This should be forbidden: List[Optional[T]]
    names: List[Optional[str]]


@dataclasses.dataclass
class InvalidNestedList:
    # This should be forbidden: List[List[T]]
    matrix: List[List[str]]


def test_valid_constructions() -> None:
    """Test that valid type constructions work."""
    print("Testing valid constructions...")

    # These should all work
    Schema(ValidSimple)
    print("✓ ValidSimple passed")

    Schema(ValidOptional)
    print("✓ ValidOptional passed")

    Schema(ValidList)
    print("✓ ValidList passed")


def test_invalid_constructions() -> None:
    """Test that invalid type constructions are rejected."""

    # Test Optional[List[T]] - should fail
    with pytest.raises(ValueError, match="Optional\\[List\\[T\\]\\]"):
        Schema(InvalidOptionalList)

    # Test List[Optional[T]] - should fail
    with pytest.raises(ValueError, match="List\\[Optional\\[T\\]\\]"):
        Schema(InvalidListOptional)

    # Test List[List[T]] - should fail
    with pytest.raises(ValueError, match="List\\[List\\[T\\]\\]"):
        Schema(InvalidNestedList)


if __name__ == "__main__":
    test_valid_constructions()
    test_invalid_constructions()
    print("\n🎉 All tests passed!")
