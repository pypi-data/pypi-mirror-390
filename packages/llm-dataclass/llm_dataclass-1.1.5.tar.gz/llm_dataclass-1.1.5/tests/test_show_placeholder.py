from dataclasses import dataclass, field
from textwrap import dedent
from typing import Optional

import llm_dataclass


def test_optional_normal() -> None:
    @dataclass
    class MyClass:
        field: Optional[int] = field(default=None)

    schema = llm_dataclass.Schema(MyClass)

    expected_schema = dedent("""\
    <MyClass>
      <field>...</field>
    </MyClass>""")

    assert schema.dumps() == expected_schema


def test_optional_show_placeholder_true() -> None:
    @dataclass
    class MyClass:
        field: Optional[int] = field(
            default=None, metadata={"xml": {"show_placeholder": True}}
        )

    schema = llm_dataclass.Schema(MyClass)

    expected_schema = dedent("""\
    <MyClass>
      <field>...</field>
    </MyClass>""")

    assert schema.dumps() == expected_schema


def test_optional_show_placeholder_false() -> None:
    @dataclass
    class MyClass:
        field: Optional[int] = field(
            default=None, metadata={"xml": {"show_placeholder": False}}
        )

    schema = llm_dataclass.Schema(MyClass)

    expected_schema = dedent("""\
    <MyClass>
    </MyClass>""")

    assert schema.dumps() == expected_schema


def test_optional_show_placeholder_false_with_value() -> None:
    @dataclass
    class MyClass:
        field: Optional[int] = field(
            default=None, metadata={"xml": {"show_placeholder": False}}
        )

    schema = llm_dataclass.Schema(MyClass)

    expected_schema = dedent("""\
    <MyClass>
      <field>42</field>
    </MyClass>""")

    assert schema.dumps(MyClass(field=42)) == expected_schema
