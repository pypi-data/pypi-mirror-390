import pathlib
from dataclasses import dataclass, field
from textwrap import dedent
from typing import TYPE_CHECKING, List, TypeVar

import llm_dataclass

if TYPE_CHECKING:
    from _typeshed import DataclassInstance
    T = TypeVar('T', bound=DataclassInstance)
else:
    T = TypeVar('T')

def ask_ollama(prompt: str, model: str, image: pathlib.Path, schema: llm_dataclass.Schema[T], **params) -> T:
    """
    Ask a question to Ollama and parse the response using the provided schema.

    Args:
        prompt: The question to ask
        model: The Ollama model to use for the chat
        schema: A schema that defines the expected response structure
    Returns:
        An instance of the dataclass type that the schema represents
    """
    try:
        import ollama
    except ImportError:
        raise ImportError("The 'ollama' package is required to use this function. Please install it via 'pip install ollama'.")

    example = schema.dumps()
    prompt = prompt + '\n' + dedent("""
    Please resond with an XML object containing the answer.
    Example Response:
    """).strip() + '\n' + example

    for _ in range(3):  # Retry up to 3 times
        print("Sending prompt to Ollama:")
        print(prompt)

        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt, "images": [str(image)]}],
            **params,
        )

        print("Received response from Ollama:")
        print(response["message"]["content"])

        try:

            result = schema.loads(response["message"]["content"])
        except RuntimeError:
            print("Failed to parse response, retrying...")
            continue

        return result

if __name__ == "__main__":

    @dataclass
    class Metadata:
        title: str = field(metadata={"xml": {"name": "dc:title"}})
        description: str = field(metadata={"xml": {"name": "dc:description"}})
        subject: List[str] = field(metadata={"xml": {"name": "dc:subject"}})

    schema = llm_dataclass.Schema(Metadata, root="metadata")

    question = dedent("""
    Can you output the metadata for the content of this image?
    """).strip()

    model = "llava:latest"
    image = pathlib.Path(__file__).parent / "image.jpg"

    answer = ask_ollama(question, model, image, schema)
    print()
    print("Final Result:")
    print(f"Question: {question}")
    print(f"Answer: {answer}")

# Example output when running this script:
"""
Sending prompt to Ollama:
Can you output the metadata for the content of this image?
Please resond with an XML object containing the answer.
Example Response:
<metadata>
  <dc:title>...</dc:title>
  <dc:description>...</dc:description>
  <dc:subject>...</dc:subject>
  <dc:subject>...</dc:subject>
</metadata>
Received response from Ollama:
 Certainly! Below is an XML object with the metadata for the content of the image you provided.

```xml
<metadata>
  <dc:title>Mona Lisa</dc:title>
  <dc:description>This is a digital reproduction of Leonardo da Vinci's famous painting, the Mona Lisa.</dc:description>
  <dc:subject>Painting</dc:subject>
  <dc:subject>Leonardo da Vinci</dc:subject>
  <dc:subject>Mona Lisa</dc:subject>
  <dc:creator>Leonardo da Vinci</dc:creator>
  <dc:date>1503-1504</dc:date>
  <dc:type>Painting</dc:type>
  <dc:format>Digital reproduction</dc:format>
</metadata>
```

Please note that the date provided is an approximation based on historical records and interpretations. The actual creation date of the Mona Lisa may vary slightly depending on the specific interpretation of its creation by art historians.

Final Result:
Question: Can you output the metadata for the content of this image?
Answer: Metadata(title='Mona Lisa', description="This is a digital reproduction of Leonardo da Vinci's famous painting, the Mona Lisa.", subject=['Painting', 'Leonardo da Vinci', 'Mona Lisa'])
"""
