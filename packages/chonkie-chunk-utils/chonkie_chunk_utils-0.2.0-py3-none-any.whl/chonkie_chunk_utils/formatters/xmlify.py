"""
XML formatter for converting Chunk objects to XML format.

This module provides functions and configurations for formatting chunks into XML,
including attribute extraction and XML tag generation.
"""

from chonkie import Chunk
from dataclasses import asdict
from typing import Iterable


def xmlify(
    chunk: Chunk,
    attributes: Iterable[str] = ["start_index", "end_index", "context"],
) -> str:
    """
    Convert a Chunk object to XML format with specified attributes.

    This function formats a Chunk into an XML string, extracting specified
    attributes from the chunk and including them as XML attributes. Only
    attributes that exist in the chunk are included in the output.

    Parameters
    ----------
    chunk : Chunk
        The Chunk object to convert to XML format.
    attributes : Iterable[str], default=["start_index", "end_index", "context"]
        Iterable of attribute names to include as XML attributes.
        Only attributes that exist in the chunk will be included.
        Default attributes are start_index, end_index, and context.

    Returns
    -------
    str
        XML-formatted string representing the chunk.
        Format: `<chunk attr1="value1" attr2="value2">content</chunk>`

    Examples
    --------
    >>> from chonkie_chunk_utils.formatters import xmlify
    >>> from chonkie import Chunk
    >>> chunk = Chunk(
    ...     text="Hello world",
    ...     start_index=0,
    ...     end_index=10,
    ...     context="example"
    ... )
    >>> xmlify(chunk)
    '<chunk start_index="0" end_index="10" context="example">Hello world</chunk>'
    >>> xmlify(chunk, attributes=["start_index", "end_index"])
    '<chunk start_index="0" end_index="10">Hello world</chunk>'
    >>> chunk_no_context = Chunk(text="Test", start_index=0, end_index=4)
    >>> xmlify(chunk_no_context, attributes=["start_index", "end_index", "context"])
    '<chunk start_index="0" end_index="4">Test</chunk>'
    """
    content = chunk.text if isinstance(chunk, Chunk) else chunk
    # 원하는 속성 중 존재하는 속성만 추출하기
    _dict = asdict(chunk)
    attributes = tuple(set(attributes) & set(_dict.keys()))
    attributes_str = " ".join(f'{attr}="{getattr(chunk, attr)}"' for attr in attributes)

    return f"<chunk {attributes_str}>{content}</chunk>"
