import sys
from dataclasses import dataclass, field

import pytest

import llm_dataclass


@pytest.mark.skipif(
    sys.version_info < (3, 10), reason="Union syntax (int | None) requires Python 3.10+"
)
def test_or() -> None:
    @dataclass
    class OrExample:
        value: int | None = field(default=None)

    schema = llm_dataclass.Schema(OrExample)
    expected_schema = "<OrExample>\n  <value>...</value>\n</OrExample>"
    assert schema.dumps() == expected_schema

    expected_schema_with_value = "<OrExample>\n  <value>42</value>\n</OrExample>"
    assert schema.dumps(OrExample(value=42)) == expected_schema_with_value
