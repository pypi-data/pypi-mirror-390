import sys
from dataclasses import dataclass, field
from textwrap import dedent

import pytest

import llm_dataclass


def test_dataclass_nested() -> None:
    @dataclass
    class Address:
        street: str
        city: str

    @dataclass
    class Person:
        name: str
        age: int
        address: Address

    schema = llm_dataclass.Schema(Person)
    expected_schema = dedent("""\
    <Person>
      <name>...</name>
      <age>...</age>
      <address>
        <street>...</street>
        <city>...</city>
      </address>
    </Person>""")

    assert schema.dumps() == expected_schema


def test_dataclass_nested_with_instance() -> None:
    @dataclass
    class Address:
        street: str
        city: str

    @dataclass
    class Person:
        name: str
        age: int
        address: Address

    schema = llm_dataclass.Schema(Person)
    expected_schema = dedent("""\
    <Person>
      <name>John Doe</name>
      <age>30</age>
      <address>
        <street>123 Main St</street>
        <city>Anytown</city>
      </address>
    </Person>""")

    address_instance = Address(street="123 Main St", city="Anytown")
    person_instance = Person(name="John Doe", age=30, address=address_instance)

    assert schema.dumps(person_instance) == expected_schema


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="Generic list syntax (list[Pet]) requires Python 3.9+",
)
def test_dataclass_nested_array() -> None:
    @dataclass
    class Pet:
        name: str
        type: str

    @dataclass
    class Person:
        name: str
        pets: list[Pet] = field(default_factory=list, metadata={"xml": {"name": "pet"}})

    schema = llm_dataclass.Schema(Person)
    expected_schema = dedent("""\
    <Person>
      <name>...</name>
      <pet>
        <name>...</name>
        <type>...</type>
      </pet>
      <pet>
        <name>...</name>
        <type>...</type>
      </pet>
    </Person>""")

    assert schema.dumps() == expected_schema


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="Generic list syntax (list[Pet]) requires Python 3.9+",
)
def test_dataclass_nested_array_with_instance() -> None:
    @dataclass
    class Pet:
        name: str
        type: str

    @dataclass
    class Person:
        name: str
        pets: list[Pet] = field(default_factory=list, metadata={"xml": {"name": "pet"}})

    schema = llm_dataclass.Schema(Person)
    expected_schema = dedent("""\
    <Person>
      <name>John Doe</name>
      <pet>
        <name>Fido</name>
        <type>Dog</type>
      </pet>
      <pet>
        <name>Whiskers</name>
        <type>Cat</type>
      </pet>
    </Person>""")

    pet1 = Pet(name="Fido", type="Dog")
    pet2 = Pet(name="Whiskers", type="Cat")
    person_instance = Person(name="John Doe", pets=[pet1, pet2])

    assert schema.dumps(person_instance) == expected_schema
