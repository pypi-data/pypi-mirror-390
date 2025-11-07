# chonkie-chunk-utils

**How about sort, merge, and formatting for your RAG?**

`chonkie-chunk-utils` is a chunk management utility library for RAG (Retrieval-Augmented Generation) systems. It provides functions for sorting, merging, formatting, and rendering document chunks to create optimal context formats that are easy for LLMs to understand.

> ⚠️ **Research Purpose**: This library is currently intended for **research purposes**. While it is functional and tested, it may undergo significant changes as research progresses. Use with caution in production environments.

## Core Feature: Formatting & Rendering

**This is what we provide.** Transform raw chunks into LLM-friendly, structured formats that enhance understanding and reduce token waste.

### Why Formatting & Rendering Matter

Unstructured chunks lack the organization and formatting that LLMs need to effectively understand relationships, boundaries, and metadata. Our formatting and rendering functions transform unstructured chunks into structured formats (XML, JSON, TOON) that LLMs can easily parse and reason about.

### Quick Example

```python
from chonkie import Chunk
from chonkie_chunk_utils import render_chunks, jsonify

chunks = [
    Chunk(start_index=0, end_index=5, text="Hello", context="doc1"),
    Chunk(start_index=20, end_index=25, text="world", context="doc1"),
]

# Default: XML format
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
```

## Use Case: Reranking Pipeline

**This is how you can use it.** While reranking itself is not provided by this library, we provide the essential preprocessing and formatting functions that make reranking pipelines work seamlessly.

### Why This Approach Works Better

> 📝 **Research Hypothesis**: When reranking is performed on sorted, merged chunks (organized chunk sets with overlapping adjacent chunks resolved), embedding models and reranking models can capture semantic meaning more effectively compared to using raw, unprocessed chunks.
>
> **Note:** This is currently a research hypothesis that we are investigating. The benefits described below are theoretical and require empirical validation.

**Theoretical benefits:**
- **Better semantic coherence**: Merged chunks represent continuous, coherent text segments rather than fragmented pieces
- **Improved context understanding**: Sorting ensures chunks follow document order, preserving logical flow
- **Enhanced embedding quality**: Clean, organized chunks allow models to better understand relationships and boundaries
- **More accurate reranking**: Reranking models receive well-structured input, leading to better relevance judgments

### Complete Workflow

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

📚 **Full documentation is available at**: [https://devcomfort.github.io/chonkie-chunk-utils/](https://devcomfort.github.io/chonkie-chunk-utils/)

- [Installation Guide](https://devcomfort.github.io/chonkie-chunk-utils/installation/)
- [Quick Start Guide](https://devcomfort.github.io/chonkie-chunk-utils/quick-start/)
- [User Guide](https://devcomfort.github.io/chonkie-chunk-utils/guide/sorting/)
- [API Reference](https://devcomfort.github.io/chonkie-chunk-utils/api/main/)

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
