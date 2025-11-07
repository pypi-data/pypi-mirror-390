from textwrap import dedent
from typing import TYPE_CHECKING, TypeVar

import llm_dataclass

if TYPE_CHECKING:
    from _typeshed import DataclassInstance
    T = TypeVar('T', bound=DataclassInstance)
else:
    T = TypeVar('T')

def ask_ollama(prompt: str, model: str, schema: llm_dataclass.Schema[T], **params) -> T:
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

    print("Sending prompt to Ollama:")
    print(prompt)

    for _ in range(3):  # Retry up to 3 times
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            **params,
        )
        try:
            result = schema.loads(response["message"]["content"])
        except RuntimeError:
            print("Failed to parse response, retrying...")
            continue

        print("Received response from Ollama:")
        print(response["message"]["content"])

        return result

if __name__ == "__main__":
    schema = llm_dataclass.Schema(llm_dataclass.BoolWrapper, root="sky_is_blue")

    question = dedent("""
    Is the sky blue?
    """).strip()

    model = "llama3:8b"

    answer = ask_ollama(question, model, schema)
    print()
    print("Final Result:")
    print(f"Question: {question}")
    print(f"Answer: {answer.value}")

# Example output when running this script:
"""
Sending prompt to Ollama:
Is the sky blue?
Please resond with an XML object containing the answer.
Example Response:
<sky_is_blue>
  <value>...</value>
</sky_is_blue>
Received response from Ollama:
What a fun question!

Here is the response you requested:

```
<sky_is_blue>
  <value>true</value>
</sky_is_blue>
```

In other words, yes, the sky is generally blue when observed during the daytime under normal atmospheric conditions. Of course, the color of the sky can change depending on factors like time of day, weather conditions, and atmospheric particles in the air... but from a simple "is it blue?" perspective, the answer is yes!

Final Result:
Question: Is the sky blue?
Answer: True
"""
