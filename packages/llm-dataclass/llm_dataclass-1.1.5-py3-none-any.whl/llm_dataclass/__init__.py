import dataclasses
import html
import re
import sys
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

import xmltodict

# Handle Python 3.10+ union types
if sys.version_info >= (3, 10):
    import types

    UnionTypes = (Union, types.UnionType)
else:
    UnionTypes = (Union,)

# Import wrapper classes
from .wrappers import BoolWrapper, FloatWrapper, IntWrapper, StrWrapper

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

    T = TypeVar("T", bound=DataclassInstance)
else:
    T = TypeVar("T")


def find_document(xml: str, root: str) -> str:
    pattern = f"(<{root}[^>]*>.*?</{root}>)"
    match = re.findall(pattern, xml, re.DOTALL)
    if len(match) == 1:
        return match[0]
    elif len(match) > 1:
        raise ValueError(f"Multiple <{root}> tags found in the provided XML.")
    else:
        raise ValueError(f"Tag <{root}> not found in the provided XML.")


def _parse_bool(value: str) -> bool:
    """Parse boolean value from string with flexible input formats."""
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        value_lower = value.lower().strip()
        if value_lower in ("true", "yes", "on", "1"):
            return True
        elif value_lower in ("false", "no", "off", "0"):
            return False
        else:
            raise ValueError(
                f"Cannot convert '{value}' to boolean. Accepted values are: true/false, yes/no, on/off (any casing), 1/0"
            )

    raise ValueError(f"Cannot convert {type(value).__name__} to boolean")


def _escape_xml(text: str) -> str:
    """Escape XML special characters in text content using the standard html module."""
    return html.escape(text, quote=False)


def _validate_type_construction(field_type: Any, field_name: str) -> None:
    """Validate that type constructions are supported (no nested Optional/List combinations)."""
    origin = get_origin(field_type)

    # Handle Optional[T] (which is Union[T, None] or T | None)
    if origin in UnionTypes:
        args = get_args(field_type)
        # For Optional[T], args will be (T, type(None))
        if len(args) == 2 and type(None) in args:
            # Extract the non-None type
            inner_type = args[0] if args[1] is type(None) else args[1]
            inner_origin = get_origin(inner_type)

            # Forbid Optional[List[T]]
            if inner_origin in (list, List):
                raise ValueError(
                    f"Field '{field_name}' has unsupported type Optional[List[T]]. Use List[T] instead and handle None as an empty list."
                )

            # Recursively validate the inner type for nested structures
            if inner_origin is not None:
                _validate_type_construction(inner_type, field_name)
        else:
            # This is a Union with more than 2 types or not Optional-like
            raise ValueError(
                f"Field '{field_name}' has unsupported Union type. Only Optional[T] (Union[T, None]) is supported."
            )

    # Handle List[T]
    elif origin in (list, List):
        args = get_args(field_type)
        if args:
            item_type = args[0]
            item_origin = get_origin(item_type)

            # Forbid List[Optional[T]]
            if item_origin in UnionTypes:
                item_args = get_args(item_type)
                if len(item_args) == 2 and type(None) in item_args:
                    raise ValueError(
                        f"Field '{field_name}' has unsupported type List[Optional[T]]. Use Optional[List[T]] instead or handle None items explicitly."
                    )

            # Forbid List[List[T]] - nested lists
            if item_origin in (list, List):
                raise ValueError(
                    f"Field '{field_name}' has unsupported nested list type List[List[T]]. Nested collections are not supported."
                )

            # Recursively validate the item type for other nested structures
            if item_origin is not None and not dataclasses.is_dataclass(item_type):
                _validate_type_construction(item_type, field_name)


class Schema(Generic[T]):
    def __init__(
        self,
        dataclass_type: Type[T],
        root: Optional[str] = None,
        root_attributes: Optional[dict[str, str]] = None,
    ) -> None:
        assert dataclasses.is_dataclass(dataclass_type), (
            "Provided type is not a dataclass."
        )
        assert isinstance(dataclass_type, type), (
            "Provided dataclass_type is not a type."
        )

        # Validate all field types to ensure supported type constructions
        fields = dataclasses.fields(dataclass_type)
        for field in fields:
            _validate_type_construction(field.type, field.name)

        self.dataclass_type = dataclass_type
        self.root_attributes = root_attributes or {}

        # Priority order: explicit root parameter, then XML_ROOT_TAG attribute, then class name
        if root is not None:
            self.root = root
        else:
            self.root = getattr(dataclass_type, "XML_ROOT_TAG", dataclass_type.__name__)

    def dumps(self, instance: Optional[T] = None) -> str:
        """Generate an example XML schema for the dataclass type."""
        assert instance is None or isinstance(instance, self.dataclass_type), (
            "Provided instance is not of the correct dataclass type."
        )

        # Convert dataclass to dictionary structure
        data_dict = self._dataclass_to_dict(self.dataclass_type, instance)

        # Add root attributes if any are specified
        if self.root_attributes:
            # xmltodict uses '@' prefix for attributes
            for attr_name, attr_value in self.root_attributes.items():
                data_dict[f"@{attr_name}"] = attr_value

        # If the data_dict is empty or only contains attributes, add an empty text node
        # to force xmltodict to generate open/close tags instead of self-closing tags
        has_non_attribute_content = any(not key.startswith("@") for key in data_dict.keys())
        if not has_non_attribute_content:
            data_dict["#text"] = ""

        root_dict = {self.root: data_dict}

        # Use xmltodict.unparse to generate XML
        xml_output = xmltodict.unparse(root_dict, full_document=False, pretty=True)

        # Convert tab indentation to 2-space indentation to match existing format
        xml_output = xml_output.replace("\t", "  ")

        # Clean up empty text nodes - remove the empty text content but keep the structure
        if "#text" in data_dict and data_dict["#text"] == "":
            # Replace the empty text with a newline for proper formatting
            xml_output = xml_output.replace(f"<{self.root}", f"<{self.root}")
            xml_output = xml_output.replace(f"></{self.root}>", f">\n</{self.root}>")

        return xml_output

    def _dataclass_to_dict(self, cls: Type[T], instance: Optional[T]) -> dict:
        """Convert a dataclass instance to a dictionary suitable for xmltodict.unparse."""
        result: dict = {}
        fields = dataclasses.fields(cls)

        for field in fields:
            field_name = field.metadata.get("xml", {}).get("name", field.name)
            value = getattr(instance, field.name) if instance else None

            converted_value = self._convert_field_value(
                field.type, field_name, value, field.metadata
            )

            # Only add to result if the field should be shown
            if converted_value is not None:
                if field_name in result:
                    # Handle multiple values with same name (for lists)
                    if not isinstance(result[field_name], list):
                        result[field_name] = [result[field_name]]
                    if isinstance(converted_value, list):
                        result[field_name].extend(converted_value)
                    else:
                        result[field_name].append(converted_value)
                else:
                    result[field_name] = converted_value

        return result

    def _convert_field_value(
        self,
        field_type: Any,
        field_name: str,
        value: Optional[object],
        metadata: Any = None,
    ) -> Any:
        """Convert a field value to the appropriate format for xmltodict.unparse."""
        origin = get_origin(field_type)

        # Handle Optional[T] (which is Union[T, None] or T | None)
        if origin in UnionTypes:
            args = get_args(field_type)
            # For Optional[T], args will be (T, type(None))
            if len(args) == 2 and type(None) in args:
                # Extract the non-None type
                non_none_type = args[0] if args[1] is type(None) else args[1]
                # Recursively handle the non-None type
                return self._convert_field_value(
                    non_none_type, field_name, value, metadata
                )
            else:
                # This should not happen due to validation in __init__, but handle gracefully
                raise ValueError(
                    f"Unsupported Union type for field '{field_name}': {field_type}"
                )

        elif origin in (list, List):
            item_type = get_args(field_type)[0]
            items = value if value is not None else [None, None]
            assert isinstance(items, list), f"Expected a list for field '{field_name}'"
            converted_items = []
            for item in items:
                converted_item = self._convert_field_value(
                    item_type, field_name, item, None
                )
                converted_items.append(converted_item)
            return converted_items

        elif dataclasses.is_dataclass(field_type):
            instance_value = value if value is not None else None
            return self._dataclass_to_dict(field_type, instance_value)  # type: ignore

        else:
            if value is not None:
                if isinstance(value, bool):
                    return "true" if value else "false"
                else:
                    # Don't escape here - xmltodict.unparse will handle escaping
                    return str(value)
            else:
                # Check if show_placeholder is False in metadata
                if (
                    metadata
                    and metadata.get("xml", {}).get("show_placeholder") is False
                ):
                    return None  # Don't include this field
                return "..."

    def loads(self, xml: str) -> T:
        """Parse XML string into an instance of the dataclass type."""
        document = find_document(xml, self.root)
        data_dict = xmltodict.parse(document, xml_attribs=False)[self.root]
        return self._dict_to_dataclass(self.dataclass_type, data_dict)

    def _dict_to_dataclass(self, cls: Type[T], data: dict) -> T:
        init_kwargs = {}
        for field in dataclasses.fields(cls):
            field_name = field.metadata.get("xml", {}).get("name", field.name)
            field_value = data.get(field_name)
            if field_value is not None:
                origin = get_origin(field.type)

                # Handle Optional[T] (which is Union[T, None] or T | None)
                actual_type = field.type
                if origin in UnionTypes:
                    args = get_args(field.type)
                    if len(args) == 2 and type(None) in args:
                        # Extract the non-None type for Optional[T]
                        actual_type = args[0] if args[1] is type(None) else args[1]
                        origin = get_origin(actual_type)

                if origin in (list, List):
                    item_type = get_args(actual_type)[0]
                    if not isinstance(field_value, list):
                        field_value = [field_value]
                    init_kwargs[field.name] = [
                        self._dict_to_dataclass(item_type, item)  # type: ignore
                        if dataclasses.is_dataclass(item_type)
                        else self._call_type(item_type, item)  # type: ignore
                        for item in field_value
                    ]
                elif dataclasses.is_dataclass(actual_type):
                    init_kwargs[field.name] = self._dict_to_dataclass(
                        actual_type,  # type: ignore
                        field_value,  # type: ignore
                    )  # type: ignore
                else:
                    # Convert string values to the appropriate type using the field type's constructor
                    assert callable(actual_type), (
                        f"Field type for '{field.name}' is not callable."
                    )
                    init_kwargs[field.name] = self._call_type(actual_type, field_value)
        return cls(**init_kwargs)  # type: ignore

    def _adjust_field_type(self, field_type: Any) -> Any:
        origin = get_origin(field_type)
        if origin in UnionTypes:
            args = get_args(field_type)
            non_none_args = [arg for arg in args if arg is not type(None)]
            if len(non_none_args) == 1:
                field_type = self._adjust_field_type(non_none_args[0])
        elif origin in (list, List):
            return list
        return field_type

    def _call_type(self, field_type: Any, value: Any) -> Any:
        assert callable(field_type), f"Field type '{field_type}' is not callable."

        # Raise error if field_type is Optional[List] or similar without proper handling
        origin = get_origin(field_type)
        if origin in UnionTypes and get_args(field_type):
            args = get_args(field_type)
            # Check if this is Optional[T] (Union[T, None] or T | None)
            if len(args) == 2 and type(None) in args:
                inner_type = args[0] if args[1] is type(None) else args[1]
                if get_origin(inner_type) in (list, List):
                    raise ValueError(
                        f"Cannot directly call type '{field_type}' for value '{value}'. Please handle list types explicitly."
                    )

        # Handle optional types
        field_type = self._adjust_field_type(field_type)

        # Special handling for boolean types
        if field_type is bool:
            return _parse_bool(value)

        return field_type(value)


__all__ = ["Schema", "StrWrapper", "IntWrapper", "FloatWrapper", "BoolWrapper"]
