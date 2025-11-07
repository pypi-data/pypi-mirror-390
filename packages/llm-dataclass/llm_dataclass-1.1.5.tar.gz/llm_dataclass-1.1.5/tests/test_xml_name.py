import sys

import pytest


def test_xml_name_loading() -> None:
    from dataclasses import dataclass, field

    import llm_dataclass

    @dataclass
    class Person:
        full_name: str = field(metadata={"xml": {"name": "name"}})
        age: int

    schema = llm_dataclass.Schema(Person)

    xml_input = """<Person>
  <name>John Doe</name>
  <age>30</age>
</Person>"""
    person_instance = schema.loads(xml_input)
    assert person_instance == Person(full_name="John Doe", age=30)


def test_xml_name_dumping() -> None:
    from dataclasses import dataclass, field
    from textwrap import dedent

    import llm_dataclass

    @dataclass
    class Person:
        full_name: str = field(metadata={"xml": {"name": "name"}})
        age: int

    schema = llm_dataclass.Schema(Person)
    expected_schema = dedent("""\
    <Person>
      <name>John Doe</name>
      <age>30</age>
    </Person>""")

    person_instance = Person(full_name="John Doe", age=30)
    assert schema.dumps(person_instance) == expected_schema


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="Generic list syntax (list[str]) requires Python 3.9+",
)
def test_xml_name_loading_dataclass_array() -> None:
    from dataclasses import dataclass, field

    import llm_dataclass

    @dataclass
    class Person:
        name: str
        pets: list[str] = field(default_factory=list, metadata={"xml": {"name": "pet"}})

    schema = llm_dataclass.Schema(Person)

    xml_input = """<Person>
  <name>Jane Doe</name>
  <pet>Fluffy</pet>
  <pet>Spot</pet>
</Person>"""

    person_instance = schema.loads(xml_input)
    assert person_instance == Person(name="Jane Doe", pets=["Fluffy", "Spot"])


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="Generic list syntax (list[str]) requires Python 3.9+",
)
def test_xml_name_dumping_dataclass_array() -> None:
    from dataclasses import dataclass, field
    from textwrap import dedent

    import llm_dataclass

    @dataclass
    class Person:
        name: str
        pets: list[str] = field(default_factory=list, metadata={"xml": {"name": "pet"}})

    schema = llm_dataclass.Schema(Person)
    expected_schema = dedent("""\
    <Person>
      <name>Jane Doe</name>
      <pet>Fluffy</pet>
      <pet>Spot</pet>
    </Person>""")

    person_instance = Person(name="Jane Doe", pets=["Fluffy", "Spot"])
    assert schema.dumps(person_instance) == expected_schema
