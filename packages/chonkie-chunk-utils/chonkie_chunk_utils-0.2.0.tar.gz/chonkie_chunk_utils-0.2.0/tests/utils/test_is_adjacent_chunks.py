import pytest
from chonkie.types.base import Chunk
from chonkie_chunk_utils.utils.is_adjacent_chunks import is_adjacent_chunks


# Test cases that should return True (adjacent chunks)
ADJACENT_TEST_CASES = [
    # (chunk1_start, chunk1_end, chunk2_start, chunk2_end, description)
    (0, 5, 4, 10, "overlapping_chunks_from_right"),
    (2, 8, 5, 12, "chunk2_partially_overlapping"),
    (0, 5, 5, 10, "boundary_meeting"),
    (0, 5, 6, 10, "immediately_adjacent"),
    (0, 5, 5, 8, "chunk2_starts_at_chunk1_end"),
]


# Test cases that should return False (not adjacent chunks)
NOT_ADJACENT_TEST_CASES = [
    # (chunk1_start, chunk1_end, chunk2_start, chunk2_end, description)
    (0, 10, 3, 7, "chunk2_within_chunk1_containment"),
    (0, 5, 0, 5, "exact_match_identical_chunks"),
    (0, 5, 8, 10, "non_overlapping_chunks_with_gap"),
    (0, 5, 20, 25, "chunks_with_large_gap"),
    (5, 10, 0, 4, "chunk2_before_chunk1"),
    (0, 5, 0, 3, "chunk2_starts_at_chunk1_start"),
]


@pytest.mark.parametrize(
    "chunk1_start,chunk1_end,chunk2_start,chunk2_end,description",
    ADJACENT_TEST_CASES,
)
def test_adjacent_chunks(
    chunk1_start, chunk1_end, chunk2_start, chunk2_end, description
):
    """Verify that chunks are correctly identified as adjacent.

    This parametrized test covers various scenarios where chunks should be
    considered adjacent: overlapping, boundary meeting, and immediately adjacent cases.
    """
    chunk1 = Chunk(start_index=chunk1_start, end_index=chunk1_end)
    chunk2 = Chunk(start_index=chunk2_start, end_index=chunk2_end)
    assert is_adjacent_chunks(chunk1, chunk2) is True, (
        f"Failed for {description}: "
        f"chunk1=[{chunk1_start}, {chunk1_end}], chunk2=[{chunk2_start}, {chunk2_end}]"
    )


@pytest.mark.parametrize(
    "chunk1_start,chunk1_end,chunk2_start,chunk2_end,description",
    NOT_ADJACENT_TEST_CASES,
)
def test_not_adjacent_chunks(
    chunk1_start, chunk1_end, chunk2_start, chunk2_end, description
):
    """Verify that chunks are correctly identified as not adjacent.

    This parametrized test covers various scenarios where chunks should NOT be
    considered adjacent: containment (not considered adjacent), exact match (not considered adjacent),
    gaps, reverse order, and same start position.
    """
    chunk1 = Chunk(start_index=chunk1_start, end_index=chunk1_end)
    chunk2 = Chunk(start_index=chunk2_start, end_index=chunk2_end)
    assert is_adjacent_chunks(chunk1, chunk2) is False, (
        f"Failed for {description}: "
        f"chunk1=[{chunk1_start}, {chunk1_end}], chunk2=[{chunk2_start}, {chunk2_end}]"
    )
