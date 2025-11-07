# API Reference

!!! warning "Research Purpose"
    This library is currently intended for **research purposes**.

This page provides a comprehensive API reference organized by functionality. All functions are available directly from the `chonkie_chunk_utils` package.

## Sorting

Sort chunks by their position in the document.

### `sort_chunks`

Sort chunks by `start_index` to ensure proper document order.

::: chonkie_chunk_utils.sort_chunks
    options:
      show_source: true
      show_root_heading: false
      show_root_toc_entry: false
      show_root_full_path: false
      heading_level: 4
      show_signature_annotations: true
      show_submodules: false

### `is_sorted_chunks`

Check if chunks are already sorted by `start_index`.

::: chonkie_chunk_utils.is_sorted_chunks
    options:
      show_source: true
      show_root_heading: false
      show_root_toc_entry: false
      show_root_full_path: false
      heading_level: 4
      show_signature_annotations: true
      show_submodules: false

**Example:**
```python
from chonkie_chunk_utils import sort_chunks, is_sorted_chunks

chunks = [Chunk(start_index=20), Chunk(start_index=0), Chunk(start_index=10)]

if not is_sorted_chunks(chunks):
    sorted_chunks = sort_chunks(chunks)
```

---

## Merging

Merge adjacent or overlapping chunks to remove duplicates and create continuous text.

### `merge_adjacent_chunks`

Merge multiple adjacent chunks in an iterable.

::: chonkie_chunk_utils.merge_adjacent_chunks
    options:
      show_source: true
      show_root_heading: false
      show_root_toc_entry: false
      show_root_full_path: false
      heading_level: 4
      show_signature_annotations: true
      show_submodules: false

### `merge_chunks`

Merge two adjacent chunks directly.

::: chonkie_chunk_utils.merge_chunks
    options:
      show_source: true
      show_root_heading: false
      show_root_toc_entry: false
      show_root_full_path: false
      heading_level: 4
      show_signature_annotations: true
      show_submodules: false

### `is_adjacent_chunks`

Check if two chunks are adjacent (overlapping, meeting at boundary, or immediately adjacent).

::: chonkie_chunk_utils.is_adjacent_chunks
    options:
      show_source: true
      show_root_heading: false
      show_root_toc_entry: false
      show_root_full_path: false
      heading_level: 4
      show_signature_annotations: true
      show_submodules: false

**Example:**
```python
from chonkie_chunk_utils import merge_adjacent_chunks, is_adjacent_chunks, merge_chunks

chunks = [
    Chunk(start_index=0, end_index=5, text="Hello"),
    Chunk(start_index=4, end_index=10, text="o world"),
]

# Check adjacency
if is_adjacent_chunks(chunks[0], chunks[1]):
    # Merge all adjacent chunks
    merged = merge_adjacent_chunks(chunks)
    # Or merge two chunks directly
    merged_chunk = merge_chunks(chunks[0], chunks[1])
```

---

## Formatting

Convert chunks to various serialization formats (XML, JSON, TOON).

### `xmlify`

Convert chunks to XML format with attributes.

::: chonkie_chunk_utils.xmlify
    options:
      show_source: true
      show_root_heading: false
      show_root_toc_entry: false
      show_root_full_path: false
      heading_level: 4
      show_signature_annotations: true
      show_submodules: false

### `jsonify`

Convert chunks to JSON format with optional XML wrapper.

::: chonkie_chunk_utils.jsonify
    options:
      show_source: true
      show_root_heading: false
      show_root_toc_entry: false
      show_root_full_path: false
      heading_level: 4
      show_signature_annotations: true
      show_submodules: false

### `toonify`

Convert chunks to TOON (Token Oriented Object Notation) format.

::: chonkie_chunk_utils.toonify
    options:
      show_source: true
      show_root_heading: false
      show_root_toc_entry: false
      show_root_full_path: false
      heading_level: 4
      show_signature_annotations: true
      show_submodules: false

### `FormatFn`

Protocol for formatter functions. All formatters conform to this protocol.

::: chonkie_chunk_utils.FormatFn
    options:
      show_source: true
      show_root_heading: false
      show_root_toc_entry: false
      show_root_full_path: false
      heading_level: 4
      show_signature_annotations: true
      show_submodules: false
      show_bases: false

**Example:**
```python
from chonkie_chunk_utils import xmlify, jsonify, toonify, FormatFn

chunk = Chunk(start_index=0, end_index=10, text="Hello", context="test")

# XML format (default)
xml_result = xmlify(chunk)

# JSON format
json_result = jsonify(chunk)

# JSON with XML wrapper
json_wrapped = jsonify(chunk, wrap_xml=True)

# TOON format
toon_result = toonify(chunk)

# All formatters conform to FormatFn protocol
formatters: list[FormatFn] = [xmlify, jsonify, toonify]
```

---

## Rendering

Render multiple chunks into a single LLM-friendly string with formatting and separators.

### `render_chunks`

Main function for rendering chunks. Handles filtering, merging, formatting, and separation.

::: chonkie_chunk_utils.render_chunks
    options:
      show_source: true
      show_root_heading: false
      show_root_toc_entry: false
      show_root_full_path: false
      heading_level: 4
      show_signature_annotations: true
      show_submodules: false

**Example:**
```python
from chonkie_chunk_utils import render_chunks, jsonify, xmlify

chunks = [
    Chunk(start_index=0, end_index=5, text="Hello", context="doc1"),
    Chunk(start_index=20, end_index=25, text="world", context="doc1"),
]

# Default XML format
result = render_chunks(chunks)

# JSON format
result = render_chunks(chunks, format_fn=jsonify)

# Plain text
result = render_chunks(chunks, format_fn=None)

# Custom separator
result = render_chunks(chunks, ellipsis_message="\n[Gap]\n")
```

---

## Quick Reference

### Import All Functions

```python
from chonkie_chunk_utils import (
    # Sorting
    sort_chunks,
    is_sorted_chunks,
    
    # Merging
    merge_adjacent_chunks,
    merge_chunks,
    is_adjacent_chunks,
    
    # Formatting
    FormatFn,
    xmlify,
    jsonify,
    toonify,
    
    # Rendering
    render_chunks,
)
```

### Typical Workflow

```python
from chonkie_chunk_utils import sort_chunks, render_chunks, jsonify

# 1. Sort chunks
sorted_chunks = sort_chunks(chunks)

# 2. Render (automatically merges and formats)
result = render_chunks(sorted_chunks, format_fn=jsonify)
```
