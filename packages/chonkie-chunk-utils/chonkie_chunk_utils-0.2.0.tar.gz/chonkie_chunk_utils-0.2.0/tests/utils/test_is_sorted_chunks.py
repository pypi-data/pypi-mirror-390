from chonkie.types.base import Chunk
from chonkie_chunk_utils.utils.is_sorted_chunks import is_sorted_chunks


def test_sorted_chunks():
    """Verify sorted chunks detection: chunks with strictly ascending start_index are sorted.
    
    When chunks have start_index values in strictly ascending order (each chunk's start_index
    is greater than the previous one), they should be considered sorted. This is the basic
    requirement for chunks to be in proper sequential order.
    """
    chunks = [
        Chunk(start_index=0),
        Chunk(start_index=3),
        Chunk(start_index=7),
    ]
    assert is_sorted_chunks(chunks) is True


def test_unsorted_chunks():
    """Verify unsorted chunks detection: chunks with descending or duplicate start_index are not sorted.
    
    When chunks have start_index values in descending order or contain duplicates, they should
    NOT be considered sorted. This ensures that the function correctly identifies when chunks
    are out of order, which is critical for operations that require sorted input.
    """
    chunks1 = [Chunk(start_index=2), Chunk(start_index=1), Chunk(start_index=5)]
    chunks2 = [Chunk(start_index=0), Chunk(start_index=2), Chunk(start_index=2)]
    assert is_sorted_chunks(chunks1) is False
    assert is_sorted_chunks(chunks2) is False


def test_sorted_with_overlap():
    """Verify sorting criteria: only start_index matters, not end_index or overlap.
    
    When chunks have overlapping ranges but start_index values are in ascending order,
    they should be considered sorted. The function only checks start_index ordering,
    ignoring end_index values or whether chunks overlap. This is important for
    understanding that sorting is based solely on start positions.
    """
    chunks = [
        Chunk(start_index=0, end_index=10),
        Chunk(start_index=5, end_index=15),
        Chunk(start_index=20, end_index=25),
    ]
    assert is_sorted_chunks(chunks) is True


def test_empty_chunks():
    """Verify edge case: empty list is considered sorted.
    
    An empty list of chunks should be considered sorted (vacuously true). This ensures
    that the function handles the empty case gracefully without errors.
    """
    assert is_sorted_chunks([]) is True


def test_single_chunk():
    """Verify edge case: single chunk is considered sorted.
    
    A list containing only one chunk should be considered sorted, as there are no
    ordering relationships to check. This ensures the function handles the minimal
    case correctly.
    """
    assert is_sorted_chunks([Chunk(start_index=8)]) is True
