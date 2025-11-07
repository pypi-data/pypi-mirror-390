from chonkie import Chunk


def is_sorted_chunks(chunks: list[Chunk]) -> bool:
    """
    Check if chunks are strictly sorted by start_index (ascending, no duplicates).

    Parameters
    ----------
    chunks : list of Chunk
        List of Chunk objects to check for sort order. Only the `start_index` of each chunk is considered.

    Returns
    -------
    bool
        True if start_index values are strictly increasing (no overlap or duplicate starts), otherwise False.

    Examples
    --------
    >>> from chonkie import Chunk
    >>> is_sorted_chunks([Chunk(start_index=0), Chunk(start_index=2), Chunk(start_index=5)])
    True
    >>> is_sorted_chunks([Chunk(start_index=0), Chunk(start_index=0)])
    False
    >>> is_sorted_chunks([Chunk(start_index=3), Chunk(start_index=2)])
    False
    >>> is_sorted_chunks([])
    True
    """
    # NOTE: overlap을 고려하여 start_index 기준으로만 정렬하여 처리합니다.
    return all(
        chunks[i].start_index < chunks[i + 1].start_index
        for i in range(len(chunks) - 1)
    )
