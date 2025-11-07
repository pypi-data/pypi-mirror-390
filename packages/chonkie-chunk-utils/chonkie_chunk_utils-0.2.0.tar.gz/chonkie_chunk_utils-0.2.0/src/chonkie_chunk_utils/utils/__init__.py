"""
Utility functions for chunk management operations.

This module provides helper functions for working with Chunk objects,
including validation, sorting, and formatting utilities.

Modules
-------
is_sorted_chunks : Function to check if chunks are sorted by start_index.
is_adjacent_chunks : Function to check if two chunks are adjacent or non-overlapping.
merge_chunks : Function to merge two adjacent chunks with automatic overlap removal.

Examples
--------
>>> from chonkie_chunk_utils.utils import is_sorted_chunks, is_adjacent_chunks, merge_chunks
>>> from chonkie import Chunk
>>> chunks = [Chunk(start_index=0), Chunk(start_index=2), Chunk(start_index=5)]
>>> is_sorted_chunks(chunks)
True
>>> chunk1 = Chunk(start_index=0, end_index=5)
>>> chunk2 = Chunk(start_index=6, end_index=10)
>>> is_adjacent_chunks(chunk1, chunk2)
True
>>> chunk1 = Chunk(start_index=0, end_index=5, text="Hello world")
>>> chunk2 = Chunk(start_index=4, end_index=10, text="world there")
>>> merged = merge_chunks(chunk1, chunk2)
>>> merged.text
'Hello world there'
"""

from .is_adjacent_chunks import is_adjacent_chunks
from .is_sorted_chunks import is_sorted_chunks
from .merge_chunks import merge_chunks

__all__ = ["is_sorted_chunks", "is_adjacent_chunks", "merge_chunks"]
