"""Test for proper Optional type detection at runtime."""

from dataclasses import dataclass
from typing import Optional, Union, get_args, get_origin

import llm_dataclass


def test_optional_runtime_representation() -> None:
    """Test that demonstrates Optional[T] is actually Union[T, None] at runtime."""
    # This test documents the actual runtime behavior of Optional types
    optional_int = Optional[int]

    # At runtime, Optional[int] is Union[int, None]
    assert get_origin(optional_int) is Union
    assert get_args(optional_int) == (int, type(None))

    # This proves that checking `get_origin(field_type) is Optional` would fail
    assert (
        get_origin(optional_int) is not Optional
    )  # This would be True with old broken code


def test_optional_list_error_handling() -> None:
    """Test that Optional[List[T]] properly raises an error during validation."""
    from typing import List

    @dataclass
    class TestClass:
        # This should trigger an error during validation
        items: Optional[List[str]] = None

    # This should raise an error because Optional[List[T]] is not supported
    try:
        llm_dataclass.Schema(TestClass)
        raise AssertionError("Expected ValueError for Optional[List[T]]")
    except ValueError as e:
        assert "Optional[List[T]]" in str(e)


def test_optional_field_with_complex_type() -> None:
    """Test that Optional fields work correctly with the fixed type detection."""

    @dataclass
    class Address:
        street: str
        city: str

    @dataclass
    class Person:
        name: str
        address: Optional[Address] = None

    # This should work without issues
    schema = llm_dataclass.Schema(Person)

    # Test loading with address
    xml_with_address = """<Person>
  <name>John</name>
  <address>
    <street>123 Main St</street>
    <city>Anytown</city>
  </address>
</Person>"""

    person_with_address = schema.loads(xml_with_address)
    expected_address = Address(street="123 Main St", city="Anytown")
    expected_person = Person(name="John", address=expected_address)
    assert person_with_address == expected_person

    # Test loading without address
    xml_without_address = """<Person>
  <name>Jane</name>
</Person>"""

    person_without_address = schema.loads(xml_without_address)
    expected_person_no_address = Person(name="Jane", address=None)
    assert person_without_address == expected_person_no_address


def test_optional_basic_types() -> None:
    """Test Optional fields with basic types work correctly."""

    @dataclass
    class TestData:
        required_field: str
        optional_int: Optional[int] = None
        optional_str: Optional[str] = None
        optional_bool: Optional[bool] = None
        optional_float: Optional[float] = None

    schema = llm_dataclass.Schema(TestData)

    # Test with all optional fields present
    xml_full = """<TestData>
  <required_field>test</required_field>
  <optional_int>42</optional_int>
  <optional_str>hello</optional_str>
  <optional_bool>true</optional_bool>
  <optional_float>3.14</optional_float>
</TestData>"""

    result_full = schema.loads(xml_full)
    expected_full = TestData(
        required_field="test",
        optional_int=42,
        optional_str="hello",
        optional_bool=True,
        optional_float=3.14,
    )
    assert result_full == expected_full

    # Test with minimal required fields
    xml_minimal = """<TestData>
  <required_field>test</required_field>
</TestData>"""

    result_minimal = schema.loads(xml_minimal)
    expected_minimal = TestData(
        required_field="test",
        optional_int=None,
        optional_str=None,
        optional_bool=None,
        optional_float=None,
    )
    assert result_minimal == expected_minimal


def test_non_optional_union_still_fails() -> None:
    """Test that non-Optional Union types still raise appropriate errors."""

    @dataclass
    class TestClass:
        # This should fail because it's Union[int, str], not Optional
        field: Union[int, str]

    try:
        llm_dataclass.Schema(TestClass)
        raise AssertionError("Expected ValueError for non-Optional Union")
    except ValueError as e:
        assert "unsupported union type" in str(e).lower()
