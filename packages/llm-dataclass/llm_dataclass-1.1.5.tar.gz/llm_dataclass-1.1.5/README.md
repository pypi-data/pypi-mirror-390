# llm-dataclass

[![PyPI - Version](https://img.shields.io/pypi/v/llm-dataclass.svg)](https://pypi.org/project/llm-dataclass)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/llm-dataclass.svg)](https://pypi.org/project/llm-dataclass)

A Python library that provides a dataclass interface for working with XML schemas, specifically designed for LLM (Large Language Model) interactions. This library allows you to define structured data using Python dataclasses and automatically generate XML schemas or parse XML responses into strongly-typed Python objects.

-----

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Basic Dataclass Schema](#basic-dataclass-schema)
  - [Generating XML Schemas](#generating-xml-schemas)
  - [Parsing XML Responses](#parsing-xml-responses)
  - [Working with Lists](#working-with-lists)
  - [Nested Dataclasses](#nested-dataclasses)
  - [Optional Fields](#optional-fields)
    - [Controlling Placeholder Display](#controlling-placeholder-display)
  - [Custom XML Field Names](#custom-xml-field-names)
  - [Custom XML Root Tag](#custom-xml-root-tag)
  - [Handling Extra Data](#handling-extra-data)
- [Type Support](#type-support)
- [Limitations](#limitations)
- [Contributing](#contributing)
- [License](#license)

## Features

- 🔗 **Seamless XML-Dataclass Integration**: Convert between Python dataclasses and XML effortlessly
- 📝 **Schema Generation**: Automatically generate XML schemas from dataclass definitions
- 🔄 **Bidirectional Conversion**: Parse XML into dataclass instances and serialize dataclass instances to XML
- 🏗️ **Nested Structure Support**: Handle complex nested dataclass structures
- 📋 **List/Array Support**: Work with lists of primitive types and dataclass objects
- ⚡ **Type Safety**: Leverages Python's type hints for validation and parsing
- �️ **Flexible Placeholders**: Control placeholder visibility for optional fields in generated templates
- �🎯 **LLM-Friendly**: Designed specifically for LLM prompt engineering and response parsing

## Installation

```console
pip install llm-dataclass
```

## Quick Start

### Parsing XML to Dataclass Objects

Parse XML responses from LLMs into strongly-typed Python objects:

```python
from dataclasses import dataclass
import llm_dataclass

@dataclass
class Person:
    name: str
    age: int

# Create a schema with custom root element name
schema = llm_dataclass.Schema(Person, root="user")

# Parse XML response from LLM
xml_response = """
This is your response:

<user>
  <name>John Doe</name>
  <age>30</age>
</user>

Let me know if you need anything else.
"""

person = schema.loads(xml_response)
print(person)  # Person(name='John Doe', age=30)
```

### Generating XML Templates for Prompts

Generate XML templates to include in LLM prompts as response format examples:

```python
from dataclasses import dataclass
import llm_dataclass

@dataclass
class Person:
    name: str
    age: int

# Create schema with custom root - useful when you want specific XML tag names
schema = llm_dataclass.Schema(Person, root="employee")

# Generate empty XML template for LLM prompts
xml_template = schema.dumps()
print(xml_template)
# Output:
# <employee>
#   <name>...</name>
#   <age>...</age>
# </employee>
```

### Serializing Dataclass Instances to XML

Convert Python dataclass instances into XML format:

```python
from dataclasses import dataclass
import llm_dataclass

@dataclass
class Person:
    name: str
    age: int

# Use default root (dataclass name) or specify custom root
schema = llm_dataclass.Schema(Person, root="contact")

# Create a dataclass instance
person = Person(name="Alice Smith", age=25)

# Serialize to XML
xml_output = schema.dumps(person)
print(xml_output)
# Output:
# <contact>
#   <name>Alice Smith</name>
#   <age>25</age>
# </contact>
```

## Usage

### Basic Dataclass Schema

Define your data structure using Python dataclasses:

```python
from dataclasses import dataclass
import llm_dataclass

@dataclass
class Product:
    name: str
    price: float
    in_stock: bool

schema = llm_dataclass.Schema(Product)
```

### Generating XML Schemas

Generate XML templates for LLM prompts:

```python
# Generate empty template
template = schema.dumps()

# Generate template with example data
example_product = Product(name="Widget", price=19.99, in_stock=True)
template_with_data = schema.dumps(example_product)
```

### Parsing XML Responses

Parse XML responses from LLMs into typed Python objects:

```python
xml_response = """<Product>
  <name>Super Widget</name>
  <price>29.99</price>
  <in_stock>true</in_stock>
</Product>"""

product = schema.loads(xml_response)
# Returns: Product(name='Super Widget', price=29.99, in_stock=True)
```

### Working with Lists

Handle lists of primitive types or objects:

```python
from dataclasses import dataclass, field

@dataclass
class ShoppingList:
    items: list[str] = field(metadata={"xml": {"name": "item"}})

schema = llm_dataclass.Schema(ShoppingList)

# Parsing XML with multiple items
xml_data = """<ShoppingList>
  <item>Apples</item>
  <item>Bananas</item>
  <item>Cherries</item>
</ShoppingList>"""

shopping_list = schema.loads(xml_data)
# Returns: ShoppingList(items=['Apples', 'Bananas', 'Cherries'])
```

### Nested Dataclasses

Support for complex nested structures:

```python
@dataclass
class Address:
    street: str
    city: str
    zipcode: str

@dataclass
class Person:
    name: str
    address: Address

schema = llm_dataclass.Schema(Person)

xml_data = """<Person>
  <name>Jane Smith</name>
  <address>
    <street>123 Main St</street>
    <city>Anytown</city>
    <zipcode>12345</zipcode>
  </address>
</Person>"""

person = schema.loads(xml_data)
```

### Optional Fields

Handle optional fields with proper type annotations:

```python
from typing import Optional

@dataclass
class User:
    username: str
    email: Optional[str] = None
    age: Optional[int] = None

schema = llm_dataclass.Schema(User)
```

#### Controlling Placeholder Display

By default, optional fields with `None` values show placeholders (`...`) in generated XML templates. You can control this behavior using the `show_placeholder` metadata option:

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class UserProfile:
    username: str
    # Default behavior - shows placeholder when None
    email: Optional[str] = None
    # Explicit placeholder - same as default
    phone: Optional[str] = field(default=None, metadata={"xml": {"show_placeholder": True}})
    # Hide placeholder when None
    bio: Optional[str] = field(default=None, metadata={"xml": {"show_placeholder": False}})

schema = llm_dataclass.Schema(UserProfile)

# Generate template with mixed placeholder behavior
template = schema.dumps()
print(template)
# Output:
# <UserProfile>
#   <username>...</username>
#   <email>...</email>
#   <phone>...</phone>
# </UserProfile>
# Note: 'bio' field is omitted since show_placeholder=False

# When field has actual value, show_placeholder setting is ignored
user = UserProfile(username="john_doe", bio="Software engineer")
xml_output = schema.dumps(user)
print(xml_output)
# Output:
# <UserProfile>
#   <username>john_doe</username>
#   <email>...</email>
#   <phone>...</phone>
#   <bio>Software engineer</bio>
# </UserProfile>
```

**Use cases for `show_placeholder: False`**:
- **Cleaner LLM prompts**: Reduce template clutter by hiding optional fields
- **Conditional fields**: Only show fields in templates when they have meaningful values
- **Progressive disclosure**: Generate minimal schemas that only include essential fields

### Custom XML Field Names

Customize XML element names using field metadata:

```python
@dataclass
class Book:
    title: str
    author_name: str = field(metadata={"xml": {"name": "author"}})
    
schema = llm_dataclass.Schema(Book)
# Will use <author> instead of <author_name> in XML
```

### Custom XML Root Tag

Customize the root XML element name using the `XML_ROOT_TAG` class attribute:

```python
@dataclass
class Product:
    XML_ROOT_TAG = "item"  # Custom root tag name
    name: str
    price: float

schema = llm_dataclass.Schema(Product)
xml_output = schema.dumps(Product(name="Widget", price=19.99))
# Output: <item><name>Widget</name><price>19.99</price></item>
```

Priority order for root tag selection:
1. Explicit `root` parameter: `Schema(Product, root="custom")`
2. `XML_ROOT_TAG` class attribute
3. Class name (default)

### Handling Extra Data

The library is designed to be robust when working with LLM responses:

- **Extra text before/after XML**: Automatically extracts XML from responses containing additional explanatory text
- **Extra XML elements**: Ignores XML elements that don't correspond to dataclass fields
- **Flexible parsing**: Only extracts the specific data defined in your dataclass schema

## Type Support

The library supports the following Python types:

- **Primitive types**: `str`, `int`, `float`, `bool`
- **Optional types**: `Optional[T]` or `Union[T, None]`
- **Lists**: `list[T]` or `List[T]`
- **Nested dataclasses**: Any dataclass type
- **Custom types**: Any type with a constructor that accepts a string

**Convenience Wrappers**: The library also provides simple wrapper dataclasses (`StrWrapper`, `IntWrapper`, `FloatWrapper`, `BoolWrapper`) for scenarios where you need to wrap primitive values in a root XML element.

## Limitations

To ensure robust XML parsing, the library has some intentional limitations:

- **No XML attributes**: XML attributes are not supported - only XML elements are parsed
- **No nested lists**: `List[List[T]]` is not supported
- **No optional lists**: `Optional[List[T]]` is not supported (use `List[T]` with empty list handling)
- **No list of optionals**: `List[Optional[T]]` is not supported
- **Union types**: Only `Optional[T]` (Union with None) is supported

These limitations help prevent ambiguous XML structures and parsing edge cases.

## Examples

You can find more examples in the [examples](https://github.com/bytehexe/llm-dataclass/blob/main/examples/examples.md) section of the repository, demonstrating various use cases and features of the `llm-dataclass` library.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

`llm-dataclass` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
