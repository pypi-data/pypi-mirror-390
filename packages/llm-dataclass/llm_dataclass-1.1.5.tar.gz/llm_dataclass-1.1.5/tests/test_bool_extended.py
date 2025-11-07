import pytest

import llm_dataclass


def test_bool_serialization() -> None:
    """Test that booleans are always serialized as lowercase true/false."""
    schema = llm_dataclass.Schema(llm_dataclass.BoolWrapper, root="bool")

    # Test True -> "true"
    bool_instance_true = llm_dataclass.BoolWrapper(value=True)
    xml_output_true = schema.dumps(bool_instance_true)
    expected_xml_true = "<bool>\n  <value>true</value>\n</bool>"
    assert xml_output_true == expected_xml_true

    # Test False -> "false"
    bool_instance_false = llm_dataclass.BoolWrapper(value=False)
    xml_output_false = schema.dumps(bool_instance_false)
    expected_xml_false = "<bool>\n  <value>false</value>\n</bool>"
    assert xml_output_false == expected_xml_false


def test_bool_deserialization_true_false() -> None:
    """Test parsing true/false (all casings)."""
    schema = llm_dataclass.Schema(llm_dataclass.BoolWrapper, root="bool")

    test_cases = ["true", "True", "TRUE", "false", "False", "FALSE"]
    expected = [True, True, True, False, False, False]

    for test_value, expected_result in zip(test_cases, expected):
        xml_input = f"<bool><value>{test_value}</value></bool>"
        result = schema.loads(xml_input)
        assert result == llm_dataclass.BoolWrapper(value=expected_result), (
            f"Failed for {test_value}"
        )


def test_bool_deserialization_yes_no() -> None:
    """Test parsing yes/no (all casings)."""
    schema = llm_dataclass.Schema(llm_dataclass.BoolWrapper, root="bool")

    test_cases = ["yes", "Yes", "YES", "no", "No", "NO"]
    expected = [True, True, True, False, False, False]

    for test_value, expected_result in zip(test_cases, expected):
        xml_input = f"<bool><value>{test_value}</value></bool>"
        result = schema.loads(xml_input)
        assert result == llm_dataclass.BoolWrapper(value=expected_result), (
            f"Failed for {test_value}"
        )


def test_bool_deserialization_on_off() -> None:
    """Test parsing on/off (all casings)."""
    schema = llm_dataclass.Schema(llm_dataclass.BoolWrapper, root="bool")

    test_cases = ["on", "On", "ON", "off", "Off", "OFF"]
    expected = [True, True, True, False, False, False]

    for test_value, expected_result in zip(test_cases, expected):
        xml_input = f"<bool><value>{test_value}</value></bool>"
        result = schema.loads(xml_input)
        assert result == llm_dataclass.BoolWrapper(value=expected_result), (
            f"Failed for {test_value}"
        )


def test_bool_deserialization_numeric() -> None:
    """Test parsing 1/0."""
    schema = llm_dataclass.Schema(llm_dataclass.BoolWrapper, root="bool")

    test_cases = ["1", "0"]
    expected = [True, False]

    for test_value, expected_result in zip(test_cases, expected):
        xml_input = f"<bool><value>{test_value}</value></bool>"
        result = schema.loads(xml_input)
        assert result == llm_dataclass.BoolWrapper(value=expected_result), (
            f"Failed for {test_value}"
        )


def test_bool_deserialization_whitespace() -> None:
    """Test parsing with extra whitespace."""
    schema = llm_dataclass.Schema(llm_dataclass.BoolWrapper, root="bool")

    test_cases = [" true ", " false ", "\ttrue\t", "\nfalse\n"]
    expected = [True, False, True, False]

    for test_value, expected_result in zip(test_cases, expected):
        xml_input = f"<bool><value>{test_value}</value></bool>"
        result = schema.loads(xml_input)
        assert result == llm_dataclass.BoolWrapper(value=expected_result), (
            f"Failed for '{test_value}'"
        )


def test_bool_deserialization_invalid() -> None:
    """Test that invalid boolean values raise appropriate errors."""
    schema = llm_dataclass.Schema(llm_dataclass.BoolWrapper, root="bool")

    invalid_cases = ["maybe", "2", "enable", "disable", "True!", "nope"]

    for test_value in invalid_cases:
        xml_input = f"<bool><value>{test_value}</value></bool>"
        with pytest.raises(ValueError, match="Cannot convert .* to boolean"):
            schema.loads(xml_input)
