from dataclasses import dataclass, field
from textwrap import dedent
from typing import TYPE_CHECKING, List, TypeVar

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
    @dataclass
    class CreativeWork:
        title: str = field(metadata={"xml": {"name": "schema:name"}})
        author: str = field(metadata={"xml": {"name": "schema:author"}})
        inLanguage: str = field(metadata={"xml": {"name": "schema:inLanguage"}})
        genre: List[str] = field(metadata={"xml": {"name": "schema:genre"}})
        abstract: str = field(metadata={"xml": {"name": "schema:abstract"}})
        keywords: str = field(metadata={"xml": {"name": "schema:keywords"}})

    @dataclass
    class CreativeWorkClassification:
        creativeWork: CreativeWork = field(metadata={"xml": {"name": "schema:CreativeWork"}})

    schema = llm_dataclass.Schema(CreativeWorkClassification, root="rdf:RDF")

    question = dedent("""
    Can you classify the following creative work?

    Achilles sing, O Goddess! Peleus' son;
    His wrath pernicious, who ten thousand woes
    Caused to Achaia's host, sent many a soul
    Illustrious into Ades premature,
    And Heroes gave (so stood the will of Jove)
    To dogs and to all ravening fowls a prey,
    When fierce dispute had separated once
    The noble Chief Achilles from the son
    Of Atreus, Agamemnon, King of men.


    """).strip()

    model = "llama3:8b"

    answer = ask_ollama(question, model, schema)
    print()
    print("Final Result:")
    print(f"Question: {question}")
    print(f"Answer: {answer}")

# Example output when running this script:
"""
Achilles sing, O Goddess! Peleus' son;
His wrath pernicious, who ten thousand woes
Caused to Achaia's host, sent many a soul
Illustrious into Ades premature,
And Heroes gave (so stood the will of Jove)
To dogs and to all ravening fowls a prey,
When fierce dispute had separated once
The noble Chief Achilles from the son
Of Atreus, Agamemnon, King of men.
Please resond with an XML object containing the answer.
Example Response:
<rdf:RDF>
  <schema:CreativeWork>
    <schema:name>...</schema:name>
    <schema:author>...</schema:author>
    <schema:inLanguage>...</schema:inLanguage>
    <schema:genre>...</schema:genre>
    <schema:genre>...</schema:genre>
    <schema:abstract>...</schema:abstract>
    <schema:keywords>...</schema:keywords>
  </schema:CreativeWork>
</rdf:RDF>
Received response from Ollama:
A classic!

Here's the XML response:

<rdf:RDF>
  <schema:CreativeWork>
    <schema:name>The Iliad (Book I, lines 1-11)</schema:name>
    <schema:author>Homer</schema:author>
    <schema:inLanguage>Classical Greek</schema:inLanguage>
    <schema:genre>Literary Work</schema:genre>
    <schema:genre>Epic Poetry</schema:genre>
    <schema:abstract>The Iliad is an ancient Greek epic poem that tells the story of the Trojan War. This excerpt is from Book I, lines 1-11.</schema:abstract>
    <schema:keywords>epic poetry, Homer, The Iliad, Classical Greek</schema:keywords>
  </schema:CreativeWork>
</rdf:RDF>

Note: The schema namespace prefix "schema" refers to the Schema for markup and vocabulary elements defined by the Dublin Core Metadata Initiative.

Final Result:
Question: Can you classify the following creative work?

Achilles sing, O Goddess! Peleus' son;
His wrath pernicious, who ten thousand woes
Caused to Achaia's host, sent many a soul
Illustrious into Ades premature,
And Heroes gave (so stood the will of Jove)
To dogs and to all ravening fowls a prey,
When fierce dispute had separated once
The noble Chief Achilles from the son
Of Atreus, Agamemnon, King of men.
Answer: CreativeWorkClassification(creativeWork=CreativeWork(title='The Iliad (Book I, lines 1-11)', author='Homer', inLanguage='Classical Greek', genre=['Literary Work', 'Epic Poetry'], abstract='The Iliad is an ancient Greek epic poem that tells the story of the Trojan War. This excerpt is from Book I, lines 1-11.', keywords='epic poetry, Homer, The Iliad, Classical Greek'))
"""
