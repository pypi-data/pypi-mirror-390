# Merging

Merge adjacent or overlapping chunks to remove duplicates.

!!! warning "Research Purpose"
    This library is currently intended for **research purposes**.

## Quick Example

```python
from chonkie_chunk_utils import merge_adjacent_chunks

chunks = [
    Chunk(start_index=0, end_index=5, text="Hello"),
    Chunk(start_index=4, end_index=10, text="o world"),  # Overlapping
]

merged = merge_adjacent_chunks(chunks)
# Result: [Chunk(text="Hello world", start_index=0, end_index=10)]
# Duplicate "o" automatically removed
```

## When to Use

Use merging when chunks overlap or are adjacent. `render_chunks` automatically merges chunks, so you usually don't need to call this separately.

```python
# render_chunks handles merging automatically
result = render_chunks(chunks)  # Merges adjacent chunks internally
```

## Merge Two Chunks Directly

```python
from chonkie_chunk_utils import merge_chunks

chunk1 = Chunk(start_index=0, end_index=5, text="Hello")
chunk2 = Chunk(start_index=5, end_index=10, text=" world")

merged = merge_chunks(chunk1, chunk2)
# Result: Chunk(text="Hello world", start_index=0, end_index=10)
```

## Check if Adjacent

```python
from chonkie_chunk_utils import is_adjacent_chunks

if is_adjacent_chunks(chunk1, chunk2):
    merged = merge_chunks(chunk1, chunk2)
```

## API Reference

### `merge_adjacent_chunks`

```python
merge_adjacent_chunks(chunks: Iterable[Chunk]) -> List[Chunk]
```

Merge multiple adjacent chunks in an iterable, removing duplicates.

**See also:** [Full API documentation](../api/main.md#merge_adjacent_chunks)

### `merge_chunks`

```python
merge_chunks(chunk_1: Chunk, chunk_2: Chunk) -> Chunk
```

Merge two adjacent chunks directly, removing text overlap.

**See also:** [Full API documentation](../api/main.md#merge_chunks)

### `is_adjacent_chunks`

```python
is_adjacent_chunks(chunk_1: Chunk, chunk_2: Chunk) -> bool
```

Check if two chunks are adjacent (overlapping, meeting at boundary, or immediately adjacent).

**See also:** [Full API documentation](../api/main.md#is_adjacent_chunks)
