from dataclasses import dataclass
from textwrap import dedent

import llm_dataclass


def test_xml_root() -> None:
    @dataclass
    class ItemClass:
        XML_ROOT_TAG = "item"
        name: str
        value: int

    schema = llm_dataclass.Schema(ItemClass)
    item = ItemClass(name="example", value=42)
    xml_output = schema.dumps(item)
    expected_xml = dedent("""
    <item>
      <name>example</name>
      <value>42</value>
    </item>
    """).strip()
    assert xml_output == expected_xml
