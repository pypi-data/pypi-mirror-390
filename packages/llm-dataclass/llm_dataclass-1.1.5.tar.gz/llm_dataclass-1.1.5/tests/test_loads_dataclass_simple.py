import sys

import pytest


def test_dataclass_simple_loads() -> None:
    from dataclasses import dataclass

    import llm_dataclass

    @dataclass
    class Person:
        name: str
        age: int

    schema = llm_dataclass.Schema(Person)

    xml_input = """<Person>
  <name>John Doe</name>
  <age>30</age>
</Person>"""

    person_instance = schema.loads(xml_input)
    assert person_instance == Person(name="John Doe", age=30)


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="Generic list syntax (list[str]) requires Python 3.9+",
)
def test_dataclass_array_loads() -> None:
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
