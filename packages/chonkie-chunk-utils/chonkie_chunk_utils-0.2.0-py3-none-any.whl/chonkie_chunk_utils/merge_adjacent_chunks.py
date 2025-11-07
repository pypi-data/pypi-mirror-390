from chonkie import Chunk
from typing import Iterable, List
from .utils import is_adjacent_chunks, merge_chunks


def merge_adjacent_chunks(chunks: Iterable[Chunk]) -> List[Chunk]:
    """
    Merge adjacent chunks in an iterable of chunks.

    This function processes an iterable of chunks sequentially and merges any
    chunks that are adjacent, overlapping, or meet at boundary. Adjacent chunks
    are automatically merged using text-based overlap detection to remove
    duplicate text content.

    The function processes chunks in order, maintaining a list of merged chunks.
    For each new chunk, if it is adjacent to the last merged chunk, they are
    merged together. Otherwise, the new chunk is added as a separate entry.

    Parameters
    ----------
    chunks : Iterable[Chunk]
        An iterable of Chunk objects to process. Chunks should ideally be
        sorted by start_index for best results, though the function will work
        with any order.

    Returns
    -------
    List[Chunk]
        A list of merged chunks. Adjacent chunks have been merged into single
        chunks with combined text (overlap removed) and expanded index ranges.

    Notes
    -----
    - Chunks are considered adjacent if they overlap, meet at boundary, or are
      immediately adjacent (gap of exactly 1 index). See `is_adjacent_chunks`
      for details.
    - Text overlap is automatically detected and removed during merging. See
      `merge_chunks` for details.
    - The function processes chunks sequentially, so the order of input chunks
      matters. Chunks that appear later in the iterable will only be merged
      with the last processed chunk if they are adjacent.

    Examples
    --------
    **Merge overlapping chunks:**
    >>> from chonkie import Chunk
    >>> chunks = [
    ...     Chunk(start_index=0, end_index=5, text="Hello world"),
    ...     Chunk(start_index=4, end_index=10, text="world there")
    ... ]
    >>> merged = merge_adjacent_chunks(chunks)
    >>> len(merged)
    1
    >>> merged[0].text
    'Hello world there'

    **Merge chunks meeting at boundary:**
    >>> chunks = [
    ...     Chunk(start_index=0, end_index=5, text="Hello"),
    ...     Chunk(start_index=5, end_index=10, text=" there")
    ... ]
    >>> merged = merge_adjacent_chunks(chunks)
    >>> len(merged)
    1
    >>> merged[0].text
    'Hello there'

    **Keep non-adjacent chunks separate:**
    >>> chunks = [
    ...     Chunk(start_index=0, end_index=5, text="Hello"),
    ...     Chunk(start_index=10, end_index=15, text="world")
    ... ]
    >>> merged = merge_adjacent_chunks(chunks)
    >>> len(merged)
    2
    >>> merged[0].text
    'Hello'
    >>> merged[1].text
    'world'

    **Merge multiple adjacent chunks:**
    >>> chunks = [
    ...     Chunk(start_index=0, end_index=5, text="The quick"),
    ...     Chunk(start_index=4, end_index=10, text="quick brown"),
    ...     Chunk(start_index=9, end_index=15, text="brown fox")
    ... ]
    >>> merged = merge_adjacent_chunks(chunks)
    >>> len(merged)
    1
    >>> merged[0].text
    'The quick brown fox'
    """
    merged_chunks = []
    for chunk in chunks:
        if not merged_chunks:
            merged_chunks.append(chunk)
        else:
            if is_adjacent_chunks(merged_chunks[-1], chunk):
                merged_chunks[-1] = merge_chunks(merged_chunks[-1], chunk)
            else:
                merged_chunks.append(chunk)
    return merged_chunks
