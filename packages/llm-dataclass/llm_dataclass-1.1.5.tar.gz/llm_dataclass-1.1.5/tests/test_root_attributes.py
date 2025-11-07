from dataclasses import dataclass
from textwrap import dedent

import llm_dataclass


def test_root_attributes_simple() -> None:
    @dataclass
    class Person:
        name: str
        age: int

    schema = llm_dataclass.Schema(Person, root_attributes={"xmlns": "http://example.com", "version": "1.0"})
    expected_schema = dedent("""\
    <Person xmlns="http://example.com" version="1.0">
      <name>...</name>
      <age>...</age>
    </Person>""")

    assert schema.dumps() == expected_schema


def test_root_attributes_with_instance() -> None:
    @dataclass
    class Person:
        name: str
        age: int

    schema = llm_dataclass.Schema(Person, root_attributes={"xmlns": "http://example.com"})
    expected_schema = dedent("""\
    <Person xmlns="http://example.com">
      <name>John Doe</name>
      <age>30</age>
    </Person>""")

    assert schema.dumps(Person(name="John Doe", age=30)) == expected_schema


def test_root_attributes_empty_class() -> None:
    @dataclass
    class Empty:
        pass

    schema = llm_dataclass.Schema(Empty, root_attributes={"version": "1.0"})
    expected_schema = dedent("""\
    <Empty version="1.0">
    </Empty>""")

    assert schema.dumps() == expected_schema


def test_no_root_attributes() -> None:
    @dataclass
    class Person:
        name: str
        age: int

    # Test that no attributes works the same as before
    schema = llm_dataclass.Schema(Person)
    expected_schema = dedent("""\
    <Person>
      <name>...</name>
      <age>...</age>
    </Person>""")

    assert schema.dumps() == expected_schema


def test_root_attributes_with_custom_root() -> None:
    @dataclass
    class Person:
        name: str
        age: int

    schema = llm_dataclass.Schema(Person, root="CustomRoot", root_attributes={"id": "123"})
    expected_schema = dedent("""\
    <CustomRoot id="123">
      <name>...</name>
      <age>...</age>
    </CustomRoot>""")

    assert schema.dumps() == expected_schema


def test_root_attributes_special_chars() -> None:
    @dataclass
    class Message:
        content: str

    schema = llm_dataclass.Schema(Message, root_attributes={"class": "test & example"})
    expected_schema = dedent("""\
    <Message class="test &amp; example">
      <content>...</content>
    </Message>""")

    assert schema.dumps() == expected_schema
