from chonkie import Chunk
from .is_adjacent_chunks import is_adjacent_chunks


def _find_text_overlap(text1: str, text2: str) -> int:
    """
    Find the length of the longest overlap between the end of text1 and the start of text2.

    This function identifies the longest suffix of text1 that matches a prefix of text2.
    Since tokenizer boundaries are programmatically undefinable, we use text-based
    comparison to detect overlaps.

    Parameters
    ----------
    text1 : str
        The first text (chunk_1.text).
    text2 : str
        The second text (chunk_2.text).

    Returns
    -------
    int
        The length of the longest overlap found. Returns 0 if no overlap exists.

    Examples
    --------
    >>> _find_text_overlap("Hello world", "world there")
    5  # "world" overlaps
    >>> _find_text_overlap("Hello", "Hello there")
    5  # "Hello" overlaps
    >>> _find_text_overlap("Hello", "there")
    0  # No overlap
    """
    if not text1 or not text2:
        return 0

    # Find the longest overlap by checking suffixes of text1 against prefixes of text2
    max_overlap = min(len(text1), len(text2))

    for overlap_len in range(max_overlap, 0, -1):
        if text1[-overlap_len:] == text2[:overlap_len]:
            return overlap_len

    return 0


def merge_chunks(chunk_1: Chunk, chunk_2: Chunk) -> Chunk:
    """
    Merge two adjacent chunks, automatically removing text overlap.

    This function merges two chunks that are adjacent, overlapping, or meet at boundary.
    Since tokenizer boundaries are programmatically undefinable and indices may vary
    based on the tokenizer used, this function uses text-based comparison to identify
    and remove overlaps automatically.

    Parameters
    ----------
    chunk_1 : Chunk
        The first chunk object. Must start before chunk_2.
    chunk_2 : Chunk
        The second chunk object. Must be adjacent to chunk_1.

    Returns
    -------
    Chunk
        A new merged chunk with:
        - start_index: min(chunk_1.start_index, chunk_2.start_index)
        - end_index: max(chunk_1.end_index, chunk_2.end_index)
        - text: chunk_1.text + chunk_2.text with overlap removed

    Raises
    ------
    ValueError
        If chunks are not adjacent (as determined by is_adjacent_chunks).

    Examples
    --------
    >>> from chonkie import Chunk
    >>> chunk1 = Chunk(start_index=0, end_index=5, text="Hello world")
    >>> chunk2 = Chunk(start_index=4, end_index=10, text="world there")
    >>> merged = merge_chunks(chunk1, chunk2)
    >>> merged.text
    'Hello world there'
    >>> chunk1 = Chunk(start_index=0, end_index=5, text="Hello")
    >>> chunk2 = Chunk(start_index=5, end_index=10, text="Hello there")
    >>> merged = merge_chunks(chunk1, chunk2)
    >>> merged.text
    'Hello there'
    """
    # NOTE: 이 함수는 시작 인덱스를 기준으로 정렬된 청크 1, 2를 입력받았을 때, 청크 1, 2가 인접됨을 가정하고 병합을 수행합니다.
    if not is_adjacent_chunks(chunk_1, chunk_2):
        raise ValueError("Chunks are not adjacent")

    # Find text overlap and remove it
    overlap_len = _find_text_overlap(chunk_1.text, chunk_2.text)
    new_text = chunk_1.text + chunk_2.text[overlap_len:]

    new_start_index = min(chunk_1.start_index, chunk_2.start_index)
    new_end_index = max(chunk_1.end_index, chunk_2.end_index)

    return Chunk(
        start_index=new_start_index,
        end_index=new_end_index,
        text=new_text,
    )
