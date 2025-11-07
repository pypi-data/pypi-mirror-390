# chonkie-chunk-utils

**How about sort, merge, and formatting for your RAG?**

`chonkie-chunk-utils` is a chunk management utility library for RAG (Retrieval-Augmented Generation) systems. It provides functions for sorting, merging, formatting, and rendering document chunks to create optimal context formats that are easy for LLMs to understand.

!!! warning "Research Purpose"
    This library is currently intended for **research purposes**. While it is functional and tested, it may undergo significant changes as research progresses. Use with caution in production environments.

## Core Feature: Formatting & Rendering

**This is what we provide.** Transform raw chunks into LLM-friendly, structured formats that enhance understanding and reduce token waste.

### Why Formatting & Rendering Matter

Unstructured chunks lack the organization and formatting that LLMs need to effectively understand relationships, boundaries, and metadata. Our formatting and rendering functions transform unstructured chunks into structured formats (XML, JSON, TOON) that LLMs can easily parse and reason about.

### How to Use

Use `render_chunks` to convert your chunks into a single, formatted string with:

- **Structured formats**: XML, JSON, or TOON for metadata-rich context
- **Smart merging**: Adjacent chunks automatically merged (no duplicates)
- **Custom separators**: Control how non-adjacent chunks are separated
- **Empty chunk filtering**: Automatically removes empty chunks

```python
from chonkie_chunk_utils import render_chunks, xmlify, jsonify, toonify

# Default: XML format (structured, LLM-friendly)
result = render_chunks(chunks)
# Output:
# <chunk start_index="0" end_index="5" context="doc1">Hello</chunk>
# [...]
# <chunk start_index="20" end_index="25" context="doc1">world</chunk>

# JSON format
result = render_chunks(chunks, format_fn=jsonify)
# Output:
# {"start_index": 0, "context": "doc1", "end_index": 5, "content": "Hello"}
# [...]
# {"start_index": 20, "context": "doc1", "end_index": 25, "content": "world"}

# JSON format with XML wrapper (wrap_xml=True)
result = render_chunks(chunks, format_fn=lambda c: jsonify(c, wrap_xml=True))
# Output:
# <chunk>{"start_index": 0, "context": "doc1", "end_index": 5, "content": "Hello"}</chunk>
# [...]
# <chunk>{"start_index": 20, "context": "doc1", "end_index": 25, "content": "world"}</chunk>

# TOON format with XML wrapper (wrap_xml=True)
result = render_chunks(chunks, format_fn=lambda c: toonify(c, wrap_xml=True))
# Output:
# <chunk>end_index: 5
# context: doc1
# start_index: 0
# content: Hello</chunk>
# [...]
# <chunk>end_index: 25
# context: doc1
# start_index: 20
# content: world</chunk>

# Custom separator (manual mode)
result = render_chunks(chunks, ellipsis_message="\n---\n", manual_ellipsis_message=True)
# Output:
# <chunk end_index="5" context="doc1" start_index="0">Hello</chunk>
# ---
# <chunk end_index="25" context="doc1" start_index="20">world</chunk>

# Newline separator (manual mode)
result = render_chunks(chunks, ellipsis_message="\n", manual_ellipsis_message=True)
# Output:
# <chunk end_index="5" context="doc1" start_index="0">Hello</chunk>
# <chunk end_index="25" context="doc1" start_index="20">world</chunk>

# Plain text with custom separator
result = render_chunks(chunks, format_fn=None, ellipsis_message="\n---\n", manual_ellipsis_message=True)
# Output:
# Hello
# ---
# world
```

## Use Case: Reranking Pipeline

**This is how you can use it.** While reranking itself is not provided by this library, we provide the essential preprocessing and formatting functions that make reranking pipelines work seamlessly.

### Why This Approach Works Better

!!! note "Research Hypothesis"
    **The core hypothesis:** When reranking is performed on sorted, merged chunks (organized chunk sets with overlapping adjacent chunks resolved), embedding models and reranking models can capture semantic meaning more effectively compared to using raw, unprocessed chunks.
    
    **Note:** This is currently a research hypothesis that we are investigating. The benefits described below are theoretical and require empirical validation.

**Theoretical benefits:**
- **Better semantic coherence**: Merged chunks represent continuous, coherent text segments rather than fragmented pieces
- **Improved context understanding**: Sorting ensures chunks follow document order, preserving logical flow
- **Enhanced embedding quality**: Clean, organized chunks allow models to better understand relationships and boundaries
- **More accurate reranking**: Reranking models receive well-structured input, leading to better relevance judgments

Vector search retrieves chunks by semantic similarity, but relevance doesn't always mean optimal context. By preprocessing chunks (sorting and merging) before reranking, we hypothesize that embedding and reranking models receive better-structured input that enables more accurate semantic understanding.

### How to Use in Reranking Pipeline

This library provides the foundation for reranking pipelines:

1. **Sort** chunks by document position (ensures proper order)
2. **Merge** adjacent/overlapping chunks (removes duplicates)
3. **Rerank** using your custom logic (you implement this)
4. **Render** for LLM (our formatting feature)

```python
from chonkie_chunk_utils import sort_chunks, merge_adjacent_chunks, render_chunks

# Step 1: Sort by document position
sorted_chunks = sort_chunks(retrieved_chunks)

# Step 2: Merge adjacent/overlapping chunks
merged_chunks = merge_adjacent_chunks(sorted_chunks)

# Step 3: Rerank (your custom logic)
reranked_chunks = your_reranking_function(merged_chunks)
# Examples:
# - reranked = [c for c in merged_chunks if c.score > 0.8]
# - reranked = sorted(merged_chunks, key=lambda x: x.custom_priority, reverse=True)[:10]
# - reranked = apply_domain_heuristics(merged_chunks)

# Step 4: Render for LLM (our formatting feature)
result = render_chunks(reranked_chunks)
# Ready to send to your LLM!
```

### Reranking Strategies You Can Implement

- Filter chunks by relevance scores from cross-encoders or custom models
- Reorder by domain-specific heuristics (e.g., prioritize certain document sections)
- Select top-k chunks based on token budget constraints
- Apply custom business logic

## Why This Combination Works

**Preprocessing (Sorting & Merging)** → **Reranking** → **Formatting & Rendering**: This pipeline creates optimal context by ensuring each step receives well-structured input.

**The complete picture:**
- **Preprocessing improves reranking** (hypothesis): Sorted, merged chunks may enable embedding and reranking models to better capture semantic meaning (as described above)
- **Reranking selects relevance**: Your custom logic filters and orders the most important chunks
- **Formatting enhances LLM understanding**: Structured formats help LLMs parse metadata and relationships
- **Together they create context that:**
  - **Maximizes relevance**: Only the most important chunks reach the LLM
  - **Minimizes noise**: Duplicates removed, empty chunks filtered
  - **Enhances understanding**: Structured formats help LLMs parse metadata and relationships
  - **Saves tokens**: Smart merging reduces redundant content
  - **Enables experimentation**: Easy to test different reranking strategies with consistent formatting

## Complete Workflow

```python
from chonkie import Chunk
from chonkie_chunk_utils import sort_chunks, merge_adjacent_chunks, render_chunks

# Step 1: Retrieve chunks from vector search
chunks = [Chunk(...), ...]  # Retrieved from your vector DB

# Step 2: Sort by document position
sorted_chunks = sort_chunks(chunks)

# Step 3: Merge adjacent/overlapping chunks
merged_chunks = merge_adjacent_chunks(sorted_chunks)

# Step 4: Rerank (your custom logic)
reranked_chunks = your_reranking_function(merged_chunks)

# Step 5: Render for LLM (default: XML format)
result = render_chunks(reranked_chunks)
# Ready to send to your LLM!
```

See the [Quick Start Guide](quick-start.md) for detailed examples with outputs.

## Features

- **Sorting**: Sort chunks by `start_index` to ensure proper document order
- **Merging**: Automatically merge adjacent or overlapping chunks to remove duplicates
- **Formatting**: Convert chunks to various formats (XML, JSON, TOON)
- **Rendering**: Render chunks into LLM-friendly single strings with customizable separators

## Installation

```bash
pip install chonkie-chunk-utils
```

Or using `rye`:

```bash
rye add chonkie-chunk-utils
```

## Documentation

- [Installation Guide](installation.md) - Detailed installation instructions
- [Quick Start Guide](quick-start.md) - Get started in minutes with examples
- [User Guide](guide/sorting.md) - Learn about sorting, merging, formatting, and rendering
- [API Reference](api/main.md) - Complete function documentation

## Requirements

- Python >= 3.8
- chonkie >= 1.4.1
- typing-extensions >= 4.15.0
- loguru >= 0.7.3
- toolz >= 1.1.0
- toon-python >= 0.1.2

## License

Please check the [LICENSE file](https://github.com/devcomfort/chonkie-chunk-utils/blob/main/LICENSE) in the repository.

## Author

- devcomfort (im@devcomfort.me)
