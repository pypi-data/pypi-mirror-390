"""
Formatters for converting Chunk objects to various formats.

This module provides formatter functions for converting Chunk objects into
different serialization formats, including XML, JSON, and TOON (Token Oriented
Object Notation). Each formatter can extract specified attributes from chunks
and format them according to the target format's specifications.

Modules
-------
xmlify : XML formatter function.
jsonify : JSON formatter function.
toonify : TOON (Token Oriented Object Notation) formatter function.

Examples
--------
**XML formatting:**
>>> from chonkie_chunk_utils.formatters import xmlify
>>> from chonkie import Chunk
>>> chunk = Chunk(text="Hello", start_index=0, end_index=4, context="test")
>>> xmlify(chunk)
'<chunk start_index="0" end_index="4" context="test">Hello</chunk>'
>>> xmlify(chunk, attributes=["start_index", "end_index"])
'<chunk start_index="0" end_index="4">Hello</chunk>'

**JSON formatting:**
>>> from chonkie_chunk_utils.formatters import jsonify
>>> chunk = Chunk(text="Hello", start_index=0, end_index=4, context="test")
>>> jsonify(chunk)
'{"start_index": 0, "end_index": 4, "context": "test", "content": "Hello"}'
>>> jsonify(chunk, wrap_xml=True)
'<chunk>{"start_index": 0, "end_index": 4, "context": "test", "content": "Hello"}</chunk>'

**TOON formatting:**
>>> from chonkie_chunk_utils.formatters import toonify
>>> chunk = Chunk(text="Hello", start_index=0, end_index=4, context="test")
>>> toonify(chunk)
'<TOON-encoded string>'
>>> toonify(chunk, wrap_xml=True)
'<chunk><TOON-encoded string></chunk>'
"""

from .format_fn import FormatFn
from .jsonify import jsonify
from .toonify import toonify
from .xmlify import xmlify

__all__ = ["FormatFn", "jsonify", "toonify", "xmlify"]
