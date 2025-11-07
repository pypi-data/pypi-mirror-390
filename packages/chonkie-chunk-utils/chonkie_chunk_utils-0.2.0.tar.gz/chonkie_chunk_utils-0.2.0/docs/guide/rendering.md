# Rendering

Render chunks into a single LLM-friendly string. This is the main function you'll use.

!!! warning "Research Purpose"
    This library is currently intended for **research purposes**.

## Quick Example

```python
from chonkie_chunk_utils import render_chunks

chunks = [
    Chunk(start_index=0, end_index=5, text="Hello"),
    Chunk(start_index=4, end_index=10, text="o world"),  # Overlapping
]

result = render_chunks(chunks)
# Output: '<chunk start_index="0" end_index="10">Hello world</chunk>'
# Automatically merges adjacent chunks
```

## With Non-adjacent Chunks

```python
chunks = [
    Chunk(start_index=0, end_index=5, text="First"),
    Chunk(start_index=20, end_index=25, text="Second"),  # Gap
]

result = render_chunks(chunks, ellipsis_message="[...]")
# Output:
# '<chunk start_index="0" end_index="5">First</chunk>
# [...]
# <chunk start_index="20" end_index="25">Second</chunk>'
```

## Complete Workflow

```python
from chonkie_chunk_utils import sort_chunks, render_chunks, jsonify

# 1. Sort first (render_chunks does not sort)
sorted_chunks = sort_chunks(chunks)

# 2. Render (automatically merges and formats)
result = render_chunks(
    sorted_chunks,
    format_fn=jsonify,
    ellipsis_message="[...]"
)
```

## Custom Formatting

```python
# JSON format
result = render_chunks(chunks, format_fn=jsonify)

# Plain text
result = render_chunks(chunks, format_fn=None)

# Custom separator
result = render_chunks(chunks, ellipsis_message="\n[Gap]\n")
```

!!! note "render_chunks does not sort"
    Always sort chunks first if they're out of order. `render_chunks` handles merging and formatting, but not sorting.

## API Reference

### `render_chunks`

```python
render_chunks(
    chunks: Iterable[Chunk],
    format_fn: Optional[FormatFn] = xmlify,
    ellipsis_message: str = "[...]",
    manual_ellipsis_message: bool = False,
) -> str
```

Render chunks into a single LLM-friendly string. Automatically merges adjacent chunks and applies formatting.

**Parameters:**
- `chunks`: Iterable of chunks to render
- `format_fn`: Formatter function (default: `xmlify`, use `None` for plain text)
- `ellipsis_message`: Separator between non-adjacent chunk groups (default: `"[...]"`)
- `manual_ellipsis_message`: Disable automatic separator formatting (default: `False`)

**See also:** [Full API documentation](../api/main.md#render_chunks)
