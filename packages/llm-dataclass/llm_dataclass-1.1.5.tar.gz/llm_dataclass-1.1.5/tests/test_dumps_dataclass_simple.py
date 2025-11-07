import sys
from dataclasses import dataclass, field
from textwrap import dedent

import pytest

import llm_dataclass


def test_dataclass_simple() -> None:
    @dataclass
    class Person:
        name: str
        age: int

    schema = llm_dataclass.Schema(Person)
    expected_schema = dedent("""\
    <Person>
      <name>...</name>
      <age>...</age>
    </Person>""")

    assert schema.dumps() == expected_schema


def test_dataclass_simple_with_instance() -> None:
    @dataclass
    class Person:
        name: str
        age: int

    schema = llm_dataclass.Schema(Person)
    expected_schema = dedent("""\
    <Person>
      <name>John Doe</name>
      <age>30</age>
    </Person>""")

    assert schema.dumps(Person(name="John Doe", age=30)) == expected_schema


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="Generic list syntax (list[str]) requires Python 3.9+",
)
def test_dataclass_array() -> None:
    @dataclass
    class Person:
        name: str
        pets: list[str] = field(default_factory=list, metadata={"xml": {"name": "pet"}})

    schema = llm_dataclass.Schema(Person)
    expected_schema = dedent("""\
    <Person>
      <name>...</name>
      <pet>...</pet>
      <pet>...</pet>
    </Person>""")

    assert schema.dumps() == expected_schema
