"""
JSON formatter for converting Chunk objects to JSON format.

This module provides functions for formatting chunks into JSON strings,
including attribute extraction and JSON serialization.
"""

import json

from chonkie import Chunk
from dataclasses import asdict
from typing import Iterable


def jsonify(
    chunk: Chunk,
    attributes: Iterable[str] = ["start_index", "end_index", "context"],
    wrap_xml: bool = False,
) -> str:
    """
    Convert a Chunk object to JSON format with specified attributes.

    This function formats a Chunk into a JSON string, extracting specified
    attributes from the chunk and including them in the JSON object. Only
    attributes that exist in the chunk are included in the output. The "content"
    attribute is always included in addition to the specified attributes.

    Parameters
    ----------
    chunk : Chunk
        The Chunk object to convert to JSON format.
    attributes : Iterable[str], default=["start_index", "end_index", "context"]
        Iterable of attribute names to include in the JSON object.
        Only attributes that exist in the chunk will be included.
        Default attributes are start_index, end_index, and context.
        Note: The "content" attribute is always included regardless of
        this parameter.
    wrap_xml : bool, default=False
        If True, wraps the JSON string in a `<chunk>...</chunk>` XML tag.
        Unlike xmlify, this does not include XML attributes in the tag.
        If False, returns the JSON string as-is.

    Returns
    -------
    str
        JSON-formatted string representing the chunk.
        If wrap_xml=False: `{"attr1": "value1", "attr2": "value2", "content": "text"}`
        If wrap_xml=True: `<chunk>{"attr1": "value1", "attr2": "value2", "content": "text"}</chunk>`

    Examples
    --------
    >>> from chonkie_chunk_utils.formatters import jsonify
    >>> from chonkie import Chunk
    >>> chunk = Chunk(
    ...     text="Hello world",
    ...     start_index=0,
    ...     end_index=10,
    ...     context="example"
    ... )
    >>> jsonify(chunk)
    '{"start_index": 0, "end_index": 10, "context": "example", "content": "Hello world"}'
    >>> jsonify(chunk, attributes=["start_index", "end_index"])
    '{"start_index": 0, "end_index": 10, "content": "Hello world"}'
    >>> jsonify(chunk, wrap_xml=True)
    '<chunk>{"start_index": 0, "end_index": 10, "context": "example", "content": "Hello world"}</chunk>'
    >>> chunk_no_context = Chunk(text="Test", start_index=0, end_index=4)
    >>> jsonify(chunk_no_context, attributes=["start_index", "end_index", "context"])
    '{"start_index": 0, "end_index": 4, "content": "Test"}'
    """
    _dict = asdict(chunk)
    attributes = set(attributes) & set(_dict.keys())
    data = {attr: getattr(chunk, attr) for attr in attributes}
    # Always include text as "content"
    data["content"] = chunk.text
    json_str = json.dumps(data)
    
    if wrap_xml:
        return f"<chunk>{json_str}</chunk>"
    return json_str
