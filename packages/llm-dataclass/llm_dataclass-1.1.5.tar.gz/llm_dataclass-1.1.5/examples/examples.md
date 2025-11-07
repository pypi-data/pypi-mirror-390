# Examples

Here are some examples demonstrating how to use the `llm-dataclass` library.

## [Boolean Question](boolean_question.py)
A simple example showing how to ask a yes/no question to an LLM and get a structured boolean response. This example demonstrates:
- Using `llm_dataclass.BoolWrapper` for boolean responses
- Basic prompt construction with XML schema examples
- Error handling and retry logic with Ollama

## [Image Classification](image_classification.py)
An advanced example that processes images with vision models to extract structured metadata. This example demonstrates:
- Working with multimodal LLMs (text + image input)
- Custom dataclass with Dublin Core metadata fields
- XML field name mapping using metadata annotations
- Processing image files with Ollama's vision capabilities

## [Work Classification](work_classification.py)
A complex example showing how to classify and analyze creative works like literature. This example demonstrates:
- Nested dataclass structures for complex schemas
- Schema.org vocabulary integration
- RDF/XML namespace handling
- Text analysis and literary classification

