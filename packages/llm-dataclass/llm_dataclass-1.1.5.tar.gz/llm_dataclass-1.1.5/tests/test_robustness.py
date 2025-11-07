from dataclasses import dataclass, field
from textwrap import dedent
from typing import List, Optional

import llm_dataclass


def test_list_type() -> None:
    @dataclass
    class Person:
        name: str
        scores: List[int] = field(default_factory=list)

    schema = llm_dataclass.Schema(Person)

    xml_input = """<Person>
  <name>Alice</name>
  <scores>85</scores>
  <scores>90</scores>
  <scores>95</scores>
</Person>"""
    person_instance = schema.loads(xml_input)
    assert person_instance == Person(name="Alice", scores=[85, 90, 95])


def test_optional_field() -> None:
    @dataclass
    class Person:
        name: str
        nickname: Optional[str] = None

    schema = llm_dataclass.Schema(Person)

    xml_input_with_nickname = """<Person>
  <name>Bob</name>
  <nickname>Bobby</nickname>
</Person>"""
    person_with_nickname = schema.loads(xml_input_with_nickname)
    assert person_with_nickname == Person(name="Bob", nickname="Bobby")


def test_optional_field_missing() -> None:
    @dataclass
    class Person:
        name: str
        nickname: Optional[str] = None

    schema = llm_dataclass.Schema(Person)

    xml_input_without_nickname = """<Person>
  <name>Bob</name>
</Person>"""
    person_without_nickname = schema.loads(xml_input_without_nickname)
    assert person_without_nickname == Person(name="Bob", nickname=None)


def test_optional_dataclass_field_dumping() -> None:
    @dataclass
    class Person:
        name: str
        nickname: Optional[str] = None

    schema = llm_dataclass.Schema(Person)
    expected_schema = dedent("""\
    <Person>
      <name>John Doe</name>
      <nickname>Johnny</nickname>
    </Person>""")

    person_instance = Person(name="John Doe", nickname="Johnny")
    assert schema.dumps(person_instance) == expected_schema


def test_optional_dataclass_field_loading() -> None:
    @dataclass
    class Person:
        name: str
        nickname: Optional[str] = None

    schema = llm_dataclass.Schema(Person)

    xml_input = """<Person>
  <name>John Doe</name>
  <nickname>Johnny</nickname>
</Person>"""
    person_instance = schema.loads(xml_input)
    assert person_instance == Person(name="John Doe", nickname="Johnny")


def test_optional_dataclass_field_loading_missing() -> None:
    @dataclass
    class Person:
        name: str
        nickname: Optional[str] = None

    schema = llm_dataclass.Schema(Person)

    xml_input = """<Person>
  <name>John Doe</name>
</Person>"""
    person_instance = schema.loads(xml_input)
    assert person_instance == Person(name="John Doe", nickname=None)

    schema = llm_dataclass.Schema(Person)

    xml_input = """<Person>
  <name>John Doe</name>
</Person>"""


# now same for dumps


def test_list_dump() -> None:
    @dataclass
    class Person:
        name: str
        scores: List[int] = field(default_factory=list)

    schema = llm_dataclass.Schema(Person)
    expected_schema = dedent("""\
    <Person>
      <name>...</name>
      <scores>...</scores>
      <scores>...</scores>
    </Person>""")

    assert schema.dumps() == expected_schema


def test_list_dump_with_instance() -> None:
    @dataclass
    class Person:
        name: str
        scores: List[int] = field(default_factory=list)

    schema = llm_dataclass.Schema(Person)
    expected_schema = dedent("""\
    <Person>
      <name>Alice</name>
      <scores>85</scores>
      <scores>90</scores>
      <scores>95</scores>
    </Person>""")

    person_instance = Person(name="Alice", scores=[85, 90, 95])
    assert schema.dumps(person_instance) == expected_schema


def test_optional_field_dump() -> None:
    @dataclass
    class Person:
        name: str
        nickname: Optional[str] = None

    schema = llm_dataclass.Schema(Person)
    expected_schema = dedent("""\
    <Person>
      <name>...</name>
      <nickname>...</nickname>
    </Person>""")

    assert schema.dumps() == expected_schema


def test_optional_dataclass_nested_dumping() -> None:
    @dataclass
    class Address:
        street: str
        city: str

    @dataclass
    class Person:
        name: str
        age: int
        address: Optional[Address] = None

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
