from dataclasses import dataclass

import llm_dataclass


def test_extra_data_handling() -> None:
    @dataclass
    class Person:
        name: str
        age: int

    schema = llm_dataclass.Schema(Person, root="person")

    xml_input = """<person>
  <name>John Doe</name>
  <age>30</age>
  <nickname>Johnny</nickname>
  <hobby>Hiking</hobby>
</person>"""
    person = schema.loads(xml_input)
    assert person == Person(name="John Doe", age=30)


def test_extra_data_with_attributes() -> None:
    @dataclass
    class Item:
        id: str
        value: str

    schema = llm_dataclass.Schema(Item, root="item")

    xml_input = """<item extra_attr="extra_value">
  <id>123</id>
  <value id="value1">Test Item</value>
</item>"""
    item = schema.loads(xml_input)
    assert item == Item(id="123", value="Test Item")
