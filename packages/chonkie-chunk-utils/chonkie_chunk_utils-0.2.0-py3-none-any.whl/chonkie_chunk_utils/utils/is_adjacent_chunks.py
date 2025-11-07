from chonkie import Chunk


def is_adjacent_chunks(chunk_1: Chunk, chunk_2: Chunk) -> bool:
    """
    Check if two chunks are adjacent, overlapping, or meet at boundary.

    This function determines if chunk_2 is in a "connected" relationship with chunk_1,
    where chunk_1 starts before chunk_2. Returns True if chunk_2 is either overlapping,
    meeting at boundary, or immediately adjacent to chunk_1.

    Note that containment and exact match cases are not considered adjacent:
    
    - **Containment**: chunk_2 is completely contained within chunk_1 (returns False).
      This represents a subset relationship, not an adjacency relationship.
      Example: chunk_1=[0, 10], chunk_2=[3, 7] -> chunk_2 is inside chunk_1
    
    - **Exact Match**: chunk_1 and chunk_2 have identical indices (returns False).
      This represents identical chunks, not an adjacency relationship.
      Example: chunk_1=[0, 5], chunk_2=[0, 5] -> identical chunks

    Relationship Types
    ------------------
    **Overlapping:**
        chunk_2.start_index < chunk_1.end_index
        chunk_2 starts before chunk_1 ends, meaning there is an overlap between the two chunks.
        Example: chunk_1=[0, 5], chunk_2=[4, 10] -> overlap at indices 4-5

    **Boundary Meeting:**
        chunk_2.start_index == chunk_1.end_index
        chunk_2 starts exactly where chunk_1 ends, with no gap and no overlap.
        Example: chunk_1=[0, 5], chunk_2=[5, 10] -> meet at index 5

    **Immediately Adjacent:**
        chunk_2.start_index == chunk_1.end_index + 1
        chunk_2 starts immediately after chunk_1 ends, with exactly one index gap.
        Example: chunk_1=[0, 5], chunk_2=[6, 10] -> adjacent with gap at index 5

    **Gap (Not Adjacent):**
        chunk_2.start_index > chunk_1.end_index + 1
        There is a gap of more than one index between the chunks.
        Example: chunk_1=[0, 5], chunk_2=[8, 10] -> gap at indices 5-7

    **Containment (Not Adjacent):**
        chunk_2 is completely contained within chunk_1.
        chunk_1.start_index <= chunk_2.start_index and chunk_2.end_index <= chunk_1.end_index
        Example: chunk_1=[0, 10], chunk_2=[3, 7] -> chunk_2 is inside chunk_1
        Returns False. Containment cases are not considered adjacent.

    **Exact Match (Not Adjacent):**
        chunk_1 and chunk_2 have identical indices.
        chunk_1.start_index == chunk_2.start_index and chunk_1.end_index == chunk_2.end_index
        Example: chunk_1=[0, 5], chunk_2=[0, 5] -> identical chunks
        Returns False. Exact match cases are not considered adjacent.

    Parameters
    ----------
    chunk_1 : Chunk
        The first chunk object. Must start before chunk_2 for the function to return True.
    chunk_2 : Chunk
        The second chunk object. Must start after chunk_1 for the function to return True.

    Returns
    -------
    bool
        Returns True when chunk_2 extends or connects to chunk_1 in a way that makes
        them mergeable. Specifically, True is returned when:

        - chunk_2 overlaps with chunk_1 (chunk_2 starts before chunk_1 ends, but
          extends beyond chunk_1's end)
        - chunk_2 meets chunk_1 at the boundary (chunk_2 starts exactly where
          chunk_1 ends)
        - chunk_2 is immediately adjacent to chunk_1 (chunk_2 starts one position
          after chunk_1 ends)

        Returns False when:

        - There is a gap of more than one position between the chunks
        - chunk_2 starts before chunk_1 (reverse order)
        - chunk_2 is completely contained within chunk_1 (containment - not considered adjacent)
        - chunk_1 and chunk_2 have identical indices (exact match - not considered adjacent)

        The key insight: chunk_2 must extend beyond chunk_1's end to be considered
        adjacent. Containment and exact match cases are explicitly not considered adjacent.

    Examples
    --------
    **Overlapping chunks (True):**
    >>> from chonkie import Chunk
    >>> chunk1 = Chunk(start_index=0, end_index=5)
    >>> chunk2 = Chunk(start_index=4, end_index=10)
    >>> is_adjacent_chunks(chunk1, chunk2)
    True

    **chunk2 completely within chunk1 - containment (False):**
    >>> chunk1 = Chunk(start_index=0, end_index=10)
    >>> chunk2 = Chunk(start_index=3, end_index=7)
    >>> is_adjacent_chunks(chunk1, chunk2)
    False

    **Exact match - identical chunks (False):**
    >>> chunk1 = Chunk(start_index=0, end_index=5)
    >>> chunk2 = Chunk(start_index=0, end_index=5)
    >>> is_adjacent_chunks(chunk1, chunk2)
    False

    **Boundary meeting (True):**
    >>> chunk1 = Chunk(start_index=0, end_index=5)
    >>> chunk2 = Chunk(start_index=5, end_index=10)
    >>> is_adjacent_chunks(chunk1, chunk2)
    True

    **Immediately adjacent (True):**
    >>> chunk1 = Chunk(start_index=0, end_index=5)
    >>> chunk2 = Chunk(start_index=6, end_index=10)
    >>> is_adjacent_chunks(chunk1, chunk2)
    True

    **Gap between chunks (False):**
    >>> chunk1 = Chunk(start_index=0, end_index=5)
    >>> chunk2 = Chunk(start_index=8, end_index=10)
    >>> is_adjacent_chunks(chunk1, chunk2)
    False

    **chunk2 starts before chunk1 (False):**
    >>> chunk1 = Chunk(start_index=5, end_index=10)
    >>> chunk2 = Chunk(start_index=0, end_index=4)
    >>> is_adjacent_chunks(chunk1, chunk2)
    False
    """
    # Check if chunk_2 is adjacent, overlapping, or meeting at boundary.
    # The condition chunk_1.end_index < chunk_2.end_index ensures that chunk_2 extends
    # beyond chunk_1's end, meaning chunk_2 is not completely contained within chunk_1.
    # If chunk_2 were contained, it would be a subset (part of chunk_1), not adjacent.
    return (
        chunk_1.start_index < chunk_2.start_index
        and chunk_2.start_index <= chunk_1.end_index + 1
        and chunk_1.end_index < chunk_2.end_index
    )
