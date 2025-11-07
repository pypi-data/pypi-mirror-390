"""
chonkie-chunk-utils: Utility functions for managing and processing chonkie Chunk objects.

This package provides strategies for sorting, merging, formatting, and rendering
document chunks to create optimal context formats that are easy for LLMs to understand.

Main Functions
--------------
sort_chunks : Sort chunks by start_index.
merge_adjacent_chunks : Merge adjacent or overlapping chunks.
render_chunks : Render chunks into LLM-friendly strings with formatting.

Formatter Functions
-------------------
FormatFn : Protocol for formatter functions.
xmlify : Convert chunks to XML format.
jsonify : Convert chunks to JSON format.
toonify : Convert chunks to TOON format.

Utility Functions
-----------------
is_sorted_chunks : Check if chunks are sorted by start_index.
is_adjacent_chunks : Check if two chunks are adjacent.
merge_chunks : Merge two adjacent chunks.

Examples
--------
**Basic usage:**
>>> from chonkie import Chunk
>>> from chonkie_chunk_utils import sort_chunks, merge_adjacent_chunks, render_chunks
>>> chunks = [
...     Chunk(start_index=20, end_index=25, text="world"),
...     Chunk(start_index=0, end_index=5, text="Hello"),
...     Chunk(start_index=4, end_index=10, text="o world"),
... ]
>>> sorted_chunks = sort_chunks(chunks)
>>> merged_chunks = merge_adjacent_chunks(sorted_chunks)
>>> result = render_chunks(merged_chunks)
>>> print(result)
'<chunk start_index="0" end_index="10">Hello world</chunk>'

**Using formatters:**
>>> from chonkie_chunk_utils import render_chunks, jsonify
>>> chunks = [Chunk(start_index=0, end_index=5, text="Hello", context="test")]
>>> result = render_chunks(chunks, format_fn=jsonify)
>>> print(result)
'{"start_index": 0, "end_index": 5, "context": "test", "content": "Hello"}'
"""

from .sort_chunks import sort_chunks
from .merge_adjacent_chunks import merge_adjacent_chunks
from .render_chunks import render_chunks

# Import formatters
from .formatters.format_fn import FormatFn
from .formatters.xmlify import xmlify
from .formatters.jsonify import jsonify
from .formatters.toonify import toonify

# Import utils
from .utils.is_sorted_chunks import is_sorted_chunks
from .utils.is_adjacent_chunks import is_adjacent_chunks
from .utils.merge_chunks import merge_chunks

__all__ = [
    # Main functions
    "sort_chunks",
    "merge_adjacent_chunks",
    "render_chunks",
    # Formatters
    "FormatFn",
    "xmlify",
    "jsonify",
    "toonify",
    # Utils
    "is_sorted_chunks",
    "is_adjacent_chunks",
    "merge_chunks",
]
