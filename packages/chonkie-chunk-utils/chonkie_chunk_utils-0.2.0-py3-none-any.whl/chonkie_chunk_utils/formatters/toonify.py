"""
TOON (Token Oriented Object Notation) formatter for converting Chunk objects to TOON format.

This module provides functions for formatting chunks into TOON strings,
including attribute extraction and TOON serialization.
"""

from toon_python import encode

from chonkie import Chunk
from dataclasses import asdict
from typing import Iterable


def toonify(
    chunk: Chunk,
    attributes: Iterable[str] = ["start_index", "end_index", "context"],
    wrap_xml: bool = False,
) -> str:
    """
    Convert a Chunk object to TOON (Token Oriented Object Notation) format with specified attributes.

    This function formats a Chunk into a TOON string, extracting specified
    attributes from the chunk and including them in the TOON object. Only
    attributes that exist in the chunk are included in the output. The "content"
    attribute is always included in addition to the specified attributes.

    Parameters
    ----------
    chunk : Chunk
        The Chunk object to convert to TOON format.
    attributes : Iterable[str], default=["start_index", "end_index", "context"]
        Iterable of attribute names to include in the TOON object.
        Only attributes that exist in the chunk will be included.
        Default attributes are start_index, end_index, and context.
        Note: The "content" attribute is always included regardless of
        this parameter.
    wrap_xml : bool, default=False
        If True, wraps the TOON string in a `<chunk>...</chunk>` XML tag.
        Unlike xmlify, this does not include XML attributes in the tag.
        If False, returns the TOON string as-is.

    Returns
    -------
    str
        TOON-formatted string representing the chunk.
        If wrap_xml=False: TOON-encoded string containing the chunk attributes and content.
        If wrap_xml=True: `<chunk><TOON-encoded string></chunk>`

    Examples
    --------
    >>> from chonkie_chunk_utils.formatters import toonify
    >>> from chonkie import Chunk
    >>> chunk = Chunk(
    ...     text="Hello world",
    ...     start_index=0,
    ...     end_index=10,
    ...     context="example"
    ... )
    >>> toonify(chunk)
    '<TOON-encoded string>'
    >>> toonify(chunk, attributes=["start_index", "end_index"])
    '<TOON-encoded string>'
    >>> toonify(chunk, wrap_xml=True)
    '<chunk><TOON-encoded string></chunk>'
    >>> chunk_no_context = Chunk(text="Test", start_index=0, end_index=4)
    >>> toonify(chunk_no_context, attributes=["start_index", "end_index", "context"])
    '<TOON-encoded string>'
    """
    _dict = asdict(chunk)
    attributes = set(attributes) & set(_dict.keys())
    data = {attr: getattr(chunk, attr) for attr in attributes}
    # Always include text as "content"
    data["content"] = chunk.text
    toon_str = encode(data)

    if wrap_xml:
        return f"<chunk>{toon_str}</chunk>"
    return toon_str
