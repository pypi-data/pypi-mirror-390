# Formatting

Convert chunks to XML, JSON, or TOON format.

!!! warning "Research Purpose"
    This library is currently intended for **research purposes**.

## Quick Examples

### XML (Default)

```python
from chonkie_chunk_utils import xmlify

chunk = Chunk(start_index=0, end_index=10, text="Hello", context="doc1")
result = xmlify(chunk)
# Output: '<chunk start_index="0" end_index="10" context="doc1">Hello</chunk>'
```

### JSON

```python
from chonkie_chunk_utils import jsonify

result = jsonify(chunk)
# Output: '{"start_index": 0, "end_index": 10, "context": "doc1", "content": "Hello"}'

# With XML wrapper
result = jsonify(chunk, wrap_xml=True)
# Output: '<chunk>{"start_index": 0, ...}</chunk>'
```

### TOON

```python
from chonkie_chunk_utils import toonify

result = toonify(chunk)  # Compact format
result = toonify(chunk, wrap_xml=True)  # With XML wrapper
```

## Use with render_chunks

Formatters work seamlessly with `render_chunks`:

```python
from chonkie_chunk_utils import render_chunks, jsonify, xmlify

chunks = [Chunk(...), Chunk(...)]

# XML (default)
result = render_chunks(chunks)

# JSON
result = render_chunks(chunks, format_fn=jsonify)

# Plain text
result = render_chunks(chunks, format_fn=None)
```

## Select Attributes

All formatters support selecting which attributes to include:

```python
# Include only start_index and end_index
result = xmlify(chunk, attributes=["start_index", "end_index"])
```

## API Reference

### `xmlify`

```python
xmlify(chunk: Chunk, attributes: Iterable[str] = ["start_index", "end_index", "context"]) -> str
```

Convert chunk to XML format with specified attributes.

**See also:** [Full API documentation](../api/main.md#xmlify)

### `jsonify`

```python
jsonify(chunk: Chunk, attributes: Iterable[str] = ["start_index", "end_index", "context"], wrap_xml: bool = False) -> str
```

Convert chunk to JSON format with optional XML wrapper.

**See also:** [Full API documentation](../api/main.md#jsonify)

### `toonify`

```python
toonify(chunk: Chunk, attributes: Iterable[str] = ["start_index", "end_index", "context"], wrap_xml: bool = False) -> str
```

Convert chunk to TOON (Token Oriented Object Notation) format.

**See also:** [Full API documentation](../api/main.md#toonify)

### `FormatFn`

Protocol for formatter functions. All formatters conform to this protocol.

**See also:** [Full API documentation](../api/main.md#formatfn)
