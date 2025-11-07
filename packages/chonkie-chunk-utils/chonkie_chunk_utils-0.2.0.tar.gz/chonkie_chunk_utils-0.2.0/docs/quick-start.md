# Quick Start

This guide will help you get started with `chonkie-chunk-utils` in minutes.

!!! warning "Research Purpose"
    This library is currently intended for **research purposes**. While it is functional and tested, it may undergo significant changes as research progresses.

## Basic Workflow

The typical workflow for processing chunks in a RAG system involves four main steps:

1. **Sort** chunks by their position in the document
2. **Merge** adjacent or overlapping chunks
3. **Rerank** chunks using your custom strategy (research focus)
4. **Render** chunks into LLM-friendly format

## Example: Processing Retrieved Chunks

```python
from chonkie import Chunk
from chonkie_chunk_utils import sort_chunks, merge_adjacent_chunks, render_chunks

# Simulate chunks retrieved from vector search (out of order)
chunks = [
    Chunk(start_index=20, end_index=25, text="world"),
    Chunk(start_index=0, end_index=5, text="Hello"),
    Chunk(start_index=4, end_index=10, text="o world"),  # Overlapping
]

# Step 1: Sort by start_index
sorted_chunks = sort_chunks(chunks)
# sorted_chunks: [Hello (0-5), o world (4-10), world (20-25)]

# Step 2: Merge adjacent chunks
merged_chunks = merge_adjacent_chunks(sorted_chunks)
# merged_chunks: [Hello world (0-10), world (20-25)]
# Overlapping chunks merged, duplicate "o" removed

# Step 3: Render for LLM
result = render_chunks(merged_chunks)
print(result)
# Output:
# <chunk context="None" start_index="0" end_index="10">Hello world</chunk>
# [...]
# <chunk context="None" start_index="20" end_index="25">world</chunk>
```

## One-Step Rendering

You can also use `render_chunks` directly, which handles merging internally (but not sorting):

```python
from chonkie import Chunk
from chonkie_chunk_utils import render_chunks, sort_chunks

chunks = [
    Chunk(start_index=20, end_index=25, text="world"),
    Chunk(start_index=0, end_index=5, text="Hello"),
    Chunk(start_index=4, end_index=10, text="o world"),
]

# Note: render_chunks does NOT sort, so sort first if needed
sorted_chunks = sort_chunks(chunks)

result = render_chunks(sorted_chunks)
# Automatically merges adjacent chunks and formats them
print(result)
# Output:
# <chunk context="None" start_index="0" end_index="10">Hello world</chunk>
# [...]
# <chunk context="None" start_index="20" end_index="25">world</chunk>
```

## Using Different Formatters

```python
from chonkie import Chunk
from chonkie_chunk_utils import render_chunks, jsonify, xmlify

chunks = [
    Chunk(start_index=0, end_index=5, text="Hello", context="doc1"),
    Chunk(start_index=20, end_index=25, text="world", context="doc1"),
]

# XML format (default)
xml_result = render_chunks(chunks, format_fn=xmlify)
print(xml_result)
# Output:
# <chunk context="doc1" end_index="5" start_index="0">Hello</chunk>
# [...]
# <chunk context="doc1" end_index="25" start_index="20">world</chunk>

# JSON format
json_result = render_chunks(chunks, format_fn=jsonify)
print(json_result)
# Output:
# {"context": "doc1", "end_index": 5, "start_index": 0, "content": "Hello"}
# [...]
# {"context": "doc1", "end_index": 25, "start_index": 20, "content": "world"}

# Plain text (no formatting)
text_result = render_chunks(chunks, format_fn=None)
print(text_result)
# Output:
# Hello
# [...]
# world
```

## Custom Separators

You can customize the separator between non-adjacent chunks:

```python
from chonkie import Chunk
from chonkie_chunk_utils import render_chunks

chunks = [
    Chunk(start_index=0, end_index=5, text="Hello", context="doc1"),
    Chunk(start_index=20, end_index=25, text="world", context="doc1"),
]

# Use newline as separator (manual mode)
result = render_chunks(chunks, ellipsis_message="\n", manual_ellipsis_message=True)
print(result)
# Output:
# <chunk context="doc1" start_index="0" end_index="5">Hello</chunk>
# <chunk context="doc1" start_index="20" end_index="25">world</chunk>
# Note: Chunks are separated by a single newline without ellipsis message

# Default separator (auto-formatted)
result_default = render_chunks(chunks, ellipsis_message="[...]")
print(result_default)
# Output:
# <chunk start_index="0" end_index="5" context="doc1">Hello</chunk>
# [...]
# <chunk start_index="20" end_index="25" context="doc1">world</chunk>
# Note: Default separator is automatically wrapped with newlines
```

## Next Steps

- Learn about [Sorting](guide/sorting.md)
- Learn about [Merging](guide/merging.md)
- Learn about [Formatting](guide/formatting.md)
- Learn about [Rendering](guide/rendering.md)
- Browse the [API Reference](api/main.md) for detailed function documentation
