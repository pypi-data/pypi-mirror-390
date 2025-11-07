from dataclasses import dataclass
from textwrap import dedent

import llm_dataclass


def test_dump_brackets_in_field_values() -> None:
    @dataclass
    class Message:
        content: str

    schema = llm_dataclass.Schema(Message)
    expected_schema = dedent("""\
    <Message>
      <content>Hello &lt;World&gt;!</content>
    </Message>""")

    message_instance = Message(content="Hello <World>!")
    assert schema.dumps(message_instance) == expected_schema


def test_dump_ampersand_in_field_values() -> None:
    @dataclass
    class Message:
        content: str

    schema = llm_dataclass.Schema(Message)
    expected_schema = dedent("""\
    <Message>
      <content>Rock &amp; Roll</content>
    </Message>""")

    message_instance = Message(content="Rock & Roll")
    assert schema.dumps(message_instance) == expected_schema
