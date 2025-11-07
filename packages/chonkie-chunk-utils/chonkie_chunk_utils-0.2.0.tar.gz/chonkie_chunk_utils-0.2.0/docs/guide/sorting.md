# Sorting

Sort chunks by their position in the document.

!!! warning "Research Purpose"
    This library is currently intended for **research purposes**.

## Quick Example

```python
from chonkie_chunk_utils import sort_chunks

chunks = [
    Chunk(start_index=20, end_index=25, text="Second"),
    Chunk(start_index=0, end_index=5, text="First"),
    Chunk(start_index=10, end_index=15, text="Third"),
]

sorted_chunks = sort_chunks(chunks)
# Result: [First, Third, Second] in document order
```

## When to Use

Use `sort_chunks` when chunks from vector search are out of order. Always sort before merging or rendering.

```python
from chonkie_chunk_utils import sort_chunks, render_chunks

# Sort first, then render
sorted_chunks = sort_chunks(chunks)
result = render_chunks(sorted_chunks)
```

!!! note "render_chunks does not sort"
    `render_chunks` does not automatically sort chunks. Sort them first if needed.

## Check if Already Sorted

```python
from chonkie_chunk_utils import is_sorted_chunks

if not is_sorted_chunks(chunks):
    chunks = sort_chunks(chunks)
```

## API Reference

### `sort_chunks`

```python
sort_chunks(chunks: Iterable[Chunk]) -> list[Chunk]
```

Sort chunks by `start_index` in ascending order.

**See also:** [Full API documentation](../api/main.md#sort_chunks)

### `is_sorted_chunks`

```python
is_sorted_chunks(chunks: list[Chunk]) -> bool
```

Check if chunks are already sorted by `start_index`.

**See also:** [Full API documentation](../api/main.md#is_sorted_chunks)
