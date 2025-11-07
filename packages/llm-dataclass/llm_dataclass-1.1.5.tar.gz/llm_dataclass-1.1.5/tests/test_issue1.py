import dataclasses
import sys

import pytest

import llm_dataclass


@pytest.mark.skipif(sys.version_info < (3, 10), reason="Syntax requires Python 3.10+")
def test_issue1() -> None:
    @dataclasses.dataclass
    class AssetMetadata:
        XML_ROOT_TAG = "metadata"
        identifier: str | None = dataclasses.field(
            default=None,
            metadata={"xml": {"name": "dc:identifier", "show_placeholder": False}},
        )
        title: str | None = dataclasses.field(
            default=None, metadata={"xml": {"name": "dc:title"}}
        )

    load_data = """
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:identifier>unique-id-123</dc:identifier>
        <dc:title>Sample Title</dc:title>
    </metadata>
    """

    schema = llm_dataclass.Schema(AssetMetadata)
    schema.loads(load_data)
