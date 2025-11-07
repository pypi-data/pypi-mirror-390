from dataclasses import dataclass
from typing import Optional

import llm_dataclass


def test_empty_root() -> None:
    @dataclass
    class Empty:
        pass

    schema = llm_dataclass.Schema(Empty)
    expected_schema = "<Empty>\n</Empty>"

    assert schema.dumps() == expected_schema


def test_empty_root_with_instance() -> None:
    @dataclass
    class Empty:
        pass

    schema = llm_dataclass.Schema(Empty)
    expected_schema = "<Empty>\n</Empty>"

    assert schema.dumps(Empty()) == expected_schema


def test_empty_root_loads() -> None:
    @dataclass
    class Empty:
        pass

    schema = llm_dataclass.Schema(Empty)

    xml_input = "<Empty>\n</Empty>"

    empty_instance = schema.loads(xml_input)
    assert empty_instance == Empty()


def test_empty_root_optional_field_dumps() -> None:
    @dataclass
    class Empty:
        optional_field: Optional[int] = None

    schema = llm_dataclass.Schema(Empty)
    expected_schema = "<Empty>\n  <optional_field>...</optional_field>\n</Empty>"

    assert schema.dumps() == expected_schema


def test_empty_root_optional_field_dumps_instance() -> None:
    @dataclass
    class Empty:
        optional_field: Optional[int] = None

    schema = llm_dataclass.Schema(Empty)
    expected_schema = "<Empty>\n  <optional_field>42</optional_field>\n</Empty>"

    assert schema.dumps(Empty(optional_field=42)) == expected_schema


def test_empty_root_optional_field_dumps_empty_instance() -> None:
    @dataclass
    class Empty:
        optional_field: Optional[int] = None

    schema = llm_dataclass.Schema(Empty)
    expected_schema = "<Empty>\n  <optional_field>...</optional_field>\n</Empty>"

    assert schema.dumps(Empty()) == expected_schema
