from dataclasses import dataclass, field
from textwrap import dedent

import llm_dataclass


def test_loads_dataclass_with_namespace() -> None:
    # XML namespaces are not directly supported,
    # but we should be able to parse the prefixes correctly.

    @dataclass
    class Item:
        id: str
        value: str = field(metadata={"xml": {"name": "my:value"}})

    schema = llm_dataclass.Schema(Item, root="item")

    xml_data = """<item>
      <id>123</id>
      <my:value>Test Item</my:value>
    </item>"""

    item = schema.loads(xml_data)
    assert item == Item(id="123", value="Test Item")


def test_dumps_dataclass_with_namespace() -> None:
    @dataclass
    class Item:
        id: str
        value: str = field(metadata={"xml": {"name": "my:value"}})

    schema = llm_dataclass.Schema(Item, root="item")

    item = Item(id="123", value="Test Item")
    xml_data = schema.dumps(item)
    assert xml_data == dedent("""\
    <item>
      <id>123</id>
      <my:value>Test Item</my:value>
    </item>""")
